# -*- coding: utf-8 -*-
"""③三期 01 image3 修复重出：用 ③图重绘/_gen_redraw.py 同代码路径调边距重出（主脑裁决①批准）。
缺陷（③二期目检）：一期 image3 底缘 O/x 标注裁半（底缘触墨、O 贴左缘；证据 ③二期\\img3_底缘.png）。
处置＝仅扩绘图窗口边距（xlim/ylim 下界放宽），figsize 3.6×2.9cm／FS=9pt／线宽/要素零改动
→ 设计显示尺寸与字高 [9,12]pt 带域不变（台账 #1 参数维持）。
产物：③三期\\I2_image3_fix.png（不覆盖 ③图重绘\\I2_image3.png 一期交付物，可溯）。
自验：像素规格＝一期同值／灰阶（alpha=255+chroma=0）／300dpi／墨迹 bbox 四边留白（一期为触底触左），
FAIL 即 exit 1。"""
import os, sys, io, importlib.util
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, '../③图重绘/_gen_redraw.py')
OUT_PNG = os.path.join(HERE, 'I2_image3_fix.png')
OLD_PNG = os.path.join(HERE, '../③图重绘/I2_image3.png')
DEFECT_EV = os.path.join(HERE, '../③二期/img3_底缘.png')

spec = importlib.util.spec_from_file_location('gen_redraw', GEN)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)   # __main__ 保护：仅取函数与常量，不批量重出

def fig_line_p0p_fixed():
    # 与 _gen_redraw.fig_line_p0p 逐行同构，仅 ax.set_xlim/ax.set_ylim 边距放宽：
    #   x 下界 -0.6→-0.80（O 贴左缘 → 留白）；y 下界 -0.6→-1.05（O/x 底缘裁半 → 留白）
    fig, ax = G.newfig(3.6, 2.9)
    ax.set_xlim(-0.80, 5.2); ax.set_ylim(-1.05, 4.0)
    G.axes_xy(ax, (-0.4, 5.0), (-0.4, 3.8), 0.0, 0.0)
    x = np.array([1.0, 4.4]); y = 0.75 * (x - 1.0) + 0.7
    ax.plot(x, y, color="k", lw=G.LW)
    ax.text(4.5, 0.75 * 3.5 + 0.7 + 0.15, "$l$", fontsize=G.FS)
    ax.plot([2.2], [0.75 * 1.2 + 0.7], "o", ms=2.6, color="k")
    ax.plot([3.4], [0.75 * 2.4 + 0.7], "o", ms=2.6, color="k")
    ax.text(2.25, 0.75 * 1.2 + 0.7 - 0.42, "$P_0$", fontsize=G.FS)
    ax.text(3.45, 0.75 * 2.4 + 0.7 - 0.42, "$P$", fontsize=G.FS)
    fig.savefig(OUT_PNG, dpi=G.DPI, facecolor="white")
    import matplotlib.pyplot as plt
    plt.close(fig)
    print('wrote', OUT_PNG)

def ink_bbox(im, thr=250):
    a = np.array(im.convert('RGB')).astype(int)
    mask = (a < thr).any(axis=2)
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), int(mask.sum())

r = {}
fig_line_p0p_fixed()

# ---- 自验 ----
new = Image.open(OUT_PNG)
old = Image.open(OLD_PNG)
r['new_px'] = new.size; r['old_px'] = old.size
assert new.size == old.size == (425, 342), f'像素规格漂移 {new.size} vs 一期 {old.size}'
r['new_mode'] = new.mode; r['old_mode'] = old.mode
dpi = new.info.get('dpi'); r['dpi'] = dpi
assert dpi and abs(dpi[0] - 300) < 1.5, f'dpi 异常 {dpi}'
a = np.array(new).astype(int)
alpha = a[..., 3]
chroma = (a[..., :3].max(2) - a[..., :3].min(2))
r['alpha_min'] = int(alpha.min()); r['chroma_max'] = int(chroma.max())
assert alpha.min() == 255 and chroma.max() == 0, f'非灰阶 alpha_min={alpha.min()} chroma_max={chroma.max()}'

nb = ink_bbox(new); ob = ink_bbox(old)
r['ink_bbox_new(x0,y0,x1,y1,inkpx)'] = nb
r['ink_bbox_old(x0,y0,x1,y1,inkpx)'] = ob
H, W = new.size[1], new.size[0]
margins_new = dict(left=nb[0], top=nb[1], right=W - 1 - nb[2], bottom=H - 1 - nb[3])
margins_old = dict(left=ob[0], top=ob[1], right=W - 1 - ob[2], bottom=H - 1 - ob[3])
r['margins_new_px'] = margins_new; r['margins_old_px'] = margins_old
log = print
log(f"一期(缺陷)墨迹边距 px = {margins_old}（bottom/left 触缘）")
log(f"重出(修复)墨迹边距 px = {margins_new}")
assert margins_new['bottom'] >= 10, f"底缘仍触墨 bottom={margins_new['bottom']}"
assert margins_new['left'] >= 10, f"左缘仍贴墨 left={margins_new['left']}"
assert margins_new['top'] >= 5 and margins_new['right'] >= 5, f"上/右缘异常 {margins_new}"
# 修复不改变绘图语义：墨迹面积量级应接近（同要素重绘，窗口变大内容略缩）
r['ink_px_ratio'] = round(nb[4] / ob[4], 4)
log(f"墨迹像素比 新/旧 = {r['ink_px_ratio']}")

import json, hashlib
r['md5_new'] = hashlib.md5(open(OUT_PNG, 'rb').read()).hexdigest()
r['md5_old_一期交付'] = hashlib.md5(open(OLD_PNG, 'rb').read()).hexdigest()
r['md5_③二期嵌入'] = 'bfb3ca951889622dac65b4cd83c298cc'
json.dump(r, open(os.path.join(HERE, '重出自验.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
log('SUMMARY_REGEN OK md5_new=' + r['md5_new'])
