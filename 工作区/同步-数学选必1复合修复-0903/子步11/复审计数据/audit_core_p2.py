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
