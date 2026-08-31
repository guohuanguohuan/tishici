# -*- coding: utf-8 -*-
"""产出原件未触碰核对：6原件sha256[:16]与T1开跑前预检值比对。"""
import hashlib, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
OUT = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
orig = {
 '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx': '877360c45f0a3176',
 '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx': 'c2601c1d7b90adf6',
 '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx': 'afb7f2e3b9d3ec87',
 '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx': 'deed4eedeaad2da9',
 '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx': 'd3c5498611565581',
 '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx': 'f1e0d7d7c6368e38',
}
allok = True
for name, want in orig.items():
    h = hashlib.sha256(open(os.path.join(OUT, name), 'rb').read()).hexdigest()[:16]
    ok = (h == want)
    allok &= ok
    print('%s 产出原件 %s sha256[:16]=%s' % ('OK未动' if ok else 'XX变动!', name[:30], h))
assert allok
print('产出文件夹6原件全部与T1开跑前逐字节一致（未触碰）')
