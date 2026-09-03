# -*- coding: utf-8 -*-
r"""六件H1~H5＋新签名H6（正文节sectPr缺w:type=continuous）全量排查（子步1·一次性脚本）。
逐件实测：分节数与各节w:type、H1显式分页计数、H2表数与导航表落点、H3 docGrid、H4承载段前后元素、
H5页眉页脚/titlePg、头部区元素清单（段号对账基础）。
"""
import sys, io, os, zipfile, json
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def nospc(s):
    import re
    return re.sub(r'[\s　]+', '', s or '')

FILES = {
 'X1': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
 'I1': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 'B':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 'X2': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
}

def is_navtbl(tbl):
    tr = tbl.find(q('tr'))
    if tr is None: return False
    cells = [nospc(ptext(tc)) for tc in tr.findall(q('tc'))]
    return any('节名' in c for c in cells) and any('题量' in c for c in cells) and any('题型组数' in c for c in cells)

def sect_summary(s):
    t = s.find(q('type'))
    cols = s.find(q('cols'))
    dg = s.find(q('docGrid'))
    hr = s.findall(q('headerReference')); fr = s.findall(q('footerReference'))
    pg = s.find(q('pgNumType'))
    return {
        'type': (t.get(q('val')) if t is not None else '(缺省=nextPage)'),
        'cols': ({etree.QName(k).localname: v for k, v in cols.attrib.items()} if cols is not None else None),
        'docGrid': ({etree.QName(k).localname: v for k, v in dg.attrib.items()} if dg is not None else None),
        'headerRef': len(hr), 'footerRef': len(fr),
        'titlePg': s.find(q('titlePg')) is not None,
        'pgNumType': ({etree.QName(k).localname: v for k, v in pg.attrib.items()} if pg is not None else None),
    }

report = {}
for code, path in FILES.items():
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = root.find(q('body'))
    kids = list(body)
    R = {'file': os.path.basename(path), 'body_children': len(kids)}
    # 段落级sectPr全部位置
    brks = []
    for i, el in enumerate(kids):
        if etree.QName(el).localname == 'p':
            ppr = el.find(q('pPr'))
            if ppr is not None and ppr.find(q('sectPr')) is not None:
                brks.append(i)
    R['para_sectPr_idx'] = brks
    sects = [kids[i].find(q('pPr')).find(q('sectPr')) for i in brks]
    bsect = body.find(q('sectPr'))
    sects.append(bsect)
    R['sections'] = [sect_summary(s) for s in sects]
    # H1
    brs = root.findall('.//' + q('br'))
    bt = {}
    for b in brs:
        t = b.get(q('type'), 'textWrapping'); bt[t] = bt.get(t, 0) + 1
    R['H1'] = {'br': bt, 'pageBreakBefore': len(root.findall('.//' + q('pageBreakBefore'))),
               'keepNext': len(root.findall('.//' + q('keepNext'))),
               'keepLines': len(root.findall('.//' + q('keepLines'))),
               'widowControl': len(root.findall('.//' + q('widowControl'))),
               'cantSplit': len(root.findall('.//' + q('cantSplit')))}
    # H2/导航表落点
    tbls = [(i, el) for i, el in enumerate(kids) if etree.QName(el).localname == 'tbl']
    R['tbl_count'] = len(tbls)
    nav = [(i, is_navtbl(el)) for i, el in tbls]
    R['nav_idx'] = [i for i, ok in nav if ok]
    # 头部区元素清单（分节符承载段及其之前）
    if brks:
        b0 = brks[0]
        hdr = []
        for i in range(0, b0 + 1):
            el = kids[i]
            ln = etree.QName(el).localname
            txt = ptext(el)[:50] if ln == 'p' else '(tbl)%s' % ('导航表' if is_navtbl(el) else '')
            hdr.append({'idx': i, 'kind': ln, 'text': txt})
        R['header_zone'] = hdr
        R['break_carrier_text'] = ptext(kids[b0])[:60]
        # 正文区前3元素
        bd = []
        for i in range(b0 + 1, min(len(kids), b0 + 4)):
            el = kids[i]
            ln = etree.QName(el).localname
            bd.append({'idx': i, 'kind': ln, 'text': (ptext(el)[:40] if ln == 'p' else '(tbl)')})
        R['body_head'] = bd
    report[code] = R

dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), '六件_H1_H6排查.json')
with open(dst, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
for code, R in report.items():
    print('== %s == body子元素=%d 段落级sectPr=%s' % (code, R['body_children'], R['para_sectPr_idx']))
    for j, s in enumerate(R['sections']):
        tag = '头部节' if j == 0 else ('正文节(文末)' if j == len(R['sections']) - 1 else '中间节%d' % j)
        print('  %s: type=%s cols=%s docGrid=%s hdr/ftr=%d/%d titlePg=%s pgNum=%s'
              % (tag, s['type'], s['cols'], s['docGrid'], s['headerRef'], s['footerRef'], s['titlePg'], s['pgNumType']))
    print('  H1=%s' % R['H1'])
    print('  表数=%d 导航表下标=%s' % (R['tbl_count'], R['nav_idx']))
    if 'header_zone' in R:
        print('  头部区: %s' % [(h['idx'], h['kind'], h['text'][:30]) for h in R['header_zone']])
        print('  正文首: %s' % [(h['idx'], h['kind'], h['text'][:30]) for h in R['body_head']])
print('落盘: 六件_H1_H6排查.json')
