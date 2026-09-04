# -*- coding: utf-8 -*-
"""dump 使用说明.docx 段落结构（含run级底纹/加粗/字号），供T2图例区改造对照。"""
import zipfile, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

P = r'C:\提示词\高中数学\高中数学同步\人教B版选必1·使用说明.docx'
with zipfile.ZipFile(P) as z:
    doc = z.read('word/document.xml').decode('utf-8')
rows = re.findall(r'<w:p[ >].*?</w:p>', doc, re.S)
print('总段数=%d' % len(rows))
for i, r in enumerate(rows):
    text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', r))
    shds = re.findall(r'<w:shd [^>]*fill="([0-9A-Fa-f]{6})"', r)
    bold = len(re.findall(r'<w:b/>', r))
    szs = set(re.findall(r'<w:sz w:val="(\d+)"', r))
    ind = re.search(r'<w:ind ([^/]*)/>', r)
    pshd = re.search(r'<w:pPr>.*?<w:shd [^>]*fill="([0-9A-Fa-f]{6})"', r, re.S)
    print('---[%02d] sz=%s b=%d shd=%s pshd=%s %s' % (
        i, '/'.join(sorted(szs)), bold, sorted(set(shds)),
        pshd.group(1) if pshd else '-', (ind.group(1) if ind else '')))
    print('     %s' % (text[:110] if text else '（空）'))
