# -*- coding: utf-8 -*-
"""子步3 收尾写回：定稿六件 → 产出文件夹覆盖（写回前后 sha256 核验）"""
import sys, io, shutil, hashlib, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\高中数学\高中数学同步'
SUB3 = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步3'
NAMES = ['人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
         '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
         '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
         '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
         '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
         '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx']
out = {}
for fn in NAMES:
    src = os.path.join(SUB3, '定稿', fn)
    dst = os.path.join(BASE, fn)
    h_src = hashlib.sha256(open(src, 'rb').read()).hexdigest()
    assert os.path.exists(dst), dst
    shutil.copy2(src, dst)
    h_dst = hashlib.sha256(open(dst, 'rb').read()).hexdigest()
    assert h_src == h_dst, fn
    out[fn] = {'sha256前12': h_src[:12], 'bytes': os.path.getsize(dst)}
    print('写回✓', fn[:30], h_src[:12], os.path.getsize(dst))
json.dump(out, open(os.path.join(SUB3, '写回哈希.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('六件写回产出文件夹完成')
