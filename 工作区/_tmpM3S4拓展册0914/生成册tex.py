# -*- coding: utf-8 -*-
r"""生成册tex.py — M3 S4 拓展册（上/下册）main.tex 生成器（题后紧跟答案制·全线括线模）。
输入：拓区数据.json（拓区提取.py 产物）。
输出（写入域＝成卷/拓展册/上册|下册/）：
  main.tex＋main-true.tex/false.tex 双壳＋值台账-上/下册.json＋生成读数.json。
口径：题面/值逐字转录（转换器机械映射，禁改写）；详解取定稿拓块（✓记号与〔…〕账面行剔除）；
  组名行只给 ≥2 成员族打（族名照片内实排名/41库名）；撤席跳号＝印面号空缺（不重编号），
  让位/撤席注记随席＝tex 注释＋台账抄件（不入印面）。
"""
import io, json, os, re, sys, collections

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = 'C:/提示词/工作区/_tmpM3S4拓展册0914/拓区数据.json'
BASE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/拓展册'
KAOSHI = {
 '01': ('2.1', '坐标法'), '02': ('2.2', '倾斜角与斜率'), '04': ('2.2', '点斜式与斜截式'),
 '05': ('2.2', '两点式与一般式'), '10': ('2.4', '曲线与方程'), '11': ('2.5.1', '椭圆的标准方程'),
 '12': ('2.5.2', '椭圆的几何性质'), '13': ('2.6.1', '双曲线的标准方程'),
 '14': ('2.6.2', '双曲线的性质'), '15': ('2.7.1', '抛物线方程'), '16': ('2.7.2', '抛物线的性质'),
 '17': ('2.8①', '压轴综合一')}
SHANG = ['01', '02', '04', '05', '10', '11', '12', '13']
XIA = ['14', '15', '16', '17']
MONGE = {'28', '29', '30', '31', '32', '33', '35', '36'}  # 课时12 蒙日族拓展 8 席（台账§5 注记）

data = json.load(open(SRC, encoding='utf-8'))
seats = data['seats']

# ================= 转换器 =================
SUP = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8',
       '⁹': '9', '⁺': '+', '⁻': '-', 'ⁿ': 'n', 'ⁱ': 'i'}
SUB = {'₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8',
       '₉': '9', '₊': '+', '₋': '-', '₌': '=', 'ₙ': 'n', 'ₘ': 'm', 'ᵢ': 'i'}
GREEK = {'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'θ': r'\theta', 'λ': r'\lambda',
         'μ': r'\mu', 'π': r'\pi', 'ρ': r'\rho', 'σ': r'\sigma', 'τ': r'\tau', 'φ': r'\varphi',
         'ω': r'\omega', 'Δ': r'\Delta', 'Ω': r'\Omega', 'ε': r'\varepsilon', 'η': r'\eta',
         'ξ': r'\xi', 'ζ': r'\zeta', 'Γ': r'\Gamma', 'Θ': r'\Theta', 'Λ': r'\Lambda'}
SYM = {'−': '-', '×': r'\times', '÷': r'\div', '±': r'\pm', '∓': r'\mp', '≤': r'\leqslant',
       '≥': r'\geqslant', '≦': r'\leqslant', '≧': r'\geqslant', '≠': r'\neq', '≈': r'\approx',
       '≡': r'\equiv', '≌': r'\cong', '∈': r'\in', '∉': r'\notin', '⊂': r'\subset', '⊆': r'\subseteq',
       '∪': r'\cup', '∩': r'\cap', '⊥': r'\perp', '∥': r'\parallel', '‖': r'\|',
       '∠': r'\angle', '△': r'\triangle', '⊙': r'\odot', '∵': r'\because', '∴': r'\therefore',
       '∀': r'\forall', '∞': r'\infty', '⇒': r'\Rightarrow', '⇔': r'\Leftrightarrow',
       '⟹': r'\Rightarrow', '⟺': r'\Leftrightarrow', '⇏': r'\nRightarrow', '→': r'\rightarrow',
       '↔': r'\leftrightarrow', '↦': r'\mapsto', '⋅': r'\cdot', '·': r'\cdot', '∶': ':', '＊': r'\ast',
       '∎': r'\rule{1.05ex}{1.05ex}', '～': r'\sim', '⟨': r'\langle', '⟩': r'\rangle', '〈': r'\langle',
       '〉': r'\rangle', '≶': r'\lessgtr', '′': "'", '″': "''", '℃': r'^{\circ}C',
       '＝': '=', '＋': '+', '＜': '<', '＞': '>', '－': '-', '／': '/', '％': r'\%',
       '＿': '_', '　': ' ', '⁄': '/'}
MATH_EXTRA = set('=+-<>|/()[]{}.,;:!?"\'`@#$%^&*_~°′')
CJK_PUNCT = set('，。；：？！、（）【】《》「」『』・—…·“”‘’〔〕．')
RARE_CJK = {'暅': r'{\fangsong 暅}'}  # 主字体 FZShuSong 缺字，仿宋回退（\gou 同档先例）
SYMREV = {**GREEK, **SYM}

def sym_sub(s):
    """符号→宏替换；控制词后补空格防吞字（\\perp l 不得成 \\perpl）。"""
    out = []
    for c in s:
        v = SYMREV.get(c)
        if v is None:
            out.append(c)
        else:
            out.append(v + ' ' if v[0] == '\\' and v[-1].isalpha() else v)
    return ''.join(out)

def brace_escape(s):
    """字面集合花括号转 \\{\\}；^{...}/_{...} 记法组括号按嵌套深浅原样保留。"""
    out = []
    depth = 0
    for i, c in enumerate(s):
        if c == '{':
            if depth == 0 and (i == 0 or s[i - 1] not in '^_'):
                out.append('\\{')
            else:
                depth += 1
                out.append('{')
        elif c == '}':
            if depth > 0:
                depth -= 1
                out.append('}')
            else:
                out.append('\\}')
        else:
            out.append(c)
    return ''.join(out)

def is_math_ch(c):
    o = ord(c)
    if c in SUP or c in SUB or c in GREEK or c in SYM or c in MATH_EXTRA:
        return True
    if c.isascii():
        return True
    if 0x2070 <= o <= 0x209F or 0x2190 <= o <= 0x22FF or 0x27E6 <= o <= 0x27EF or o == 0x00B0:
        return True
    if 0x0391 <= o <= 0x03C9:
        return True
    return False

def conv_math(seg):
    """数学段 → LaTeX（已剥离首尾空白）。"""
    s = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ⁿⁱ]+', lambda m: '^{' + ''.join(SUP[c] for c in m.group(0)) + '}', seg)
    s = re.sub(r'[₀₁₂₃₄₅₆₇₈₉₊₋₌ₙₘᵢ]+', lambda m: '_{' + ''.join(SUB[c] for c in m.group(0)) + '}', s)
    s = re.sub(r'°', r'^{\\circ}', s)
    s = s.replace('%', r'\%').replace('#', r'\#').replace('&', r'\&')
    prev = None
    PL, PR = chr(3), chr(4)  # 根号括号占位字节（brace_escape 后还原）
    while prev != s:
        prev = s
        s = re.sub(r'√\(([^()]*)\)', lambda m: '\\sqrt' + PL + conv_math(m.group(1)) + PR, s)
        s = re.sub(r'√\{([^{}]*)\}', lambda m: '\\sqrt' + PL + conv_math(m.group(1)) + PR, s)
        s = re.sub(r'√\[([^\[\]]*)\]', lambda m: '\\sqrt' + PL + conv_math(m.group(1)) + PR, s)
        s = re.sub(r'√([0-9][0-9.]*)', lambda m: '\\sqrt' + PL + m.group(1) + PR, s)
        s = re.sub(r'√([A-Za-z][₀₁₂₃₄₅₆₇₈₉]*)', lambda m: '\\sqrt' + PL + conv_math(m.group(1)) + PR, s)
    s = s.replace('√', '\\sqrt' + PL + PR)
    s = brace_escape(s)
    s = s.replace(PL, '{').replace(PR, '}')
    s = re.sub(r' (?=[=≤≥≠≈<>])', r' \\allowbreak ', s)
    s = sym_sub(s)
    s = re.sub(r'_{2,}', r'\\kongbai{}', s)
    s = re.sub(r'_(?!\{)', r'\_', s)
    return s

def convert(text):
    """混排文本 → LaTeX。返回 (tex, 未知字符集)。"""
    text = re.sub(r'(.)\u0303', r'\\tilde \1 ', text)
    runs, cur, curm = [], '', None
    for c in text:
        if c in ' \u3000' and curm is not None:
            cur += c
            continue
        m = is_math_ch(c)
        if curm is None or m == curm:
            cur, curm = cur + c, m
        else:
            runs.append((curm, cur))
            cur, curm = c, m
    if cur:
        runs.append((curm, cur))
    out = ''
    for m, seg in runs:
        if m:
            t = seg.strip()
            if t:
                out += r'\(' + conv_math(t) + r'\)'
            tail = seg[len(seg.rstrip()):]
            out += tail.replace('\u3000', '　')
        else:
            seg = seg.replace('{', r'\{').replace('}', r'\}')
            out += ''.join(RARE_CJK.get(c, c) for c in seg)
    unknown = set()
    for c in text:
        if ord(c) > 0x2000 and not (0x4E00 <= ord(c) <= 0x9FFF) and c not in SUP and c not in SUB \
           and c not in GREEK and c not in SYM and c not in CJK_PUNCT and not c.isascii() \
           and c not in '①②③④⑤⑥⑦⑧⑨⑩ⅠⅡⅢⅣⅰⅱⅲ　｜．√＠':
            unknown.add(c)
    return out.replace(r'\(\)', ''), unknown

# 清理：✓✗⚠、〔…〕账面段、**markdown 加粗**
def clean_detail(lines):
    out = []
    for ln in lines:
        ln = re.sub(r'^〔.*〕\s*$', '', ln)
        ln = ln.replace('✓', '').replace('✗', '').replace('⚠', '')
        ln = re.sub(r'\*\*(.+?)\*\*', r'\1', ln)
        ln = ln.strip()
        if ln:
            out.append(ln)
    return out

def clean_text(lines):
    out = []
    for ln in lines:
        ln = re.sub(r'^【注】.*$', '', ln)
        ln = ln.replace('✓', '').replace('⚠', '')
        ln = re.sub(r'\*\*(.+?)\*\*', r'\1', ln)
        out.append(ln.strip())
    return [l for l in out if l]

# ================= 题面结构解析 =================
OPT_RE = re.compile(r'(?:^|[　\s])((?:[A-D])．)')

def split_opts(lines):
    """拆题干/选项。返回 (stem_lines, opts or None)。要求恰 4 个 A．B．C．D．锚。"""
    joined = '\n'.join(lines)
    ms = list(OPT_RE.finditer(joined))
    if len(ms) != 4:
        return lines, None
    first = ms[0].start(1)
    stem = joined[:first].strip()
    pos = [m.start(1) for m in ms] + [len(joined)]
    opts = []
    for i in range(4):
        seg = joined[pos[i]:pos[i + 1]].strip()
        seg = re.sub(r'\s*\n\s*', ' ', seg)
        opts.append(seg)
    stem_lines = [l for l in stem.split('\n') if l.strip()]
    return stem_lines, opts

COL_EM = 22.7
COL_MM, HANG_MM, MM2PT = 84.0, 7.6, 2.84528  # 与 makebox槽宽门缺省同源（lw/lxhang/pt每mm）

import importlib.util as _ilu
_spec_cmg = _ilu.spec_from_file_location('caomen_gate', 'C:/提示词/工具/makebox槽宽门.py')
_mod_cmg = _ilu.module_from_spec(_spec_cmg)
_spec_cmg.loader.exec_module(_mod_cmg)
ink_em = _mod_cmg.ink_em

def opt_tier(opts, hang_em):
    """降档梯：四连排→两连排→单列（估宽承 makebox槽宽门 ink_em 同源，85% 线内收 3pt）。"""
    if not opts or len(opts) != 4:
        return '1'
    conv = [convert(o)[0] for o in opts]
    wmax_pt = max(ink_em(t, False) * 10.5 for t in conv)
    slot4_pt = (COL_MM - HANG_MM) / 4 * MM2PT - 0.25 * 10.5
    slot2_pt = (COL_MM - HANG_MM) / 2 * MM2PT - 0.25 * 10.5
    if wmax_pt <= slot4_pt * 0.85 - 1.0:
        return '4'
    if wmax_pt <= slot2_pt * 0.85 - 1.0:
        return '2'
    return '1'

def opt_width_em(o):
    """估墨宽（em，10.5pt 基；与 makebox槽宽门 估宽口径同向）。"""
    w = 0.0
    for c in o:
        if ord(c) > 0x2E80:
            w += 1.0
        elif c in 'iljt.,;:!|\'"()[]{} ':
            w += 0.32
        elif c.isdigit() or c.isalpha():
            w += 0.55
        else:
            w += 0.62
    return w

def nandu_word(raw):
    r = raw.strip()
    m = re.search(r'（(简[^）]*|中[^）]*|难[^）]*)）', r)
    if m:
        w = m.group(1)
        return w.replace('档', '')
    if '简' in r:
        return '简'
    if '难' in r:
        return '难'
    if '中' in r:
        return '中'
    return ''

def detect_form(seat, val):
    joined = '\n'.join(seat['题'])
    has_opt = len(OPT_RE.findall(joined)) >= 4
    v = (val or '').replace('（', '(').replace('）', ')')
    letters = re.findall(r'(?:^|[(,，、;；\s])([ABCD]{1,4})(?=$|[(,，、;；\s.。])', v)
    if has_opt:
        if letters and max((len(l) for l in letters), default=0) >= 2:
            return '多选'
        return '单选'
    if re.search(r'[＿_]{2,}|_____', joined):
        return '填空'
    return '解答'

def group_name(s):
    if s['课时'] == '12' and re.sub(r'^0', '', s['seat']) in MONGE:
        return '蒙日圆族'
    return s.get('族名') or ''

# ================= 渲染 =================
PRE = r'''% ============================================================
% M3 S4 拓展册（册名）· 拓区收编（收编读数）
% 依据：_tmpM3S4预备0913/S4波次方案.md §3.1（221 题次口径）＋canonical键名总表.md＋
%   定稿/定稿汇总-第2章.md（拓区账）＋_tmpM3S4题源闸0914/首跑钉码.md。
% 版式：练习线 qp-m3.sty（md5 7c3930362be8a0a2bdf21bbf8ac16573，本地挂载副本）；题后紧跟答案制；
%   全线括线模（\ansblockgrayfalse 导言一次置定——「>8 行→括线模」在全括线下自然满足）。
% 组织：节域序（canonical 01→…→17）→题型族组→组内席序；组名行只给 ≥2 成员族打。
% 跳号对号档：撤席（10-拓1／11-拓2／12-拓27／拓14-13／拓14-31／16-18）＝印面号空缺不重编号，
%   注记随席（tex 注释＋值台账抄件，不入印面）；章末 19 席缺料未收编（残余项，见汇编报告）。
% ============================================================
\documentclass[fontset=none]{ctexart}
\usepackage{qp-m3}
% —— 印面逐字符号路由补钉（承练习件母版；− 走 TNR、▱ NSC 子块；禁改 sty 保 md5） ——
\xeCJKDeclareCharClass{Default}{"2212}%
\setCJKfamilyfont{nscblk}[Path=C:/提示词/工作区/字替对照-0909/variantF/fonts/,BoldFont=NSC-w600.ttf]{NSC-w500.ttf}%
\xeCJKDeclareSubCJKBlock{nscblk}{"25B1}%
\newcommand{\pxparallelogram}{{\CJKfamily{nscblk}▱}}%
\xeCJKsetup{CJKglue={\hskip 0.10em plus 0.08em minus 0.05em}}%
\ansblockgrayfalse
\renewcommand{\qpzhangming}{第二章\quad 平面解析几何}%
\renewcommand{\qpjianming}{拓展册（册名）}%
% —— 拓展册局部宏（组名行＝M2 拓展册档独立行；悬挂题号＝席号字面自适应宽，撤席跳号照印） ——
\newsavebox{\thbox}%
\newcommand{\tuhao}[1]{\par\glueguard{1}%
  \sbox{\thbox}{\textbf{#1.}}%
  \setlength{\lxhang}{\dimexpr\wd\thbox+1.4mm\relax}%
  \noindent\hangindent=\lxhang\hangafter=0
  \llap{\hbox to\lxhang{\textbf{#1.}\hss}}}%
\definecolor{gray102}{HTML}{666666}%
\newcommand{\zux}[1]{\par\glueguard{2}\addvspace{2.4mm}\noindent
  {\fontsize{10.5pt}{18pt}\selectfont\heibf 【#1】}\par\addvspace{1.2mm}}%

\begin{document}

\zhangtitle{拓展册（册名）}
'''

def render_opts(opts, hang_em):
    tier = opt_tier(opts, hang_em)
    fs = r'{\fontsize{10.5pt}{\qpTJgLeadLiti}\selectfont '
    rows = []
    if tier == '4':
        cells = []
        for o in opts:
            t, u = convert(o)
            cells.append((t, u))
        row = r'\bindopt ' + fs + ''.join(r'\makebox[\dimexpr0.25\linewidth-0.25\lxhang-0.25em\relax][l]{%s}' % c[0]
                           for c in cells) + r'\par}'
        rows.append(row)
    elif tier == '2':
        for i in (0, 2):
            cells = []
            for o in opts[i:i + 2]:
                t, u = convert(o)
                cells.append((t, u))
            row = r'\bindopt ' + fs + ''.join(r'\makebox[\dimexpr0.5\linewidth-0.5\lxhang-0.25em\relax][l]{%s}' % c[0]
                               for c in cells) + r'\par}'
            rows.append(row)
    else:
        for o in opts:
            t, u = convert(o)
            rows.append(r'\lxopt{' + t + '}')
    return rows, tier

def stem_tex(stem_lines, form, val):
    txt = []
    unknown = set()
    joined = '\n'.join(stem_lines)
    kd = ''
    if form == '填空' and val:
        vclean = val.strip()
        if len(vclean) <= 18 and re.search(r'[＿_]{2,}', joined):
            kd = vclean
            joined = re.sub(r'[＿_]{2,}', '＠＠', joined, count=1)
    for ln in joined.split('\n'):
        t, u = convert(ln)
        unknown |= u
        txt.append(t)
    body = '\n'.join(txt)
    if kd:
        vtex, u2 = convert(kd)
        unknown |= u2
        if body.count('＠＠') != 1:
            raise RuntimeError('kongda 锚丢失或重复：' + body[:80])
        body = body.replace('＠＠', r'\kongda{' + vtex + '}', 1)
    return body, unknown

def liubai_h(seat, form):
    if form != '解答':
        return ''
    n = len(re.findall(r'^\s*[（(]\d[)）]', '\n'.join(seat['题']), re.M))
    h = '16mm' if n <= 1 else ('24mm' if n == 2 else ('32mm' if n <= 4 else '40mm'))
    return r'\liubai[%s]{解答书写区}' % h

def render_question(idx_counter, s, kc, notes_out):
    unknown = set()
    seat = s['seat']
    val = s['值'] or s['dg答案'] or ''
    form = detect_form(s, val)
    stem_lines, opts = split_opts(clean_text(s['题']))
    hang_em = 1.55 if len(seat) <= 1 else (2.06 if len(seat) <= 2 else 3.2)
    num = seat
    head = r'\tuhao{%s}' % num
    if form == '多选':
        head += r'\duoxuan\hspace{0.6em}'
    nw = nandu_word(s['难度raw'])
    side = r' \tieside{%s}' % nw if nw else ''
    stem_body, u1 = stem_tex(stem_lines, form, val)
    unknown |= u1
    out = []
    # 席注（撤席邻位/图债/让位——随席注释，不入印面）
    ann = []
    if s.get('注'):
        ann.append('席注（账面）：%s' % s['注'][:150])
    if '如图' in '\n'.join(stem_lines):
        ann.append('图债注：「如图」指源件配图，印面无图（冻片【注】裁定：去装饰图/条件全在文字/尺寸随注——图债登记汇编报告）')
    if ann:
        out.append('% ' + '　'.join(ann))
    out.append(head + side + stem_body)
    if opts:
        rows, tier = render_opts(opts, hang_em)
        out.extend(rows)
    else:
        lb = liubai_h(s, form)
        if lb:
            out.append(lb)
    det = clean_detail(s['详解'] or [])
    det_tex, u2 = convert(' '.join(det))
    unknown |= u2
    vtex, u3 = convert(val)
    unknown |= u3
    out.append(r'\begin{ansblock}[%s]' % s['key'])
    out.append('% ans:' + s['key'])
    out.append(r'\ansitem{%s}{%s}' % (num, vtex))
    out.append(r'\ansnote{详解}{%s}' % det_tex)
    out.append(r'\end{ansblock}')
    rec = dict(key=s['key'], seat=seat, num=num, form=form, tier=tier_opt(opts, hang_em) if opts else '',
               值=val, nline_detail=len(det))
    return '\n'.join(out) + '\n', rec, unknown

def tier_opt(opts, hang_em):
    return opt_tier(opts, hang_em)

def build(ks,册名, fname_tag):
    ks = [s for s in seats if s['课时'] in ks]
    body = [PRE.replace('册名', 册名).replace('收编读数', '%d 题' % len(ks))]
    body.append(r'\begin{multicols}{2}' + '\n' + r'\emergencystretch=1em' + '\n')
    ledger = dict(件='拓展册（%s）' % 册名, 口径='键账 {keys,vals}＋items 逐键读数', keys=[], vals={}, items=[])
    allunk = set()
    counter = collections.Counter()
    cur_kc = None
    cur_group = None
    prev_num = 0
    for s in sorted(ks, key=lambda x: (x['课时'], [int(p) if p.isdigit() else p for p in re.split(r'(\d+)', x['seat'])])):
        kc = s['课时']
        if kc != cur_kc:
            jie, ming = KAOSHI[kc]
            cur_kc = kc
            cur_group = None
            prev_num = 0
            body.append(r'\jietitle{%s　%s（课时%s·拓区）}' % (jie, ming, kc))
            if kc == '10':
                body.append('% 【10-拓1｜撤位登记（案2令1：与G5·单1 同题双列撤席让位，唯一活位＝10-G1）】本席不设题——跳号留痕（拓2 起），注记随席（台账抄件）；防双收 B22。')
            if kc == '11':
                body.append('% 【11-拓2｜撤位登记（案2令2：与11-简7 逐字同题撤席让位，唯一活位＝11-简7）】本席不设题——跳号留痕（拓3 起），注记随席（台账抄件）；防双收 B21。')
            if kc == '12':
                body.append('% 【12-拓27｜撤席登记（0914 主裁：保 12-拓6 撤 12-拓27，同题双收）】本席不设题——跳号留痕（拓28 起），注记随席（台账抄件）；防双收 B23。')
            if kc == '14':
                body.append('% 【拓14-13｜让位席（教材练A2 判重让位）不占键；【拓14-31｜双收4 撤】不设块——两席跳号留痕，注记随席（台账抄件）。】')
            if kc == '16':
                body.append('% 【16-18｜让位席（教材版让位）无键留块——印面跳号（17 后直接 19），注记随席（台账抄件）。】')
            if kc == '17':
                body.append('% 课时17：卷④2.8.12.1-25 让位无块无键，注记随 17-03（豁免登记在案）。章末拓展 19 席（2章-拓-章末-01~19）缺料未收编——残余项。')
        g = group_name(s)
        if g and g != cur_group:
            body.append(r'\zux{%s}' % g)
            cur_group = g
        elif not g:
            cur_group = None
        q, rec, unk = render_question(None, s, kc, ledger['items'])
        body.append(q)
        ledger['keys'].append(s['key'])
        ledger['vals'][s['key']] = s['值'] or s['dg答案']
        ledger['items'].append(rec)
        allunk |= unk
        prev_num += 1
    body.append(r'\tailfill')
    body.append(r'\end{multicols}')
    body.append(r'\end{document}')
    d = os.path.join(BASE, fname_tag)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'main.tex'), 'w', encoding='utf-8', newline='\n').write('\n'.join(body))
    open(os.path.join(d, 'main-true.tex'), 'w', encoding='utf-8', newline='\n').write(r'\def\mthreepure{0}\input{main.tex}' + '\n')
    open(os.path.join(d, 'main-false.tex'), 'w', encoding='utf-8', newline='\n').write(r'\def\mthreepure{1}\input{main.tex}' + '\n')
    json.dump(ledger, open(os.path.join(d, '值台账-%s.json' % fname_tag), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return len(ledger['keys']), sorted(allunk), ledger['items']

if __name__ == '__main__':
    n1, u1, it1 = build(SHANG, '上', '上册')
    n2, u2, it2 = build(XIA, '下', '下册')
    print('上册：%d 题｜下册：%d 题' % (n1, n2))
    print('未知字符（上）：', ''.join(sorted(u1)) or '无')
    print('未知字符（下）：', ''.join(sorted(u2)) or '无')
    tiers = collections.Counter(r['tier'] for r in it1 + it2)
    print('选项降档梯：', dict(tiers))
    forms = collections.Counter(r['form'] for r in it1 + it2)
    print('形态：', dict(forms))
    long8 = [r['key'] for r in it1 + it2 if r['nline_detail'] > 8]
    print('详解 >8 行席：%d（全线括线模覆盖）' % len(long8))
    json.dump(dict(shang=n1, xia=n2, unknown_u=''.join(sorted(u1)), unknown_x=''.join(sorted(u2)),
                   tiers=dict(tiers), forms=dict(forms), long8=long8),
              open('C:/提示词/工作区/_tmpM3S4拓展册0914/生成读数.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
