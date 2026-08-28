from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path

from docx import Document
from lxml import etree


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
NS = {"w": W, "m": M, "r": R, "wp": WP, "a": A, "pic": PIC}


def qn(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def text_of(el) -> str:
    parts: list[str] = []
    for node in el.iter():
        if node.tag in (qn(W, "t"), qn(M, "t"), qn(W, "delText")):
            parts.append(node.text or "")
        elif node.tag == qn(W, "tab"):
            parts.append("\t")
        elif node.tag in (qn(W, "br"), qn(W, "cr")):
            parts.append("\n")
    return "".join(parts)


def paragraph_info(p_el, index: str) -> dict:
    ppr = p_el.find(qn(W, "pPr"))
    style = None
    outline = None
    align = None
    spacing = {}
    keep_next = False
    if ppr is not None:
        pstyle = ppr.find(qn(W, "pStyle"))
        if pstyle is not None:
            style = pstyle.get(qn(W, "val"))
        ol = ppr.find(qn(W, "outlineLvl"))
        if ol is not None:
            outline = ol.get(qn(W, "val"))
        jc = ppr.find(qn(W, "jc"))
        if jc is not None:
            align = jc.get(qn(W, "val"))
        sp = ppr.find(qn(W, "spacing"))
        if sp is not None:
            spacing = {etree.QName(k).localname: v for k, v in sp.attrib.items()}
        keep_next = ppr.find(qn(W, "keepNext")) is not None
    omath = len(p_el.xpath(".//m:oMath | .//m:oMathPara"))
    inline = len(p_el.xpath(".//wp:inline"))
    anchor = len(p_el.xpath(".//wp:anchor"))
    blips = [x.get(qn(R, "embed")) for x in p_el.xpath(".//a:blip")]
    return {
        "index": index,
        "text": text_of(p_el),
        "style": style,
        "outline_level": outline,
        "alignment": align,
        "spacing": spacing,
        "keep_next": keep_next,
        "equations": omath,
        "inline_images": inline,
        "anchored_images": anchor,
        "image_rel_ids": [x for x in blips if x],
    }


def table_info(tbl_el, index: str) -> dict:
    tbl_pr = tbl_el.find(qn(W, "tblPr"))
    width = None
    layout = None
    borders = []
    if tbl_pr is not None:
        tw = tbl_pr.find(qn(W, "tblW"))
        if tw is not None:
            width = {etree.QName(k).localname: v for k, v in tw.attrib.items()}
        tl = tbl_pr.find(qn(W, "tblLayout"))
        if tl is not None:
            layout = tl.get(qn(W, "type"))
        tb = tbl_pr.find(qn(W, "tblBorders"))
        if tb is not None:
            borders = [etree.QName(x).localname for x in tb]
    grid = []
    grid_el = tbl_el.find(qn(W, "tblGrid"))
    if grid_el is not None:
        grid = [x.get(qn(W, "w")) for x in grid_el.findall(qn(W, "gridCol"))]
    rows = []
    for ri, tr in enumerate(tbl_el.findall(qn(W, "tr"))):
        cells = []
        for ci, tc in enumerate(tr.findall(qn(W, "tc"))):
            paras = [paragraph_info(p, f"{index}.r{ri}.c{ci}.p{pi}") for pi, p in enumerate(tc.findall(qn(W, "p")))]
            cells.append({"text": text_of(tc), "paragraphs": paras})
        rows.append(cells)
    return {
        "index": index,
        "rows": len(rows),
        "cols_per_row": [len(r) for r in rows],
        "width": width,
        "layout": layout,
        "grid": grid,
        "borders": borders,
        "content": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--json", required=True)
    ap.add_argument("--txt", required=True)
    args = ap.parse_args()
    src = Path(args.docx)

    doc = Document(src)
    body = doc._element.body
    blocks = []
    p_count = t_count = 0
    for bi, child in enumerate(body):
        if child.tag == qn(W, "p"):
            blocks.append({"type": "paragraph", **paragraph_info(child, f"b{bi}.p{p_count}")})
            p_count += 1
        elif child.tag == qn(W, "tbl"):
            blocks.append({"type": "table", **table_info(child, f"b{bi}.t{t_count}")})
            t_count += 1
        elif child.tag != qn(W, "sectPr"):
            blocks.append({"type": etree.QName(child).localname, "index": f"b{bi}", "text": text_of(child)})

    with zipfile.ZipFile(src) as zf:
        names = zf.namelist()
        media = []
        for name in names:
            if name.startswith("word/media/") and not name.endswith("/"):
                data = zf.read(name)
                media.append({"name": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        duplicate_media = [
            {"sha256": h, "files": [m["name"] for m in media if m["sha256"] == h]}
            for h, n in Counter(m["sha256"] for m in media).items() if n > 1
        ]
        document_xml = etree.fromstring(zf.read("word/document.xml"))
        structural = {
            "comments_part": "word/comments.xml" in names,
            "footnotes_part": "word/footnotes.xml" in names,
            "endnotes_part": "word/endnotes.xml" in names,
            "tracked_insertions": len(document_xml.xpath(".//w:ins", namespaces=NS)),
            "tracked_deletions": len(document_xml.xpath(".//w:del", namespaces=NS)),
            "math_objects": len(document_xml.xpath(".//m:oMath", namespaces=NS)),
            "math_paragraphs": len(document_xml.xpath(".//m:oMathPara", namespaces=NS)),
            "inline_drawings": len(document_xml.xpath(".//wp:inline", namespaces=NS)),
            "anchored_drawings": len(document_xml.xpath(".//wp:anchor", namespaces=NS)),
        }

    sections = []
    for i, s in enumerate(doc.sections):
        sections.append({
            "index": i,
            "page_width": s.page_width,
            "page_height": s.page_height,
            "top_margin": s.top_margin,
            "bottom_margin": s.bottom_margin,
            "left_margin": s.left_margin,
            "right_margin": s.right_margin,
        })

    report = {
        "source": str(src.resolve()),
        "paragraphs": p_count,
        "tables": t_count,
        "sections": sections,
        "structural": structural,
        "media": media,
        "duplicate_media": duplicate_media,
        "blocks": blocks,
    }
    Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    for b in blocks:
        if b["type"] == "paragraph":
            lines.append(
                f"[{b['index']}] P style={b['style']} outline={b['outline_level']} eq={b['equations']} "
                f"img={b['inline_images']}/{b['anchored_images']} :: {b['text']}"
            )
        elif b["type"] == "table":
            lines.append(f"[{b['index']}] TABLE rows={b['rows']} grid={b['grid']} width={b['width']}")
            for ri, row in enumerate(b["content"]):
                for ci, cell in enumerate(row):
                    lines.append(f"  R{ri}C{ci}: {cell['text']}")
        else:
            lines.append(f"[{b['index']}] {b['type']} :: {b.get('text', '')}")
    Path(args.txt).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
