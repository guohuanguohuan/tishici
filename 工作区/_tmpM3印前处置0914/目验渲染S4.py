# -*- coding: utf-8 -*-
"""S4 印前处置·目验渲染：涉图 in-place main-true.pdf 含图页 → 目验S4/*.png"""
import os, pymupdf

CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
OUT = r'C:/提示词/工作区/_tmpM3印前处置0914/目验S4'
os.makedirs(OUT, exist_ok=True)

PIECES = [('练习件', ['课时02-倾斜角与斜率', '课时12-2.5.2椭圆的几何性质', '课时13-2.6.1双曲线的标准方程',
                      '课时15-2.7.1抛物线方程', '课时18-2.8②压轴综合二', '课时19-章末总结与复习']),
          ('导学件', ['课时02-倾斜角与斜率', '课时12-2.5.2椭圆的几何性质', '课时13-2.6.1双曲线的标准方程',
                      '课时15-2.7.1抛物线方程', '课时18-2.8②压轴综合二', '课时19-章末总结与复习'])]

n = 0
for tree, dirs in PIECES:
    for d in dirs:
        pdir = os.path.join(CJ, tree, d)
        doc = pymupdf.open(os.path.join(pdir, 'main-true.pdf'))
        tag = ('练' if tree == '练习件' else '导') + d.split('-')[0].replace('课时', '')
        for i, page in enumerate(doc):
            if page.get_images(full=True):
                pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
                fn = os.path.join(OUT, '%s-true-p%d.png' % (tag, i + 1))
                pix.save(fn)
                print(fn, '%dx%d' % (pix.width, pix.height))
                n += 1
        doc.close()
print('rendered', n)
