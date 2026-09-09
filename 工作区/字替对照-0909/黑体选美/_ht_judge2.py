# -*- coding: utf-8 -*-
"""标题黑体选型·第 2 轮（定榜）：
  定榜口径＝各家用「实装可用」的全部档位（思源＝NSC VF 细分阶梯；HarmonyOS＝6 档；普惠＝4 档），
  每岗先以竖笔粗标定字重（等密度口径），再测六项 |Δ|%。
  校验口径＝雅黑额外允许图像空间 binary_dilation +1/+2px 合成中间字重（方法学等化，
  检验测量法能否认出兰亭黑本家；雅黑仍禁止入选）。
另出：形态学裁片（喇叭口目检）＋章岗全串条。
"""
import pymupdf, numpy as np, json, os
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

QP = "C:/提示词/高中物理/参考/全品学练考官方样书/选必一/【5563】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 导学案.pdf"
FB = "C:/提示词/工作区/字替对照-0909/fonts/"
NF = "C:/提示词/工作区/字替对照-0909/variantE/_calib/fonts/"
OUT = "C:/提示词/工作区/字替对照-0909/黑体选美/"
os.makedirs(OUT, exist_ok=True)
EM = 96.0
METRICS = ("横笔粗", "竖笔粗", "advance", "字形高", "宽高比", "墨密")

CANDS = {
    "思源": [(f"w{w}", NF + f"NSC-w{w}.ttf") for w in
             (250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900)],
    "普惠": [(w, FB + f"PuHuiTi__Alibaba-PuHuiTi-{w}.ttf") for w in ("Regular", "Medium", "Bold", "Heavy")],
    "HarmonyOS": [(w, FB + f"_npm原始包/npm_fontpkg--harmony-os-sans-sc/package/HarmonyOS_Sans_SC_{w}.ttf")
                  for w in ("Thin", "Light", "Regular", "Medium", "Bold", "Black")],
    "雅黑(校验)": [("Regular", "C:/Windows/Fonts/msyh.ttc"), ("Bold", "C:/Windows/Fonts/msyhbd.ttc")],
}
DILATE_OK = {"雅黑(校验)": (0, 1, 2)}  # 校验口径：允许合成 +1/+2px 中间字重；其余品牌空＝仅实档

GANGS = [
    ("章20.67",  20.67, "第一章动量守恒定律",           (99.7, 75.8, 317.8, 99.4), 4),
    ("节16.88",  16.88, "动量",                         (284.1, 127.2, 336.9, 146.5), 4),
    ("课时13.0", 13.00, "学习任务一寻求碰撞中的不变量", (201.8, 163.6, 410.4, 178.5), 4),
    ("◆层10.09", 10.09, "参考答案",                     (71.6, 713.0, 114.6, 724.5), 3),
    ("角度10.09", 10.09, "角度二用动量定理定量计算",    (51.4, 56.4, 193.1, 68.0), 8),
    ("条目10.09", 10.09, "课时折射现象与折射定律",      (127.3, 410.8, 258.0, 422.4), 3),
]

def glyph_metrics(cell):
    dark = cell < 128
    ys, xs = np.where(dark)
    if ys.size == 0:
        return None
    g = dark[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = g.shape
    lr, lc = [], []
    for row in g:
        idx = np.flatnonzero(row)
        if idx.size:
            for s in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):
                lr.append(len(s))
    for col in g.T:
        idx = np.flatnonzero(col)
        if idx.size:
            for s in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):
                lc.append(len(s))
    sh = [L for L in lr if L < 0.5 * w]
    sv = [L for L in lc if L < 0.5 * h]
    if not sh or not sv:
        return None
    return dict(w=int(w), h=int(h), 竖笔粗=float(np.median(sh)), 横笔粗=float(np.median(sv)),
                宽高比=w / h, 墨密=float(g.sum()) / (w * h))

def render_chars(font, s, dilate=0):
    out = []
    for ch in s:
        if ch == "\u3000" or not ("\u4e00" <= ch <= "\u9fff"):
            continue
        im = Image.new("L", (int(EM) + 60, int(EM) + 60), 255)
        ImageDraw.Draw(im).text((30, int(EM * 1.6)), ch, font=font, fill=0, anchor="ls")
        a = np.asarray(im)
        if dilate:
            a = np.where(ndimage.binary_dilation(a < 128, iterations=dilate), 0, 255).astype(np.uint8)
        m = glyph_metrics(a)
        if m:
            out.append(m)
    return out

# ---------- 全品侧 ----------
doc = pymupdf.open(QP)
qp_data = {}
for name, pt, s, bbox, pno in GANGS:
    Z = EM / pt
    page = doc[pno - 1]
    chars = []
    for b in page.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for sp in l["spans"]:
                if (abs(sp["bbox"][0] - bbox[0]) < 1 and abs(sp["bbox"][1] - bbox[1]) < 1
                        and abs(sp["size"] - pt) < 0.01):
                    chars = sp["chars"]
    assert chars, name
    clip = pymupdf.Rect(bbox[0] - 0.3 * pt, bbox[1] - 0.3 * pt, bbox[2] + 0.3 * pt, bbox[3] + 0.3 * pt)
    pm = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csRGB, clip=clip)
    gray = np.asarray(Image.frombuffer("RGB", (pm.width, pm.height), pm.samples, "raw", "RGB", 0, 1).convert("L"))
    per, adv = [], []
    for i, c in enumerate(chars):
        ch = c["c"]
        if ch == "\u3000" or not ("\u4e00" <= ch <= "\u9fff"):
            continue
        bx = c["bbox"]
        cellimg = gray[max(0, int((bx[1] - clip.y0) * Z) - 2):int((bx[3] - clip.y0) * Z) + 3,
                       max(0, int((bx[0] - clip.x0) * Z) - 2):int((bx[2] - clip.x0) * Z) + 3]
        m = glyph_metrics(cellimg)
        if m:
            per.append(m)
        if i + 1 < len(chars) and chars[i + 1]["c"] != "\u3000":
            adv.append((chars[i + 1]["origin"][0] - c["origin"][0]) * Z)
    med = lambda k: float(np.median([p[k] for p in per]))
    qp_data[name] = dict(pt=pt, string=s, n=len(per), advance=float(np.median(adv)),
                         横笔粗=med("横笔粗"), 竖笔粗=med("竖笔粗"), 字形高=med("h"),
                         宽高比=med("宽高比"), 墨密=med("墨密"))
    print(f"[全品] {name}: n={len(per)} adv={qp_data[name]['advance']:.1f} 竖={med('竖笔粗'):.1f} "
          f"横={med('横笔粗'):.1f} 高={med('h'):.0f} 密={med('墨密'):.3f}")
doc.close()

# ---------- 候选侧（定榜）＋雅黑等化（校验） ----------
res = {}
for brand, weights in CANDS.items():
    dilates = DILATE_OK.get(brand, (0,))
    res[brand] = {}
    for name, pt, s, bbox, pno in GANGS:
        t = qp_data[name]
        variants = []
        for wname, wpath in weights:
            font = ImageFont.truetype(wpath, int(EM))
            for dil in dilates:
                perchar = render_chars(font, s, dil)
                if len(perchar) < 2:
                    continue
                med = lambda k: float(np.median([p[k] for p in perchar]))
                variants.append(dict(
                    weight=wname + (f"+{dil}px" if dil else ""),
                    竖笔粗=med("竖笔粗"), 横笔粗=med("横笔粗"), 字形高=med("h"),
                    宽高比=med("宽高比"), 墨密=med("墨密"),
                    advance=float(np.median([font.getlength(c) for c in s if "\u4e00" <= c <= "\u9fff"]))))
        best = min(variants, key=lambda v: abs(v["竖笔粗"] - t["竖笔粗"]))
        devs = {k: (best[k] - t[k]) / t[k] * 100.0 for k in METRICS}
        score = float(np.mean([abs(v) for v in devs.values()]))
        res[brand][name] = dict(weight=best["weight"], calib_px=best["竖笔粗"] - t["竖笔粗"],
                                devs=devs, score=score)
        print(f"[{brand}] {name}: {best['weight']:12s} 竖粗差={best['竖笔粗']-t['竖笔粗']:+.1f}px  "
              + "  ".join(f"{k}{devs[k]:+.1f}%" for k in METRICS) + f"  岗分={score:.2f}")

print("\n==== 定榜总偏差分（六项 |Δ|% 岗均值；越小越像） ====")
totals = {b: float(np.mean([res[b][g[0]]["score"] for g in GANGS])) for b in CANDS}
for b, v in sorted(totals.items(), key=lambda kv: kv[1]):
    print(f"{b:10s} 总分={v:6.2f}   " + "  ".join(f"{g[0]}={res[b][g[0]]['score']:.2f}" for g in GANGS))
json.dump(dict(qp=qp_data, cand=res, totals=totals),
          open(OUT + "偏差.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)

# ---------- 等化校验口径：全部品牌允许 ±2px 图像空间合成（回答"字重完全等化后谁最像"） ----------
print("\n==== 等化校验（各品牌 real 档 ∪ ±2px 合成；雅黑入选禁令不变） ====")
resE = {}
for brand, weights in CANDS.items():
    resE[brand] = {}
    for name, pt, s, bbox, pno in GANGS:
        t2 = qp_data[name]
        variants = []
        for wname, wpath in weights:
            font = ImageFont.truetype(wpath, int(EM))
            for dil in (-2, -1, 0, 1, 2):
                perchar = render_chars(font, s, dil)
                if len(perchar) < 2:
                    continue
                med = lambda k: float(np.median([p[k] for p in perchar]))
                variants.append(dict(weight=f"{wname}{'%+dpx' % dil if dil else ''}",
                                     竖笔粗=med("竖笔粗"), 横笔粗=med("横笔粗"), 字形高=med("h"),
                                     宽高比=med("宽高比"), 墨密=med("墨密"),
                                     advance=float(np.median([font.getlength(c) for c in s if "一" <= c <= "鿿"]))))
        def vkey(v):
            wd = v["weight"]
            d = 0
            if "px" in wd:
                d = int(wd.split("+")[1].replace("px", "").replace("-", ""))
            return (round(abs(v["竖笔粗"] - t2["竖笔粗"]), 3), abs(d))
        best = min(variants, key=vkey)
        devs = {k: (best[k] - t2[k]) / t2[k] * 100.0 for k in METRICS}
        resE[brand][name] = dict(weight=best["weight"], devs=devs,
                                 score=float(np.mean([abs(v) for v in devs.values()])))
    tot = float(np.mean([resE[brand][g[0]]["score"] for g in GANGS]))
    print(f"{brand:10s} 等化总分={tot:6.2f}   " + "  ".join(f"{g[0]}={resE[brand][g[0]]['score']:.2f}" for g in GANGS))
json.dump(dict(equalized=resE), open(OUT + "等化校验.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)

# ---------- 形态学裁片（章岗「守」高倍）＋ 章岗全串条 ----------
def render_qp_char(pno, bbox, pt, ch):
    Z = EM / pt * 2.2
    page = doc if False else pymupdf.open(QP)
    page = page[pno - 1]
    for b in page.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for sp in l["spans"]:
                if (abs(sp["bbox"][0] - bbox[0]) < 1 and abs(sp["bbox"][1] - bbox[1]) < 1
                        and abs(sp["size"] - pt) < 0.01):
                    for c in sp["chars"]:
                        if c["c"] == ch:
                            bx = c["bbox"]
                            clip = pymupdf.Rect(bx[0] - 0.15 * pt, bx[1] - 0.15 * pt,
                                                bx[2] + 0.15 * pt, bx[3] + 0.15 * pt)
                            pm = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csRGB, clip=clip)
                            page.parent.close()
                            return Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
    page.parent.close()
    return None

def render_font_char(path, ch, dil=0):
    font = ImageFont.truetype(path, int(EM * 2.2))
    im = Image.new("L", (int(EM * 2.2) + 80, int(EM * 2.2) + 80), 255)
    ImageDraw.Draw(im).text((40, int(EM * 2.2 * 1.5)), ch, font=font, fill=0, anchor="ls")
    a = np.asarray(im)
    if dil:
        a = np.where(ndimage.binary_dilation(a < 128, iterations=dil), 0, 255).astype(np.uint8)
    img = np.asarray(Image.fromarray(a).convert("RGB"))
    ys, xs = np.where(np.asarray(Image.fromarray(a)) < 128)
    pad = 8
    return Image.fromarray(img[max(0, ys.min() - pad):ys.max() + pad, max(0, xs.min() - pad):xs.max() + pad])

rows, H = [], 190
labf = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 24)
def addrow(label, img):
    img = img.resize((int(img.width * H / img.height), H), Image.LANCZOS)
    row = Image.new("RGB", (img.width + 240, H + 10), "white")
    ImageDraw.Draw(row).text((8, H // 2 - 14), label, font=labf, fill="black")
    row.paste(img, (240, 5))
    rows.append(row)

qpc = render_qp_char(4, (99.7, 75.8, 317.8, 99.4), 20.67, "守")
addrow("全品 FZLTZCHK(真迹)", qpc)
sel = {}
for brand, weights in CANDS.items():
    w = res[brand]["章20.67"]["weight"]
    base = w.split("+")[0]
    dil = int(w.split("+")[1].rstrip("px")) if "+" in w else 0
    path = dict(weights)[base]
    sel[brand] = (path, dil)
    addrow(f"{brand}({w})", render_font_char(path, "守", dil))
W = max(r.width for r in rows)
board = Image.new("RGB", (W, sum(r.height for r in rows) + 40), "white")
ImageDraw.Draw(board).text((8, 6), "形态学：章岗「守」笔画末端（兰亭黑微喇叭口 vs 平切）同竖粗对齐", font=labf, fill="black")
y = 36
for r in rows:
    board.paste(r, (0, y)); y += r.height
board.save(OUT + "对照HT-形态学.png")
print("已写", OUT + "对照HT-形态学.png", board.size)
