# -*- coding: utf-8 -*-
"""FX5-G probe 13: OMML structure of ④-hit paras"""
from lxml import etree

DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

tree = etree.parse(DOC)
body = tree.getroot().find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

HITS = [26, 51, 60, 62, 119, 130, 175, 339, 443, 455, 456, 652, 654, 721]

def omml_struct(om, depth=0):
    """print structural skeleton: element names + key attrs + m:t text"""
    out = []
    def walk(el, d=0):
        for c in el:
            t = c.tag.split('}')[1]
            if t in ('rPr',):
                continue
            if t == 't':
                out.append('  ' * d + f"'{c.text}'")
                continue
            attrs = ''
            if t == 'd':  # delimiter
                prs = []
                dPr = c.find(f'{{{M}}}dPr')
                if dPr is not None:
                    for a in dPr:
                        at = a.tag.split('}')[1]
                        for k, v in a.attrib.items():
                            prs.append(f'{at}={v}')
                attrs = '[' + ','.join(prs) + ']'
            if t in ('eqArr', 'f', 'rad', 'sSub', 'sSup', 'd', 'm', 'func', 'nary'):
                out.append('  ' * d + t + attrs)
                walk(c, d + 1)
            elif t == 'oMath' or t == 'oMathPara':
                out.append('  ' * d + t)
                walk(c, d + 1)
            elif t == 'e':
                walk(c, d)
            else:
                walk(c, d)
    walk(om)
    return '\n'.join(out)

def ptext(p):
    out = []
    def walk(el):
        for c in el:
            if c.tag == f'{{{W}}}t' and c.text is not None:
                out.append(c.text)
            elif c.tag == f'{{{M}}}t' and c.text is not None:
                out.append(c.text)
            else:
                walk(c)
    walk(p)
    return ''.join(out)

for idx in HITS:
    p = paras[idx]
    print(f'\n########## p#{idx} full text: {ptext(p)[:150]!r}')
    # find the oMath containing the hit — print all oMath structs (truncated)
    for j, om in enumerate(p.iter(f'{{{M}}}oMath')):
        txt = ''.join(x.text or '' for x in om.iter(f'{{{M}}}t'))
        if len(txt) < 3:
            continue
        s = omml_struct(om)
        if len(s.splitlines()) > 40:
            s = '\n'.join(s.splitlines()[:40]) + '\n...(truncated)'
        print(f'--- oMath[{j}] text={txt[:80]!r}')
        print(s)
