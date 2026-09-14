# -*- coding: utf-8 -*-
r"""重产-回流制.py — S5-W4 阶段二·M2/P1 四卷重产（\jpthree 零高固定栏 → \juancols multicols 三栏回流）

对每卷执行：
  1) main.tex / main-pure.tex 改前自存 .bak_w4（已存在则拒跑防覆盖）
  2) 件型层 E（\jpcol/\jpthree/\jplead）→ E′（\columnsep/\columnseprule/juancols）；
     \datu/\dabiao 定义随速查表退役整体撤销
  3) 正文：\jpthree 手分栏解包为单一题流（\newpage/页横幅随解包废弃），卷末附卷 ansblock
     逐键内联到其题末行之后；退役＝\ifshowans\dabiao\fi／\ifshowans\else \anskey×N \fi／附卷整页
  4) 题面零改举证：旧件题流（剔结构件/退役件/附卷）与新件题流（剔 juancols 壳/ansblock）逐行比对
  5) main-pure.tex 重生成（唯一差＝[pure] 包选项）

红线：题面行原样搬运零改写；ansblock 行原样搬运零改写；写域＝四卷目录＋本目录。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'C:/提示词/工作区/_tmp换装正装0914'
VOLUMES = [
    (os.path.join(ROOT, 'M2测评滚动/测评卷'), 19),
    (os.path.join(ROOT, 'M2测评滚动/滚动卷A'), 16),
    (os.path.join(ROOT, 'M2测评滚动/滚动卷B'), 16),
    (os.path.join(ROOT, 'P1测评本/测评卷'), 19),
]
OUTDIR = r'C:/提示词/工作区/_tmpS5W4卷件紧跟0914/_M2P1'

EPRIME_COM = '''% ------------------------------------------------------------
% 件型层 E′｜三栏排布器（S5-W4 阶段二·卷件三栏回流制：零高固定栏 \\jpthree → multicols \\juancols）
%   观感三参数锁定：栏宽 \\jpcolw=120mm（＝multicol 列宽）、栏距 \\jpgap=11mm（＝\\columnsep，
%   同旧手拼 \\hspace{\\jpgap}）、无栏线。全幅 382＝3×120＋2×11，三栏逐位等宽等距＝旧观感。
%   multicol 系既载（\\multicolsep=0pt＋\\raggedcolumns）；旧 \\jpcol 内「\\setlength\\linewidth{\\jpcolw}
%   换装补钉」退役：multicol 逐栏自更新 \\linewidth。题面与 ansblock 同流顺写，栏满在合法切点
%   切栏、页满翻页，越限必报 Overfull——静默吞块在机制上不存在（设计件：机制设计-卷件三栏回流制.md）。
% ------------------------------------------------------------
\\setlength{\\columnsep}{\\jpgap}
\\setlength{\\columnseprule}{0pt}
\\newenvironment{juancols}
  {\\begin{multicols}{3}\\fontsize{10.5pt}{17.7pt}\\selectfont}%
  {\\end{multicols}}
'''

W4NOTE = '''% ------------------------------------------------------------
% S5-W4 阶段二重产（2026-09-14，回流制，主脑过目样张后放行）：件型层 E′ \\juancols（multicols
% 三栏回流）替 \\jpthree 零高固定栏；卷末附卷答案块逐键内联题后（题-答-解析同流）；
% 退役＝附卷页／\\anskey 补偿发射／速查表（\\dabiao 定义随撤）。题面字符零改
% （举证＝_tmpS5W4卷件紧跟0914/_M2P1/题面零改举证-*.txt）；双壳纪律＝main-pure 唯一差 [pure]。
% ------------------------------------------------------------
'''

RE_BANNER = re.compile(r'^% =+ 第.*页')            # 旧手分页横幅注释（撤，页码语义失效）
RE_OPENER = re.compile(r'^\\jpthree\{')
RE_GROUP2 = re.compile(r'^\}\{\\jplead\s*$')        # 「}{\jplead」组界行
RE_BARE = re.compile(r'^\}$')                       # \jpthree 收束行
RE_TI = re.compile(r'^\s*\\ti\{(\d+)\}\{')
RE_PRELINE = re.compile(r'^(?:\s*%|\s*$|\s*\\vgt\{|\s*\\zuhang\{|\s*\\setcounter\{page\})')
RE_PKG = re.compile(r'^\\usepackage\{(qp-m3(?:p-overlay)?)\}[ \t]*(?:%.*)?\r?$', re.M)


def read_lines(path):
    with io.open(path, encoding='utf-8', newline='') as f:
        return f.readlines()


def write_lines(path, lines):
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.writelines(lines)


def backup(path):
    bak = path + '.bak_w4'
    if os.path.exists(bak):
        sys.exit('红｜备份已存在，拒覆盖：%s' % bak)
    write_lines(bak, read_lines(path))


def strip_arg(arg):
    """剥去组首导件行（\\jphead／\\jplead），返回余下行。"""
    lines = arg.splitlines(keepends=True)
    first = lines[0].strip() if lines else ''
    if first in ('\\jphead', '\\jplead'):
        return lines[1:]
    sys.exit('红｜组首非导件行：%r' % first[:40])


def extract_jpthree_args(text, start):
    """text[start:] 起 \\jpthree{a}{b}{c} → (三组串, 收束位)。花括号配平计 \\ 转义。"""
    i = text.index('\\jpthree{', start) + len('\\jpthree')
    args = []
    for _ in range(3):
        while text[i] in ' \t\r\n':
            i += 1
        assert text[i] == '{', '组首非花括号@%d' % i
        depth, j, buf = 0, i, []
        while True:
            c = text[j]
            buf.append(c)
            if c == '\\' and j + 1 < len(text):
                buf.append(text[j + 1])
                j += 2
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        args.append(''.join(buf)[1:-1])
        i = j + 1
    return args, i


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    for d, want_n in VOLUMES:
        name = os.path.basename(d.rstrip('/\\'))
        print('==== %s（%d 题）====' % (name, want_n))
        src = os.path.join(d, 'main.tex')
        lines = read_lines(src)
        text = ''.join(lines)
        nl = '\r\n' if '\r\n' in text else '\n'
        assert nl == '\r\n', '%s 行尾非 CRLF' % name

        mpkg = RE_PKG.search(text)
        assert mpkg, '%s 未找到包选项行' % name
        pkg, pkg_pure = mpkg.group(0).rstrip(), mpkg.group(0).replace('{qp', '[pure]{qp').rstrip()

        # —— 双壳纪律（改前）：旧 main vs 旧 main-pure 唯一差＝[pure] 包选项 ——
        pure_path = os.path.join(d, 'main-pure.tex')
        pure_text = ''.join(read_lines(pure_path))
        assert text.replace(pkg, pkg_pure) == pure_text, '%s 双壳唯一差断言失败' % name
        print('  双壳唯一差 OK（%s → [pure]）' % pkg)

        # —— 定位：导言／正文／附卷 ——
        body_l = next(i for i, l in enumerate(lines) if l.rstrip('\r\n') == '\\begin{document}')
        app_l = next(i for i, l in enumerate(lines) if '卷末附卷' in l)
        end_l = next(i for i, l in enumerate(lines) if l.rstrip('\r\n') == '\\end{document}')
        assert body_l < app_l < end_l

        # —— 附卷 ansblock 全量摘取（案B 下 ansblock 仅存附卷）——
        app_text = ''.join(lines[app_l:end_l])
        spans = []
        for m in re.finditer(r'[^\S\n]*\\begin\{ansblock\}\[([^\]]+)\].*?^[ \t]*\\end\{ansblock\}[ \t]*(?=\r?$)',
                             app_text, re.M | re.S):
            spans.append((m.group(1), m.group(0)))
        assert len(spans) == want_n, '%s 块数 %d≠%d' % (name, len(spans), want_n)
        for key, span in spans:
            assert span.count('\\ansitem{') == 1, '%s 块 %s \\ansitem≠1' % (name, key)
        nums = [int(re.search(r'(\d+)$', k).group(1)) for k, _ in spans]
        assert nums == list(range(1, want_n + 1)), '%s 键尾序 %s' % (name, nums)
        blocks = {int(re.search(r'(\d+)$', k).group(1)): span for k, span in spans}

        # —— 正文流：解包全部 \jpthree（\\newpage／页横幅随解包废弃）——
        body_text = ''.join(lines[body_l + 1:app_l])
        head_pre, flow, pos = [], [], 0

        def collect(chunk):
            for ln in chunk.splitlines(keepends=True):
                st = ln.strip()
                if RE_BANNER.match(st) or st == '\\newpage':
                    continue
                (head_pre if not flow else flow).append(ln)

        while True:
            nxt = body_text.find('\\jpthree{', pos)
            if nxt < 0:
                tail = body_text[pos:]
                assert '\\ifshowans' not in tail and '\\anskey' not in tail, '尾段残留退役件'
                collect(tail)
                break
            collect(body_text[pos:nxt])
            args, pos = extract_jpthree_args(body_text, nxt)
            nlpos = body_text.find('\n', pos)
            pos = nlpos + 1 if nlpos >= 0 else len(body_text)   # 弃收束行尾余量（\r\n）
            for a in args:
                flow.extend(strip_arg(a))

        # —— 退役件剔除（速查表挂载＋纯题补偿发射，恰 4 行一处）——
        out, i, retired = [], 0, 0
        while i < len(flow):
            s = flow[i].strip()
            if re.match(r'^\\ifshowans\\dabiao\\fi', s) or re.match(r'^\\ifshowans\\else', s):
                j = i + 1
                while not re.match(r'^\\fi$', flow[j].strip()):
                    st_j = flow[j].strip()
                    assert '\\anskey{' in st_j or re.match(r'^\\ifshowans\\else', st_j), \
                        '退役段意外行：%r' % flow[j][:40]
                    j += 1
                retired += j - i + 1
                i = j + 1
                continue
            out.append(flow[i])
            i += 1
        assert retired == 4, '%s 退役行数 %d≠4' % (name, retired)
        flow = out

        # —— 分段：段 n＝[前导件行（空/注释/\vgt/\zuhang/setcounter）]＋[\ti{n}..段末] ——
        ti_at = {}
        for idx, ln in enumerate(flow):
            m = RE_TI.match(ln)
            if m:
                n = int(m.group(1))
                assert n not in ti_at, '%s \\ti{%d} 重号' % (name, n)
                ti_at[n] = idx
        assert sorted(ti_at) == list(range(1, want_n + 1)), '%s 题号域 %s' % (name, sorted(ti_at))
        starts = {}
        for n, idx in ti_at.items():
            s = idx
            while s - 1 >= 0 and RE_PRELINE.match(flow[s - 1]):
                s -= 1
            starts[n] = s
        assert starts[1] == 0
        segs = {n: flow[starts[n]:(starts[n + 1] if n + 1 in starts else len(flow))]
                for n in range(1, want_n + 1)}

        # —— 组装新件 ——
        new = list(lines[:body_l + 1]) + list(head_pre)
        new.append('% ===================== 题-答-解析同流（S5-W4 回流制）：三栏自动回流，题后紧跟 ansblock =====================' + nl)
        new.append('\\begin{juancols}' + nl)
        new.append('\\jphead' + nl)
        for n in range(1, want_n + 1):
            new.extend(segs[n])
            new.append(blocks[n] if blocks[n].endswith('\n') else blocks[n] + nl)
        new.append('\\end{juancols}' + nl)
        new.append('\\end{document}' + nl)

        # —— 导言改造：E 层→E′；\datu/\dabiao 随撤；W4 注记横幅 ——
        pre_lines = new[:body_l + 1]
        assert sum(1 for l in pre_lines if '\\newcommand{\\jpcol}' in l) == 1
        assert sum(1 for l in pre_lines if '\\newcommand{\\datu}' in l) == 1
        j = next(i for i, l in enumerate(pre_lines) if '\\newcommand{\\jpcol}' in l)
        k = next(i for i, l in enumerate(pre_lines) if '\\newcommand{\\jplead}' in l)
        b0 = j
        while b0 - 1 >= 0 and pre_lines[b0 - 1].lstrip().startswith('%'):
            b0 -= 1
        pre_lines[b0:k + 1] = [EPRIME_COM.replace('\n', nl)]
        j = next(i for i, l in enumerate(pre_lines) if '\\newcommand{\\datu}' in l)
        k = j
        while pre_lines[k + 1].strip() != '\\begin{document}':
            k += 1
        b0 = j
        while b0 - 1 >= 0 and pre_lines[b0 - 1].lstrip().startswith('%'):
            b0 -= 1
        del pre_lines[b0:k + 1]
        b = next(i for i, l in enumerate(pre_lines) if l.rstrip('\r\n') == '\\begin{document}')
        pre_lines[b:b] = [W4NOTE.replace('\n', nl)]
        new = pre_lines + new[body_l + 1:]

        # —— 题面零改举证：旧件题流 vs 新件题流（双侧同剔结构件/退役件/横幅/壳/ansblock）——
        def question_flow(ls, side):
            res, skip_ans = [], False
            for ln in ''.join(ls).splitlines(keepends=True):
                s = ln.rstrip('\r\n')
                st = s.strip()
                if side == 'old' and '卷末附卷' in s:
                    break
                if RE_BANNER.match(st):
                    continue
                if side == 'new' and '题-答-解析同流（S5-W4 回流制）' in st:
                    continue
                if st in ('\\begin{juancols}', '\\end{juancols}', '\\jphead', '\\jplead', '\\newpage',
                          '\\begin{document}', '\\end{document}'):
                    continue
                if RE_OPENER.match(st) or RE_GROUP2.match(st) or RE_BARE.match(st):
                    continue
                if (re.match(r'^\\ifshowans\\dabiao\\fi', st) or re.match(r'^\\ifshowans\\else', st)
                        or '\\anskey{' in st or st == '\\fi'):
                    continue
                if st.startswith('\\begin{ansblock}'):
                    skip_ans = True
                    continue
                if st.startswith('\\end{ansblock}'):
                    skip_ans = False
                    continue
                if skip_ans:
                    continue
                res.append(ln)
            return res

        old_flow = question_flow(lines[body_l + 1:app_l], 'old')
        nb = next(i for i, l in enumerate(new) if l.rstrip('\r\n') == '\\begin{document}')
        new_flow = question_flow(new[nb + 1:], 'new')
        same = old_flow == new_flow
        ev = os.path.join(OUTDIR, '题面零改举证-%s.txt' % name)
        with io.open(ev, 'w', encoding='utf-8', newline='') as f:
            f.write('题面零改举证｜%s｜S5-W4 阶段二 回流制重产 2026-09-14\r\n' % name)
            f.write('口径：双侧同剔结构件（\\jpthree 三器/\\newpage/页横幅/壳行）＋退役件（速查挂载/\\anskey 补偿）\r\n')
            f.write('＋ansblock（旧附卷块/新内联块整块剔）＋导言宏区；余行逐行比对。\r\n')
            f.write('旧件题流 %d 行 vs 新件题流 %d 行 → %s\r\n\r\n' % (
                len(old_flow), len(new_flow), '逐行一致（零改）' if same else '存在差异！'))
            if not same:
                import difflib
                for d in difflib.unified_diff([l.rstrip('\r\n') for l in old_flow],
                                              [l.rstrip('\r\n') for l in new_flow],
                                              fromfile='旧件题流', tofile='新件题流',
                                              lineterm='', n=1):
                    f.write(d + '\r\n')
                f.write('\r\n')
            f.write('—— 旧件题流全文 ——\r\n')
            f.writelines(old_flow)
            f.write('\r\n—— 新件题流全文 ——\r\n')
            f.writelines(new_flow)
        assert same, '%s 题面流比对不一致，举证见 %s' % (name, ev)

        # —— 落盘（改前自存 .bak_w4）＋纯题壳重生成 ——
        backup(src)
        write_lines(src, new)
        backup(pure_path)
        new_text = ''.join(new)
        assert new_text.count(pkg) == 1 and new_text.count(pkg_pure) == 0
        write_lines(pure_path, new_text.replace(pkg, pkg_pure).splitlines(keepends=True))
        print('  改造完成：%d 题逐键内联｜退役 4 行｜举证 %s' % (want_n, os.path.basename(ev)))
    print('四卷改造全部完成')


if __name__ == '__main__':
    main()
