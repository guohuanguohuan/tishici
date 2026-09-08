# ②片三轮：等密度(px/mm一致)字重实测＋物理例N数字归属＋铁证裁片导出（只读）
import pymupdf, numpy as np, json
from PIL import Image
import os

THR = 128
OUT = r"C:\提示词\工作区\体系-v44改版取证-0908\_tmp扫差0908b"
os.makedirs(OUT, exist_ok=True)
Z = 14.18 / 2.835  # zoom=5.0 → 14.18px/mm，与全品扫描 14.176px/mm 等密度

def runs_stroke(dark):
    rr = []
    for row in dark:
        c = 0
        for v in row:
            if v: c += 1
            elif c: rr.append(c); c = 0
        if c: rr.append(c)
    return float(np.median(rr)) if rr else 0.0

PDF = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v4\导学件\main.pdf"
doc = pymupdf.open(PDF)
pages_img = {}
def page_img(pno):
    if pno not in pages_img:
        pix = doc[pno].get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csGRAY)
        pages_img[pno] = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return pages_img[pno]

def m(a):
    dark = a < THR
    if dark.sum() == 0:
        return None
    vals = a[dark]
    rows = np.where(dark.any(axis=1))[0]
    return {"ink": round(dark.sum() / a.size, 3), "stroke": runs_stroke(dark),
            "gmin": int(vals.min()), "gmode": int(np.bincount(vals).argmax()),
            "ih": int(rows[-1] - rows[0] + 1)}

res = {}
def our_spans(pno, want, exclude_bracket=False, nmax=10, name=""):
    img = page_img(pno)
    acc = []
    for blk in doc[pno].get_text("dict")["blocks"]:
        if blk["type"]:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if want(sp):
                    x0, y0, x1, y1 = [v * Z for v in sp["bbox"]]
                    if exclude_bracket:
                        w = x1 - x0
                        x0, x1 = x0 + w * 0.15, x1 - w * 0.15
                    a = img[max(0, int(y0) - 1):int(y1) + 1, max(0, int(x0) - 1):int(x1) + 1]
                    mm = m(a)
                    if mm:
                        mm["txt"] = sp["text"].strip()[:10]
                        acc.append(mm)
                    if len(acc) >= nmax:
                        return acc
    return acc

fz = lambda f, s=None: (lambda sp: ("FZHT" in sp["font"] or sp["font"] == f) and (s is None or round(sp["size"], 2) == s))
res["o_正文"] = our_spans(1, lambda sp: "FZSSJW" in sp["font"] and round(sp["size"], 2) == 10.46 and len(sp["text"].strip()) > 6, nmax=10)
res["o_检测题号数字"] = our_spans(6, lambda sp: sp["font"] == "TimesNewRomanPSMT" and round(sp["size"], 2) == 11.36 and sp["text"].strip() in "12345", nmax=5)
res["o_例N汉字"] = our_spans(2, lambda sp: "FZHT" in sp["font"] and round(sp["size"], 2) == 11.96 and sp["text"].strip()[:1] in ("例", "变"), nmax=6)
res["o_例N数字"] = our_spans(2, lambda sp: sp["font"] == "TimesNewRomanPSMT" and round(sp["size"], 2) == 11.96, nmax=6)
res["o_【答案】内字"] = our_spans(3, lambda sp: sp["text"].strip() == "【答案】" and round(sp["size"], 2) == 10.46, exclude_bracket=True, nmax=8)
res["o_【解析】内字"] = our_spans(3, lambda sp: sp["text"].strip() == "【解析】" and round(sp["size"], 2) == 10.46, exclude_bracket=True, nmax=8)
res["o_◆知识点汉字"] = our_spans(0, lambda sp: "FZHT" in sp["font"] and round(sp["size"], 2) == 11.96 and "知识点" in sp["text"], nmax=3)
res["o_条目号数字"] = our_spans(0, lambda sp: sp["font"] == "TimesNewRomanPSMT" and round(sp["size"], 2) == 10.46 and sp["text"].strip() in ("1.", "2.", "3.", "4.") and abs(sp["bbox"][0] - 43) < 6, nmax=4)
res["o_素养小结楷体"] = our_spans(2, lambda sp: "KaiTi" in sp["font"] and round(sp["size"], 2) == 10.46 and len(sp["text"].strip()) > 4, nmax=6)
res["o_页脚小字"] = our_spans(1, lambda sp: "FZSSJW" in sp["font"] and round(sp["size"], 2) == 5.48, nmax=4)

# ---- 物理PDF：例N数字归属＋【科学探究】栏目标签铁证渲染裁片 ----
PHY = r"C:\提示词\高中物理\参考\全品学练考官方样书\选必一\【5563】2025-2026（上）全品学练考 高中物理 选择性必修第一册 RJ 导学案.pdf"
phy = pymupdf.open(PHY)
digit12 = []
li_rect = None
tanjiu = None
for pno in range(phy.page_count):
    d = phy[pno].get_text("dict")
    for b in d["blocks"]:
        if b["type"]:
            continue
        for l in b["lines"]:
            spans = l["spans"]
            for i, sp in enumerate(spans):
                if round(sp["size"], 1) == 12.0 and sp["font"].split("+")[-1].split("--")[0] != "FZSSK":
                    digit12.append((pno + 1, sp["font"].split("+")[-1].split("--")[0], round(sp["size"], 2), sp["text"][:6]))
                if sp["text"].strip() == "例" and round(sp["size"], 1) == 12.0 and li_rect is None:
                    li_rect = (pno, sp["bbox"])
                if sp["text"].strip() == "【科学探究】" and tanjiu is None:
                    tanjiu = (pno, sp["bbox"])
res["物理_12pt档全部span"] = digit12[:15]

# 铁证裁片：物理 例N 标签行 / 【科学探究】行；我方 例1 行 / 【答案】行 / 检测题号行
def crop_pdf(docx, pno, bbox, path, pad_pt=2, zoom=8):
    x0, y0, x1, y1 = bbox
    pix = docx[pno].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=pymupdf.Rect(x0 - pad_pt, y0 - pad_pt, x1 + pad_pt, y1 + pad_pt), colorspace=pymupdf.csGRAY)
    pix.save(path)
    return path

if li_rect:
    pno, bb = li_rect
    line_r = None
    for b in phy[pno].get_text("dict")["blocks"]:
        if b["type"]:
            continue
        for l in b["lines"]:
            for sp in l["spans"]:
                if sp["text"].strip() == "例":
                    line_r = l["bbox"]
    crop_pdf(phy, pno, line_r, fr"{OUT}\②_全品物理_例N行_铁证.png")
if tanjiu:
    pno, bb = tanjiu
    crop_pdf(phy, pno, bb, fr"{OUT}\②_全品物理_科学探究标签_铁证.png")

# 我方裁片（同 zoom）
def our_line_crop(pno, want, path, pad=2.5):
    for b in doc[pno].get_text("dict")["blocks"]:
        if b["type"]:
            continue
        for l in b["lines"]:
            for sp in l["spans"]:
                if want(sp):
                    crop_pdf(doc, pno, l["bbox"], path, pad_pt=pad, zoom=8)
                    return True
    return False

our_line_crop(2, lambda sp: sp["text"].strip() == "例" and round(sp["size"], 2) == 11.96, fr"{OUT}\②_我方_例N行.png")
our_line_crop(3, lambda sp: sp["text"].strip() == "【答案】", fr"{OUT}\②_我方_答案解析行.png")
our_line_crop(6, lambda sp: sp["text"].strip() in ("1", "2") and round(sp["size"], 2) == 11.36, fr"{OUT}\②_我方_检测题号行.png")
our_line_crop(0, lambda sp: "知识点" in sp["text"] and round(sp["size"], 2) == 11.96, fr"{OUT}\②_我方_知识点标题行.png")

# 全品数学扫描裁片：例1标签(p05) / 课堂评价题号(p07) / ◆知识点标题(p04)
DD = r"C:\提示词\工作区\全品结构提取\数学选必一\导学案页图"
def crop_scan(page, box, path, pad=4):
    a = Image.open(fr"{DD}\p{page:02d}.png").convert("L")
    x0, y0, x1, y1 = box
    a.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad)).save(path)

crop_scan(5, (1478, 2184, 1720, 2236), fr"{OUT}\②_全品扫描_例1行.png")
crop_scan(7, (248, 480, 560, 545), fr"{OUT}\②_全品扫描_检测题号行.png")
crop_scan(4, (240, 1585, 900, 1645), fr"{OUT}\②_全品扫描_知识点标题行.png")

doc.close()
phy.close()

with open(r"C:\提示词\工作区\体系-v44改版取证-0908\_②等密度字重.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)

for k, v in res.items():
    if isinstance(v, list) and v and isinstance(v[0], dict) and "stroke" in v[0]:
        st = [x["stroke"] for x in v]; ik = [x["ink"] for x in v]
        print(f"{k:18s} n={len(v)} 笔画{sorted(st)[len(st)//2]}px(范围{min(st)}~{max(st)}) 墨密中位{sorted(ik)[len(ik)//2]:.3f} 例:{v[0].get('txt','')!r}")
    else:
        print(k, "→", str(v)[:300])
print("crops saved to", OUT)
