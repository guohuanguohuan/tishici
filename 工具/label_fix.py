# -*- coding: utf-8 -*-
"""label_fix.py — 标签对齐修复：删「未标注」残缺组＋单独占行【难度】/【知识点】并入前段
用法: python label_fix.py <docx>（就地修改，zip重建）"""
import sys, io, os, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WC = '{%s}'%W

def fix(path):
    zin = zipfile.ZipFile(path)
    root = etree.fromstring(zin.read('word/document.xml'))
    body = root.find(WC+'body')
    n_unmark = 0
    # 1) 删含「未标注」的 run（值与标签同run时整run删；值独立run只删值）
    for p in root.iter(WC+'p'):
        for r in list(p.findall(WC+'r')):
            t = ''.join(x.text or '' for x in r.iter(WC+'t'))
            if not t: continue
            if re.search(r'【(难度|知识点)】未标注', t) and len(t) < 30:
                p.remove(r); n_unmark += 1
            elif t.strip() == '未标注':
                p.remove(r); n_unmark += 1
    # 段内残余
    for t in root.iter(WC+'t'):
        if t.text and '未标注' in t.text:
            t.text = re.sub(r'【(难度|知识点)】未标注\s*|未标注', '', t.text)
    # 2) 单独占行标签并入前一非空段
    children = [c for c in body if etree.QName(c).localname != 'sectPr']
    merged = 0
    i = 0
    while i < len(children):
        t = ''.join(x.text or '' for x in children[i].iter(WC+'t')).strip()
        if re.match(r'^【(难度|知识点)】\S{0,25}$', t):
            j = i - 1
            while j >= 0 and not ''.join(x.text or '' for x in children[j].iter(WC+'t')).strip():
                j -= 1
            if j >= 0:
                prev = children[j]
                for r in list(children[i]):
                    if etree.QName(r).localname in ('r', 'hyperlink'):
                        prev.append(r)
                body.remove(children[i])
                children.pop(i)
                merged += 1
                continue
        i += 1
    # 保存
    zo = zipfile.ZipFile(path + '.tmp', 'w', zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename == 'word/document.xml':
            data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        zo.writestr(it, data)
    zo.close(); zin.close()
    os.replace(path + '.tmp', path)
    # 复验
    root2 = etree.fromstring(zipfile.ZipFile(path).read('word/document.xml'))
    paras = [''.join(x.text or '' for x in p.iter(WC+'t')).strip() for p in root2.iter(WC+'p')]
    na = sum('【答案】' in t for t in paras)
    nd = sum('【难度】' in t for t in paras)
    nk = sum('【知识点】' in t for t in paras)
    nu = sum('未标注' in t for t in paras)
    solo = sum(1 for t in paras if re.match(r'^【(难度|知识点)】\S{0,25}$', t))
    print('%-56s 删未标注%d 合并%d -> A/D/K=%d/%d/%d 未标注%d 单独行%d' % (os.path.basename(path)[:54], n_unmark, merged, na, nd, nk, nu, solo))

if __name__ == '__main__':
    for p in sys.argv[1:]:
        fix(p)
