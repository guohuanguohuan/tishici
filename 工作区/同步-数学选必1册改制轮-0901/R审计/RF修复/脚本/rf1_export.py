# -*- coding: utf-8 -*-
"""RF修复轮 PDF导出（基线/修复后复用）。8件全件导出到 RF修复\PDF\<code>.pdf；基线导为 <code>_base.pdf。
COM版本预检＋开卷冒烟；自建实例用毕Quit。"""
import os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
import win32com.client as wc

BASE = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\基线'
PDFDIR = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\PDF'
CODES = ['X1','B','C','I2','E','F','G','H']

word = wc.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
print('Word COM version:', word.Version, 'Build:', word.Build, flush=True)
try:
    for code in CODES:
        src = os.path.join(BASE, code + '.docx')
        local = os.path.join(PDFDIR, code + '_local.docx')
        shutil.copy2(src, local)
        pdf = os.path.join(PDFDIR, '%s_%s.pdf' % (code, sys.argv[1] if len(sys.argv) > 1 else 'base'))
        doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
        try:
            n = doc.ComputeStatistics(2)  # wdStatisticPages
            doc.ExportAsFixedFormat(pdf, 17, False, 0, 0)
            print('%s COM页数=%d PDF=%dB' % (code, n, os.path.getsize(pdf)), flush=True)
        finally:
            doc.Close(False)
        os.remove(local)
finally:
    word.Quit()
print('ALL DONE')
