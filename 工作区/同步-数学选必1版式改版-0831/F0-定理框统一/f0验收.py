# -*- coding: utf-8 -*-
"""F0-定理框统一·验收脚本：文字流恒等/仅pBdr差异/字号行距解析抽验/条目与题量断言/框段对照。"""
import sys, zipfile, re
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def load(path):
    zin = zipfile.ZipFile(path)
    doc = etree.fromstring(zin.read('word/document.xml'))
    styles = zin.read('word/styles.xml') if 'word/styles.xml' in zin.namelist() else None
    zin.close()
    return doc, styles


def textflow(doc):
    """文档序全文字符流：w:t + m:t，含段边界分隔符。"""
    out = []
    body = doc.find(W + 'body')
    for el in body.iter():
        if not isinstance(el.tag, str):
            continue
        if el.tag == W + 't' or el.tag.endswith('}t') and el.tag.startswith('{http://schemas.openxmlformats.org/officeDocument/2006/math}'):
            out.append(el.text or '')
    return ''.join(out)


def textflow_para(doc):
    """逐段字符流（含表格单元格段），用于段级恒等对比。"""
    lines = []
    for p in doc.iter(W + 'p'):
        lines.append(''.join(t.text or '' for t in p.iter() if isinstance(t.tag, str) and t.tag.endswith('}t')))
    return lines


def strip_pbdr(doc):
    for pb in list(doc.iter(W + 'pBdr')):
        pb.getparent().remove(pb)
    return doc


def canon(el):
    return etree.tostring(el, method='c14n2')


def sz_spacing_stats(doc):
    """run字号分布与段落行距分布（正文段落，不含页眉脚——document.xml内即正文）。"""
    sz = {}
    for rpr in doc.iter(W + 'rPr'):
        e = rpr.find(W + 'sz')
        if e is not None and e.get(W + 'val'):
            v = e.get(W + 'val'); sz[v] = sz.get(v, 0) + 1
    sp = {}
    ind = 0
    for ppr in doc.iter(W + 'pPr'):
        e = ppr.find(W + 'spacing')
        if e is not None:
            key = (e.get(W + 'line'), e.get(W + 'lineRule'))
            sp[key] = sp.get(key, 0) + 1
        else:
            ind += 1
    ntbl = sum(1 for t in doc.iter(W + 'tbl'))
    return sz, sp, ind, ntbl


def entries(doc):
    n = 0
    for p in doc.iter(W + 'p'):
        t = ''.join(x.text or '' for x in p.iter(W + 't'))
        if re.match(r'^\d{1,2}．〔基|^\d{1,2}．〔进', t):
            n += 1
    return n


def qa_labels(doc):
    return sum(1 for t in doc.iter(W + 't') if t.text and '【答案】' in t.text)


def boxes(doc):
    out = []
    body = list(doc.find(W + 'body'))
    for i, p in enumerate(body):
        if p.tag != W + 'p':
            continue
        ppr = p.find(W + 'pPr')
        if ppr is None:
            continue
        pb = ppr.find(W + 'pBdr')
        if pb is None:
            continue
        sides = [s for s in ('top', 'left', 'bottom', 'right') if pb.find(W + s) is not None]
        out.append((i, len(sides), all(pb.find(W + s).get(W + 'sz') == '4' and pb.find(W + s).get(W + 'space') == '4' for s in sides) if len(sides) == 4 else False))
    return out


for tag, before, after in [('I1', 'I1.改前基线.docx', 'I1.docx'), ('I2', 'I2.改前基线.docx', 'I2.docx')]:
    print('=' * 20, tag, '=' * 20)
    d0, _ = load(before); d1, _ = load(after)
    tf0, tf1 = textflow(d0), textflow(d1)
    print(f'[{tag}] 文字流恒等: {tf0 == tf1}（改前{len(tf0)}字符 / 改后{len(tf1)}字符）')
    pf0, pf1 = textflow_para(d0), textflow_para(d1)
    print(f'[{tag}] 段数: {len(pf0)} -> {len(pf1)}；逐段字符流恒等: {pf0 == pf1}')
    c0, c1 = canon(strip_pbdr(d0)), canon(strip_pbdr(d1))
    print(f'[{tag}] 剥离全部pBdr后XML恒等（仅pBdr差异证明）: {c0 == c1}（{len(c0)} vs {len(c1)}字节）')
    sz0, sp0, ind0, nt0 = sz_spacing_stats(d0)
    sz1, sp1, ind1, nt1 = sz_spacing_stats(d1)
    print(f'[{tag}] run字号分布不变: {sz0 == sz1} -> {dict(sorted(sz1.items(), key=lambda x: int(x[0])))}')
    print(f'[{tag}] 段行距分布不变: {sp0 == sp1} -> {sp1}')
    print(f'[{tag}] 无spacing段数: {ind0} -> {ind1}；表格数: {nt0} -> {nt1}')
    b0, b1 = boxes(d0), boxes(d1)
    four0 = [i for i, n, ok in b0 if n == 4 and ok]
    four1 = [i for i, n, ok in b1 if n == 4 and ok]
    other0 = [i for i, n, ok in b0 if n != 4 or not ok]
    other1 = [i for i, n, ok in b1 if n != 4 or not ok]
    print(f'[{tag}] 定理框四边细框段: {len(four0)} -> {len(four1)}；非四边sz4sp4框段（应仅章标题底边框）: {other0} -> {other1}')
    print(f'[{tag}] 条目数: {entries(d0)} -> {entries(d1)}；【答案】标签数（题量，应为0）: {qa_labels(d0)} -> {qa_labels(d1)}')
    if tag == 'I2':
        expect = {21, 24, 27, 28, 47, 54, 84, 87, 92, 100, 108, 112, 115, 119, 120, 121, 130, 150, 151, 154, 155, 157, 176, 177, 178, 196, 197, 225, 226, 230, 255, 257, 264, 265, 282, 292, 301, 302, 313, 324, 337, 339, 341, 342, 355, 359, 360, 361, 362, 363, 364, 368, 374, 383, 393, 399, 405, 413, 421, 440, 442, 444, 446, 452, 464, 465, 471, 472, 476, 483, 484, 485, 486, 487, 488, 492, 494, 514, 517, 520}
        print(f'[{tag}] 框集与判定表期望集一致: {set(four1) == expect}（实际{len(four1)}段 vs 期望{len(expect)}段）')
