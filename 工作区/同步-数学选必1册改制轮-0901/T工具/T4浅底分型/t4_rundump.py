# -*- coding: utf-8 -*-
"""T4 一次性勘察2：指定段落的run级明细（w:r / m:oMath 顺序+底纹+颜色）"""
import sys, io, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

def rinfo(rpr):
    if rpr is None:
        return '-'
    out = []
    for c in rpr:
        tn = tag(c)
        if tn == 'shd':
            out.append('shd=' + (c.get(q('fill')) or '?'))
        elif tn == 'color':
            out.append('color=' + (c.get(q('val')) or '?'))
        elif tn in ('b', 'bCs'):
            out.append(tn)
        elif tn == 'rFonts':
            out.append('font')
    return ','.join(out) if out else 'empty'

def dump_para(path, idxs):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(q('body'))
    els = list(body)
    print('== %s' % path.split('\\')[-1])
    for i in idxs:
        el = els[i]
        print('--- para %d' % i)
        for c in el:
            tn = tag(c)
            ns = etree.QName(c).namespace
            if tn == 'r' and ns == W:
                txt = ''.join(t.text or '' for t in c.findall(q('t')))
                print('  w:r  [%s] %r' % (rinfo(c.find(q('rPr'))), txt[:50]))
            elif tn in ('oMath', 'oMathPara'):
                nmr = 0; nctrl = 0; gmr = 0; gctrl = 0; mt = ''
                for e in c.iter():
                    if etree.QName(e).namespace != M:
                        continue
                    t2 = tag(e)
                    if t2 == 'r':
                        nmr += 1
                        rpr = e.find(q('rPr'))
                        s = rpr.find(q('shd')) if rpr is not None else None
                        if s is not None and s.get(q('fill')) == 'C9C9C9':
                            gmr += 1
                        if t2 == 'r' and e.getparent() is not None:
                            mt += ''.join(t.text or '' for t in e.findall(M and q('t')))
                    elif t2 == 'ctrlPr':
                        nctrl += 1
                        rpr = e.find(q('rPr'))
                        s = rpr.find(q('shd')) if rpr is not None else None
                        if s is not None and s.get(q('fill')) == 'C9C9C9':
                            gctrl += 1
                print('  %s  m:r=%d(g%d) ctrl=%d(g%d) text=%r' % (tn, nmr, gmr, nctrl, gctrl, mt[:40]))
            elif tn == 'pPr':
                s = c.find(q('shd'))
                print('  pPr shd=%s' % (s.get(q('fill')) if s is not None else ''))
            else:
                print('  <%s>' % tn)

if __name__ == '__main__':
    base = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\T工具\T4浅底分型\副本\\'
    which = sys.argv[1]
    idxs = [int(x) for x in sys.argv[2:]]
    files = {
        'x2': base + '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
        'f': base + '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
        'i2': base + '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    }
    dump_para(files[which], idxs)
