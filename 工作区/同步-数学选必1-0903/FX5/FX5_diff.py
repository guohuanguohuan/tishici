# -*- coding: utf-8 -*-
"""FX5-G: 归一化字符流diff对账（orig vs fixed 全段落）——改动范围声明"""
import re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return f'{{{W}}}{t}'
def m(t): return f'{{{M}}}{t}'

def stream(path):
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(path, parser)
    body = tree.getroot().find(w('body'))
    out = []
    for p in body.findall(w('p')):
        s = []
        for node in p.iter():
            if node.tag == w('t') and node.text:
                s.append(node.text)
            elif node.tag == m('t') and node.text:
                s.append(node.text)
            elif node.tag == w('drawing'):
                s.append('[IMG]')
        out.append(''.join(s))
    return out

orig = stream(r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml.orig')
fixed = stream(r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\word\document.xml')

# orig[0] deleted
assert '人教B版选必1' in orig[0] and '68题' in orig[0]
o = orig[1:]
assert len(o) == len(fixed), f'{len(o)} vs {len(fixed)}'

diffs = []
for i, (a, b) in enumerate(zip(o, fixed)):
    if a != b:
        diffs.append((i, a, b))
print(f'changed paragraphs: {len(diffs)} / {len(fixed)} (+1 deleted title para)')
for i, a, b in diffs:
    # show compact delta
    print(f'--- p#{i} (fixed)')
    print(f'    O: {a[:100]!r}')
    print(f'    F: {b[:100]!r}')

# char-level net delta
import difflib
net = 0
for i, a, b in diffs:
    sm = difflib.SequenceMatcher(None, a, b)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal':
            net += (j2 - j1) - (i2 - i1)
print('net char delta (changed paras only):', net)
