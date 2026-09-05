# -*- coding: utf-8 -*-
"""②E_02_册目录重造.py — ②-E 册目录页整件重造（照 成品轮①/册目录页重造_成品轮①.py 范式，②-E 路径适配）。
用法: python ②E_02_册目录重造.py <盖章记录md> <节页码json> <build输出json>
输入：盖章记录（件级行start/N同源）＋节页码json（二级节级行定位值）。
硬规则与段落构造同范式：无列头行；小注；章行加粗无页码列；件级行 ind420＋C9C9C9＋·本N页＋P起始页；
节级行 ind840＋P定位值；点线前导右对齐制表位 pos=10206。施工后：页码列三源恒等核验（16行）。"""
import zipfile, re, os, sys, io, json, shutil
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(HERE, '副本_②E')
REC_PATH, LOC_PATH, BUILD_OUT = sys.argv[1], sys.argv[2], sys.argv[3]
TARGET = os.path.join(DST, '人教B版选必1·册目录页.docx')

rec = {}
for ln in open(REC_PATH, encoding='utf-8'):
    m = re.match(r'\| P(\d+) \| 本(\d+) \| (.+?) \| (\d+) \| (\d+) \| (.+?) \| (\d+) \|', ln.strip())
    if m:
        rec[m.group(3)] = {'part': int(m.group(1)), 'book': int(m.group(2)), 'pages': int(m.group(4)),
                           'start': int(m.group(5)), 'tag': m.group(6), 'N': int(m.group(7))}
assert len(rec) == 10, len(rec)

def by_tag(tag):
    return [(v, k) for k, v in rec.items() if v['tag'] == tag]

loc = json.load(open(LOC_PATH, encoding='utf-8'))
sec2 = {}
for f in loc['files']:
    if '讲练件' not in f['name']:
        continue
    for s in f['sections']:
        if s['no'].count('.') == 1:
            assert s['no'] not in sec2, '二级节重复命中: %s' % s['no']
            sec2[s['no']] = s['part_page']

# ---- 题量括注同源核验（②-E 改源：T3 统计段独立成行后，节标题行不再携带「本节N题」——
#      改从 讲练件 document.xml 段序直接重建：节号段之后最近的「本节N题」统计段（独立行或行内）归入该节） ----
WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
RE_SECHEAD = re.compile(r'^(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)[\s\u3000]+(\S.*)?$')
RE_SECSTAT = re.compile(r'本节(\d+)题')
sum3 = {}
for f in loc['files']:
    if '讲练件' not in f['name']:
        continue
    nm = f['name'] if f['name'].lower().endswith('.docx') else f['name'] + '.docx'
    z = zipfile.ZipFile(os.path.join(DST, nm))
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    last = None
    for p in root.iter('{%s}p' % WNS):
        t = ''.join(tt.text or '' for tt in p.iter('{%s}t' % WNS)).strip()
        if not t:
            continue
        mh = RE_SECHEAD.match(t)
        if mh:
            last = mh.group(1)
        ms = RE_SECSTAT.search(t)
        if ms and last:
            n = int(ms.group(1))
            no = last
            if no.count('.') == 1:
                sum3[no] = sum3.get(no, 0) + n
            else:
                two = '.'.join(no.split('.')[:2])
                sum3[two] = sum3.get(two, 0) + n
            last = None          # 每个统计段只归一次（防题型标题/重复行误归）
EXPECT2 = {'1.1': 24, '1.2': 116, '2.1': 1, '2.2': 38, '2.3': 61, '2.4': 19, '2.5': 63,
           '2.6': 36, '2.7': 32, '2.8': 89}
for no, n in EXPECT2.items():
    assert sum3.get(no) == n, '二级节题量括注不同源: %s 实测%d 期望%d' % (no, sum3.get(no), n)
print('题量括注同源核验：10/10二级节 讲练件段序统计段之和＝目录括注值 ✓（②-E 段序重建口径）')

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

bakdir = os.path.join(DST, 'bak_TOC')
os.makedirs(bakdir, exist_ok=True)
if not os.path.exists(os.path.join(bakdir, '人教B版选必1·册目录页.docx')):
    shutil.copy2(TARGET, os.path.join(bakdir, '人教B版选必1·册目录页.docx'))
    print('已留 bak_TOC（入场原态）')
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

with zipfile.ZipFile(TARGET) as z:
    x2d = z.read('word/document.xml').decode('utf-8')
rows = re.findall(r'<w:p[ >].*?</w:p>', x2d, re.S)
plan = [(x1['start'],), (i1['start'],), (st3,), (sec2['1.1'],), (sec2['1.2'],),
        (x2['start'],), (i2['start'],), (st6,)] + [(sec2[n],) for n in
        ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7', '2.8']]
prow = [r for r in rows if '<w:tab/>' in r]
assert len(prow) == 16, len(prow)
ok = 0
for r, (exp,) in zip(prow, plan):
    t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', r))
    pv = int(re.search(r'P(\d+)$', t).group(1))
    assert pv == exp, 'P值不符: %r 期望P%d' % (t, exp)
    ok += 1
print('页码列三源恒等：16/16 行 P值＝盖章记录start/定位工具值 ✓')
print('列头行缺失断言：%s' % ('✓ 无列头行' if not any('件／节' in ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', r)) for r in rows) else '✗'))
json.dump({'record': os.path.basename(REC_PATH), 'loc': os.path.basename(LOC_PATH),
           'rows': len(rows), 'p_rows': ok,
           'sec2_pages': {k: v for k, v in sec2.items()},
           'items': {'x1': x1, 'i1': i1, 'n3': n3, 'st3': st3, 'x2': x2, 'i2': i2, 'n6': n6, 'st6': st6}},
          open(BUILD_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('build json 落盘：%s' % BUILD_OUT)
