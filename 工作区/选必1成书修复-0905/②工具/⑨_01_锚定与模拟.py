# -*- coding: utf-8 -*-
"""⑨轮探针1：(a) 12件docx MD5改前锚定→报告/⑨_12件MD5锚定.json；
(b) SM 两题块解剖（防腿3扩展翻转 SM 0/2）；(c) X1 已覆盖题对照解剖；
(d) 修后逻辑模拟（门WJ归一＋腿3续值段加OMML扫描）对 X1/X2/SM 预测覆盖。只读。"""
import sys, re, zipfile, hashlib, json
sys.path.insert(0, r'C:/提示词/工具')
from extract_structure import structure
from lxml import etree

ROOT = r'C:/提示词'
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

CASES = [
    ('B',   '高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
    ('C',   '高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
    ('E',   '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
    ('F',   '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
    ('G',   '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
    ('H',   '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
    ('I1',  '高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
    ('I2',  '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
    ('X1',  '高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
    ('X2',  '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
    ('SM',  '高中数学/高中数学同步/人教B版选必1·使用说明.docx'),
    ('TOC', '高中数学/高中数学同步/人教B版选必1·册目录页.docx'),
]

# (a) MD5 锚定
anchor = {}
for code, rel in CASES:
    p = ROOT + '/' + rel
    h = hashlib.md5()
    with open(p, 'rb') as f:
        h.update(f.read())
    anchor[code] = {'path': rel, 'md5': h.hexdigest(), 'bytes': __import__('os').path.getsize(p)}
out_json = ROOT + '/工作区/选必1成书修复-0905/②工具/报告/⑨_12件MD5锚定.json'
with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(anchor, f, ensure_ascii=False, indent=1)
print('MD5锚定 %d 件 → %s' % (len(anchor), out_json))

def dump_block(code, rel, want_nos, maxq=None):
    path = ROOT + '/' + rel
    st = structure(path)
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    els = list(doc.find(q('body')))
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    items = st['items']
    for qu in st['questions'][:maxq] if maxq else st['questions']:
        if want_nos is not None and qu['no'] not in want_nos:
            continue
        s_el = items[qu['start']]['el']
        e_el = items[qu['end']]['el'] if qu['end'] < len(items) else len(els)
        print('-' * 90)
        print('%s 题 %s｜body el [%d..%d)' % (code, qu['no'], s_el, e_el))
        for ci in range(s_el, e_el):
            el = els[ci]
            if tag(el) != 'p':
                print('  [%d] <%s>' % (ci, tag(el))); continue
            print('  [%d] %r' % (ci, vis(ptexts[ci])[:70]))
            for r in el.iter(q('r')):
                txt = ''.join(x.text or '' for x in r.findall(q('t')))
                rpr = r.find(q('rPr'))
                f_, db = shd_fill(rpr), deep_blue(rpr)
                if txt or f_ or db:
                    print('       run %r fill=%s db=%s' % (vis(txt)[:36], f_, db))
            for m_el in el.iter():
                if etree.QName(m_el).namespace == M and tag(m_el) in ('r', 'ctrlPr'):
                    rpr = m_el.find(q('rPr'))
                    print('       m:%s fill=%s db=%s' % (tag(m_el), shd_fill(rpr), deep_blue(rpr)))

# (b) SM 两题解剖
dump_block('SM', CASES[10][1], None)
# (c) X1 已覆盖题对照（1.2.1.1-1 与 1.2.1.2-6）
dump_block('X1', CASES[8][1], {'1.2.1.1-1', '1.2.1.2-6'})

# (d) 修后逻辑模拟
def simulate(rel):
    path = ROOT + '/' + rel
    st = structure(path)
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    els = list(doc.find(q('body')))
    ptexts = {i: (ptext(el) if el.tag == q('p') else '') for i, el in enumerate(els)}
    items = st['items']
    cov = 0; nocov = []; legs = {}
    for qu in st['questions']:
        s_el = items[qu['start']]['el']
        e_el = items[qu['end']]['el'] if qu['end'] < len(items) else len(els)
        hit = False; used = ''
        for ci in range(s_el, e_el):
            p = els[ci]
            if tag(p) != 'p': continue
            t = ptexts[ci]
            if not t.translate(NORM).startswith('【答案】'): continue
            for r in p.iter(q('r')):
                txt = ''.join(x.text or '' for x in r.findall(q('t')))
                if txt and not CHIP_RE.fullmatch(txt) and \
                        (shd_fill(r.find(q('rPr'))) == FILL_CONTENT or deep_blue(r.find(q('rPr')))):
                    hit = True; used = '腿1值行run'; break
            if not hit:
                for el in p.iter():
                    if etree.QName(el).namespace == M and tag(el) in ('r', 'ctrlPr') and \
                            (shd_fill(el.find(q('rPr'))) == FILL_CONTENT or deep_blue(el.find(q('rPr')))):
                        hit = True; used = '腿2值行OMML'; break
            if not hit and '【知识点】' not in t.translate(NORM):
                cj = ci + 1
                while cj < e_el and tag(els[cj]) == 'p' and not ptexts[cj].strip():
                    cj += 1
                if cj < e_el and tag(els[cj]) == 'p':
                    for r in els[cj].iter(q('r')):
                        txt = ''.join(x.text or '' for x in r.findall(q('t')))
                        if txt and not CHIP_RE.fullmatch(txt) and not NUMDOT_RE.match(txt) \
                                and (shd_fill(r.find(q('rPr'))) == FILL_CONTENT
                                     or deep_blue(r.find(q('rPr')))):
                            hit = True; used = '腿3续值run'; break
                    if not hit:
                        for m_el in els[cj].iter():
                            if etree.QName(m_el).namespace == M and tag(m_el) in ('r', 'ctrlPr') and \
                                    (shd_fill(m_el.find(q('rPr'))) == FILL_CONTENT
                                     or deep_blue(m_el.find(q('rPr')))):
                                hit = True; used = '腿3续值OMML(新增)'; break
            break
        if hit:
            cov += 1; legs[used] = legs.get(used, 0) + 1
        else:
            nocov.append(qu['no'])
    return len(st['questions']), cov, nocov, legs

for code, rel in [('X1', CASES[8][1]), ('X2', CASES[9][1]), ('SM', CASES[10][1])]:
    n, cov, nocov, legs = simulate(rel)
    print('模拟修后 %s: %d/%d%s｜命中腿分布 %s' % (code, cov, n,
          ('' if not nocov else '｜未覆盖 %s' % nocov[:6]), legs))
