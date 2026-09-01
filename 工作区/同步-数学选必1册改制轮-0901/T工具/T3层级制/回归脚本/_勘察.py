# -*- coding: utf-8 -*-
"""勘察B/I1副本：节标题判据（样式/底纹/字号/节号pattern）、题号与条目形态分布"""
import sys, re, zipfile, os
sys.path.insert(0, r'C:\提示词\工具')
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))

def probe(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    n_num = 0
    print('=' * 30, os.path.basename(path))
    sec_pat = re.compile(r'^(\d+\.\d+(?:\.\d+)?)[\s\u3000]+')
    for i, c in enumerate(body):
        if c.tag != q('p'):
            continue
        t = ptext(c).strip()
        if not t:
            continue
        m = sec_pat.match(t)
        is_lec = re.match(r'^\d+(\.\d+)*\s*方法讲解', t)
        is_num = re.match(r'^\d+．', t)
        if m and not is_lec and not is_num and len(t) < 60:
            ppr = c.find(q('pPr'))
            style = shd = sz = None
            if ppr is not None:
                ps = ppr.find(q('pStyle'))
                style = ps.get(q('val')) if ps is not None else None
                sh = ppr.find(q('shd'))
                shd = sh.get(q('fill')) if sh is not None else None
            for r in c.findall(q('r')):
                rpr = r.find(q('rPr'))
                if rpr is not None:
                    s = rpr.find(q('sz'))
                    if s is not None:
                        sz = s.get(q('val')); break
            kind = 'LEC' if is_lec else ('GRP' if '：' in t else 'SEC?')
            print('  [%3d] %s style=%s shd=%s sz=%s | %s' % (i, kind, style, shd, sz, t[:52]))
        elif is_lec:
            print('  [%3d] LECTURE | %s' % (i, t[:52]))
        elif is_num:
            n_num += 1
            if n_num <= 8 or n_num % 20 == 0:
                print('  [%3d] NUM#%d | %s' % (i, n_num, t[:56]))
    print('  -> 数字起段总数=%d' % n_num)

probe(r'测试副本/B讲练上（61题）.docx')
probe(r'测试副本/I1知识清单.docx')
