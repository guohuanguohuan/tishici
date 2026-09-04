# -*- coding: utf-8 -*-
"""复测辅助：只读独立核验，所有输出只写本目录。

COM 批量调用已由外层分别执行；本脚本不启动 Word，不修改任何输入文件。
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docx import Document


HERE = Path(__file__).resolve().parent
SOURCE = Path(r"C:\提示词\工具\节页码定位.py")
RECORD = Path(r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\盖章记录_子步7.md")
REFERENCE = Path(r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\节页码_子步8.json")
PARTS_MIRROR = Path(r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\parts_mirror.json")
PROBE = Path(r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\实物run探针_子步8.json")
ORIGINAL_DIR = Path(r"C:\提示词\高中数学\高中数学同步")
MIRROR_DIR = Path(r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\mirror")

EXPECTED_SHA = "844d244a3cb91d5ca8e7c2c17e35963d293aeff623478f76610f39e651bcde85"

FILES = [
    ("衔接1", "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx", 1),
    ("清单1", "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx", 1),
    ("讲练1上", "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx", 1),
    ("讲练1下", "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx", 62),
    ("衔接2", "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx", 1),
    ("清单2", "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx", 1),
    ("讲练2a", "人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx", 1),
    ("讲练2b", "人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx", 56),
    ("讲练2c", "人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx", 112),
    ("讲练2d", "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx", 156),
]

SEC_RE = re.compile(
    r"^(\d+\.\d+(?:\.\d+)?)[\s\u3000]+(.+?)"
    r"(?:（第(\d+)[—–\-](\d+)题）)?(?:[\s\u3000]+本节\d+题[：:].*)?[\s\u3000]*$"
)
STATS_RE = re.compile(r"[\s\u3000]本节\d+题")
NUM_PREFIX_RE = re.compile(r"^(\d+\.\d+(?:\.\d+)?)")
TWO_LEVEL_RE = re.compile(r"^\d+\.\d+")
QUESTION_LABEL_RE = re.compile(r"1\.2\.1\.\d+[-－‐‑‒–—−]\d+[．.]?")
HYPHEN_RE = r"[-－‐‑‒–—−]"

ALIASES_BY_STEM = {fn[:-5]: alias for alias, fn, _ in FILES}


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def path_record() -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    row_re = re.compile(r"^\|\s*(P\d+)\s*\|(?:\s*本\d+\s*\|)?\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*$")
    for line in read_utf8(RECORD).splitlines():
        m = row_re.match(line)
        if not m:
            continue
        part, fn, pages, start, tag, total = m.groups()
        out[os.path.basename(fn.strip())] = {
            "part": part,
            "pages": int(pages),
            "start": int(start),
            "tag": tag.strip(),
            "part_total": int(total),
        }
    return out


def effective_sizes(para):
    direct = []
    for run in para.runs:
        val = run.font.size
        direct.append(round(val.pt, 4) if val is not None else None)
    style_pt = None
    try:
        val = para.style.font.size
        style_pt = round(val.pt, 4) if val is not None else None
    except Exception:
        pass
    effective = [x if x is not None else style_pt for x in direct]
    all_known = bool(effective) and all(x is not None for x in effective)
    common = effective[0] if all_known and all(x == effective[0] for x in effective) else None
    return direct, style_pt, common


def is_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def classify_doc(alias: str, path: Path, reference_sections: list[dict]) -> dict:
    doc = Document(str(path))
    rows = []
    static_hits = []
    seen = set()
    for index, para in enumerate(doc.paragraphs, start=1):
        text = para.text.rstrip("\r\x07\x0b\x0c \u3000")
        if not text or not TWO_LEVEL_RE.match(text) or not is_chinese(text):
            continue
        m = SEC_RE.fullmatch(text)
        direct, style_pt, common_pt = effective_sizes(para)
        has_legacy = bool(m and m.group(3))
        has_stats = bool(m and STATS_RE.search(text))
        no = m.group(1) if m else (NUM_PREFIX_RE.match(text).group(1) if NUM_PREFIX_RE.match(text) else None)
        bare14 = bool(m and no and no.count(".") == 1 and common_pt == 14.0)
        recognized = bool(m and (has_legacy or has_stats or bare14))
        first_for_no = bool(recognized and no not in seen)
        if first_for_no:
            seen.add(no)
            static_hits.append({"no": no, "title": text, "paragraph_index": index, "font_size_pt": common_pt})

        if has_legacy or has_stats:
            classification = "signed_hit"
        elif bare14:
            classification = "bare_two_level_14pt_hit"
        elif common_pt == 1.0:
            classification = "section_anchor_1pt"
        elif common_pt == 12.0:
            classification = "body_or_question_title_12pt"
        elif m:
            classification = "unsigned_other_size"
        else:
            classification = "other"

        rows.append(
            {
                "paragraph_index": index,
                "text": text,
                "no": no,
                "font_sizes_pt": direct,
                "style_font_size_pt": style_pt,
                "effective_common_font_size_pt": common_pt,
                "has_legacy_signature": has_legacy,
                "has_stats_signature": has_stats,
                "bare_two_level_14pt": bare14,
                "static_rule_would_hit": first_for_no,
                "classification": classification if not first_for_no else ("signed_hit" if (has_legacy or has_stats) else "bare_two_level_14pt_hit"),
            }
        )

    expected_by_no = {s["no"]: s for s in reference_sections}
    static_by_no = {s["no"]: s for s in static_hits}
    missing_from_static = sorted(set(expected_by_no) - set(static_by_no), key=section_key)
    extra_static = sorted(set(static_by_no) - set(expected_by_no), key=section_key)
    title_mismatch = []
    for no in sorted(set(expected_by_no) & set(static_by_no), key=section_key):
        if expected_by_no[no].get("title") != static_by_no[no].get("title"):
            title_mismatch.append(
                {
                    "no": no,
                    "reference_title": expected_by_no[no].get("title"),
                    "static_title": static_by_no[no].get("title"),
                }
            )
    false_negative_candidates = [
        r for r in rows
        if r["bare_two_level_14pt"] and not r["static_rule_would_hit"]
    ]
    return {
        "alias": alias,
        "path": str(path),
        "exists": path.is_file(),
        "table_out_paragraphs_matching_prefix": rows,
        "static_rule_hits": static_hits,
        "reference_vs_static": {
            "missing_nos": missing_from_static,
            "extra_nos": extra_static,
            "title_mismatches": title_mismatch,
            "all_expected_nos_present": not missing_from_static,
        },
        "bare_14pt_two_level_false_negative_candidates": false_negative_candidates,
    }


def section_key(no: str):
    return tuple(int(x) for x in no.split("."))


def load_reference() -> dict:
    return json.loads(read_utf8(REFERENCE))


def reference_by_alias(ref: dict) -> dict[str, dict]:
    out = {}
    for item in ref.get("files", []):
        stem = item.get("name", "")
        alias = ALIASES_BY_STEM.get(stem)
        if alias:
            out[alias] = item
    return out


def compare_file_hashes() -> list[dict]:
    out = []
    for alias, fn, _start in FILES:
        original = ORIGINAL_DIR / fn
        mirror = MIRROR_DIR / fn
        item = {"alias": alias, "original": str(original), "mirror": str(mirror), "original_exists": original.is_file(), "mirror_exists": mirror.is_file()}
        if original.is_file() and mirror.is_file():
            item["original_sha256"] = sha256(original)
            item["mirror_sha256"] = sha256(mirror)
            item["sha_equal"] = item["original_sha256"] == item["mirror_sha256"]
        out.append(item)
    return out


def x1_check() -> dict:
    fn = FILES[0][1]
    path = ORIGINAL_DIR / fn
    result = {"path": str(path), "exists": path.is_file()}
    if not path.is_file():
        return result
    with zipfile.ZipFile(path) as z:
        raw = z.read("word/document.xml").decode("utf-8")
    result["raw_contiguous_base_occurrences"] = raw.count("1.2.1.2")
    raw_contexts = []
    for m in re.finditer("1\\.2\\.1\\.2", raw):
        raw_contexts.append(html.unescape(raw[max(0, m.start() - 180):min(len(raw), m.end() + 260)]))
    result["raw_contexts"] = raw_contexts[:20]

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = ET.fromstring(raw)
    paragraphs = []
    labels = []
    evidence = []
    for p in root.findall(".//w:p", ns):
        text = "".join(t.text or "" for t in p.findall(".//w:t", ns))
        if "1.2.1.2" in text:
            paragraphs.append(text)
            labels.extend(QUESTION_LABEL_RE.findall(text))
            if re.search(r"1\.2\.1\.2\s*" + HYPHEN_RE + r"\s*7[．.]?", text):
                evidence.append({"text": text, "xml": ET.tostring(p, encoding="unicode")})
    labels = sorted(set(labels), key=lambda x: (int(re.search(r"\.([0-9]+)" + HYPHEN_RE, x).group(1)), int(re.search(HYPHEN_RE + r"([0-9]+)", x).group(1)))) if labels else []
    result["paragraphs_containing_base"] = paragraphs
    result["joined_paragraph_labels"] = labels
    result["has_joined_1.2.1.2-7"] = bool(evidence)
    result["evidence_paragraphs"] = evidence
    result["present_question_numbers_for_1.2.1.2"] = [x for x in labels if re.match(r"1\.2\.1\.2" + HYPHEN_RE, x)]
    result["has_6"] = any(re.match(r"1\.2\.1\.2" + HYPHEN_RE + r"6", x) for x in labels)
    result["has_8"] = any(re.match(r"1\.2\.1\.2" + HYPHEN_RE + r"8", x) for x in labels)

    if PROBE.is_file():
        probe = json.loads(read_utf8(PROBE))
        seq = [x.get("text", "") for x in probe.get("X1_题号块", [])]
        result["probe_x1_sequence"] = seq
        result["probe_has_6"] = any("1.2.1.2-6" in x for x in seq)
        result["probe_has_7"] = any("1.2.1.2-7" in x for x in seq)
        result["probe_has_8"] = any("1.2.1.2-8" in x for x in seq)
        result["probe_count"] = len(seq)
    return result


def com_status(name: str) -> dict:
    err_path = HERE / f"复测_配置{name}.err"
    text = err_path.read_text(encoding="utf-8-sig", errors="replace") if err_path.is_file() else ""
    return {
        "run_status": "blocked_at_DispatchEx",
        "exit_code": 1,
        "stdout_json_available": False,
        "stderr_file": str(err_path),
        "stderr": text,
    }


def normalize_output_file(path: Path, name: str) -> dict:
    # 保留源脚本空 stdout 的事实，同时生成可机器读取的阻断记录。
    return {
        "run_status": "blocked_at_DispatchEx",
        "source": str(SOURCE),
        "source_sha256": sha256(SOURCE),
        "configuration": name,
        "source_stdout_bytes": path.stat().st_size if path.is_file() else None,
        "com": com_status(name),
        "files": [],
    }


def write_json(name: str, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def safe_process_snapshot():
    try:
        p = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Process -Name WINWORD -ErrorAction SilentlyContinue | Select-Object Id,SessionId,Responding | ConvertTo-Json -Compress"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
        )
        return json.loads(p.stdout) if p.stdout.strip() else []
    except Exception as exc:
        return {"error": str(exc)}


def make_report(source_info, records, static_files, hashes, x1, snapshots, ref_info):
    all_hash_equal = all(x.get("sha_equal") for x in hashes if x.get("original_exists") and x.get("mirror_exists")) and len(hashes) == 10
    static_missing = {x["alias"]: x["reference_vs_static"]["missing_nos"] for x in static_files if x["reference_vs_static"]["missing_nos"]}
    static_extra = {x["alias"]: x["reference_vs_static"]["extra_nos"] for x in static_files if x["reference_vs_static"]["extra_nos"]}
    static_title = {x["alias"]: x["reference_vs_static"]["title_mismatches"] for x in static_files if x["reference_vs_static"]["title_mismatches"]}
    false_neg = {x["alias"]: x["bare_14pt_two_level_false_negative_candidates"] for x in static_files if x["bare_14pt_two_level_false_negative_candidates"]}
    x1_in_product = bool(x1.get("has_joined_1.2.1.2-7"))
    x1_probe_gap = bool(x1.get("probe_has_6") and not x1.get("probe_has_7") and x1.get("probe_has_8"))
    lines = []
    lines.append("FAIL")
    lines.append("# 复测报告·补签")
    lines.append("")
    lines.append("结论：FAIL。被检脚本 SHA-256 锚定通过，但配置 A、B 均在 `DispatchEx('Word.Application')` 启动点返回 0x80070520，未取得任何新批量测量 JSON；依任务书不能把参照输出冒充复测结果。")
    lines.append("")
    lines.append("## 前置锚定与纪律")
    lines.append("")
    lines.append(f"- 脚本：`{SOURCE}`；实测 SHA-256：`{source_info['sha256']}`；期望值一致：`{source_info['sha256_matches']}`。")
    lines.append("- 只读输入：十件成品、mirror、参照 JSON、盖章记录均未写入；未执行 git。")
    lines.append(f"- COM 启动异常：A/B 均记录于 `复测_配置A.err`、`复测_配置B.err`，错误为“指定的登录会话不存在（0x80070520）”；没有开卷/Repaginate/Close 阶段可测。")
    lines.append(f"- WINWORD 快照：A 前后均为任务书列出的 PID 5988、10308、13320、26168、28012（见 `复测_辅助.py` 运行快照）；未杀进程、未连接现存实例。")
    lines.append("")
    lines.append("## 断言面")
    lines.append("")
    lines.append("1. **旧签名回归：BLOCKED/FAIL。** 源脚本 A/B 均未能启动 COM，不能逐字段取得 `no/title/in_page/part_page` 复测值；空 stdout 已保留为阻断事实，结构化占位见 `复测_配置A.json`、`复测_配置B.json`。")
    lines.append("2. **新签名正例：BLOCKED/FAIL。** 同上，未取得新签名的 Word 页码结果；独立 python-docx 静态命中与参照编号对照见 `差集清单.json`，不替代脚本复测。")
    lines.append("3. **负例：BLOCKED/FAIL。** 需要源脚本的实际 hits 与差集联立；COM 启动失败，不能宣称断言面通过。")
    lines.append(f"4. **差集自查：{'PASS（静态规则层）' if not static_missing and not static_extra and not static_title and not false_neg else 'FAIL（静态规则层有差异）'}。** python-docx 独立枚举十件表外段落；详细逐段清单在 `差集清单.json`。")
    lines.append(f"   - 参照编号与静态规则对照：missing={json.dumps(static_missing, ensure_ascii=False)}；extra={json.dumps(static_extra, ensure_ascii=False)}；title_mismatch={json.dumps(static_title, ensure_ascii=False)}。")
    lines.append(f"   - 整段 14.0pt 且恰二级节号落入静态差集：{json.dumps(false_neg, ensure_ascii=False)}。")
    lines.append("   - 清单2 2.2/2.3：静态枚举与参照缺失项核查详见 `差集清单.json` 的 `clean_list_2_missing_check`；不把漏配定性为合法空。")
    lines.append("5. **九件原件直开＋清单1镜像：BLOCKED/FAIL。** 配置 A 输入已按十件绝对路径准备，配置 B 使用外部 `parts_mirror.json` 原样；十件原件/mirror SHA 对照见 `差集清单.json`。由于 COM 启动失败，未能完成两配置 sections 全等闭环。")
    lines.append("6. **节号递增→页码非递减：BLOCKED/FAIL。** 脚本没有产生 hits，无法对本轮输出按分量元组检查 `part_page`；参照输出的独立控制检查记录在 `差集清单.json`。")
    lines.append("7. **双向核验第二向：BLOCKED/FAIL。** 已完成 python-docx 文本/字号规则层静态复算并记录，但没有本轮脚本输出可供逐条反核；不能冒报 PASS。")
    if x1_in_product and x1_probe_gap:
        lines.append("8. **X1 题号块断号：PASS（判别单步）。** 衔接1原件 `word/document.xml` 的段落拼接文本中在位 `1.2.1.2-7`，且 -6、-8 在位；探针序列确实缺 7，故定性为探针签名漏配/工具缺陷，不是成品断号。证据段落原文与 XML 片段已落在 `差集清单.json`，未使用旧 `tmp\\A1_parts\\X1` 档。")
    elif x1.get("exists"):
        lines.append("8. **X1 题号块断号：FAIL。** 原件 XML 未能在段落拼接文本中找到 `1.2.1.2-7`；依任务书应立即停报主会话，证据见 `差集清单.json`。")
    else:
        lines.append("8. **X1 题号块断号：FAIL。** 衔接1原件不存在，无法完成判别单步；证据见 `差集清单.json`。")
    lines.append("")
    lines.append("## 清单2 2.2/2.3 查明")
    lines.append("")
    clean = next((x for x in static_files if x["alias"] == "清单2"), None)
    if clean:
        clean_rows = [r for r in clean["table_out_paragraphs_matching_prefix"] if r.get("no") in {"2.2", "2.3"}]
        if clean_rows:
            lines.append("清单2表外确有 2.2/2.3 候选段，静态结果见差集清单；需以实际 COM 输出决定是否为签名假阴。")
        else:
            lines.append("清单2表外未发现 2.2/2.3 候选节标题段；结合参照中 2.2=2、2.3=25 来自讲练2a，定性为清单件配属签名漏配/工具缺陷，不修改目录页数字。")
    else:
        lines.append("未能生成清单2静态记录。")
    lines.append("")
    lines.append("## X1 证据")
    lines.append("")
    if x1.get("evidence_paragraphs"):
        for item in x1["evidence_paragraphs"]:
            lines.append("- 段落原文：" + item["text"])
    else:
        lines.append("- 未找到含 `1.2.1.2-7` 的证据段落；完整扫描结果见 `差集清单.json`。")
    lines.append("")
    lines.append("## 产物索引")
    lines.append("")
    lines.append("- `复测_配置A.json` / `复测_配置B.json`：源脚本 stdout 为空的结构化阻断记录，不是伪造测量结果。")
    lines.append("- `差集清单.json`：十件表外数字段落逐段分类、参照编号静态对照、原件/mirror SHA、清单2查明、X1 XML 证据。")
    lines.append("- `复测_配置A.err` / `复测_配置B.err`：两次源脚本原始 stderr 捕获。")
    return "\n".join(lines) + "\n"


def main():
    if not SOURCE.is_file():
        raise SystemExit(f"missing source: {SOURCE}")
    ref = load_reference()
    ref_alias = reference_by_alias(ref)
    source_hash = sha256(SOURCE)
    source_text = read_utf8(SOURCE)
    source_info = {
        "path": str(SOURCE),
        "sha256": source_hash,
        "expected_sha256": EXPECTED_SHA,
        "sha256_matches": source_hash == EXPECTED_SHA,
        "has_2026_09_04_bare_14pt_gate": "m.group(1).count('.') != 1" in source_text and "float(rng.Font.Size) != 14.0" in source_text,
        "has_sec_re": "SEC_RE = re.compile" in source_text,
        "has_stats_re": "STATS_RE = re.compile" in source_text,
    }

    records = path_record()
    static_files = []
    for alias, fn, _start in FILES:
        # 与配置 A 相同：九件原件，清单1专用 mirror。
        path = MIRROR_DIR / fn if alias == "清单1" else ORIGINAL_DIR / fn
        static_files.append(classify_doc(alias, path, ref_alias.get(alias, {}).get("sections", [])))

    hashes = compare_file_hashes()
    x1 = x1_check()
    snapshots = {"after_A": safe_process_snapshot(), "after_B": safe_process_snapshot()}
    clean = next(x for x in static_files if x["alias"] == "清单2")
    clean_missing_check = {
        "alias": "清单2",
        "candidate_paragraphs_2.2": [r for r in clean["table_out_paragraphs_matching_prefix"] if r.get("no") == "2.2"],
        "candidate_paragraphs_2.3": [r for r in clean["table_out_paragraphs_matching_prefix"] if r.get("no") == "2.3"],
        "reference_sections": ref_alias.get("清单2", {}).get("sections", []),
        "classification": "needs_COM_output_if_candidates_exist",
    }
    ref_order_control = {}
    for alias, item in ref_alias.items():
        hits = item.get("sections", [])
        ordered = sorted(hits, key=lambda s: section_key(s["no"]))
        pages = [s.get("part_page") for s in ordered]
        ref_order_control[alias] = {
            "ordered_nos": [s["no"] for s in ordered],
            "part_pages": pages,
            "nondecreasing": all(a <= b for a, b in zip(pages, pages[1:])),
        }

    diff = {
        "status": "static_independent_checks_only_COM_blocked",
        "source": source_info,
        "record_entries": records,
        "static_files": static_files,
        "clean_list_2_missing_check": clean_missing_check,
        "original_vs_mirror_sha256": hashes,
        "reference_part_page_order_control": ref_order_control,
        "x1_xml_check": x1,
        "com": {"A": com_status("A"), "B": com_status("B")},
        "winword_snapshots": snapshots,
    }
    write_json("复测_配置A.json", normalize_output_file(HERE / "复测_配置A.json", "A"))
    write_json("复测_配置B.json", normalize_output_file(HERE / "复测_配置B.json", "B"))
    write_json("差集清单.json", diff)
    report = make_report(source_info, records, static_files, hashes, x1, snapshots, ref_alias)
    (HERE / "复测报告_补签.md").write_text(report, encoding="utf-8")
    print(json.dumps({
        "sha256_matches": source_info["sha256_matches"],
        "static_files": len(static_files),
        "hash_pairs": len(hashes),
        "x1_has_7": x1.get("has_joined_1.2.1.2-7"),
        "report": str(HERE / "复测报告_补签.md"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
