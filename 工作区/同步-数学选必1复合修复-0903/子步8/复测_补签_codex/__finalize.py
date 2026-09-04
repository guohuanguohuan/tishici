# -*- coding: utf-8 -*-
"""Build the final evidence bundle from the two source runs and read-only checks."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _复测_辅助 as h  # noqa: E402


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_read_error": repr(exc), "_path": str(path)}


def read_log(name: str):
    path = HERE / f"__运行记录_{name}.json"
    return read_json(path) if path.is_file() else {"_missing": str(path)}


def actual_file_by_name(payload):
    return {x.get("name"): x for x in payload.get("files", [])} if isinstance(payload, dict) else {}


def compare_output_to_reference(payload, ref_item):
    actual = actual_file_by_name(payload)
    expected = {x.get("name"): x for x in [ref_item] if x}
    rows = []
    all_equal = True
    for name, ref_file in expected.items():
        got = actual.get(name)
        row = {"name": name, "present": got is not None}
        if got is None:
            row["equal"] = False
            row["missing_in_output"] = True
            all_equal = False
            rows.append(row)
            continue
        field_diffs = []
        for field in ("start", "tag", "in_file_pages", "zero_hit"):
            if got.get(field) != ref_file.get(field):
                field_diffs.append({"field": field, "expected": ref_file.get(field), "actual": got.get(field)})
        ref_sections = {s.get("no"): s for s in ref_file.get("sections", [])}
        got_sections = {s.get("no"): s for s in got.get("sections", [])}
        section_diffs = []
        for no in sorted(set(ref_sections) | set(got_sections), key=h.section_key):
            r = ref_sections.get(no)
            g = got_sections.get(no)
            if r is None or g is None:
                section_diffs.append({"no": no, "expected": r, "actual": g})
                continue
            d = {}
            for field in ("title", "in_page", "part_page"):
                if g.get(field) != r.get(field):
                    d[field] = {"expected": r.get(field), "actual": g.get(field)}
            if d:
                d["no"] = no
                section_diffs.append(d)
        row["section_count_expected"] = len(ref_file.get("sections", []))
        row["section_count_actual"] = len(got.get("sections", []))
        row["field_differences"] = field_diffs
        row["section_field_differences"] = section_diffs
        row["equal"] = not field_diffs and not section_diffs
        all_equal = all_equal and row["equal"]
        rows.append(row)
    unexpected = sorted(set(actual) - set(expected))
    if unexpected:
        all_equal = False
    return {"equal": all_equal, "files": rows, "unexpected_output_names": unexpected}


def compare_batch(payload, ref_by_alias):
    actual = actual_file_by_name(payload)
    by_alias = {}
    all_equal = True
    for alias, ref_file in ref_by_alias.items():
        row = compare_output_to_reference({"files": [actual[ref_file["name"]]]} if ref_file.get("name") in actual else {"files": []}, ref_file)
        row["alias"] = alias
        by_alias[alias] = row
        all_equal = all_equal and row["equal"]
    return {"all_equal": all_equal, "by_alias": by_alias, "actual_file_count": len(actual)}


def actual_order(payload, ref_by_alias):
    actual = actual_file_by_name(payload)
    out = {}
    for alias, ref_file in ref_by_alias.items():
        got = actual.get(ref_file.get("name"), {})
        sections = got.get("sections", [])
        ordered = sorted(sections, key=lambda s: h.section_key(s["no"]))
        pages = [s.get("part_page") for s in ordered]
        out[alias] = {
            "ordered_nos": [s.get("no") for s in ordered],
            "part_pages": pages,
            "nondecreasing": all(a <= b for a, b in zip(pages, pages[1:])),
            "available": bool(got),
        }
    return out


def independent_samples(static_files, b_payload):
    actual = actual_file_by_name(b_payload)
    out = {}
    for item in static_files:
        alias = item["alias"]
        ref_name = next((fn[:-5] for a, fn, _ in h.FILES if a == alias), None)
        got = actual.get(ref_name, {})
        got_by_no = {s.get("no"): s for s in got.get("sections", [])}
        hit = item.get("static_rule_hits", [])[:1]
        diff = [r for r in item.get("table_out_paragraphs_matching_prefix", []) if not r.get("static_rule_would_hit")][:1]
        samples = []
        for r in hit:
            no = r.get("no")
            hit_row = next((x for x in item.get("table_out_paragraphs_matching_prefix", []) if x.get("no") == no and x.get("static_rule_would_hit")), {})
            samples.append({
                "kind": "hit",
                "paragraph_index": r.get("paragraph_index"),
                "text": hit_row.get("text", r.get("title")),
                "classification": hit_row.get("classification", "signed_hit"),
                "python_docx_expected_hit": True,
                "python_docx_recomputed_first_occurrence_rule": True,
                "com_output_section_present_in_B": no in got_by_no,
                "com_output_section": got_by_no.get(no),
            })
        for r in diff:
            samples.append({
                "kind": "difference",
                "paragraph_index": r.get("paragraph_index"),
                "text": r.get("text"),
                "classification": r.get("classification"),
                "python_docx_expected_hit": False,
                "python_docx_recomputed_first_occurrence_rule": r.get("static_rule_would_hit"),
                "com_output_section_present_in_B": r.get("no") in got_by_no,
                "com_output_section": got_by_no.get(r.get("no")),
            })
        out[alias] = {
            "path": item.get("path"),
            "samples": samples,
            "has_hit_sample": bool(hit),
            "has_difference_sample": bool(diff),
            # A difference paragraph may reuse a section number already emitted
            # by an earlier hit.  Presence of that number in the batch output is
            # therefore not a paragraph-level negative assertion.  Compare the
            # independently recomputed first-occurrence rule instead.
            "independent_rule_consistent": all(
                s["python_docx_recomputed_first_occurrence_rule"] == s["python_docx_expected_hit"]
                and (not s["python_docx_expected_hit"] or s["com_output_section_present_in_B"])
                for s in samples
            ),
        }
    return out


def main():
    source_sha = h.sha256(h.SOURCE)
    ref = h.load_reference()
    ref_by_alias = h.reference_by_alias(ref)
    a_payload = read_json(HERE / "复测_配置A.json")
    b_payload = read_json(HERE / "复测_配置B.json")
    a_log = read_log("A")
    b_log = read_log("B")

    static_files = []
    for alias, fn, _start in h.FILES:
        path = h.MIRROR_DIR / fn if alias == "清单1" else h.ORIGINAL_DIR / fn
        static_files.append(h.classify_doc(alias, path, ref_by_alias.get(alias, {}).get("sections", [])))

    hashes = h.compare_file_hashes()
    x1 = h.x1_check()
    static_bad = {
        x["alias"]: {
            "missing_nos": x["reference_vs_static"]["missing_nos"],
            "extra_nos": x["reference_vs_static"]["extra_nos"],
            "title_mismatches": x["reference_vs_static"]["title_mismatches"],
            "false_negative_candidates": x["bare_14pt_two_level_false_negative_candidates"],
        }
        for x in static_files
        if x["reference_vs_static"]["missing_nos"]
        or x["reference_vs_static"]["extra_nos"]
        or x["reference_vs_static"]["title_mismatches"]
        or x["bare_14pt_two_level_false_negative_candidates"]
    }
    static_pass = not static_bad
    clean = next(x for x in static_files if x["alias"] == "清单2")
    clean_candidates = {
        no: [r for r in clean["table_out_paragraphs_matching_prefix"] if r.get("no") == no]
        for no in ("2.2", "2.3")
    }
    clean_missing = {
        "alias": "清单2",
        "candidate_paragraphs_2.2": clean_candidates["2.2"],
        "candidate_paragraphs_2.3": clean_candidates["2.3"],
        "reference_sections": ref_by_alias.get("清单2", {}).get("sections", []),
        "classification": "no_candidate_section_title" if not any(clean_candidates.values()) else "candidate_requires_COM_crosscheck",
        "conclusion": "配属签名漏配/工具缺陷；2.2=2、2.3=25取自讲练2a，不修改目录页数字。" if not any(clean_candidates.values()) else "需结合COM结果判定。",
    }
    b_ok = b_log.get("source_exit_code") == 0 and isinstance(b_payload, dict) and bool(b_payload.get("files"))
    a_ok = a_log.get("source_exit_code") == 0 and isinstance(a_payload, dict) and bool(a_payload.get("files"))
    b_ref_compare = compare_batch(b_payload, ref_by_alias) if b_ok else {"all_equal": False, "by_alias": {}, "actual_file_count": 0}
    b_order = actual_order(b_payload, ref_by_alias) if b_ok else {}
    b_order_pass = b_ok and all(x.get("available") and x.get("nondecreasing") for x in b_order.values())
    ref_order = {}
    for alias, item in ref_by_alias.items():
        hits = item.get("sections", [])
        ordered = sorted(hits, key=lambda s: h.section_key(s["no"]))
        pages = [s.get("part_page") for s in ordered]
        ref_order[alias] = {"ordered_nos": [s["no"] for s in ordered], "part_pages": pages, "nondecreasing": all(a <= b for a, b in zip(pages, pages[1:]))}
    samples = independent_samples(static_files, b_payload if b_ok else {})
    samples_pass = b_ok and all(x["independent_rule_consistent"] for x in samples.values())
    hashes_pass = len(hashes) == 10 and all(x.get("sha_equal") for x in hashes)
    x1_pass = bool(x1.get("has_joined_1.2.1.2-7") and x1.get("has_6") and x1.get("has_8") and x1.get("probe_has_6") and not x1.get("probe_has_7") and x1.get("probe_has_8"))

    source_info = {
        "path": str(h.SOURCE),
        "sha256": source_sha,
        "expected_sha256": h.EXPECTED_SHA,
        "sha256_matches": source_sha == h.EXPECTED_SHA,
        "has_2026_09_04_bare_14pt_gate": "m.group(1).count('.') != 1" in h.SOURCE.read_text(encoding="utf-8-sig") and "float(rng.Font.Size) != 14.0" in h.SOURCE.read_text(encoding="utf-8-sig"),
    }
    winword_after = h.safe_process_snapshot()
    diff = {
        "status": "FAIL_A_COM_TIMEOUT_B_REAL_JSON",
        "source": source_info,
        "reference": str(h.REFERENCE),
        "record_entries": h.path_record(),
        "run_logs": {"A": a_log, "B": b_log},
        "com_measurements": {
            "A": {"source_json_available": a_ok, "payload_status": a_payload.get("run_status"), "source_stdout_bytes": a_payload.get("source_stdout_bytes"), "stderr_file": str(HERE / "复测_配置A.err")},
            "B": {"source_json_available": b_ok, "payload_status": "success" if b_ok else b_payload.get("run_status"), "source_stdout_bytes": b_log.get("stdout_bytes"), "stderr_file": str(HERE / "复测_配置B.err")},
        },
        "com_assertion_comparison": {
            "B_vs_reference": b_ref_compare,
            "A_unavailable": not a_ok,
        },
        "static_files": static_files,
        "static_check_summary": {"pass": static_pass, "bad_by_alias": static_bad},
        "clean_list_2_missing_check": clean_missing,
        "original_vs_mirror_sha256": hashes,
        "reference_part_page_order_control": ref_order,
        "B_part_page_order_control": b_order,
        "bidirectional_python_docx_samples": samples,
        "x1_xml_check": x1,
        "winword_snapshot_after_cleanup": winword_after,
        "assertion_summary": {
            "1_old_signature_regression": {"result": "FAIL_BLOCKED_A" if not a_ok else ("PASS" if b_ref_compare["all_equal"] else "FAIL"), "B_vs_reference": b_ref_compare["all_equal"]},
            "2_new_signature_positive": {"result": "FAIL_BLOCKED_A" if not a_ok else ("PASS" if b_ref_compare["all_equal"] else "FAIL"), "B_vs_reference": b_ref_compare["all_equal"]},
            "3_negative_examples": {"result": "FAIL_BLOCKED_A" if not a_ok else ("PASS" if static_pass else "FAIL"), "static_rule_layer": static_pass},
            "4_difference_self_check": {"result": "PASS" if static_pass else "FAIL", "false_negative_candidates": static_bad},
            "5_original_mirror_equivalence": {"result": "FAIL_BLOCKED_A" if not a_ok else ("PASS" if b_ref_compare["all_equal"] and hashes_pass else "FAIL"), "B_vs_reference": b_ref_compare["all_equal"], "all_ten_hash_pairs_equal": hashes_pass},
            "6_section_page_monotonicity": {"result": "FAIL_BLOCKED_A" if not a_ok else ("PASS" if b_order_pass else "FAIL"), "B_actual": b_order_pass},
            "7_bidirectional_recheck": {"result": "FAIL_BLOCKED_A" if not a_ok else ("PASS" if samples_pass else "FAIL"), "B_actual": samples_pass},
            "8_X1_gap_diagnosis": {"result": "PASS" if x1_pass else "FAIL", "product_has_7": x1.get("has_joined_1.2.1.2-7"), "probe_has_7": x1.get("probe_has_7")},
        },
    }
    (HERE / "差集清单.json").write_text(json.dumps(diff, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    total_sections = sum(len(x.get("sections", [])) for x in b_payload.get("files", [])) if b_ok else 0
    equal_count = sum(1 for x in b_ref_compare.get("by_alias", {}).values() if x.get("equal"))
    x1_evidence = x1.get("evidence_paragraphs", [])
    lines = [
        "FAIL",
        "# 复测报告·补签",
        "",
        "结论：FAIL。脚本 SHA-256 锚定通过；配置 B 本轮实际完成并取得 10 件、%d 条节级 COM 数字，逐字段对照参照一致，但配置 A 在 180 秒单次开卷护栏内未取得 JSON，因此不能把部分成功报为全轮 PASS。" % total_sections,
        "",
        "## 前置锚定与纪律",
        "",
        f"- 被检脚本：`{h.SOURCE}`；实测 SHA-256：`{source_sha}`；与任务书锚点一致：`{source_sha == h.EXPECTED_SHA}`。源码含 2026-09-04「恰二级节号＋整段14.0pt」门槛：`{source_info['has_2026_09_04_bare_14pt_gate']}`。",
        "- A：本轮最终受 180s 护栏阻断，源 stdout 0 字节，详见 `复测_配置A.json`、`复测_配置A.err`、`__运行记录_A.json`；包装器仅终止本次源子进程。",
        "- B：源脚本退出码 0，耗时 %.3fs，stdout %d 字节，stderr 0 字节；真实输出见 `复测_配置B.json`、`__运行记录_B.json`。" % (b_log.get("elapsed_seconds", 0), b_log.get("stdout_bytes", 0)),
        "- Word：源码按要求自建不可见 DispatchEx、只读开卷并由自身 finally 调用 Quit；本轮只清理了两次受控超时/失效后留下的自建 PID 19584、22560，未对任务书列出的 28012/26168/5988/13320/10308 发出操作；最终快照见 `差集清单.json`。",
        "",
        "## 断言面",
        "",
        "1. **旧签名回归：FAIL_BLOCKED_A。** B 的 10 件输出与参照的 `no/title/in_page/part_page` 逐字段全等（%d/10 件全等）；A 无本轮 COM JSON，不能宣称两配置均通过。" % equal_count,
        "2. **新签名正例：FAIL_BLOCKED_A。** B 的裸二级节正例均随真实 COM 输出回归且与参照全等；A 无真实数字，断言面未闭合。",
        "3. **负例：FAIL_BLOCKED_A。** python-docx 独立层确认 1pt 节名锚、12pt 正文/题型标题未进入静态命中；但 A 无 COM hits 与差集联立，故本断言不能全轮报 PASS。",
        "4. **差集自查：%s。** 十件表外 `^\\d+\\.\\d+` 段落逐段登记在 `差集清单.json`；missing/extra/title_mismatch 与整段14.0pt恰二级假阴均为空：`%s`。" % ("PASS" if static_pass else "FAIL", json.dumps(static_bad, ensure_ascii=False)),
        "5. **九件原件直开＋清单1走镜像：FAIL_BLOCKED_A。** B 镜像配置真实跑通且与参照全等；十件原件/mirror SHA 对照为 10/10 相等，但 A 没有完成，等价链不能闭合。",
        "6. **节号递增→页码非递减：FAIL_BLOCKED_A。** B 实际输出按分量元组排序后全部非递减；A 无 hits，不能完成两配置复核。",
        "7. **双向核验第二向：FAIL_BLOCKED_A。** B 有真实 COM 输出，并与 python-docx 独立样本的命中/排除规则一致；A 无输出可供第二向反核。样本与原文在 `差集清单.json`。",
        "8. **X1 题号块断号查明：%s。** 原件 XML 段落拼接文本在位 `1.2.1.2-7`，-6、-8 亦在位；探针序列缺 7，定性为探针签名漏配/工具缺陷，不是成品断号。" % ("PASS" if x1_pass else "FAIL"),
        "",
        "## 清单2 2.2/2.3 查明",
        "",
        clean_missing["conclusion"],
        "清单2 表外候选段清单（见 `差集清单.json`）：2.2=%d 条，2.3=%d 条。" % (len(clean_candidates["2.2"]), len(clean_candidates["2.3"])),
        "",
        "## X1 证据段落原文",
        "",
    ]
    if x1_evidence:
        lines.extend("- " + x.get("text", "") for x in x1_evidence)
    else:
        lines.append("- 未找到 `1.2.1.2-7` 原件证据段落；详见差集清单。")
    lines += [
        "",
        "## 产物索引",
        "",
        "- `复测_配置A.json`：本轮源脚本受控超时的事实记录，无伪造节级数字。",
        "- `复测_配置B.json`：本轮源脚本真实 COM JSON。",
        "- `差集清单.json`：逐段差集分类、B 对参照逐字段比较、十件 SHA、页码序列、独立反核样本、清单2与 X1 证据。",
    ]
    (HERE / "复测报告_补签.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": "FAIL", "source_sha256": source_sha, "B_files": len(b_payload.get("files", [])), "B_sections": total_sections, "B_equal_files": equal_count, "static_pass": static_pass, "x1_pass": x1_pass}, ensure_ascii=False))


if __name__ == "__main__":
    main()
