# -*- coding: utf-8 -*-
"""最终比对出图：①600dpi 同尺并排对照 ②604dpi 红蓝叠加＋对齐后逐要素重合度
对齐口径：2x 帧全局搜优（1px@2x 步进＝0.5px@1x），目标＝墨迹阈值 IoU 最大。
本图线网与 6 字母的最优位移已完全一致（同为 -1,+1 @2x）→ 无逐要素残余错位。"""
import fitz, numpy as np, cv2

SRC = cv2.imdecode(np.fromfile("source-image4.png", dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
W2, H2 = 1576, 848

# ---- ① 600dpi 同尺并排对照（由 LaTeX 对照页栅格化，两图均 66.3mm 宽）----
d = fitz.open("片G-image4-对照-604dpi.pdf"); p = d[0]; z = 600/72.0
pix = p.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csRGB)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
cv2.imencode('.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))[1].tofile("片G-image4-对照-604dpi.png")
print("① 对照图：%dx%d px；页面 74.0mm@600dpi；单图宽 66.3mm＝%dpx（=600.0dpi 等效）"
      % (pix.width, pix.height, round(66.3/25.4*600)))

# ---- 重绘 2x 渲染 ----
d = fitz.open("片G-image4-二面角-standalone.pdf"); p = d[0]
zz = W2/p.rect.width
pix = p.get_pixmap(matrix=fitz.Matrix(zz, zz), colorspace=fitz.csGRAY)
mine = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
src2 = cv2.resize(SRC, (W2, H2), interpolation=cv2.INTER_NEAREST)
ms = src2 < 128

best = None
for ddx in np.arange(-6, 6.5, 1.0):
    for ddy in np.arange(-6, 6.5, 1.0):
        mm_ = cv2.warpAffine(mine, np.float32([[1,0,ddx],[0,1,ddy]]), (W2,H2),
                             flags=cv2.INTER_LINEAR, borderValue=255) < 128
        iou = (ms & mm_).sum()/max(1, (ms | mm_).sum())
        if best is None or iou > best[0]: best = (iou, ddx, ddy)
iou, ddx, ddy = best
print("② 全局最优对齐 @2x: (%.0f,%.0f) px ＝ (%.2f,%.2f) px@1x；墨迹 IoU=%.4f（＝源 %.2f%% 被覆盖）"
      % (ddx, ddy, ddx/2, ddy/2, iou, (ms & (cv2.warpAffine(mine, np.float32([[1,0,ddx],[0,1,ddy]]),(W2,H2),flags=cv2.INTER_LINEAR,borderValue=255)<128)).sum()/ms.sum()*100))
mm_ = cv2.warpAffine(mine, np.float32([[1,0,ddx],[0,1,ddy]]), (W2,H2), flags=cv2.INTER_LINEAR, borderValue=255) < 128
out = np.full((H2, W2, 3), 255, np.uint8)
out[ms & ~mm_] = (40, 40, 220)    # 仅源 → 红
out[mm_ & ~ms] = (220, 40, 40)    # 仅重绘 → 蓝
out[ms & mm_] = (25, 25, 25)      # 重合 → 黑
cv2.imencode('.png', out)[1].tofile("片G-image4-叠加-604dpi.png")
REG = {"线网":(40,55,720,370), "A":(255,11,326,76), "B":(692,47,751,111), "C":(651,339,713,410),
       "D":(258,350,325,414), "E":(2,175,64,239), "F":(367,207,429,271)}
print("   逐要素（2x 帧，对齐后）：")
worst = 1.0
for k,(x0,y0,x1,y1) in REG.items():
    a = ms[y0*2:y1*2, x0*2:x1*2]; b = mm_[y0*2:y1*2, x0*2:x1*2]
    v = (a&b).sum()/max(1,(a|b).sum()); worst = min(worst, v)
    print("     %-4s IoU=%.4f  源ink=%-6d 重绘ink=%-6d 差=%+d px" % (k, v, a.sum(), b.sum(), b.sum()-a.sum()))
print("   最差要素 IoU=%.4f" % worst)
