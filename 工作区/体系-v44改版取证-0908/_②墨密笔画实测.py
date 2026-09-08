# ②片专用：双指标字重/墨密/墨色实测（我方 v4.3 main.pdf 渲染 × 全品数学扫描页图；只读）
# 口径：灰度阈值128（沿v43简报）；墨密=暗像素占bbox面积比；笔画=暗run中位宽；墨色=暗核最小/众数灰度。
import pymupdf, numpy as np, json
from PIL import Image

THR = 128
out = {}

def metrics(arr):
    """arr: 2D uint8 灰度，已裁剪到元素bbox"""
    dark = arr < THR
    n_dark = int(dark.sum())
    if n_dark == 0:
        return None
    ink = n_dark / arr.size
    runs = []
    for row in dark:
        c = 0
        for v in row:
            if v:
                c += 1
            elif c:
                runs.append(c); c = 0
        if c:
            runs.append(c)
    stroke = float(np.median(runs)) if runs else 0.0
    vals = arr[dark]
    # 行墨迹高：含暗像素的行数；字面高=暗像素行跨度
    rows = np.where(dark.any(axis=1))[0]
    h = int(rows[-1] - rows[0] + 1) if len(rows) else 0
    return {"ink": round(ink, 3), "stroke": stroke, "gmin": int(vals.min()),
            "gmode": int(np.bincount(vals).argmax()), "ih": h}

# ---------- A. 我方 v4.3 ----------
PDF = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\main.pdf"
Z = 4.0  # 渲染倍率
doc = pymupdf.open(PDF)

def our(pno, flt, label, n=8, pad=1.0):
    page = doc[pno]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    res = []
    for blk in page.get_text("dict")["blocks"]:
        if blk["type"]:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if flt(sp):
                    x0, y0, x1, y1 = sp["bbox"]
                    X0, Y0 = int(max(0, (x0 - pad) * Z)), int(max(0, (y0 - pad) * Z))
                    X1, Y1 = int(min(pix.width, (x1 + pad) * Z)), int(min(pix.height, (y1 + pad) * Z))
                    m = metrics(img[Y0:Y1, X0:X1])
                    if m:
                        m["pt"] = round(sp["size"], 2)
                        m["font"] = sp["font"].split("+")[-1].split("--")[0]
                        res.append(m)
                    if len(res) >= n:
                        return res
    return res

def flt_text(t_pref=None, font=None, size=None):
    def f(sp):
        if font and sp["font"].split("+")[-1].split("--")[0] != font:
            return False
        if size and round(sp["size"], 2) != size:
            return False
        if t_pref and not any(sp["text"].startswith(p) for p in t_pref):
            return False
        return True
    return f

ours = {}
ours["正文"] = our(1, flt_text(font="FZSSJW", size=10.46), "body", 10)
ours["检测题号"] = our(6, flt_text(t_pref=["1", "2", "3", "4", "5"], font="TimesNewRomanPSMT", size=11.36), "qnum", 5)
ours["检测题号点"] = our(6, flt_text(t_pref=["．"], font="FZHTJW", size=11.36), "qnumdot", 5)
ours["【答案】"] = our(5, flt_text(t_pref=["【答案】"], font="FZHTJW", size=10.46), "ans", 7)
ours["【解析】"] = our(5, flt_text(t_pref=["【解析】"], font="FZHTJW", size=10.46), "jx", 7)
ours["例N标签"] = our(2, flt_text(t_pref=["例", "变式"], font="FZHTJW", size=11.96), "lib", 8)
ours["◆知识点标题"] = our(0, flt_text(t_pref=["知识点"], font="FZHTJW", size=11.96), "zsd", 3)
ours["素养小结内容"] = our(2, flt_text(font="KaiTi", size=10.46), "xiaojie", 6)
ours["页脚小字"] = our(1, flt_text(font="FZSSJW", size=5.48), "foot", 4)
ours["学习目标序号"] = our(0, flt_text(t_pref=["1", "2"], font="TimesNewRomanPS-BoldMT", size=10.96), "mubiao", 3)
ours["题侧灰标"] = our(2, flt_text(t_pref=["〔简单"], font="FZSSJW", size=7.97), "ce", 4)
# 条目号：p1 左栏行首 TNR@10.46 数字.（x0≈版心左 15mm=42.52pt ±3）
def flt_tiaomu(sp):
    if not (sp["font"].split("+")[-1].split("--")[0] == "TimesNewRomanPSMT" and round(sp["size"], 2) == 10.46):
        return False
    t = sp["text"].strip()
    return t in ("1.", "2.", "3.", "4.", "5.", "6.") and abs(sp["bbox"][0] - 43.0) < 6
ours["条目号"] = our(0, flt_tiaomu, "tm", 6)

out["我方v43"] = ours
doc.close()

# ---------- B. 全品数学扫描 ----------
D = r"C:\提示词\工作区\全品结构提取\数学选必一\导学案页图"
imgs = {}
def qp(page, box, label, pad=2):
    if page not in imgs:
        imgs[page] = np.array(Image.open(fr"{D}\p{page:02d}.png").convert("L"))
    im = imgs[page]
    x0, y0, x1, y1 = box
    m = metrics(im[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad])
    if m:
        m["pxmm"] = 14.057
    return m

qpout = {}
qpout["正文(例2题干)"] = qp(6, (1010, 1740, 1400, 1782), "body")
qpout["课堂评价题号1."] = qp(7, (248, 491, 330, 529), "qnum")
qpout["例1标签"] = qp(5, (1478, 2184, 1600, 2236), "li1")
qpout["变式标签"] = qp(7, (248, 1112, 380, 1161), "bs")
qpout["◆探究点一标题"] = qp(5, (1546, 2074, 2100, 2125), "tjd")
qpout["◆知识点一标题(去◆)"] = qp(4, (300, 1590, 700, 1640), "zsd")
qpout["条目号3．"] = qp(8, (248, 2740, 300, 2790), "tm")
qpout["素养小结楷体"] = qp(6, (350, 2740, 1300, 2790), "xj")
qpout["页脚小字"] = qp(4, (2059, 3950, 2554, 3973), "foot")
qpout["花形右灰词"] = qp(4, (1165, 1490, 1420, 1540), "gray")
qpout["诊断小问号(1)"] = qp(4, (600, 2450, 680, 2500), "wen")
# 字面高辅助行（知识点一标题行整带，含◆与名）
qpout["◆知识点一标题(整行)"] = qp(4, (240, 1585, 900, 1645), "zsdall")
out["全品扫描"] = qpout

with open(r"C:\提示词\工作区\体系-v44改版取证-0908\_②墨密笔画实测.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

for side, dd in out.items():
    print(f"===== {side} =====")
    for k, v in dd.items():
        if isinstance(v, list):
            if not v:
                print(f"  {k:22s} 无样本")
                continue
            ink = [x["ink"] for x in v]; st = [x["stroke"] for x in v]; ih = [x["ih"] for x in v]
            gm = [x["gmode"] for x in v]
            print(f"  {k:22s} n={len(v)} 墨密{min(ink):.3f}~{max(ink):.3f} 笔画{min(st):.0f}~{max(st):.0f}(中位{sorted(st)[len(st)//2]}) 字面高{min(ih)}~{max(ih)} 暗核众灰{min(gm)}~{max(gm)} @{v[0]['pt']}pt")
        elif v:
            print(f"  {k:22s} 墨密{v['ink']:.3f} 笔画{v['stroke']} 字面高{v['ih']} 暗核{v['gmin']}/{v['gmode']} (box采样)")
        else:
            print(f"  {k:22s} 无样本")
