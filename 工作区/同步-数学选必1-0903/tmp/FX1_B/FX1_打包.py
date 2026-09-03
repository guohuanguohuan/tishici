# -*- coding: utf-8 -*-
"""FX1-B 重打包与完整性校验"""
import zipfile, os, hashlib
from lxml import etree

SRC_DIR = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX1_B\unzipped'
OUT = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX1_B\B_修复后.docx'
ORIG = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'

files = []
for root, dirs, fns in os.walk(SRC_DIR):
    for fn in fns:
        full = os.path.join(root, fn)
        rel = os.path.relpath(full, SRC_DIR).replace(os.sep, '/')
        files.append(rel)
files.sort()
files.remove('[Content_Types].xml')
files.insert(0, '[Content_Types].xml')

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for rel in files:
        z.write(os.path.join(SRC_DIR, rel), rel)
print('打包完成', len(files), '条目')

with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    doc = z.read('word/document.xml')
root = etree.fromstring(doc)
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
paras = root.findall(f'.//{{{W}}}body/{{{W}}}p')
print('重解包OK，段数=', len(paras))
print('标题=', paras[0].find(f'.//{{{W}}}t').text)

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

print('修复件md5=', md5(OUT))
print('原件md5  =', md5(ORIG))
# 媒体文件数目一致性（图像守恒）
with zipfile.ZipFile(OUT) as z:
    nm_new = [n for n in z.namelist() if n.startswith('word/media/')]
with zipfile.ZipFile(ORIG) as z:
    nm_old = [n for n in z.namelist() if n.startswith('word/media/')]
print('媒体数 新/旧 =', len(nm_new), '/', len(nm_old), '差集=', set(nm_old) ^ set(nm_new))
