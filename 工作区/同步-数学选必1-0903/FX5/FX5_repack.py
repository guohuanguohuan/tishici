# -*- coding: utf-8 -*-
"""FX5-G: repack docx (only word/document.xml replaced; other entries byte-identical) + XML verify"""
import zipfile, os, shutil, re, hashlib
from lxml import etree

SRC_DOCX = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'
TMP = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G'
OUT = os.path.join(TMP, 'G_fixed.docx')
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def w(t): return f'{{{W}}}{t}'
def m(t): return f'{{{M}}}{t}'

new_doc = open(os.path.join(TMP, 'word', 'document.xml'), 'rb').read()
with zipfile.ZipFile(SRC_DOCX) as zin:
    names = zin.namelist()
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            if n == 'word/document.xml':
                zout.writestr(n, new_doc)
            else:
                zout.writestr(n, zin.read(n))
print('repacked:', OUT, os.path.getsize(OUT), 'bytes')

# ---------- XML verification ----------
tree = etree.parse(os.path.join(TMP, 'word', 'document.xml'))
root = tree.getroot()
body = root.find(w('body'))

print('\n=== sectPr assertions ===')
sects = root.findall(f'.//{w("sectPr")}')
assert len(sects) == 1, f'sectPr count {len(sects)}'
s = sects[0]
assert s.getparent() is body
kids = [c.tag.split('}')[1] for c in s]
print('sectPr children order:', kids)
assert kids == ['headerReference', 'footerReference', 'pgSz', 'pgMar', 'pgNumType', 'cols', 'docGrid'], kids
href = s.find(w('headerReference')); fref = s.find(w('footerReference'))
assert href.get(f'{{{R}}}id') == 'rId49' and fref.get(f'{{{R}}}id') == 'rId50'
assert s.find(w('pgNumType')).get(w('start')) == '103'
cols = s.find(w('cols'))
assert (cols.get(w('num')), cols.get(w('space')), cols.get(w('sep'))) == ('2', '425', '1')
pgsz = s.find(w('pgSz')); assert (pgsz.get(w('w')), pgsz.get(w('h'))) == ('11906', '16838')
pgm = s.find(w('pgMar'))
assert all(pgm.get(w(k)) == '850' for k in ('top', 'bottom', 'left', 'right', 'footer')) and pgm.get(w('header')) == '283'
print('sectPr: 1个/refs各1(rId49,rId50)/start=103/cols=2-425-1/A4/850边距 ✓')

print('\n=== 题号68序列 ===')
paras = body.findall(w('p'))
pat = re.compile(r'^(\d+(?:\.\d+){3,}-(\d+))．')  # 题号≥4段（条目号2.7.2-1为3段不入计）
seen = []
for i, p in enumerate(paras):
    txt = ''.join(t.text or '' for t in p.iter(w('t')))
    mm = pat.match(txt)
    if mm:
        seen.append((i, mm.group(1)))
assert len(seen) == 68, f'题块 {len(seen)}'
from collections import OrderedDict, Counter
by_sec = OrderedDict()
for i, qn in seen:
    full, num = qn.rsplit('-', 1)
    sec = '.'.join(full.split('.')[:3])  # 教材节 = 前三段
    by_sec.setdefault(sec, []).append(int(num))
for sec, nums in by_sec.items():
    assert nums == list(range(1, len(nums) + 1)), f'{sec} not consecutive: {nums}'
assert {k: len(v) for k, v in by_sec.items()} == {'2.6.1': 16, '2.6.2': 20, '2.7.1': 14, '2.7.2': 18}
print('题块68 ✓ 节内序列：', {k: f'1..{len(v)}' for k, v in by_sec.items()})

print('\n=== 三向恒等（统计段） ===')
# 题型标题行末统计段
grp = re.compile(r'　(\d+)题：')
type_sum = 0; type_cnt = 0
for p in paras:
    txt = ''.join(t.text or '' for t in p.iter(w('t')))
    if txt.startswith('2.') and '　' in txt and grp.search(txt):
        # C6D4E3 shaded title line with 统计段
        shd = p.find(f'{w("pPr")}/{w("shd")}')
        if shd is not None and shd.get(w('fill')) == 'C6D4E3':
            type_sum += int(grp.search(txt).group(1)); type_cnt += 1
sec_sum = 0
secpat = re.compile(r'本节(\d+)题')
for p in paras:
    txt = ''.join(t.text or '' for t in p.iter(w('t')))
    shd = p.find(f'{w("pPr")}/{w("shd")}')
    if shd is not None and shd.get(w('fill')) == 'ADC2DA':
        mm = secpat.search(txt)
        if mm:
            sec_sum += int(mm.group(1))
print(f'题型组统计段: {type_cnt}组 Σ={type_sum}；节标题统计段Σ={sec_sum}')
assert type_sum == sec_sum == 68 and type_cnt == 50, (type_cnt, type_sum, sec_sum)

print('\n=== 选项分隔终态 ===')
n_tab = sum(len(r.findall(w('tab'))) for p in body.findall(w('p')) for r in p.findall(w('r')))
n_tabc = len(root.findall(f'.//{w("tabs")}'))
print(f'run级w:tab={n_tab} pPr w:tabs容器={n_tabc}')
assert n_tab == 0 and n_tabc == 0
# all option paras now ；-separated (within-line): check gap analysis on option marker letters
bad = []
for i, p in enumerate(paras):
    txts = [t.text or '' for t in p.iter(w('t'))]
    joined = ''.join(txts)
    if 'A．' in joined and '故选' not in joined and '可判断' not in joined and '判断' not in joined[:4]:
        for mm in re.finditer(r'([A-D])．', joined):
            j = mm.start()
            if mm.group(1) != 'A':
                prev = joined[:j]
                # last non-space char before marker must be ；or ）(answer slot) etc.
                prev_trim = prev.rstrip('\xa0 ）　')
                if not prev_trim.endswith(('；', '。', '：', '）', '?', '？')) and prev_trim:
                    bad.append((i, joined[max(0, j-20):j+5]))
print('选项前置分隔异常:', bad if bad else '0')
assert not bad

print('\n=== sz21 / 编注签名 ===')
n21 = sum(1 for rPr in root.findall(f'.//{w("rPr")}') for el in rPr
          if el.tag in (w('sz'), w('szCs')) and el.get(w('val')) == '21')
assert n21 == 0
print('sz21 = 0 ✓')
sig = re.compile(r'[√½¼¾²³¹∠⊥∈∩∪≈≤≥≠±⋅·×₀-₉]|_')
nbian = 0
for i, p in enumerate(paras):
    full = ''.join(t.text or '' for t in p.iter(w('t'))) + '|' + ''.join(t.text or '' for t in p.iter(m('t')))
    if '【编注】' not in full:
        continue
    wt = ''.join(t.text or '' for t in p.iter(w('t')))
    if sig.search(wt):
        nbian += 1
        print(f'  residual p#{i}: {wt[:60]!r}')
assert nbian == 0
print('编注段 w:t层签名 = 0 ✓')

print('\n=== 空格卫生终态（math-aware即时邻接）===')
nsp = 0
nfx = 0
for i, p in enumerate(paras):
    ev = []
    for node in p.iter():
        if node.tag == w('t'):
            ev.append(node)
        elif node.tag == m('t'):
            ev.append(node)
        elif node.tag == w('drawing'):
            ev.append(node)
    for j, node in enumerate(ev):
        if node.tag == w('t') and node.text and node.text.strip() == '' and ' ' in node.text:
            nk = None
            for k in range(j + 1, len(ev)):
                t2 = ev[k]
                if t2.tag == w('t') and (t2.text or '') == '':
                    continue
                nk = t2; break
            if nk is not None and nk.tag == w('t') and nk.text and nk.text[0] in '，。；：？！、）．':
                nsp += 1
                print(f'  residual punct-space p#{i}')
            elif nk is not None and nk.tag != w('t'):
                nfx += 1  # formula-preceding space（FX3登记观察族，保留）
assert nsp == 0
print(f'标点前空格 = 0 ✓（公式前孤立空格保留{ nfx }处——FX3同族登记，非本slice对象）')

print('\n=== 首段结构 ===')
p1 = paras[0]
st = p1.find(f'{w("pPr")}/{w("pStyle")}')
t1 = ''.join(t.text or '' for t in p1.iter(w('t')))
print(f'新首段: style={st.get(w("val")) if st is not None else None} text={t1!r}')
assert st is not None and st.get(w('val')) == 'JieMingMao' and t1 == '2.6 双曲线及其方程'

print('\nALL XML CHECKS PASS')
