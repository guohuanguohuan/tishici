# -*- coding: utf-8 -*-
"""②C_04_解析块分区探针.py — T6c 衔接件作用域开关的设计前侦察（只读、不改任何文件）。
逐题块分区：题干区（题号块起至首个标签前）／答案区（【答案】＋其值段）／
知识点区（【知识点】＋其节号前缀值段）／解析区（【分析】【详解】【点睛】【编注】块
＋解析已开后知识点值段之后的未标注续段＝无标签详解公式段）。
输出：逐件各区段数与 run 级 C9C9C9 计数、逐题块分区明细（前 N 题）、界外未归类段登记。"""
import sys, io, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

NUM = r'(?:\d+(?:\.\d+)+-\d+|\d+)'
QBLOCK_RE = re.compile(r'^%s．（' % NUM)          # 题号块（括注题号）
ENTRY_RE = re.compile(r'^%s．' % NUM)             # 条目号（知识回顾/讲部条目）
TITLE_RE = re.compile(r'^\d+(?:\.\d+)+[\s　]')     # 章/节/题型标题
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*(?:方法讲解|知识讲解)[｜|]')
KNOWVAL_RE = re.compile(r'^\d+(?:\.\d+)*[\s　]+\S')  # 知识点值＝教材节号前缀（公共规则 L115）
LBL_ANS = re.compile(r'【答案】')
LBL_KNOW = re.compile(r'【知识点】')
LBL_ANA = re.compile(r'【(?:分析|详解|点睛|编注)】')
LBL_OTHER = re.compile(r'【(?:大招指引|题后反思|温馨提醒|定义|结论)】')


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None


def has_bar18(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return False
    pb = ppr.find(q('pBdr'))
    if pb is None:
        return False
    lf = pb.find(q('left'))
    return lf is not None and lf.get(q('sz')) == '18'


def rc9(p):
    """run 级 C9C9C9 计数（含 oMath 内 m:r 的 w:rPr/w:shd）"""
    n = 0
    for shd in p.iter(q('shd')):
        if tag(shd.getparent()) == 'rPr' and (shd.get(q('fill')) or '').upper() == 'C9C9C9':
            n += 1
    return n


def classify(path):
    z = zipfile.ZipFile(path)
    try:
        doc = etree.fromstring(z.read('word/document.xml'))
    finally:
        z.close()
    els = list(doc.find(q('body')))
    rows = []          # (idx, region, rC9, text前40)
    region = None      # None＝题块外
    ana_open = False
    know_val_pending = False
    qidx = 0
    for i, c in enumerate(els):
        if c.tag != q('p'):
            region = None; ana_open = False; know_val_pending = False
            rows.append((i, '<%s>' % tag(c), 0, ''))
            continue
        t = ptext(c)
        f = pfill(c)
        is_title = (TITLE_RE.match(t) and (f in ('ADC2DA', 'C6D4E3') or LECT_RE.match(t) or has_bar18(c)))
        if is_title:
            region = '标题'; ana_open = False; know_val_pending = False
            rows.append((i, '标题', rc9(c), t[:40])); continue
        if QBLOCK_RE.match(t):
            qidx += 1
            region = '题干区'; ana_open = False; know_val_pending = False
            rows.append((i, '题干区#%d' % qidx, rc9(c), t[:40])); continue
        if ENTRY_RE.match(t):
            region = '条目区'; ana_open = False; know_val_pending = False
            rows.append((i, '条目区', rc9(c), t[:40])); continue
        if region in (None, '标题', '条目区'):
            rows.append((i, region or '题块外', rc9(c), t[:40])); continue
        # —— 题块内 ——
        if LBL_ANA.search(t):
            region = '解析区'; ana_open = True; know_val_pending = False
        elif LBL_ANS.search(t):
            region = '答案区'; know_val_pending = False
        elif LBL_KNOW.search(t):
            region = '知识点区'; know_val_pending = True
        elif LBL_OTHER.search(t):
            region = '解析区' if ana_open else '其他标签区'
            know_val_pending = False
        else:
            if region == '知识点区':
                if know_val_pending and KNOWVAL_RE.match(t):
                    know_val_pending = False      # 知识点值段（节号前缀），仍属知识点区
                else:
                    # 知识点值段之后的未标注段：解析已开→无标签详解公式段（解析区）
                    region = '解析区' if ana_open else '知识点区余'
                    know_val_pending = False
            # 题干区/答案区/解析区 的未标注续段：沿用当前区
        rows.append((i, region, rc9(c), t[:40]))
    return rows


B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '副本')
FILES = [('衔接1(29)', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
         ('衔接2(13)', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx')]
DETAIL = int(sys.argv[1]) if len(sys.argv) > 1 else 0
for label, n in FILES:
    rows = classify(os.path.join(B, n))
    agg = {}
    for (i, r, c, t) in rows:
        base = r.split('#')[0]
        a = agg.setdefault(base, [0, 0])
        a[0] += 1; a[1] += c
    print('#### %s  总段=%d  run级C9C9C9总=%d' % (label, len(rows), sum(r[2] for r in rows)))
    for k in sorted(agg, key=lambda x: -agg[x][1]):
        print('   %-12s 段数=%-4d rC9=%d' % (k, agg[k][0], agg[k][1]))
    if DETAIL:
        print('   --- 逐段明细 ---')
        for (i, r, c, t) in rows:
            print('   %4d %-14s rC9=%-4d %s' % (i, r, c, t))
    print()
