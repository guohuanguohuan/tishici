# -*- coding: utf-8 -*-
r"""对勘-P1测评（副本树-P1测评 内；只读调用正树 PDF，写入限本树）
判据（方案草案 §2.2＋任务书「与原印面对勘零漂移」）：
 A. 钉值/键面：答案册 body.tex 19 键值 ⊆ main-换装A/B.tex 逐字节在体；% ans: 锚 19；
 B. 工具链零漂：本树复编译「原样基线 main.pdf」 vs 正树原印面 main.pdf 逐页文本全等；
 C. 页级零漂移：false 档与原印面逐页像素差（150dpi）——p1、p2 须 0 差异像素；
    p3 容差＝仅件尾 \tailfill 新增（题面行零漂移另以「原件行文本子序列」证）；
 D. 固定栏溢出审计（P1 测评卷件型＝零高 \jpcol 不可回流）：各档逐页逐栏内容底边
    （文本∪图∪矢量线，剔页脚带）vs 版心底缘 266.6mm——超＝静默溢出（TeX 不报）；
 E. true 档答案印面读数：含「[答案]」×19；false 档含 0；「参考答案」仅 B-true 在。
产物：对勘-P1测评-out.txt ＋ png-* 目验图。
"""
import io, os, re, subprocess, sys
import fitz
from PIL import Image, ImageChops

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "测评卷")
PT = 72 / 25.4
ORIG_PDF = os.path.join(P, "00原件对照", "原印面-main.pdf")
BODY = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex"
OUT = []
def log(s):
    OUT.append(s); print(s)

def page_texts(pdf):
    d = fitz.open(pdf)
    return d, ["\n".join(l.strip() for l in pg.get_text().splitlines() if l.strip()) for pg in d]

# ---------- A. 键值钉值（body → 换装件 逐字节） ----------
blines = open(BODY, encoding="utf-8").read().splitlines()
st = next(i for i, l in enumerate(blines) if "【丁】测评卷答案" in l)
vals = {}
for ln in blines[st:]:
    m = re.match(r"^\\ansitem\{(\d+)\}\{(.+)\}\s*$", ln.strip())
    if m: vals["测-%s" % m.group(1)] = m.group(2)
    if ln.strip() == r"\end{multicols}" and vals: break
assert len(vals) == 19
for mode in ("A", "B"):
    src = open(os.path.join(P, "main-换装%s.tex" % mode), encoding="utf-8").read()
    miss = [k for k, v in vals.items() if ("\\ansitem{%s}{%s}" % (k.split("-")[1], v)) not in src]
    assert src.count("% ans:测-") == 19, "锚缺失"
    log("[A] %s案 钉值：19 键逐字节在体 %s；ans 锚＝19" % (mode, "零缺失 PASS" if not miss else "FAIL %s" % miss))

# ---------- B. 工具链零漂（原样基线 vs 原印面） ----------
d0, t0 = page_texts(ORIG_PDF)
d1, t1 = page_texts(os.path.join(P, "main.pdf"))
same = t0 == t1 and d0.page_count == d1.page_count
log("[B] 原样基线复编译 vs 原印面：页数 %d↔%d，逐页文本 %s" % (d0.page_count, d1.page_count, "全等 PASS" if same else "FAIL"))

# ---------- C. false 档页级零漂移 ----------
def pixdiff(pdfa, pdfb, dpi=150):
    da, db = fitz.open(pdfa), fitz.open(pdfb)
    res = []
    for i in range(max(da.page_count, db.page_count)):
        if i >= da.page_count or i >= db.page_count:
            res.append((i+1, None)); continue
        pa = da[i].get_pixmap(dpi=dpi); pb = db[i].get_pixmap(dpi=dpi)
        ia = Image.frombytes("RGB", (pa.width, pa.height), pa.samples)
        ib = Image.frombytes("RGB", (pb.width, pb.height), pb.samples)
        diff = ImageChops.difference(ia, ib)
        bbox = diff.getbbox()
        npx = sum(1 for px in diff.convert("L").getdata() if px > 8) if bbox else 0
        res.append((i+1, (bbox, npx)))
    return res

for j in ("main-换装A-false", "main-换装B-false"):
    for pgno, info in pixdiff(ORIG_PDF, os.path.join(P, j + ".pdf")):
        if info is None:
            log("[C] %s p%d：页数不齐 FAIL" % (j, pgno))
        else:
            bbox, npx = info
            note = "（差异仅在 p3 下部＝\tailfill 尾块新增区，150dpi 下 y>1299px）" if (bbox and bbox[1] > 1299) else ""
            log("[C] %s p%d：差异像素=%d%s" % (j, pgno, npx, note))
    # 原件行子序列（题面行零漂移）
    dj, tj = page_texts(os.path.join(P, j + ".pdf"))
    okall = True
    for i, t in enumerate(t0):
        it = iter("\n".join(tj).splitlines())
        for ln in t.splitlines():
            if not any(x == ln for x in it):
                okall = False; log("[C] %s p%d 原件行丢失：%r" % (j, i+1, ln[:30])); break
    log("[C] %s：原印面逐行文本子序列 %s（题面零漂移）" % (j, "PASS" if okall else "FAIL"))

# ---------- D. 固定栏静默溢出审计 ----------
# 卷式实测：原印面本就有内容底至 ~276mm（底余带是卷式常态）；页脚＝两侧签名块，剔之；
# 硬底线＝纸边 284.2mm；277~284.2＝触页脚带（红旗区）；>284.2＝出血纸外（内容丢失，FAIL）。
cols = {1: (8.9, 128.9), 2: (139.9, 259.9), 3: (270.9, 390.9)}
RED, BOT = 277.0, 284.2
FOOT_SIG = ("卷0", "羿郭工作室", "必修第三册", "物理")
def col_bottoms(pdf):
    d = fitz.open(pdf); out = {}
    for i, pg in enumerate(d, 1):
        ymax = {1: 0.0, 2: 0.0, 3: 0.0}
        items = [b[:4] for b in pg.get_text("blocks")
                 if not (any(s in b[4] for s in FOOT_SIG) and b[1] / PT > 265)]
        items += [im["bbox"] for im in pg.get_image_info() if im["bbox"][1] / PT < 276]
        items += [(dd["rect"].x0, dd["rect"].y0, dd["rect"].x1, dd["rect"].y1) for dd in pg.get_drawings()
                  if dd["rect"].y0 / PT > 30 and not (dd["rect"].y0 / PT > 265
                  and (dd["rect"].x0 / PT < 80 or dd["rect"].x1 / PT > 330))]
        for x0, y0, x1, y1 in items:
            cx = (x0 + x1) / 2 / PT
            for c, (a, b) in cols.items():
                if a <= cx <= b and y1 / PT > ymax[c]:
                    ymax[c] = y1 / PT
        out[i] = ymax
    return out
log(r"[D] 栏内容底边（mm；纸边 %.1f＝硬线，%.1f~%.1f＝触页脚带红旗区；零高 \jpcol 溢出 TeX 不报）：" % (BOT, RED, BOT))
for name, pdf in (("原印面", ORIG_PDF), ("A-true", os.path.join(P, "main-换装A-true.pdf")),
                  ("A-false", os.path.join(P, "main-换装A-false.pdf")), ("B-true", os.path.join(P, "main-换装B-true.pdf")),
                  ("B-false", os.path.join(P, "main-换装B-false.pdf"))):
    for i, ymax in sorted(col_bottoms(pdf).items()):
        flags = {c: ("!!出纸%.1f" % (y - BOT) if y > BOT + 0.05 else
                     ("旗:触脚带" if y > RED else "ok")) for c, y in ymax.items()}
        bad = any("!!" in v or "旗" in v for v in flags.values())
        log("    %-8s p%d 栏底边 %s → %s" % (name, i, {c: round(y, 1) for c, y in ymax.items()},
                                             ("FAIL " + str(flags)) if bad else "PASS"))

# ---------- E. 答案印面读数 ----------
import re as _re
for j, want in (("main-换装A-true", 19), ("main-换装A-false", 0), ("main-换装B-true", 19), ("main-换装B-false", 0)):
    d, t = page_texts(os.path.join(P, j + ".pdf"))
    alltxt = "\n".join(t)
    c = alltxt.count("[答案]")
    found = {int(m.group(1)) for m in _re.finditer(r"(\d{1,2})[.\uFF0E]\s*\[答案\]", alltxt)}
    miss = sorted(set(range(1, 20)) - found) if want else []
    fu = ("参考答案" in alltxt)
    log("[E] %s：[答案]×%d（应 %d）%s%s；附卷标题「参考答案」在=%s；页数=%d" %
        (j, c, want, "PASS" if c == want else "FAIL",
         ("；印面缺题号答案=%s（出纸丢失实锤）" % miss) if miss else "", fu, d.page_count))

# ---------- 目验 png ----------
for j in ("main", "main-换装A-true", "main-换装A-false", "main-换装B-true", "main-换装B-false"):
    dd = fitz.open(os.path.join(P, j + ".pdf"))
    odir = os.path.join(P, "png-" + j.replace("main-换装", "").replace("main", "原样基线"))
    os.makedirs(odir, exist_ok=True)
    for i, pg in enumerate(dd, 1):
        pg.get_pixmap(dpi=150).save(os.path.join(odir, "page%d.png" % i))

open(os.path.join(HERE, "对勘-P1测评-out.txt"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
print("\n[产物] 对勘-P1测评-out.txt；png-* 目验图")
