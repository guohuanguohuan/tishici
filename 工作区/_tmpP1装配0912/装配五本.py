# -*- coding: utf-8 -*-
# P1 装配轮 · 五本装订（G7 跨本连续页码·物理五本＝导学本/练习本/拓展本/测评本/答案本）
# 承 M2 装配四本.py 工艺（工作区/M2-第1章量产0911/_tmp装配装订0912/装配四本.py），物理线适配：
#   ①五本划分（拓展册独立成本三＝拍板增设）；②章末并入导学本末尾（任务书指定）；
#   ③答案册 body.tex 起页改写 44（义5-4）＋甲→乙 \clearpage 撤除（义6-1 试验丙定案）；
#   ④义6-2 G8 统一清扫在装配副本层执行（句末「。」/半角「.」→全角「.」·原件不动＝G7 双轨）；
#   ⑤测评卷装配副本速查表两处排布层修正（收尾记录 §4-2 #21）；⑥门＝五0（err/Overfull/Underfull/缺字/QP-FIGS）。
# 学史切片＝独立薄本（定案见装配记录），不注入跨本页码（自成页码制起 1），编译入册末散件。
import io, sys, os, re, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader, PdfWriter

ROOT = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷"
ASM = os.path.join(ROOT, "装配")
SKIP = re.compile(r"^(__pycache__|png)$|\.aux$|\.log$|\.out$|\.py$|\.pdf$|\.md$|\.json$|^_x[0-9].*\.(txt|log)$")

# (副本目录名, 源相对路径, 起始页, 书签显示名, 预期页数)
BOOKS = [
    ("导学本", [
        ("9.1电荷", "导学件/9.1电荷", 1, "9.1 电荷（导学件）", 3),
        ("9.2库仑定律", "导学件/9.2库仑定律", 4, "9.2 库仑定律（导学件）", 3),
        ("9.3电场电场强度", "导学件/9.3电场电场强度", 7, "9.3 电场 电场强度（导学件）", 4),
        ("9.4静电的防止与利用", "导学件/9.4静电的防止与利用", 11, "9.4 静电的防止与利用（导学件）", 4),
        ("章末-本章易错过关", "章末-本章易错过关", 15, "章末·本章易错过关（导学本末尾）", 2),
    ]),
    ("练习本", [
        ("9.1电荷", "练习件/9.1电荷", 17, "9.1 电荷（练习件）", 3),
        ("9.2库仑定律", "练习件/9.2库仑定律", 20, "9.2 库仑定律（练习件）", 4),
        ("9.3电场电场强度", "练习件/9.3电场电场强度", 24, "9.3 电场 电场强度（练习件）", 4),
        ("9.4静电的防止与利用", "练习件/9.4静电的防止与利用", 28, "9.4 静电的防止与利用（练习件）", 3),
    ]),
    ("拓展本", [
        ("拓展册", "拓展册", 31, "拓展册（46题）", 10),
    ]),
    ("测评本", [
        ("测评卷", "测评卷", 41, "单元素养测评卷（一）·第9章", 3),
    ]),
    ("答案本", [
        ("答案册", "答案册", 44, "参考答案册（导学·练习·拓展·测评全含）", 5),
    ]),
]
XUESHI = ("学史切片", "学史切片/第9章静电学史", "物理学史切片（第9章·5条）", 1)

CJK = "\u4e00-\u9fff"
re_dot = re.compile(r"[" + CJK + r"，、；：）】《》]\.(?![0-9A-Za-z])")
re_dotspace = re.compile(r"[" + CJK + r"，、；：）】《》]\.\\ (?!$)")

def clean_g8(text):
    """装配副本层 G8 句末标点统一清扫：。→. 与 半角句末.→.（去紧跟强制空格）；
    注释段保留（头注历史注记）、$..$ 数学段保护。返回(新文本, 替换数)。"""
    total = 0
    out = []
    for line in text.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        code, comm = (line, "") if m is None else (line[:m.start()], line[m.start():])
        parts = re.split(r"(\$[^$]*\$)", code)   # 奇数下标＝数学段，原样保留
        for i, p in enumerate(parts):
            if i % 2 == 1:
                continue
            n1 = p.count("。")
            p = p.replace("。", "．")
            p, n2 = re_dotspace.subn(lambda mo: mo.group(0)[0] + "．", p)
            p, n3 = re_dot.subn(lambda mo: mo.group(0)[0] + "．", p)
            total += n1 + n2 + n3
            parts[i] = p
        out.append("".join(parts) + comm)
    return "\n".join(out), total

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

def inject_main(tex_path, start):
    t = open(tex_path, encoding="utf-8").read()
    assert "\\begin{document}" in t, tex_path
    assert "装配轮G7" not in t, tex_path
    ins = ("\\begin{document}\n"
           "%装配轮G7跨本连续页码 setcounter 注入位（五本式·方案B）\n"
           "\\setcounter{page}{" + str(start) + "}")
    t = t.replace("\\begin{document}", ins, 1)
    open(tex_path, "w", encoding="utf-8").write(t)

def fix_ceping_main(tex_path):
    """测评卷装配副本专改（收尾记录 §4-2 #21 两处排布层）：速查表 tan→\\tan 三处＋单位前薄空格三处。"""
    t = open(tex_path, encoding="utf-8").read()
    a = "$mgtan\\alpha$；$\\frac{mgtan\\alpha}{q}$，水平向右；$\\frac{mgr^{2}tan\\alpha}{kq}$"
    b = "$mg\\tan\\alpha$；$\\frac{mg\\tan\\alpha}{q}$，水平向右；$\\frac{mgr^{2}\\tan\\alpha}{kq}$"
    c = "$12$\\unit{N}；$6\\times10^{-5}$\\unit{C}；$1.6$\\unit{kg}"
    d = "$12\\,\\unit{N}$；$6\\times10^{-5}\\,\\unit{C}$；$1.6\\,\\unit{kg}$"
    assert t.count(a) == 1 and t.count(c) == 1
    t = t.replace(a, b).replace(c, d)
    open(tex_path, "w", encoding="utf-8").write(t)

def do_answyi61(body_path):
    """答案册装配副本（义5-4＋义6-1）：body.tex 起页 1→44；甲→乙 \\clearpage 撤除（试验丙五0定案）；
    乙→丙／丙→丁 两处分本界维持（试验甲全撤复发 Underfull×1＝五0 不达标，登记回退依据）。"""
    t = open(body_path, encoding="utf-8").read()
    assert "\\setcounter{page}{1}" in t
    t = t.replace("\\setcounter{page}{1}",
                  "\\setcounter{page}{44}   % 装配轮义5-4：五本跨本连续页码（本五答案本起页 44）", 1)
    t, n = re.subn(r"^\\clearpage   % 分本切页：甲→乙.*$",
                   "%装配轮义6-1：甲→乙分本 clearpage 撤除（P2 章末尾留白位点·栏流接续·试验丙五0定案）",
                   t, count=1, flags=re.M)
    assert n == 1
    open(body_path, "w", encoding="utf-8").write(t)

def compile2(d):
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "main.tex"],
                           cwd=d, capture_output=True)
    log = open(os.path.join(d, "main.log"), encoding="utf-8", errors="ignore").read()
    err = len(re.findall(r"^! ", log, re.M))
    ovr = log.count("Overfull")
    und = log.count("Underfull")
    mch = log.count("Missing character")
    qpf = len(re.findall(r"QP-FIGS", log))
    n = len(PdfReader(os.path.join(d, "main.pdf")).pages)
    return err, ovr, und, mch, qpf, n, r.returncode

report, cleanstat = [], {}
for book, pieces in BOOKS:
    book_dir = os.path.join(ASM, book)
    os.makedirs(book_dir, exist_ok=True)
    writer = PdfWriter()
    cursor = 0
    for name, rel, start, disp, want in pieces:
        dst = os.path.join(book_dir, name)
        copy_piece(os.path.join(ROOT, rel), dst)
        # 专改先行（义6-1／#21），再全件 G8 清扫（义6-2）
        if name == "答案册":
            do_answyi61(os.path.join(dst, "body.tex"))
        if name == "测评卷":
            fix_ceping_main(os.path.join(dst, "main.tex"))
        inject_main(os.path.join(dst, "main.tex"), start) if name != "答案册" else None
        if name == "答案册":
            pass  # 起页值在 body.tex（M2 同位工艺）
        c = 0
        for f in ("main.tex", "body.tex"):
            p = os.path.join(dst, f)
            if os.path.exists(p):
                t = open(p, encoding="utf-8").read()
                t2, k = clean_g8(t)
                open(p, "w", encoding="utf-8").write(t2)
                c += k
        cleanstat[f"{book}/{name}"] = c
        err, ovr, und, mch, qpf, n, rc = compile2(dst)
        ok = (err == 0 and ovr == 0 and und == 0 and mch == 0 and qpf == 0 and rc == 0 and n == want)
        report.append(f"{book}/{name:<12s} 起{start:>3d} {n:>2d}页 清扫{c:>3d}处 err={err} ovr={ovr} und={und} mch={mch} qpfig={qpf} rc={rc} {'OK' if ok else '**FAIL**'}")
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

# 学史切片：独立薄本（自成页码制起 1，不注入）——装配副本编译＋单册 PDF
name, rel, disp, want = XUESHI
dst = os.path.join(ASM, name)
copy_piece(os.path.join(ROOT, rel), dst)
t = open(os.path.join(dst, "main.tex"), encoding="utf-8").read()
t2, c = clean_g8(t)
open(os.path.join(dst, "main.tex"), "w", encoding="utf-8").write(t2)
cleanstat["学史切片/第9章静电学史"] = c
err, ovr, und, mch, qpf, n, rc = compile2(dst)
ok = (err == 0 and ovr == 0 and und == 0 and mch == 0 and qpf == 0 and rc == 0 and n == want)
report.append(f"学史切片/独立薄本 {n}页 清扫{c}处 err={err} ovr={ovr} und={und} mch={mch} qpfig={qpf} rc={rc} {'OK' if ok else '**FAIL**'}")
shutil.copy2(os.path.join(dst, "main.pdf"), os.path.join(ASM, "学史切片.pdf"))
total = sum(n for _, n in cleanstat.items())
print("\n".join(report))
print("G8 清扫合计：", sum(cleanstat.values()), "处；逐件：", cleanstat)
