# -*- coding: utf-8 -*-
# 一次性诊断：I1第一子层 56(run)≠59(计数) 差异定位——列出全部（N）起段段落＋阴影状态＋状态机判定
import zipfile, re, sys
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

path = sys.argv[1] if len(sys.argv) > 1 else '副本/I1.docx'
z = zipfile.ZipFile(path)
doc = etree.fromstring(z.read('word/document.xml'))
z.close()
body = doc.find(q('body'))
els = list(body)

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def shd_fill(rpr):
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd.get(q('fill')) if shd is not None else None

ENT_RE = re.compile(r'^\d+．')
HEAD_RE = re.compile(r'^\d+(?:\.\d+){1,6}(?:\s|方法讲解)')
SUB_RE = re.compile(r'^（\d+）')
CIRC_RE = re.compile(r'^[①②③④⑤⑥⑦⑧⑨⑩]')
QBLOCK_RE = re.compile(r'^\d+．（')

# 状态机（与工具 entry_counts 同款）
entry_active = False; deep = False; last_sub_no = 0
rows = []
for i, el in enumerate(els):
    if el.tag != q('p'):
        continue
    t = ptext(el)
    if QBLOCK_RE.match(t):
        entry_active = False; deep = False; last_sub_no = 0
        continue
    if ENT_RE.match(t) and not HEAD_RE.match(t):
        rows.append((i, 'ENTRY', t[:36], '', entry_active, deep, last_sub_no))
        entry_active = True; deep = False; last_sub_no = 0
        continue
    if HEAD_RE.match(t):
        entry_active = False; deep = False; last_sub_no = 0
        continue
    if CIRC_RE.match(t):
        deep = True
        continue
    m = SUB_RE.match(t)
    if m and entry_active:
        no = int(m.group(0)[1:-1])
        # 段首连续灰底 run 串接
        lead = ''
        for r in el.iter(q('r')):
            rt = ''.join(x.text or '' for x in r.findall(q('t')))
            if rt == '':
                continue
            if shd_fill(r.find(q('rPr'))) == 'C9C9C9':
                lead += rt
            else:
                break
        shaded = bool(re.fullmatch(r'（\d+）', lead))
        skipped = deep and no != last_sub_no + 1
        rows.append((i, 'SUB%d' % no, t[:36], lead[:16], 'SHD' if shaded else 'white',
                     'deep' if deep else '-', last_sub_no))
        if skipped:
            continue
        deep = False; last_sub_no = no

print('%-5s %-7s %-38s %-16s %-6s %-5s %s' % ('idx', 'kind', 'text', 'lead_run', 'shd', 'deep', 'last'))
for r in rows:
    if r[1] == 'ENTRY' or True:
        mark = ''
        if r[1].startswith('SUB') and r[4] == 'white':
            mark = '  <<< 无灰底'
        if r[1].startswith('SUB') and r[5] == 'deep':
            mark += '  [deep态]'
        print('%-5d %-7s %-38s %-16s %-6s %-5s %s%s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], mark))
