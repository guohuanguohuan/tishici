# -*- coding: utf-8 -*-
"""FX5-G: unpack docx to tmp dir for analysis"""
import zipfile, os, shutil

SRC = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'
TMP = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G'

if os.path.exists(os.path.join(TMP, 'word')):
    shutil.rmtree(os.path.join(TMP, 'word'))
os.makedirs(TMP, exist_ok=True)
with zipfile.ZipFile(SRC) as z:
    names = z.namelist()
    z.extractall(TMP)
print('entries:', len(names))
for n in sorted(names):
    if 'word/' in n and ('document' in n or 'header' in n or 'footer' in n or 'settings' in n or 'styles' in n or n=='word/_rels/document.xml.rels'):
        print(' ', n, os.path.getsize(os.path.join(TMP, n)))
