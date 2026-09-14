# -*- coding: utf-8 -*-
# 换装成书重装·工装 装配五本.py ——五本两链一串装订（承 M3 成卷/装配/工装/装配三本.py＋M2 _tmp装配装订0912/装配四本.py 先例）
# 适配五点：
#   ①取件序 34 件参数化＝M2导学 12（衔接→课时01~10→章末）＋M2练习 12（课时01~10→上册→下册）
#     ＋P1导学 5（9.1~9.4→章末）＋P1练习 4＋P1拓展 1（P1练习拓展/ 树内两本）；
#   ②双链 G7 方案B 跨本连续页码：M2 链＝导学＋练习、P1 链＝导学＋练习＋拓展，各自起 1
#     （目录页本轮不产，页码待卷件定稿后统一机核回填——不锁目录页）；
#   ③件制＝main-true.tex（\mthreepure 0 含详解印本）／main-pure.tex（纯题档）双壳双档各跑一遍；
#   ④sty md5 钉（换装轮报告注册值）：qp-m3＝7c3930362be8a0a2bdf21bbf8ac16573（M2 两本）、
#     P1导 overlay v0.2＝94ca406ee6a7c89a188e20d63b2d095a、P1练拓 overlay v0.1＝da54d841927284052336cf9709ff6fb2；
#   ⑤页数断言：逐件实测＝换装轮基线（_进度.md 件账／波2 报告§二／_进度-波4a.md 件账／波4b 报告§二），
#     漂移即红旗退出（起页链随基线，漂移必断链）。
# 副本树剔除 png/__pycache__/压测* 与 aux/log/pdf/py/md/json/txt（figs 随目录）；源树全程只读。
# 写入域仅 工作区/_tmp换装正装0914/成书重装/（写前核 mode：os.access 实测）。
# 用法：python 装配五本.py
import io, sys, os, re, json, shutil, subprocess, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", write_through=True)
from pypdf import PdfReader, PdfWriter

WS   = r"C:\提示词\工作区"
ROOT = os.path.join(WS, "_tmp换装正装0914")          # 只读源
ASM  = os.path.join(ROOT, "成书重装")                # 写入域（新建）

# ---- 写前核 mode ----
os.makedirs(ASM, exist_ok=True)
assert os.access(ASM, os.W_OK), f"写入域不可写: {ASM}"
print(f"[mode] 写入域 {ASM} 可写实测 OK（源树全程只读）")

STY_MD5 = {"qp-m3":          "7c3930362be8a0a2bdf21bbf8ac16573",
           "overlay-v0.2":   "94ca406ee6a7c89a188e20d63b2d095a",
           "overlay-v0.1":   "da54d841927284052336cf9709ff6fb2"}

# ---- 取件序 34 件（rel, 显示名(书签), (true 页, pure 页)——页数基线＝换装轮各波在案读数） ----
M2DAO = [  # M2导学本 12（_进度.md 件账 true/pure）
    ("衔接节-1.2.1前",     "衔接（1.2.1 前）",        (5, 4)),
    ("课时01",            "第1课时",                 (4, 3)),
    ("课时02",            "第2课时",                 (3, 3)),
    ("课时03",            "第3课时",                 (3, 3)),
    ("课时04",            "第4课时",                 (4, 3)),
    ("课时05",            "第5课时",                 (4, 3)),
    ("课时06",            "第6课时",                 (4, 3)),
    ("课时07",            "第7课时",                 (4, 3)),
    ("课时08",            "第8课时",                 (4, 3)),
    ("课时09",            "第9课时",                 (4, 3)),
    ("课时10",            "第10课时",                (4, 3)),
    ("章末-本章总结提升",   "章末·本章总结提升",        (8, 6)),
]
M2LIAN = [  # M2练习本 12（波2 报告§二 页数表）
    ("课时01", "第1课时 配套练习",              (3, 2)),
    ("课时02", "第2课时 配套练习",              (2, 2)),
    ("课时03", "第3课时 配套练习",              (3, 2)),
    ("课时04", "第4课时 配套练习",              (3, 3)),
    ("课时05", "第5课时 配套练习",              (3, 2)),
    ("课时06", "第6课时 配套练习",              (3, 2)),
    ("课时07", "第7课时 配套练习",              (3, 3)),
    ("课时08", "第8课时 配套练习",              (3, 2)),
    ("课时09", "第9课时 配套练习",              (3, 3)),
    ("课时10", "第10课时 配套练习",             (3, 3)),
    ("上册",   "拓展册·上册（1.1.1~1.2.3）",    (6, 5)),
    ("下册",   "拓展册·下册（1.2.4~1.2.5）",   (15, 12)),
]
P1DAO = [  # P1导学本 5（_进度-波4a.md 件账）
    ("9.1电荷",              "9.1 电荷",            (4, 3)),
    ("9.2库仑定律",           "9.2 库仑定律",         (4, 3)),
    ("9.3电场电场强度",        "9.3 电场 电场强度",     (4, 3)),
    ("9.4静电的防止与利用",     "9.4 静电的防止与利用",   (4, 4)),
    ("章末-本章易错过关",      "章末·本章易错过关",     (3, 2)),
]
P1LIAN = [  # P1练习本 4（波4b 报告§二 页数表）
    ("9.1电荷",              "9.1 配套练习",          (6, 3)),
    ("9.2库仑定律",           "9.2 配套练习",          (5, 4)),
    ("9.3电场电场强度",        "9.3 配套练习",          (4, 4)),
    ("9.4静电的防止与利用",     "9.4 配套练习",          (5, 3)),
]
P1TUO = [("拓展册", "拓展册（第9章 静电场及其应用）", (11, 10))]
# 本（书名, 链, 源子树, 取件表, sty 钉名）
BOOKS = [("M2导学本", "M2", "M2导学本",     M2DAO, "qp-m3"),
         ("M2练习本", "M2", "M2练习本",     M2LIAN, "qp-m3"),
         ("P1导学本", "P1", "P1导学本",     P1DAO, "overlay-v0.2"),
         ("P1练习本", "P1", "P1练习拓展",   P1LIAN, "overlay-v0.1"),
         ("P1拓展本", "P1", "P1练习拓展",   P1TUO,  "overlay-v0.1")]
ENTRY = {"true": "main-true.tex", "false": "main-pure.tex"}   # false 档＝纯题档

# ---- 副本树剔除（先例同款＋本轮：txt 过程件、压测* 非印本候选） ----
SKIP_DIR  = ("png", "__pycache__")
def copy_piece(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR and not d.startswith("压测")]
        rel = os.path.relpath(root, src)
        tgt = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(tgt, exist_ok=True)
        for f in files:
            if re.search(r"\.(aux|log|pdf|py|md|json|txt)$", f):
                continue
            shutil.copy2(os.path.join(root, f), os.path.join(tgt, f))

def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()

# ---- setcounter 注入：入口 tex 无 \begin{document}（壳）则解析 \input 注被引件 ----
MARK = "成书重装五本"
def inject(entry_path, start):
    d = os.path.dirname(entry_path)
    cur = os.path.basename(entry_path)
    for _ in range(3):
        with open(os.path.join(d, cur), encoding="utf-8") as fh:
            t = fh.read()
        if "\\begin{document}" in t:
            break
        m = re.search(r"\\input\{([^}]+)\}", t)
        assert m, f"{entry_path} 找不到 \\begin{{document}} 也无 \\input"
        cur = m.group(1) + (".tex" if not m.group(1).endswith(".tex") else "")
    else:
        raise AssertionError(f"{entry_path} 注入位三跳未中")
    assert MARK not in t, f"{cur} 已有注入痕迹"
    m = re.search(r"(?m)^\\begin\{document\}", t)   # 行首真注入位——P1 件头注含字面 \begin{document}，禁 replace 首现
    assert m, f"{cur} 找不到行首 \\begin{{document}}"
    ins = ("\\begin{document}\n"
           "%" + MARK + "跨本连续页码（G7方案B，承M2/M3装配先例）setcounter 注入位\n"
           "\\setcounter{page}{" + str(start) + "}")
    t = t[:m.start()] + ins + t[m.end():]
    with open(os.path.join(d, cur), "w", encoding="utf-8") as fh:
        fh.write(t)

def compile2(d, entry):
    job = entry[:-4]
    r = None
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", entry],
                           cwd=d, capture_output=True)
    with open(os.path.join(d, job + ".log"), encoding="utf-8", errors="ignore") as fh:
        txt = fh.read()
    err = len(re.findall(r"^! ", txt, re.M))
    ovr = txt.count("Overfull")
    mch = txt.count("Missing character")
    n = len(PdfReader(os.path.join(d, job + ".pdf")).pages)
    return err, ovr, mch, n, r.returncode

# ---- 主流程：双档各跑一遍（true 含详解印本／false 纯题档），链内跨本连续 ----
data = {"sty_md5": STY_MD5, "chains": {}, "modes": {}}
report = []
for mode in ("true", "false"):
    entry = ENTRY[mode]
    cursor_chain = {"M2": 1, "P1": 1}                 # 双链各自起 1（G7 方案B）
    data["modes"][mode] = {"books": [], "total_pages": 0, "total_bookmarks": 0}
    for book, chain, subtree, pieces, sty_name in BOOKS:
        book_dir = os.path.join(ASM, mode, book)
        os.makedirs(book_dir, exist_ok=True)
        writer, cursor = PdfWriter(), 0
        rec = {"book": book, "chain": chain, "pdf": f"{mode}/{book}.pdf",
               "start": cursor_chain[chain], "pieces": [], "bookmarks": 0}
        for rel, disp, pages2 in pieces:
            baseline = pages2[0 if mode == "true" else 1]
            start = cursor_chain[chain]
            dst = os.path.join(book_dir, rel)
            copy_piece(os.path.join(ROOT, subtree, rel), dst)
            sty = "qp-m3.sty" if sty_name == "qp-m3" else "qp-m3p-overlay.sty"
            got = md5_of(os.path.join(dst, sty))
            assert got == STY_MD5[sty_name], f"{dst} {sty} md5 漂移: {got}"
            inject(os.path.join(dst, entry), start)
            err, ovr, mch, n, rc = compile2(dst, entry)
            ok = (err == 0 and ovr == 0 and mch == 0 and rc == 0 and n == baseline)
            tag = "OK" if ok else "**FAIL**"
            report.append(f"[{mode}] {book}/{rel:<14s} 起{start:>3d} {n:>2d}页(基线{baseline}) "
                          f"err={err} ovr={ovr} mch={mch} rc={rc} {tag}")
            if not ok:
                print("\n".join(report)); sys.exit(1)
            rec["pieces"].append({"rel": rel, "disp": disp, "mark": rel,
                                  "start": start, "pages": n})
            writer.append(PdfReader(os.path.join(dst, entry[:-4] + ".pdf")))
            writer.add_outline_item(disp, cursor)
            cursor += n
            cursor_chain[chain] += n
        out = os.path.join(ASM, mode, f"{book}.pdf")
        with open(out, "wb") as fh:
            writer.write(fh)
        n_bm = len(PdfReader(out).outline)
        assert n_bm == len(pieces), f"{book} 书签 {n_bm} ≠ {len(pieces)}"
        rec["pages"], rec["bookmarks"] = cursor, n_bm
        data["modes"][mode]["books"].append(rec)
        data["modes"][mode]["total_pages"] += cursor
        data["modes"][mode]["total_bookmarks"] += n_bm
        report.append(f"■ [{mode}] {book}.pdf 合并 {cursor} 页（链内起{rec['start']}）书签 {n_bm} 条")
    data["chains"][mode] = dict(cursor_chain)
    report.append(f"■ [{mode}] 全档 {data['modes'][mode]['total_pages']} 页 "
                  f"书签合计 {data['modes'][mode]['total_bookmarks']} 条 链尾 {dict(cursor_chain)}")

with open(os.path.join(ASM, "装配读数.json"), "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1)
report.append("■ 装配读数.json 已落 " + ASM)
print("\n".join(report))
