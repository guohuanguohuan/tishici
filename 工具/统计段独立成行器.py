# -*- coding: utf-8 -*-
r"""统计段独立成行器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·T3（工具先建后用）

口径（规格书T3）：节标题行末／题型标题行末的统计段拆分为紧跟其后的独立普通段落（标题行独占一行）；
  题型统计段内题号区间简写「-m～n」——省略与行首题型号重复的父链前缀
  （如「2.4.1.2-1～2」→「-1～2」；实测现行全链形「1.1.1.8-7～1.1.1.8-8」→「-7～8」，
   左端保留引导连字符「-7」、右端剥前缀与连字符得「8」，与规格书样例一致）。
  节统计段「　本节N题：简单a｜中档b｜难c（｜提分线：…）」整段随拆分迁出，文本不变。
  衔接件「　本节N题」同拆。知识清单件无统计段（0 处置登记）。
  新统计段＝无 pPr 普通段、正文默认字号（源 run 剥 b/sz/shd）。

识别：节标题段＝段级底纹 ADC2DA＋节号 pattern（^\d+\.\d+(\.\d+)?\s，排除 JieMingMao 1pt 锚段——
  其无 ADC2DA 底纹天然排除）；题型标题段＝段级底纹 C6D4E3＋父链续层序号起段＋行内「　N题：」。
  幂等：标题行无行内统计段且紧随其后已是独立统计段（^本节\d+题 ／ ^\d+题：）→ 幂等跳过计数。
断言：拆分后统计段总数＝拆分前（行内＋已独立）统计段总数；
      题数恒等式不破坏——逐节：节内各题型统计段题数之和＝节统计段题数（前置恒等，输入违反即硬停）；
      零意外字符：标题行残文＋新统计段文字拼接＝原标题行文字（去引导全角空格）。
模式：默认就地改写（留 .bak_统计段拆）；--dry-run 出分布报告不落盘。
用法:
  python 工具/统计段独立成行器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None

SEC_TTL_RE = re.compile(r'^(\d+\.\d+(?:\.\d+)?)[\s　]+\S')
GRP_TTL_RE = re.compile(r'^(\d+(?:\.\d+)+)[\s　]+\S')
STATS_MARK_RE = re.compile(r'　((?:本节)?\d+题[:：]?)')
SEC_STANDALONE_RE = re.compile(r'^本节\d+题')
GRP_STANDALONE_RE = re.compile(r'^\d+题：')
SECNUM_RE = re.compile(r'^本节(\d+)题')
GRPNUM_RE = re.compile(r'^(\d+)题：')
TOKEN_RE = re.compile(r'(\d+(?:\.\d+)+)-(\d+)')


def wt_nodes(p):
    return [t for t in p.iter(q('t'))]


def del_span(p, a, b):
    """删除段内 w:t 文本流 [a,b)；删空且无其他内容的 run 一并移除。返回删除文本。"""
    off = 0
    removed = ''
    for r in list(p.findall(q('r'))):
        ts = r.findall(q('t'))
        if not ts:
            continue
        txt = ''.join(t.text or '' for t in ts)
        ra, rb = off, off + len(txt)
        off = rb
        if rb <= a or ra >= b:
            continue
        cs, ce = max(a - ra, 0), min(b - ra, len(txt))
        removed += txt[cs:ce]
        keep = txt[:cs] + txt[ce:]
        ts[0].text = keep
        ts[0].set(XMLSPACE, 'preserve')
        for t in ts[1:]:
            t.text = ''
        if not keep:
            others = [c for c in r if tag(c) not in ('rPr', 't')]
            if not others:
                p.remove(r)
    return removed


def abbreviate(stat, grp_no):
    """题型统计段题号简写：「G-m～G-n」→「-m～n」；「G-m」→「-m」。前缀≠G 的 token 原样保留并计数。"""
    out = []
    pos = 0
    alien = 0
    for m in TOKEN_RE.finditer(stat):
        out.append(stat[pos:m.start()])
        if m.group(1) == grp_no:
            # 左端（紧随「题：」或区间中第二端）皆简写；区间右端剥「G-」整体
            out.append('-' + m.group(2) if stat[max(0, m.start() - 1):m.start()] != '～' else m.group(2))
        else:
            out.append(m.group(0))
            alien += 1
        pos = m.end()
    out.append(stat[pos:])
    return ''.join(out), alien


def make_stats_para(text, src_p):
    """新普通统计段：无 pPr；run 剥 b/sz/shd（正文默认字号）。"""
    np = etree.Element(q('p'))
    r = etree.SubElement(np, q('r'))
    # 取源段首个非空 run 的 rPr 作字体基底（东亚字体随文档默认）
    for sr in src_p.findall(q('r')):
        rpr = sr.find(q('rPr'))
        if rpr is not None:
            import copy
            nr = copy.deepcopy(rpr)
            for t in ('b', 'bCs', 'sz', 'szCs', 'shd'):
                e = nr.find(q(t))
                if e is not None:
                    nr.remove(e)
            if len(nr) or nr.attrib:
                r.append(nr)
            break
    t = etree.SubElement(r, q('t'))
    t.text = text
    t.set(XMLSPACE, 'preserve')
    return np


def process(path, dry):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    els = list(body)
    n = len(els)

    # ---- 第一遍：恒等式前置核验（节统计题数 ＝ 节内题型统计题数之和） ----
    pre_stats = 0           # 行内统计段数
    pre_standalone = 0      # 已独立统计段数
    identity_bad = []
    cur_sec = None          # (节号, 本节N题) —— 仅带统计段的节标题入帐
    grp_sum = 0
    sec_pending = None
    sec_rows = []           # (节号, 本节N, 组题数和)
    def close_sec():
        nonlocal sec_pending, grp_sum
        if sec_pending is not None:
            sec_rows.append((sec_pending[0], sec_pending[1], grp_sum))
        sec_pending = None
        grp_sum = 0
    for i, c in enumerate(els):
        if c.tag != q('p'):
            continue
        txt = ptext(c)
        f = pfill(c)
        m = STATS_MARK_RE.search(txt)
        if f == 'ADC2DA' and SEC_TTL_RE.match(txt):
            close_sec()
            if m and SECNUM_RE.match(txt[m.start() + 1:]):
                sec_pending = (SEC_TTL_RE.match(txt).group(1), int(SECNUM_RE.match(txt[m.start() + 1:]).group(1)))
                pre_stats += 1
            elif i + 1 < n and els[i + 1].tag == q('p') and SEC_STANDALONE_RE.match(ptext(els[i + 1]).strip()):
                sec_pending = (SEC_TTL_RE.match(txt).group(1), int(SECNUM_RE.match(ptext(els[i + 1]).strip()).group(1)))
                pre_standalone += 1
            continue
        if f == 'C6D4E3' and GRP_TTL_RE.match(txt):
            if m and GRPNUM_RE.match(txt[m.start() + 1:]):
                grp_sum += int(GRPNUM_RE.match(txt[m.start() + 1:]).group(1))
                pre_stats += 1
            elif i + 1 < n and els[i + 1].tag == q('p') and GRP_STANDALONE_RE.match(ptext(els[i + 1]).strip()):
                grp_sum += int(GRPNUM_RE.match(ptext(els[i + 1]).strip()).group(1))
                pre_standalone += 1
            continue
    close_sec()
    for secno, secn, gsum in sec_rows:
        if secn != gsum:
            identity_bad.append('节%s：本节%d题 ≠ 题型统计之和%d' % (secno, secn, gsum))
    if identity_bad:
        raise AssertionError('题数恒等式前置核验失败（输入侧已破坏，先修数据源）: %s' % '；'.join(identity_bad))

    # ---- 第二遍：拆分 ----
    n_split_sec = n_split_grp = n_keep = n_abbrev = n_alien = 0
    split_rows = []
    i = 0
    while i < len(els):
        c = els[i]
        if c.tag != q('p'):
            i += 1
            continue
        txt = ptext(c)
        f = pfill(c)
        kind = None
        if f == 'ADC2DA' and SEC_TTL_RE.match(txt):
            kind = '节'
        elif f == 'C6D4E3' and GRP_TTL_RE.match(txt):
            kind = '题型'
        if kind is None:
            i += 1
            continue
        m = STATS_MARK_RE.search(txt)
        if m and (SECNUM_RE.match(txt[m.start() + 1:]) or GRPNUM_RE.match(txt[m.start() + 1:])):
            stat_text = txt[m.start() + 1:]
            grp_no = GRP_TTL_RE.match(txt).group(1) if kind == '题型' else None
            if kind == '题型':
                stat_text, alien = abbreviate(stat_text, grp_no)
                if alien:
                    n_alien += alien
            removed = del_span(c, m.start(), len(txt))
            assert removed == txt[m.start():], '统计段删除文本不符'
            assert ptext(c) + removed == txt, '零意外字符断言失败: %r' % ptext(c)[:60]
            nxt = c.getnext()
            nxt_text = ptext(nxt).strip() if nxt is not None and nxt.tag == q('p') else ''
            if (kind == '节' and SEC_STANDALONE_RE.match(nxt_text)) or (kind == '题型' and GRP_STANDALONE_RE.match(nxt_text)):
                raise RuntimeError('标题行内统计段与既有独立统计段并存（重复挂载），人工核查: %r' % txt[:50])
            c.addnext(make_stats_para(stat_text, c))
            if kind == '节':
                n_split_sec += 1
            else:
                n_split_grp += 1
                n_abbrev += 1
            split_rows.append((kind, txt[:m.start()][:46], stat_text[:46]))
            i += 2
            continue
        # 幂等：紧随其后已独立统计段
        nxt = c.getnext()
        nxt_text = ptext(nxt).strip() if nxt is not None and nxt.tag == q('p') else ''
        if (kind == '节' and SEC_STANDALONE_RE.match(nxt_text)) or (kind == '题型' and GRP_STANDALONE_RE.match(nxt_text)):
            if kind == '题型':
                grp_no = GRP_TTL_RE.match(txt).group(1)
                old = ptext(nxt)
                new, alien = abbreviate(old.strip(), grp_no)
                if alien:
                    n_alien += alien
                if new != old.strip():
                    ts = wt_nodes(nxt)
                    # 独立统计段整段文本替换（单 run 承接）
                    ts[0].text = new
                    ts[0].set(XMLSPACE, 'preserve')
                    for t in ts[1:]:
                        t.text = ''
            n_keep += 1
        i += 1

    # ---- 断言：统计段总数守恒 ----
    post_stats = 0
    for c in body.iter(q('p')):
        t = ptext(c).strip()
        if SEC_STANDALONE_RE.match(t) or GRP_STANDALONE_RE.match(t):
            post_stats += 1
    total_pre = pre_stats + pre_standalone
    if post_stats != total_pre:
        raise AssertionError('统计段总数不守恒: 前%d（行内%d＋独立%d）→ 后%d' % (total_pre, pre_stats, pre_standalone, post_stats))

    lines = []
    lines.append('## T3 统计段独立成行器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    lines.append('拆分：节统计段 %d｜题型统计段 %d（含区间简写 %d）｜幂等跳过（已独立）%d｜统计段总数 前%d→后%d 守恒 PASS'
                 % (n_split_sec, n_split_grp, n_abbrev, n_keep, total_pre, post_stats))
    lines.append('题数恒等式：%s（%d 节核验）' % ('PASS' if not identity_bad else 'FAIL', len(sec_rows)))
    if n_alien:
        lines.append('  ! 父链前缀与行首题型号不符的区间 token %d 处（原样保留，交人工）' % n_alien)
    for k, a, b in split_rows[:8]:
        lines.append('  [%s] %s ⇒ %s' % (k, a, b))
    if len(split_rows) > 8:
        lines.append('  …共 %d 处拆分' % len(split_rows))
    lines.append('')

    if not dry and (n_split_sec or n_split_grp):
        import shutil
        bak = path + '.bak_统计段拆'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.t3tmp'
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
    return '\n'.join(lines)


def main():
    argv = sys.argv[1:]
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    report = None
    if '--report' in argv:
        k = argv.index('--report'); report = argv[k + 1]; del argv[k:k + 2]
    assert argv, '用法: python 工具/统计段独立成行器.py <docx...> [--dry-run] [--report r.md]'
    out = []
    for path in argv:
        r = process(path, dry)
        out.append(r)
        print(r)
    if report:
        with open(report, 'a', encoding='utf-8') as f:
            f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
