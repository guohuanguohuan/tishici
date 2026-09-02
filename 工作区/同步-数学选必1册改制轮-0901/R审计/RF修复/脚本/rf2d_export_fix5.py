# -*- coding: utf-8 -*-
"""RF2 fix5导出：X1/B/C三件 fix5 PDF＋COM页数。"""
import os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
import win32com.client as wc
R = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复'
word = wc.DispatchEx('Word.Application')
word.Visible = False; word.DisplayAlerts = 0
print('Word COM:', word.Version, word.Build, flush=True)
try:
    for code in ['X1', 'B', 'C']:
        src = os.path.join(R, '基线', code + '.docx')
        local = os.path.join(R, 'PDF', code + '_local.docx')
        pdf = os.path.join(R, 'PDF', '%s_fix5.pdf' % code)
        shutil.copy2(src, local)
        doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
        try:
            n = doc.ComputeStatistics(2)
            doc.ExportAsFixedFormat(pdf, 17, False, 0, 0)
            print('%s COM页数=%d PDF=%dB' % (code, n, os.path.getsize(pdf)), flush=True)
        finally:
            doc.Close(False)
        os.remove(local)
finally:
    word.Quit()
print('DONE')
