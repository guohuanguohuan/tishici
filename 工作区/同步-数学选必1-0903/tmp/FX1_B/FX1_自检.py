# -*- coding: utf-8 -*-
"""FX1-B 自检：①题号61块节内序列 ②统计段恒等式 ③文内标题逐字核 ④改动点复测"""
import zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
PATH = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
with zipfile.ZipFile(PATH) as z:
    root = etree.fromstring(z.read('word/document.xml'))
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def ptext(p, math=True):
    parts = []
    for el in p.iter():
        ln = etree.QName(el).localname
        if ln == 't' and el.text:
            if math or etree.QName(el).namespace == W:
                parts.append(el.text)
    return ''.join(parts)

# ①题号块序列（C9C9C9加粗run，文本=题号）
pat_q = re.compile(r'^(\d+(?:\.\d+){3})-(\d+)．$')
seq = {}
order = []
for p in paras:
    for r in p.findall(f'.//{{{W}}}r'):
        shd = r.find(f'{{{W}}}rPr/{{{W}}}shd')
        if shd is None or shd.get(f'{{{W}}}fill') != 'C9C9C9':
            continue
        t = r.find(f'{{{W}}}t')
        txt = t.text if t is not None and t.text else ''
        m = pat_q.match(txt)
        if m:
            seq.setdefault(m.group(1), []).append(int(m.group(2)))
            order.append(txt)
total = sum(len(v) for v in seq.values())
print('①题号块: 总数=', total)
expect = {'1.1.1': 10, '1.1.2': 4, '1.1.3': 10, '1.2.1': 9, '1.2.2': 7, '1.2.3': 8, '1.2.4': 13}
ok = True
for k, v in expect.items():
    got = seq.get(k, [])
    cont = got == list(range(1, len(got) + 1))
    match = len(got) == v and cont
    ok &= match
    print(f'  {k}: 期望{v} 实测{len(got)} 连续1..{len(got)}={cont} {"OK" if match else "FAIL"}')
print(f'①结论: {"PASS 题号61块序列与节内连续不变" if ok and total == 61 else "FAIL"}')

# ②统计段恒等式
print('②统计段恒等式:')
# 全件统计行 p#1
t1 = ptext(paras[1], math=False)
print('  全件统计行:', t1)
assert '140' in t1 and '简单21' in t1.replace(' ', ''), t1
# 节标题统计段（ADC2DA段非p#0）
node_sum = 0
for i, p in enumerate(paras):
    if i == 0:
        continue
    shd = p.find(f'{{{W}}}pPr/{{{W}}}shd')
    if shd is not None and shd.get(f'{{{W}}}fill') == 'ADC2DA':
        t = ptext(p, math=False)
        m = re.search(r'(\d+)\s*题', t)
        if m:
            node_sum += int(m.group(1))
            print(f'  节标题 p#{i}: {t[:50]}')
print(f'  节统计段合计={node_sum}（期望61）')
# 题型标题统计段（C6D4E3段）
type_sum = 0
type_cnt = 0
for p in paras:
    shd = p.find(f'{{{W}}}pPr/{{{W}}}shd')
    if shd is not None and shd.get(f'{{{W}}}fill') == 'C6D4E3':
        t = ptext(p, math=False)
        m = re.search(r'(\d+)\s*题[：:]', t)
        if m:
            type_sum += int(m.group(1))
            type_cnt += 1
print(f'  题型统计段: 组数={type_cnt} Σ={type_sum}（期望49组Σ61）')
print(f'②结论: {"PASS 全件140=61(B)+79(C)，节Σ61=题型Σ61=B卷题量" if node_sum == 61 and type_sum == 61 and type_cnt == 49 else "FAIL"}')

# ③文内标题逐字核
EXP = '人教B版选必1 第1章 空间向量与立体几何·讲练件（140题）'
got = ptext(paras[0], math=False)
print('③文内标题逐字核:', repr(got))
print('   与期望逐字相等:', got == EXP)

# ④改动点复测
print('④改动点复测（最终落盘件）:')
# 题1.2.1.2-2 解得值
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
p260 = paras[260]
found = False
for om in p260.findall(f'.//{{{M}}}oMath'):
    lin = ''.join(e.text or '' for e in om.iter() if etree.QName(e).localname == 't')
    if lin == 'x=-1z=2':
        found = True
print('  解得纠错后 oMath 线性化 x=-1z=2:', found)
print('  详解全文:', ptext(p260)[:200])
# run级tab=0
run_tabs = len(root.findall(f'.//{{{W}}}r/{{{W}}}tab'))
print('  run级w:tab残留=', run_tabs, '（期望0）')
# pPr制表位定义数（非字符，登记不动）
pPr_tabdefs = len(root.findall(f'.//{{{W}}}pPr/{{{W}}}tabs/{{{W}}}tab'))
print('  pPr制表位定义（非字符tab，登记不动）=', pPr_tabdefs)
# 段尾空格=0
tr = 0
for p in paras:
    last_t = None
    for el in p.iter():
        if etree.QName(el).localname == 't':
            last_t = el
    if last_t is not None and last_t.text and last_t.text != last_t.text.rstrip(' \xa0'):
        tr += 1
print('  段尾空格残留=', tr, '（期望0）')
