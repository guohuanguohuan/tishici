# -*- coding: utf-8 -*-
# M2 轮4 装配轮 · 四本装订模拟（G7 跨本连续页码·方案B）
# 每件：整目录拷贝 → \begin{document} 后注入 \setcounter{page}{起始页} → xelatex×2 → 按序合并＋书签
import io, sys, os, re, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader, PdfWriter

ROOT = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
ASM  = os.path.join(ROOT, "装配")

BOOKS = [
    ("导学本", [
        ("课时01", "导学件/课时01", 1,  "第1课时 空间向量的概念及线性运算（含1.1.1前衔接）"),
        ("课时02", "导学件/课时02", 5,  "第2课时 空间向量的数量积"),
        ("课时03", "导学件/课时03", 8,  "第3课时 空间向量基本定理"),
        ("课时04", "导学件/课时04", 11, "第4课时 空间直角坐标系与空间向量的坐标"),
        ("课时05", "导学件/课时05", 14, "第5课时 空间向量运算的坐标表示"),
        ("衔接节-1.2.1前", "导学件/衔接节-1.2.1前", 17, "衔接 初等几何必会（1.2.1前）"),
        ("课时06", "导学件/课时06", 21, "第6课时 空间中的点、直线与空间向量"),
        ("课时07", "导学件/课时07", 25, "第7课时 空间中的平面与空间向量"),
        ("课时08", "导学件/课时08", 29, "第8课时 直线与平面的夹角"),
        ("课时09", "导学件/课时09", 33, "第9课时 二面角"),
        ("课时10", "导学件/课时10", 36, "第10课时 空间中的距离"),
        ("章末-本章总结提升", "导学件/章末-本章总结提升", 39, "本章总结提升"),
    ]),
    ("练习本", [
        ("课时01", "练习件/课时01", 45, "第1课时 配套练习"),
        ("课时02", "练习件/课时02", 47, "第2课时 配套练习"),
        ("课时03", "练习件/课时03", 49, "第3课时 配套练习"),
        ("课时04", "练习件/课时04", 51, "第4课时 配套练习"),
        ("课时05", "练习件/课时05", 53, "第5课时 配套练习"),
        ("课时06", "练习件/课时06", 55, "第6课时 配套练习"),
        ("课时07", "练习件/课时07", 57, "第7课时 配套练习"),
        ("课时08", "练习件/课时08", 59, "第8课时 配套练习"),
        ("课时09", "练习件/课时09", 61, "第9课时 配套练习"),
        ("课时10", "练习件/课时10", 63, "第10课时 配套练习"),
        ("拓展册-上册", "拓展册/上册", 65, "拓展册 上册"),
        ("拓展册-下册", "拓展册/下册", 70, "拓展册 下册"),
    ]),
    ("测评本", [
        ("测评卷", "测评卷", 83, "单元素养测评卷（一）·第一章"),
        ("滚动卷A", "滚动卷/滚A", 86, "滚动测评卷（A）"),
        ("滚动卷B", "滚动卷/滚B", 88, "滚动测评卷（B）"),
    ]),
    ("答案本", [
        ("答案册", "答案册", 90, "参考答案册（导学·练习·拓展·测评全含）"),
    ]),
]

SKIP = re.compile(r"^(png|__pycache__)$|\.aux$|\.log$|\.out$|\.py$|\.pdf$|\.md$|\.json$|^_b[0-9]\.txt$")

def copy_piece(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ("png", "__pycache__")]
        rel = os.path.relpath(root, src)
        tgt = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(tgt, exist_ok=True)
        for f in files:
            if SKIP.search(f):
                continue
            shutil.copy2(os.path.join(root, f), os.path.join(tgt, f))

def inject(tex_path, start):
    with open(tex_path, encoding="utf-8") as fh:
        t = fh.read()
    assert "\\begin{document}" in t, tex_path
    assert "装配轮G7" not in t, tex_path
    ins = ("\\begin{document}\n"
           "%装配轮G7跨本连续页码（方案B）setcounter 注入位\n"
           "\\setcounter{page}{" + str(start) + "}")
    t = t.replace("\\begin{document}", ins, 1)
    with open(tex_path, "w", encoding="utf-8") as fh:
        fh.write(t)

def compile2(d):
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "main.tex"],
                           cwd=d, capture_output=True)
    log = os.path.join(d, "main.log")
    with open(log, encoding="utf-8", errors="ignore") as fh:
        txt = fh.read()
    err = len(re.findall(r"^! ", txt, re.M))
    ovr = txt.count("Overfull")
    mch = txt.count("Missing character")
    n = len(PdfReader(os.path.join(d, "main.pdf")).pages)
    return err, ovr, mch, n, r.returncode

report = []
for book, pieces in BOOKS:
    book_dir = os.path.join(ASM, book)
    os.makedirs(book_dir, exist_ok=True)
    writer = PdfWriter()
    cursor = 0
    for name, rel, start, disp in pieces:
        dst = os.path.join(book_dir, name)
        copy_piece(os.path.join(ROOT, rel), dst)
        inject(os.path.join(dst, "main.tex"), start)
        err, ovr, mch, n, rc = compile2(dst)
        ok = (err == 0 and ovr == 0 and mch == 0 and rc == 0)
        report.append(f"{book}/{name:<12s} 起{start:>3d} {n:>2d}页 err={err} ovr={ovr} mch={mch} rc={rc} {'OK' if ok else '**FAIL**'}")
        if not ok:
            print("\n".join(report)); sys.exit(1)
        reader = PdfReader(os.path.join(dst, "main.pdf"))
        writer.append(reader)
        writer.add_outline_item(disp, cursor)
        cursor += n
    out = os.path.join(ASM, f"{book}.pdf")
    with open(out, "wb") as fh:
        writer.write(fh)
    report.append(f"■ {book}.pdf 合并 {cursor} 页")
print("\n".join(report))
