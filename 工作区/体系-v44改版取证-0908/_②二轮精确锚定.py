# ②片二轮：精确锚定全品行带＋我方标签大样本＋题号周边墨隙（只读）
import pymupdf, numpy as np, json
from PIL import Image

THR = 128
D = r"C:\提示词\工作区\全品结构提取\数学选必一\导学案页图"
imgs = {}
def im(page):
    if page not in imgs:
        imgs[page] = np.array(Image.open(fr"{D}\p{page:02d}.png").convert("L"))
    return imgs[page]

def runs_stroke(dark):
    rr = []
    for row in dark:
        c = 0
        for v in row:
            if v: c += 1
            elif c: rr.append(c); c = 0
        if c: rr.append(c)
    return float(np.median(rr)) if rr else 0.0

def probe(page, y0, y1, x0=0, x1=None):
    a = im(page)[y0:y1, x0:(x1 or im(page).shape[1])]
    dark = a < THR
    cols = np.where(dark.any(axis=0))[0]
    rows = np.where(dark.any(axis=1))[0]
    if len(cols) == 0:
        return None
    return {"x": (int(cols[0] + x0), int(cols[-1] + x0)), "y": (int(rows[0] + y0), int(rows[-1] + y0))}

# --- 探锚：p07 课堂评价题号行（v43 记 y491–529），p06 素养小结（y1039–1424 取首行带） ---
print("p07 题号带探针:", probe(7, 480, 540, 240, 400))
print("p07 题号带2  :", probe(7, 570, 640, 240, 400))
print("p06 素养小结带:", probe(6, 1030, 1090, 300, 1400))
print("p08 条目号带 :", probe(8, 2735, 2800, 240, 400))
print("p04 判断小问 :", probe(4, 2440, 2520, 400, 800))

def elem(page, box, tag, pad=2):
    a = im(page)[box[1] - pad:box[3] + pad, box[0] - pad:box[2] + pad]
    dark = a < THR
    if dark.sum() == 0:
        return None
    vals = a[dark]
    rows = np.where(dark.any(axis=1))[0]
    return {"tag": tag, "ink": round(dark.sum() / a.size, 3), "stroke": runs_stroke(dark),
            "gmin": int(vals.min()), "gmode": int(np.bincount(vals).argmax()),
            "ih": int(rows[-1] - rows[0] + 1)}

R = {}
# 全品课堂评价题号「1．」（用探针结果锚定——若探针失败改用v43坐标带内自适应）
for anchor, name in [((7, 480, 540, 240, 400), "课堂评价题号1"), ((7, 570, 640, 240, 400), "课堂评价题号2")]:
    p = probe(*anchor)
    if p:
        R[f"全品{name}"] = elem(anchor[0], (p["x"][0], p["y"][0], p["x"][1], p["y"][1]), name, 1)
# 全品素养小结楷体首行
p = probe(6, 1030, 1090, 300, 1400)
if p:
    R["全品素养小结楷体首行"] = elem(6, (p["x"][0], p["y"][0], p["x"][1], p["y"][1]), "xj", 1)
# 全品条目号「3．」p08 知识点二下
p = probe(8, 2735, 2800, 240, 400)
if p:
    R["全品条目号带"] = elem(8, (p["x"][0], p["y"][0], min(p["x"][1], p["x"][0] + 60), p["y"][1]), "tm", 1)
# 全品正文对照带（p06 例2题干 y1740–1782 x1010–1400）
R["全品正文对照"] = elem(6, (1010, 1740, 1400, 1782), "body", 0)

# --- 我方大样本：【答案】【解析】跨页 ---
PDF = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\main.pdf"
doc = pymupdf.open(PDF)
Z = 4.0
def ourbatch(pnos, want, nmax=12):
    res = []
    for pno in pnos:
        page = doc[pno]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csGRAY)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        for blk in page.get_text("dict")["blocks"]:
            if blk["type"]:
                continue
            for line in blk["lines"]:
                for sp in line["spans"]:
                    t = sp["text"].strip()
                    if t in want and round(sp["size"], 2) == 10.46 and "FZHT" in sp["font"]:
                        x0, y0, x1, y1 = sp["bbox"]
                        # 去掉首尾【】括号区：按字符数近似——取 12%~88% 宽度
                        w = x1 - x0
                        X0, Y0 = int((x0 + w * 0.14) * Z), int(max(0, (y0 - 1)) * Z)
                        X1, Y1 = int((x0 + w * 0.86) * Z), int((y1 + 1) * Z)
                        a = img[Y0:Y1, X0:X1]
                        dark = a < THR
                        if dark.sum() == 0:
                            continue
                        res.append({"ink": round(dark.sum() / a.size, 3), "stroke": runs_stroke(dark),
                                    "txt": t, "p": pno + 1})
                        if len(res) >= nmax:
                            return res
    return res

R["我方【答案】内字"] = ourbatch([2, 3, 4, 5, 6], {"【答案】"})
R["我方【解析】内字"] = ourbatch([2, 3, 4, 5, 6], {"【解析】"})

# --- 我方检测题号周边墨隙（p6/p7 题号行：右隙=题号右缘到同行下一墨列；上/下隙=行带到邻行墨） ---
def qgap(pno):
    page = doc[pno]
    out = []
    pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    for blk in page.get_text("dict")["blocks"]:
        if blk["type"]:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if sp["text"].strip() in ("1", "2", "3", "4", "5") and round(sp["size"], 2) == 11.36:
                    x0, y0, x1, y1 = [v * Z for v in sp["bbox"]]
                    band = img[int(y0) - 2:int(y1) + 2, :]
                    cols = np.where((band < THR).any(axis=0))[0]
                    right = cols[cols > x1]
                    rgap = (right[0] - x1) / Z if len(right) else None
                    # 行带上下：题号行带 ±2px 外的上下墨行距
                    rows_above = np.where((img[:int(y0) - 2, int(x0):int(x1)] < THR).any(axis=1))[0]
                    above = (int(y0) - 2 - rows_above[-1]) / Z if len(rows_above) else None
                    rows_below = np.where((img[int(y1) + 2:, int(x0):int(x1)] < THR).any(axis=1))[0]
                    below = (rows_below[0]) / Z if len(rows_below) else None
                    out.append({"txt": sp["text"].strip(), "右隙pt": round(rgap * 72 / 72, 1) if rgap else None,
                                "右隙px@288": round(rgap, 1) if rgap else None,
                                "上隙px@288": round(above, 1) if above is not None else None,
                                "下隙px@288": round(below, 1) if below is not None else None})
    return out

R["我方检测题号墨隙p7"] = qgap(6)
doc.close()

with open(r"C:\提示词\工作区\体系-v44改版取证-0908\_②二轮墨密墨隙.json", "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=1, default=str)
for k, v in R.items():
    print(k, "→", json.dumps(v, ensure_ascii=False, default=str)[:400])
