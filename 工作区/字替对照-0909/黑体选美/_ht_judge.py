# -*- coding: utf-8 -*-
"""标题黑体选型测量赛：思源 vs 普惠 vs HarmonyOS vs 雅黑(校验) —— 对 全品兰亭黑族(FZLT*).
靶子＝【5563】RJ 导学案文字层 span（矢量真迹，高倍渲染）。
方法：每岗先用「竖笔粗」把候选字重标定到全品等粗（等密度口径），再在同串同字号上测
  横笔粗/竖笔粗/advance(字面宽)/字形高/宽高比/墨密 六项，逐岗 |Δ|% → 总分。
"""
import pymupdf, numpy as np, json, os
from PIL import Image, ImageDraw, ImageFont

QP = "C:/提示词/高中物理/参考/全品学练考官方样书/选必一/【5563】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 导学案.pdf"
FB = "C:/提示词/工作区/字替对照-0909/fonts/"
OUT = "C:/提示词/工作区/字替对照-0909/黑体选美/"
os.makedirs(OUT, exist_ok=True)
EM = 96.0  # 渲染 em 像素（全品 zoom=EM/pt，候选 PIL size=int(EM)）

CANDS = {
    "思源":   [(w, FB + f"NotoSansSC-{w}.otf") for w in ("Regular", "Medium", "Bold", "Black")],
    "普惠":   [(w, FB + f"PuHuiTi__Alibaba-PuHuiTi-{w}.ttf") for w in ("Regular", "Medium", "Bold", "Heavy")],
    "HarmonyOS": [(w, FB + f"候选字体/HarmonyOSSansSC-{w}.ttf") for w in ("Regular", "Medium", "Bold", "Black")],
    "雅黑(校验)": [("Regular", "C:/Windows/Fonts/msyh.ttc"), ("Bold", "C:/Windows/Fonts/msyhbd.ttc")],
}
GANGS = [  # (岗名, pt, 串, span_bbox, 页码1-based)
    ("章20.67",  20.67, "第一章动量守恒定律",           (99.7, 75.8, 317.8, 99.4), 4),
    ("节16.88",  16.88, "动量",                         (284.1, 127.2, 336.9, 146.5), 4),
    ("课时13.0", 13.00, "学习任务一寻求碰撞中的不变量", (201.8, 163.6, 410.4, 178.5), 4),
    ("◆层10.09", 10.09, "参考答案",                     (71.6, 713.0, 114.6, 724.5), 3),
    ("角度10.09", 10.09, "角度二用动量定理定量计算",    (51.4, 56.4, 193.1, 68.0), 8),
    ("条目10.09", 10.09, "课时折射现象与折射定律",      (127.3, 410.8, 258.0, 422.4), 3),
]
METRICS = ("横笔粗", "竖笔粗", "advance", "字形高", "宽高比", "墨密")

def runs_med(img, axis, cap_ratio):
    """沿 axis 方向的 run 长度集合的中位（剔除 ≥cap_ratio×长的＝正交笔画/横条）。"""
    m = img.astype(bool)
    lens = []
    if axis == 0:  # 每行水平 run（量竖笔粗）
        for row in m:
            idx = np.flatnonzero(row)
            if idx.size == 0:
                continue
            splits = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)
            lens += [len(s) for s in splits]
    else:          # 每列垂直 run（量横笔粗）
        for col in m.T:
            idx = np.flatnonzero(col)
            if idx.size == 0:
                continue
            splits = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)
            lens += [len(s) for s in splits]
    lens = [L for L in lens if L <= max(2, cap_ratio * (max(m.shape) if False else 1))]
    return lens

def glyph_metrics(cell):
    """cell＝灰度小图（含边距）。返回 tight 域六项。"""
    dark = cell < 128
    ys, xs = np.where(dark)
    if ys.size == 0:
        return None
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    g = dark[y0:y1 + 1, x0:x1 + 1]
    h, w = g.shape
    lr = []
    for row in g:
        idx = np.flatnonzero(row)
        if idx.size == 0:
            continue
        for s in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):
            lr.append(len(s))
    lc = []
    for col in g.T:
        idx = np.flatnonzero(col)
        if idx.size == 0:
            continue
        for s in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):
            lc.append(len(s))
    sh = [L for L in lr if L < 0.5 * w]   # 竖笔粗候选
    sv = [L for L in lc if L < 0.5 * h]   # 横笔粗候选
    if not sh or not sv:
        return None
    return dict(w=int(w), h=int(h),
                竖笔粗=float(np.median(sh)), 横笔粗=float(np.median(sv)),
                宽高比=w / h, 墨密=float(g.sum()) / (w * h))

# ---------- 全品侧 ----------
doc = pymupdf.open(QP)
qp_data = {}
for name, pt, s, bbox, pno in GANGS:
    Z = EM / pt
    page = doc[pno - 1]
    # 该 span 的 rawdict 逐字格（origin/advance 矢量真值）
    chars = []
    for b in page.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for sp in l["spans"]:
                if (abs(sp["bbox"][0] - bbox[0]) < 1 and abs(sp["bbox"][1] - bbox[1]) < 1
                        and abs(sp["size"] - pt) < 0.01):
                    chars = sp["chars"]
    assert chars, f"{name} rawdict 未命中"
    clip = pymupdf.Rect(bbox[0] - 0.3 * pt, bbox[1] - 0.3 * pt, bbox[2] + 0.3 * pt, bbox[3] + 0.3 * pt)
    pm = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csRGB, clip=clip)
    img = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)
    gray = np.asarray(Image.fromarray(img).convert("L"))
    per = []
    adv = []
    for i, c in enumerate(chars):
        ch = c["c"]
        if ch == "\u3000" or ch.strip() == "" or not ('\u4e00' <= ch <= '\u9fff'):
            continue
        bx = c["bbox"]
        cx0 = int((bx[0] - clip.x0) * Z) - 2; cx1 = int((bx[2] - clip.x0) * Z) + 3
        cy0 = int((bx[1] - clip.y0) * Z) - 2; cy1 = int((bx[3] - clip.y0) * Z) + 3
        cellimg = gray[max(0, cy0):cy1, max(0, cx0):cx1]
        m = glyph_metrics(cellimg)
        if m is None:
            continue
        m["char"] = ch
        per.append(m)
        if i + 1 < len(chars) and chars[i + 1]["c"] != "\u3000":
            adv.append((chars[i + 1]["origin"][0] - c["origin"][0]) * Z)
    med = lambda k: float(np.median([p[k] for p in per]))
    qp_data[name] = dict(pt=pt, string=s, em_px=EM, n=len(per),
                         advance=float(np.median(adv)),
                         横笔粗=med("横笔粗"), 竖笔粗=med("竖笔粗"),
                         字形高=med("h"), 宽高比=med("宽高比"), 墨密=med("墨密"),
                         per=per, img=gray)
    print(f"[全品] {name}: n={len(per)} adv={qp_data[name]['advance']:.1f} 竖={med('竖笔粗'):.1f} "
          f"横={med('横笔粗'):.1f} 高={med('h'):.0f} 密={med('墨密'):.3f}")
doc.close()

# ---------- 候选侧 ----------
def cand_string_img(font, s):
    W = int(EM) * (len(s) + 2) + 40
    H = int(EM) * 3
    im = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(im)
    x = 30.0
    base = int(EM * 2)
    for ch in s:
        d.text((x, base), ch, font=font, fill=0, anchor="ls")
        x += font.getlength(ch)
    return im, 30.0, base

res = {}
for brand, weights in CANDS.items():
    res[brand] = {}
    for name, pt, s, bbox, pno in GANGS:
        target = qp_data[name]
        perweight = {}
        for wname, wpath in weights:
            font = ImageFont.truetype(wpath, int(EM))
            perchar = []
            for ch in s:
                if ch == "\u3000" or not ('\u4e00' <= ch <= '\u9fff'):
                    continue
                im = Image.new("L", (int(EM) + 60, int(EM) + 60), 255)
                d = ImageDraw.Draw(im)
                d.text((30, int(EM * 1.6)), ch, font=font, fill=0, anchor="ls")
                m = glyph_metrics(np.asarray(im))
                if m:
                    perchar.append(m)
            med = lambda k: float(np.median([p[k] for p in perchar]))
            perweight[wname] = dict(竖笔粗=med("竖笔粗"), 横笔粗=med("横笔粗"),
                                    字形高=med("h"), 宽高比=med("宽高比"),
                                    墨密=med("墨密"),
                                    advance=float(np.median([font.getlength(c) for c in s if '\u4e00' <= c <= '\u9fff'])))
        wstar = min(perweight, key=lambda w: abs(perweight[w]["竖笔粗"] - target["竖笔粗"]))
        m = perweight[wstar]
        devs = {}
        for k in METRICS:
            devs[k] = (m[k] - target[k]) / target[k] * 100.0
        score = float(np.mean([abs(v) for v in devs.values()]))
        res[brand][name] = dict(weight=wstar, calib_px=m["竖笔粗"] - target["竖笔粗"],
                                metrics=m, devs=devs, score=score)
        print(f"[{brand}] {name}: 字重={wstar:8s} 竖粗差={m['竖笔粗']-target['竖笔粗']:+.1f}px  "
              + "  ".join(f"{k}{devs[k]:+.1f}%" for k in METRICS) + f"  岗分={score:.2f}")

print("\n==== 总偏差分（六项 |Δ|% 的岗位均值，再全岗均值；越小越像） ====")
totals = {}
for brand in CANDS:
    tot = float(np.mean([res[brand][g[0]]["score"] for g in GANGS]))
    totals[brand] = tot
    per = "  ".join(f"{g[0]}={res[brand][g[0]]['score']:.2f}" for g in GANGS)
    print(f"{brand:10s} 总分={tot:6.2f}   {per}")
json.dump(dict(qp=qp_data, cand=res, totals=totals),
          open(OUT + "偏差.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("已写", OUT + "偏差.json")
