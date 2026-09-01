# -*- coding: utf-8 -*-
"""SW任务3勘察：B/E导航表题号区间列与表头run结构（只读，工作副本）。"""
import io
import os
import sys
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from lxml import etree

WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def W(t):
    return '{%s}%s' % (WNS, t)


WORK = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\S盖章\SW工作'
FILES = {
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
}

for code, fname in FILES.items():
    path = os.path.join(WORK, fname)
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read('word/document.xml'))
    body = root.find(W('body'))
    tbl = next(t for t in body if t.tag == W('tbl'))
    rows = tbl.findall(W('tr'))
    print('==== %s 导航表 %d行 × %d列 ====' % (code, len(rows), len(rows[0].findall(W('tc')))))
    for ri, tr in enumerate(rows):
        tcs = tr.findall(W('tc'))
        tc = tcs[1]  # 题号区间列
        for pi, p in enumerate(tc.findall(W('p'))):
            runs = p.findall(W('r'))
            rt = ['%r' % (''.join(t.text or '' for t in r.findall(W('t')))) for r in runs]
            # run rPr签名（字体/字号/底纹）
            sig = []
            for r in runs:
                rPr = r.find(W('rPr'))
                keys = []
                if rPr is not None:
                    for e in rPr:
                        tag = e.tag.split('}')[1]
                        v = e.get(W('val')) or e.get(W('fill')) or ''
                        keys.append('%s=%s' % (tag, v))
                sig.append('|'.join(keys) or '(无rPr)')
            print('行%d列2 段%d: %d runs=%s rPr=%s' % (ri + 1, pi, len(runs), rt, sig))
