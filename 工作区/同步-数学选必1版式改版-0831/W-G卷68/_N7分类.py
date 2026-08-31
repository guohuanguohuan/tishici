# -*- coding: utf-8 -*-
"""N7 前置分类：CONTENT 类 run 全量清单＋并行解法标记识别"""
import zipfile, re, sys
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

def rtext(r):
    return ''.join(t.text or '' for t in r.iter() if t.tag in (w('t'), '{%s}t' % M))

def rshd(r):
    rPr = r.find(w('rPr'))
    if rPr is None: return None
    s = rPr.find(w('shd'))
    return None if s is None else s.get(w('fill'))

def in_table(p):
    par = p.getparent()
    while par is not None:
        if par.tag == w('tbl'): return True
        par = par.getparent()
    return False

PARALLEL = re.compile(r'^(方法[一二三四五六七八九十]|解法[一二三四五六七八九十]|另解|法[一二三四五六七八九十])[：:]?$')

def main(path):
    with zipfile.ZipFile(path) as z:
        doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(w('body'))
    n_ans, n_par, n_other = 0, 0, 0
    others = []
    for p in body.iter(w('p')):
        if in_table(p): continue
        rs = p.findall('.//' + w('r'))
        ptxt = ''.join(rtext(x) for x in rs)
        has_answer_chip = bool(re.search(r'【答案】', ptxt[:12]))
        for r in rs:
            if rshd(r) != 'C9C9C9': continue
            t = rtext(r)
            if re.fullmatch(r'\d+．', t) or re.fullmatch(r'【[^】]*】', t.strip()) or re.fullmatch(r'（\d+）', t):
                continue
            if PARALLEL.match(t.strip()):
                n_par += 1
                continue
            if has_answer_chip or re.match(r'^\(\d\)', ptxt[:4]):
                n_ans += 1
                continue
            n_other += 1
            others.append((t[:40], ptxt[:80]))
    print('答案值runs(段落含【答案】起头或(1)起头):', n_ans)
    print('并行解法标记runs:', n_par)
    print('其他CONTENT runs:', n_other)
    for t, pt in others:
        print('  OTHER[%s] PAR[%s]' % (t, pt))

if __name__ == '__main__':
    main(sys.argv[1])
