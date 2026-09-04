# -*- coding: utf-8 -*-
"""§13复审计 自测主脚本：任务书§2 项1,2,3,4,5,6,9,10,12"""
import hashlib, os, re, json, zipfile, subprocess, sys
import fitz
from lxml import etree

ROOT = r"C:\提示词"
SYNC = ROOT + r"\高中数学\高中数学同步"
WS = ROOT + r"\工作区\同步-数学选必1复合修复-0903"
PDFDIR = WS + r"\pages_406\pdf"
DOCX = {
 "X1": r"人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
 "I1": r"人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
 "B":  r"人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",
 "C":  r"人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx",
 "X2": r"人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx",
 "I2": r"人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx",
 "E":  r"人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx",
 "F":  r"人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx",
 "G":  r"人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx",
 "H":  r"人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx",
}
EXP = {  # 页数, start, footer, 本n, 前缀有无, 共N页, 件型词
 "X1": dict(pages=14, start=1,   footer=850, ben=1, prefix=False, N=14,  typ="衔接"),
 "I1": dict(pages=13, start=1,   footer=850, ben=2, prefix=False, N=13,  typ="清单"),
 "B":  dict(pages=61, start=1,   footer=850, ben=3, prefix=False, N=121, typ="讲练"),
 "C":  dict(pages=60, start=62,  footer=567, ben=3, prefix=True,  N=121, typ="讲练"),
 "X2": dict(pages=5,  start=1,   footer=850, ben=4, prefix=True,  N=5,   typ="衔接"),
 "I2": dict(pages=28, start=1,   footer=850, ben=5, prefix=True,  N=28,  typ="清单"),
 "E":  dict(pages=55, start=1,   footer=850, ben=6, prefix=True,  N=225, typ="讲练"),
 "F":  dict(pages=56, start=56,  footer=850, ben=6, prefix=True,  N=225, typ="讲练"),
 "G":  dict(pages=44, start=112, footer=850, ben=6, prefix=True,  N=225, typ="讲练"),
 "H":  dict(pages=70, start=156, footer=567, ben=6, prefix=True,  N=225, typ="讲练"),
}
R = {}

def nows(s):  # 去全部空白
    return re.sub(r"\s+", "", s)

# ---------- 项1 PDF页数账 ----------
pdf_pages = {}
for k in list(DOCX) + ["FM","SM","ML","FQ1","FQ2","FQ3","FQ4","FQ5","FQ6"]:
    d = fitz.open(os.path.join(PDFDIR, k + ".pdf"))
    pdf_pages[k] = d.page_count
    d.close()
content_ok = all(pdf_pages[k] == EXP[k]["pages"] for k in DOCX)
content_sum = sum(pdf_pages[k] for k in DOCX)
peiye = {k: pdf_pages[k] for k in ["FM","SM","ML","FQ1","FQ2","FQ3","FQ4","FQ5","FQ6"]}
R["item1"] = {"per_file": pdf_pages, "content_sum": content_sum,
              "content_match_EXP": content_ok, "peiye_all_1": all(v == 1 for v in peiye.values()),
              "total": content_sum + sum(peiye.values())}

# ---------- 项2/3/4/6/12b docx 侧 ----------
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
HDR_RE = re.compile(r"^(羿郭工作室·)?人教B版选必1 (第1章 空间向量与立体几何|第2章 平面解析几何)·(衔接|清单|讲练)（共(\d+)页）·本(\d)/共6本　.+　第(\d+)页$")

item2, item3, item4, item12b = {}, {}, {}, {}
doc_first_para = {}
for k, fn in DOCX.items():
    p = os.path.join(SYNC, fn)
    z = zipfile.ZipFile(p)
    names = z.namelist()
    doc = z.read("word/document.xml").decode("utf-8")
    settings = z.read("word/settings.xml").decode("utf-8") if "word/settings.xml" in names else ""
    # 项2 start
    starts = re.findall(r'w:start="(\d+)"', doc)
    item2[k] = {"start_occurrences": len(starts), "start_values": starts,
                "pgNumType_total": doc.count("<w:pgNumType")}
    # 项3 pgMar
    mars = []
    for m in re.finditer(r"<w:pgMar\b[^>]*/?>", doc):
        tag = m.group(0)
        attrs = dict(re.findall(r'w:(\w+)="(-?\d+)"', tag))
        mars.append(attrs)
    item3[k] = {"pgMar_count": len(mars), "attrs": mars}
    # 项4 部件计数 + 同串
    headers = sorted(n for n in names if re.fullmatch(r"word/header\d+\.xml", n))
    footers = sorted(n for n in names if re.fullmatch(r"word/footer\d+\.xml", n))
    def vis(part):
        xml = z.read(part).decode("utf-8")
        return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))
    htxt = {h: vis(h) for h in headers}
    ftxt = {f: vis(f) for f in footers}
    hdr_text = htxt[headers[0]] if headers else ""
    ftr_text = ftxt[footers[0]] if footers else ""
    mh = HDR_RE.match(hdr_text); mf = HDR_RE.match(ftr_text)
    def cap(m):
        return None if not m else {"prefix": bool(m.group(1)), "chap": m.group(2), "typ": m.group(3),
                                   "N": int(m.group(4)), "ben": int(m.group(5)), "page": int(m.group(6))}
    item4[k] = {"headers": headers, "footers": footers,
                "titlePg": "<w:titlePg" in doc, "evenAndOdd": "evenAndOddHeaders" in settings,
                "header_text": hdr_text, "footer_text": ftr_text,
                "header_match": cap(mh), "footer_match": cap(mf),
                "hf_identical": hdr_text == ftr_text}
    # 项12b 首段
    root = etree.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    first = ""
    for para in body.iter(W + "p"):
        t = "".join(node.text or "" for node in para.iter() if node.tag in (W + "t", M + "t"))
        if nows(t):
            first = nows(t); break
    item12b[k] = first
    z.close()

R["item2"] = item2; R["item3"] = item3; R["item4"] = item4

# ---------- 项5 PDF页码链（十件全量逐页） ----------
item5 = {}
assert_total = 0
for k in DOCX:
    d = fitz.open(os.path.join(PDFDIR, k + ".pdf"))
    bad = []
    nmatch_hist = {}
    for i in range(d.page_count):
        t = nows(d[i].get_text("text"))
        vals = [int(x) for x in re.findall(r"第(\d+)页", t)]
        expv = EXP[k]["start"] + i
        assert_total += len(vals)
        nmatch_hist[len(vals)] = nmatch_hist.get(len(vals), 0) + 1
        if not vals or any(v != expv for v in vals):
            bad.append({"page": i + 1, "found": vals, "expect": expv})
    item5[k] = {"pages": d.page_count, "bad_pages": bad, "match_count_hist": nmatch_hist}
    d.close()
R["item5"] = item5
R["item5_total_asserts"] = assert_total
# 接缝
seams = [("B", "C"), ("E", "F"), ("F", "G"), ("G", "H")]
R["item5_seams"] = {f"{a}->{b}": {"a_last": EXP[a]["start"] + EXP[a]["pages"] - 1,
                                  "b_first_expect": EXP[b]["start"],
                                  "chain_ok": EXP[b]["start"] == EXP[a]["start"] + EXP[a]["pages"]} for a, b in seams}

# ---------- 项6 勘误点（B件） ----------
z = zipfile.ZipFile(os.path.join(SYNC, DOCX["B"]))
root = etree.fromstring(z.read("word/document.xml"))
body = root.find(W + "body")
paras = []
for para in body.iter(W + "p"):
    t_all = "".join(node.text or "" for node in para.iter() if node.tag in (W + "t", M + "t"))
    t_math = "".join(node.text or "" for node in para.iter() if node.tag == M + "t")
    paras.append((nows(t_all), nows(t_math)))
full = "\n".join(p[0] for p in paras)
sig = "若PA⊥平面ABC"
hits = [m.start() for m in re.finditer(re.escape(sig), full)]
hit_paras = [i for i, (t, _) in enumerate(paras) if sig in t]
item6 = {"sig": sig, "fulltext_hits": len(hits), "doc_offsets": hits, "para_indices": hit_paras}
blk_re = re.compile(r"^\d+\.\d+\.\d+\.\d+-\d+．")
bstart = next((i for i, (t, _) in enumerate(paras) if t.startswith("1.2.1.3-2．")), None)
if bstart is not None:
    bend = next((j for j in range(bstart + 1, len(paras)) if blk_re.match(paras[j][0])), len(paras))
    math_lin = "".join(paras[j][1] for j in range(bstart, bend))
    item6["block"] = {"para_range": [bstart, bend], "n_paras": bend - bstart}
    for label, variant in [("halfwidth", "解得x=-1z=2"), ("U2212", "解得x=−1z=2")]:
        item6["block"]["contains_" + label] = variant in math_lin
    for label, variant in [("halfwidth", "x=1z=-2"), ("U2212", "x=1z=−2")]:
        item6["block"]["absent_" + label] = variant not in math_lin
    idx = math_lin.find("解得")
    item6["block"]["math_lin_around_解得"] = math_lin[max(0, idx - 5):idx + 40] if idx >= 0 else None
    item6["block"]["math_lin_len"] = len(math_lin)
z.close()
R["item6"] = item6
# ---------- 项9 装订三方 ----------
order = open(os.path.join(SYNC, "人教B版选必1·装订单.md"), encoding="utf-8").read()
rows = re.findall(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", order, re.M)
item9 = {"装订单_rows": [[c.strip() for c in r] for r in rows]}
pj = json.load(open(WS + r"\子步11\parts_选必1_现行.json", encoding="utf-8"))
item9["parts_tags_files"] = [{"tag": p["tag"], "n_files": len(p["files"]),
                              "files": [os.path.basename(f) for f in p["files"]]} for p in pj["parts"]]
z = zipfile.ZipFile(os.path.join(SYNC, "人教B版选必1·册目录页.docx"))
root = etree.fromstring(z.read("word/document.xml"))
ml_lines = []
for para in root.iter(W + "p"):
    t = nows("".join(node.text or "" for node in para.iter() if node.tag in (W + "t", M + "t")))
    if t:
        ml_lines.append(t)
z.close()
item9["册目录页_lines"] = ml_lines
cp = subprocess.run([sys.executable, ROOT + r"\工具\本厚复核.py", os.path.join(SYNC, "人教B版选必1·装订单.md")],
                    capture_output=True, text=True, encoding="utf-8", errors="replace")
item9["本厚复核"] = {"returncode": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr}
R["item9"] = item9

# ---------- 项10 哈希快照 ----------
SNAP = json.load(open(WS + r"\tmp\章码重盖前备份\_快照.json", encoding="utf-8"))
def sig(path):
    h = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n == "word/document.xml" or re.fullmatch(r"word/(header|footer)\d+\.xml", n) or n == "word/settings.xml":
                h[n] = hashlib.sha1(z.read(n)).hexdigest()[:12]
    return h
item10 = {}
for k, fn in DOCX.items():
    now = sig(os.path.join(SYNC, fn))
    old = SNAP.get(fn, {})
    changed = sorted(n for n in now if old.get(n) != now[n])
    extra = sorted(set(now) - set(old)); gone = sorted(set(old) - set(now))
    item10[k] = {"changed_keys": changed, "extra": extra, "gone": gone, "all_equal": not (changed or extra or gone)}
R["item10"] = item10
import datetime
snapf = WS + r"\tmp\章码重盖前备份\_快照.json"
R["item10_snap"] = {"sha256": hashlib.sha256(open(snapf, "rb").read()).hexdigest(),
                    "mtime": datetime.datetime.fromtimestamp(os.stat(snapf).st_mtime).isoformat()}
bak = WS + r"\tmp\章码重盖前备份"
R["item10_backup_docx_mtime"] = {f: datetime.datetime.fromtimestamp(os.stat(os.path.join(bak, f)).st_mtime).isoformat()
                                 for f in os.listdir(bak) if f.endswith(".docx")}

# ---------- 项12 PDF↔docx 同源 ----------
item12 = {}
for k, fn in DOCX.items():
    dmt = os.stat(os.path.join(SYNC, fn)).st_mtime
    pmt = os.stat(os.path.join(PDFDIR, k + ".pdf")).st_mtime
    d = fitz.open(os.path.join(PDFDIR, k + ".pdf"))
    p1 = nows(d[0].get_text("text"))
    d.close()
    firstp = item12b[k]
    item12[k] = {"docx_mtime": datetime.datetime.fromtimestamp(dmt).isoformat(),
                 "pdf_mtime": datetime.datetime.fromtimestamp(pmt).isoformat(),
                 "pdf_ge_docx": pmt >= dmt,
                 "first_para": firstp,
                 "first_para_in_pdf_p1": firstp in p1}
R["item12"] = item12

json.dump(R, open("自测_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("项1:", R["item1"]["content_sum"], "配页全1:", R["item1"]["peiye_all_1"], "总计:", R["item1"]["total"])
print("项1 逐件:", {k: pdf_pages[k] for k in DOCX})
for k in DOCX:
    print("项2", k, item2[k], "| 项3 pgMar数:", item3[k]["pgMar_count"])
    for a in item3[k]["attrs"]:
        print("   ", a)
for k in DOCX:
    i4 = item4[k]
    print("项4", k, "H:", i4["headers"], "F:", i4["footers"], "titlePg:", i4["titlePg"], "evenOdd:", i4["evenAndOdd"], "HF同:", i4["hf_identical"])
    print("   header_text:", repr(i4["header_text"]))
    print("   footer_text:", repr(i4["footer_text"]))
    print("   hmatch:", i4["header_match"], "fmatch:", i4["footer_match"])
print("项5 总断言数:", R["item5_total_asserts"])
for k in DOCX:
    print("项5", k, "bad:", item5[k]["bad_pages"], "hist:", item5[k]["match_count_hist"])
print("项5 接缝:", R["item5_seams"])
print("项6:", json.dumps(item6, ensure_ascii=False))
print("项9 装订单行数:", len(item9["装订单_rows"]))
print("项9 parts:", json.dumps(item9["parts_tags_files"], ensure_ascii=False))
print("项9 本厚复核 rc:", item9["本厚复核"]["returncode"])
print(item9["本厚复核"]["stdout"])
print("项9 册目录页行:")
for l in item9["册目录页_lines"]:
    print("   ", l)
print("项10:", {k: (v["all_equal"], v["changed_keys"], v["extra"], v["gone"]) for k, v in item10.items()})
print("项10 快照:", R["item10_snap"])
print("项10 备份docx mtime:", json.dumps(R["item10_backup_docx_mtime"], ensure_ascii=False, indent=1))
for k in DOCX:
    i12 = item12[k]
    print("项12", k, "pdf>=docx:", i12["pdf_ge_docx"], "| 首段含:", i12["first_para_in_pdf_p1"], "| 首段:", i12["first_para"][:60])
