# 片G · sub3 对照构建
#  ① sub3_render1x.png ：重绘 PDF 按「源同尺」栅格（86.0mm → 1408px），供逐要素量测（无重采样误差）
#  ② sub3_render600.png：重绘 PDF @600dpi 等效（86.0mm → 2032px），供交付对照
#  ③ sub3_叠加-600dpi.png：红=源、蓝=重绘、重合=黑
# 用法：python sub3_build.py
import numpy as np
import fitz
from PIL import Image

TARGET_1X = 1408           # 源位图原生宽（86.0mm）
TARGET_600 = 2032          # 86.0mm @600dpi = 2031.5 → 2032

page = fitz.open("sub3_投影三联-standalone.pdf")[0]

for target, out in ((TARGET_1X, "sub3_render1x.png"), (TARGET_600, "sub3_render600.png")):
    z = target / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L")
    if img.width != target:                       # 裁/补 1px 以内，不做缩放
        w = min(img.width, target)
        img = img.crop((0, 0, w, img.height))
    img.save(out)
    print(f"{out}: {img.size}  (原始 {pix.width}x{pix.height}, z={z:.4f} px/pt)")

src = Image.open("sub3_source.png").convert("L")
src600 = src.resize((TARGET_600, round(TARGET_600 * src.height / src.width)), Image.LANCZOS)
src600.save("sub3_source600.png")
red600 = Image.open("sub3_render600.png").convert("L")
h = min(src600.height, red600.height)
red600 = red600.crop((0, 0, TARGET_600, h)); src600 = src600.crop((0, 0, TARGET_600, h))
R = np.array(src600).astype(float) / 255.0
B = np.array(red600).astype(float) / 255.0
Image.fromarray((np.dstack([R, np.minimum(R, B), B]) * 255).astype(np.uint8)).save("sub3_叠加-600dpi.png")
print("sub3_叠加-600dpi.png:", src600.size)
