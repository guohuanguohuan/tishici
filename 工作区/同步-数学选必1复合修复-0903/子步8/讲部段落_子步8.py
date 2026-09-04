# -*- coding: utf-8 -*-
"""抽取B讲部条目1.1.1-1完整段群（条目号段＋子层段）run级底纹分布。"""
import zipfile, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
BASE = r'C:\提示词\高中数学\高中数学同步'
with zipfile.ZipFile(os.path.join(BASE, '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx')) as z:
    doc = z.read('word/document.xml').decode('utf-8')
rows = re.findall(r'<w:p[ >].*?</w:p>', doc, re.S)
start = None
for i, r in enumerate(rows):
    text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', r))
    if text.startswith('1.1.1-1．'):
        start = i
        break
assert start is not None
for r in rows[start:start + 6]:
    print('----')
    for rm in re.finditer(r'<w:r>(<w:rPr>.*?</w:rPr>)<w:t[^>]*>([^<]*)</w:t></w:r>', r, re.S):
        rpr, text = rm.group(1), rm.group(2)
        shd = re.search(r'fill="([0-9A-Fa-f]{6})"', rpr)
        print('  [%s] %s' % (shd.group(1) if shd else '·····', text[:70]))
