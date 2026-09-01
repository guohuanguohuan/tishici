# -*- coding: utf-8 -*-
"""S盖章·PDF抽验：B卷(start=1,N=154)与H卷(start=151,N=221)各导出PDF（ExportAsFixedFormat），
抽3页断言「页脚第X页=X域渲染值=start+页序」「（共N页）值」＋页眉页脚同串节名段在位。"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client
import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(os.path.dirname(HERE), 'PDF')
os.makedirs(PDFDIR, exist_ok=True)
OUT = r'C:\提示词\高中数学\高中数学同步'
SPEC = [
    ('B', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 1, 154),
    ('H', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 151, 221),
]

word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
pdfs = []
try:
    for tag, fn, start, n in SPEC:
        src = os.path.join(OUT, fn)
        pdf = os.path.join(PDFDIR, tag + '.pdf')
        doc = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
        try:
            doc.ExportAsFixedFormat(pdf, 17)  # wdExportFormatPDF
        finally:
            doc.Close(False)
        pdfs.append(pdf)
        print('%s 导出 -> %s（%d bytes）' % (tag, pdf, os.path.getsize(pdf)))
finally:
    word.Quit()

fail = []
for (tag, fn, start, n), pdf in zip(SPEC, pdfs):
    d = fitz.open(pdf)
    print('%s PDF页数=%d' % (tag, d.page_count))
    for pno in (0, 1, 2):  # 抽第1/2/3页
        page = d[pno]
        expect_x = start + pno
        # PyMuPDF 数字与汉字间插空格（经验定论）——正则容忍空白；页眉顶部/页脚底部分区提取、两处同串各自断言
        results = {}
        for region, clip in (('页眉', fitz.Rect(0, 0, 595, 60)), ('页脚', fitz.Rect(0, 770, 595, 842))):
            txt = page.get_text(clip=clip)
            m = re.search(r'（共\s*(\d+)\s*页）', txt)
            mx = re.search(r'第\s*(\d+)\s*页', txt)
            results[region] = (m, mx, txt)
        ok, desc = True, []
        for region, (m, mx, txt) in results.items():
            v_ok = bool(m) and int(m.group(1)) == n
            x_ok = bool(mx) and int(mx.group(1)) == expect_x
            str_ok = ('讲练' in txt) and ('人教B' in txt.replace(' ', '')) and 'B' in txt
            ok = ok and v_ok and x_ok and str_ok
            desc.append('%s%s' % (region, '✓' if v_ok and x_ok and str_ok else '✗'))
            if not (v_ok and x_ok and str_ok):
                fail.append('%s p%d %s: %r' % (tag, pno + 1, region, txt[:120]))
        print('%s p%d: 期望 第%d页/（共%d页） | %s | 同串两区在位 %s' %
              (tag, pno + 1, expect_x, n, '＋'.join(desc), '✓' if ok else '✗'))
        if not ok:
            fail.append('%s p%d 断言未全过' % (tag, pno + 1))
    d.close()
print('PDF抽验：%s' % ('全绿（6/6页断言过）' if not fail else '失败项=%d' % len(fail)))
sys.exit(0 if not fail else 1)
