# -*- coding: utf-8 -*-
"""W-E卷92 步骤7后：导航表规整＋同源恒等断言（N11合并后重算）
规整面：表内段落9pt(18半点)+line=280 atLeast+jc=left｜表头tcPr C9C9C9+加粗｜边框细实线+表头下加重线
恒等：nav节行(本件8叶节)＝节标题行统计段｜nav合计＝全件统计行｜本件8节题量和＝92｜区间1—339连续"""
import zipfile, re, sys, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def w(t): return '{%s}%s' % (W, t)

path = 'E卷92-工作副本.docx'
with zipfile.ZipFile(path) as z:
    parts = {n: z.read(n) for n in z.namelist()}
doc = etree.fromstring(parts['word/document.xml'])
body = doc.find(w('body'))

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag in (w('t'), '{http://schemas.openxmlformats.org/officeDocument/2006/math}t'))

# ---- 1. 定位导航表与全件统计行 ----
tbl = None
for el in body:
    if isinstance(el.tag, str) and el.tag == w('tbl'):
        tbl = el; break
assert tbl is not None, '未找到导航表'
full_stat = None
for el in body:
    if isinstance(el.tag, str) and el.tag == w('p') and lin(el).startswith('全件'):
        full_stat = lin(el); break
assert full_stat and re.match(r'^全件(\d+)题：简单(\d+)｜中档(\d+)｜难(\d+)$', full_stat), '全件统计行形态异常: %r' % full_stat
m = re.match(r'^全件(\d+)题：简单(\d+)｜中档(\d+)｜难(\d+)$', full_stat)
FULL = (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))

# ---- 2. 提取节标题行统计段（N11合并后形态：标题行内「本节N题：…」） ----
sect_stats = {}
for el in body:
    if not (isinstance(el.tag, str) and el.tag == w('p')): continue
    t = lin(el)
    mm = re.match(r'^(\d+(?:\.\d+)+)\s.*（第(\d+)—(\d+)题）\u3000?本节(\d+)题：简单(\d+)｜中档(\d+)｜难(\d+)', t)
    if mm:
        sect_stats[mm.group(1)] = dict(rng=(int(mm.group(2)), int(mm.group(3))), n=int(mm.group(4)),
                                       s=int(mm.group(5)), m=int(mm.group(6)), h=int(mm.group(7)))
assert len(sect_stats) == 8, '节标题行统计段数=%d≠8' % len(sect_stats)

# ---- 3. 提取导航表行 ----
rows = tbl.findall(w('tr'))
def rowcells(tr):
    return [tc for tc in tr.findall(w('tc'))]
nav = []
for ri, tr in enumerate(rows):
    cells = rowcells(tr)
    nav.append([lin(c) for c in cells])
head = nav[0]
assert '节名' in head[0] and '题型组数' in head[-1], '表头形态异常: %r' % head
total_row = nav[-1]
assert total_row[0].startswith('合计'), '末行非合计: %r' % total_row[0]
data_rows = nav[1:-1]

# ---- 4. 同源恒等断言 ----
report = []
ok = True
# 4a 本件8叶节：nav行 vs 节标题行统计段
nav_in_file = {}
for r in data_rows:
    secname = r[0].strip()
    m2 = re.match(r'^([\d.]+)\s*(.+)$', secname)
    if not m2: continue
    num = m2.group(1)
    rng = re.match(r'^第(\d+)—(\d+)题$', r[1].strip())
    cnt = re.match(r'^(\d+)$', r[2].strip())
    smh = re.match(r'^简单(\d+)/中档(\d+)/难(\d+)$', r[3].strip())
    grp = re.match(r'^(\d+)$', r[4].strip())
    assert rng and cnt and smh and grp, 'nav行形态异常: %r' % r
    ent = dict(name=secname, rng=(int(rng.group(1)), int(rng.group(2))), n=int(cnt.group(1)),
               s=int(smh.group(1)), m=int(smh.group(2)), h=int(smh.group(3)), grp=int(grp.group(1)))
    if num in sect_stats:
        nav_in_file[num] = ent
for num, ss in sect_stats.items():
    nv = nav_in_file.get(num)
    if nv is None:
        ok = False; report.append('FAIL nav缺本件节 %s' % num); continue
    same = (nv['rng'] == ss['rng'] and nv['n'] == ss['n'] and nv['s'] == ss['s'] and nv['m'] == ss['m'] and nv['h'] == ss['h'])
    report.append('%s nav=%s vs 节标题行=%s -> %s' % (num, (nv['rng'], nv['n'], nv['s'], nv['m'], nv['h']), (ss['rng'], ss['n'], ss['s'], ss['m'], ss['h']), 'PASS' if same else 'FAIL'))
    if not same: ok = False
# 4b 合计行 vs 全件统计行
mt = re.match(r'^第?(\d+)—(\d+)题?$', total_row[1].strip())
mc = re.match(r'^(\d+)$', total_row[2].strip())
ms = re.match(r'^简单(\d+)/中档(\d+)/难(\d+)$', total_row[3].strip())
assert mt and mc and ms, '合计行形态异常: %r' % total_row
TOT = (int(mc.group(1)), int(ms.group(1)), int(ms.group(2)), int(ms.group(3)))
report.append('合计行(n/s/m/h)=%s vs 全件统计行=%s -> %s' % (TOT, FULL, 'PASS' if TOT == FULL else 'FAIL'))
if TOT != FULL: ok = False
report.append('合计区间=%s—%s -> %s' % (mt.group(1), mt.group(2), 'PASS' if (int(mt.group(1)), int(mt.group(2))) == (1, FULL[0]) else 'FAIL'))
if (int(mt.group(1)), int(mt.group(2))) != (1, FULL[0]): ok = False
# 4c 本件8节题量和=92；nav全表题量和=合计
sum8 = sum(ss['n'] for ss in sect_stats.values())
report.append('本件8节题量和=%d -> %s' % (sum8, 'PASS' if sum8 == 92 else 'FAIL'))
if sum8 != 92: ok = False
sum_all = sum(int(re.match(r'^(\d+)$', r[2].strip()).group(1)) for r in data_rows)
report.append('nav全表(%d节)题量和=%d vs 合计=%d -> %s' % (len(data_rows), sum_all, TOT[0], 'PASS' if sum_all == TOT[0] else 'FAIL'))
if sum_all != TOT[0]: ok = False
# 4d nav区间连续1—339
spans = sorted((int(re.match(r'^第(\d+)—(\d+)题$', r[1].strip()).group(1)),
                int(re.match(r'^第(\d+)—(\d+)题$', r[1].strip()).group(2))) for r in data_rows)
contig = spans[0][0] == 1 and spans[-1][1] == FULL[0] and all(spans[i][1] + 1 == spans[i+1][0] for i in range(len(spans)-1))
report.append('nav区间连续1—%d -> %s' % (FULL[0], 'PASS' if contig else 'FAIL'))
if not contig: ok = False
# 4e 题型组数列合计 vs 本件题型标题数（62）＋他件（F/G/H在其件，本件只核本件节行组数和≥62对应）
grp_in_file = sum(nav_in_file[num]['grp'] for num in nav_in_file)
report.append('本件8节题型组数和=%d（本件题型标题62＋讲部6＝68组结构）' % grp_in_file)

# ---- 5. 版式规整（表内段落18半点+280atLeast+jc=left；表头tcPr C9C9C9+run加粗；边框细实线+表头下加重线） ----
fix = {'sz18补': 0, 'line280补': 0, 'jc_left补': 0, '表头tcPr灰补': 0, '表头run补粗': 0, '表头加重线': 0, '表格细实线': 0}
for ri, tr in enumerate(rows):
    for tc in tr.findall(w('tc')):
        if ri == 0:
            tcPr = tc.find(w('tcPr'))
            shd = tcPr.find(w('shd')) if tcPr is not None else None
            if shd is None or shd.get(w('fill')) != 'C9C9C9':
                if tcPr is None:
                    tcPr = etree.SubElement(tc, w('tcPr')); tc.remove(tcPr); tc.insert(0, tcPr)
                shd = etree.SubElement(tcPr, w('shd'))
                shd.set(w('val'), 'clear'); shd.set(w('color'), 'auto'); shd.set(w('fill'), 'C9C9C9')
                fix['表头tcPr灰补'] += 1
        for p in tc.findall(w('p')):
            pPr = p.find(w('pPr'))
            if pPr is None:
                pPr = etree.Element(w('pPr')); p.insert(0, pPr)
            sp = pPr.find(w('spacing'))
            if sp is None:
                sp = etree.SubElement(pPr, w('spacing'))
                sp.set(w('before'), '0'); sp.set(w('after'), '0')
                sp.set(w('line'), '280'); sp.set(w('lineRule'), 'atLeast')
                fix['line280补'] += 1
            else:
                if sp.get(w('line')) != '280' or sp.get(w('lineRule')) != 'atLeast':
                    sp.set(w('line'), '280'); sp.set(w('lineRule'), 'atLeast'); fix['line280补'] += 1
                if sp.get(w('before') or '0') != '0': sp.set(w('before'), '0')
                if sp.get(w('after') or '0') != '0': sp.set(w('after'), '0')
            jc = pPr.find(w('jc'))
            if jc is None:
                jc = etree.SubElement(pPr, w('jc')); jc.set(w('val'), 'left'); fix['jc_left补'] += 1
            elif jc.get(w('val')) != 'left':
                jc.set(w('val'), 'left'); fix['jc_left补'] += 1
            for r in p.findall('.//' + w('r')):
                rPr = r.find(w('rPr'))
                if rPr is None:
                    rPr = etree.Element(w('rPr')); r.insert(0, rPr)
                szel = rPr.find(w('sz'))
                if szel is None:
                    szel = etree.SubElement(rPr, w('sz')); szel.set(w('val'), '18'); fix['sz18补'] += 1
                elif szel.get(w('val')) != '18':
                    szel.set(w('val'), '18'); fix['sz18补'] += 1
                szcs = rPr.find(w('szCs'))
                if szcs is None:
                    szcs = etree.SubElement(rPr, w('szCs')); szcs.set(w('val'), '18')
                if ri == 0:
                    b = rPr.find(w('b'))
                    if b is None:
                        b = etree.SubElement(rPr, w('b')); fix['表头run补粗'] += 1
# 表格边框：tblBorders 细实线 single sz=4；首行下加重 sz=12
tblPr = tbl.find(w('tblPr'))
borders = tblPr.find(w('tblBorders'))
if borders is None:
    borders = etree.SubElement(tblPr, w('tblBorders'))
BORD = [('top', '4'), ('left', '4'), ('bottom', '4'), ('right', '4'), ('insideH', '4'), ('insideV', '4')]
for side, szv in BORD:
    be = borders.find(w(side))
    if be is None:
        be = etree.SubElement(borders, w(side)); fix['表格细实线'] += 1
    be.set(w('val'), 'single'); be.set(w('sz'), szv); be.set(w('space'), '0'); be.set(w('color'), 'auto')
tr0 = rows[0]
trPr0 = tr0.find(w('trPr'))
first_tc = tr0.findall(w('tc'))[0]
tcPr0 = first_tc.find(w('tcPr'))
tcB = tcPr0.find(w('tcBorders')) if tcPr0 is not None else None
if tcB is None:
    tcB = etree.SubElement(tcPr0, w('tcBorders'))
bb = tcB.find(w('bottom'))
if bb is None:
    bb = etree.SubElement(tcB, w('bottom'))
if bb.get(w('sz') or '0') != '12':
    bb.set(w('val'), 'single'); bb.set(w('sz'), '12'); bb.set(w('space'), '0'); bb.set(w('color'), 'auto')
    fix['表头下加重线'] += 1

parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = path + '.navtmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n, b in parts.items():
        zo.writestr(n, b)
for i2 in range(12):
    try:
        os.replace(tmp, path); break
    except PermissionError:
        time.sleep(5)
with open('登记-导航表规整.md', 'w', encoding='utf-8') as f:
    f.write('# 导航表规整＋同源恒等断言（E卷92，N11合并后重算）\n\n')
    f.write('全件统计行：%s\n\n' % full_stat)
    f.write('## 恒等断言（%s）\n\n' % ('全PASS' if ok else '存在FAIL'))
    for r in report:
        f.write('- %s\n' % r)
    f.write('\n## 版式规整动作计数\n\n%s\n' % json.dumps(fix, ensure_ascii=False, indent=1))
print(json.dumps({'恒等断言': '全PASS' if ok else 'FAIL', 'fix': fix, 'rows': len(rows), 'data_rows': len(data_rows)}, ensure_ascii=False))
for r in report:
    print(' ', r)
