# -*- coding: utf-8 -*-
"""建十件工作区镜像（同文件名、字节级sha核验）——B原件路径COM开卷僵化（6次重试挂死）的绕行载体。
镜像仅用于COM测量与盖章施工；盖章完成后按sha逐件写回产出文件夹原件。"""
import os, sys, io, shutil, hashlib, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

HERE = os.path.dirname(os.path.abspath(__file__))
MIR = os.path.join(HERE, 'mirror')
BASE = r'C:\提示词\高中数学\高中数学同步'
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

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

os.makedirs(MIR, exist_ok=True)
tab = {}
for fn in FILES:
    src, dst = os.path.join(BASE, fn), os.path.join(MIR, fn)
    shutil.copy2(src, dst)
    a, b = sha(src), sha(dst)
    assert a == b, 'sha不一致: %s' % fn
    tab[fn] = a
    print('%s  sha=%s' % (a[:12], fn[:30]))
json.dump(tab, open(os.path.join(HERE, 'mirror_sha.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('镜像建成：10/10 sha一致 → mirror_sha.json')
