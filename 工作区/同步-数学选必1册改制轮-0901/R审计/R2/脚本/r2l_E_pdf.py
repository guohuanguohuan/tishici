# -*- coding: utf-8 -*-
"""R2——E件PDF双证：导出E、定位节标题所在页（2.3.1/2.3.2/2.3.3）、页脚X渲染值抽验。"""
import os, shutil, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

D = r'C:\提示词\高中数学\高中数学同步'
W = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\PDF'
shutil.copy2(os.path.join(D, '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
             os.path.join(W, 'E_local.docx'))
from win32com.client import DispatchEx
word = DispatchEx('Word.Application'); word.Visible = False; word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(os.path.join(W, 'E_local.docx'), ReadOnly=True)
    doc.ExportAsFixedFormat(os.path.join(W, 'E.pdf'), 17)
    print('E COM页数=', doc.ComputeStatistics(2))
    doc.Close(False)
finally:
    word.Quit()

import fitz
pdf = fitz.open(os.path.join(W, 'E.pdf'))
targets = ['2.3.1 圆的标准方程', '2.3.2 圆的一般方程', '2.3.3 直线与圆的位置关系', '2.2.4 点到直线的距离']
for t in targets:
    hits = []
    for pno in range(pdf.page_count):
        txt = pdf[pno].get_text()
        if t in txt.replace(' ', '').replace('\u3000', ''):
            hits.append(pno + 1)
    print('节标题[%s] 出现页(页内): %s' % (t, hits))
# 页脚X渲染抽验：p1/p10/p32/p53
for pno1 in (1, 10, 32, 53):
    txt = pdf[pno1 - 1].get_text()
    m = re.findall(r'第(\d+)页', txt)
    m2 = re.findall(r'（共(\d+)页）', txt)
    print('E p%d: 第X页渲染=%s 共N页=%s' % (pno1, m, m2))
pdf.close()
print('DONE')
