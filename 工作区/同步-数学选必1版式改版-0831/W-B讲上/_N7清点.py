# -*- coding: utf-8 -*-
"""N7 前置清点：全件 C9C9C9 底纹 run 分类统计（一次性脚本）"""
import zipfile, json, re, sys
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

def runs_of(p):
    return p.findall('.//' + w('r'))

def rtext(r):
    return ''.join(t.text or '' for t in r.iter() if t.tag in (w('t'), '{%s}t' % M))

def rshd(r):
    rPr = r.find(w('rPr'))
    if rPr is None: return None
    s = rPr.find(w('shd'))
    return None if s is None else s.get(w('fill'))

def rcolor(r):
    rPr = r.find(w('rPr'))
    if rPr is None: return None
    c = rPr.find(w('color'))
    return None if c is None else c.get(w('val'))

def in_table(p, body):
    # 判断段落是否在表内：沿父链找 w:tbl
    par = p.getparent()
    while par is not None:
        if par.tag == w('tbl'): return True
        par = par.getparent()
    return False

def main(path):
    with zipfile.ZipFile(path) as z:
        doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(w('body'))
    cats = {}
    samples = {}
    for p in body.iter(w('p')):
        tbl = in_table(p, body)
        for r in runs_of(p):
            if rshd(r) != 'C9C9C9': continue
            t = rtext(r)
            # 分类
            if tbl:
                cat = 'TBL'  # 导航表/内容表内
            elif re.fullmatch(r'\d+．', t):
                cat = 'NUM'  # 题号块N．或条目号N．
            elif re.fullmatch(r'【[^】]*】', t.strip()):
                cat = 'CHIP'  # 块标签芯片
            elif re.fullmatch(r'（\d+）', t):
                cat = 'SUB1'  # 第一子层（N）
            else:
                cat = 'CONTENT'
            col = rcolor(r)
            key = (cat, col)
            cats[key] = cats.get(key, 0) + 1
            samples.setdefault(key, []).append(t[:30])
    for k in sorted(cats, key=str):
        print(k, cats[k], '样例:', samples[k][:4])
    # CONTENT 类含「＿＿」的段落级上下文
    print('--- CONTENT run 样本（前30） ---')
    n = 0
    for p in body.iter(w('p')):
        if in_table(p, body): continue
        for r in runs_of(p):
            if rshd(r) == 'C9C9C9' and not re.fullmatch(r'\d+．', rtext(r)) and not re.fullmatch(r'【[^】]*】', rtext(r).strip()) and not re.fullmatch(r'（\d+）', rtext(r)):
                ptxt = ''.join(rtext(x) for x in runs_of(p))
                print('RUN[%s] PAR[%s]' % (rtext(r)[:24], ptxt[:60]))
                n += 1
                if n >= 30: break
        if n >= 30: break

if __name__ == '__main__':
    main(sys.argv[1])
