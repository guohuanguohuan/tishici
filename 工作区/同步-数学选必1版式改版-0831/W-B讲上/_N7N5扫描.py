# -*- coding: utf-8 -*-
"""N15 前置：全件「＿＿」出现位置扫描（答案在位性核验）"""
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

def main(path):
    with zipfile.ZipFile(path) as z:
        doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(w('body'))
    total = 0
    for p in body.iter(w('p')):
        rs = p.findall('.//' + w('r'))
        ptxt = ''.join(rtext(x) for x in rs)
        hits = re.findall(r'＿+', ptxt)
        if not hits: continue
        # 段内灰底run（答案候选）
        grey = [(i, rtext(r)) for i, r in enumerate(rs) if rshd(r) == 'C9C9C9']
        total += len(hits)
        print('PAR[%s] ＿×%d 段文本[%s]' % (len(hits), 0, ptxt[:90]))
        print('   灰底runs:', [(i, t[:16]) for i, t in grey if t.strip()][:8])
    print('＿＿串总数:', total)

if __name__ == '__main__':
    main(sys.argv[1])
