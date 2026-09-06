# -*- coding: utf-8 -*-
"""⑧轮债1探针4：X1/X2 覆盖循环(:727-763)转实漂移机理定位——:736 裸 startswith 门 vs 灰底值在场性。"""
import sys, re, zipfile
sys.path.insert(0, r'C:/提示词/工具')
from extract_structure import structure
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
WJ = '\u2060'
CHIP_RE = re.compile(r'【[^】]{1,16}】')
FILL_CONTENT = 'C7C7C7'
DEEP_BLUE = '1F4E79'

def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def shd_fill(rpr):
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd.get(q('fill')) if shd is not None else None
def deep_blue(rpr):
    if rpr is None: return False
    c = rpr.find(q('color'))
    return c is not None and c.get(q('val')) == DEEP_BLUE

for code, path in [('X1', r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
                   ('X2', r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx')]:
    st = structure(path)
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    els = list(doc.find(q('body')))
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    items = st['items']
    n_gatefail = n_cov_sim = 0
    for qu in st['questions']:
        s_el = items[qu['start']]['el']
        e_el = items[qu['end']]['el'] if qu['end'] < len(items) else len(els)
        gate_hit = sim_hit = False
        for ci in range(s_el, e_el):
            if els[ci].tag != q('p'): continue
            t = ptexts[ci]
            if not t.replace(WJ, '').startswith('【答案】'): continue
            if t.startswith('【答案】'):
                gate_hit = True          # 现行 :736 裸门可开
            sim_hit = True               # 若门做 WJ 归一即可进入 run 扫描
            for r in els[ci].iter(q('r')):
                txt = ''.join(x.text or '' for x in r.findall(q('t')))
                if txt and not CHIP_RE.fullmatch(txt) and \
                        (shd_fill(r.find(q('rPr'))) == FILL_CONTENT or deep_blue(r.find(q('rPr')))):
                    sim_hit = '值行灰底/深蓝在位'; break
            if sim_hit is not True and sim_hit != '值行灰底/深蓝在位':
                pass
            break
        if sim_hit == '值行灰底/深蓝在位': n_cov_sim += 1
        if not gate_hit: n_gatefail += 1
    n = len(st['questions'])
    print('%s: 题块 %d｜:736裸门可开 %d（归一后可入扫描 %d）｜门归一后覆盖模拟 %d/%d'
          % (code, n, n - n_gatefail, n, n_cov_sim, n))
    # 样本：首题【答案】行原文前12字（可见WJ）
    qu = st['questions'][0]
    s_el = items[qu['start']]['el']
    for ci in range(s_el, min(s_el + 12, len(els))):
        t = ptexts.get(ci, '')
        if t.replace(WJ, '').startswith('【答案】'):
            print('   首题【答案】行原文=%r  startswith裸真=%s' % (t[:14], t.startswith('【答案】')))
            break
