# -*- coding: utf-8 -*-
#
# 收编：2026-08-28 视觉锚新口径回扫轮·讲上卷试点（与 块标签芯片.py / 难度前置.py 配套对账）
#
"""四类底纹计数.py — C9C9C9 挂点分类计数与恒等式核验（只读，不改文件）：
  类①题号难度块：run 文本「N．（简单|中档|难）」（难度前置产物，加粗＋灰底只盖块本身）
  类②节标题序号：节标题段内 run 文本「N.N(.N)」
  类③块标签：【答案】【知识点】【分析】【详解】【点睛】＋详解内并行解法起段标记
      （方法一/解法一/另解等，含［］形；【法一】【整题法一】【最优解】等非枚举形态不算）
  类④内容标记（答案值）：答案行/跨段续值段内除【答案】chip 外的灰底文字 run
      ＋ OMML 挂点（m:r、结构 ctrlPr 的 w:rPr）
  表内非标签灰底（导航表头等）单独登记，不入四类。
  恒等式：带答案值标记的题块数＝题量；A6A6A6 残留＝0；w:bdr＝0。
  清单件分支（2026-08-29 条目号底纹新口径）：文件名含「知识清单」时启用——条目题名行条目号
  「N．」（独立 C9C9C9 run）计入「类①-条目子列：条目号底纹 run 数」，按新恒等式断言
  「条目号底纹 run 数＝条目名计数（件内条目题名行数，body 级 ^\\d+． 段数）」，并实测底纹 run
  加粗违规数＝0（条目号不加粗）；类②10/20 节序号与类④内容标记口径不变（§7：节标题序号底纹
  2026-08-28 知识清单件跟进、条目号底纹 2026-08-29 改口径——原「题号底纹 run 数＝0 正向归零」
  旧断言废止）。讲练件/衔接件/实验卷等非清单件逻辑完全不变。
用法: python 四类底纹计数.py <docx> <报告txt>"""
import sys, zipfile, re, os
from lxml import etree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_structure import structure   # 注：该模块导入时会自重包 stdout

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname

FILL = 'C9C9C9'
LABELS = ['【答案】', '【知识点】', '【分析】', '【详解】', '【点睛】']
MARK_RE = re.compile(r'^(?:\(\d{1,2}\)|（\d{1,2}）)?(?:【[^】]{1,12}】)?(?:解：|证明：)?'
                     r'(［?(?:方法|解法)[一二三四五六七八九十]{1,3}］?|另解)')
QNUM_RE = re.compile(r'^\d+．（(?:简单|中档|难)）$')
SECT_RE = re.compile(r'^\d+(?:\.\d+){1,2} ?$')   # 节序号 run 文本形如「1.1.1 」（尾部半角空格随灰底）
ENTNUM_RE = re.compile(r'^\d+．$')               # 清单件条目号独立 run（2026-08-29 条目号底纹）

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

def count(path, report):
    st = structure(path)
    items = st['items']
    sec_els = {x['el'] for x in items if x['kind'] == 'section'}
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    els = list(body)

    cls = {'题号难度块': 0, '节标题序号': 0, '答案值文字run': 0, '表内其他': 0, '条目号底纹': 0}
    chip = {lb: 0 for lb in LABELS}
    marker = 0
    om_mr = om_ctrl = 0
    a6 = 0
    ent_bold = 0   # 条目号底纹 run 加粗违规数（2026-08-29 口径：不加粗）
    odd = []   # 无法归类的 C9C9C9 文字 run 样本

    # 清单件判定＋条目名计数（body 级 ^\d+． 段；节标题 N.N(.N) 无全角句点不冲突、清单件无题号）
    is_qd = '知识清单' in os.path.basename(path)
    nent = sum(1 for el in els if tag(el) == 'p'
               and re.match(r'^\d+．', ''.join(t.text or '' for t in el.iter(q('t')))))

    # 段→body序号 映射（节标题判定用；表内段不在其列）
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
        if QNUM_RE.match(txt):
            cls['题号难度块'] += 1
        elif txt in LABELS:
            chip[txt] += 1
        elif MARK_RE.match(txt) and MARK_RE.match(txt).end(1) == len(txt):
            marker += 1
        elif bi in sec_els and SECT_RE.match(txt):
            cls['节标题序号'] += 1
        elif is_qd and ENTNUM_RE.match(txt) and not in_tbl(r):
            cls['条目号底纹'] += 1
            if rpr.find(q('b')) is not None:
                ent_bold += 1
        elif in_tbl(r):
            cls['表内其他'] += 1
        elif txt.strip():
            cls['答案值文字run'] += 1
        else:
            odd.append(txt)

    for el in doc.iter():
        tg = tag(el)
        if etree.QName(el).namespace == M and tg in ('r', 'ctrlPr'):
            rpr = el.find(q('rPr'))
            if shd_fill(rpr) == FILL:
                if tg == 'r':
                    om_mr += 1
                else:
                    om_ctrl += 1
    # A6A6A6 全局残留（w:r 侧＋OMML 侧所有 shd）
    a6_total = sum(1 for el in doc.iter(q('shd')) if el.get(q('fill')) == 'A6A6A6')
    bdr_total = sum(1 for _ in doc.iter(q('bdr')))
    # 单元格级底纹（导航表头等，登记不入四类）
    tc_shd = 0
    for tcpr in doc.iter(q('tcPr')):
        shd = tcpr.find(q('shd'))
        if shd is not None and shd.get(q('fill')) == FILL:
            tc_shd += 1

    # 类④覆盖恒等：每题块答案行（或跨段续值段）有答案值灰底
    cov = 0
    nocov = []
    for qu in st['questions']:
        s_el = items[qu['start']]['el']
        e_el = items[qu['end']]['el'] if qu['end'] < len(items) else len(els)
        hit = False
        for p in els[s_el:e_el]:
            if tag(p) != 'p':
                continue
            t = ptext(p)
            if not t.startswith('【答案】'):
                continue
            # 本段值区灰底（非 chip 的文字 run 或 OMML 挂点）
            for r in p.iter(q('r')):
                txt = ''.join(x.text or '' for x in r.findall(q('t')))
                if txt and txt not in LABELS and shd_fill(r.find(q('rPr'))) == FILL:
                    hit = True; break
            if not hit:
                for el in p.iter():
                    if etree.QName(el).namespace == M and tag(el) in ('r', 'ctrlPr') \
                            and shd_fill(el.find(q('rPr'))) == FILL:
                        hit = True; break
            # 跨段续值：答案段无【知识点】时查下一非空段
            if not hit and '【知识点】' not in t:
                nx = p.getnext()
                while nx is not None and tag(nx) == 'p' and not ptext(nx).strip():
                    nx = nx.getnext()
                if nx is not None and tag(nx) == 'p':
                    for r in nx.iter(q('r')):
                        txt = ''.join(x.text or '' for x in r.findall(q('t')))
                        if txt and txt not in LABELS and shd_fill(r.find(q('rPr'))) == FILL:
                            hit = True; break
            break  # 每题只认首个【答案】行
        if hit:
            cov += 1
        else:
            nocov.append(qu['no'])

    nq = len(st['questions'])
    lines = []
    lines.append('四类底纹计数（XML 同源口径）：%s' % os.path.basename(path))
    lines.append('类①题号难度块 %d（期望＝题量 %d）' % (cls['题号难度块'], nq))
    lines.append('类②节标题序号 %d（期望＝节数 %d）' % (cls['节标题序号'], len(sec_els)))
    lines.append('类③块标签 chip：%s｜并行解法标记 %d（合计 %d）'
                 % (' '.join('%s %d' % (lb, chip[lb]) for lb in LABELS), marker,
                    sum(chip.values()) + marker))
    lines.append('类④答案值：文字run %d｜OMML挂点 m:r %d＋ctrlPr %d＝%d'
                 % (cls['答案值文字run'], om_mr, om_ctrl, om_mr + om_ctrl))
    if is_qd:
        lines.append('类①-条目子列（2026-08-29 条目号底纹新口径）：条目号底纹 run %d（期望＝条目名计数 %d）'
                     '｜加粗违规 %d（期望 0）' % (cls['条目号底纹'], nent, ent_bold))
    lines.append('带答案值标记的题块数 %d / 题量 %d%s'
                 % (cov, nq, ('（未覆盖题: %s）' % nocov) if nocov else ''))
    lines.append('表内非标签灰底run（登记不入四类） %d｜单元格级底纹（导航表头） %d' % (cls['表内其他'], tc_shd))
    lines.append('A6A6A6 残留 %d（期望 0；w:r 侧 %d）｜w:bdr %d（期望 0）' % (a6_total, a6, bdr_total))
    c9_total = (cls['题号难度块'] + cls['节标题序号'] + cls['条目号底纹'] + sum(chip.values()) + marker
                + cls['答案值文字run'] + om_mr + om_ctrl + cls['表内其他'] + tc_shd + len(odd))
    lines.append('C9C9C9 挂点总数（XML） %d' % c9_total)
    if odd:
        lines.append('未归类灰底文字run %d 个，样本: %r' % (len(odd), odd[:10]))
    ok = (cls['题号难度块'] == nq and cls['节标题序号'] == len(sec_els)
          and cov == nq and a6_total == 0 and bdr_total == 0 and not odd
          and (not is_qd or (cls['条目号底纹'] == nent and ent_bold == 0)))
    lines.append('结论: ' + ('PASS 四类齐＋恒等式成立' + ('（含条目号底纹子列 %d=%d）' % (cls['条目号底纹'], nent) if is_qd else '')
                           if ok else 'CHECK 见上'))
    out = '\n'.join(lines)
    open(report, 'w', encoding='utf-8').write(out + '\n')
    print(out)

if __name__ == '__main__':
    count(sys.argv[1], sys.argv[2])
