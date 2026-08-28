# -*- coding: utf-8 -*-
"""extract_structure.py — 讲练件结构提取：节标题/题型组/题块（含难度）/讲块位置
用法: python extract_structure.py <docx> [out.json]"""
import sys, io, zipfile, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)

def ptext(p):
    parts = []
    for e in p.iter():
        t = etree.QName(e).localname
        if t == 't' and e.text:
            parts.append(e.text)
    return ''.join(parts)

def structure(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(q('body'))
    els = list(body)  # body级元素（含表格）
    items = []  # (kind, idx_in_els, text)
    for i, el in enumerate(els):
        if el.tag != q('p'):
            items.append({'kind': 'other', 'el': i, 'text': '[TBL]' if el.tag == q('tbl') else etree.QName(el).localname, 'p': el})
            continue
        t = ptext(el)
        kind = 'para'
        if re.match(r'^\d+(\.\d+)*\s+\S', t):
            if '：' in t and re.match(r'^\d+(\.\d+)+\s', t):
                kind = 'group'      # 题型标题 X.Y.Z 标题：题型
            else:
                kind = 'section'    # 节标题（X.Y / X.Y.Z 无冒号）
        elif re.match(r'^\d+．', t):
            kind = 'qstart'
        items.append({'kind': kind, 'el': i, 'text': t, 'p': el})

    # 题块判定：qstart 起到下一个 qstart/标题/表格 前，块内须含【难度】
    n = len(items)
    qinfo = []  # {no, start, end(Exclusive), diff}
    i = 0
    while i < n:
        it = items[i]
        if it['kind'] == 'qstart':
            j = i + 1
            while j < n and items[j]['kind'] == 'para':
                j += 1
            block = [items[k]['text'] for k in range(i, j)]
            blk = '\n'.join(block)
            md = re.search(r'【难度】(简单|中档|难)', blk)
            mno = re.match(r'^(\d+)．', it['text'])
            if md and mno:
                qinfo.append({'no': int(mno.group(1)), 'start': it['el'], 'end': items[j-1]['el'] + 1 if j > i + 1 else it['el'] + 1, 'diff': md.group(1)})
                i = j
                continue
        i += 1
    return {'items': [{'kind': x['kind'], 'el': x['el'], 'text': x['text'][:80]} for x in items], 'questions': qinfo}

if __name__ == '__main__':
    s = structure(sys.argv[1])
    secs = [x for x in s['items'] if x['kind'] == 'section']
    grps = [x for x in s['items'] if x['kind'] == 'group']
    qs = s['questions']
    print('节标题 %d | 题型组 %d | 题块 %d（%d..%d）' % (len(secs), len(grps), len(qs), qs[0]['no'] if qs else 0, qs[-1]['no'] if qs else 0))
    cont = [qs[k]['no'] for k in range(1, len(qs)) if qs[k]['no'] != qs[k-1]['no'] + 1]
    print('题号连续性断点:', cont if cont else '无（1..N 连续）' if qs and qs[0]['no'] == 1 else '异常')
    for x in secs: print(' 节', x['el'], x['text'])
    if len(sys.argv) > 2:
        json.dump(s, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
