# -*- coding: utf-8 -*-
r"""makebox槽宽门.py — M3 规格书新增门（规格书-v1.md §四.4「makebox 槽宽门」）。
断言面（静态扫描 tex 源，M2 两例选项叠印红旗前移到门内）：
  ①四连排形制：每组 0.25\linewidth 槽恰 4 槽；双盒制 0.5\linewidth 槽每组 1–2 槽
    （1＝批4 拆行修复形，合法）；混形/超编＝形旗。
  ②槽墨宽：每槽内容墨宽估值 ≤ 槽宽（0.25\linewidth−0.5em 等 dimexpr 现算；
    \optII/\optIV 定槽按件内 \newcommand 实值解析，缺省承 M2 拍板 53.05/21.5mm）；
    宏尾自由参（#2/#4）可断行，不作宽断言（报告标「自由」）。
墨宽口径（宁可严报不可漏报）：中文字符（含全角、①②圈号族）≈1em；ASCII 字母数字
≈0.5em；数学片段按字符加权——变量 0.55em、关系/二元符 0.7em（含肌距）、上下标内容
×0.7、分式 max(分子,分母)+0.25em、根号内容+0.55em、向量箭头内容+0.35em（≥1em）；
基准字号＝qp-m3.sty 正文 10.09pt，行内带 \fontsize 者按行值（练件选项行 10.5pt）。
两档开关：--mode zero-fp 零误报档（默认；估值>槽宽＋2.5mm 判旗——与 bindopt 印面层
          「真侵入>2.5mm 记红」判据同源对齐，亚阈微超不旗、零误报）；
          --mode strict 严格档（估值>槽宽×0.85 即旗，宁可严报，供印前严报复核抽榜）。
用法: python 工具/makebox槽宽门.py <tex文件或目录> [--mode zero-fp|strict]
      [--linewidth-mm 84.0] [--xhang-mm 11.0] [--out 报告.txt]
  \linewidth 默认 84.0mm＝M2/M3 双栏栏宽（(210−2×17.2−7.6)/2）；测评/滚动 8 开三栏件
  传 --linewidth-mm 120。\optII/\optIV 定槽为字面 mm 值，不随 \linewidth。
退出码: 0＝全过；1＝有旗；2＝用法/输入错。红线：qp-m3.sty、M2 成卷件、工具/ 既有文件只读。
"""
import sys, io, os, re

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MM2PT = 2.84528                      # 1mm＝2.84528pt（TeX pt）
BASE_PT = 10.09                      # qp-m3.sty \normalsize 正文字号基准
K_ZEROFP, K_STRICT = 0, 0.85         # 档位哨兵（零误报）／严格档预警线系数
TOL_PT = 7.11                        # 零误报档容差＝2.5mm（bindopt 印面层真侵入红阈同源）
DEF_LW_MM, DEF_XHANG_MM, DEF_LXHANG_MM = 84.0, 13.0, 7.6
DEF_OPTII_MM, DEF_OPTIV_MM = 53.05, 21.5

# ---------------- 槽定位与行装配 ----------------
RE_COMMENT = re.compile(r'(?<!\\)%.*$')
RE_OPTDEF = re.compile(r'\\newcommand\{?\\(optI[IV])\}?\s*\[(\d)\]\s*\{')
RE_OPTCALL = re.compile(r'\\optI([IV])\s*\{')
RE_SLOT_POS = re.compile(r'\\makebox\[([^\]]+)\]\s*(?:\[([clr])\])?\s*\{')


def strip_comment(line):
    return RE_COMMENT.sub('', line.rstrip('\n')).rstrip()


def brace_balance(s):
    """净花括号平衡（跳过反斜杠转义对）。"""
    bal, i = 0, 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            i += 2
            continue
        if s[i] == '{':
            bal += 1
        elif s[i] == '}':
            bal -= 1
        i += 1
    return bal


def split_args(s, start, n):
    """从 s[start]（应为'{'）起按花括号平衡切 n 个参数；返回 [参数...] 或 None。"""
    args, i = [], start
    for _ in range(n):
        while i < len(s) and s[i] in ' \t':
            i += 1
        if i >= len(s) or s[i] != '{':
            return None
        depth, j = 0, i
        while j < len(s):
            if s[j] == '\\' and j + 1 < len(s):
                j += 2
                continue
            if s[j] == '{':
                depth += 1
            elif s[j] == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            return None
        args.append(s[i + 1:j])
        i = j + 1
    return args


def parse_optdef(text):
    """解析件内 \\newcommand{\\optII}[2]{...}：返回 (名, {参号: 槽宽mm}, 自由参序号集) 或 None。"""
    m = RE_OPTDEF.search(text)
    if not m:
        return None
    name, nargs, body = m.group(1), int(m.group(2)), text[m.end():]
    boxed = {}
    for sm in RE_SLOT_POS.finditer(body):
        w = sm.group(1).strip()
        seg = body[sm.end():]
        if not seg.startswith('#'):
            return None
        k = int(seg[1])
        wm = re.fullmatch(r'([0-9.]+)\s*mm', w)
        if not wm:
            return None
        boxed[k] = float(wm.group(1))
    if not boxed:
        return None
    free = {k for k in range(1, nargs + 1) if k not in boxed}
    return (name, boxed, free)


def parse_dimexpr_mm(spec, em_pt, lw_mm, xhang_mm, lxhang_mm):
    """dimexpr/字面宽 → mm。支持 N\\linewidth、N\\xhang、N\\lxhang、N em、N mm、N pt 加减链。"""
    spec = spec.replace('\\dimexpr', '').replace('\\relax', '').strip()
    toks = re.findall(r'([+-]?)\s*([0-9.]+)\s*(\\linewidth|\\xhang|\\lxhang|mm|em|pt)', spec)
    residue = re.sub(r'[0-9.]+\s*\\(?:linewidth|xhang|lxhang)|[0-9.]+(?:mm|em|pt)|[+\-\s]', '', spec)
    if not toks or residue:
        return None
    total = 0.0
    for sign, num, unit in toks:
        v = float(num)
        if unit == '\\linewidth':
            mm = v * lw_mm
        elif unit == '\\xhang':
            mm = v * xhang_mm
        elif unit == '\\lxhang':
            mm = v * lxhang_mm
        elif unit == 'em':
            mm = v * em_pt / MM2PT
        elif unit == 'pt':
            mm = v / MM2PT
        else:
            mm = v
        total += mm if sign != '-' else -mm
    return total


# ---------------- 墨宽估算（em 值；从严） ----------------
GREEK = set('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi '
            'omicron pi rho sigma tau upsilon phi chi psi omega vartheta varphi'.split())
REL1 = {'to': 1.0, 'rightarrow': 1.0, 'leftarrow': 1.0, 'leftrightarrow': 1.0,
        'Rightarrow': 1.0, 'Leftarrow': 1.0, 'Leftrightarrow': 1.1,
        'mapsto': 1.1, 'longrightarrow': 1.6}
RELBIN = {'approx': 0.8, 'ne': 0.7, 'neq': 0.7, 'le': 0.7, 'leq': 0.7, 'ge': 0.7, 'geq': 0.7,
          'pm': 0.7, 'mp': 0.7, 'times': 0.7, 'div': 0.7, 'cdot': 0.6, 'cup': 0.75, 'cap': 0.75,
          'in': 0.7, 'notin': 0.8, 'subset': 0.75, 'subseteq': 0.8, 'perp': 0.65,
          'parallel': 0.85, 'equiv': 0.8, 'sim': 0.75, 'propto': 0.8, 'setminus': 0.6}
INVIS = {'penalty', 'hss', 'relax', 'nobreak', 'allowbreak', 'displaystyle', 'limits',
         'nolimits', 'noindent', 'par', 'hfill', 'hfil', 'strut', 'null'}
TEXTWRAP = {'text', 'mathrm', 'mathbf', 'mathit', 'mathsf', 'mbox', 'textrm', 'operatorname'}
OVERHANG = {'overrightarrow': (0.35, 0.0), 'overleftarrow': (0.35, 0.0),
            'overline': (0.15, 0.0), 'underline': (0.12, 0.0), 'widehat': (0.2, 0.0),
            'widetilde': (0.2, 0.0)}
MATHCH = {'+': 0.7, '-': 0.65, '=': 0.7, '<': 0.7, '>': 0.7, '\u2212': 0.7, '\u00d7': 0.7,
          ',': 0.25, ';': 0.3, ':': 0.3, '!': 0.1, '.': 0.3, '(': 0.33, ')': 0.33,
          '[': 0.38, ']': 0.38, '/': 0.5, '|': 0.25, "'": 0.35, '~': 0.35, ' ': 0.35}


def char_em(ch, math):
    o = ord(ch)
    if o >= 0x2E80 or 0x1100 <= o <= 0x115F or 0x3000 <= o <= 0x303F or \
       0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFFEF or \
       0x2460 <= o <= 0x24FF or 0x2600 <= o <= 0x26FF or 0x2200 <= o <= 0x22FF or \
       0x25A0 <= o <= 0x25FF:
        return 1.0                       # 中文/全角/圈号族（qp-m3 xeCJK charclass 同口径）
    if math:
        if ch.isdigit():
            return 0.5
        if 'A' <= ch <= 'Z':
            return 0.62                  # 数学大写（Termes 实宽 0.67–0.72，从严取 0.62）
        if 'a' <= ch <= 'z':
            return 0.55
        return MATHCH.get(ch, 0.8)
    if ch.isalnum():
        return 0.5
    if ch == ' ':
        return 0.35
    if ch in '\u00b0\u2103':
        return 0.5
    if ch in '\u2212\u00d7\u00f7':
        return 0.6
    return 0.4


def ink_em(s, math, depth=0):
    """内容墨宽估值（em）。math＝当前数学模式。"""
    if depth > 24 or not s:
        return 0.0
    total, i, n = 0.0, 0, len(s)
    while i < n:
        ch = s[i]
        if ch == '\\' and i + 1 < n:
            nxt = s[i + 1]
            if nxt.isalpha():
                m = re.match(r'\\([a-zA-Z]+)', s[i:])
                name = m.group(1)
                i += m.end()
                if name == 'left' or name == 'right':
                    while i < n and s[i] in ' \t':
                        i += 1
                    if i < n and s[i] == '\\':
                        m2 = re.match(r'\\([a-zA-Z]+|.)', s[i:])
                        total += 0.55 if m2.group(1) in ('lbrace', 'rbrace') else 0.5
                        i += m2.end()
                    elif i < n:
                        total += 0.4 if s[i] != '.' else 0.0
                        i += 1
                elif name in INVIS:
                    pass
                elif name in ('quad',):
                    total += 1.0
                elif name in ('qquad',):
                    total += 2.0
                elif name in (',', ';', ':'):
                    total += 0.28
                elif name in ('thinspace', 'enspace'):
                    total += 0.4
                elif name in TEXTWRAP:
                    inner = read_group(s, i)
                    if inner is None:
                        total += 0.6
                    else:
                        arg, i = inner
                        total += ink_em(arg, False, depth + 1)
                elif name in OVERHANG:
                    inner = read_group(s, i)
                    if inner is None:
                        total += 0.9
                    else:
                        arg, i = inner
                        add, floor = OVERHANG[name]
                        total += max(ink_em(arg, math, depth + 1) + add, floor)
                elif name in ('frac', 'dfrac', 'tfrac'):
                    inner = read_group(s, i)
                    if inner is None:
                        total += 1.2
                    else:
                        num, i = inner
                        inner2 = read_group(s, i)
                        if inner2 is None:
                            total += 2.0
                        else:
                            den, i = inner2
                            total += max(ink_em(num, math, depth + 1),
                                         ink_em(den, math, depth + 1)) + 0.25
                elif name == 'sqrt':
                    j = i
                    while j < n and s[j] in ' \t':
                        j += 1
                    if j < n and s[j] == '[':
                        k = s.find(']', j)
                        i = (k + 1) if k >= 0 else j
                    inner = read_group(s, i)
                    if inner is None:
                        total += 1.0
                    else:
                        arg, i = inner
                        total += ink_em(arg, math, depth + 1) + 0.55
                elif name in ('hspace', 'kern'):
                    while i < n and s[i] == '*':
                        i += 1
                    inner = read_group(s, i)
                    if inner is not None:
                        dim, i = inner
                        dm = re.fullmatch(r'\s*([0-9.]+)\s*(mm|em|pt)', dim.strip())
                        if dm:
                            v, u = float(dm.group(1)), dm.group(2)
                            total += v / MM2PT if u == 'mm' else (v if u == 'em' else v / 10.09)
                    else:
                        i = skip_dim(s, i)
                elif name in GREEK:
                    total += 0.6
                elif name in REL1:
                    total += REL1[name]
                elif name in RELBIN:
                    total += RELBIN[name]
                elif name in ('circ', 'degree'):
                    total += 0.5
                elif name == 'prime':
                    total += 0.35
                elif name in ('sum', 'prod', 'int'):
                    total += 1.2
                elif name in ('sin', 'cos', 'tan', 'log', 'ln', 'lim', 'max', 'min'):
                    total += 0.5 * len(name)
                elif re.match(r'^[MHB]$', name):   # \MBody 等
                    total += 0.6
                else:
                    inner = read_group(s, i)
                    if inner is not None:
                        arg, i = inner
                        total += 0.6 + ink_em(arg, math, depth + 1)
                    else:
                        total += 0.6
            elif nxt in ',;:! ':
                i += 2
                total += 0.28
            elif nxt in '()':
                i += 2
                math = not math        # \( \) 数学模式开合
            elif nxt in '[]':
                i += 2                 # \[ \] 显示数学开合（槽内罕见，同制开合）
                math = not math
            elif nxt == '{':
                i += 1          # \{ 字面花括号
                total += 0.4 if math else 1.0
            elif nxt == '}':
                i += 2
                total += 0.4 if math else 1.0
            else:
                i += 2
                total += char_em(nxt, math)
        elif ch in '{}':
            i += 1
        elif ch in '^_':
            i += 1
            while i < n and s[i] in ' \t':
                i += 1
            if i < n and s[i] == '{':
                inner = read_group(s, i)
                if inner is None:
                    total += 0.8
                else:
                    arg, i = inner
                    total += 0.05 + 0.7 * ink_em(arg, math, depth + 1)
            elif i < n and s[i] == '\\':
                m2 = re.match(r'\\([a-zA-Z]+)', s[i:])
                if m2:
                    total += 0.05 + 0.7 * 0.6   # 上下标内符号：脚本字号从严 0.7×
                    i += m2.end()
                else:
                    total += 0.5
                    i += 2
            elif i < n:
                total += 0.05 + 0.7 * char_em(s[i], math)
                i += 1
        elif ch == '$':
            math = not math
            i += 1
        else:
            total += char_em(ch, math)
            i += 1
    return total


def read_group(s, i):
    """s[i] 应为'{'；返回 (组内串, 结束后下标) 或 None。"""
    if i >= len(s) or s[i] != '{':
        return None
    depth, j = 0, i
    while j < len(s):
        if s[j] == '\\' and j + 1 < len(s):
            j += 2
            continue
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return None


def skip_dim(s, i):
    m = re.match(r'\s*[0-9.]+\s*(mm|em|pt)', s[i:])
    return i + m.end() if m else i


# ---------------- 主流程 ----------------
def scan_file(path, cfg):
    """返回 (报告行列表, 槽数, 旗数, 形旗数)。"""
    rep, nslot, nflag, nform = [], 0, 0, 0
    try:
        raw = open(path, encoding='utf-8').readlines()
    except (OSError, UnicodeDecodeError) as e:
        rep.append(f'[跳过] {path}: {e}')
        return rep, 0, 0, 0
    # 行装配＝物理行剥注释（不跨行并段：\vbox 等容器跨行，并段会把多选项行并成
    # 巨行致形误报；真跨行槽/宏调用经失衡检测落形旗，现库 0 例）
    # 第一遍：件内 \optII/\optIV 定义
    defs = {}
    for lineno, text in ((i + 1, strip_comment(raw[i])) for i in range(len(raw))):
        if 'newcommand' in text and RE_OPTDEF.search(text):
            d = parse_optdef(text)
            if d:
                defs[d[0]] = d
    optii = defs.get('optII', ('optII', {1: cfg['optii_mm']}, {2}))
    optiv = defs.get('optIV', ('optIV', {1: cfg['optiv_mm'], 2: cfg['optiv_mm'], 3: cfg['optiv_mm']}, {4}))
    # 第二遍：逐行取槽
    for lineno, text in ((i + 1, strip_comment(raw[i])) for i in range(len(raw))):
        if 'makebox' not in text and '\\optI' not in text:
            continue
        if 'newcommand' in text:      # 定义行（\optII/\optIV/\ansfig 等）不作数据行
            continue
        fs = re.search(r'\\fontsize\{([0-9.]+)pt\}', text)
        em_pt = float(fs.group(1)) if fs else BASE_PT
        # —— 宏槽行（\optII/\optIV 调用）——
        row_slots = []
        for m in RE_OPTCALL.finditer(text):
            name = 'optI' + m.group(1)
            d = optiv if name == 'optIV' else optii
            boxed, free = d[1], d[2]
            args = split_args(text, m.end() - 1, len(boxed) + len(free))
            if args is None:
                nform += 1
                rep.append(f'{path}:{lineno}:{name}:形旗·参数花括号不平衡(恰{len(boxed)+len(free)}槽制)')
                continue
            if len(args) != len(boxed) + len(free):
                nform += 1
                rep.append(f'{path}:{lineno}:{name}:形旗·实参{len(args)}≠{len(boxed)}定槽+{len(free)}自由')
                continue
            for slot_i, k_arg in enumerate(sorted(set(boxed) | free), 1):
                content = args[k_arg - 1]
                if k_arg in free:
                    row_slots.append((slot_i, len(args), None, content))
                else:
                    row_slots.append((slot_i, len(args), boxed[k_arg], content))
        # —— 原生 \makebox 分数槽（四连排/双盒；裸 \linewidth 图框、\ansfig 类
        #     无数字系数盒非选项槽，不收）——
        raw_slots = []
        for m in RE_SLOT_POS.finditer(text):
            w = m.group(1)
            if not re.match(r'\s*(?:\\dimexpr\s*)?[0-9.]+\s*\\linewidth', w):
                continue
            g = read_group(text, m.end() - 1)
            if g is None:
                nform += 1
                rep.append(f'{path}:{lineno}:makebox:形旗·槽体花括号不平衡')
                continue
            raw_slots.append((w, g[0], m.start()))
        if raw_slots:
            kinds = set()
            for w, _, _ in raw_slots:
                fm = re.match(r'\s*(?:\\dimexpr\s*)?([0-9.]+)\s*\\linewidth', w)
                kinds.add(float(fm.group(1)) if fm else -1)
            cnt = len(raw_slots)
            frac = sorted(kinds)
            ok_form = (frac == [0.25] and cnt in (2, 4)) or \
                      (frac == [0.5] and cnt in (1, 2))
            if not ok_form:
                nform += 1
                rep.append(f'{path}:{lineno}:形旗·{cnt}槽/系数{frac}不合'
                           f'{{"四连排=0.25×4（拆两行制×2）", "双盒=0.5×1~2"}}制')
            for slot_i, (w, content, _) in enumerate(raw_slots, 1):
                mm = parse_dimexpr_mm(w, em_pt, cfg['lw_mm'], cfg['xhang_mm'], cfg['lxhang_mm'])
                row_slots.append((slot_i, len(raw_slots), mm, content))
        if not row_slots:
            continue
        # —— 逐槽断言（零误报档：超槽宽＋容差 2.5mm 判旗，与 bindopt 印面层真侵入阈同源；
        #     严格档：超槽宽×0.85 即旗，供印前严报复核）——
        for slot_i, n_total, slot_mm, content in row_slots:
            nslot += 1
            est_em = ink_em(content, False)
            est_pt = est_em * em_pt
            if slot_mm is None:
                rep.append(f'{path}:{lineno}:槽{slot_i}/{n_total}:自由文本(可断行·不断言) 估值{est_pt:.1f}pt:—')
                continue
            slot_pt = slot_mm * MM2PT
            if cfg['k'] == K_ZEROFP:
                line_pt, limit_pt = slot_pt, slot_pt + cfg['tol_pt']
                tag = f'超槽宽＋{cfg["tol_pt"]:.1f}pt容差'
            else:
                line_pt, limit_pt = slot_pt * K_STRICT, slot_pt * K_STRICT
                tag = '超槽宽85%预警线'
            pct = est_pt / slot_pt * 100 if slot_pt > 0 else 999.0
            if est_pt > limit_pt:
                nflag += 1
                rep.append(f'{path}:{lineno}:槽{slot_i}/{n_total}:旗·估值{est_pt:.1f}pt>{tag}({limit_pt:.1f}pt,占槽{pct:.0f}%,超{est_pt-limit_pt:.1f}pt)'
                           + f' 内容={content[:40]!r}')
            else:
                rep.append(f'{path}:{lineno}:槽{slot_i}/{n_total}:过·估值{est_pt:.1f}pt/槽宽{slot_pt:.1f}pt({pct:.0f}%)')
    return rep, nslot, nflag, nform


def main(argv):
    args = argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        return 2
    cfg = {'k': K_ZEROFP, 'lw_mm': DEF_LW_MM, 'xhang_mm': DEF_XHANG_MM,
           'lxhang_mm': DEF_LXHANG_MM, 'tol_pt': TOL_PT,
           'optii_mm': DEF_OPTII_MM, 'optiv_mm': DEF_OPTIV_MM, 'out': None}
    pos = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--mode':
            i += 1
            if i >= len(args) or args[i] not in ('zero-fp', 'strict'):
                print('[FAIL] --mode 仅接受 zero-fp|strict')
                return 2
            cfg['k'] = K_ZEROFP if args[i] == 'zero-fp' else K_STRICT
        elif a == '--linewidth-mm':
            i += 1
            cfg['lw_mm'] = float(args[i])
        elif a == '--tol-pt':
            i += 1
            cfg['tol_pt'] = float(args[i])
        elif a == '--lxhang-mm':
            i += 1
            cfg['lxhang_mm'] = float(args[i])
        elif a == '--xhang-mm':
            i += 1
            cfg['xhang_mm'] = float(args[i])
        elif a == '--optii-mm':
            i += 1
            cfg['optii_mm'] = float(args[i])
        elif a == '--optiv-mm':
            i += 1
            cfg['optiv_mm'] = float(args[i])
        elif a == '--out':
            i += 1
            cfg['out'] = args[i]
        elif a.startswith('--'):
            print('[FAIL] 未知开关:', a)
            return 2
        else:
            pos.append(a)
        i += 1
    if len(pos) != 1:
        print('用法: python 工具/makebox槽宽门.py <tex文件或目录> [--mode zero-fp|strict] '
              '[--linewidth-mm 84.0] [--xhang-mm 13.0] [--lxhang-mm 7.6] [--tol-pt 7.11] '
              '[--optii-mm 53.05] [--optiv-mm 21.5] [--out 报告.txt]')
        return 2
    target = pos[0]
    if os.path.isdir(target):
        files = []
        for root, dirs, names in os.walk(target):
            dirs[:] = [d for d in dirs if d not in ('figs', '__pycache__')]
            files += [os.path.join(root, x) for x in names if x.endswith('.tex')]
        files.sort()
    elif target.endswith('.tex') and os.path.isfile(target):
        files = [target]
    else:
        print('[FAIL] 输入须为 .tex 文件或目录:', target)
        return 2
    if not files:
        print('[FAIL] 未找到 tex 文件')
        return 2
    mode = ('零误报(超槽宽＋%.1fpt容差判旗)' % cfg['tol_pt'] if cfg['k'] == K_ZEROFP
            else '严格(超槽宽%.0f%%即旗)' % (K_STRICT * 100))
    print(f'makebox槽宽门｜档位={mode}｜\\linewidth={cfg["lw_mm"]}mm｜件数={len(files)}')
    totp = tots = totf = totn = 0
    lines = []
    for f in files:
        rep, ns, nf, nfo = scan_file(f, cfg)
        tots += ns
        totf += nf
        totn += nfo
        totp += sum(1 for r in rep if ':过·' in r)
        lines += rep
    for ln in lines:
        if '旗' in ln or '跳过' in ln:
            print(ln)
    print(f'—— 槽{tots}（过{totp}／旗{totf}）形旗{totn} ——')
    modename = '零误报档' if cfg['k'] == K_ZEROFP else '严格档'
    verdict = f'[PASS] 槽宽门全过（{modename}｜槽{tots}／旗0）' if (totf == 0 and totn == 0) else \
              f'[FAIL] 旗{totf}+形旗{totn}（{modename}），超宽/形制违例须拆行或双盒改制后复跑'
    print(verdict)
    if cfg['out']:
        with open(cfg['out'], 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines + [verdict]) + '\n')
    return 0 if (totf == 0 and totn == 0) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
