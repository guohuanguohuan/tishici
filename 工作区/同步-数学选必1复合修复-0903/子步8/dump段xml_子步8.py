# -*- coding: utf-8 -*-
"""dump 使用说明.docx 段4/5/13/14 原始XML，供T2精确手术。"""
import zipfile, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

P = r'C:\提示词\高中数学\高中数学同步\人教B版选必1·使用说明.docx'
with zipfile.ZipFile(P) as z:
    doc = z.read('word/document.xml').decode('utf-8')
rows = re.findall(r'<w:p[ >].*?</w:p>', doc, re.S)
for i in (4, 5, 13, 14):
    print('========== 段%d ==========' % i)
    print(rows[i])
