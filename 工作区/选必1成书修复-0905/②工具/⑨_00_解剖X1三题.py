# -*- coding: utf-8 -*-
"""⑨轮探针0：X1 三题（1.2.1.2-9／1.2.1.3-15／1.2.5.2-10）详解区值行形态解剖。
与计数器 :727-763 覆盖循环同构取块；逐段引出归一后全文＋逐 run 底纹/色值/OMML 挂点。只读。"""
import sys, re, zipfile
sys.path.insert(0, r'C:/提示词/工具')
from extract_structure import structure
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
WJ = '\u2060'
NORM = str.maketrans('', '', WJ)
CHIP_RE = re.compile(r'【[^】]{1,16}】')
NUMDOT_RE = re.compile(r'^\d+．$')
FILL_CONTENT = 'C7C7C7'
DEEP_BLUE = '1F4E79'
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def vis(s): return s.replace(WJ, 'Ⓙ')
def shd_fill(rpr):
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd.get(q('fill')) if shd is not None else None
def deep_blue(rpr):
    if rpr is None: return False
    c = rpr.find(q('color'))
    return c is not None and c.get(q('val')) == DEEP_BLUE

PATH = r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'
st = structure(PATH)
z = zipfile.ZipFile(PATH)
doc = etree.fromstring(z.read('word/document.xml'))
z.close()
els = list(doc.find(q('body')))
ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
items = st['items']

TARGET = {'1.2.1.2-9', '1.2.1.3-15', '1.2.5.2-10'}
for qu in st['questions']:
    if qu['no'] not in TARGET:
        continue
    s_el = items[qu['start']]['el']
    e_el = items[qu['end']]['el'] if qu['end'] < len(items) else len(els)
    print('=' * 100)
    print('题 %s｜items[%d..%d)｜body el [%d..%d)' % (qu['no'], qu['start'], qu['end'], s_el, e_el))
    for ci in range(s_el, e_el):
        el = els[ci]
        if tag(el) != 'p':
            print('  [%d] <%s>（非段落元素）' % (ci, tag(el)))
            continue
        t = ptexts[ci]
        tn = t.translate(NORM)
        is_ans = tn.startswith('【答案】')
        is_kp = '【知识点】' in tn
        print('  [%d] 段 原文=%r' % (ci, vis(t)[:80]))
        if not t.strip() and not list(el.iter(q('drawing'))) and not list(el.iter(q('tbl'))):
            print('       （空文本段）')
        # 逐 run
        for r in el.iter(q('r')):
            txt = ''.join(x.text or '' for x in r.findall(q('t')))
            rpr = r.find(q('rPr'))
            f = shd_fill(rpr); db = deep_blue(rpr)
            if txt or f or db:
                print('       run txt=%r fill=%s deep_blue=%s%s' % (vis(txt)[:40], f, db,
                      ' ←命中腿1' if (txt and not CHIP_RE.fullmatch(txt) and (f == FILL_CONTENT or db)) else ''))
        # OMML 挂点
        for m_el in el.iter():
            if etree.QName(m_el).namespace == M and tag(m_el) in ('r', 'ctrlPr'):
                rpr = m_el.find(q('rPr'))
                f = shd_fill(rpr); db = deep_blue(rpr)
                mt = ''.join(t.text or '' for t in m_el.iter(q('t')))
                print('       OMML m:%s txt=%r fill=%s deep_blue=%s%s' % (tag(m_el), vis(mt)[:40], f, db,
                      ' ←命中腿2' if (f == FILL_CONTENT or db) else ''))
        # 腿3模拟（仅对【答案】段做）
        if is_ans:
            cj = ci + 1
            while cj < e_el and tag(els[cj]) == 'p' and not ptexts[cj].strip():
                cj += 1
            if cj < e_el and tag(els[cj]) == 'p':
                for r in els[cj].iter(q('r')):
                    txt = ''.join(x.text or '' for x in r.findall(q('t')))
                    rpr = r.find(q('rPr'))
                    f = shd_fill(rpr); db = deep_blue(rpr)
                    if txt and not CHIP_RE.fullmatch(txt) and not NUMDOT_RE.match(txt) \
                            and (f == FILL_CONTENT or db):
                        print('       腿3续值段[%d] run txt=%r ←命中' % (cj, vis(txt)[:40]))
            print('       （【答案】段腿1/2/3 模拟结束；【知识点】在本段=%s）' % is_kp)
