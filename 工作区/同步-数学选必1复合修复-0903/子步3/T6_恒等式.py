# -*- coding: utf-8 -*-
"""子步3 T6：统计行恒等式链（定稿态）
各题型组统计段题数之和＝该节标题行统计段题数；各节之和＝全件统计行题数（首卷）＝文件名题量；
分卷题量和＝全章题量（B+C=140、E+F+G+H=339→文件名口径核验）。"""
import sys, io, re, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def pfill(p):
    ppr = p.find(q('pPr'))
    s = ppr.find(q('shd')) if ppr is not None else None
    return s.get(q('fill')) if s is not None else None

SUB3 = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步3'
NAMES = {
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
QTY = {'B': 61, 'C': 79, 'E': 92, 'F': 90, 'G': 68, 'H': 89}
SEC_RE = re.compile(r'^(\d+(?:\.\d+)+)\s+.+?　本节(\d+)题：简单(\d+)｜中档(\d+)｜难(\d+)')
GRP_RE = re.compile(r'^(\d+(?:\.\d+)+)\s+.+?　(\d+)题：')
ALL_RE = re.compile(r'^全件(\d+)题：简单(\d+)｜中档(\d+)｜难(\d+)')
LEAVES = {
    'B': ['1.1.1', '1.1.2', '1.1.3', '1.2.1', '1.2.2', '1.2.3', '1.2.4'],
    'C': ['1.2.5'],
    'E': ['2.1', '2.2.1', '2.2.2', '2.2.3', '2.2.4', '2.3.1', '2.3.2', '2.3.3'],
    'F': ['2.3.4', '2.4', '2.5.1', '2.5.2'],
    'G': ['2.6.1', '2.6.2', '2.7.1', '2.7.2'],
    'H': ['2.8'],
}
for v in LEAVES:
    LEAVES[v] = sorted(LEAVES[v], key=len, reverse=True)

res = {}
ok_all = True
for vol, fn in NAMES.items():
    z = zipfile.ZipFile(SUB3 + '\\定稿\\' + fn)
    root = etree.fromstring(z.read('word/document.xml'))
    body = root.find(q('body'))
    sec_stat = {}    # 节号 → (题量, 简, 中, 难)
    grp_stat = {}    # 节号 → [组题数...]
    all_stat = None
    for el in body:
        if tag(el) != 'p':
            continue
        t = ptext(el)
        f = pfill(el)
        m = SEC_RE.match(t)
        if f == 'ADC2DA' and m:
            sec_stat[m.group(1)] = tuple(int(x) for x in m.groups()[1:])
            continue
        m = ALL_RE.match(t)
        if m:
            all_stat = tuple(int(x) for x in m.groups())
            continue
        if f == 'C6D4E3' and '知识讲解' not in t and '方法讲解' not in t:
            m = GRP_RE.match(t)
            if m:
                num = m.group(1)
                sec = next((s for s in LEAVES[vol] if num == s or num.startswith(s + '.')), None)
                grp_stat.setdefault(sec, []).append(int(m.group(2)))
    # 恒等式链
    bad = []
    for sec, (n, a, b, c) in sec_stat.items():
        gsum = sum(grp_stat.get(sec, []))
        if gsum != n:
            bad.append((sec, n, gsum))
    vol_sum = sum(v[0] for v in sec_stat.values())
    dist = [sum(v[i] for v in sec_stat.values()) for i in (1, 2, 3)]
    if vol_sum != QTY[vol]:
        bad.append(('卷合计', QTY[vol], vol_sum))
    if all_stat is not None:
        if all_stat[0] != vol_sum and vol in ('B', 'E'):
            # 首卷全件统计行＝全章口径
            pass
        # 首卷全件统计行＝全章题量（B 140 / E 339）
    res[vol] = {'节统计': {k: v[0] for k, v in sec_stat.items()},
                '组统计和': {k: sum(v) for k, v in grp_stat.items()},
                '卷合计': vol_sum, '三档': dist, '全件统计行': all_stat, '不符': bad}
    ok_all &= not bad
    print(vol, '节数', len(sec_stat), '组恒等', '✓' if not bad else bad, '卷合计', vol_sum, '三档', dist, '全件行', all_stat)

# 全章口径
ch1 = sum(res[v]['卷合计'] for v in ('B', 'C'))
ch2 = sum(res[v]['卷合计'] for v in ('E', 'F', 'G', 'H'))
print('全章题量：第1章', ch1, '（全件统计行140 应等）', '第2章', ch2, '（339 应等）')
ok_all &= ch1 == 140 and ch2 == 339
ok_all &= res['B']['全件统计行'][0] == 140 and res['E']['全件统计行'][0] == 339
json.dump(res, open(SUB3 + r'\T6_统计行恒等式.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T6 统计行恒等式链 总判定:', 'PASS' if ok_all else 'FAIL')
