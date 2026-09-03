# -*- coding: utf-8 -*-
"""FX1-B COM页数实测·副本版（原位路径COM Open挂起，按A1先例改md5一致本地副本；
自建实例 ReadOnly 用完Quit，副本与锁文件用完即删）"""
import os, hashlib, datetime
import pythoncom
from win32com.client import DispatchEx

SRC = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
CPY = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX1_B\B_COM测页副本.docx'

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

import shutil
shutil.copyfile(SRC, CPY)
m1, m2 = md5(SRC), md5(CPY)
assert m1 == m2, 'md5不一致'
print(f'副本md5一致: {m1}')

t0 = datetime.datetime.now()
pythoncom.CoInitialize()
word = None
try:
    word = DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(CPY, ReadOnly=True, AddToRecentFiles=False)
    pages = doc.ComputeStatistics(2)  # wdStatisticPages
    doc.Close(False)
    print(f'COM开卷(md5一致副本) 实测页数={pages}')
    print(f'耗时={(datetime.datetime.now() - t0).total_seconds():.1f}s')
finally:
    if word is not None:
        word.Quit()
    pythoncom.CoUninitialize()
    print('实例已Quit')
    for p in (CPY, os.path.join(os.path.dirname(CPY), '~$B_COM测页副本.docx')):
        if os.path.exists(p):
            os.remove(p)
            print('已删:', os.path.basename(p))
