# -*- coding: utf-8 -*-
"""把源知识清单中被误删但仍属于正文的章级导图图片恢复到教材节下。"""
from __future__ import annotations

import copy
import sys
import zipfile
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

W_P = qn("w:p")
W_PPR = qn("w:pPr")
W_T = qn("w:t")
W_DRAWING = qn("w:drawing")
R_EMBED = qn("r:embed")
WP_EXTENT = qn("wp:extent")
A_EXT = qn("a:ext")


def paragraph_text(p_el):
    return "".join(t.text or "" for t in p_el.iter(W_T)).strip()


def drawing_count(p_el):
    return sum(1 for _ in p_el.iter(W_DRAWING))


def image_rids(p_el):
    return [el.get(R_EMBED) for el in p_el.iter() if el.tag.endswith("}blip") and el.get(R_EMBED)]


def assert_same_image_relationships(source_path, target_path, rids):
    """本轮目标源自同一 DOCX，恢复前先证明相同 rId 仍指向相同图片。"""
    def targets(path):
        with zipfile.ZipFile(path) as zf:
            from lxml import etree
            root = etree.fromstring(zf.read("word/_rels/document.xml.rels"))
            return {el.get("Id"): el.get("Target") for el in root}

    source_targets = targets(source_path)
    target_targets = targets(target_path)
    for rid in rids:
        if source_targets.get(rid) != target_targets.get(rid):
            raise ValueError(f"图片关系不一致，禁止直接迁移：{rid}")


def image_only_copy(p_el):
    copied = copy.deepcopy(p_el)
    for child in list(copied):
        if child.tag == W_PPR:
            continue
        if drawing_count(child) == 0:
            copied.remove(child)
            continue
        for text in list(child.iter(W_T)):
            parent = text.getparent()
            if parent is not None:
                parent.remove(text)
    if drawing_count(copied) == 0:
        raise ValueError("图片段复制后没有 drawing")
    return copied


def scale_drawing_for_compact_layout(p_el, rid, ratio):
    """仅改显示尺寸，不改图片文件；用于避免末页只有数行的大面积留白。"""
    for blip in p_el.iter():
        if not blip.tag.endswith("}blip") or blip.get(R_EMBED) != rid:
            continue
        drawing = blip
        while drawing is not None and drawing.tag != W_DRAWING:
            drawing = drawing.getparent()
        if drawing is None:
            raise ValueError(f"未找到图片 {rid} 的 drawing")
        for extent in drawing.iter():
            if (extent.tag in (WP_EXTENT, A_EXT) and
                    extent.get("cx") is not None and extent.get("cy") is not None):
                extent.set("cx", str(round(int(extent.get("cx")) * ratio)))
                extent.set("cy", str(round(int(extent.get("cy")) * ratio)))


def restore(source_path, target_path, output_path):
    source = Document(source_path)
    target = Document(target_path)
    source_image_paras = []
    for p_el in source.element.body:
        if p_el.tag != W_P:
            continue
        if paragraph_text(p_el).startswith("1．电功和电功率"):
            break
        if drawing_count(p_el):
            source_image_paras.append(p_el)
    if sum(drawing_count(p) for p in source_image_paras) != 4:
        raise ValueError("源文件章首应有4个导图相关图片引用")

    existing_refs = sum(drawing_count(p) for p in target.element.body if p.tag == W_P)
    if existing_refs != 7:
        raise ValueError(f"待修成品预期有7个图片引用，实际为{existing_refs}")

    rids = [rid for p in source_image_paras for rid in image_rids(p)]
    assert_same_image_relationships(source_path, target_path, rids)

    anchor = next(
        p for p in target.element.body
        if p.tag == W_P and paragraph_text(p) == "12.1 电路中的能量转化"
    )
    cursor = anchor
    for p_el in source_image_paras:
        restored = image_only_copy(p_el)
        # rId9 是整章知识思维导图；原始图片字节不变，显示为86%，
        # 可在保持可读性的同时消除末页仅4行的版面浪费。
        scale_drawing_for_compact_layout(restored, "rId9", 0.86)
        cursor.addnext(restored)
        cursor = restored
    target.save(output_path)
    print(f"OK 恢复导图相关图片4个：{output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("用法：python 知识清单图片恢复.py 源文件.docx 待修成品.docx 输出.docx")
    restore(*sys.argv[1:])
