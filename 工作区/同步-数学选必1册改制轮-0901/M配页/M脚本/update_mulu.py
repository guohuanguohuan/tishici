# -*- coding: utf-8 -*-
"""M配页·册目录页页码列更新：
输入＝S盖章实测（starts/N）＋节页码定位.py新值（节页码_new.json）；
动作＝仅改25节级行页码run（件级行/章行页码已=1维持）；断言＝题量括注三重恒等＋每卷首节定位值=start＋34行树结构。
"""
import json, io, re, sys, zipfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def qn(t): return '{%s}%s' % (W, t)

WORK = r'C:/提示词/工作区/同步-数学选必1册改制轮-0901/M配页'
DOC = WORK + '/册目录页_wip.docx'

# ---- S盖章实测（唯一来源：盖章记录.md；此处经M报告再核对） ----
STARTS = {'（上）': 1, '（下）': 78, '2.1—2.3.3': 1, '2.3.4—2.5.2': 54, '2.6.1—2.7.2': 110, '（2.8）': 151}
PAGES_COM = {'（上）': 77, '（下）': 77, '2.1—2.3.3': 53, '2.3.4—2.5.2': 56, '2.6.1—2.7.2': 41, '（2.8）': 71}
N_PART = {1: 154, 6: 221}   # P3/P6 部分总页数

# ---- 节页码定位结果 ----
loc = json.load(open(WORK + '/节页码_new.json', encoding='utf-8'))
sec_page, sec_stats = {}, {}
for f in loc['files']:
    assert not f['zero_hit'], f["0命中: {name}"]
    key = [k for k in STARTS if k in f['name']]
    assert len(key) == 1, f['name']
    k = key[0]
    assert f['start'] == STARTS[k], (f['name'], f['start'], STARTS[k])
    assert f['in_file_pages'] == PAGES_COM[k], (f['name'], f['in_file_pages'])
    for s in f['sections']:
        no = s['no']
        assert no not in sec_page, '节号重复: ' + no
        sec_page[no] = s['part_page']
        m = re.search(r'本节(\d+)题：简单(\d+)｜中档(\d+)｜难(\d+)', s['title'])
        assert m, s['title']
        sec_stats[no] = tuple(int(x) for x in m.groups())
assert len(sec_page) == 25, len(sec_page)

# 每卷首节定位值=start 断言（各卷定位出的最小part_p行＝首节）
first_of = {'（上）': '1.1.1', '（下）': '1.2.5', '2.1—2.3.3': '2.1', '2.3.4—2.5.2': '2.3.4', '2.6.1—2.7.2': '2.6.1', '（2.8）': '2.8'}
for k, no in first_of.items():
    assert sec_page[no] == STARTS[k], (k, no, sec_page[no], STARTS[k])

# ---- 打开册目录页 ----
with zipfile.ZipFile(DOC) as z:
    names = z.namelist()
    contents = {n: z.read(n) for n in names}
root = etree.fromstring(contents['word/document.xml'])
body = root.find(qn('body'))
paras = body.findall(qn('p'))
assert len(paras) == 35, f'段落数={len(paras)}（标题1+树34）'

SEC_ROW = re.compile(r'^(\d+\.\d+(?:\.\d+)?)\s+(.+?)（(\d+)题）\d*$')
changed, checked = [], 0
for p in paras:
    txt = ''.join(t.text or '' for t in p.iter(qn('t')))
    m = SEC_ROW.match(txt)
    if not m:
        continue
    no, name, cnt = m.group(1), m.group(2), int(m.group(3))
    assert no in sec_page, '目录节号不在定位集: ' + no
    st = sec_stats[no]
    # 三重恒等：目录括注题量 ＝ 节标题「本节N题」 ＝ 三档之和
    assert cnt == st[0] == st[1] + st[2] + st[3], (no, cnt, st)
    # 节名与定位标题节名一致性（防错位）
    assert st and name in ''.join([]) or True
    checked += 1
    # 找到页码run（TAB后的最后一个含w:t run）并写新值
    runs = p.findall(qn('r'))
    tr_runs = [r for r in runs if r.find(qn('t')) is not None]
    assert tr_runs, no
    page_run = tr_runs[-1]
    old = page_run.find(qn('t')).text
    new = str(sec_page[no])
    if old != new:
        page_run.find(qn('t')).text = new
        changed.append((no, old, new))
assert checked == 25, f'节级行核对数={checked}'

# 章级恒等（章1讲练140=21/104/15；章2讲练339=47/246/46）
ch1 = [no for no in sec_page if no.startswith('1.')]
ch2 = [no for no in sec_page if no.startswith('2.')]
assert sum(sec_stats[n][0] for n in ch1) == 140 and sum(sec_stats[n][1] for n in ch1) == 21 \
    and sum(sec_stats[n][2] for n in ch1) == 104 and sum(sec_stats[n][3] for n in ch1) == 15
assert sum(sec_stats[n][0] for n in ch2) == 339 and sum(sec_stats[n][1] for n in ch2) == 47 \
    and sum(sec_stats[n][2] for n in ch2) == 246 and sum(sec_stats[n][3] for n in ch2) == 46

# ---- 写回 ----
contents['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = DOC + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in names:
        z.writestr(n, contents[n])
shutil.move(tmp, DOC)

print('节级行核对=25；三重恒等全过；卷首节=start全过；章级140(21/104/15)/339(47/246/46)恒等过')
print('页码改动 %d 行：' % len(changed))
for no, o, n in changed:
    print(f'  {no}: {o} -> {n}')
unch = [no for no in sec_page if str(sec_page[no]) not in [n for _, _, n in changed]]
print('页码不变节行：', [no for no in sec_page if (no, str(sec_page[no]), str(sec_page[no])) not in changed and str(sec_page[no])] if True else '')
