# -*- coding: utf-8 -*-
import sys, zipfile, os
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(W,t)
D=r'C:\提示词\高中数学\高中数学同步'
for code,fn in [('I1','人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
                ('I2','人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx')]:
    z=zipfile.ZipFile(os.path.join(D,fn))
    doc=etree.fromstring(z.read('word/document.xml'))
    mr_blue=mr_grey=mr_nocolor=run_blue_grey=0
    for mr in doc.iter('{%s}r'%M):
        rpr=mr.find(q('rPr'))
        col=rpr.find(q('color')) if rpr is not None else None
        shd=rpr.find(q('shd')) if rpr is not None else None
        c=(col.get(q('val')) if col is not None else None)
        has_grey=shd is not None and shd.get(q('fill'))=='C9C9C9'
        if has_grey: mr_grey+=1
        elif c=='1F4E79': mr_blue+=1
        else: mr_nocolor+=1
    for r in doc.iter(q('r')):
        rpr=r.find(q('rPr'))
        if rpr is None: continue
        col=rpr.find(q('color')); shd=rpr.find(q('shd'))
        if shd is not None and shd.get(q('fill'))=='C9C9C9' and col is not None and col.get(q('val'))=='1F4E79':
            run_blue_grey+=1
    print(code, 'm:r深蓝(公式型需背)=',mr_blue,' m:r灰挂=',mr_grey,' m:r无色=',mr_nocolor,' 灰底深蓝文字run(文字型需背/答案)=',run_blue_grey)
