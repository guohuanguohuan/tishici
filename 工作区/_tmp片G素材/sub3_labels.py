# 片G · sub3 标签墨迹盒逐字对比（源 vs 重绘，1x 同尺）：输出 bbox 中心 Δ（重绘−源，源 px）与尺寸差
# 用法：python sub3_labels.py
import numpy as np
from PIL import Image

src = np.array(Image.open("sub3_source.png").convert("L")).astype(float) < 128
red = np.array(Image.open("sub3_render1x.png").convert("L")).astype(float) < 128
MM = 0.06107955

W = {
    "①a(上)": (110, 55, 150, 96), "①a(内)": (168, 155, 205, 198), "①c": (132, 245, 168, 292),
    "①b": (213, 246, 250, 295), "①α": (340, 160, 375, 192),
    "②a(上)": (598, 52, 640, 92), "②a(内)": (655, 153, 692, 198), "②c": (618, 244, 652, 292),
    "②l": (782, 212, 805, 254), "②α": (836, 150, 870, 182),
    "③A": (1080, 85, 1118, 120), "③B": (1267, 8, 1302, 48), "③A'": (1082, 193, 1132, 235),
    "③B'": (1242, 194, 1292, 236), "③a(上)": (1165, 25, 1200, 68), "③a(中)": (1192, 147, 1226, 187),
    "③c": (1183, 192, 1216, 236), "③β": (1315, 145, 1352, 196),
}
print(f"{'标签':<9}{'源盒 w×h':>12}{'绘盒 w×h':>12}{'Δ尺寸':>12}{'Δ中心(px)':>16}{'Δ中心(mm)':>18}")
for k, (x0, y0, x1, y1) in W.items():
    out = []
    for img in (src, red):
        sub = img[y0:y1, x0:x1]
        ys, xs = np.nonzero(sub)
        if len(xs) == 0:
            out.append(None); continue
        out.append((xs.min() + x0, xs.max() + x0, ys.min() + y0, ys.max() + y0))
    a, b = out
    if not a or not b:
        print(f"{k:<9} 空"); continue
    wa, ha = a[1] - a[0] + 1, a[3] - a[2] + 1
    wb, hb = b[1] - b[0] + 1, b[3] - b[2] + 1
    dx, dy = ((b[0] + b[1]) - (a[0] + a[1])) / 2, ((b[2] + b[3]) - (a[2] + a[3])) / 2
    print(f"{k:<9}{f'{wa}×{ha}':>12}{f'{wb}×{hb}':>12}{f'{wb-wa:+3d}×{hb-ha:+3d}':>12}"
          f"{f'({dx:+.2f},{dy:+.2f})':>16}{f'({dx*MM:+.3f},{dy*MM:+.3f})':>18}")
