# -*- coding: utf-8 -*-
r"""答案抽册器.py — M3 三档导出·第三档「纯答案单独成册」抽册器（2026-09-14）

定位：LaTeX 三档导出——整体（main-true）／纯题（main-false）已在产，本器补第三档：
从成卷 tex 件（main.tex 单源）逐题抽出 ansblock 答案块，生成「纯答案册」
（题面不重印）＝册头＋逐题（题号＝正册印面号＋[答案]＋[详解]），单源双壳双档编译三零：
  ansbook-true  ＝详解印本（答案＋详解）
  ansbook-false ＝纯值速查本（仅答案，详解不印）

抽取口径：照 `% ans:<键>` 源层锚＋`\begin{ansblock}[键]` 编译层锚，逐块取
`\ansitem{印面号}{值}`／`\ansnote{详解}{文}`（花括号平衡取参，逐字保真）。

册序口径（--order）：
  zhengce（默认）＝正册装配序＝印面号升序（同序同号；与正册 log ANSKEY 序逐位全等）；
  canonical      ＝题面库冻结 manifest 键序（键账基准序）。
  两模式均断言：键集合≡canonical（双向 diff）、印面号集≡1..N 恰一对应。

随册硬断言（门谱）：
  守恒门  源锚数＝源块数＝册锚数＝册块数＝canonical 键数（抽册守恒：源键数＝册内块数）；
  对号门  册 log M3-ANSKEY 序≡册 tex 序（两档两遍）、集合≡canonical、两档恒等；
  钉值门  册值≡正册件内值（逐字全等·硬断言）≡值台账 items.值tex；册详解≡正册详解；
          册印面号≡值台账印面号；
  PDF 门  [答案] 计数＝N、号序≡正册 true PDF 号序（逐位＝同序同号印面证）；true [详解]＝N／
          false＝0；逐键值印面在册（空白归一）；题面泄漏＝0（题面库题面行≥12字run，
          正册答案块体内已有者豁免；两档各查）；
  三零门  error/Overfull/Underfull/Missing character 全零（双档×两遍，exit=0）。

红线：成卷件树零写入（全程只读）；本器唯一写入位＝--out（默认
工作区/_tmpM3抽答器0914/<件型>-<片名>）；qp-m3.sty 照源件副本 md5 锁校验后随册挂载。
用法：
  python 工具/答案抽册器.py <成卷tex件目录> [--out 目录] [--order zhengce|canonical]
      [--skip-compile] [--skip-png]
  例：python 工具/答案抽册器.py 工作区/M3-第2章量产0913/成卷/导学件/课时01-坐标法
退出码：0＝门全绿；1＝有红。
"""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
XELATEX = os.environ.get('XELATEX',
                         'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex.exe')
STY_MD5_LOCK = '7c3930362be8a0a2bdf21bbf8ac16573'  # 两钉落盘版（toolchain钉档 §四，破损即停）

RE_BEGIN = re.compile(r'^\s*\\begin\{ansblock\}\[([^\]]+)\]')
RE_END = re.compile(r'^\s*\\end\{ansblock\}')
RE_ANCH = re.compile(r'^\s*%\s*ans:(\S+)\s*$')
RE_ITEM = re.compile(r'\\ansitem\{(\d+)\}\{')
RE_NOTE = re.compile(r'\\ansnote\{详解\}\{')
RE_KEYLOG = re.compile(r'^M3-ANSKEY: (.+)$', re.M)
RE_TITLE = re.compile(r'^\\(zhangtitle|jietitle|xiaojietitle|keshi|xjkeshi)\{.+\}\s*$')
RE_ZHANGM = re.compile(r'^\\renewcommand\{\\qpzhangming\}\{(.*)\}%?\s*$')
RE_JIANM = re.compile(r'^\\renewcommand\{\\qpjianming\}\{(.*)\}%?\s*$')


def md5_of(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


def read_text(path):
    return open(path, encoding='utf-8', newline='').read()


def strip_comment(s):
    """去未转义 % 后缀（值域无 %，仅锚行/注释放行用）。"""
    j = 0
    while j < len(s):
        if s[j] == '\\':
            j += 2
            continue
        if s[j] == '%':
            return s[:j]
        j += 1
    return s


def extract_arg(lines, li, cpos):
    r"""lines[li][cpos] 为 '{'：花括号平衡取参（跨行安全），返回 (body, 结束行号)。
    深度自 1 起——cpos 处开括号即本参开括号，体内嵌套组（如 \sqrt{4^{2}}）自平衡，
    惟本参收括号归零。"""
    depth = 1
    buf = []
    for k in range(li, len(lines)):
        s = lines[k] if k > li else lines[k][cpos + 1:]
        j = 0
        while j < len(s):
            ch = s[j]
            if ch == '\\' and j + 1 < len(s):
                buf.append(s[j:j + 2])
                j += 2
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return ''.join(buf), k
            buf.append(ch)
            j += 1
        buf.append('\n')
    raise ValueError('花括号不配平（行 %d 起）' % (li + 1))


def parse_piece(piece_dir):
    r"""main.tex → {blocks(装配序), anchors, titles, zhangming, jianming, md5}。

    逐块：键＝\begin{ansblock}[键]；锚行 % ans:键 须与块键同；
    值＝\ansitem{印面号}{值}；详解＝\ansnote{详解}{文}（均可跨行，花括号平衡）。
    """
    main_path = os.path.join(piece_dir, 'main.tex')
    if not os.path.exists(main_path):
        raise SystemExit('红：%s 缺 main.tex（输入须为成卷 tex 件目录）' % piece_dir)
    src = read_text(main_path)
    lines = [ln.rstrip('\r') for ln in src.split('\n')]
    blocks, anchors, cur = [], [], None
    titles, zhangming, jianming = [], None, None
    in_multicols = False
    for i, raw in enumerate(lines):
        line = raw.rstrip('\r')
        code = strip_comment(line)
        if not in_multicols and '\\begin{multicols}' in code:
            in_multicols = True
        if not in_multicols:
            if RE_TITLE.match(code.strip()):
                titles.append(code.strip())
            mz = RE_ZHANGM.match(code.strip())
            if mz:
                zhangming = mz.group(1)
            mj = RE_JIANM.match(code.strip())
            if mj:
                jianming = mj.group(1)
        mb = RE_BEGIN.match(code)
        if mb and cur is None:
            cur = {'key': mb.group(1), 'num': None, 'val': None, 'note': None,
                   'line': i + 1}
            continue
        if cur is not None:
            ma = RE_ANCH.match(line)
            if ma:
                anchors.append(ma.group(1))
                continue
            mi = RE_ITEM.search(code)
            if mi and cur['val'] is None:
                cur['num'] = int(mi.group(1))
                cur['val'], _ = extract_arg(lines, i, mi.end() - 1)
                continue
            mn = RE_NOTE.search(code)
            if mn and cur['note'] is None:
                cur['note'], _ = extract_arg(lines, i, mn.end() - 1)
                continue
            if RE_END.match(code):
                cur['anchor'] = anchors[-1] if anchors else None
                blocks.append(cur)
                cur = None
    if cur is not None:
        raise SystemExit('红：main.tex ansblock 未闭合（键 %s）' % cur['key'])
    return {'dir': os.path.normpath(piece_dir), 'main': main_path, 'src': src,
            'md5': md5_of(main_path), 'blocks': blocks, 'anchors': anchors,
            'titles': titles, 'zhangming': zhangming, 'jianming': jianming,
            'sty': os.path.join(piece_dir, 'qp-m3.sty')}


def chengjuan_root(piece_dir):
    """成卷根＝件目录上两级（成卷/<件型>/<片名>）。"""
    return os.path.normpath(os.path.join(piece_dir, '..', '..'))


def pian_name(piece_dir):
    name = os.path.basename(os.path.normpath(piece_dir))
    m = re.match(r'(课时\d+[A-Za-z]*)', name)
    return m.group(1) if m else name


def resolve_canonical(piece_dir, keys):
    """canonical 键序：题面库冻结 manifest 本体优先，件manifest 冻结键序次之，
    皆缺＝退装配序（并如实标注）。返回 (序, 来源标签)。"""
    cj = chengjuan_root(piece_dir)
    pian = pian_name(piece_dir)
    cand = []
    fm = os.path.join(cj, '题面库', 'manifest', pian + '.manifest.json')
    if os.path.exists(fm):
        cand.append((json.load(open(fm, encoding='utf-8')).get('键序') or [],
                     '题面库冻结manifest'))
    mm = os.path.join(piece_dir, '件manifest.json')
    if os.path.exists(mm):
        cand.append((json.load(open(mm, encoding='utf-8')).get('冻结manifest键序') or [],
                     '件manifest冻结键序'))
    keyset = set(keys)
    for seq, tag in cand:
        sub = [k for k in seq if k in keyset]
        if len(sub) == len(keys) and set(sub) == keyset:
            return sub, tag
    return list(keys), '装配序退化（未得canonical，须核）'


def load_ledger(piece_dir):
    """值台账-<片名>.json → (值tex映射, 印面号映射, 路径|None)。缺件＝空映射。"""
    pian = pian_name(piece_dir)
    p = os.path.join(piece_dir, '值台账-%s.json' % pian)
    if not os.path.exists(p):
        return {}, {}, None
    d = json.load(open(p, encoding='utf-8'))
    vt = {it['键']: it.get('值tex') for it in d.get('items', [])}
    nm = {it['键']: it.get('印面号') for it in d.get('items', [])}
    return vt, nm, p


# ============ 纯答案册生成 ============
# 符号路由补钉＋CJK 胶微调：照母版体例说明 §二 逐字档（无 ▱/− 用件的片整块照抄零副作用）
ROUTING = [
    '\\xeCJKDeclareCharClass{Default}{"2212}%',
    '\\setCJKfamilyfont{nscblk}[Path=C:/提示词/工作区/字替对照-0909/variantF/fonts/,'
    'BoldFont=NSC-w600.ttf]{NSC-w500.ttf}%',
    '\\xeCJKDeclareSubCJKBlock{nscblk}{"25B1}%',
    '\\newcommand{\\pxparallelogram}{{\\CJKfamily{nscblk}▱}}%',
]
CJKGLUE = '\\xeCJKsetup{CJKglue={\\hskip 0.10em plus 0.08em minus 0.05em}}%'


def order_blocks(piece, canonical, mode):
    """册序：zhengce＝印面号升序（须≡装配序）；canonical＝键账序。返回 (序, 备注)。"""
    blocks = piece['blocks']
    by_key = {b['key']: b for b in blocks}
    if mode == 'canonical':
        return [by_key[k] for k in canonical], 'canonical 键序（键账基准）'
    nums = [b['num'] for b in blocks]
    if nums != sorted(nums) or sorted(set(nums)) != list(range(1, len(blocks) + 1)):
        raise SystemExit('红：装配序≠印面号升序（zhengce 模式前置不成立，'
                         'nums=%s）——请改 --order canonical' % nums[:8])
    return list(blocks), '正册装配序＝印面号 1..%d 升序（同序同号）' % len(blocks)


def gen_booklet_tex(piece, ordered, mode, ordernote, sty_md5):
    """纯答案册单源体 ansbook.tex 文本。"""
    jianming = (piece['jianming'] or '答案册') + '答案册'
    orderline = ('册序＝%s；键序断言基准＝题面库冻结 manifest canonical 键序。' % ordernote)
    L = []
    A = L.append
    A('% ' + '=' * 60)
    A('%% 纯答案册·%s —— 工具/答案抽册器.py 抽册生成件（勿手改；第三档＝纯答案单独成册）'
      % os.path.basename(piece['dir']))
    A('%% 源件（只读）：%s（md5 %s）' % (piece['main'].replace('\\', '/'), piece['md5']))
    A('%% 口径：题面不重印；逐题＝题号(印面号同正册)＋[答案]＋[详解]，值/详解照源件逐字')
    A('%%       （钉值门硬断言：册值≡正册件内值≡值台账值tex，逐字全等）。%s' % orderline)
    A('%% 三档导出：整体 main-true／纯题 main-false（在产）｜本册＝纯答案册（本件）')
    A('%% 双档：ansbook-true.tex＝详解印本；ansbook-false.tex＝纯值速查本（详解不印）')
    A('%% 编译：xelatex <壳> ×2，cwd＝本目录；sty＝qp-m3.sty 本地挂载（md5 %s，锁校验）' % sty_md5)
    A('% ' + '=' * 60)
    A('\\documentclass[fontset=none]{ctexart}')
    A('\\usepackage{qp-m3}')
    A('% —— 印面逐字符号路由补钉（承源件；− 走 TNR、▱ NSC 子块；禁改 sty 保 md5） ——')
    L.extend(ROUTING)
    A('% —— 断行微调（承母版实测档，三零门承重；\\emergencystretch 不另设） ——')
    A(CJKGLUE)
    A('% —— 纯答案册全线括线（长详解可跨栏断，承练习件全线括线口径；灰底盒不可跨栏断） ——')
    A('\\ansblockgrayfalse')
    A('% —— 双档开关（false 档＝纯值速查：答案印、详解不印；件面开关，不动 sty 本体） ——')
    A('\\newif\\ifansbookdetail')
    A('\\ifdefined\\ansbookdetail')
    A('  \\ifnum\\ansbookdetail=0 \\ansbookdetailfalse\\else\\ansbookdetailtrue\\fi')
    A('\\else')
    A('  \\ansbookdetailtrue')
    A('\\fi')
    A('% —— 页脚件名（承源件章名；件名＝<件型>答案册） ——')
    A('\\renewcommand{\\qpzhangming}{%s}%%' % (piece['zhangming'] or ''))
    A('\\renewcommand{\\qpjianming}{%s}%%' % jianming)
    A('')
    A('\\begin{document}')
    L.extend(piece['titles'])
    A('\\par\\glueguard{1}\\addvspace{2pt}\\noindent\\biaoqian{【纯答案册】}'
      '{\\fangsong 题面不重印\\quad 印面号与正册同号同序}\\par\\addvspace{2pt}')
    A('')
    A('\\begin{multicols}{2}')
    A('\\emergencystretch=1em')
    for b in ordered:
        A('')
        A('\\begin{ansblock}[%s]' % b['key'])
        A('%% ans:%s' % b['key'])
        A('\\ansitem{%d}{%s}' % (b['num'], b['val']))
        A('\\ifansbookdetail')
        A('\\ansnote{详解}{%s}' % b['note'])
        A('\\fi')
        A('\\end{ansblock}')
    A('')
    A('% ---- 尾块（\\tailfill[30mm] 定高参——钉档 §三.3：无参在平衡栏呈「内容尾随框」，'
      '贴栏底须定高参；实测无参致末页平衡 Overfull\\vbox 12.99pt，定高 30mm 三零） ----')
    A('\\tailfill[30mm]')
    A('')
    A('\\end{multicols}')
    A('\\end{document}')
    return '\n'.join(L) + '\n'


SHELL_TMPL = '''%% ============================================================
%% 纯答案册·%s壳（\\ansbookdetail %s）→ %s.pdf
%% 双壳制（体单源零改）：xelatex %s.tex ×2，cwd＝本目录
%% \\mthreepure{0}＝showans true（ansblock 印面必需）；\\ansbookdetail 管 详解印/不印
%% ============================================================
\\def\\mthreepure{0}
\\def\\ansbookdetail{%s}
\\input{ansbook.tex}
'''


def write_booklet(out_dir, piece, ordered, mode, ordernote):
    """落盘：ansbook.tex＋双壳＋sty 副本（md5 锁校验）。返回 (sty_md5, 正文文本)。"""
    src_sty = piece['sty']
    if not os.path.exists(src_sty):
        raise SystemExit('红：源件缺 qp-m3.sty 本地挂载副本（%s）' % src_sty)
    sty_md5 = md5_of(src_sty)
    if sty_md5 != STY_MD5_LOCK:
        raise SystemExit('红：qp-m3.sty md5 %s ≠ 锁 %s（破损即停）' % (sty_md5, STY_MD5_LOCK))
    os.makedirs(out_dir, exist_ok=True)
    body = gen_booklet_tex(piece, ordered, mode, ordernote, sty_md5)
    open(os.path.join(out_dir, 'ansbook.tex'), 'w', encoding='utf-8', newline='\n').write(body)
    open(os.path.join(out_dir, 'ansbook-true.tex'), 'w', encoding='utf-8', newline='\n').write(
        SHELL_TMPL % ('详解印本', '1', 'ansbook-true', 'ansbook-true', '1'))
    open(os.path.join(out_dir, 'ansbook-false.tex'), 'w', encoding='utf-8', newline='\n').write(
        SHELL_TMPL % ('纯值速查本', '0', 'ansbook-false', 'ansbook-false', '0'))
    shutil.copyfile(src_sty, os.path.join(out_dir, 'qp-m3.sty'))
    if md5_of(os.path.join(out_dir, 'qp-m3.sty')) != STY_MD5_LOCK:
        raise SystemExit('红：sty 副本落盘后 md5 漂移（中止）')
    return sty_md5, body


def reparse_booklet(out_dir):
    """从落盘 ansbook.tex 复抽（生成件独立复核面）。→ {键: (号, 值, 详解)}＋序＋锚/块数。"""
    src = read_text(os.path.join(out_dir, 'ansbook.tex'))
    lines = [ln.rstrip('\r') for ln in src.split('\n')]
    blocks, anchors, cur = [], [], None
    for i, raw in enumerate(lines):
        code = strip_comment(raw.rstrip('\r'))
        mb = RE_BEGIN.match(code)
        if mb and cur is None:
            cur = {'key': mb.group(1), 'num': None, 'val': None, 'note': None}
            continue
        if cur is not None:
            ma = RE_ANCH.match(raw.rstrip('\r'))
            if ma:
                anchors.append(ma.group(1))
                continue
            mi = RE_ITEM.search(code)
            if mi and cur['val'] is None:
                cur['num'] = int(mi.group(1))
                cur['val'], _ = extract_arg(lines, i, mi.end() - 1)
                continue
            mn = RE_NOTE.search(code)
            if mn and cur['note'] is None:
                cur['note'], _ = extract_arg(lines, i, mn.end() - 1)
                continue
            if RE_END.match(code):
                blocks.append(cur)
                cur = None
    return {'blocks': blocks, 'anchors': anchors,
            'vals': {b['key']: b['val'] for b in blocks},
            'notes': {b['key']: b['note'] for b in blocks},
            'nums': {b['key']: b['num'] for b in blocks},
            'seq': [b['key'] for b in blocks]}


def compile_shell(out_dir, shell, passes=2):
    """xelatex <shell>.tex ×N（cwd＝册目录）；逐遍读 log 取三零＋ANSKEY。"""
    stats = []
    for p in range(1, passes + 1):
        r = subprocess.run([XELATEX, '-interaction=nonstopmode', shell + '.tex'],
                           cwd=out_dir, capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        logp = os.path.join(out_dir, shell + '.log')
        log = open(logp, encoding='utf-8', errors='replace').read() if os.path.exists(logp) else ''
        stats.append({'pass': p, 'rc': r.returncode,
                      'error': len(re.findall(r'^!', log, re.M)),
                      'overfull': log.count('Overfull'),
                      'underfull': log.count('Underfull'),
                      'missing': log.count('Missing character'),
                      'anskeys': RE_KEYLOG.findall(log)})
    return stats


def render_png(out_dir, tag, dpi=150):
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    import fitz
    outp = os.path.join(out_dir, 'png-%s' % tag)
    os.makedirs(outp, exist_ok=True)
    for p in os.listdir(outp):
        if p.endswith('.png'):
            os.remove(os.path.join(outp, p))
    doc = fitz.open(os.path.join(out_dir, 'ansbook-%s.pdf' % tag))
    n = 0
    for i, page in enumerate(doc, 1):
        page.get_pixmap(dpi=dpi).save(os.path.join(outp, 'page%d.png' % i))
        n = i
    doc.close()
    return n


# ============ 门谱（抽册件：守恒／对号／钉值／PDF／三零） ============
class Gates:
    def __init__(self):
        self.reds = []
        self.rows = []

    def check(self, name, ok, detail=''):
        tag = '绿' if ok else '红'
        self.rows.append((tag, name, detail))
        print('  [%s] %s%s' % (tag, name, ('｜' + detail) if detail else ''))
        if not ok:
            self.reds.append(name)


def norm_ws(s):
    return re.sub(r'\s+', '', s or '')


def texstrip(s):
    r"""TeX 标记粗剥离（题面泄漏比对用；渲染形近似——探测以 CJK 散文长run为承重）。"""
    s = re.sub(r'\\[a-zA-Z]+\*?', '', s or '')
    for t in ('\\(', '\\)', '$', '{', '}', '~', '\\\\'):
        s = s.replace(t, ' ')
    return s


def prose_runs(s, minlen=12):
    """≥minlen 连续段（CJK/中文标点/ASCII字母数字括点）；空白断段。"""
    def okc(ch):
        if '\u4e00' <= ch <= '\u9fff':
            return True
        if ch in '，。；：、（）“”‘’【】·．！？—…':
            return True
        return ch.isascii() and (ch.isalnum() or ch in '(),.=+-/')
    runs, buf = [], ''
    for ch in s:
        if okc(ch):
            buf += ch
        else:
            if len(buf) >= minlen:
                runs.append(buf)
            buf = ''
    if len(buf) >= minlen:
        runs.append(buf)
    return runs


def parse_timu_side(path):
    """题面库题面侧 → 每键题面行表（照题面库对号门 parse_questions 口径取行）。"""
    out, cur = {}, None
    for ln in read_text(path).splitlines():
        if ln.startswith('### '):
            cur = ln[4:].split('｜')[0].strip()
            out[cur] = []
        elif cur is not None:
            if ln.strip() == '---':
                cur = None
            elif ln.startswith('【注】') or not ln.strip():
                continue
            else:
                out[cur].append(ln)
    return out


def gate_tex(g, piece, bk, canonical, led_vals, led_nums, ordernote):
    N = len(piece['blocks'])
    src_keys = [b['key'] for b in piece['blocks']]
    g.check('守恒：源锚数＝源块数＝%d' % N,
            len(piece['anchors']) == len(src_keys) == N, '%d/%d' % (len(piece['anchors']), N))
    g.check('守恒：册锚数＝册块数＝%d（抽册守恒：源键数＝册内块数）' % N,
            len(bk['anchors']) == len(bk['blocks']) == N,
            '%d/%d' % (len(bk['anchors']), len(bk['blocks'])))
    g.check('对号：源键集合≡canonical（双向diff）', set(src_keys) == set(canonical),
            '缺%s 浮%s' % (sorted(set(canonical) - set(src_keys))[:4],
                           sorted(set(src_keys) - set(canonical))[:4]))
    g.check('对号：册键集合≡canonical（双向diff）', set(bk['seq']) == set(canonical), '')
    g.check('对号：册锚序列≡册块序列（逐位）', bk['anchors'] == bk['seq'], '')
    src_nums = sorted(b['num'] for b in piece['blocks'])
    g.check('对号：印面号集≡1..%d 恰一对应' % N,
            src_nums == list(range(1, N + 1)) and
            sorted(bk['nums'].values()) == list(range(1, N + 1)), '')
    exp_seq = canonical if 'canonical' in ordernote else src_keys
    g.check('对号：册tex序≡期望序（%s，逐位）' % ordernote, bk['seq'] == exp_seq, '')
    if led_vals:
        bad_v = [k for k in canonical if bk['vals'].get(k) != led_vals.get(k)]
        g.check('钉值：册值≡值台账值tex（逐字，%d键）' % N, not bad_v,
                ('漂移键 ' + ','.join(bad_v[:4])) if bad_v else '%d/%d 全等' % (N, N))
    if led_nums:
        bad_n = [k for k in canonical if bk['nums'].get(k) != led_nums.get(k)]
        g.check('钉值：册印面号≡值台账印面号（%d键）' % N, not bad_n,
                ('漂移键 ' + ','.join(bad_n[:4])) if bad_n else '%d/%d 全等' % (N, N))
    return exp_seq


def gate_value(g, piece, bk, canonical):
    src = {b['key']: b for b in piece['blocks']}
    bad_v = [k for k in canonical if bk['vals'][k] != src[k]['val']]
    g.check('钉值：册值≡正册件内值（逐字全等·硬断言，%d键）' % len(canonical), not bad_v,
            ('漂移键 ' + ','.join(bad_v[:4])) if bad_v else '%d/%d 逐字全等' % (len(canonical), len(canonical)))
    bad_n = [k for k in canonical if (bk['notes'][k] or '') != (src[k]['note'] or '')]
    g.check('钉值：册详解≡正册详解（逐字全等，%d键）' % len(canonical), not bad_n,
            ('漂移键 ' + ','.join(bad_n[:4])) if bad_n else '%d/%d 逐字全等' % (len(canonical), len(canonical)))


def gate_pdf(g, out_dir, piece, bk, canonical, leak_lines, allowed_norm):
    import fitz
    import unicodedata

    def fold(s):
        t = unicodedata.normalize('NFKC', norm_ws(s or ''))
        return t.replace('\u2212', '-')  # 数学负号折 ASCII 连字（两侧同折，比对恒稳）

    def needle(val):
        # 值 tex 形 → 渲染形（unicode-math 实测：\iff→⟺ U+27FA、\leqslant→⩽ U+2A7D；
        # _/^ 为数学上下标结构符，渲染面无此字符）
        v = (val or '').replace('$', '').replace('\\iff', '\u27fa') \
                       .replace('\\leqslant', '\u2a7d').replace('\\geqslant', '\u2a7e') \
                       .replace('_', '').replace('^', '')
        return fold(v)

    N = len(canonical)
    src_pdf = os.path.join(piece['dir'], 'main-true.pdf')
    sdoc = fitz.open(src_pdf)
    src_raw = '\n'.join(p.get_text() for p in sdoc)
    sdoc.close()
    src_nums = [int(m) for m in re.findall(r'(\d+)\.\s*\[答案\]', src_raw)]
    re_num = re.compile(r'(?<!\d)(\d+)\.\s*\[答案\]')
    pdfs = {}
    for tag in ('true', 'false'):
        doc = fitz.open(os.path.join(out_dir, 'ansbook-%s.pdf' % tag))
        text = '\n'.join(p.get_text() for p in doc)
        pdfs[tag] = {'n': len(doc), 'text': text, 'ntext': fold(text)}
        doc.close()
    for tag in ('true', 'false'):
        t = pdfs[tag]
        nums = [int(m) for m in re_num.findall(t['text'])]
        g.check('PDF[%s]：[答案] 计数＝%d' % (tag, N), t['text'].count('[答案]') == N,
                str(t['text'].count('[答案]')))
        g.check('PDF[%s]：号序≡正册true号序（逐位＝同序同号印面证）' % tag, nums == src_nums,
                '%d枚' % len(nums))
        g.check('PDF[%s]：号序≡1..%d 连号' % (tag, N), nums == list(range(1, N + 1)), '')
        miss = [k for k in canonical if needle(bk['vals'][k]) not in t['ntext']]
        g.check('PDF[%s]：逐键值印面在册（空白归一＋NFKC折形）' % tag, not miss,
                ('缺印 ' + ','.join(miss[:3])) if miss else '%d/%d 全中' % (N, N))
    g.check('PDF[true]：[详解] 计数＝%d' % N,
            pdfs['true']['text'].count('[详解]') == N, str(pdfs['true']['text'].count('[详解]')))
    g.check('PDF[false]：[详解] 计数＝0（纯值速查无详解）',
            pdfs['false']['text'].count('[详解]') == 0,
            str(pdfs['false']['text'].count('[详解]')))
    for tag in ('true', 'false'):
        leaks = [r for r in leak_lines if r in pdfs[tag]['ntext'] and r not in allowed_norm]
        g.check('PDF[%s]：题面泄漏＝0（题面行run≥12字，正册答案块体豁免）' % tag, not leaks,
                (str(leaks[:2])[:120]) if leaks else '0 条')
    g.check('PDF：页数 true≥false', pdfs['true']['n'] >= pdfs['false']['n'],
            'true=%d false=%d' % (pdfs['true']['n'], pdfs['false']['n']))
    return {t: pdfs[t]['n'] for t in pdfs}


def build_leakset(piece):
    """题面库题面行 → ≥12字 run 表；豁免 haystack＝正册 ansblock 体（值＋详解）剥离归一。
    run/haystack 与 PDF 文本同折（NFKC＋空白归一）后再比对。"""
    import unicodedata
    tj = os.path.join(chengjuan_root(piece['dir']),
                      '题面库', os.path.basename(os.path.normpath(piece['dir'])) + '.md')
    if not os.path.exists(tj):
        return None, None, tj
    fold = lambda s: unicodedata.normalize('NFKC', norm_ws(s))
    allowed = fold(texstrip(''.join(
        (b['val'] or '') + (b['note'] or '') for b in piece['blocks'])))
    runs = []
    for key, lns in parse_timu_side(tj).items():
        for ln in lns:
            runs.extend(prose_runs(texstrip(ln)))
    runs = sorted(set(fold(r) for r in runs))
    return runs, allowed, tj


def gate_log(g, piece, stats_by_shell, book_seq, canonical, ordernote):
    seqs = []
    for shell in ('ansbook-true', 'ansbook-false'):
        for st in stats_by_shell[shell]:
            tag = '%s#%d' % (shell.replace('ansbook-', ''), st['pass'])
            g.check('三零[%s]：error/Overfull/Underfull/Missing＝0/0/0/0 且 exit=0' % tag,
                    st['rc'] == 0 and st['error'] == 0 and st['overfull'] == 0
                    and st['underfull'] == 0 and st['missing'] == 0,
                    'rc=%d %d/%d/%d/%d' % (st['rc'], st['error'], st['overfull'],
                                           st['underfull'], st['missing']))
            g.check('对号[%s]：log ANSKEY 序≡册tex序（逐位）' % tag, st['anskeys'] == book_seq,
                    '%d键' % len(st['anskeys']))
            g.check('对号[%s]：log ANSKEY 集合≡canonical（双向diff）' % tag,
                    set(st['anskeys']) == set(canonical), '')
            seqs.append(st['anskeys'])
    g.check('对号：两档×两遍 ANSKEY 序恒等（4编全同）', all(s == seqs[0] for s in seqs), '')
    if '正册装配序' in ordernote:
        src_log = RE_KEYLOG.findall(read_text(os.path.join(piece['dir'], 'main-true.log')))
        g.check('对号：册log序≡正册log序（逐位）', seqs[0] == src_log,
                '%d vs %d 键' % (len(seqs[0]), len(src_log)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('piece', help='成卷 tex 件目录（含 main.tex＋qp-m3.sty 副本）')
    ap.add_argument('--out', default=None, help='输出册目录（默认 工作区/_tmpM3抽答器0914/<件型>-<片名>）')
    ap.add_argument('--order', choices=['zhengce', 'canonical'], default='zhengce',
                    help='zhengce＝正册装配序（默认）；canonical＝冻结manifest键序')
    ap.add_argument('--skip-compile', action='store_true')
    ap.add_argument('--skip-png', action='store_true')
    args = ap.parse_args()

    piece_dir = os.path.normpath(args.piece)
    piece = parse_piece(piece_dir)
    N = len(piece['blocks'])
    canonical, can_tag = resolve_canonical(piece_dir, [b['key'] for b in piece['blocks']])
    led_vals, led_nums, led_path = load_ledger(piece_dir)
    ordered, ordernote = order_blocks(piece, canonical, args.order)

    out = args.out or os.path.join(REPO, '工作区', '_tmpM3抽答器0914',
                                   '%s-%s' % (os.path.basename(os.path.dirname(piece_dir)),
                                              os.path.basename(piece_dir)))
    print('== 抽册：%s → %s' % (piece_dir, out))
    print('  片=%s｜件型=%s｜键数=%d｜canonical来源=%s｜册序=%s'
          % (pian_name(piece_dir), piece['jianming'], N, can_tag, ordernote))
    sty_md5, _ = write_booklet(out, piece, ordered, args.order, ordernote)
    print('  落盘：ansbook.tex＋ansbook-true/false.tex＋qp-m3.sty（md5 %s 锁同）' % sty_md5)

    bk = reparse_booklet(out)
    g = Gates()
    print('== 门①守恒＋对号（tex 层）＋钉值（值台账腿） ==')
    exp_seq = gate_tex(g, piece, bk, canonical, led_vals, led_nums, ordernote)
    print('== 门②钉值（正册件内值腿·硬断言） ==')
    gate_value(g, piece, bk, canonical)

    pdf_pages, leak_read = None, '未跑'
    if not args.skip_compile:
        print('== 编译（双档×两遍，cwd＝册目录） ==')
        stats = {s: compile_shell(out, s) for s in ('ansbook-true', 'ansbook-false')}
        for s, sts in stats.items():
            for st in sts:
                print('  %s#%d rc=%d err=%d over=%d under=%d miss=%d anskey=%d'
                      % (s, st['pass'], st['rc'], st['error'], st['overfull'],
                         st['underfull'], st['missing'], len(st['anskeys'])))
        print('== 门③三零＋对号（log 层） ==')
        gate_log(g, piece, stats, exp_seq, canonical, ordernote)
        print('== 门④PDF 层（双档） ==')
        leak_lines, allowed_norm, tj_path = build_leakset(piece)
        if leak_lines is None:
            g.check('PDF：题面泄漏＝0（题面库缺 %s，无法断言）' % tj_path, False, '缺件')
        else:
            pdf_pages = gate_pdf(g, out, piece, bk, canonical, leak_lines, allowed_norm)
            leak_read = '题面run %d 条（豁免haystack=正册答案块体）' % len(leak_lines)
        if not args.skip_png:
            nt, nf = render_png(out, 'true'), render_png(out, 'false')
            print('== PNG 留证：png-true %d 页／png-false %d 页（150dpi） ==' % (nt, nf))
    else:
        print('== 编译跳过（--skip-compile）：log/PDF 门未跑 ==')

    print()
    print('答案抽册器：', '全绿' if not g.reds else '红 %d 项：%s' % (len(g.reds), g.reds))
    readings = {'片': pian_name(piece_dir), '件型': piece['jianming'],
                '源件md5': piece['md5'], '键数': N, 'canonical来源': can_tag,
                '册序': ordernote, 'out': out.replace('\\', '/'),
                'sty_md5': sty_md5,
                '册值快照': {k: bk['vals'][k] for k in bk['seq']},
                '门读数': [{'判定': t, '项': n, '读数': d} for t, n, d in g.rows],
                '红': g.reds, '页数': pdf_pages, '泄漏口径': leak_read,
                '台账': led_path.replace('\\', '/') if led_path else None}
    rp = os.path.join(out, '抽册读数.json')
    json.dump(readings, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('读数落盘 →', rp)
    sys.exit(0 if not g.reds else 1)


if __name__ == '__main__':
    main()
