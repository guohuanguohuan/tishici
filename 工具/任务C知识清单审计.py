# -*- coding: utf-8 -*-
"""任务C知识清单审计.py — 任务C知识清单的结构、图片与基础版式审计。
用法: python 工具/任务C知识清单审计.py <math|physics> <源文件.docx> <成品.docx>
输出: stdout 打印「PASS + 图片数」或以 SystemExit 给出 FAIL 逐行清单；只适配内置 CASES 两张清单（数学选必2第3章/物理必修3第12章），源件仅用于图片保真比对。"""
from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path

from lxml import etree

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "dc": "http://purl.org/dc/elements/1.1/",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
}

CASES = {
    "math": {
        "title": "人教B版选必2 第3章 排列、组合与二项式定理·知识清单（完成）",
        "headings": [
            "3.1 排列与组合", "3.1.1 基本计数原理", "3.1.2 排列与排列数",
            "3.1.3 组合与组合数", "3.2 数学探究活动：生日悖论的解释与模拟",
            "3.3 二项式定理与杨辉三角",
        ],
        "banned": ["一、单元学习目标", "二、单元知识架构", "三、单元知识梳理"],
    },
    "physics": {
        "title": "人教版必修3 第12章 电能 能量守恒定律·知识清单（完成）",
        "headings": [
            "12.1 电路中的能量转化", "12.2 闭合电路的欧姆定律",
            "12.3 实验：电池电动势和内阻的测量", "12.4 能源与可持续发展",
        ],
        "banned": [
            "1．电功和电功率", "2．焦耳定律", "3．电路中的能量转化", "4．电动势",
            "5．闭合电路欧姆定律", "6．路端电压与负载的关系", "7．电源的U-I图像",
            "8．能量守恒定律", "9．能量转移或转化的方向性",
            "10．能源的分类与应用　能源与社会发展",
        ],
    },
}


def media_hashes(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        return sorted(
            hashlib.sha256(zf.read(name)).hexdigest()
            for name in zf.namelist() if name.startswith("word/media/") and not name.endswith("/")
        )


def fail_if(condition: bool, message: str, errors: list[str]) -> None:
    if condition:
        errors.append(message)


def audit(mode: str, source: Path, final: Path) -> None:
    case = CASES[mode]
    errors: list[str] = []
    with zipfile.ZipFile(final) as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
        core = etree.fromstring(zf.read("docProps/core.xml"))
        rels = etree.fromstring(zf.read("word/_rels/document.xml.rels"))
        media_names = [name for name in zf.namelist()
                       if name.startswith("word/media/") and not name.endswith("/")]
        footer_xmls = [etree.fromstring(zf.read(name)) for name in zf.namelist()
                       if name.startswith("word/footer") and name.endswith(".xml")]
    texts = ["".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()
             for p in root.xpath(".//w:body//w:p", namespaces=NS)]
    full_text = "\n".join(texts)

    first_text = next((text for text in texts if text), "")
    fail_if(final.stem != case["title"], f"文件名不符合总控3.5：{final.stem!r}", errors)
    fail_if(first_text != final.stem, f"文内标题与文件名不一致：{first_text!r}", errors)
    core_title = "".join(core.xpath(".//dc:title/text()", namespaces=NS)).strip()
    fail_if(core_title != final.stem, f"核心属性标题不一致：{core_title!r}", errors)
    for heading in case["headings"]:
        fail_if(texts.count(heading) != 1, f"教材节标题数量异常：{heading} -> {texts.count(heading)}", errors)
    for banned in case["banned"]:
        fail_if(banned in full_text, f"残留源结构标题：{banned}", errors)
    for marker in ("题型", "【答案】", "【难度】", "【知识点】", "____"):
        fail_if(marker in full_text, f"残留禁用标记：{marker}", errors)
    fail_if(bool(root.xpath(".//m:oMathPara", namespaces=NS)), "存在块级公式 m:oMathPara", errors)

    for run in root.xpath(".//w:r[w:rPr/w:u]", namespaces=NS):
        bold = run.xpath("./w:rPr/w:b[not(@w:val='0') and not(@w:val='false')]", namespaces=NS)
        fail_if(not bold, "发现未加粗的下划线文本", errors)

    sects = root.xpath(".//w:sectPr", namespaces=NS)
    fail_if(not sects, "缺少节设置", errors)
    for sect in sects:
        size = sect.xpath("./w:pgSz", namespaces=NS)
        mar = sect.xpath("./w:pgMar", namespaces=NS)
        fail_if(not size or size[0].get(f"{{{NS['w']}}}w") != "11906" or
                size[0].get(f"{{{NS['w']}}}h") != "16838", "纸张不是 A4 纵向", errors)
        if mar:
            vals = [mar[0].get(f"{{{NS['w']}}}{key}") for key in ("top", "right", "bottom", "left", "header", "footer")]
            fail_if(any(abs(int(value) - 850) > 1 for value in vals), f"页边距不是 1.5 cm（850缇）：{vals}", errors)

    current_heading = None
    image_sections: list[str | None] = []
    heading_set = set(case["headings"])
    for p in root.xpath(".//w:body//w:p", namespaces=NS):
        text = "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()
        if text in heading_set:
            current_heading = text
        image_refs = (p.xpath(".//a:blip[@r:embed]", namespaces=NS) +
                      p.xpath(".//v:imagedata[@r:id]", namespaces=NS))
        if image_refs:
            image_sections.extend([current_heading] * len(image_refs))
    fail_if(any(section is None for section in image_sections), f"存在未挂靠教材节的图片：{image_sections}", errors)
    if mode == "physics":
        start = texts.index("12.3 实验：电池电动势和内阻的测量")
        end = texts.index("12.4 能源与可持续发展")
        section_texts = [text for text in texts[start + 1:end] if text]
        fail_if(not section_texts, "12.3 教材节为空，电源 U-I 图像条目未正确挂靠", errors)
        fail_if(not any("U-I图像" in text.replace(" ", "") for text in section_texts),
                "12.3 缺少电源 U-I 图像知识条目", errors)
        fail_if("12.3 实验：电池电动势和内阻的测量" not in image_sections,
                "12.3 缺少随 U-I 图像条目迁移的源配图", errors)

    source_media = media_hashes(source)
    final_media = media_hashes(final)
    fail_if(source_media != final_media,
            f"图片未原样保全：源 {len(source_media)} 张，成品 {len(final_media)} 张", errors)
    image_rels = rels.xpath("./pr:Relationship[contains(@Type, '/image')]", namespaces=NS)
    image_refs = (root.xpath(".//a:blip[@r:embed]", namespaces=NS) +
                  root.xpath(".//v:imagedata[@r:id]", namespaces=NS))
    fail_if(not (len(media_names) == len(image_rels) == len(image_refs)),
            f"图片三查不一致：media={len(media_names)}, rels={len(image_rels)}, refs={len(image_refs)}", errors)
    fail_if(not footer_xmls, "缺少页脚部件", errors)
    for footer in footer_xmls:
        footer_text = "".join(footer.xpath(".//w:t/text()", namespaces=NS))
        instructions = " ".join(footer.xpath(".//w:instrText/text()", namespaces=NS))
        fail_if("PAGE" not in instructions or "NUMPAGES" in instructions or "共" in footer_text,
                "页脚不是仅页码格式", errors)

    if errors:
        raise SystemExit("\n".join("FAIL " + error for error in errors))
    print(f"PASS {mode}: 标题、结构、A4、公式、下划线、图片均通过；图片 {len(final_media)} 张")
    print("  图片挂靠：" + ("；".join(image_sections) if image_sections else "无图片"))


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in CASES:
        raise SystemExit("用法：python 任务C知识清单审计.py math|physics 源文件.docx 成品.docx")
    audit(sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]))
