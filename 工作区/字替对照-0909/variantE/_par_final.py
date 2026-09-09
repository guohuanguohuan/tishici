# -*- coding: utf-8 -*-
# TikZ ∥ 终测（干净复测）：极简单字形页 + 按形状拣笔
#   拣笔条件：墨高 150–300px(zoom24)、逐行质心斜率折角 −24°~−30°、水平 run 中位 4–14px、
#   恰得两笔且同高配对 → 四项对比全品 E-BZ 真迹
import pymupdf, numpy as np, math
from PIL import Image
from scipy import ndimage

Z = 24.0
SIZE_PT = 10.09
REF = dict(ang=-26.71, h=0.972, w=0.037, gap=0.260)

doc = pymupdf.open("_calib/parcalib.pdf")
page = doc[0]
# 用 a/b 文字 bbox 定位 ∥（tikz 画在两字母之间）
words = page.get_text("words")
ab = [w for w in words if w[4] in ("a", "b")]
assert len(ab) == 2, f"a/b 定位失败: {[w[4] for w in words]}"
x0 = min(w[0] for w in ab) - 8
x1 = max(w[2] for w in ab) + 8
y0 = min(w[1] for w in ab) - 12
y1 = max(w[3] for w in ab) + 12
pm = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csRGB,
                     clip=pymupdf.Rect(x0, y0, x1, y1))
arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)
doc.close()
Image.fromarray(arr).save("_par_my24x.png")
dark = (arr[:, :, 0] < 128) & (arr[:, :, 1] < 128) & (arr[:, :, 2] < 128)
pt_per_px = 1.0 / Z

lab, n = ndimage.label(dark)
cands = []
for i in range(1, n + 1):
    m = (lab == i)
    ys, xs = np.where(m)
    h = ys.max() - ys.min() + 1
    if not (150 <= h <= 300):
        continue
    rows = {}
    for r in range(ys.min(), ys.max() + 1):
        if m[r].any():
            rows[r] = np.average(np.flatnonzero(m[r]))
    rr = np.array(sorted(rows))
    k, _ = np.polyfit(rr, np.array([rows[r] for r in rr]), 1)
    ang = math.degrees(math.atan(k))
    if not (-30 <= ang <= -24):
        continue
    runs = []
    for r in range(ys.min(), ys.max() + 1):
        row = m[r]
        if not row.any():
            continue
        p = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        for s, e in zip(np.where(p == 1)[0], np.where(p == -1)[0]):
            runs.append(e - s)
    med = float(np.median(runs))
    if not (4 <= med <= 14):
        continue
    cands.append(dict(mask=m, h=h, ang=ang, med=med, ytop=int(ys.min()), ybot=int(ys.max())))

print(f"按形状拣得笔画 {len(cands)} 条（a/b/杂散应被过滤）")
cands.sort(key=lambda c: np.where(c["mask"])[1].min())
assert len(cands) == 2, f"应恰两笔，实得 {len(cands)}"

def ends(c):
    m = c["mask"]
    top = m[c["ytop"]]
    bot = m[c["ybot"]]
    def runl(row):
        p = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        return [e - s for s, e in zip(np.where(p == 1)[0], np.where(p == -1)[0])]
    return runl(top), runl(bot)

L, R = cands
gapL, gapR = [], []
lm, rm = L["mask"], R["mask"]
for r in range(max(L["ytop"], R["ytop"]), min(L["ybot"], R["ybot"]) + 1):
    if lm[r].any() and rm[r].any():
        le = np.flatnonzero(lm[r]).max()
        rs = np.flatnonzero(rm[r]).min()
        gapL.append(rs - le)
gm = float(np.median(gapL))

ang = (L["ang"] + R["ang"]) / 2
hh = (L["h"] + R["h"]) / 2 * pt_per_px / SIZE_PT
ww = (L["med"] + R["med"]) / 2 * pt_per_px / SIZE_PT
gg = gm * pt_per_px / SIZE_PT
lt, lb = ends(L)
rt, rb = ends(R)
print(f"左笔: 墨高 {L['h']}px  倾角 {L['ang']:.2f}°  笔粗中位 {L['med']:.1f}px  顶行run {lt} 底行run {lb}")
print(f"右笔: 墨高 {R['h']}px  倾角 {R['ang']:.2f}°  笔粗中位 {R['med']:.1f}px  顶行run {rt} 底行run {rb}")
print(f"==> 倾角 {ang:.2f}° (全品 {REF['ang']})   墨高 {hh:.3f}em (全品 {REF['h']})   "
      f"水平笔粗 {ww:.3f}em (全品 {REF['w']})   间隙 {gg:.3f}em (全品 {REF['gap']})")
ok = (abs(ang - REF['ang']) <= 0.6 and abs(hh - REF['h']) <= 0.02
      and abs(ww - REF['w']) <= 0.008 and abs(gg - REF['gap']) <= 0.012)
print("端点水平平头：", "是" if (lt and lb and rt and rb) else "否",
      f"(顶 run {lt}/{rt}, 底 run {lb}/{rb}, 中位 {L['med']:.1f}px)")
print("四项判定：", "PASS" if ok else "FAIL")
