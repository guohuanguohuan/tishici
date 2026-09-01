# -*- coding: utf-8 -*-
"""T4 一次性勘察：段落文本+底纹形态概览（不入工具/）"""
import sys, io, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def para_info(path, lo=0, hi=200):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(q('body'))
    els = list(body)
    print('== %s | body级元素 %d' % (path.split('\\')[-1], len(els)))
    for i, el in enumerate(els):
        if i < lo or i >= hi:
            continue
        if el.tag != q('p'):
            print('%4d [%s]' % (i, tag(el)))
            continue
        t = ptext(el)
        ppr = el.find(q('pPr'))
        pshd = ppr.find(q('shd')) if ppr is not None else None
        pf = pshd.get(q('fill')) if pshd is not None else ''
        # run级底纹统计
        fills = {}
        nrun = 0; nomath = 0
        for r in el.iter(q('r')):
            nrun += 1
            rpr = r.find(q('rPr'))
            s = rpr.find(q('shd')) if rpr is not None else None
            if s is not None:
                f = s.get(q('fill'))
                fills[f] = fills.get(f, 0) + 1
        nomath = len(el.findall(q('oMath'))) + len(el.findall(q('oMathPara')))
        mom = 0
        for om in el.iter('{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath'):
            for mr in om.iter('{http://schemas.openxmlformats.org/officeDocument/2006/math}r'):
                rpr = mr.find(q('rPr'))
                s = rpr.find(q('shd')) if rpr is not None else None
                if s is not None:
                    f = s.get(q('fill'))
                    fills['OMML:'+f] = fills.get('OMML:'+f, 0) + 1
            mom += 1
        print('%4d pshd=%-7s run=%d om=%d fills=%s | %s' % (i, pf, nrun, mom, fills, t[:70]))

if __name__ == '__main__':
    base = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\T工具\T4浅底分型\副本\\'
    which = sys.argv[1] if len(sys.argv) > 1 else 'x2'
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    files = {
        'x2': base + '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
        'f': base + '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
        'i2': base + '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    }
    para_info(files[which], lo, hi)
