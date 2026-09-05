# -*- coding: utf-8 -*-
"""②C_05_口径对平侦察.py — T6c 设计前对平侦察（只读、不改任何文件）。
对照三口径在同一现行副本上的 run 级 C9C9C9 计数：
  旧审计口径（工具现行 c 路径）＝题号块内、首个【分析|详解|点睛】后全部段（in_ana 粘滞至题块结束）；
  新块界定口径（拟 T6c）＝同旧触发，但【答案】【知识点】行与题号块行本身受保护不剥；
  探针解析区口径＝②C_04 分区（含编注触发、知识点值后续段归解析区）。
输出：逐口径计数＋新旧差集逐段明细（含区类、C9 数、文本前50）——用于对平 649−595=54。"""
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
ANA_TOOL = re.compile(r'【(?:分析|详解|点睛)】')      # 工具现行口径（无编注）
ANA_PROBE = re.compile(r'【(?:分析|详解|点睛|编注)】')  # 探针口径
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


def scan(path):
    z = zipfile.ZipFile(path)
    try:
        doc = etree.fromstring(z.read('word/document.xml'))
    finally:
        z.close()
    els = list(doc.find(q('body')))
    old = new = probe = 0
    diffs = []
    region = None; ana_open = False; know_val_pending = False
    in_q = False; in_ana = False
    for i, c in enumerate(els):
        if c.tag != q('p'):
            region = None; ana_open = False; know_val_pending = False
            in_q = False; in_ana = False
            continue
        t = ptext(c); f = pfill(c)
        is_title = (TITLE_RE.match(t) and (f in ('ADC2DA', 'C6D4E3') or LECT_RE.match(t) or has_bar18(c)))
        # —— 旧口径状态机（工具现行） ——
        if QBLOCK_RE.match(t):
            in_q = True; in_ana = False
        elif is_title:
            in_q = False; in_ana = False
        elif ENTRY_RE.match(t) and not QBLOCK_RE.match(t):
            in_q = False; in_ana = False
        if in_q and ANA_TOOL.search(t):
            in_ana = True
        old_hit = in_q and in_ana
        n = rc9(c)
        if old_hit: old += n
        # —— 新口径（旧触发＋答案/知识点/题号块行保护） ——
        protected = bool(QBLOCK_RE.match(t) or LBL_ANS.search(t) or LBL_KNOW.search(t))
        if old_hit and not protected:
            new += n
            if False: pass
        # —— 探针分区 ——
        if is_title:
            region = '标题'; ana_open = False; know_val_pending = False
        elif QBLOCK_RE.match(t):
            region = '题干区'; ana_open = False; know_val_pending = False
        elif ENTRY_RE.match(t):
            region = '条目区'; ana_open = False; know_val_pending = False
        elif region in (None, '标题', '条目区'):
            pass
        else:
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
        if region == '解析区':
            probe += n
        # 差异登记：旧命中但新保护（拟不剥）
        if old_hit and protected and n:
            diffs.append((i, n, '题号块' if QBLOCK_RE.match(t) else ('答案' if LBL_ANS.search(t) else '知识点'), t[:50]))
    return old, new, probe, diffs


B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '副本')
FILES = [('衔接1(29)', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
         ('衔接2(13)', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx')]
for label, n in FILES:
    old, new, probe, diffs = scan(os.path.join(B, n))
    print('#### %s  旧审计口径=%d  新口径(保护答案/知识点/题号块)=%d  探针解析区=%d' % (label, old, new, probe))
    print('   旧−新差=%d（受保护段C9合计）' % (old - new))
    for (i, nn, k, t) in diffs:
        print('   段%-4d %s 受保护 rC9=%-3d %s' % (i, k, nn, t))
    print()
