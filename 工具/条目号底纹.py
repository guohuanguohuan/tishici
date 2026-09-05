# -*- coding: utf-8 -*-
#
# 收编：2026-08-29 条目号底纹轮·选必1两清单件落地（公共规则§7题号难度块底纹条款·条目号底纹）
# 2026-08-29 成书形态回扫轮（T代理）扩版：衔接件/讲练件讲部条目扩面＋条目第一子层「（N）」底纹
#
"""条目号底纹.py — 条目题名行条目号「N．」＋条目第一子层「（N）」挂 C7C7C7 底纹（可复用，幂等）

口径注记（公共规则§7题号难度块底纹条款·条目号底纹＋条目第一子层底纹）：
  · 2026-08-29 用户拍板改口径＋同日成书形态拍板扩面：凡条目形内容的条目号「N．」挂
    w:shd val="clear" color="auto" fill="C7C7C7"——适用面＝知识清单件条目题名行＋衔接件讲部条目
    ＋讲练件讲部条目＋实验卷条目组条目题名行；只盖条目号本身、不盖题名文字（同 run 先拆独立
    run 再挂）、不加粗（纯序号锚）；恒等式＝条目号底纹 run 数＝条目计数。
  · 2026-08-29 成书形态拍板新增「条目第一子层底纹」：条目下第一子层「（N）」（全角括号）同款
    挂 C7C7C7、只盖「（N）」本身、不加粗；恒等式＝第一子层底纹 run 数＝第一子层计数。
    第二子层①②③、更深层复用（N）（隔层复用层）、题目小问半角(1)(2)与详解步骤序号不挂。
  · 题号块排斥（扩面必配）：题号块「N．（档位）」及其三段式「N．（档位·提分线·卡壳看答案）」
    （2026-08-30 起，题号后带档位全角括号）不是条目，
    一律跳过——讲练件/衔接件题号流天然排除。退化真题卷件题号块「N．」无档位者与条目同形，
    本工具不适用该类件（不传入即可）。

判定与行为：
  · 条目题名行＝body 级段落全文匹配 ^\\d+． 且非题号块形态（^\\d+．（档位〔·提分线·卡壳看答案〕））；
  · 第一子层＝body 级段落 ^（\\d+） 且位于条目语境：自最近条目题名行（或同条目内）起、未遇
    标题段（N.N(.N)+ 空格起段／讲部形）与题号块，且其间未出现 ①② 层（出现即转入更深层，
    其后复用（N）不挂——编号唯一层形·逐层换形条款）；
  · 条目号/（N）与题名同 run → 拆独立 run；跨多 run → 归并单一 run（零字符增删）；
  · 已挂（恰有一独立 C7C7C7 run）→ 跳过并计数（幂等）；底纹 run 强制去加粗；
  · 修改的 w:t 一律置 xml:space="preserve" 防吞空格。
输出：登记 md（条目号→条目名首句＋第一子层清单）＋stdout 计数与恒等式断言。

用法: python 条目号底纹.py <docx> <登记md>
"""
import sys, io, os, re, zipfile, shutil, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

FILL = 'C7C7C7'
ENT_RE = re.compile(r'^(\d+)．')                       # 条目号：数字＋全角句点
# 题号块（题号＋档位全角括号）——排斥；2026-08-30 起兼容三段式「N．（档位·提分线·卡壳看答案）」
QBLOCK_RE = re.compile(r'^\d+．（(?:简单|中档|难)(?:·(?:保60%|保80%|冲100%)·卡壳看答案)?）')
SUB_RE = re.compile(r'^（\d+）')                        # 条目第一子层（全角括号）
HEAD_RE = re.compile(r'^\d+(?:\.\d+){1,6}(?:\s|方法讲解)')  # 节/讲部/题型标题段
CIRC_RE = re.compile(r'^[①②③④⑤⑥⑦⑧⑨⑩]')            # 第二子层①②（逐层换形：其后（N）不挂）

def run_text(r):
    return ''.join(t.text or '' for t in r.findall(q('t')))

def set_run_text(r, txt):
    """run 文字整体替换（多个 w:t 归一为一个，置 preserve）。"""
    for t in r.findall(q('t')):
        r.remove(t)
    t = etree.SubElement(r, q('t'))
    t.text = txt
    if txt != txt.strip() or txt == '':
        t.set(XMLSPACE, 'preserve')
    return t

def ensure_shd(r):
    """run 补 w:shd C7C7C7（缺才补；schema 序：vertAlign/rtl/lang 等尾部元素之前、否则末尾）。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr'))
        r.insert(0, rpr)
    shd = rpr.find(q('shd'))
    if shd is None:
        shd = etree.Element(q('shd'))
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
        anchor = None
        for name in ('vertAlign', 'rtl', 'lang', 'eastAsianLayout', 'specVanish', 'oMath'):
            e = rpr.find(q(name))
            if e is not None:
                anchor = e
                break
        if anchor is not None:
            anchor.addprevious(shd)
        else:
            rpr.append(shd)
    else:
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
    return shd

def strip_bold(r):
    """去加粗（不加粗口径）：删 w:b / w:bCs。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        return
    for name in ('b', 'bCs'):
        e = rpr.find(q(name))
        if e is not None:
            rpr.remove(e)

def is_shaded(r):
    rpr = r.find(q('rPr'))
    shd = rpr.find(q('shd')) if rpr is not None else None
    return shd is not None and shd.get(q('fill')) == FILL

def _first_runs_text(p):
    """段内 run 直子级 [(run, text)]。"""
    return [(c, run_text(c)) for c in p if tag(c) == 'r']

def isolate_prefix(p, need):
    """把段首 [0,need) 字符隔离为单一独立 run（跨多 run 归并、边界拆分、零字符增删）。
    返回 (目标run, 其余文本run列表)；其余文本为空时不留 run。幂等口径由调用方判定。"""
    runs = _first_runs_text(p)
    covered = []
    off = 0
    for r, tx in runs:
        if not tx:
            continue
        covered.append((r, tx))
        off += len(tx)
        if off >= need:
            break
    assert covered and off >= need, '段首前缀未落在文本run内（跨 run 碎裂超限需人工归并）'
    first_r = covered[0][0]
    total = sum(len(tx) for _, tx in covered)
    last_r, last_tx = covered[-1]
    if total > need:
        cut = need - (total - len(last_tx))
        rest = last_tx[cut:]
        set_run_text(last_r, last_tx[:cut])
        nr = etree.fromstring(etree.tostring(last_r))   # 深拷（带 rPr；shd 剥掉）
        nrpr = nr.find(q('rPr'))
        if nrpr is not None:
            nshd = nrpr.find(q('shd'))
            if nshd is not None:
                nrpr.remove(nshd)
        set_run_text(nr, rest)
        last_r.addnext(nr)
    if len(covered) > 1:
        set_run_text(first_r, ''.join(tx for _, tx in covered)[:need])
        for r, _ in covered[1:]:
            p.remove(r)
    assert len(run_text(first_r)) == need
    return first_r

def process_entry(p):
    """条目题名行：返回 'skip'（已挂幂等）| 'done'（本轮新挂/拆分/归并）。"""
    full = ''.join(t.text or '' for t in p.iter(q('t')))
    m = ENT_RE.match(full)
    assert m and not QBLOCK_RE.match(full)
    target = m.group(0)
    for r, tx in _first_runs_text(p):
        if tx:
            if tx == target and is_shaded(r):
                strip_bold(r)
                return 'skip'
            break
    base = isolate_prefix(p, len(target))
    ensure_shd(base)
    strip_bold(base)
    return 'done'

def process_sub(p):
    """条目第一子层段：「（N）」前缀挂底纹。返回 'skip' | 'done'。"""
    m = SUB_RE.match(''.join(t.text or '' for t in p.iter(q('t'))))
    assert m
    target = m.group(0)
    for r, tx in _first_runs_text(p):
        if tx:
            if tx == target and is_shaded(r):
                strip_bold(r)
                return 'skip'
            break
    base = isolate_prefix(p, len(target))
    ensure_shd(base)
    strip_bold(base)
    return 'done'

def first_sentence(title):
    """条目名首句：题名文字至第一个全角句号（含）；无句号取前40字。"""
    title = title.strip()
    i = title.find('。')
    return title[:i + 1] if i >= 0 else title[:40]

def main(path, regmd):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    rows = []          # (条目号, 条目名首句)
    sub_rows = []      # （第一子层序号, 首句, 所属条目号）
    n_done = n_skip = s_done = s_skip = 0
    n_qblk_excl = 0
    # 条目语境状态机：entry_active=最近条目题名行以来未遇标题/题号块；deep=①②层已出现；
    #   表格属条目内容、不打断语境；deep 后的（N）若续外层序号（＝上层末号＋1）仍计第一子层
    #   （①②为其上层项内的行内步骤——I件（3）①②→（4）实测例），隔层重启（1）不计。
    entry_active = False
    deep = False
    last_sub_no = 0
    cur_ent = '?'
    for p in body:
        if p.tag != q('p'):
            continue                      # 表格＝条目内容，不打断条目语境（D件（1）表格→（2）实测例）
        full = ''.join(t.text or '' for t in p.iter(q('t')))
        if QBLOCK_RE.match(full):
            entry_active = False
            deep = False
            n_qblk_excl += 1
            continue
        if ENT_RE.match(full):
            num = ENT_RE.match(full).group(0)
            st = process_entry(p)
            if st == 'skip':
                n_skip += 1
            else:
                n_done += 1
            rows.append((num, first_sentence(full[len(num):])))
            entry_active = True
            deep = False
            last_sub_no = 0
            cur_ent = num
            continue
        if HEAD_RE.match(full):
            entry_active = False
            deep = False
            last_sub_no = 0
            continue
        if CIRC_RE.match(full):
            deep = True
            continue
        if SUB_RE.match(full) and entry_active:
            num = SUB_RE.match(full).group(0)
            no = int(num[1:-1])
            if deep and no != last_sub_no + 1:
                continue                  # ①②层之下的隔层复用（N）——不挂
            st = process_sub(p)
            if st == 'skip':
                s_skip += 1
            else:
                s_done += 1
            sub_rows.append((num, first_sentence(full[len(num):]), cur_ent))
            deep = False
            last_sub_no = no
    n_total = len(rows)
    s_total = len(sub_rows)
    # 恒等式断言：条目号底纹 run 数＝条目计数；第一子层底纹 run 数＝第一子层计数
    ent_runs = sub_runs = 0
    for p in body:
        if p.tag != q('p'):
            continue
        for r in p.findall(q('r')):
            tx = run_text(r)
            if tx and re.match(r'^\d+．$', tx) and is_shaded(r):
                ent_runs += 1
            elif tx and re.match(r'^（\d+）$', tx) and is_shaded(r):
                sub_runs += 1
    ok = (ent_runs == n_total == n_done + n_skip) and (sub_runs == s_total == s_done + s_skip)
    # 落盘 docx（仅替换 word/document.xml，其余成员原样回写）
    new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    fd, tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(path)))
    os.close(fd)
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
            zout.writestr(item, data)
    shutil.move(tmp, path)
    # 登记 md
    lines = []
    lines.append('# 条目号＋第一子层底纹登记 — %s' % os.path.basename(path))
    lines.append('')
    lines.append('轮次：成书形态回扫轮 2026-08-29（公共规则§7条目号底纹扩面＋条目第一子层底纹新拍板：')
    lines.append('C7C7C7、不加粗、只盖条目号/（N）本身；题号块「N．（档位）」排斥；第二子层①②后')
    lines.append('复用（N）与题目小问半角(1)(2)不挂；恒等式＝条目号底纹 run 数＝条目计数、第一子层')
    lines.append('底纹 run 数＝第一子层计数）')
    lines.append('')
    lines.append('条目计数 %d（新挂 %d｜已挂跳过 %d）｜条目号底纹 run 数 %d｜'
                 '第一子层计数 %d（新挂 %d｜已挂跳过 %d）｜第一子层底纹 run 数 %d｜'
                 '题号块排斥段 %d｜恒等式 %s'
                 % (n_total, n_done, n_skip, ent_runs, s_total, s_done, s_skip, sub_runs,
                    n_qblk_excl, '成立' if ok else '不成立!!'))
    lines.append('')
    lines.append('| 条目号 | 条目名首句 |')
    lines.append('|---|---|')
    for num, sent in rows:
        lines.append('| %s | %s |' % (num, sent.replace('|', '\\|')))
    lines.append('')
    if sub_rows:
        lines.append('| 第一子层 | 所属条目 | 首句 |')
        lines.append('|---|---|---|')
        for num, sent, ent in sub_rows:
            lines.append('| %s | %s | %s |' % (num, ent, sent.replace('|', '\\|')))
        lines.append('')
    open(regmd, 'w', encoding='utf-8').write('\n'.join(lines))
    print('条目计数 %d = 新挂 %d ＋ 已挂跳过 %d；条目号底纹 run %d；'
          '第一子层计数 %d = 新挂 %d ＋ 已挂跳过 %d；第一子层底纹 run %d；题号块排斥 %d；恒等式%s'
          % (n_total, n_done, n_skip, ent_runs, s_total, s_done, s_skip, sub_runs,
             n_qblk_excl, '成立 PASS' if ok else '不成立 CHECK'))
    print('登记md -> %s' % regmd)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
