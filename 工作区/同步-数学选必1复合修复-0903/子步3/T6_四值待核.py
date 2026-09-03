# -*- coding: utf-8 -*-
"""子步3 T6 四值待核项二层核验：
①红旗词扫描——待核文本含题侧特征（卡壳看答案/【答案】/【详解】/【分析】/题号块形态）即红旗；
②页域断言——待核矩形页必须落在某讲部块页域（该节首条目页 ~ 末节条目页+1）内。"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pymupdf

SUB3 = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步3'
VOLS = ['B', 'C', 'E', 'F', 'G', 'H']
SEC_ENTRIES = {
    'B': {'1.1.1': 9, '1.1.2': 2, '1.1.3': 7, '1.2.1': 5, '1.2.2': 9, '1.2.3': 1, '1.2.4': 4},
    'C': {'1.2.5': 10},
    'E': {'2.1': 2, '2.2.1': 4, '2.2.2': 7, '2.2.3': 4, '2.2.4': 3, '2.3.1': 1, '2.3.2': 3, '2.3.3': 3},
    'F': {'2.3.4': 1, '2.4': 3, '2.5.1': 2, '2.5.2': 4},
    'G': {'2.6.1': 2, '2.6.2': 6, '2.7.1': 4, '2.7.2': 4},
    'H': {'2.8': 14},
}
RED = re.compile(r'卡壳看答案|【答案】|【详解】|【分析】|【点睛】|（简单|（中档|（难·')
ITEM_RE = re.compile(r"^\s*待核 第(\d+)页 \([0-9.,\-]+\)-\([0-9.,\-]+\) '(.*)'")

ok_all = True
out = {}
for vol in VOLS:
    # 解析四值报告的待核项
    items = []
    for line in open(SUB3 + r'\四值2\%s.txt' % vol, encoding='utf-8'):
        m = ITEM_RE.match(line.rstrip('\n'))
        if m:
            items.append((int(m.group(1)), m.group(2)))
    # 讲部块页域：各节首/末条目页
    doc = pymupdf.open(SUB3 + r'\pdf\%s.pdf' % vol)
    zones = []
    for sec, n in SEC_ENTRIES[vol].items():
        first_anchor = '%s-1．' % sec
        last_anchor = '%s-%d．' % (sec, n)
        p_first = p_last = None
        for pno in range(len(doc)):
            t = re.sub(r'\s+', '', doc[pno].get_text())
            if p_first is None and first_anchor.replace('．', '．') in t.replace(' ', ''):
                p_first = pno + 1
            if last_anchor in t:
                p_last = pno + 1
        assert p_first is not None and p_last is not None, (vol, sec, p_first, p_last)
        zones.append((sec, p_first, p_last + 1))  # 末条目内容可续页
    doc.close()
    bad_red = [(p, t) for p, t in items if RED.search(t)]
    bad_zone = [(p, t) for p, t in items if not any(f <= p <= l for _, f, l in zones)]
    out[vol] = {'待核总数': len(items), '红旗词': bad_red[:5], '页域外': bad_zone[:5],
                '页域': zones}
    ok = not bad_red and not bad_zone
    ok_all &= ok
    print(vol, '待核', len(items), '红旗', len(bad_red), '页域外', len(bad_zone), '判定', 'PASS' if ok else 'FAIL')
    if bad_zone[:3]:
        print('   页域外样本:', bad_zone[:3], '页域:', zones)
json.dump(out, open(SUB3 + r'\四值2\待核核验.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('总判定:', 'PASS' if ok_all else 'FAIL')
