# -*- coding: utf-8 -*-
"""RF2补导：单件COM导出（默认 H,fix2）＋COM实测页数。用法: python rf2b_export_one.py [code] [tag]"""
import os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
import win32com.client as wc

R = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复'
code = sys.argv[1] if len(sys.argv) > 1 else 'H'
tag = sys.argv[2] if len(sys.argv) > 2 else 'fix2'
src = os.path.join(R, '基线', code + '.docx')
local = os.path.join(R, 'PDF', '%s_local.docx' % code)
pdf = os.path.join(R, 'PDF', '%s_%s.pdf' % (code, tag))
shutil.copy2(src, local)
word = wc.DispatchEx('Word.Application')
word.Visible = False; word.DisplayAlerts = 0
print('Word COM version:', word.Version, 'Build:', word.Build, flush=True)
try:
    doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
    try:
        n = doc.ComputeStatistics(2)
        doc.ExportAsFixedFormat(pdf, 17, False, 0, 0)
        print('%s COM页数=%d PDF=%dB' % (code, n, os.path.getsize(pdf)), flush=True)
    finally:
        doc.Close(False)
finally:
    word.Quit()
os.remove(local)
print('DONE')
