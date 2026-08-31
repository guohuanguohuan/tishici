# -*- coding: utf-8 -*-
"""W-G 图内字母视觉高测量：>9cm高图5张＋抽样3张普通图
方法：暗像素行带（连通暗行段）中位高度→按显示高换算pt（1cm=28.35pt）"""
import zipfile, io, json
import numpy as np
from PIL import Image

CPY = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G工作副本.docx"
# (媒体名, 显示宽cm, 显示高cm)
TARGETS = [
    ('image26.png', 17.80, 13.30),
    ('image30.png', 18.00, 17.01),
    ('image31.png', 5.90, 12.01),
    ('image159.png', 7.70, 9.26),
    ('image34.png', 9.70, 9.24),
    ('image27.png', 7.30, 5.00),   # 对照普通图
    ('image300.png', 6.60, 6.79),  # 对照普通图
    ('image157.png', 8.20, 8.58),  # 对照普通图
]

z = zipfile.ZipFile(CPY)
out = {}
for name, wcm, hcm in TARGETS:
    img = Image.open(io.BytesIO(z.read('word/media/' + name))).convert('L')
    a = np.asarray(img)
    dark = a < 120
    rows = dark.sum(axis=1)
    # 连通行带（≥2暗像素的行连成带）
    bands = []
    s = None
    for i, v in enumerate(rows):
        if v >= 2 and s is None: s = i
        elif v < 2 and s is not None:
            bands.append(i - s); s = None
    if s is not None: bands.append(len(rows) - s)
    # 文字行带：高度3~80px（排除细线/大图形轮廓）
    tb = [b for b in bands if 4 <= b <= 80]
    if not tb:
        out[name] = {'行带数': len(bands), '中位带px': None}
        continue
    med = float(np.median(tb))
    pt_per_px = hcm * 28.35 / a.shape[0]
    out[name] = {
        '图像px': '%dx%d' % (a.shape[1], a.shape[0]),
        '显示cm': '%.2fx%.2f' % (wcm, hcm),
        '文字行带数': len(tb), '中位带高px': round(med, 1),
        '字母视觉高pt@现显': round(med * pt_per_px, 1),
        '字母视觉高pt@缩至9cm': round(med * (9.0 * 28.35 / a.shape[0]), 1) if hcm > 9 else None,
    }
z.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
