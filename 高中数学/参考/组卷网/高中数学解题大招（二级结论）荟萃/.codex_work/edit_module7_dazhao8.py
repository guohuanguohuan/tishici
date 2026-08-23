from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from lxml import etree


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"w": W, "r": R, "wp": WP, "a": A}


def qn(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def text_of(el) -> str:
    parts: list[str] = []
    for node in el.iter():
        if node.tag == qn(W, "t"):
            parts.append(node.text or "")
    return "".join(parts).strip()


def ensure(parent, tag: str):
    child = parent.find(tag)
    if child is None:
        child = etree.SubElement(parent, tag)
    return child


def set_attr(el, ns: str, name: str, value: str) -> None:
    el.set(qn(ns, name), value)


def clear_children(el) -> None:
    for child in list(el):
        el.remove(child)


def set_outline_level(p, level: int | None) -> None:
    ppr = ensure(p, qn(W, "pPr"))
    old = ppr.find(qn(W, "outlineLvl"))
    if old is not None:
        ppr.remove(old)
    if level is not None:
        outline = etree.SubElement(ppr, qn(W, "outlineLvl"))
        set_attr(outline, W, "val", str(level))


def main() -> None:
    src = Path(r"04_原始资料\模块7立体几何\模块7大招8判二面角的锐钝问题.docx")
    if not src.exists():
        raise FileNotFoundError(src)

    with TemporaryDirectory() as tmpdir:
        work = Path(tmpdir)
        unpack = work / "unpacked"
        unpack.mkdir()
        with zipfile.ZipFile(src) as zin:
            zin.extractall(unpack)

        doc_xml = unpack / "word" / "document.xml"
        rels_xml = unpack / "word" / "_rels" / "document.xml.rels"
        doc = etree.parse(str(doc_xml))
        rels = etree.parse(str(rels_xml))
        relmap = {
            rel.get("Id"): rel.get("Target")
            for rel in rels.getroot()
            if rel.tag.endswith("Relationship")
        }

        body = doc.getroot().find(qn(W, "body"))
        block_tables = [child for child in body if child.tag == qn(W, "tbl")]

        # Reorder question-level blocks so each question follows:
        # label -> stem -> answer ideas -> answer -> analysis tables -> other notes.
        children = list(body)
        sect_pr = None
        if children and children[-1].tag == qn(W, "sectPr"):
            sect_pr = children[-1]
            content = children[:-1]
        else:
            content = children

        new_order = (
            list(range(0, 23))
            + [23, 24, 25, 26, 28, 29, 27, 30, 31, 32, 33, 34, 35, 36]
            + [37, 38, 39, 40, 42, 44, 46, 48, 54, 56, 58, 41, 43, 45, 47, 49, 55, 57, 59, 50, 51, 52, 53, 60, 61, 62]
            + [63, 64, 65, 66, 67, 70, 68, 71, 69, 72, 73, 74]
            + [75, 76, 77, 78, 79, 82, 83, 80, 84, 81, 85]
            + [86, 87, 88, 89, 90, 91, 95, 96, 97, 92, 98, 93, 94, 99]
            + [100, 101, 102, 103, 104, 110, 111, 105, 106, 112, 107, 108, 109]
            + [113, 114, 115, 116, 117, 118, 122, 123, 124, 119, 125, 120, 121]
            + [126, 127, 128, 129, 130, 137, 138, 131, 132, 139, 133, 134, 135, 136, 140]
        )
        assert len(content) == len(new_order), "Body block count changed; reorder map must be updated."
        reordered = [content[i] for i in new_order]
        for child in list(body):
            body.remove(child)
        for child in reordered:
            body.append(child)
        if sect_pr is not None:
            body.append(sect_pr)

        # Global paragraph formatting and outline levels.
        for p in doc.xpath(".//w:p", namespaces=NS):
            ppr = ensure(p, qn(W, "pPr"))

            jc = ensure(ppr, qn(W, "jc"))
            set_attr(jc, W, "val", "left")

            spacing = ensure(ppr, qn(W, "spacing"))
            set_attr(spacing, W, "before", "0")
            set_attr(spacing, W, "after", "0")
            set_attr(spacing, W, "line", "300")
            set_attr(spacing, W, "lineRule", "auto")

            snap = ensure(ppr, qn(W, "snapToGrid"))
            set_attr(snap, W, "val", "0")

            text = text_of(p)
            if text.startswith("【答案】") or text.startswith("【详细解析】"):
                set_outline_level(p, 1)
            elif "【法" in text or text.startswith("【答案思路】"):
                set_outline_level(p, 2)
            elif text.startswith("【步骤"):
                set_outline_level(p, 3)

            keep_next = ppr.find(qn(W, "keepNext"))
            if keep_next is not None:
                ppr.remove(keep_next)

        # Analysis tables: fix width, equal columns, borders, top align.
        for tbl in block_tables:
            rows = tbl.findall(qn(W, "tr"))
            if len(rows) != 1:
                continue
            cells = rows[0].findall(qn(W, "tc"))
            if len(cells) != 2:
                continue
            first_cell_text = text_of(cells[0])
            if "【详细解析】" not in first_cell_text:
                continue

            tbl_pr = ensure(tbl, qn(W, "tblPr"))

            tbl_w = ensure(tbl_pr, qn(W, "tblW"))
            set_attr(tbl_w, W, "type", "dxa")
            set_attr(tbl_w, W, "w", "8307")

            layout = ensure(tbl_pr, qn(W, "tblLayout"))
            set_attr(layout, W, "type", "fixed")

            indent = ensure(tbl_pr, qn(W, "tblInd"))
            set_attr(indent, W, "type", "dxa")
            set_attr(indent, W, "w", "0")

            borders = ensure(tbl_pr, qn(W, "tblBorders"))
            clear_children(borders)
            for name in ("top", "left", "bottom", "right", "insideH", "insideV"):
                border = etree.SubElement(borders, qn(W, name))
                set_attr(border, W, "val", "single")
                set_attr(border, W, "sz", "4")
                set_attr(border, W, "space", "0")
                set_attr(border, W, "color", "000000")

            grid = tbl.find(qn(W, "tblGrid"))
            if grid is None:
                grid = etree.Element(qn(W, "tblGrid"))
                tbl.insert(1, grid)
            clear_children(grid)
            for width in ("4153", "4154"):
                col = etree.SubElement(grid, qn(W, "gridCol"))
                set_attr(col, W, "w", width)

            for tc, width in zip(cells, ("4153", "4154"), strict=True):
                tc_pr = ensure(tc, qn(W, "tcPr"))
                tc_w = ensure(tc_pr, qn(W, "tcW"))
                set_attr(tc_w, W, "type", "dxa")
                set_attr(tc_w, W, "w", width)
                v_align = ensure(tc_pr, qn(W, "vAlign"))
                set_attr(v_align, W, "val", "top")

        # Remove an obvious stray sentence and tighten one wording.
        for t in doc.xpath(".//w:t", namespaces=NS):
            if t.text == "检验学习效果的时候到啦":
                t.text = ""
            elif t.text == "建立如上图所示的坐标系．":
                t.text = "建立如图所示的空间直角坐标系．"
            elif t.text == "【迁移说明】本题沿用“方向向量—法向量夹角”的共同原理；线面角规定为锐角或直角，计算时取绝对值，无需再判锐钝。":
                t.text = "【迁移说明】本题沿用“方向向量—法向量夹角”原理；线面角恒取锐角或直角，计算时取绝对值，无需再判锐钝。"

        # Pull the cone figure back inside the page on page 3.
        for p in doc.xpath(".//w:p[.//wp:anchor]", namespaces=NS):
            for anchor in p.xpath(".//wp:anchor", namespaces=NS):
                embeds = anchor.xpath(".//a:blip/@r:embed", namespaces=NS)
                targets = {relmap.get(embed) for embed in embeds}
                if "media/image11.png" in targets:
                    pos_h = anchor.find(qn(WP, "positionH"))
                    if pos_h is not None:
                        off = pos_h.find(qn(WP, "posOffset"))
                        if off is not None:
                            off.text = "4300000"

        # Slightly reduce the last question's figure to avoid an almost-empty tail page.
        for inline in doc.xpath(".//wp:inline", namespaces=NS):
            embeds = inline.xpath(".//a:blip/@r:embed", namespaces=NS)
            targets = {relmap.get(embed) for embed in embeds}
            if "media/image42.png" in targets:
                extent = inline.find(qn(WP, "extent"))
                if extent is not None:
                    extent.set("cx", "1211580")
                    extent.set("cy", "1623060")

        out_xml = etree.tostring(
            doc.getroot(),
            xml_declaration=True,
            encoding="UTF-8",
            standalone="yes",
        )
        doc_xml.write_bytes(out_xml)

        rebuilt = work / "rebuilt.docx"
        with zipfile.ZipFile(rebuilt, "w", zipfile.ZIP_DEFLATED) as zout:
            for file in sorted(unpack.rglob("*")):
                if file.is_file():
                    zout.write(file, file.relative_to(unpack).as_posix())

        shutil.copy2(rebuilt, src)


if __name__ == "__main__":
    main()
