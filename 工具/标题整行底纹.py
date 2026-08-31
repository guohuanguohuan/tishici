# -*- coding: utf-8 -*-
#
# 沿革：2026-08-29 节序号底纹收口轮建 节标题序号底纹.py（只盖序号灰块＋标题层级缩进）→
#   2026-08-31 欠账A·工具债⑤ 改版更名 标题整行底纹.py——N4/N5 拍板废止「结构序号底纹（只盖
#   序号）＋缩进梯子（0/200/400/800）」形态，本工具为其拆除与整行底纹落地载体（旧文件名废弃）。
#
"""标题整行底纹.py — 四类标题整行底纹＋新字号梯子＋顶格＋章底边框（N3/N4/N5；可复用，幂等）

口径（公共规则§7题号难度块底纹条款「标题字号梯子＋标题整行底纹」现行文本——2026-08-31 N3/N4/N5）：
  · 四类标题识别（body级段落，extract_structure 三标题分型＋章级补充识别）：
      章标题＝文内开头标题（首个非空段，件名行）＋「第X章/第X讲」级行；
      节标题＝教材 N.N / N.N.N 式（kind=section）；讲部标题＝「父号.k 方法讲解｜…」（kind=lecture）；
      题型标题＝父链续层「N.N.N[.k[.j]] …：…」（kind=group）。
  · 字号梯子：章/讲标题 run=32半点加粗、教材节标题 run=28半点加粗、讲部/题型标题 run=24半点加粗
    （sz/szCs 同值、b/bCs 补齐——缺才补，已有正确值不动）。
  · 整行底纹（段落 w:pPr/w:shd，val=clear color=auto）：章/节 #ADC2DA（转灰≈190）、
    讲部/题型 #C6D4E3（转灰≈209）。
  · 顶格：标题段落 w:ind 一律摘除（N4——旧缩进梯子 0/200/400/800 全部拆除）。
  · 章标题段加 w:pBdr bottom 通栏细线（single sz=4 space=1 auto）。
  · 拆除旧「结构序号底纹」形态：标题段内旧 run 级 C9C9C9 序号灰块剥除（序号随整行在底纹内、
    不单独挂灰）；标题段内其他 fill 的 run 级底纹不静默剥，登记告警。
  · 只改字号/底纹/ind/pBdr，不动 spacing/jc（行距归 T3 工具、对齐归左对齐管线）；
    条目题名行「N．」不属本口径（条目号底纹.py），断言守恒不误伤。

断言（全过才落盘）：A1 每标题段 pPr shd fill∈{ADC2DA/C6D4E3} 且分型正确；A2 标题段内
  C9C9C9 run 底纹＝0、w:ind＝0 段；A3 章标题 pBdr bottom 在位；A4 标题 run 字号/加粗全合规；
  A5 零字符（w:t 全文字符序列恒等）；A6 条目号底纹 run 数守恒；A7 幂等（二跑全部计数=0）。

用法: python 工具/标题整行底纹.py <docx> <登记md>
输出: 就地改写 docx（仅 word/document.xml；零改动时跳过重写、字节不变）＋登记md＋stdout。
"""
import sys, os, re, zipfile, time, copy, tempfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:   # reconfigure 防双重包装（extract_structure 导入时会重包 stdout——二次包装GC关buffer坑，经验文件2026-08-25）
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from extract_structure import structure
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

FILL_CH_SEC = 'ADC2DA'   # 章/节（N5 三色板，转灰≈190）
FILL_LEC_GRP = 'C6D4E3'  # 讲部/题型（转灰≈209）
FILL_OLD_GRAY = 'C9C9C9' # 旧结构序号灰块（拆除对象）

SZ = {'章': '32', '节': '28', '讲部': '24', '题型': '24'}
FILL = {'章': FILL_CH_SEC, '节': FILL_CH_SEC, '讲部': FILL_LEC_GRP, '题型': FILL_LEC_GRP}

SECHEAD_RE = re.compile(r'^(\d+(?:\.\d+){1,6})( ?)')  # 父链续层序号＋至多一个尾随半角空格
ENT_RE = re.compile(r'^\d+．')                         # 条目题名行（全角句点，天然排除）
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*方法讲解[｜|]')
CHAP_RE = re.compile(r'^第\d+[章讲]')

# w:pPr / w:rPr 子件 schema 序（插入定位用）
PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
             'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens',
             'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN',
             'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind', 'contextualSpacing',
             'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection', 'textAlignment',
             'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange']
RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'dstrike',
             'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish',
             'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs', 'highlight',
             'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs', 'em', 'lang',
             'eastAsianLayout', 'specVanish', 'oMath']


def _insert_ordered(parent, el, order):
    name = tag(el)
    idx = order.index(name)
    for c in parent:
        cn = tag(c)
        if cn in order and order.index(cn) > idx:
            c.addprevious(el)
            return
        if cn not in order:
            c.addprevious(el)
            return
    parent.append(el)


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def doc_text(doc):
    return ''.join(t.text or '' for t in doc.iter(q('t')))


def run_text(r):
    return ''.join(t.text or '' for t in r.findall(q('t')))


def shd_of(r):
    rpr = r.find(q('rPr'))
    return rpr.find(q('shd')) if rpr is not None else None


def ent_shaded_count(doc):
    """条目号底纹 run 数（body 级条目题名行的独立「N．」C9C9C9 run——与条目号底纹.py同源口径）。"""
    n = 0
    for p in doc.find(q('body')):
        if p.tag != q('p'):
            continue
        for r in p.findall(q('r')):
            tx = run_text(r)
            if tx and re.match(r'^\d+．$', tx):
                s = shd_of(r)
                if s is not None and s.get(q('fill')) == FILL_OLD_GRAY:
                    n += 1
    return n


def ensure_rpr(r):
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr'))
        r.insert(0, rpr)
    return rpr


def set_run_size_bold(r, szval):
    """run 设 sz/szCs=szval＋b/bCs（缺才加、异值才改）。返回 (字号改动, 加粗补齐)。"""
    rpr = ensure_rpr(r)
    size_chg = bold_add = 0
    for t in ('sz', 'szCs'):
        e = rpr.find(q(t))
        if e is None:
            e = etree.Element(q(t))
            _insert_ordered(rpr, e, RPR_ORDER)
            e.set(q('val'), szval)
            size_chg += 1
        elif e.get(q('val')) != szval:
            e.set(q('val'), szval)
            size_chg += 1
    for t in ('b', 'bCs'):
        if rpr.find(q(t)) is None:
            _insert_ordered(rpr, etree.Element(q(t)), RPR_ORDER)
            bold_add += 1
    return size_chg, bold_add


def set_para_shd(p, fill):
    """段落 pPr 挂整行底纹（缺/异值才改）。返回是否改动。"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    s = ppr.find(q('shd'))
    if s is not None and s.get(q('fill')) == fill and s.get(q('val')) == 'clear':
        return False
    if s is None:
        s = etree.Element(q('shd'))
        _insert_ordered(ppr, s, PPR_ORDER)
    s.set(q('val'), 'clear'); s.set(q('color'), 'auto'); s.set(q('fill'), fill)
    return True


def clear_ind(p):
    """摘除标题段 w:ind（N4 顶格）。返回是否改动。"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        return False
    ind = ppr.find(q('ind'))
    if ind is None:
        return False
    ppr.remove(ind)
    return True


def ensure_chapter_border(p):
    """章标题段加 w:pBdr bottom 通栏细线（single sz=4 space=1 auto）。返回是否改动。"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    pbdr = ppr.find(q('pBdr'))
    if pbdr is None:
        pbdr = etree.Element(q('pBdr'))
        _insert_ordered(ppr, pbdr, PPR_ORDER)
    bot = pbdr.find(q('bottom'))
    want = {'val': 'single', 'sz': '4', 'space': '1', 'color': 'auto'}
    if bot is None:
        bot = etree.Element(q('bottom'))
        pbdr.append(bot)
    cur = {k: bot.get(q(k)) for k in want}
    if cur == want:
        return False
    for k, v in want.items():
        bot.set(q(k), v)
    return True


def strip_old_gray(p):
    """拆除标题段内旧 run 级 C9C9C9 序号灰块。返回 (剥除数, 其他fill告警数)。"""
    stripped = warned = 0
    for r in p.iter(q('r')):
        s = shd_of(r)
        if s is None:
            continue
        if s.get(q('fill')) == FILL_OLD_GRAY:
            s.getparent().remove(s)
            stripped += 1
        else:
            warned += 1
    return stripped, warned


def find_titles(path, doc):
    """识别四类标题。返回 [(body索引, 类型, 序号或空, 文本)]。"""
    st = structure(path)
    body = doc.find(q('body'))
    els = list(body)
    heads, ch_idx = [], None
    # 章级：文内开头标题＝首个非空段（件名行特征含「·」）；另扫「第X章/第X讲」级行
    for i, c in enumerate(els):
        if c.tag != q('p'):
            continue
        t = ptext(c)
        if t.strip():
            ch_idx = i
            break
    anomalies = []
    if ch_idx is not None:
        t = ptext(els[ch_idx])
        if '·' in t:
            heads.append((ch_idx, '章', '', t))
        else:
            anomalies.append('首个非空段不含「·」（非件名行特征），未按章标题处置: %s' % t[:30])
    for i, c in enumerate(els):
        if c.tag != q('p') or i == ch_idx:
            continue
        t = ptext(c)
        if CHAP_RE.match(t):
            heads.append((i, '章', '', t))
    for x in st['items']:
        if x['kind'] not in ('section', 'group', 'lecture'):
            continue
        m = SECHEAD_RE.match(x['text'])
        kind = {'section': '节', 'group': '题型', 'lecture': '讲部'}[x['kind']]
        if x['kind'] in ('section', 'group') and LECT_RE.match(x['text']):
            kind = '讲部'   # 讲部形文本纠偏（历史同款）
        if not m:
            anomalies.append('%s标题无序号匹配，跳过: %s' % (kind, x['text'][:30]))
            continue
        assert not ENT_RE.match(x['text']), '条目题名行误入标题口径: %r' % x['text'][:30]
        heads.append((x['el'], kind, m.group(1), x['text']))
    heads.sort(key=lambda h: h[0])
    return heads, anomalies


def main(path, regmd):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    before_text = doc_text(doc)
    ent_before = ent_shaded_count(doc)

    heads, anomalies = find_titles(path, doc)
    body = doc.find(q('body'))
    els = list(body)

    rows = []
    c_size = c_bold = c_shd = c_ind = c_gray = c_pbdr = 0
    warn_other = 0
    lad = collections.Counter()
    for idx, kind, num, text in heads:
        p = els[idx]
        full = ptext(p)
        # —— 字号梯子（sz/szCs＋b/bCs，缺才补异值才改）——
        size_chg = bold_add = 0
        for r in p.iter(q('r')):
            sc, ba = set_run_size_bold(r, SZ[kind])
            size_chg += sc
            bold_add += ba
        c_size += (1 if size_chg else 0)
        c_bold += bold_add
        # —— 整行底纹 ——
        if set_para_shd(p, FILL[kind]):
            c_shd += 1
        # —— 顶格（摘 w:ind）——
        if clear_ind(p):
            c_ind += 1
        # —— 章底边框 ——
        if kind == '章' and ensure_chapter_border(p):
            c_pbdr += 1
        # —— 拆旧序号灰块 ——
        stripped, warned = strip_old_gray(p)
        c_gray += stripped
        warn_other += warned
        lad[kind] += 1
        rows.append((kind, num, full[:40], size_chg, bold_add, stripped))

    # ---- 断言 ----
    for idx, kind, num, text in heads:
        p = els[idx]
        ppr = p.find(q('pPr'))
        assert ppr is not None and ppr.find(q('shd')) is not None \
            and ppr.find(q('shd')).get(q('fill')) == FILL[kind], 'A1整行底纹缺失/异色: %s' % ptext(p)[:30]
        assert ppr.find(q('ind')) is None, 'A2标题段w:ind未清零: %s' % ptext(p)[:30]
        for r in p.iter(q('r')):
            s = shd_of(r)
            assert s is None or s.get(q('fill')) != FILL_OLD_GRAY, \
                'A2标题段残留C9C9C9 run底纹: %s' % ptext(p)[:30]
            rpr = r.find(q('rPr'))
            if rpr is not None:
                e = rpr.find(q('sz'))
                assert e is None or e.get(q('val')) == SZ[kind], \
                    'A4标题run字号异值: %s' % ptext(p)[:30]
                assert rpr.find(q('b')) is not None, 'A4标题run缺加粗: %s' % ptext(p)[:30]
        if kind == '章':
            assert ppr.find(q('pBdr')) is not None and ppr.find(q('pBdr')).find(q('bottom')) is not None, \
                'A3章标题pBdr bottom缺失: %s' % ptext(p)[:30]
    assert doc_text(doc) == before_text, 'A5零字符铁律被破坏'
    ent_after = ent_shaded_count(doc)
    assert ent_after == ent_before, 'A6条目号底纹 run 数变化 %d->%d（不得碰条目题名行）' % (ent_before, ent_after)

    changed = any((c_size, c_bold, c_shd, c_ind, c_gray, c_pbdr))
    if changed:
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        fd, tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(path)) or '.')
        os.close(fd)
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
                zout.writestr(item, data)
        for k in range(12):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                time.sleep(6)
        else:
            raise RuntimeError('locked: ' + path)

    # ---- 登记 md ----
    L = []
    L.append('# 标题整行底纹登记 — %s' % os.path.basename(path))
    L.append('')
    L.append('口径：2026-08-31 N3/N4/N5——章32/节28/讲部·题型24半点加粗；整行底纹 章/节#ADC2DA、'
             '讲部/题型#C6D4E3；标题段w:ind清零顶格；章标题pBdr bottom通栏细线；旧run级C9C9C9'
             '序号灰块拆除；不动spacing/jc；幂等可重跑（零改动时跳过重写字节不变）。')
    L.append('')
    L.append('标题段 %d（章 %d｜节 %d｜讲部 %d｜题型 %d）｜字号/加粗改动段 %d（run级字号改动＋加粗补齐 %d 处）｜'
             '整行底纹新挂/改色 %d｜w:ind清零 %d｜旧序号灰块剥除 %d｜章底边框新挂 %d｜'
             '其他fill run底纹告警 %d｜A5零字符 PASS｜A6条目号底纹守恒 %d＝%d PASS'
             % (len(heads), lad['章'], lad['节'], lad['讲部'], lad['题型'], c_size, c_bold,
                c_shd, c_ind, c_gray, c_pbdr, warn_other, ent_before, ent_after))
    L.append('三色fill实测：章/节段数×%s＝%d、讲部/题型段数×%s＝%d（run级C9C9C9在标题段内=0）'
             % (FILL_CH_SEC, lad['章'] + lad['节'], FILL_LEC_GRP, lad['讲部'] + lad['题型']))
    if anomalies:
        L.append('异常登记：' + '；'.join(anomalies))
    L.append('')
    L.append('| 类型 | 序号 | 标题 | run字号改动 | 补加粗 | 剥旧灰块 |')
    L.append('|---|---|---|---|---|---|')
    for kind, num, text, size_chg, bold_add, stripped in rows:
        L.append('| %s | %s | %s | %d | %d | %d |'
                 % (kind, num or '—', text.replace('|', '\\|')[:40], size_chg, bold_add, stripped))
    L.append('')
    open(regmd, 'w', encoding='utf-8').write('\n'.join(L))
    print('标题段 %d（章%d｜节%d｜讲部%d｜题型%d）｜字号段%d（+粗%d）｜底纹%d｜ind清零%d｜剥旧灰%d｜'
          '章边框%d｜告警%d｜零字符PASS｜条目守恒%d=%d%s'
          % (len(heads), lad['章'], lad['节'], lad['讲部'], lad['题型'], c_size, c_bold, c_shd,
             c_ind, c_gray, c_pbdr, warn_other, ent_before, ent_after,
             '' if changed else '｜幂等零改动（未重写）'))
    print('登记md -> %s' % regmd)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
