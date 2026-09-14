# -*- coding: utf-8 -*-
# M3 S6 工装② 装配三本.py ——三本一串装订（装配方案.md §一/§二/§四/§五）
# 先例：M2 _tmp装配装订0912/装配四本.py。M3 适配：
#   ①取件序 46 件参数化＝导学 21＋练习 21＋本三 5（canonical 序：衔接→01~06→06B→07~19）；
#   ②副本树剔除：png 目录/aux/log/pdf/py/md/json 剔除，figs 随目录（方案 §一.2）；
#   ③\setcounter{page}{起始页} 注入（G7 方案B 跨本连续，起页由基线页数自动累计，不硬编码）；
#   ④编译入口路由：ke 件制＝main-true/false.tex 双壳（\mthreepure）；
#     juan 件制＝main.tex（含详解）／main-pure.tex（纯题）（\ifshowans，案B 附卷制）；
#   ⑤pypdf 按序合并＋add_outline_item 件名书签：21/21/5＝47 条（断言）；
#   ⑥双档各跑一遍（true 含详解印本／false 纯题版），页码链/书签各自成套（方案 §四）；
#   ⑦A1 页数断言：逐件实测＝基线（S2/S3 报告 §1.4 逐片表＋本三 S4 出口在位实测 2026-09-14），
#     漂移即红旗退出（起页链随基线，漂移必断链）；
#   ⑧产出 装配读数.json＝工装③终验页脚.py 的同源输入。
# 用法：python 装配三本.py [--sandbox]
#   正式态 副本树/合并 PDF/读数 json 落 成卷/装配/；--sandbox 落 工作区/_tmpM3S6沙箱0914/装配/
#   源 成卷/ 全程只读（整目录拷贝出副本树后在副本上注入编译）。
import io, sys, os, re, json, shutil, subprocess, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader, PdfWriter

WS   = r"C:\提示词\工作区"
ROOT = os.path.join(WS, "M3-第2章量产0913", "成卷")          # 只读源
ASM  = (os.path.join(WS, "_tmpM3S6沙箱0914", "装配") if "--sandbox" in sys.argv
        else os.path.join(ROOT, "装配"))                      # 写入域（沙箱/正式）
STY_MD5 = "7c3930362be8a0a2bdf21bbf8ac16573"                 # qp-m3 钉后版（E2）

# ---- 取件序 46 件（rel, 显示名, mark 页脚件标识, (true 页, false 页), kind ke|juan） ----
K, J = "ke", "juan"
DAO = [  # 本一 导学件 21（S2 收拢验报告 §1.4 逐片表；课时02 true 5→6、课时14 18/8→19/9
         #  系换装轮改件后在位实测回填 2026-09-14——A1 红旗首件实证，收验基线回填义务在收验侧）
    ("衔接节",                  "衔接（2.8 预备）",                    "导学件",     (6, 3),  K),
    ("课时01-坐标法",           "第1课时 坐标法",                      "导学件",     (6, 3),  K),
    ("课时02-倾斜角与斜率",      "第2课时 倾斜角与斜率",                "导学件",     (6, 3),  K),
    ("课时03-方向向量与法向量",   "第3课时 方向向量与法向量",            "导学件",     (5, 2),  K),
    ("课时04-点斜式与斜截式",     "第4课时 点斜式与斜截式",              "导学件",     (5, 3),  K),
    ("课时05-两点式与一般式",     "第5课时 两点式与一般式",              "导学件",     (7, 3),  K),
    ("课时06-两条直线的位置关系",  "第6课时 两条直线的位置关系",          "导学件",     (5, 3),  K),
    ("课时06B-2.2.4点到直线距离", "第6课时B 点到直线的距离（2.2.4）",    "导学件",     (5, 3),  K),
    ("课时07-圆的方程",          "第7课时 圆的方程",                    "导学件",     (5, 3),  K),
    ("课时08-直线与圆的位置关系",  "第8课时 直线与圆的位置关系",          "导学件",     (5, 3),  K),
    ("课时09-圆与圆的位置关系",   "第9课时 圆与圆的位置关系",            "导学件",     (5, 3),  K),
    ("课时10-2.4曲线与方程",     "第10课时 曲线与方程（2.4）",          "导学件",     (6, 3),  K),
    ("课时11-2.5.1椭圆的标准方程", "第11课时 椭圆的标准方程（2.5.1）",    "导学件",     (6, 3),  K),
    ("课时12-2.5.2椭圆的几何性质", "第12课时 椭圆的几何性质（2.5.2）",    "导学件",     (6, 3),  K),
    ("课时13-2.6.1双曲线的标准方程", "第13课时 双曲线的标准方程（2.6.1）", "导学件",    (7, 3),  K),
    ("课时14-2.6.2双曲线性质",   "第14课时 双曲线的性质（2.6.2）",      "导学件",     (19, 9), K),
    ("课时15-2.7.1抛物线方程",   "第15课时 抛物线方程（2.7.1）",        "导学件",     (10, 5), K),
    ("课时16-2.7.2抛物线性质",   "第16课时 抛物线的性质（2.7.2）",      "导学件",     (12, 5), K),
    ("课时17-2.8①压轴综合一",    "第17课时 压轴综合一（2.8①）",        "导学件",     (14, 4), K),
    ("课时18-2.8②压轴综合二",    "第18课时 压轴综合二（2.8②）",        "导学件",     (9, 4),  K),
    ("课时19-章末总结与复习",     "第19课时 章末总结与复习（章末件）",   "导学件",     (7, 4),  K),
]
LIAN = [  # 本二 练习件 21（S3 全收验报告 §1.4 逐片表；序＝canonical 与本一同）
    ("衔接节",                  "衔接 配套练习",       "练习件", (4, 2), K),
    ("课时01-坐标法",           "第1课时 配套练习",    "练习件", (4, 2), K),
    ("课时02-倾斜角与斜率",      "第2课时 配套练习",    "练习件", (3, 2), K),
    ("课时03-方向向量与法向量",   "第3课时 配套练习",    "练习件", (4, 2), K),
    ("课时04-点斜式与斜截式",     "第4课时 配套练习",    "练习件", (4, 2), K),
    ("课时05-两点式与一般式",     "第5课时 配套练习",    "练习件", (5, 2), K),
    ("课时06-两条直线的位置关系",  "第6课时 配套练习",    "练习件", (4, 2), K),
    ("课时06B-2.2.4点到直线距离", "第6课时B 配套练习",   "练习件", (4, 2), K),
    ("课时07-圆的方程",          "第7课时 配套练习",    "练习件", (3, 2), K),
    ("课时08-直线与圆的位置关系",  "第8课时 配套练习",    "练习件", (3, 2), K),
    ("课时09-圆与圆的位置关系",   "第9课时 配套练习",    "练习件", (4, 2), K),
    ("课时10-2.4曲线与方程",     "第10课时 配套练习",   "练习件", (4, 2), K),
    ("课时11-2.5.1椭圆的标准方程", "第11课时 配套练习",  "练习件", (4, 2), K),
    ("课时12-2.5.2椭圆的几何性质", "第12课时 配套练习",  "练习件", (5, 2), K),
    ("课时13-2.6.1双曲线的标准方程", "第13课时 配套练习", "练习件", (5, 2), K),
    ("课时14-2.6.2双曲线性质",   "第14课时 配套练习",   "练习件", (5, 2), K),
    ("课时15-2.7.1抛物线方程",   "第15课时 配套练习",   "练习件", (4, 2), K),
    ("课时16-2.7.2抛物线性质",   "第16课时 配套练习",   "练习件", (4, 2), K),
    ("课时17-2.8①压轴综合一",    "第17课时 配套练习",   "练习件", (5, 2), K),
    ("课时18-2.8②压轴综合二",    "第18课时 配套练习",   "练习件", (7, 3), K),
    ("课时19-章末总结与复习",     "第19课时 配套练习",   "练习件", (5, 2), K),
]
SAN = [  # 本三 测评拓展本 5（S4 出口在位实测 2026-09-14；U1 内序＝拓展上→拓展下→测评→滚A→滚B）
    ("拓展册/上册", "拓展册·上册（2.1~2.6.1 域）",   "拓展册（上）", (28, 11), K),
    ("拓展册/下册", "拓展册·下册（2.6.2~2.8 域）",   "拓展册（下）", (34, 12), K),
    ("测评卷",      "单元素养测评卷（二）·第二章",   "测评卷",       (4, 3),  J),
    ("滚动卷/滚A",  "滚动测评卷 A",                  "滚动卷",       (3, 2),  J),
    ("滚动卷/滚B",  "滚动测评卷 B",                  "滚动卷",       (3, 2),  J),
]
BOOKS = [("本一导学本", "导学件", DAO), ("本二练习本", "练习件", LIAN), ("本三测评拓展本", None, SAN)]
ENTRY = {K: {"true": "main-true.tex", "false": "main-false.tex"},       # ke 件制双壳
         J: {"true": "main.tex",      "false": "main-pure.tex"}}       # juan 件制单源两入口

# ---- 副本树：png/aux/log/pdf/py/md/json 剔除，figs 随目录（方案 §一.2） ----
SKIP_DIR  = ("png", "__pycache__")
SKIP_FILE = re.compile(r"\.(aux|log|pdf|py|md|json)$|^_b[0-9]\.txt$")

def copy_piece(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR]      # figs 等其余目录随树
        rel = os.path.relpath(root, src)
        tgt = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(tgt, exist_ok=True)
        for f in files:
            if SKIP_FILE.search(f):
                continue
            shutil.copy2(os.path.join(root, f), os.path.join(tgt, f))

def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()

# ---- setcounter 注入：入口 tex 无 \begin{document}（壳）则解析 \input 注被引件 ----
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
    assert "装配轮S6" not in t, f"{cur} 已有注入痕迹"
    ins = ("\\begin{document}\n"
           "%装配轮S6三本跨本连续页码（G7方案B）setcounter 注入位\n"
           "\\setcounter{page}{" + str(start) + "}")
    t = t.replace("\\begin{document}", ins, 1)
    with open(os.path.join(d, cur), "w", encoding="utf-8") as fh:
        fh.write(t)

def compile2(d, entry):
    job = entry[:-4]                                   # main-true / main-pure / main
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

# ---- 主流程：双档各跑一遍（方案 §四） ----
data = {"sty_md5": STY_MD5, "sandbox": "--sandbox" in sys.argv, "modes": {}}
report = []
for mode in ("true", "false"):
    mi = 0 if mode == "true" else 1
    cursor_global = 1                                   # 跨本连续页码（不随本复位）
    data["modes"][mode] = {"books": [], "total_pages": 0, "total_bookmarks": 0}
    for book, jianming_default, pieces in BOOKS:
        book_dir = os.path.join(ASM, mode, book)
        os.makedirs(book_dir, exist_ok=True)
        writer, cursor = PdfWriter(), 0
        rec = {"book": book, "pdf": f"{mode}/{book}.pdf", "start": cursor_global,
               "pieces": [], "bookmarks": 0}
        for name, disp, mark, pages2, kind in pieces:
            baseline = pages2[mi]
            start = cursor_global
            dst = os.path.join(book_dir, name.replace("/", "_"))
            copy_piece(os.path.join(ROOT, ("导学件/" if pieces is DAO else
                                           "练习件/" if pieces is LIAN else "") + name), dst)
            got = md5_of(os.path.join(dst, "qp-m3.sty"))
            assert got == STY_MD5, f"{dst} qp-m3.sty md5 漂移: {got}"
            entry = ENTRY[kind][mode]
            inject(os.path.join(dst, entry), start)
            err, ovr, mch, n, rc = compile2(dst, entry)
            ok = (err == 0 and ovr == 0 and mch == 0 and rc == 0 and n == baseline)
            tag = "OK" if ok else "**FAIL**"
            report.append(f"[{mode}] {book}/{name:<22s} 起{start:>3d} {n:>2d}页(基线{baseline}) "
                          f"err={err} ovr={ovr} mch={mch} rc={rc} {tag}")
            if not ok:
                print("\n".join(report)); sys.exit(1)
            rec["pieces"].append({"name": name, "disp": disp, "mark": mark, "kind": kind,
                                  "start": start, "pages": n})
            writer.append(PdfReader(os.path.join(dst, entry[:-4] + ".pdf")))
            writer.add_outline_item(disp, cursor)
            cursor += n
            cursor_global += n
        out = os.path.join(ASM, mode, f"{book}.pdf")
        with open(out, "wb") as fh:
            writer.write(fh)
        n_bm = len(PdfReader(out).outline)
        assert n_bm == len(pieces), f"{book} 书签 {n_bm} ≠ {len(pieces)}"
        rec["pages"], rec["bookmarks"] = cursor, n_bm
        data["modes"][mode]["books"].append(rec)
        data["modes"][mode]["total_pages"] += cursor
        data["modes"][mode]["total_bookmarks"] += n_bm
        report.append(f"■ [{mode}] {book}.pdf 合并 {cursor} 页（起{rec['start']}）书签 {n_bm} 条")
    report.append(f"■ [{mode}] 全册 {data['modes'][mode]['total_pages']} 页 "
                  f"书签合计 {data['modes'][mode]['total_bookmarks']} 条")

with open(os.path.join(ASM, "装配读数.json"), "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1)
report.append("■ 装配读数.json 已落 " + ASM)
print("\n".join(report))
