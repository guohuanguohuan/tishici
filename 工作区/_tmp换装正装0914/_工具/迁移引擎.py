# -*- coding: utf-8 -*-
r"""迁移引擎.py — M2 导学本 12 件批插（锚点迁移法·副本树正装·2026-09-14 波1）。

依据：_tmp换装预备0913/换装方案草案.md §1＋正装三裁①②③；副本树/试迁报告.md 规约 R1/R2/R3；
     副本树-测评本/试迁报告-测评本.md（\ov 随值迁入件内＋钉后版 qp-m3 两补钉）。
红线：零 git；M2/P1 正件只读一个字符不动；写入仅限 工作区/_tmp换装正装0914/；
     main.src.tex＝预迁移快照（验收 diff 面），main.tex＝换装件。

三裁兑现：
  ①纯题版孤行抑制：\bindp {\kaishu ②/③ 独立段改 \bindpx（件内定义，\ifshowans 门控）。
  ②qp-m3 本地挂载：钉后版 md5 7c3930362be8a0a2bdf21bbf8ac16573（两补钉随版）。
  ③衔接填空补键随迁：课时01 衔接位组尾 ansblock，键＝导-课时01-衔接填空，值＝body.tex \ansline{衔接填空} 逐字。
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 册解析 import parse_book, split_group, read, SNAP, QP_M3_MD5  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # _tmp换装正装0914
TREE = os.path.join(HERE, 'M2导学本')
KS = ['课时%02d' % i for i in range(1, 11)] + ['衔接节-1.2.1前', '章末-本章总结提升']
BODY_EXTRA = {}


# ---------- qp-m3 宏/长度集（撞名预删判据）＋定义体抓取 ----------
def qpm3_defs():
    sty = read(os.path.join(TREE, '课时01', 'qp-m3.sty'))
    names, bodies = set(), {}
    for m in re.finditer(r'\\(?:new|re|provide)command\*?\s*(?:\{\\([A-Za-z@]+)\}|\\([A-Za-z@]+))', sty):
        names.add(m.group(1) or m.group(2))
    for m in re.finditer(r'\\def\\([A-Za-z@]+)', sty):
        names.add(m.group(1))
    for m in re.finditer(r'\\newlength\{\\([A-Za-z@]+)\}', sty):
        names.add(m.group(1))
    for m in re.finditer(r'\\newenvironment\{([A-Za-z@]+)\}', sty):
        names.add('env:' + m.group(1))
    for m in re.finditer(r'\\newif\\if([A-Za-z@]+)', sty):
        names.add('if:' + m.group(1))
    for m in re.finditer(r'\\newcommand\*?\s*\{\\([A-Za-z@]+)\}(\[\d\](\[[^\]]*\])?)?\s*\{', sty):
        depth, j = 1, m.end()
        while j < len(sty) and depth:
            if sty[j] == '{':
                depth += 1
            elif sty[j] == '}':
                depth -= 1
            j += 1
        bodies[m.group(1)] = sty[m.end():j - 1]
    return names, bodies


def norm_body(s):
    s = re.sub(r'(?<!\\)%.*$', '', s, flags=re.M)
    return re.sub(r'\s+', '', s)


def ensure_ov(tex, log):
    """迁后补查：值面 \\ov 随迁（三裁③ 补键/答案值）发生在导言换装之后，导言期 \\ov{ 探测会漏——
    此处在全部插入完成后补 \\providecommand（已注入则跳过，幂等）。"""
    if '\\ov{' in tex and '\\providecommand{\\ov}' not in tex:
        i = tex.find('\\begin{document}')
        assert i >= 0, '\\ov 补定义：\\begin{document} 未命中'
        tex = tex[:i] + ('% \\ov 系答案册 body 局部宏，随值迁入件内补定义（实测 qp-m3 无 \\ov，不撞名）\n'
                         '\\providecommand{\\ov}[1]{\\overrightarrow{#1}}\n\n') + tex[i:]
        log.append(('\\ov 补定义', '值面含 \\ov 而导言未注入 → \\begin{document} 前 \\providecommand（迁后补查）'))
    return tex


def local_defs(tex):
    """[(start,end,name,body)] — \\newcommand{\\X}[n][d]{…} 整条（体括号配平）。"""
    out = []
    for m in re.finditer(r'\\newcommand\*?\s*\{\\([A-Za-z@]+)\}(\[\d\](\[[^\]]*\])?)?\s*\{', tex):
        depth, j = 1, m.end()
        while j < len(tex) and depth:
            if tex[j] == '{':
                depth += 1
            elif tex[j] == '}':
                depth -= 1
            j += 1
        out.append((m.start(), j, m.group(1), tex[m.end():j - 1]))
    return out


# ---------- 导言换装（六宏→qp-m3＋册名回钉＋\ov＋bindpx＋撞名处置） ----------
def preamble_swap(tex, piece, m3names, m3bodies, log):
    def sub_once(old, new, tag, count=1):
        nonlocal tex
        n = tex.count(old)
        assert n == count, '锚点[%s:%s]命中 %d 次（须 %d）' % (piece, tag, n, count)
        tex = tex.replace(old, new, count)

    sub_once("""\\documentclass[fontset=none]{ctexart}
\\input{qp-fonts.tex}
\\input{qp-layout.tex}
\\input{qp-parts.tex}
\\input{qp-headfoot.tex}
\\input{qp-titles.tex}
\\input{qp-blocks.tex}""",
             "\\documentclass[fontset=none]{ctexart}\n\\usepackage{qp-m3}"
             " %% 换装：六宏→qp-m3 单包（钉后版 md5 %s，两补钉随版）" % QP_M3_MD5,
             '导言六宏→qp-m3')
    cm = list(re.finditer(r'^\\renewcommand\{\\qpceming\}\{([^}]*)\}', tex, re.M))
    assert len(cm) <= 1, '%s \\qpceming 行 %d（须 ≤1）' % (piece, len(cm))
    if cm:
        assert '选择性必修第一册' in cm[0].group(1), '%s 既有册名行非选必一：%s' % (piece, cm[0].group(1))
        log.append(('册名', '件内既有 \\qpceming 选必一行在位（不重钉）'))
    else:
        sub_once('\\renewcommand{\\qpjianming}{导学件}',
                 '\\renewcommand{\\qpjianming}{导学件}\n'
                 '\\renewcommand{\\qpceming}{高中数学\\quad 选择性必修第一册(人教B版)}'
                 ' % 换装回钉：qp-m3 默认册名＝选必二，防页脚漂移（试迁规约）',
                 '册名回钉')
    if '\\ov{' in tex:
        sub_once('\\begin{document}',
                 '% \\ov 系答案册 body 局部宏，随值迁入件内补定义（实测 qp-m3 无 \\ov，不撞名）\n'
                 '\\providecommand{\\ov}[1]{\\overrightarrow{#1}}\n\n\\begin{document}',
                 '\\ov 补定义')
    # 三裁①：纯题版孤行抑制（②操作/③收束独立 \bindp 段 → \bindpx，pure 档整段隐藏）
    n23 = len(re.findall(r'\\bindp \{\\kaishu [②③]', tex))
    if n23:
        tex = re.sub(r'\\bindp(\s*\{\\kaishu [②③])', r'\\bindpx\1', tex)
        sub_once('\\begin{document}',
                 '% 纯题版孤行抑制（正装三裁①）：小结②操作/③收束独立段，pure 档整段隐藏，含详解版不受影响\n'
                 '\\newcommand{\\bindpx}[1]{\\ifshowans\\bindp{#1}\\fi}\n\n\\begin{document}',
                 '\\bindpx 定义')
        log.append(('三裁①', '\\bindp {\\kaishu ②/③ 独立段 %d 处 → \\bindpx（pure 档隐藏）' % n23))
    # 撞名预删／改 renew（方案§1.4：等值预删；不等值件面语义优先改 \renewcommand）
    # 先收齐全部编辑区间，按起点倒序一次性套用——边扫边改会使后续区间失位（课时01 实证）
    dropped, renewed, edits = [], [], []
    for st, en, name, body in local_defs(tex):
        if name in m3names:
            if norm_body(body) == norm_body(m3bodies.get(name, '\x00')):
                edits.append((st, en, '%% 局部宏 \\%s 已由 qp-m3 收编（等值定义），依换装方案§1.4 预删防撞名' % name))
                dropped.append(name)
            else:
                edits.append((st, st + len('\\newcommand'), '\\renewcommand'))
                renewed.append(name)
    for m in re.finditer(r'(?m)^\\newlength\{\\([A-Za-z@]+)\}\s*$', tex):
        if m.group(1) in m3names:
            edits.append((m.start(), m.end(), '%% 长度 \\%s 已由 qp-m3 分配，预删防重复定义' % m.group(1)))
            dropped.append('len:' + m.group(1))
    for st, en, rep in sorted(edits, key=lambda e: e[0], reverse=True):
        tex = tex[:st] + rep + tex[en:]
    if dropped or renewed:
        log.append(('撞名处置', '预删：%s｜renew（不等值·件面语义优先）：%s'
                    % ('，'.join(dropped) or '无', '，'.join(renewed) or '无')))
    return tex


# ---------- 通用插入 ----------
def block(key, label, value, inner, extra_lines=()):
    """ansblock 体：编译锚[键]＋源层锚 % ans:键＋内件宏（ansitem=数字标签｜ansnote=CJK 标签·R3）。"""
    b = '\\begin{ansblock}[%s]\n%% ans:%s\n' % (key, key)
    b += ('\\ansitem{%s}{%s}' % (label, value)) if inner == 'ansitem' \
        else ('\\ansnote{%s}{%s}' % (label, value))
    for el in extra_lines:
        b += '\n' + el
    return b + '\n\\end{ansblock}'


def insert_before(tex, idx, s):
    return tex[:idx] + s + '\n\n' + tex[idx:]


def insert_after_line(tex, idx, s):
    eol = tex.index('\n', idx) + 1
    return tex[:eol] + '\n' + s + '\n' + tex[eol:]


def find1(tex, pat, start, tag, stop=None):
    i = tex.find(pat, start)
    assert i >= 0, '锚未命中：%s' % tag
    if stop is not None:
        assert i < stop, '锚越界：%s（@%d ≥ 界 %d）' % (tag, i, stop)
    return i


def kv_of(k, kmap, P):
    """键→(值, 附行列表)；成组附行（解析）只挂组首键，余键不重复承载。"""
    g = kmap[k]
    if len(g['keys']) == 1:
        return g['value'], g['extra']
    sp, unc = split_group(g, P)
    assert unc is None, '拆分不确定（禁猜停件）：%s' % unc
    extra = g['extra'] if g['keys'][0] == k else []
    return sp[k], extra
