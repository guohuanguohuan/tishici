# -*- coding: utf-8 -*-
"""W-G 图内字母视觉高测量v2：连通域组件法（小组件＝字母/标注）
逻辑：暗像素8连通域→按组件高分布取「字母族」（高3~60px、宽2~60px、非细长线）中位高"""
import zipfile, io, json
import numpy as np
from PIL import Image

CPY = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G工作副本.docx"
TARGETS = [
    ('image26.png', 17.80, 13.30), ('image30.png', 18.00, 17.01),
    ('image31.png', 5.90, 12.01), ('image159.png', 7.70, 9.26),
    ('image34.png', 9.70, 9.24), ('image27.png', 7.30, 5.00),
    ('image300.png', 6.60, 6.79), ('image157.png', 8.20, 8.58),
]

def components(dark):
    """简易两遍标记法8连通组件"""
    h, w = dark.shape
    lab = np.zeros((h, w), dtype=np.int32)
    cur = 0
    from collections import deque
    for y in range(h):
        for x in range(w):
            if dark[y, x] and lab[y, x] == 0:
                cur += 1
                qd = deque([(y, x)]); lab[y, x] = cur
                y0 = y1 = y; x0 = x1 = x; n = 0
                while qd:
                    cy, cx = qd.popleft(); n += 1
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and dark[ny, nx] and lab[ny, nx] == 0:
                                lab[ny, nx] = cur; qd.append((ny, nx))
                                y0 = min(y0, ny); y1 = max(y1, ny)
                                x0 = min(x0, nx); x1 = max(x1, nx)
                yield cur, (y0, y1, x0, x1, n)
    return

z = zipfile.ZipFile(CPY)
out = {}
for name, wcm, hcm in TARGETS:
    img = Image.open(io.BytesIO(z.read('word/media/' + name))).convert('L')
    # 降采样防大图慢：>1200px按比例缩
    w0, h0 = img.size
    scale = 1.0
    if max(w0, h0) > 1200:
        scale = 1200.0 / max(w0, h0)
        img = img.resize((int(w0 * scale), int(h0 * scale)))
    a = np.asarray(img)
    dark = a < 120
    hs = []
    for _, (y0, y1, x0, x1, n) in components(dark):
        ch = y1 - y0 + 1; cw = x1 - x0 + 1
        # 字母族：高度4~60px、宽3~60px、实心率>0.15、非细线（高宽比0.3~4）
        if 4 <= ch <= 60 and 3 <= cw <= 60 and n > 0.15 * ch * cw and 0.25 <= ch / cw <= 4.5:
            hs.append(ch)
    if not hs:
        out[name] = {'组件数0': True, 'scale': scale}
        continue
    med = float(np.median(hs))
    disp_h_px = (img.size[1])
    pt_per_px = hcm * 28.35 / disp_h_px
    out[name] = {
        '图像px': '%dx%d' % img.size, '降采样': round(1 / scale, 2),
        '字母族组件数': len(hs), '中位组件高px': round(med / scale, 1),
        '字母视觉高pt@现显': round(med * pt_per_px, 1),
        '若缩至高9cm→pt': round(med * (9.0 * 28.35 / disp_h_px), 1) if hcm > 9 else '—',
    }
z.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
