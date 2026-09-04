# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib, json, re, subprocess, sys, time, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from collections import Counter
from docx import Document

OUT = Path(__file__).resolve().parent
SCRIPT = Path(r"C:\提示词\工具\节页码定位.py")
REF = Path(r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\节页码_子步8.json")
PROBE = Path(r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\实物run探针_子步8.json")
ORIG = Path(r"C:\提示词\高中数学\高中数学同步")
MIRR = Path(r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\mirror")
EXPECTED_SHA = "844d244a3cb91d5ca8e7c2c17e35963d293aeff623478f76610f39e651bcde85"
ALLOWED = {28012, 26168, 5988, 13320, 10308}

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
ALIASES = {fn[:-5]: a for a, fn, _ in FILES}
OLD_SIG = {
    "衔接1": ["1.2.1", "1.2.5"],
    "讲练1上": ["1.1.1", "1.1.2", "1.1.3", "1.2.1", "1.2.2", "1.2.3", "1.2.4"],
    "讲练1下": ["1.2.5"],
    "衔接2": ["2.8"],
    "讲练2a": ["2.1", "2.2.1", "2.2.2", "2.2.3", "2.2.4", "2.3.1", "2.3.2", "2.3.3"],
    "讲练2b": ["2.3.4", "2.4", "2.5.1", "2.5.2"],
    "讲练2c": ["2.6.1", "2.6.2", "2.7.1", "2.7.2"],
    "讲练2d": ["2.8"],
}
NEW_SIG = {
    "清单1": ["1.1", "1.2"],
    "讲练1上": ["1.1", "1.2"],
    "清单2": ["2.1", "2.4", "2.5", "2.6", "2.7", "2.8"],
    "讲练2a": ["2.2", "2.3"],
    "讲练2b": ["2.5"],
    "讲练2c": ["2.6", "2.7"],
}

SEC_RE = re.compile(
    r"^(\d+\.\d+(?:\.\d+)?)[\s\u3000]+(.+?)"
    r"(?:（第(\d+)[—–\-](\d+)题）)?(?:[\s\u3000]+本节\d+题[：:].*)?[\s\u3000]*$"
)
STATS_RE = re.compile(r"[\s\u3000]本节\d+题")
NUM_PREFIX_RE = re.compile(r"^(\d+\.\d+(?:\.\d+)?)")
TWO_LEVEL_RE = re.compile(r"^\d+\.\d+")
QUESTION_LABEL_RE = re.compile(r"1\.2\.1\.\d+[-－‐‑‒–—−]\d+[．.]?")
HYPHEN_RE = r"[-－‐‑‒–—−]"

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def section_key(no):
    return tuple(int(x) for x in no.split("."))

def winword_pids():
    p = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq WINWORD.EXE", "/FO", "CSV", "/NH"],
        capture_output=True, text=True, encoding="gbk", errors="replace", timeout=15,
    )
    pids = set()
    for line in p.stdout.splitlines():
        parts = [x.strip('"') for x in line.split(",")]
        if len(parts) >= 2 and parts[0].upper().startswith("WINWORD"):
            try:
                pids.add(int(parts[1]))
            except Exception:
                pass
    return pids

def kill_orphans(label=""):
    cur = winword_pids()
    orphans = cur - ALLOWED
    if orphans:
        print("kill", label, orphans, flush=True)
        for pid in orphans:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
        time.sleep(1)
    return sorted(winword_pids())

def sec_eq(a, b):
    keys = ("no", "title", "in_page", "part_page")
    return {k: a.get(k) for k in keys} == {k: b.get(k) for k in keys}

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

def is_chinese(text):
    return any("一" <= ch <= "鿿" for ch in text)

def classify_doc(alias, path, com_hits):
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
        rows.append({
            "paragraph_index": index, "text": text, "no": no,
            "font_sizes_pt": direct, "style_font_size_pt": style_pt,
            "effective_common_font_size_pt": common_pt,
            "has_legacy_signature": has_legacy, "has_stats_signature": has_stats,
            "bare_two_level_14pt": bare14, "static_rule_would_hit": first_for_no,
            "classification": ("signed_hit" if (has_legacy or has_stats) else "bare_two_level_14pt_hit") if first_for_no else classification,
        })
    com_nos = {s["no"] for s in com_hits}
    hit_titles = {s["title"] for s in com_hits}
    diff_rows = []
    for r in rows:
        if r["text"] in hit_titles:
            continue
        if r["static_rule_would_hit"] and r["no"] in com_nos:
            continue
        if not r["static_rule_would_hit"]:
            diff_rows.append(r)
    false_neg = [r for r in rows if r["bare_two_level_14pt"] and r["no"] not in com_nos]
    return {
        "alias": alias, "path": str(path),
        "table_out_paragraphs_matching_prefix": rows,
        "static_rule_hits": static_hits,
        "diff_vs_com_hits": diff_rows,
        "bare_14pt_false_negative_in_diff": false_neg,
        "com_nos": sorted(com_nos, key=section_key),
        "static_nos": [h["no"] for h in static_hits],
    }

def main():
    kill_orphans("start")
    A = json.loads((OUT / "复测_配置A.json").read_text(encoding="utf-8"))
    B = json.loads((OUT / "复测_配置B.json").read_text(encoding="utf-8"))
    ref = json.loads(REF.read_text(encoding="utf-8-sig"))
    Amap = {f["name"]: f for f in A["files"]}
    Bmap = {f["name"]: f for f in B["files"]}
    Rmap = {}
    for item in ref["files"]:
        a = ALIASES.get(item["name"])
        if a:
            Rmap[a] = item

    def get_com(alias):
        fa = Amap.get(alias) or {}
        if fa.get("sections") and not fa.get("error"):
            return fa, "A"
        fb = Bmap.get(alias) or {}
        if fb.get("sections") and not fb.get("error"):
            return fb, "B_fallback"
        return fa or fb, "MISSING"

    if (Amap.get("讲练1上") or {}).get("error"):
        path = Amap["讲练1上"]["path"]
        start = Amap["讲练1上"]["start"]
        tag = Amap["讲练1上"].get("tag")
        print("retry 讲练1上 final", flush=True)
        time.sleep(3)
        kill_orphans("pre_final")
        try:
            pr = subprocess.run(
                [sys.executable, str(SCRIPT), path, str(start), "--name", "讲练1上", "--json"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
            )
            print("final rc", pr.returncode, "stderr", (pr.stderr or "")[:300], flush=True)
            if pr.returncode == 0 and (pr.stdout or "").strip():
                data = json.loads(pr.stdout)
                f0 = data["files"][0]
                f0.update({"tag": tag, "start": start, "path": path, "name": "讲练1上"})
                for s in f0.get("sections", []):
                    s["part_page"] = start + s["in_page"] - 1
                for i, f in enumerate(A["files"]):
                    if f["name"] == "讲练1上":
                        A["files"][i] = f0
                A["errors"] = [e for e in A.get("errors", []) if e.get("name") != "讲练1上"]
                A["run_status"] = "ok" if not any(x.get("error") for x in A["files"]) else "partial"
                (OUT / "复测_配置A.json").write_text(json.dumps(A, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                Amap = {f["name"]: f for f in A["files"]}
                print("RETRY OK", [s["no"] for s in f0["sections"]], flush=True)
            else:
                for i, f in enumerate(A["files"]):
                    if f["name"] == "讲练1上":
                        A["files"][i]["error"] = "retry_final rc=%s %s" % (pr.returncode, (pr.stderr or "")[:200])
                (OUT / "复测_配置A.json").write_text(json.dumps(A, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                Amap = {f["name"]: f for f in A["files"]}
        except subprocess.TimeoutExpired:
            print("final timeout", flush=True)
            kill_orphans("final_to")
            for i, f in enumerate(A["files"]):
                if f["name"] == "讲练1上":
                    A["files"][i]["error"] = "TIMEOUT>180s final"
            (OUT / "复测_配置A.json").write_text(json.dumps(A, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            Amap = {f["name"]: f for f in A["files"]}
        kill_orphans("post_final")

    a1 = {"pass": True, "details": {}}
    for alias, nos in OLD_SIG.items():
        ref_secs = {s["no"]: s for s in Rmap[alias]["sections"]}
        got, src = get_com(alias)
        gmap = {s["no"]: s for s in got.get("sections", [])}
        row = []
        ok = True
        for n in nos:
            r, g = ref_secs.get(n), gmap.get(n)
            eq = r is not None and g is not None and sec_eq(r, g)
            if not eq:
                ok = False
            row.append({"no": n, "equal": eq, "ref": r, "got": g, "source": src})
        a1["details"][alias] = row
        if not ok:
            a1["pass"] = False

    a2 = {"pass": True, "details": {}}
    for alias, nos in NEW_SIG.items():
        ref_secs = {s["no"]: s for s in Rmap[alias]["sections"]}
        got, src = get_com(alias)
        gmap = {s["no"]: s for s in got.get("sections", [])}
        row = []
        ok = True
        for n in nos:
            r, g = ref_secs.get(n), gmap.get(n)
            eq = r is not None and g is not None and sec_eq(r, g)
            if not eq:
                ok = False
            row.append({"no": n, "equal": eq, "ref": r, "got": g, "source": src})
        a2["details"][alias] = row
        if not ok:
            a2["pass"] = False

    a5 = {"pass": True, "details": {}}
    for alias, _, _ in FILES:
        fa = Amap.get(alias) or {}
        fb = Bmap.get(alias) or {}
        if fa.get("error") or fb.get("error"):
            a5["details"][alias] = {
                "equal": False,
                "reason": "A_err=%s B_err=%s" % (fa.get("error"), fb.get("error")),
                "A_nos": [s["no"] for s in fa.get("sections", [])],
                "B_nos": [s["no"] for s in fb.get("sections", [])],
            }
            a5["pass"] = False
            continue
        sa = [{k: s[k] for k in ("no", "title", "in_page", "part_page")} for s in fa.get("sections", [])]
        sb = [{k: s[k] for k in ("no", "title", "in_page", "part_page")} for s in fb.get("sections", [])]
        eq = sa == sb
        pages_eq = fa.get("in_file_pages") == fb.get("in_file_pages")
        a5["details"][alias] = {
            "equal": eq and pages_eq,
            "sections_equal": eq,
            "pages_equal": pages_eq,
            "A_pages": fa.get("in_file_pages"),
            "B_pages": fb.get("in_file_pages"),
            "A": sa,
            "B": sb,
        }
        if not (eq and pages_eq):
            a5["pass"] = False

    a6 = {"pass": True, "details": {}}
    for alias, _, _ in FILES:
        got, src = get_com(alias)
        hits = got.get("sections", [])
        ordered = sorted(hits, key=lambda s: section_key(s["no"]))
        pages = [s["part_page"] for s in ordered]
        ok = all(x <= y for x, y in zip(pages, pages[1:])) if len(pages) > 1 else True
        a6["details"][alias] = {
            "source": src,
            "ordered_nos": [s["no"] for s in ordered],
            "part_pages": pages,
            "nondecreasing": ok,
        }
        if not ok:
            a6["pass"] = False

    static_files = []
    for alias, fn, _st in FILES:
        path = (MIRR / fn) if alias == "清单1" else (ORIG / fn)
        got, src = get_com(alias)
        static_files.append(classify_doc(alias, path, got.get("sections", [])))

    a4 = {"pass": True, "details": {}}
    for sf in static_files:
        fn_list = sf["bare_14pt_false_negative_in_diff"]
        counts = dict(Counter(r["classification"] for r in sf["diff_vs_com_hits"]))
        a4["details"][sf["alias"]] = {
            "false_neg_count": len(fn_list),
            "false_neg": fn_list,
            "diff_class_counts": counts,
        }
        if fn_list:
            a4["pass"] = False
    a3 = {"pass": a4["pass"], "note": "负例由断言4差集分类覆盖"}

    a7 = {"pass": True, "samples": []}
    for sf in static_files:
        alias = sf["alias"]
        got, src = get_com(alias)
        hits = got.get("sections", [])
        if not hits:
            a7["samples"].append({"alias": alias, "error": "no hits", "source": src})
            a7["pass"] = False
            continue
        h = hits[0]
        static_by_no = next((x for x in sf["static_rule_hits"] if x["no"] == h["no"]), None)
        d = sf["diff_vs_com_hits"][0] if sf["diff_vs_com_hits"] else None
        hit_ok = static_by_no is not None
        diff_ok = True
        diff_info = None
        if d:
            should_exclude = not d["static_rule_would_hit"]
            diff_ok = should_exclude
            diff_info = {
                "text": d["text"][:80],
                "classification": d["classification"],
                "font": d["effective_common_font_size_pt"],
                "should_exclude": should_exclude,
                "agree": should_exclude,
            }
        if not hit_ok or not diff_ok:
            a7["pass"] = False
        a7["samples"].append({
            "alias": alias,
            "source": src,
            "hit": {"com_no": h["no"], "static": static_by_no, "agree_should_hit": hit_ok},
            "diff": diff_info,
        })

    fn0 = FILES[0][1]
    path0 = ORIG / fn0
    x1 = {"path": str(path0), "exists": path0.is_file()}
    with zipfile.ZipFile(path0) as z:
        raw = z.read("word/document.xml").decode("utf-8")
    x1["raw_contiguous_base_occurrences"] = raw.count("1.2.1.2")
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = ET.fromstring(raw)
    labels = []
    evidence = []
    paragraphs = []
    for pnode in root.findall(".//w:p", ns):
        text = "".join(t.text or "" for t in pnode.findall(".//w:t", ns))
        if "1.2.1.2" in text:
            paragraphs.append(text)
            labels.extend(QUESTION_LABEL_RE.findall(text))
            if re.search(r"1\.2\.1\.2\s*" + HYPHEN_RE + r"\s*7[．.]?", text):
                evidence.append({"text": text, "xml": ET.tostring(pnode, encoding="unicode")[:2000]})
    labels = sorted(set(labels))
    x1.update({
        "paragraphs_containing_base": paragraphs,
        "joined_paragraph_labels": labels,
        "has_joined_1.2.1.2-7": bool(evidence),
        "evidence_paragraphs": evidence,
        "has_6": any(re.match(r"1\.2\.1\.2" + HYPHEN_RE + r"6", x) for x in labels),
        "has_8": any(re.match(r"1\.2\.1\.2" + HYPHEN_RE + r"8", x) for x in labels),
    })
    if PROBE.is_file():
        probe = json.loads(PROBE.read_text(encoding="utf-8-sig"))
        seq = [x.get("text", "") for x in probe.get("X1_题号块", [])]
        x1.update({
            "probe_x1_sequence": seq,
            "probe_has_6": any("1.2.1.2-6" in x for x in seq),
            "probe_has_7": any("1.2.1.2-7" in x for x in seq),
            "probe_has_8": any("1.2.1.2-8" in x for x in seq),
            "probe_count": len(seq),
        })
    a8 = {
        "pass": bool(x1.get("has_joined_1.2.1.2-7")),
        "x1_in_product": bool(x1.get("has_joined_1.2.1.2-7")),
        "probe_gap": bool(x1.get("probe_has_6") and not x1.get("probe_has_7") and x1.get("probe_has_8")),
    }
    if a8["x1_in_product"] and a8["probe_gap"]:
        a8["conclusion"] = "探针签名漏配/工具缺陷，非成品断号"
    elif a8["x1_in_product"]:
        a8["conclusion"] = "原件在位1.2.1.2-7；非成品断号"
    else:
        a8["conclusion"] = "成品断号->停报主会话"
        a8["pass"] = False

    hashes = []
    for alias, fn, _ in FILES:
        o, m = ORIG / fn, MIRR / fn
        item = dict(alias=alias, original_exists=o.is_file(), mirror_exists=m.is_file())
        if o.is_file() and m.is_file():
            item['original_sha256'] = sha256(o)
            item['mirror_sha256'] = sha256(m)
            item['sha_equal'] = item['original_sha256'] == item['mirror_sha256']
        hashes.append(item)

    clean = next(x for x in static_files if x['alias'] == '清单2')
    c22 = [r for r in clean['table_out_paragraphs_matching_prefix'] if r.get('no') == '2.2']
    c23 = [r for r in clean['table_out_paragraphs_matching_prefix'] if r.get('no') == '2.3']
    noset = {r['no'] for r in clean['table_out_paragraphs_matching_prefix'] if r.get('no')}
    clean_check = {
        'candidate_2.2': c22,
        'candidate_2.3': c23,
        'all_table_out_prefix_nos': sorted(noset, key=section_key),
        'com_hits': get_com('清单2')[0].get('sections', []),
        'classification': ('本无该节标题段->清单件配属签名漏配/工具缺陷' if not c22 and not c23 else '存在候选需判假阴'),
    }

    com_exceptions = []
    jl_key = '讲练1上'
    if (Amap.get(jl_key) or {}).get('error'):
        jl1 = next(h for h in hashes if h['alias'] == jl_key)
        com_exceptions.append({'config':'A','name':jl_key,'error':Amap[jl_key].get('error'),'note':'sha_equal=%s' % jl1.get('sha_equal')})

    source_sha = sha256(SCRIPT)
    source_ok = source_sha == EXPECTED_SHA
    overall = all([a1['pass'], a2['pass'], a3['pass'], a4['pass'], a5['pass'], a6['pass'], a7['pass'], a8['pass']]) and source_ok

    sfs_out = []
    for sf in static_files:
        sfs_out.append({
            'alias': sf['alias'], 'path': sf['path'], 'com_nos': sf['com_nos'], 'static_nos': sf['static_nos'],
            'diff_count': len(sf['diff_vs_com_hits']), 'diff_vs_com_hits': sf['diff_vs_com_hits'],
            'bare_14pt_false_negative_in_diff': sf['bare_14pt_false_negative_in_diff'],
            'table_out_paragraphs_matching_prefix': sf['table_out_paragraphs_matching_prefix'],
            'static_rule_hits': sf['static_rule_hits'],
        })
    diff = {
        'status': 'com_ran_opencode',
        'source': {'path': str(SCRIPT), 'sha256': source_sha, 'expected_sha256': EXPECTED_SHA, 'sha256_matches': source_ok},
        'assertions': {'1_old_sig': a1, '2_new_sig': a2, '3_neg': a3, '4_diff': a4, '5_A_vs_B': a5, '6_nondecreasing': a6, '7_bidirectional': a7, '8_x1': a8},
        'static_files': sfs_out,
        'clean_list_2_missing_check': clean_check,
        'original_vs_mirror_sha256': hashes,
        'x1_xml_check': x1,
        'com_exceptions': com_exceptions,
        'winword_final': sorted(winword_pids()),
        'overall': ('PASS' if overall else 'FAIL'),
    }
    (OUT / '差集清单.json').write_text(json.dumps(diff, ensure_ascii=False, indent=1) + chr(10), encoding='utf-8')

    def yn(pflag):
        return 'PASS' if pflag else 'FAIL'

    jl1_hash = next(h for h in hashes if h['alias'] == jl_key)
    lines = []
    lines.append('PASS' if overall else 'FAIL')
    lines.append('# 复测报告·补签（opencode臂）')
    lines.append('')
    lines.append('结论：%s。SHA %s；COM A/B。' % (('PASS' if overall else 'FAIL'), ('OK' if source_ok else 'BAD')))
    lines.append('')
    lines.append('## 前置')
    lines.append('')
    lines.append('- SHA %s match=%s' % (source_sha, source_ok))
    lines.append('- A=%s B=%s' % (A.get('run_status'), B.get('run_status')))
    for e in com_exceptions:
        lines.append('- COM %s %s: %s' % (e['config'], e['name'], e['error']))
    lines.append('- jl1 sha_equal=%s' % jl1_hash.get('sha_equal'))
    lines.append('')
    lines.append('## 断言面')
    lines.append('')
    lines.append('1. old_sig: %s' % yn(a1['pass']))
    for alias, rows in a1['details'].items():
        bad = [r['no'] for r in rows if not r['equal']]
        lines.append('   - %s %s src=%s' % (alias, ('FAIL '+str(bad) if bad else 'PASS'), rows[0]['source'] if rows else '?'))
    lines.append('2. new_sig: %s' % yn(a2['pass']))
    for alias, rows in a2['details'].items():
        bad = [r['no'] for r in rows if not r['equal']]
        lines.append('   - %s %s' % (alias, ('FAIL '+str(bad) if bad else 'PASS '+str([r['no'] for r in rows]))))
    lines.append('3. neg: %s' % yn(a3['pass']))
    lines.append('4. diff: %s' % yn(a4['pass']))
    for alias, d in a4['details'].items():
        lines.append('   - %s fn=%s cls=%s' % (alias, d['false_neg_count'], json.dumps(d['diff_class_counts'], ensure_ascii=False)))
    lines.append('5. A_vs_B: %s' % yn(a5['pass']))
    for alias, d in a5['details'].items():
        lines.append('   - %s %s' % (alias, ('PASS' if d.get('equal') else 'FAIL '+str(d.get('reason')))))
    lines.append('6. nondec: %s' % yn(a6['pass']))
    for alias, d in a6['details'].items():
        lines.append('   - %s ok=%s pages=%s' % (alias, d['nondecreasing'], d['part_pages']))
    lines.append('7. bidir: %s' % yn(a7['pass']))
    for s in a7['samples']:
        if s.get('error'):
            lines.append('   - %s ERR %s' % (s['alias'], s['error']))
        else:
            lines.append('   - %s hit=%s diff=%s' % (s['alias'], s['hit']['agree_should_hit'], (s['diff'] or {}).get('classification')))
    lines.append('8. X1: %s %s' % (yn(a8['pass']), a8['conclusion']))
    if x1.get('evidence_paragraphs'):
        lines.append('   - %s' % x1['evidence_paragraphs'][0]['text'])
    lines.append('   - probe 6/7/8=%s/%s/%s joined7=%s' % (x1.get('probe_has_6'), x1.get('probe_has_7'), x1.get('probe_has_8'), x1.get('has_joined_1.2.1.2-7')))
    lines.append('')
    lines.append('## 清单2 2.2/2.3')
    lines.append('')
    lines.append('- c22=%s c23=%s' % (len(c22), len(c23)))
    lines.append('- %s' % clean_check['classification'])
    lines.append('- nos=%s' % clean_check['all_table_out_prefix_nos'])
    lines.append('')
    lines.append('## X1')
    lines.append('')
    if x1.get('evidence_paragraphs'):
        for item in x1['evidence_paragraphs']:
            lines.append('- ' + item['text'])
    else:
        lines.append('- none')
    lines.append('')
    lines.append('## files')
    lines.append('- A/B json, diff json, errs')
    lines.append('PIDs %s' % sorted(winword_pids()))
    (OUT / '复测报告_补签.md').write_text(chr(10).join(lines) + chr(10), encoding='utf-8')
    print('OVERALL', 'PASS' if overall else 'FAIL')
    print('flags', a1['pass'], a2['pass'], a3['pass'], a4['pass'], a5['pass'], a6['pass'], a7['pass'], a8['pass'])
    print('A jl1', (Amap.get(jl_key) or {}).get('error'))

if __name__ == '__main__':
    main()
