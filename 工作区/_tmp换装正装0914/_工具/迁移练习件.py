# -*- coding: utf-8 -*-
r"""迁移练习件.py — M2 练习本 12 件批插（锚点迁移法·副本树正装·2026-09-14 波2）。

依据：换装方案草案 §1.2 练习/拓展件行（题锚＝\tihao{n} 块尾·书写位不废；长详解括线模判据）＋
     试迁报告-练习本 §一（\xiexwei 后插、\anshang 双位档块内局部、解析 6 处随迁、收编宏 7 件删除、
     页脚三件保留）＋§六（页脚四名 renew 必查、\qpceming 回钉）＋义务总表 §一.2（319 键；
     练习件无 \vbox 回流核 0；尾块 12 处）＋正装三裁①②。
红线：零 git；M2/P1 正件只读一个字符不动；写入仅限 工作区/_tmp换装正装0914/；
     main.src.tex＝预迁移快照（验收 diff 面），main.tex＝换装件。
括线模判据（承重墙）：块体估高 >8 行（47 半角位/行）或含 display 数学/表格/图 →
     \ansblockgrayfalse 强制（上下 hairline 可跨栏）；短答灰底默认。
"""
import hashlib
import io
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 册解析练习 import parse_book_lt, QP_M3_SRC, QP_M3_MD5  # noqa: E402
from 迁移引擎 import (qpm3_defs, norm_body, local_defs, insert_before,  # noqa: E402
                     find1, ensure_ov, QP_M3_MD5 as MD5_REEXPORT)

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # _tmp换装正装0914
TREE = os.path.join(HERE, 'M2练习本')
SRC = r'C:/提示词/工作区/M2-第1章量产0911/成卷'
MODULES = ['qp-fonts.tex', 'qp-layout.tex', 'qp-parts.tex', 'qp-headfoot.tex',
           'qp-titles.tex', 'qp-blocks.tex', 'render.py']
PIECES_LX = ['课时%02d' % i for i in range(1, 11)]
PIECES_TUO = ['上册', '下册']
COPY_FILES = ('main.tex',) + tuple(MODULES) + ('main.pdf',)

RE_TIHAO_N = lambda n: re.compile(r'\\tihao(?:\[[^\]]*\])?\{%d\}(?!\d)' % n)
RE_DISPLAY = re.compile(r'\\\[|\\begin\{(?:align|tabular|figure|array)|includegraphics|\\tu\{|\\ansfig')
LINE_UNITS = 47        # 84mm 双栏栏宽 ÷ 10.09pt 半字位 ≈ 47 半角位/行
RULED_LINES = 8        # 承重墙判据：估高 >8 行 → 括线模强制


def est_lines(s):
    t = re.sub(r'\\[a-zA-Z]+', ' ', s)
    t = re.sub(r'[{}$~]', '', t)
    w = sum(2 if ord(c) > 0x2e7f else 1 for c in t)
    return max(1, -(-w // LINE_UNITS))


def setup_tree():
    """12 件目录就位：源件拷贝（main.tex 双名＝src 快照＋待迁件、六模块、render.py、原印面 main.pdf）
    ＋qp-m3 钉后版本地挂载（md5 断言）。figs/ 整树随迁。"""
    h = hashlib.md5()
    with open(QP_M3_SRC, 'rb') as f:
        h.update(f.read())
    assert h.hexdigest() == QP_M3_MD5, 'qp-m3 钉后版 md5 断言破：%s' % h.hexdigest()
    for piece in PIECES_LX + PIECES_TUO:
        srcdir = os.path.join(SRC, '练习件' if piece in PIECES_LX else '拓展册', piece)
        d = os.path.join(TREE, piece)
        os.makedirs(d, exist_ok=True)
        for fn in COPY_FILES:
            shutil.copyfile(os.path.join(srcdir, fn), os.path.join(d, fn))
        shutil.copyfile(QP_M3_SRC, os.path.join(d, 'qp-m3.sty'))
        shutil.copyfile(os.path.join(srcdir, 'main.tex'), os.path.join(d, 'main.src.tex'))
        fsrc = os.path.join(srcdir, 'figs')
        fdst = os.path.join(d, 'figs')
        if os.path.isdir(fsrc) and not os.path.isdir(fdst):
            shutil.copytree(fsrc, fdst)
    return len(PIECES_LX + PIECES_TUO)


def block_end(tex, start, bounds):
    """题块终结位：bounds 各自 start 后首现的最小者，回走空行至末个非空行尾（插入点）。"""
    cands = [x for x in (tex.find(b, start) for b in bounds) if x > start]
    assert cands, '块尾界未命中（start=%d）' % start
    j = min(cands)
    while j > start and tex[j - 1] in '\n\r':
        j -= 1
    return j


def insert_block(tex, j, btxt):
    """插于末非空行后：块紧贴题块（试迁同形），块后恒一空行。"""
    k = j
    while k < len(tex) and tex[k] in '\n\r':
        k += 1
    return tex[:j] + '\n' + btxt + '\n\n' + tex[k:]


def ansblock(key, label, value, extras, anshang76, comment):
    b = '\\begin{ansblock}[%s]\n%% ans:%s\n' % (key, key)
    if anshang76:
        b += '\\setlength{\\anshang}{7.6mm}%% %s（照答案册同值，块内局部）\n' % comment
    b += '\\ansitem{%s}{%s}' % (label, value)
    for tag, v in extras:
        b += '\n\\ansnote{%s}{%s}' % (tag, v)
    return b + '\n\\end{ansblock}'


def preamble_swap_lt(tex, piece, jianming, m3names, m3bodies, log):
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
        anchor = '\\renewcommand{\\qpjianming}{%s}' % jianming
        sub_once(anchor,
                 anchor + '\n'
                 '\\renewcommand{\\qpceming}{高中数学\\quad 选择性必修第一册(人教B版)}'
                 ' % 换装回钉：qp-m3 默认册名＝选必二，防页脚漂移（试迁规约·试迁报告§四 B3 实证必改）',
                 '册名回钉')
    # 撞名预删／改 renew（等值预删；不等值件面语义优先 renew）——区间倒序一次套用（波1 六缺陷修法在案）
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


def tailfill_tail(tex, piece, log):
    m = re.search(r'\\end\{multicols\}\s*\n\\end\{document\}\s*$', tex)
    assert m, '%s 件尾锚（末 \\end{multicols}＋\\end{document}）未命中' % piece
    tex = tex[:m.start()] + '\\end{multicols}\n\n\\tailfill\n\\end{document}\n' + tex[m.end():]
    log.append(('尾块', '\\tailfill 于 \\end{multicols} 后·\\end{document} 前（\\iftailfillused 装配断言面；'
                        '正装口径＝波1 同款——试迁 §二.5 栏内贴尾形经三零门实证卡栏溢出'
                        '（课时10 pure Overfull 27.99pt），装配轮待裁销项）'))
    return tex


def migrate_lian(piece, kmap, m3names, m3bodies):
    tex = io.open(os.path.join(TREE, piece, 'main.src.tex'), encoding='utf-8').read()
    log = []
    tex = preamble_swap_lt(tex, piece, '练习件', m3names, m3bodies, log)
    P = '练-' + piece
    n_vbox = len(re.findall(r'\\vbox\b', tex))
    assert n_vbox == 0, '%s \\vbox=%d（义务总表 §一.2③ 练习件 0 处判据破·停）' % (piece, n_vbox)
    log.append(('回流核', '\\vbox %d 处（练习件无回流义务·核 0 通过）' % n_vbox))
    for n in range(1, 17):
        k = '%s-%d' % (P, n)
        g = kmap[k]
        assert g['keys'] == [k], '%s 非单键组' % k
        m = RE_TIHAO_N(n).search(tex)
        assert m, '%s \\tihao{%d} 未命中' % (piece, n)
        btxt = ansblock(k, str(n), g['value'], g['extra'], n >= 10, '题%d 起双位档' % n)
        assert not RE_DISPLAY.search(btxt) and est_lines(btxt) <= RULED_LINES, \
            '%s %s 触括线模判据（估 %d 行）而练区判短答——停核' % (piece, k, est_lines(btxt))
        j = block_end(tex, m.end(), ('\\tihao{', '\\dangbadge{', '\\end{multicols}'))
        seg = tex[m.end():j]
        anch = '\\xiexwei 书写位后' if '\\xiexwei' in seg else '题块末行后'
        tex = insert_block(tex, j, btxt)
        log.append((k, '\\tihao{%d} 块尾（%s·书写位不废）' % (n, anch), g['value'][:60]))
    tex = tailfill_tail(tex, piece, log)
    return ensure_ov(tex, log), log


def migrate_tuo(piece, rng, kmap, m3names, m3bodies):
    tex = io.open(os.path.join(TREE, piece, 'main.src.tex'), encoding='utf-8').read()
    log = []
    tex = preamble_swap_lt(tex, piece, '拓展册', m3names, m3bodies, log)
    n_vbox = len(re.findall(r'\\vbox\b', tex))
    assert n_vbox == 0, '%s \\vbox=%d（拓区回流核 0 判据破·停）' % (piece, n_vbox)
    log.append(('回流核', '\\vbox %d 处（拓展册无回流义务·核 0 通过）' % n_vbox))
    nums = [n for n in range(rng[0], rng[1] + 1) if n != 57]
    nruled = 0
    for n in nums:
        k = '拓-%03d' % n
        g = kmap[k]
        assert g['keys'] == [k], '%s 非单键组' % k
        m = RE_TIHAO_N(n).search(tex)
        assert m, '%s \\tihao{%d} 未命中' % (piece, n)
        btxt = ansblock(k, str(n), g['value'], g['extra'], n >= 10, '拓-三位号＝双位档起')
        if RE_DISPLAY.search(btxt) or est_lines(btxt) > RULED_LINES:
            btxt = '\\ansblockgrayfalse\n' + btxt + '\n\\ansblockgraytrue'
            nruled += 1
            log.append((k, '括线模强制（承重墙判据：估 %d 行＞%d 或含 display/图）' % (est_lines(btxt), RULED_LINES), g['value'][:60]))
        j = block_end(tex, m.end(), ('% 拓-', '\\zu{', '\\jietitle{', '\\end{multicols}', '\\zhangtitle{'))
        tex = insert_block(tex, j, btxt)
        log.append((k, '\\tihao{%d} 块尾（拓区随册·题后紧跟答案）' % n, g['value'][:60]))
    log.append(('括线模', '强制块 %d／%d（拓区值单行形，估高 ≤%d 行为主判据）' % (nruled, len(nums), RULED_LINES)))
    tex = tailfill_tail(tex, piece, log)
    return ensure_ov(tex, log), log


def main(argv):
    only = argv[1:]
    if not only or 'setup' in only:
        print('[树] 就位 %d 件（qp-m3 md5 %s… 断言过）' % (setup_tree(), QP_M3_MD5[:8]))
    _, _, kmap = parse_book_lt()
    m3names, m3bodies = qpm3_defs()
    todo = [p for p in PIECES_LX + PIECES_TUO
            if not only or any(t in p for t in only if t != 'setup')]
    for piece in todo:
        if piece in PIECES_LX:
            tex, log = migrate_lian(piece, kmap, m3names, m3bodies)
        else:
            tex, log = migrate_tuo(piece, (1, 58) if piece == '上册' else (59, 160),
                                   kmap, m3names, m3bodies)
        d = os.path.join(TREE, piece)
        with io.open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(tex)
        nblk = tex.count('\\begin{ansblock}')
        nanc = len(re.findall(r'^% ans:(\S+)', tex, re.M))
        with io.open(os.path.join(d, '_迁移日志.md'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('# %s 换装迁移日志（正装波2·练习本·2026-09-14）\n\n| 键/项 | 锚点 | 值 |\n|---|---|---|\n' % piece)
            for row in log:
                a, b, c = (row + ('',))[:3] if len(row) == 2 else row
                f.write('| %s | %s | %s |\n' % (a, b, str(c).replace('|', '\\|')[:120]))
            f.write('\nansblock %d｜源层锚 %d｜tailfill %d\n'
                    % (nblk, nanc, tex.count('\\tailfill')))
        print('[迁] %s：ansblock %d｜源锚 %d｜日志 %d 行' % (piece, nblk, nanc, len(log)))


if __name__ == '__main__':
    main(sys.argv)
