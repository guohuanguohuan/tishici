# -*- coding: utf-8 -*-
"""F0-定理框统一·验收脚本v2（修box检测bug：strip_pbdr改为深拷贝后再剥，不改原树）。
文字流恒等/仅pBdr差异/字号行距解析抽验/条目与题量断言/框段对照（期望集含e0243共81）。"""
import sys, zipfile, re, copy
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'


def load(path):
    zin = zipfile.ZipFile(path)
    doc = etree.fromstring(zin.read('word/document.xml'))
    zin.close()
    return doc


def textflow(doc):
    out = []
    for el in doc.find(W + 'body').iter():
        if not isinstance(el.tag, str):
            continue
        if el.tag == W + 't' or el.tag == M + 't':
            out.append(el.text or '')
    return ''.join(out)


def textflow_para(doc):
    lines = []
    for p in doc.iter(W + 'p'):
        lines.append(''.join(t.text or '' for t in p.iter() if isinstance(t.tag, str) and t.tag.endswith('}t')))
    return lines


def canon(el):
    return etree.tostring(el, method='c14n2')


def sz_spacing_stats(doc):
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
    """四边single细框段（sz=4 space=4）与其他pBdr段（应仅章标题底边框）。"""
    four, other = [], []
    body = list(doc.find(W + 'body'))
    for i, el in enumerate(body):
        if not isinstance(el.tag, str) or el.tag != W + 'p':
            continue
        ppr = el.find(W + 'pPr')
        if ppr is None:
            continue
        pb = ppr.find(W + 'pBdr')
        if pb is None:
            continue
        sides = {s: pb.find(W + s) for s in ('top', 'left', 'bottom', 'right')}
        if all(v is not None and v.get(W + 'sz') == '4' and v.get(W + 'space') == '4'
               and v.get(W + 'val') == 'single' for v in sides.values()):
            four.append(i)
        else:
            other.append((i, sorted(s for s, v in sides.items() if v is not None)))
    n_tbl_pbdr = sum(1 for tbl in doc.find(W + 'body').iter(W + 'tbl') for _ in tbl.iter(W + 'pBdr'))
    return four, other, n_tbl_pbdr


EXPECT_I1 = {28, 34, 36, 48, 52, 79, 82, 85, 103, 106, 120, 123, 126, 129, 132, 133, 147, 150,
             155, 158, 160, 163, 169, 179, 183, 186, 189, 194, 200, 202, 203, 208, 209, 210, 211,
             212, 223, 231, 234, 237, 238, 243, 245, 247, 254}
EXPECT_I2 = {21, 24, 27, 28, 47, 54, 84, 87, 92, 100, 108, 112, 115, 119, 120, 121, 130, 150, 151,
             154, 155, 157, 176, 177, 178, 196, 197, 225, 226, 230, 243, 255, 257, 264, 265, 282,
             292, 301, 302, 313, 324, 337, 339, 341, 342, 355, 359, 360, 361, 362, 363, 364, 368,
             374, 383, 393, 399, 405, 413, 421, 440, 442, 444, 446, 452, 464, 465, 471, 472, 476,
             483, 484, 485, 486, 487, 488, 492, 494, 514, 517, 520}

for tag, before, after, expect in [('I1', 'I1.改前基线.docx', 'I1.docx', EXPECT_I1),
                                   ('I2', 'I2.改前基线.docx', 'I2.docx', EXPECT_I2)]:
    print('=' * 20, tag, '=' * 20)
    d0, d1 = load(before), load(after)
    tf0, tf1 = textflow(d0), textflow(d1)
    print('[%s] 文字流恒等: %s（改前%d字符 / 改后%d字符）' % (tag, tf0 == tf1, len(tf0), len(tf1)))
    pf0, pf1 = textflow_para(d0), textflow_para(d1)
    print('[%s] 段数: %d -> %d；逐段字符流恒等: %s' % (tag, len(pf0), len(pf1), pf0 == pf1))
    strip0 = copy.deepcopy(d0)
    for pb in list(strip0.iter(W + 'pBdr')):
        pb.getparent().remove(pb)
    c0 = canon(strip0)
    c1t = copy.deepcopy(d1)
    for pb in list(c1t.iter(W + 'pBdr')):
        pb.getparent().remove(pb)
    c1 = canon(c1t)
    print('[%s] 剥离全部pBdr后XML恒等（仅pBdr差异证明）: %s（%d vs %d字节）' % (tag, c0 == c1, len(c0), len(c1)))
    sz0, sp0, ind0, nt0 = sz_spacing_stats(d0)
    sz1, sp1, ind1, nt1 = sz_spacing_stats(d1)
    print('[%s] run字号分布不变: %s -> %s' % (tag, sz0 == sz1, dict(sorted(sz1.items(), key=lambda x: int(x[0])))))
    print('[%s] 段行距分布不变: %s -> %s' % (tag, sp0 == sp1, sp1))
    print('[%s] 无spacing段数: %d -> %d；表格数: %d -> %d' % (tag, ind0, ind1, nt0, nt1))
    f0, o0, t0 = boxes(d0)
    f1, o1, t1 = boxes(d1)
    print('[%s] 定理框四边single sz4sp4段: %d -> %d；其他pBdr段: %s -> %s；表格内pBdr: %d -> %d' % (tag, len(f0), len(f1), o0, o1, t0, t1))
    print('[%s] 条目数: %d -> %d；【答案】标签数（题量，应为0）: %d -> %d' % (tag, entries(d0), entries(d1), qa_labels(d0), qa_labels(d1)))
    print('[%s] 框集与判定表期望集一致: %s（实际%d段 vs 期望%d段）' % (tag, set(f1) == expect, len(f1), len(expect)))
