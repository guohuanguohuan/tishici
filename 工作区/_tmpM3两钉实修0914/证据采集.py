# -*- coding: utf-8 -*-
r"""出战重现·证据采集（只读渲染，全部产物落 _tmpM3两钉实修0914/截图/）
  ① 滚A p1 十框位：原印面 vs 旧病ctl(旧sty) vs 钉后ctl(新sty) —— 矢量笔画框(≈5.5×10.2pt)计数+逐框坐标比对
  ② 最小平行件：钉后 5 处 \parallel → 10 框形貌核
  ③ 测评卷 p3 速查表：三面同区裁剪（原印面/旧病/钉后）
  ④ 三栏括线最小件：旧病(无\linewidth钉) vs 病愈(件面\jpcol补钉) 全页双面
"""
import io, os, sys
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(S, "截图")
os.makedirs(OUT, exist_ok=True)
M2 = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
TREE = r"C:\提示词\工作区\_tmp换装预备0913\副本树-测评本"
NEG = r"C:\提示词\工作区\_tmpM3两钉预研0913\负测"

def boxes(pdf, pno=1, wlo=5.0, whi=6.0, hlo=9.5, hhi=11.0):
    doc = fitz.open(pdf)
    pg = doc[pno - 1]
    out = []
    for d in pg.get_drawings():
        if d.get("fill") is None:
            continue
        r = d["rect"]
        if wlo <= r.width <= whi and hlo <= r.height <= hhi:
            out.append((round(r.y0, 1), round(r.x0, 1), round(r.width, 2), round(r.height, 2)))
    doc.close()
    return sorted(out)

def render_clip(pdf, pno, clip, dpi):
    doc = fitz.open(pdf)
    pix = doc[pno - 1].get_pixmap(dpi=dpi, clip=fitz.Rect(*clip), alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return im

def font(sz=16):
    for p in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def grid(cells, labels, cols, path, pad=6, band=30):
    """cells: row-major list of PIL images; labels: 同排布文字"""
    rows = (len(cells) + cols - 1) // cols
    w = max(im.width for im in cells) + pad * 2
    h = max(im.height for im in cells) + pad * 2 + band
    cvs = Image.new("RGB", (w * cols, h * rows), (255, 255, 255))
    dr = ImageDraw.Draw(cvs)
    f = font()
    for i, (im, lb) in enumerate(zip(cells, labels)):
        r, c = divmod(i, cols)
        x0, y0 = c * w, r * h
        dr.text((x0 + 4, y0 + 4), lb, fill=(0, 0, 160), font=f)
        cvs.paste(im, (x0 + pad, y0 + band))
    cvs.save(path)
    print("截图→", path)

# ---------- ① 滚A p1 十框位 ----------
A = os.path.join(M2, r"滚动卷\滚A\main.pdf")          # 原印面
B = os.path.join(TREE, r"滚动卷A\main-ctl.pdf")       # 旧病ctl（旧sty 编）
C = os.path.join(S, r"复编-滚A\main-ctl.pdf")         # 钉后ctl（新sty 编）
ba, bb, bc = boxes(A), boxes(B), boxes(C)
print("① 滚A p1 矢量笔画框（≈5.5×10.2pt）：原印面 %d 框｜旧病ctl %d 框｜钉后ctl %d 框"
      % (len(ba), len(bb), len(bc)))
print("   原印面十框位(y0,x0,w,h)：", ba)
same = ba == bc
print("   钉后ctl 逐框坐标比对：", "与原印面全等 ✓" if same else "不等 ✗ " + str(bc))
M = 28.3465  # mm→pt
pg = fitz.open(A)[0]
bands = []
for y0, x0, w, h in ba:
    for b in bands:
        if b[0] - 20 <= y0 <= b[1] + 20:
            b[0], b[1] = min(b[0], y0), max(b[1], y0 + h)
            b[2], b[3] = min(b[2], x0), max(b[3], x0 + w)
            break
    else:
        bands.append([y0, y0 + h, x0, x0 + w])
cells, labels = [], []
for i, (y0, y1, x0, x1) in enumerate(sorted(bands), 1):
    clip = (max(0, x0 - 25), max(0, y0 - 16), min(pg.rect.x1, x1 + 25), min(pg.rect.y1, y1 + 16))
    cells.append(render_clip(A, 1, clip, 220)); labels.append("A 原印面 band%d" % i)
    cells.append(render_clip(B, 1, clip, 220)); labels.append("B ctl-旧sty(旧病) band%d" % i)
    cells.append(render_clip(C, 1, clip, 220)); labels.append("C ctl-新sty(钉后) band%d" % i)
grid(cells, labels, 3, os.path.join(OUT, "平行框-滚Ap1-三面.png"))

# ---------- ② 最小平行件 ----------
mS = os.path.join(S, "最小-平行框.pdf")
mb = boxes(mS)
print("② 最小平行件（钉后 5 处\\parallel）：%d 框；形貌集合 %s" % (len(mb), sorted({(w, h) for _, _, w, h in mb})))
log = open(os.path.join(S, "最小-平行框.log"), encoding="utf-8", errors="replace").read()
print("   body \\meaning\\parallel =", "TikZ 矢量宏 ✓" if "tikzpicture" in log.split("PAR-MIN-BODY: ")[1][:80] else "非 TikZ ✗")

# ---------- ③ 测评卷 p3 速查表 ----------
A3 = os.path.join(M2, r"测评卷\main.pdf")
B3 = os.path.join(TREE, r"测评卷\main-ctl.pdf")
C3 = os.path.join(S, r"复编-测评卷\main-ctl.pdf")
doc = fitz.open(A3); pg3 = doc[2]
rect3 = pg3.rect
hit = None
for b in pg3.get_text("blocks"):
    if "题号" in b[4] and "答案" in b[4] or "题号" in b[4]:
        hit = fitz.Rect(b[0], b[1], b[2], b[3]); break
doc.close()
clip = (max(0, hit.x0 - 15), max(0, hit.y0 - 25), min(rect3.x1, hit.x1 + 15), min(rect3.y1, hit.y0 + 235))
cells = [render_clip(p, 3, clip, 220) for p in (A3, B3, C3)]
labels = ["A 原印面 p3 速查表", "B ctl-旧sty（行高回落病）", "C ctl-新sty（钉①病愈）"]
grid(cells, labels, 3, os.path.join(OUT, "速查表-测评卷p3-三面.png"))

# ---------- ④ 括线最小件 ----------
lb = render_clip(os.path.join(NEG, "orig", "p-linewidth.pdf"), 1, None, 100) if False else None
def full(pdf, dpi):
    doc = fitz.open(pdf); pix = doc[0].get_pixmap(dpi=dpi, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples); doc.close(); return im
cells = [full(os.path.join(NEG, "orig", "p-linewidth.pdf"), 110),
         full(os.path.join(NEG, "patch", "p-linewidth.pdf"), 110)]
grid(cells, ["BAD 无\\linewidth钉：括线横穿三栏(旧病)", "GOOD 件面\\jpcol补钉：括线=120mm 栏宽(病愈)"],
     2, os.path.join(OUT, "括线-最小件-双面.png"))

print("①结论：钉后ctl 滚A p1 十框位 %s" % ("与原印面逐框全等" if same else "有差异"))
