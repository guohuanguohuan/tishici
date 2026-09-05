# -*- coding: utf-8 -*-
"""②C_06_衔接2差集明细.py — 只读：衔接2 逐段分区明细＋「新口径∩探针非解析区」差集段落全貌；
并全两件扫【编注】【点睛】出现情况，定 T6c 触发词口径。"""
import sys, io, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

NUM = r'(?:\d+(?:\.\d+)+-\d+|\d+)'
QBLOCK_RE = re.compile(r'^%s．（' % NUM)
ENTRY_RE = re.compile(r'^%s．' % NUM)
TITLE_RE = re.compile(r'^\d+(?:\.\d+)+[\s　]')
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*(?:方法讲解|知识讲解)[｜|]')
KNOWVAL_RE = re.compile(r'^\d+(?:\.\d+)*[\s　]+\S')
ANA_TOOL = re.compile(r'【(?:分析|详解|点睛)】')
ANA_PROBE = re.compile(r'【(?:分析|详解|点睛|编注)】')
LBL_ANS = re.compile(r'【答案】')
LBL_KNOW = re.compile(r'【知识点】')


def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))


def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None


def has_bar18(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return False
    pb = ppr.find(q('pBdr'))
    if pb is None: return False
    lf = pb.find(q('left'))
    return lf is not None and lf.get(q('sz')) == '18'


def rc9(p):
    n = 0
    for shd in p.iter(q('shd')):
        if tag(shd.getparent()) == 'rPr' and (shd.get(q('fill')) or '').upper() == 'C9C9C9':
            n += 1
    return n


def scan(path, dump):
    z = zipfile.ZipFile(path)
    try:
        doc = etree.fromstring(z.read('word/document.xml'))
    finally:
        z.close()
    els = list(doc.find(q('body')))
    rows = []
    region = None; ana_open = False; know_val_pending = False
    in_q = False; in_ana = False
    for i, c in enumerate(els):
        if c.tag != q('p'):
            region = None; ana_open = False; know_val_pending = False
            in_q = False; in_ana = False
            rows.append((i, '<%s>' % tag(c), 0, '', False, '-'))
            continue
        t = ptext(c); f = pfill(c)
        is_title = (TITLE_RE.match(t) and (f in ('ADC2DA', 'C6D4E3') or LECT_RE.match(t) or has_bar18(c)))
        if QBLOCK_RE.match(t):
            in_q = True; in_ana = False
        elif is_title:
            in_q = False; in_ana = False
        elif ENTRY_RE.match(t) and not QBLOCK_RE.match(t):
            in_q = False; in_ana = False
        if in_q and ANA_TOOL.search(t):
            in_ana = True
        old_hit = in_q and in_ana
        protected = bool(QBLOCK_RE.match(t) or LBL_ANS.search(t) or LBL_KNOW.search(t))
        n = rc9(c)
        # 探针分区
        if is_title:
            region = '标题'; ana_open = False; know_val_pending = False
        elif QBLOCK_RE.match(t):
            region = '题干区'; ana_open = False; know_val_pending = False
        elif ENTRY_RE.match(t):
            region = '条目区'; ana_open = False; know_val_pending = False
        elif region not in (None, '标题', '条目区'):
            if ANA_PROBE.search(t):
                region = '解析区'; ana_open = True; know_val_pending = False
            elif LBL_ANS.search(t):
                region = '答案区'; know_val_pending = False
            elif LBL_KNOW.search(t):
                region = '知识点区'; know_val_pending = True
            elif region == '知识点区':
                if know_val_pending and KNOWVAL_RE.match(t):
                    know_val_pending = False
                else:
                    region = '解析区' if ana_open else '知识点区余'
                    know_val_pending = False
        rows.append((i, region, n, t, old_hit and not protected, 'P' if protected else '-'))
    if dump:
        for (i, r, n, t, newhit, prot) in rows:
            mark = ''
            if newhit and r != '解析区':
                mark = '  <== 新口径命中但探针非解析区'
            print('%4d %-8s rC9=%-3d %s %s %s%s' % (i, r, n, prot, '旧命中' if (prot == '-' and False) else '', t[:60], mark))
    # 差集统计
    delta = [(i, r, n, t) for (i, r, n, t, newhit, prot) in rows if newhit and r != '解析区']
    print('   差集段数=%d rC9合计=%d' % (len(delta), sum(d[2] for d in delta)))
    for (i, r, n, t) in delta:
        print('   差集 段%-4d 区=%-6s rC9=%-3d %s' % (i, r, n, t[:60]))
    return rows


B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '副本')
F2 = os.path.join(B, '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx')
F1 = os.path.join(B, '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx')

print('===== 衔接2 全逐段明细 =====')
scan(F2, dump=True)
print()
print('===== 衔接1 差集（新口径∩非解析区） =====')
scan(F1, dump=False)
print()
print('===== 触发词普查 =====')
for label, f in [('衔接1', F1), ('衔接2', F2)]:
    z = zipfile.ZipFile(f)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    cnt = {}
    for p in doc.iter(q('p')):
        t = ptext(p)
        for m in re.findall(r'【[^】]{1,6}】', t):
            cnt[m] = cnt.get(m, 0) + 1
    print(label, dict(sorted(cnt.items(), key=lambda kv: -kv[1])))
