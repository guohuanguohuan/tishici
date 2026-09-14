# -*- coding: utf-8 -*-
"""A1 知识点错位回核·全片扫描器。
键联法：练习件 \\tihao→\\begin{ansblock}[键]；导学件 \\tjdnr/\\liB→其 ansblock 键；
同键对读 \\tieside{难度(知识点N)} vs 导学贴标{难度(知识点N)}，知识点 N 异者报错。
只读；输出逐片核销表文本。零 git。
"""
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
OUT = r'C:/提示词/工作区/_tmpM3印前处置0914/A1-逐片核销表.md'

ORDER = ['衔接节'] + ['课时%02d' % i for i in range(1, 20)] + ['课时06B']


def piece_dir(tree, pid):
    for d in os.listdir(os.path.join(CJ, tree)):
        if d == pid or d.startswith(pid + '-'):
            return os.path.join(CJ, tree, d)
    raise SystemExit('片目录未找到:%s %s' % (tree, pid))


def read(p):
    return open(os.path.join(p, 'main.tex'), encoding='utf-8').read()


def skip_ws(s, i):
    while i < len(s) and s[i] in ' \t\r\n':
        i += 1
    return i


def brace_group(s, i):
    """s[i]=='{' → (content, next_index)。花括号配平，跳过 \\{ \\}。"""
    assert s[i] == '{', s[i - 10:i + 10]
    d, j, buf = 0, i, []
    while j < len(s):
        c = s[j]
        if c == '\\' and j + 1 < len(s):
            buf.append(c)
            buf.append(s[j + 1])
            j += 2
            continue
        if c == '{':
            d += 1
            if d > 1:
                buf.append(c)
        elif c == '}':
            d -= 1
            if d == 0:
                return ''.join(buf), j + 1
            buf.append(c)
        else:
            buf.append(c)
        j += 1
    raise ValueError('花括号不配平')


def parse_args(s, i, n):
    """从 s[i]（应为 {）连读 n 个花括号组。"""
    args = []
    for _ in range(n):
        i = skip_ws(s, i)
        g, i = brace_group(s, i)
        args.append(g)
    return args, i


def find_ansblock_key(s, i, stop):
    """在 s[i:stop] 找第一个 \\begin{ansblock}[键]。"""
    m = re.compile(r'\\begin\{ansblock\}\[([^\]]+)\]').search(s, i, stop)
    return m.group(1) if m else None


def parse_practice(src):
    """→ [(题号, tieside标签, 键)]"""
    out = []
    positions = [(m.start(), m.group(1)) for m in re.finditer(r'\\tihao\{(\d+)\}', src)]
    for k, (pos, num) in enumerate(positions):
        end = positions[k + 1][0] if k + 1 < len(positions) else len(src)
        seg = src[pos:end]
        mt = re.search(r'\\tieside\{([^}]*)\}', seg)
        label = mt.group(1) if mt else ''
        key = find_ansblock_key(src, pos, end)
        out.append((int(num), label, key))
    return out


ITEM_MACROS = ('\\tjdnr', '\\liB')


def parse_guide(src):
    """→ [(席名, 贴标, 键, 分册号, 分册题名)]（例/变式席）"""
    out = []
    spots = []
    for mac in ITEM_MACROS:
        for m in re.finditer(re.escape(mac) + r'(?![a-zA-Z])', src):
            spots.append((m.start(), mac))
    spots.sort()
    cur_sec, cur_title = '', ''
    for k, (pos, mac) in enumerate(spots):
        end = spots[k + 1][0] if k + 1 < len(spots) else len(src)
        nargs = 5 if mac == '\\tjdnr' else 4
        try:
            args, after = parse_args(src, skip_ws(src, pos + len(mac)), nargs)
        except (ValueError, AssertionError):
            continue
        if mac == '\\tjdnr':
            cur_sec, cur_title = args[0], args[1]
            seat, label, body = args[2], args[3], args[4]
        else:
            seat, label, body = args[0], args[1], args[3]
        seat = re.sub(r'\\textbf|[\s{}]', '', seat)
        key = find_ansblock_key(src, after, end)
        out.append((seat, label, key, cur_sec, cur_title))
    return out


re_N = re.compile(r'知识点([一二三四五六])')
NCN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6}


def nof(label):
    m = re_N.search(label)
    return NCN[m.group(1)] if m else None


rows = []
summary = []
for pid in ORDER:
    pdir = piece_dir('练习件', pid)
    gdir = piece_dir('导学件', pid)
    prac = parse_practice(read(pdir))
    guide = parse_guide(read(gdir))
    gmap = {}
    for seat, label, key, sec, title in guide:
        if key:
            gmap[key] = (seat, label, sec, title)
    piece_rows = []
    for num, label, key in prac:
        g = gmap.get(key)
        pn = nof(label)
        if g is None:
            piece_rows.append((num, label, key, '', '', None, '', '导学侧无同键席'))
            continue
        seat, glabel, sec, title = g
        gn = nof(glabel)
        ok = (pn is not None and gn is not None and pn == gn)
        piece_rows.append((num, label, key, seat, glabel, ok, sec + title, ''))
    rows.append((pid, piece_rows))
    bad = [r for r in piece_rows if r[5] is False]
    nm = [r for r in piece_rows if r[5] is None]
    summary.append((pid, len(piece_rows), len(bad), nm))

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('# A1 知识点错位回核·逐片核销表（键联法全片扫描）\n\n')
    f.write('联接键＝题面库练键（练习件 ansblock[键] ≡ 导学件同键 ansblock[键]）；'
            '比对＝\\tieside{难度(知识点N)} vs 导学席贴标知识点 N。难度词照题面库头标第4字段（母版体例§二），不属本次回核改域。\n\n')
    nbad_total = 0
    for pid, piece_rows in rows:
        bad = [r for r in piece_rows if r[5] is False]
        nm = [r for r in piece_rows if r[5] is None]
        nbad_total += len(bad)
        f.write('## %s（练%d 题）— 错位 %d%s\n\n' % (pid, len(piece_rows), len(bad),
               ('；无匹配 %d' % len(nm)) if nm else ''))
        f.write('| 题 | 练习件贴标 | 键 | 导学席 | 导学贴标 | 分册 | N判 | 备注 |\n|---|---|---|---|---|---|---|---|\n')
        for num, label, key, seat, glabel, ok, sec, note in piece_rows:
            mark = '✓' if ok else ('✗错位' if ok is False else '？')
            f.write('| %d | %s | %s | %s | %s | %s | %s | %s |\n' % (
                num, label, key, seat, glabel, sec, mark, note))
        f.write('\n')
    f.write('## 汇总\n\n')
    for pid, n, nb, nm in summary:
        f.write('- %s：练%d 题，错位 %d%s\n' % (pid, n, nb,
               ('，无匹配 %d（%s）' % (len(nm), '、'.join('题%d %s' % (r[0], r[6]) for r in nm))) if nm else ''))
    f.write('\n**错位合计：%d**\n' % nbad_total)
print('错位合计：%d' % nbad_total)
for pid, n, nb, nm in summary:
    print('%-6s 练%d 错位%d%s' % (pid, n, nb, (' 无匹配%d' % len(nm)) if nm else ''))
