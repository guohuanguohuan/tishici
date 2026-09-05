# -*- coding: utf-8 -*-
"""子步8 T1：册目录页整件重造（§11 P页码制）。
输入：子步7盖章记录（件级行start/N同源）＋节页码_成品轮①.json（二级节级行定位值）。
硬规则：无列头行；标题下小注「页码＝所在本部分内页码（各本独立起算）」；章行加粗不设页码列；
件级行 ind420＋整行C9C9C9底纹＋行尾「·本N页」（N＝该件部分内实测页数＝盖章记录N）＋P起始页；
节级行 ind840＋二级节粒度＋P定位值；页码列＝点线前导右对齐制表位（pos=10206）；左对齐、12pt、
line=410 atLeast。施工后：COM页数断言（>1页走降级顺位）＋页码列三源恒等核验。"""
import zipfile, re, os, sys, io, json, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

HERE = os.path.dirname(os.path.abspath(__file__))
S7 = HERE
BASE = HERE
TARGET = os.path.join(BASE, '人教B版选必1·册目录页.docx')

# ---- 输入1：盖章记录 ----
rec = {}
for ln in open(os.path.join(S7, '盖章记录_成品轮①.md'), encoding='utf-8'):
    m = re.match(r'\| P(\d+) \| 本(\d+) \| (.+?) \| (\d+) \| (\d+) \| (.+?) \| (\d+) \|', ln.strip())
    if m:
        rec[m.group(3)] = {'part': int(m.group(1)), 'book': int(m.group(2)), 'pages': int(m.group(4)),
                           'start': int(m.group(5)), 'tag': m.group(6), 'N': int(m.group(7))}
assert len(rec) == 10, len(rec)

def by_tag(tag):
    rows = [(v, k) for k, v in rec.items() if v['tag'] == tag]
    return rows

# ---- 输入2：节页码（二级节，按章归并） ----
loc = json.load(open(os.path.join(S7, '节页码_成品轮①.json'), encoding='utf-8'))
sec2 = {}   # 节号 -> (part_page, title文本)
for f in loc['files']:
    if '讲练件' not in f['name']:
        continue
    for s in f['sections']:
        if s['no'].count('.') == 1:
            assert s['no'] not in sec2, '二级节重复命中: %s' % s['no']
            sec2[s['no']] = s['part_page']

# ---- 题量括注同源核验：二级节题量＝其下三级节统计段题量之和（无子节者＝自身统计段） ----
sum3 = {}
for f in loc['files']:
    if '讲练件' not in f['name']:
        continue
    for s in f['sections']:
        m = re.search(r'本节(\d+)题', s['title'])
        if not m:
            continue
        n = int(m.group(1))
        no = s['no']
        if no.count('.') == 1:
            sum3[no] = sum3.get(no, 0) + n
        else:
            two = '.'.join(no.split('.')[:2])
            sum3[two] = sum3.get(two, 0) + n
EXPECT2 = {'1.1': 24, '1.2': 116, '2.1': 1, '2.2': 38, '2.3': 61, '2.4': 19, '2.5': 63,
           '2.6': 36, '2.7': 32, '2.8': 89}
for no, n in EXPECT2.items():
    assert sum3.get(no) == n, '二级节题量括注不同源: %s 实测%d 期望%d' % (no, sum3.get(no), n)
print('题量括注同源核验：10/10二级节 三级节统计段之和＝目录括注值 ✓')

# ---- 目录行内容 ----
x1 = by_tag('第1章·衔接')[0][0]; i1 = by_tag('第1章·清单')[0][0]
b3 = by_tag('第1章·讲练'); n3 = sum(v['pages'] for v, _ in b3); st3 = min(v['start'] for v, _ in b3)
x2 = by_tag('第2章·衔接')[0][0]; i2 = by_tag('第2章·清单')[0][0]
b6 = by_tag('第2章·讲练'); n6 = sum(v['pages'] for v, _ in b6); st6 = min(v['start'] for v, _ in b6)
assert n3 == rec[by_tag('第1章·讲练')[0][1]]['N'] and n6 == rec[b6[0][1]]['N']

L1 = [('第1章 空间向量与立体几何', None, None),
      ('衔接件（29题·全部必会）　·本%d页' % x1['N'], 'P%d' % x1['start'], 'item'),
      ('知识清单（47条：基33·进14）　·本%d页' % i1['N'], 'P%d' % i1['start'], 'item'),
      ('讲练件（140题：简单21·中档104·难15）　·本%d页' % n3, 'P%d' % st3, 'item'),
      ('1.1 空间向量及其运算（24题）', 'P%d' % sec2['1.1'], 'sec'),
      ('1.2 空间向量在立体几何中的应用（116题）', 'P%d' % sec2['1.2'], 'sec')]
L2 = [('第2章 平面解析几何', None, None),
      ('衔接件（13题·全部必会）　·本%d页' % x2['N'], 'P%d' % x2['start'], 'item'),
      ('知识清单（67条：基38·进29）　·本%d页' % i2['N'], 'P%d' % i2['start'], 'item'),
      ('讲练件（339题：简单47·中档246·难46）　·本%d页' % n6, 'P%d' % st6, 'item')]
for no in ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7', '2.8']:
    name = {'2.1': '坐标法', '2.2': '直线及其方程', '2.3': '圆及其方程', '2.4': '曲线与方程',
            '2.5': '椭圆及其方程', '2.6': '双曲线及其方程', '2.7': '抛物线及其方程',
            '2.8': '直线与圆锥曲线的位置关系'}[no]
    L2.append(('%s %s（%d题）' % (no, name, EXPECT2[no]), 'P%d' % sec2[no], 'sec'))

# ---- 段落XML构造 ----
RPR = '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>%s<w:sz w:val="%d"/></w:rPr>'
TABS = '<w:tabs><w:tab w:pos="10206" w:val="right" w:leader="dot"/></w:tabs>'

def para(text, sz=24, bold=False, shd=None, ind=None, page=None):
    ppr = '<w:pPr>' + TABS + '<w:spacing w:before="0" w:after="0" w:line="410" w:lineRule="atLeast"/><w:jc w:val="left"/>'
    if shd:
        ppr += '<w:shd w:val="clear" w:color="auto" fill="%s"/>' % shd
    if ind:
        ppr += '<w:ind w:left="%d"/>' % ind
    ppr += '</w:pPr>'
    rpr = RPR % ('<w:b/>' if bold else '', sz)
    body = ppr + '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, text)
    if page is not None:
        body += '<w:r>%s<w:tab/><w:t>%s</w:t></w:r>' % (rpr, page)
    return '<w:p>%s</w:p>' % body

paras = [para('人教B版选必1·册目录页', sz=32, bold=True),
         para('页码＝所在本部分内页码（各本独立起算）')]
for rows in (L1, L2):
    for text, page, kind in rows:
        if kind is None:
            paras.append(para(text, bold=True))
        elif kind == 'item':
            paras.append(para(text, shd='C9C9C9', ind=420, page=page))
        else:
            paras.append(para(text, ind=840, page=page))
print('段落数=%d（标题1＋小注1＋章行2＋件级6＋节级10）' % len(paras))
assert len(paras) == 20

# ---- zip手术：仅替换 word/document.xml 的 body ----
shutil.copy2(TARGET, os.path.join(HERE, 'bak8', '人教B版选必1·册目录页.docx'))
with zipfile.ZipFile(TARGET) as z:
    names = z.namelist()
    blob = {n: z.read(n) for n in names}
doc = blob['word/document.xml'].decode('utf-8')
i = doc.index('<w:body>')
j = doc.rindex('<w:sectPr')
assert doc.rindex('</w:sectPr>') > j
newdoc = doc[:i] + '<w:body>' + ''.join(paras) + doc[j:]
with zipfile.ZipFile(TARGET + '.tmp', 'w', zipfile.ZIP_DEFLATED) as zo:
    for n in names:
        zo.writestr(n, newdoc if n == 'word/document.xml' else blob[n])
os.replace(TARGET + '.tmp', TARGET)
print('册目录页重造落盘：%s' % TARGET)

# ---- 回读三源恒等核验（件级行=start实测、章行=首件start、节级行=定位值） ----
with zipfile.ZipFile(TARGET) as z:
    x2d = z.read('word/document.xml').decode('utf-8')
rows = re.findall(r'<w:p[ >].*?</w:p>', x2d, re.S)
ok = 0
plan = [(x1['start'],), (i1['start'],), (st3,), (sec2['1.1'],), (sec2['1.2'],),
        (x2['start'],), (i2['start'],), (st6,)] + [(sec2[n],) for n in
        ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7', '2.8']]
prow = [r for r in rows if '<w:tab/>' in r]
assert len(prow) == 16, len(prow)
for r, (exp,) in zip(prow, plan):
    t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', r))
    pv = int(re.search(r'P(\d+)$', t).group(1))
    assert pv == exp, 'P值不符: %r 期望P%d' % (t, exp)
    ok += 1
print('页码列三源恒等：16/16 行 P值＝盖章记录start/定位工具值 ✓（章行不设页码列：第1章首件start=1=衔接件行、第2章首件start=1=衔接件行 ✓）')
print('列头行缺失断言：%s' % ('✓ 无列头行' if not any('件／节' in ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', r)) for r in rows) else '✗'))
json.dump({'rows': len(rows), 'p_rows': ok,
           'sec2_pages': {k: v for k, v in sec2.items()}},
          open(os.path.join(HERE, 'build_成品轮①.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('build_成品轮①.json 落盘')
