# -*- coding: utf-8 -*-
"""N11 候选枚举：题干/详解区枚举序号短行组＋超短行清单"""
import zipfile, re, sys
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

def lin(el):
    out = []
    for sub in el.iter():
        if not isinstance(sub.tag, str): continue
        if sub.tag in (w('t'), '{%s}t' % M): out.append(sub.text or '')
    return ''.join(out)

def has_object(p):
    for sub in p.iter():
        if not isinstance(sub.tag, str): continue
        if sub.tag in (w('drawing'), w('pict')): return True
    return False

ENUM = re.compile(r'^([①②③④⑤⑥⑦⑧⑨]|\([1-9]\)|[A-D]．)')
QHEAD = re.compile(r'^\d{1,3}．')
LAB = re.compile(r'^【[^】]*】')

def main(path):
    with zipfile.ZipFile(path) as z:
        doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(w('body'))
    # 建立行模型
    rows = []
    for el in body:
        if not isinstance(el.tag, str): continue
        if el.tag == w('p'):
            t = lin(el)
            rows.append({'el': el, 't': t, 'kind': 'p', 'obj': has_object(el)})
        elif el.tag == w('tbl'):
            rows.append({'el': el, 't': '', 'kind': 'tbl', 'obj': False})
    # 分区：QHEAD起、LAB/SECT/题型止
    SECT = re.compile(r'^\d+(\.\d+)+\s')
    zone = 'LECT'
    groups = []
    cur = None
    for i, r in enumerate(rows):
        t = r['t'].strip()
        if r['kind'] == 'tbl' or not t:
            continue
        if QHEAD.match(t) or SECT.match(t) or t.startswith('【编注】题型通式') or t.startswith('全件') or t.startswith('本节') or (i == 0):
            zone = 'STEM' if QHEAD.match(t) else 'LECT'
            if cur and cur['items']: groups.append(cur)
            cur = None
            continue
        if LAB.match(t):
            zone = 'ANS'
            if cur and cur['items']: groups.append(cur)
            cur = None
            continue
        if zone == 'STEM' and ENUM.match(t):
            if cur is None:
                cur = {'start': i, 'items': [], 'zone': zone}
            cur['items'].append((i, r['t'], r['obj']))
        else:
            if cur and cur['items']: groups.append(cur)
            cur = None
    if cur and cur['items']: groups.append(cur)
    print('=== STEM枚举组 ===')
    for g in groups:
        print('zone=%s start行%d 数量%d' % (g['zone'], g['start'], len(g['items'])))
        for i, t, obj in g['items']:
            print('   [%d]%s len=%d obj=%s %s' % (i, '图' if obj else ' ', len(t), obj, t[:60]))
    # 全部短行清单（<25字、非空、非标题、非LAB）
    print('=== 全部短行(<25字, 排除LAB/枚举/图段) ===')
    zone = 'LECT'
    for i, r in enumerate(rows):
        t = r['t'].strip()
        if r['kind'] == 'tbl' or not t: continue
        if QHEAD.match(t):
            zone = 'STEM'; continue
        if SECT.match(t) or t.startswith('【编注】题型通式') or t.startswith('全件') or t.startswith('本节'):
            zone = 'LECT'; continue
        if LAB.match(t):
            zone = 'ANS'; continue
        if len(t) < 25 and not ENUM.match(t) and not r['obj']:
            print('[%d] zone=%s len=%d %s' % (i, zone, len(t), t))

if __name__ == '__main__':
    main(sys.argv[1])
