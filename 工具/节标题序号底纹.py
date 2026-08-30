# -*- coding: utf-8 -*-
#
# 收编：2026-08-29 节序号底纹收口轮（来源：桌面一次性脚本 同步-数学选必1第2章清单-0828回扫/节序号底纹.py
#       升级收编为常驻工具；升级点见 docstring「2026-08-29 收编注记」）
# 2026-08-29 成书形态回扫轮（T代理）扩版：节·讲部·题型三标题同族底纹＋标题层级缩进挂载
# 2026-08-30 拍板执行轮（T2代理）缩进梯子改版：按号深区分＋缩进加倍（底纹逻辑不动）
#
"""节标题序号底纹.py — 节/讲部/题型标题序号挂 C9C9C9 底纹＋加粗＋标题层级缩进（可复用，幂等）

口径注记（效力序见公共规则§7「题号难度块底纹」条款内「结构序号底纹」扩展）：
  · 2026-08-27 用户拍板「节标题序号底纹」；2026-08-29 成书形态拍板扩为节·讲部·题型三标题同族
    （原「题型标题不挂底纹」口径废止）：教材节标题序号、讲部标题序号（父号.k 方法讲解｜…）、
    题型标题序号（父链续层 父号.j）一律加同款 C9C9C9 结构底纹＋随标题加粗；底纹只盖序号字符
    （含尾随半角空格）、不盖标题文字；序号与标题文字同 run 时先拆出独立 run 再挂。
  · 标题层级缩进——【2026-08-30 用户拍板加倍改版（原「节0/讲部2/题型4或直挂2」口径废止）】：
    二级节标题（N.N）leftChars=0（即清 w:ind 顶格）／三级节标题（N.N.N）leftChars=200／
    讲部标题 leftChars=400／节下直挂题型 leftChars=400／讲部下题型 leftChars=800
    （层级与序号点数一致；题型归属判定按其前最近讲部——题型父号＝其前最近讲部序号即讲部下，
    否则节下直挂）。只动标题段，正文与题目段落一律不碰（顶格不变）。
  · 父级节标题（如「2.5」「9.1」二级）与叶节同款挂底纹——恒等式「结构序号底纹 run 数＝节＋讲部＋
    题型标题总数」，三标题分型以 extract_structure（section/lecture/group）为源。
  · 条目题名行「N．」全角句点起段，与 N.N(.N) 半角点分序号天然不同形——条目号不属本工具口径
    （另由 工具/条目号底纹.py 处置，本工具不碰条目题名行，断言守恒）。
  · 2026-08-29 收编注记：标题段内「标题文字 run 剥遗留底纹」归一（存量整行铺灰形态）；
    工具内断言全文 w:t 字符序列改前后恒等（零字符铁律）＋条目号底纹 run 数守恒。

判定与行为：
  · 标题源＝extract_structure 判定的 section（节）/lecture（讲部）/group（题型）段（body 级，
    序号 N.N(.N)+ 半角点分〔1..6 层〕＋空白＋标题文字；讲部形「父号.k 方法讲解｜…」）；
    一级章号「N 标题」不属节标题口径，跳过并逐处登记；
  · 序号 run 文本终态＝「N.N(.N) 」（尾随半角空格随灰底）；
  · 已挂（序号独立 run 已 C9C9C9）→ 幂等跳过，仍补加粗（缺才补）；
  · 序号 run 已有其他 fill 底纹 → 报错人工处置（不静默覆盖）；
  · 标题段内其他 run 带 C9C9C9（遗留铺灰）→ 剥除并计数（标题文字无底纹口径）；
  · 缩进（2026-08-30 梯子）：二级节摘 w:ind／三级节 leftChars=200／讲部 400／
    题型按其前最近讲部判定归属——讲部下（父号＝最近讲部序号）800、节下直挂 400；
    已同值幂等跳过；
  · 修改的 w:t 一律置 xml:space="preserve" 防吞空格。
输出：登记 md（三类型逐处：序号→标题、级别、缩进值、处置）＋stdout 恒等式断言
  （结构序号底纹 run 数＝节数＋讲部数＋题型数＝新挂＋幂等跳过）。

用法: python 节标题序号底纹.py <docx> <登记md>
"""
import sys, os, re, zipfile, time, copy, tempfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_structure import structure   # 注：该模块导入时会自重包 stdout
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

FILL = 'C9C9C9'
SECTNUM_RE = re.compile(r'^\d+(?:\.\d+){1,6} ?$')     # 序号 run 终态文本（尾随半角空格随灰底）
SECHEAD_RE = re.compile(r'^(\d+(?:\.\d+){1,6})( ?)')  # 父链续层序号（1..6层）＋至多一个尾随半角空格
ENT_RE = re.compile(r'^\d+．')                         # 条目题名行（全角句点，天然排除）
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*方法讲解[｜|]')

IND_2SEC = None      # 二级节（N.N）＝清 w:ind 顶格（leftChars=0）
IND_3SEC = 200       # 三级节（N.N.N）＝2字符
IND_LECT = 400       # 讲部标题＝4字符
IND_GRP_DIRECT = 400 # 节下直挂题型＝4字符
IND_GRP_LECT = 800   # 讲部下题型＝8字符

def para_runs(p):
    return [c for c in p if tag(c) == 'r']

def run_text(r):
    return ''.join(t.text or '' for t in r.findall(q('t')))

def set_run_text(r, s):
    ts = r.findall(q('t'))
    ts[0].text = s
    ts[0].set(XMLSPACE, 'preserve')
    for t in ts[1:]:
        t.text = ''

def shd_of(r):
    rpr = r.find(q('rPr'))
    return rpr.find(q('shd')) if rpr is not None else None

def doc_text(doc):
    return ''.join(t.text or '' for t in doc.iter(q('t')))

def ent_shaded_count(doc):
    """条目号底纹 run 数（body 级条目题名行的独立「N．」C9C9C9 run，与条目号底纹.py/六类计数同源口径）。"""
    n = 0
    body = doc.find(q('body'))
    for p in body:
        if p.tag != q('p'):
            continue
        for r in p.findall(q('r')):
            tx = run_text(r)
            if tx and re.match(r'^\d+．$', tx):
                shd = shd_of(r)
                if shd is not None and shd.get(q('fill')) == FILL:
                    n += 1
    return n

def ensure_anchor_rpr(r):
    """序号 run 补加粗＋底纹 C9C9C9（各自缺才补）。返回 (是否新挂底纹, 是否补加粗)。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    bold_added = False
    if rpr.find(q('b')) is None:
        b = etree.Element(q('b'))
        rf = rpr.find(q('rFonts'))
        rpr.insert(list(rpr).index(rf) + 1 if rf is not None else 0, b)
        bold_added = True
    shd = rpr.find(q('shd'))
    if shd is not None and shd.get(q('fill')) == FILL:
        return False, bold_added
    if shd is None:
        shd = etree.Element(q('shd'))
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
        rpr.append(shd)  # rPr 内 shd 序靠后（bdr 之后），追加即合法
        return True, bold_added
    raise RuntimeError('序号run已有其他底纹 fill=%s，需人工处置' % shd.get(q('fill')))

def isolate_and_shade(p, numlen):
    """把段首 [0,numlen) 字符隔离为独立 run 并挂底纹（缺才挂，幂等）。
    序号跨多 run（如「1.1」＋「.1 」）时：边界拆分后把序号段合并回收首个文本 run
    （字符合并、顺序不变、零字符增删；标题文字其余部分留在独立 run 并剥底纹）。
    返回 (序号run元素, 是否新挂底纹, 是否补加粗, 序号run文本)。"""
    runs = para_runs(p)
    covered = []   # [(run, text)] 累计覆盖 [0,numlen)
    off = 0
    for r in runs:
        tx = run_text(r)
        if not tx:
            continue
        covered.append((r, tx))
        off += len(tx)
        if off >= numlen:
            break
    assert covered and off >= numlen, '序号未落在文本run内（序号跨 run 碎裂超限需人工归并）'
    first_r, first_tx = covered[0]
    # 末个覆盖 run 越界拆分：拆出序号段之后的标题文字（剥底纹独立 run）
    total = sum(len(tx) for _, tx in covered)
    last_r, last_tx = covered[-1]
    if total > numlen:
        cut = numlen - (total - len(last_tx))
        rest = last_tx[cut:]
        set_run_text(last_r, last_tx[:cut])
        nr = copy.deepcopy(last_r)
        set_run_text(nr, rest)
        nrpr = nr.find(q('rPr'))
        if nrpr is not None:
            nshd = nrpr.find(q('shd'))
            if nshd is not None:
                nrpr.remove(nshd)
        last_r.addnext(nr)
    # 多 run 序号合并回收首 run（只动 run 边界不动文字流）
    if len(covered) > 1:
        set_run_text(first_r, ''.join(tx for _, tx in covered)[:numlen])
        for r, _ in covered[1:]:
            p.remove(r)
    target = first_r
    assert run_text(target) and len(run_text(target)) == numlen
    shd_added, bold_added = ensure_anchor_rpr(target)
    return target, shd_added, bold_added, run_text(target)

# ---------- 缩进挂载（2026-08-29 成书形态拍板：标题层级缩进；只动标题段） ----------
PPR_AFTER_IND = ('contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection',
                 'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr',
                 'sectPr', 'pPrChange')

def set_indent(p, left_chars):
    """标题段挂 w:ind leftChars=left_chars（leftChars=0/None → 摘除 w:ind 顶格）。
    返回 (旧值或None, 是否改动)。幂等：已同值不动。"""
    ppr = p.find(q('pPr'))
    ind = ppr.find(q('ind')) if ppr is not None else None
    if left_chars is None or left_chars == 0:
        if ind is None:
            return None, False
        ppr.remove(ind)
        return (ind.get(q('leftChars')) or ind.get(q('left')), True)
    if ppr is None:
        ppr = etree.Element(q('pPr')); p.insert(0, ppr)
    if ind is not None:
        old = ind.get(q('leftChars')) or ind.get(q('left'))
        for a in (q('left'), q('start')):     # 摘绝对左缩进，只按字符缩进
            if a in ind.attrib:
                del ind.attrib[a]
        ind.set(q('leftChars'), str(left_chars))
        return old, (old != str(left_chars))
    ind = etree.Element(q('ind'))
    ind.set(q('leftChars'), str(left_chars))
    anchor = None
    for c in ppr:
        if tag(c) in PPR_AFTER_IND:
            anchor = c
            break
    if anchor is not None:
        anchor.addprevious(ind)
    else:
        ppr.append(ind)
    return None, True

def indent_for(kind, num, last_lecture):
    """2026-08-30 缩进梯子（按号深区分＋加倍）：二级节=None（清ind顶格）；三级节=200；
    讲部=400；题型按其前最近讲部判定归属——父号＝最近讲部序号→讲部下800，否则节下直挂400。"""
    if kind == '节':
        return IND_2SEC if num.count('.') == 1 else IND_3SEC
    if kind == '讲部':
        return IND_LECT
    parent = num.rsplit('.', 1)[0]
    return IND_GRP_LECT if (last_lecture is not None and parent == last_lecture) else IND_GRP_DIRECT

def main(path, regmd):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    before_text = doc_text(doc)
    ent_before = ent_shaded_count(doc)

    st = structure(path)
    heads = []     # (body索引, 类型, 序号, numlen)
    skipped = []   # 一级章号等非标题口径段（登记不处置）
    for x in st['items']:
        if x['kind'] not in ('section', 'group', 'lecture'):
            continue
        m = SECHEAD_RE.match(x['text'])
        kind = {'section': '节', 'group': '题型', 'lecture': '讲部'}[x['kind']]
        if x['kind'] in ('section', 'group') and LECT_RE.match(x['text']):
            kind = '讲部'   # 讲部形文本纠偏（无「：」曾误判 section；带「：」误判 group 同理）
        if not m:
            skipped.append(x['text'][:30])
            continue
        assert not ENT_RE.match(x['text']), '条目题名行误入标题口径: %r' % x['text'][:30]
        heads.append((x['el'], kind, m.group(1), m.end()))

    body = doc.find(q('body'))
    els = list(body)

    rows = []
    n_new = n_already = n_strip = n_bold = 0
    ind_changes = []
    last_lecture = None   # 题型归属判定锚：其前最近讲部序号
    for eli, kind, num, numlen in heads:
        p = els[eli]
        full = ''.join(t.text or '' for t in p.iter(q('t')))
        m = SECHEAD_RE.match(full)
        assert m and m.group(1) == num, '标题序号复检不一致: %r' % full[:30]
        if kind == '节':
            level = '二级' if num.count('.') == 1 else '三级'
        elif kind == '讲部':
            level = '讲部'
        else:
            level = '讲部下' if (last_lecture is not None
                                 and num.rsplit('.', 1)[0] == last_lecture) else '直挂'
        target, shd_added, bold_added, rt = isolate_and_shade(p, numlen)
        assert SECTNUM_RE.match(rt), '序号run文本形态异常: %r' % rt
        n_new += (1 if shd_added else 0)
        n_already += (0 if shd_added else 1)
        n_bold += (1 if bold_added else 0)
        # 标题文字 run 剥遗留底纹（底纹只盖序号口径；序号 run 本身除外）
        stripped = 0
        for r in p.iter(q('r')):
            if r is target:
                continue
            shd = shd_of(r)
            if shd is not None and shd.get(q('fill')) == FILL:
                shd.getparent().remove(shd)
                stripped += 1
        n_strip += stripped
        # 缩进挂载（2026-08-30 梯子：二级节0/三级节200/讲部400/直挂题型400/讲部下题型800，幂等）
        chars = indent_for(kind, num, last_lecture)
        oldind, ind_chg = set_indent(p, chars)
        if ind_chg:
            ind_changes.append((kind, num, oldind, chars))
        if kind == '讲部':
            last_lecture = num
        title = full[len(m.group(0)):].strip() or full.strip()
        rows.append((kind, num, level, title, rt, shd_added, bold_added, stripped, oldind, chars))

    # 恒等式断言：每标题段底纹 run 恰为序号 run 一个，总数＝节＋讲部＋题型标题数
    total_shaded = 0
    for eli, kind, num, numlen in heads:
        p = els[eli]
        shd_runs = [run_text(r) for r in p.iter(q('r'))
                    if shd_of(r) is not None and shd_of(r).get(q('fill')) == FILL]
        assert len(shd_runs) == 1 and SECTNUM_RE.match(shd_runs[0]), \
            '标题 b#%d 底纹run异常: %r' % (eli, shd_runs)
        total_shaded += 1
    n_heads = len(heads)
    n_by = {k: sum(1 for _, kk, _, _ in heads if kk == k) for k in ('节', '讲部', '题型')}
    ok = (total_shaded == n_heads == n_new + n_already)
    # 零字符铁律断言＋条目号底纹守恒断言
    assert doc_text(doc) == before_text, '零字符铁律被破坏（w:t 字符序列变化）'
    ent_after = ent_shaded_count(doc)
    assert ent_after == ent_before, '条目号底纹 run 数变化 %d->%d（本工具不得碰条目题名行）' % (ent_before, ent_after)

    # 落盘 docx（仅替换 word/document.xml，其余成员原样回写；占用重试禁杀进程）
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

    # 登记 md
    lines = []
    lines.append('# 结构序号底纹＋标题缩进登记 — %s' % os.path.basename(path))
    lines.append('')
    lines.append('轮次：0830拍板执行轮 2026-08-30（公共规则§7结构序号底纹——节·讲部·题型三标题同族＋')
    lines.append('标题缩进梯子〔2026-08-30拍板加倍〕：二级节0（清ind）/三级节200/讲部400/')
    lines.append('节下直挂题型400/讲部下题型800（归属按其前最近讲部），只动标题段正文顶格不变；')
    lines.append('恒等式＝结构序号底纹 run 数＝节数＋讲部数＋题型数；结构锚加粗、底纹只盖序号')
    lines.append('含尾随半角空格、不盖标题文字；条目号「N．」不属本口径不碰；幂等可重跑）')
    lines.append('')
    lines.append('标题总数 %d（节 %d｜讲部 %d｜题型 %d）｜新挂 %d｜幂等跳过 %d｜补加粗 %d｜'
                 '标题文字剥遗留底纹 %d｜缩进变更 %d 段｜恒等式（挂底纹 run 数 %d＝标题总数）%s｜'
                 '零字符断言 通过｜条目号底纹守恒 %d＝%d 通过'
                 % (n_heads, n_by['节'], n_by['讲部'], n_by['题型'], n_new, n_already, n_bold,
                    n_strip, len(ind_changes), total_shaded,
                    '成立' if ok else '不成立!!', ent_before, ent_after))
    # 缩进梯子实测分布（2026-08-30）
    lad = collections.Counter()
    for kind, num, level, title, rt, sa, ba, st_, oldind, chars in rows:
        lad[(kind, level, '顶格(清ind)' if chars is None else str(chars))] += 1
    lines.append('')
    lines.append('缩进梯子实测（leftChars值×段数）：' + '｜'.join(
        '%s·%s %s×%d' % (k, lv, v, n) for (k, lv, v), n in sorted(lad.items())))
    lines.append('')
    lines.append('| 类型 | 序号 | 级别 | 标题 | 序号run | 缩进 | 处置 |')
    lines.append('|---|---|---|---|---|---|---|')
    for kind, num, level, title, rt, shd_added, bold_added, stripped, oldind, chars in rows:
        disp = '新挂' if shd_added else '已挂（幂等跳过）'
        extra = []
        if bold_added:
            extra.append('补加粗')
        if stripped:
            extra.append('剥标题文字遗留底纹%d处' % stripped)
        if extra:
            disp += '（' + '＋'.join(extra) + '）'
        ind_disp = '顶格(摘ind)' if chars is None else 'leftChars=%d' % chars
        if oldind is not None and str(oldind) != str(chars if chars is not None else ''):
            ind_disp += '（原%s）' % oldind
        lines.append('| %s | %s | %s | %s | 「%s」 | %s | %s |'
                     % (kind, num, level, title.replace('|', '\\|')[:40], rt, ind_disp, disp))
    if skipped:
        lines.append('')
        lines.append('非标题口径跳过段（一级章号等，登记不处置）：%s' % '；'.join(skipped))
    lines.append('')
    open(regmd, 'w', encoding='utf-8').write('\n'.join(lines))
    print('标题总数 %d（节%d｜讲部%d｜题型%d）｜新挂 %d｜幂等跳过 %d｜补加粗 %d｜剥遗留 %d｜缩进变更 %d；'
          '恒等式（%d＝%d）%s；零字符断言通过；条目号底纹守恒 %d＝%d'
          % (n_heads, n_by['节'], n_by['讲部'], n_by['题型'], n_new, n_already, n_bold, n_strip,
             len(ind_changes), total_shaded, n_heads,
             '成立 PASS' if ok else '不成立 CHECK', ent_before, ent_after))
    print('缩进梯子实测：' + '｜'.join(
        '%s·%s %s×%d' % (k, lv, v, n) for (k, lv, v), n in sorted(lad.items())))
    print('登记md -> %s' % regmd)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
