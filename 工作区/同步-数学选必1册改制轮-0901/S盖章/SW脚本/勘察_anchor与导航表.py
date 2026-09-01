# -*- coding: utf-8 -*-
"""
SW勘察（只读）：①十件全部XML部件wp:anchor的allowOverlap分布计数；
②B/E两件章首导航表列结构dump（表格行×列文本矩阵）。
用法: python 勘察_anchor与导航表.py
"""
import io
import os
import re
import sys
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from lxml import etree

WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WPNS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
MNS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'


def W(t):
    return '{%s}%s' % (WNS, t)


SRC = r'C:\提示词\高中数学\高中数学同步'
FILES = {
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}


def para_text(p):
    return ''.join(t.text or '' for t in p.iter()
                   if t.tag in (W('t'), '{%s}t' % MNS))


def survey_anchor(code, fname):
    path = os.path.join(SRC, fname)
    stat = {}
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            if not info.filename.endswith('.xml'):
                continue
            data = z.read(info.filename)
            if b'wp:anchor' not in data and b'allowOverlap' not in data:
                continue
            try:
                root = etree.fromstring(data)
            except etree.XMLSyntaxError:
                continue
            anchors = [a for a in root.iter('{%s}anchor' % WPNS)]
            if not anchors:
                continue
            c1 = sum(1 for a in anchors if a.get('allowOverlap') == '1')
            c0 = sum(1 for a in anchors if a.get('allowOverlap') == '0')
            cother = len(anchors) - c1 - c0
            stat[info.filename] = (len(anchors), c0, c1, cother)
    tot = sum(v[0] for v in stat.values())
    c0 = sum(v[1] for v in stat.values())
    c1 = sum(v[2] for v in stat.values())
    co = sum(v[3] for v in stat.values())
    print('[%s] anchor总计=%d 已0=%d 需改1=%d 缺省/他值=%d | 明细: %s'
          % (code, tot, c0, c1, co,
             '; '.join('%s: n=%d,0=%d,1=%d,other=%d' % (k, *v) for k, v in stat.items())))
    return tot, c0, c1, co


def dump_nav(code, fname):
    """dump章首导航表：文内开头标题后的第一个w:tbl（行×列文本矩阵）。"""
    path = os.path.join(SRC, fname)
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read('word/document.xml'))
    body = root.find(W('body'))
    tbls = [t for t in body if t.tag == W('tbl')]
    print('\n=== %s 导航表勘察（body直接子级表格共%d个）===' % (code, len(tbls)))
    for ti, tbl in enumerate(tbls[:2]):
        rows = tbl.findall(W('tr'))
        print('--- 表%d：%d行 ---' % (ti + 1, len(rows)))
        for ri, tr in enumerate(rows):
            cells = []
            for tc in tr.findall(W('tc')):
                txt = ' '.join(para_text(p).strip() for p in tc.findall(W('p'))).strip()
                txt = re.sub(r'\s+', ' ', txt)
                cells.append(txt)
            print('  行%d：%s' % (ri + 1, ' ｜ '.join(cells)))


def main():
    print('==== ① 十件allowOverlap分布 ====')
    grand = [0, 0, 0, 0]
    for code, fname in FILES.items():
        tot, c0, c1, co = survey_anchor(code, fname)
        grand[0] += tot
        grand[1] += c0
        grand[2] += c1
        grand[3] += co
    print('十件合计 anchor=%d 已0=%d 需改1=%d 缺省/他值=%d' % tuple(grand))
    print('\n==== ② B/E导航表列结构 ====')
    dump_nav('B', FILES['B'])
    dump_nav('E', FILES['E'])


if __name__ == '__main__':
    main()
