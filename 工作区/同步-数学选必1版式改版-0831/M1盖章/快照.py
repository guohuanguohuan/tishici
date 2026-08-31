# -*- coding: utf-8 -*-
"""M1盖章·快照：全十件zip成员级sha256（幂等二跑前后对比用）。用法：python 快照.py <out.json>"""
import hashlib
import json
import os
import sys
import zipfile

PROD = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
FILES = [
    '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
]
snap = {}
for name in FILES:
    p = os.path.join(PROD, name)
    z = zipfile.ZipFile(p)
    snap[name] = {n: hashlib.sha256(z.read(n)).hexdigest()[:16] for n in z.namelist()}
    z.close()
json.dump(snap, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('snapshot -> %s (files=%d)' % (sys.argv[1], len(snap)))
