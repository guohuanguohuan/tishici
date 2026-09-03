# -*- coding: utf-8 -*-
r"""X1锚点更正（子步1·一次性脚本）——锚点映射表X1行由题号块式更正为实际首块（条目号式）。
依据：附则前置步0「锚点＝正文首块机读特征」；X1正文首块＝讲部条目「1.2.1-1．平行线分线段成比例定理」，
v1锚点（首题1.2.1.1-1．）因讲部4条目占满首页而落第2页——非修复失败，登记滞后。
附则表行改写由主会话执行；本脚本只更新工作区JSON载体并留痕old/new。
"""
import sys, io, os, re, json, zipfile
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def nospc(s): return re.sub(r'[\s　]+', '', s or '')

WS = os.path.dirname(os.path.abspath(__file__))          # 子步1/
ROOT = os.path.dirname(WS)                                # 工作区根
fix = os.path.join(WS, 'fixed', 'X1.docx')
z = zipfile.ZipFile(fix)
root = etree.fromstring(z.read('word/document.xml'))
z.close()
body = root.find(q('body'))
kids = list(body)
brk = None
for i, el in enumerate(kids):
    if etree.QName(el).localname == 'p':
        ppr = el.find(q('pPr'))
        if ppr is not None and ppr.find(q('sectPr')) is not None:
            brk = i; break
RE_TMH = re.compile(r'^(\d+\.\d+(?:\.\d+)?-\d+．)')
RE_QK = re.compile(r'^（(?:简单|中档|难|衔接必会)')
first_entry = None
for el in kids[brk + 1:]:
    if etree.QName(el).localname != 'p':
        continue
    t = ptext(el).strip()
    if not t:
        continue
    m = RE_TMH.match(t)
    if m and not RE_QK.match(t[m.end(1):]):
        first_entry = t
        break
assert first_entry, '未找到条目号首块'
tok = RE_TMH.match(first_entry).group(1)
new_anchor = {'family': '条目号式',
              'regex': r'^' + re.escape(tok) + re.escape(nospc(first_entry[len(tok):len(tok) + 8])),
              'source': first_entry}
mpath = os.path.join(ROOT, '锚点映射表v1.json')
data = json.load(open(mpath, encoding='utf-8'))
old = dict(data['X1']['anchor'])
data['X1']['anchor'] = new_anchor
data['X1']['anchor_override_note'] = ('2026-09-03子步1更正：v1题号块式锚点%s因讲部条目占满首页落第2页；'
    '按前置步0「锚点＝正文首块机读特征」更正为实际首块（条目号式）。附则表行改写待主会话。' % old['regex'])
json.dump(data, open(mpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('X1锚点更正:')
print('  old:', old['family'], old['regex'])
print('  new:', new_anchor['family'], new_anchor['regex'])
print('  源串:', new_anchor['source'][:50])
