# -*- coding: utf-8 -*-
"""M配页·册目录页结构dump：逐段输出段落文本/缩进/字号/加粗/制表位/点线，供页码列重算定位。"""
import sys, io, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = NS['w']

def qn(t): return '{%s}%s' % (W, t)

path = sys.argv[1]
with zipfile.ZipFile(path) as z:
    xml = z.read('word/document.xml')
root = etree.fromstring(xml)
body = root.find(qn('body'))

for i, p in enumerate(body.iter(qn('p'))):
    pPr = p.find(qn('pPr'))
    ind = ''
    tabs = ''
    if pPr is not None:
        indEl = pPr.find(qn('ind'))
        if indEl is not None:
            ind = 'ind(' + ','.join(f'{k.split("}")[1]}={v}' for k, v in indEl.attrib.items()) + ')'
        tabsEl = pPr.find(qn('tabs'))
        if tabsEl is not None:
            tinfo = []
            for tb in tabsEl.findall(qn('tab')):
                tinfo.append(','.join(f'{k.split("}")[1]}={v}' for k, v in tb.attrib.items()))
            tabs = 'tabs[' + ';'.join(tinfo) + ']'
    runs = []
    for r in p.iter(qn('r')):
        rPr = r.find(qn('rPr'))
        sz = b = shd = ''
        if rPr is not None:
            szEl = rPr.find(qn('sz'))
            sz = szEl.get(qn('val')) if szEl is not None else ''
            bEl = rPr.find(qn('b'))
            b = 'B' if bEl is not None and bEl.get(qn('val')) != '0' and bEl.get(qn('val')) != 'false' else ''
            shdEl = rPr.find(qn('shd'))
            if shdEl is not None:
                shd = 'shd:' + shdEl.get(qn('fill'), '')
        txt = ''.join(t.text or '' for t in r.iter(qn('t')))
        fld = ''.join(t.text or '' for t in r.iter(qn('instrText')))
        tabc = 'TAB' if r.find(qn('tab')) is not None else ''
        if txt or fld or tabc:
            runs.append(f'<{sz}{b}{"|"+shd if shd else ""}>{tabc}{"«"+txt+"»" if txt else ""}{"§"+fld+"§" if fld else ""}')
    full = ''.join(t.text or '' for t in p.iter(qn('t')))
    print(f'[{i:03d}] {ind} {tabs} | {full!r}')
    if runs:
        print('      runs:', ' ∥ '.join(runs))
