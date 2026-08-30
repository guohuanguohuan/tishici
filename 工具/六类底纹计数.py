# -*- coding: utf-8 -*-
#
# 沿革：2026-08-28 视觉锚新口径回扫轮收编为「四类底纹计数.py」；
# 2026-08-29 成书形态拍板由四类扩为六类（公共规则§7「六类底纹分开计数」条款），T代理改造更名。
# 旧名 工具/四类底纹计数.py 保留为兼容入口（同一 count，报告口径为六类）。
#
# 2026-08-30 拍板执行轮（T2代理）：②题号难度块签名同步三段式——「N．（档位·提分线·卡壳看答案）」
#   （工具/题号块三段式.py 改写产物）与旧单段「N．（档位）」两形态并收（过渡期兼容）。
"""六类底纹计数.py — C9C9C9 挂点六类分计与恒等式核验（只读，不改文件）：
  ①内容标记（答案值/需背）：答案行/跨段续值段内除 chip 外的灰底文字 run＋OMML 挂点
      （m:r、结构 ctrlPr 的 w:rPr）＋清单件填空答案标记（各线标记恒等式自定义，本工具只计数）
  ②题号难度块：run 文本「N．（档位·提分线·卡壳看答案）」（2026-08-30 三段式；兼容旧单段
      「N．（简单|中档|难）」），加粗＋灰底只盖块本身
  ③结构序号（节·讲部·题型，2026-08-29 三标题同族）：节/讲部/题型标题段内 run 文本
      「N.N(.N)+ 」（父链续层序号，尾部半角空格随灰底）
  ④块标签（含行内小标签，2026-08-29 扩面）：凡行内【×】栏目标签整 run（黑名单：
      【典例N】类删除对象、【易错】【了解】学史豁免）＋详解内并行解法起段标记
      （方法一/解法一/另解等，含［］形；【法一】等以标签形态入④）
  ⑤条目号：条目题名行独立「N．」run（题号块排斥：N．（档位）不算条目）
  ⑥条目第一子层：独立「（N）」run（全角括号；第二子层①②后隔层复用（N）、题目小问半角(1)不算）
  表内非标签灰底（导航表头 run 等）与单元格级底纹（tcPr shd）、空文本灰底 run 单独登记，不入六类。
  恒等式：③＝节数＋讲部数＋题型数；⑤＝条目计数；⑥＝第一子层计数；②＝题量（清单件无题块不适用）；
  ④＝标签计数（含行内小标签）；带答案值标记的题块数＝题量（清单件不适用）；A6A6A6/D9D9D9 残留＝0；w:bdr＝0。
  清单件判定：文件名含「知识清单」——②与答案值覆盖恒等式不适用（2026-08-29 收口注记②口径），
  ⑤⑥恒等式照查；讲练件/衔接件/实验卷全断言适用。
用法: python 六类底纹计数.py <docx> <报告txt>（旧名 四类底纹计数.py 同 CLI 兼容入口）"""
import sys, zipfile, re, os, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lxml import etree
from extract_structure import structure   # 注：该模块导入时会自重包 stdout

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

FILL = 'C9C9C9'
# —— 与 工具/块标签芯片.py 同源口径（复制常量避免中文名模块导入脆性；改动须两处同步）——
CHIP_RE = re.compile(r'【[^】]{1,16}】')
CHIP_BLACKLIST = ('【易错】', '【了解】')
CHIP_BLACKLIST_RE = re.compile(r'^【典例[^】]*】$')
MARK_RE = re.compile(r'^(?:\(\d{1,2}\)|（\d{1,2}）)?(?:【[^】]{1,12}】)?(?:解：|证明：)?'
                     r'(［?(?:方法|解法)[一二三四五六七八九十]{1,3}］?|另解)$')
QNUM_RE = re.compile(r'^\d+．（(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%)·卡壳看答案)?）$')
SECTNUM_RE = re.compile(r'^\d+(?:\.\d+){1,6} ?$')   # 结构序号 run 文本形如「1.1.1 」（尾随半角空格随灰底）
ENTNUM_RE = re.compile(r'^\d+．$')                  # 条目号独立 run
SUBNUM_RE = re.compile(r'^（\d+）$')                # 条目第一子层独立 run（全角括号）
QBLOCK_RE = re.compile(r'^\d+．（(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%)·卡壳看答案)?）')
ENT_RE = re.compile(r'^\d+．')
SUB_RE = re.compile(r'^（\d+）')
HEAD_RE = re.compile(r'^\d+(?:\.\d+){1,6}(?:\s|方法讲解)')
CIRC_RE = re.compile(r'^[①②③④⑤⑥⑦⑧⑨⑩]')

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def shd_fill(rpr):
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd.get(q('fill')) if shd is not None else None

def in_tbl(el):
    cur = el.getparent()
    while cur is not None:
        if tag(cur) == 'tbl':
            return True
        cur = cur.getparent()
    return False

def entry_counts(els):
    """条目计数与第一子层计数（与 工具/条目号底纹.py 同源状态机：题号块排斥、标题/题块断语境、
    表格不断语境、①②后外层续号仍计、隔层重启（1）不计）。返回 (条目数, 第一子层数)。"""
    n_ent = n_sub = 0
    entry_active = False
    deep = False
    last_sub_no = 0
    for el in els:
        if el.tag != q('p'):
            continue                      # 表格＝条目内容，不断语境
        t = ptext(el)
        if QBLOCK_RE.match(t):
            entry_active = False; deep = False; last_sub_no = 0
            continue
        if ENT_RE.match(t):
            n_ent += 1
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
            if deep and no != last_sub_no + 1:
                continue
            n_sub += 1
            deep = False
            last_sub_no = no
    return n_ent, n_sub

def count(path, report):
    st = structure(path)
    items = st['items']
    kind_by_el = {}
    for x in items:
        if x['kind'] in ('section', 'group', 'lecture'):
            kind_by_el[x['el']] = x['kind']
    sec_els = {x['el'] for x in items if x['kind'] == 'section'}
    lec_els = {x['el'] for x in items if x['kind'] == 'lecture'}
    grp_els = {x['el'] for x in items if x['kind'] == 'group'}
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    els = list(body)

    cls = {'内容标记': 0, '题号难度块': 0, '结构序号': 0, '块标签': 0, '条目号': 0, '条目第一子层': 0,
           '表内其他': 0}
    cls3 = {'节': 0, '讲部': 0, '题型': 0}
    chip = {}
    marker = 0
    om_mr = om_ctrl = 0
    a6 = 0
    qd_bold = 0    # ②题号难度块加粗违规（期望 0——§7加粗口径）
    ent_bold = 0   # ⑤条目号底纹 run 加粗违规（2026-08-29 口径：不加粗）
    sub_bold = 0   # ⑥第一子层底纹 run 加粗违规（不加粗）
    sec_bold = 0   # ③结构序号 run 加粗违规（结构锚加粗，期望 0）
    head_multi = 0 # 标题段多底纹 run 段数（节/讲部/题型——只盖序号，期望 0）
    empty_shd = 0  # 空文本灰底 run（登记不入六类不阻断）
    odd = []       # 无法归类的 C9C9C9 文字 run 样本

    is_qd = '知识清单' in os.path.basename(path)
    nent, nsub = entry_counts(els)

    # 段→body序号 映射（标题判定用；表内段不在其列）
    pidx = {id(p): i for i, p in enumerate(els) if tag(p) == 'p'}

    for r in doc.iter(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None:
            continue
        fill = shd_fill(rpr)
        if fill == 'A6A6A6':
            a6 += 1
        if fill != FILL:
            continue
        txt = ''.join(t.text or '' for t in r.findall(q('t')))
        p = r.getparent()
        while p is not None and tag(p) != 'p':
            p = p.getparent()
        bi = pidx.get(id(p), -1)
        hkind = kind_by_el.get(bi)
        if QNUM_RE.match(txt):
            cls['题号难度块'] += 1
            if rpr.find(q('b')) is None:
                qd_bold += 1
        elif txt and CHIP_RE.fullmatch(txt) and txt not in CHIP_BLACKLIST \
                and not CHIP_BLACKLIST_RE.match(txt):
            chip[txt] = chip.get(txt, 0) + 1
        elif txt and MARK_RE.match(txt):
            marker += 1
        elif hkind and SECTNUM_RE.match(txt):
            cls['结构序号'] += 1
            cls3[{'section': '节', 'lecture': '讲部', 'group': '题型'}[hkind]] += 1
            if rpr.find(q('b')) is None:
                sec_bold += 1
        elif ENTNUM_RE.match(txt) and not in_tbl(r):
            cls['条目号'] += 1
            if rpr.find(q('b')) is not None:
                ent_bold += 1
        elif SUBNUM_RE.match(txt) and not in_tbl(r):
            cls['条目第一子层'] += 1
            if rpr.find(q('b')) is not None:
                sub_bold += 1
        elif in_tbl(r):
            cls['表内其他'] += 1
        elif txt.strip():
            cls['内容标记'] += 1
        elif txt == '':
            empty_shd += 1
        else:
            odd.append(txt)

    # 标题段多底纹 run 段数（节/讲部/题型——每标题段底纹应恰为序号 run 一个）
    for he in sorted(sec_els | lec_els | grp_els):
        p = els[he]
        shd_runs = [''.join(x.text or '' for x in r.findall(q('t')))
                    for r in p.iter(q('r')) if shd_fill(r.find(q('rPr'))) == FILL]
        if len(shd_runs) != 1 or not SECTNUM_RE.match(shd_runs[0]):
            head_multi += 1

    for el in doc.iter():
        tg = tag(el)
        if etree.QName(el).namespace == M and tg in ('r', 'ctrlPr'):
            rpr = el.find(q('rPr'))
            if shd_fill(rpr) == FILL:
                if tg == 'r':
                    om_mr += 1
                else:
                    om_ctrl += 1
    # A6A6A6/D9D9D9 全局残留＋w:bdr
    a6_total = sum(1 for el in doc.iter(q('shd')) if el.get(q('fill')) == 'A6A6A6')
    d9_total = sum(1 for el in doc.iter(q('shd')) if el.get(q('fill')) == 'D9D9D9')
    bdr_total = sum(1 for _ in doc.iter(q('bdr')))
    # 单元格级底纹（导航表头等，登记不入六类）
    tc_shd = 0
    for tcpr in doc.iter(q('tcPr')):
        shd = tcpr.find(q('shd'))
        if shd is not None and shd.get(q('fill')) == FILL:
            tc_shd += 1
    # 标签计数（④期望值：文本出现数，与 块标签芯片.chip_spans 同源口径）
    lb_occ = {}
    for p in body.iter(q('p')):
        for mm in CHIP_RE.finditer(ptext(p)):
            lb = mm.group(0)
            if lb in CHIP_BLACKLIST or CHIP_BLACKLIST_RE.match(lb):
                continue
            lb_occ[lb] = lb_occ.get(lb, 0) + 1

    # ①覆盖恒等：每题块答案行（或跨段续值段）有答案值灰底
    cov = 0
    nocov = []
    ENTNUM_ONLY = ENTNUM_RE
    for qu in st['questions']:
        s_el = items[qu['start']]['el']
        e_el = items[qu['end']]['el'] if qu['end'] < len(items) else len(els)
        hit = False
        for ci in range(s_el, e_el):
            p = els[ci]
            if tag(p) != 'p':
                continue
            t = ptext(p)
            if not t.startswith('【答案】'):
                continue
            for r in p.iter(q('r')):
                txt = ''.join(x.text or '' for x in r.findall(q('t')))
                if txt and not CHIP_RE.fullmatch(txt) and shd_fill(r.find(q('rPr'))) == FILL:
                    hit = True; break
            if not hit:
                for el in p.iter():
                    if etree.QName(el).namespace == M and tag(el) in ('r', 'ctrlPr') \
                            and shd_fill(el.find(q('rPr'))) == FILL:
                        hit = True; break
            # 跨段续值：答案段无【知识点】时查下一段（同块内、排除条目号形态 run）
            if not hit and '【知识点】' not in t:
                cj = ci + 1
                while cj < e_el and tag(els[cj]) == 'p' and not ptext(els[cj]).strip():
                    cj += 1
                if cj < e_el and tag(els[cj]) == 'p':
                    for r in els[cj].iter(q('r')):
                        txt = ''.join(x.text or '' for x in r.findall(q('t')))
                        if txt and not CHIP_RE.fullmatch(txt) and not ENTNUM_ONLY.match(txt) \
                                and shd_fill(r.find(q('rPr'))) == FILL:
                            hit = True; break
            break  # 每题只认首个【答案】行
        if hit:
            cov += 1
        else:
            nocov.append(qu['no'])

    nq = len(st['questions'])
    nchip_runs = sum(chip.values()) + marker
    lines = []
    lines.append('六类底纹计数（XML 同源口径，2026-08-29 六类口径）：%s' % os.path.basename(path))
    lines.append('①内容标记（答案值/需背）：文字run %d｜OMML挂点 m:r %d＋ctrlPr %d＝%d'
                 % (cls['内容标记'], om_mr, om_ctrl, om_mr + om_ctrl + cls['内容标记']))
    lines.append('②题号难度块 %d（期望＝题量 %d%s）｜加粗违规 %d（期望 0）'
                 % (cls['题号难度块'], nq, '；清单件不适用' if is_qd else '', qd_bold))
    lines.append('③结构序号 %d（期望＝节 %d＋讲部 %d＋题型 %d＝%d）｜分计：节 %d｜讲部 %d｜题型 %d｜'
                 '加粗违规 %d（期望 0）｜标题段多底纹 run 段数 %d（期望 0——只盖序号）'
                 % (cls['结构序号'], len(sec_els), len(lec_els), len(grp_els),
                    len(sec_els) + len(lec_els) + len(grp_els),
                    cls3['节'], cls3['讲部'], cls3['题型'], sec_bold, head_multi))
    lines.append('④块标签（含行内小标签）run %d（其中并行解法标记 %d）｜标签run %d vs 标签计数（文本出现数）%d｜差 %d'
                 % (nchip_runs, marker, sum(chip.values()), sum(lb_occ.values()),
                    sum(chip.values()) - sum(lb_occ.values())))
    top = sorted(chip.items(), key=lambda kv: -kv[1])[:12]
    lines.append('   标签分计 TOP：%s' % ('；'.join('%s×%d' % kv for kv in top) if top else '（无）'))
    lines.append('⑤条目号 %d（期望＝条目计数 %d）｜加粗违规 %d（期望 0）' % (cls['条目号'], nent, ent_bold))
    lines.append('⑥条目第一子层 %d（期望＝第一子层计数 %d）｜加粗违规 %d（期望 0）'
                 % (cls['条目第一子层'], nsub, sub_bold))
    lines.append('带答案值标记的题块数 %d / 题量 %d%s%s'
                 % (cov, nq, ('（未覆盖题: %s）' % nocov) if nocov else '',
                    '（清单件：覆盖恒等式不适用）' if is_qd else ''))
    lines.append('表内非标签灰底run（登记不入六类） %d｜单元格级底纹（导航表头） %d｜空文本灰底run（登记不入六类） %d'
                 % (cls.get('表内其他', 0), tc_shd, empty_shd))
    lines.append('A6A6A6 残留 %d（期望 0；w:r 侧 %d）｜D9D9D9 残留 %d（期望 0）｜w:bdr %d（期望 0）'
                 % (a6_total, a6, d9_total, bdr_total))
    c9_total = (sum(cls[k] for k in ('内容标记', '题号难度块', '结构序号', '块标签', '条目号', '条目第一子层'))
                + om_mr + om_ctrl + cls.get('表内其他', 0) + tc_shd + empty_shd + len(odd))
    lines.append('C9C9C9 挂点总数（XML） %d' % c9_total)
    if odd:
        lines.append('未归类灰底文字run %d 个，样本: %r' % (len(odd), odd[:10]))
    base_ok = (cls['结构序号'] == len(sec_els) + len(lec_els) + len(grp_els)
               and cls3['节'] == len(sec_els) and cls3['讲部'] == len(lec_els) and cls3['题型'] == len(grp_els)
               and sec_bold == 0 and head_multi == 0 and qd_bold == 0
               and cls['条目号'] == nent and ent_bold == 0
               and cls['条目第一子层'] == nsub and sub_bold == 0
           and sum(chip.values()) == sum(lb_occ.values())
           and a6_total == 0 and d9_total == 0 and bdr_total == 0 and not odd)
    if is_qd:
        ok = base_ok
    else:
        ok = base_ok and cls['题号难度块'] == nq and cov == nq
    lines.append('结论: ' + ('PASS 六类齐＋恒等式成立' if ok else 'CHECK 见上'))
    out = '\n'.join(lines)
    open(report, 'w', encoding='utf-8').write(out + '\n')
    print(out)

if __name__ == '__main__':
    count(sys.argv[1], sys.argv[2])
