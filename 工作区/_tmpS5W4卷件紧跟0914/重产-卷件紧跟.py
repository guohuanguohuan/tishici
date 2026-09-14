# -*- coding: utf-8 -*-
r"""重产-卷件紧跟.py — S5-W4 阶段二：M3 三卷按 \juancols 三栏回流制重产（案B 附卷制退役）。
输入＝各卷 main.tex（改前自存 main.tex.bak_w4）；输出＝新 main.tex＋main-pure.tex（唯一差 [pure]）。
题面字符零改：题面行（\ti/\optline/\qpart/\zuhang/\vgt/\jphead）自 bak 逐行原样迁移；
答案块自卷末附卷逐字节原样内联到题后（仅随流位移）。对账脚本＝题面零改-对账.py。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
VOLS = {
    '测评卷': ('2章-测', 19),
    os.path.join('滚动卷', '滚A'): ('2章-滚A', 16),
    os.path.join('滚动卷', '滚B'): ('2章-滚B', 16),
}

EPREAMBLE = r'''% ------------------------------------------------------------
% 件型层 E′｜三栏排布器（S5-W4 阶段二：零高固定栏 → multicols 三栏回流）
%   观感三参数锁定：栏宽 \jpcolw=120mm（＝multicol 列宽）、栏距 \jpgap=11mm（＝\columnsep，
%   同旧手拼 \hspace{\jpgap}）、无栏线（旧手拼三栏本无线）。全幅 382＝3×120＋2×11。
%   退役（案B）：\jpcol 零高申报／\jpthree 手分栏／\jplead／「\setlength\linewidth 换装补钉」
%   ／卷末附卷页／\anskey 补偿发射／速查表 \datu+\dabiao——答案块随题入流，
%   锚点由 ansblockbegin 恒发（sty:556，双档 M3-ANSKEY 恒等由源结构保证）。
%   [D] 门「零高固定栏承件族」判定随零高结构消失自然失配，卷件退出承件族走 strict 严档。
% ------------------------------------------------------------
\setlength{\columnsep}{\jpgap}
\setlength{\columnseprule}{0pt}
% 栏底降部收口：article 默认 \\maxdepth=4pt（1.41mm）＝末行盒可伸出列高，
%   266.6＋1.41＝268.0 越腿3 设计线 267.6（滚B 括线底规实证）。收 2.5pt（0.88mm）
%   → 列墨底 ≤267.48，门线内；只影响贴线末行落点，排印间距零变动。
\maxdepth=2.5pt
\splitmaxdepth=2.5pt
\newenvironment{juancols}
  {\begin{multicols}{3}\fontsize{10.5pt}{17.7pt}\selectfont}%
  {\end{multicols}}
'''

CASEB_COMMENT = {
    '测评卷': '''%   S5-W4 阶段二重产（0914）：案B 附卷制退役——三栏回流制 \\juancols，答案块随题入流
%   （题后紧跟）；卷末附卷页／\\anskey 补偿发射／速查表 \\dabiao 全撤，锚点 ansblock 恒发。''',
    os.path.join('滚动卷', '滚A'): '''% S5-W4 阶段二重产（0914）：案B 附卷制退役——三栏回流制 \\juancols，答案块随题入流
% （题后紧跟）；卷末附卷页／\\anskey 补偿发射／速查表 \\dabiao 全撤，锚点 ansblock 恒发。''',
}
CASEB_COMMENT[os.path.join('滚动卷', '滚B')] = CASEB_COMMENT[os.path.join('滚动卷', '滚A')]
CASEB_OLD = {
    '测评卷': '%   案B 附卷制：答案迁卷末附卷、逐题 % ans: 锚、速查表纯题档 \\ifshowans 吞、\n%   纯题档 \\anskey 补偿发射（M3-ANSKEY 双档恒等）。',
    os.path.join('滚动卷', '滚A'): '% 案B 附卷制：答案迁卷末附卷、% ans: 锚、速查表纯题档吞、\\anskey 补偿发射。',
}
CASEB_OLD[os.path.join('滚动卷', '滚B')] = CASEB_OLD[os.path.join('滚动卷', '滚A')]

JUNK_EXACT = {'\\jpthree{', '\\jpthree{\\jplead', '}{', '}', '}\\jplead', '}{\\jplead', '\\jplead'}


def is_junk(s):
    return (s == '' or s == '\\begin{document}' or s.startswith('%')
            or s.startswith('\\newpage')
            or s.startswith('\\ifshowans') or s == '\\fi'
            or s.startswith('\\anskey{')
            or s in JUNK_EXACT)


def parse_old(text):
    """返回 (题面流行表, {键: ansblock 原文(含首尾行, 原缩进)}, 区位点)。"""
    i0 = text.index('\\begin{document}')
    i1 = text.index('% ===================== 卷末附卷')
    body = text[i0:i1]
    app = text[i1:]
    flow = []
    for ln in body.splitlines():
        if ln.lstrip().startswith('\\jpthree{'):
            ln = ln.lstrip()[len('\\jpthree{'):]      # 剥栏组前缀，保行内内容（如 \jphead）
        s = ln.strip()
        if is_junk(s):
            continue
        flow.append(ln.rstrip())
    blocks = {}
    cur = None
    for ln in app.splitlines():
        m = re.search(r'\\begin\{ansblock\}\[([^\]]+)\]', ln)
        if m:
            cur = [ln]
            continue
        if cur is not None:
            cur.append(ln)
            if '\\end{ansblock}' in ln:
                blocks[cur_key(cur[0])] = '\n'.join(cur)
                cur = None
    return flow, blocks


def cur_key(begin_ln):
    return re.search(r'\\begin\{ansblock\}\[([^\]]+)\]', begin_ln).group(1)


def rebuild(flow, blocks, keys_prefix, nkeys, volname):
    # 题面行按题分组：遇 \ti 开新题；题的 ansblock 在该题内容行之后、
    # 下一结构行（\vgt/\zuhang）或下一 \ti 或流尾之前内联。
    tis = [i for i, ln in enumerate(flow) if ln.strip().startswith('\\ti{')]
    assert len(tis) == nkeys, '题数 %d ≠ %d' % (len(tis), nkeys)
    # 单遍扫描：题面行按序迁移；结构行（\vgt/\zuhang）或流尾前先内联当前题答案块
    out = []
    cur_t = None          # 当前题号
    cur_keyname = None
    for i, ln in enumerate(flow):
        s = ln.strip()
        if s.startswith('\\ti{'):
            if cur_t is not None:               # 连题无结构行：新题前先落当前题块
                out.append(blocks[cur_keyname])
                cur_t = None
            cur_t = int(re.match(r'\\ti\{(\d+)\}\{', s).group(1))
            cur_keyname = '%s-%d' % (keys_prefix, cur_t)
            out.append(ln)
            continue
        struct = s.startswith('\\vgt{') or s.startswith('\\zuhang{') or s.startswith('\\jphead')
        if struct and cur_t is not None:
            # 结构行前：先内联当前题答案块（题面行已全部出现）
            out.append(blocks[cur_keyname])
            cur_t = None
        out.append(ln)
    if cur_t is not None:
        out.append(blocks[cur_keyname])
        cur_t = None
    # 校验：每题块恰落一次
    joined = '\n'.join(out)
    assert joined.count('\\begin{ansblock}') == nkeys, '内联块数 ≠ %d' % nkeys
    for n in range(1, nkeys + 1):
        k = '%s-%d' % (keys_prefix, n)
        assert k in blocks, '缺块 %s' % k
        assert blocks[k] in joined, '块 %s 未原样内联' % k
    header = ('\n\\begin{document}\n'
              '% ============ S5-W4 阶段二：题-答-解析同流（三栏回流制），案B 手分页/附卷退役 ============\n'
              '\\begin{juancols}\n')
    return header + '\n'.join(out) + '\n\\end{juancols}\n\\end{document}\n'


def main():
    for vol, (prefix, nkeys) in VOLS.items():
        d = os.path.join(BASE, vol)
        src_p = os.path.join(d, 'main.tex')
        bak_p = os.path.join(d, 'main.tex.bak_w4')
        text = io.open(src_p, encoding='utf-8', newline='').read()
        if not os.path.isfile(bak_p):
            io.open(bak_p, 'w', encoding='utf-8', newline='').write(text)
            print('[%s] 自存 main.tex.bak_w4' % vol)
        bak = io.open(bak_p, encoding='utf-8', newline='').read()
        assert text == bak, '[%s] main.tex 与 bak 不一致（重跑护）' % vol
        # 案B 注记行替换
        assert CASEB_OLD[vol] in text, '[%s] 案B 注记行未找到' % vol
        text = text.replace(CASEB_OLD[vol], CASEB_COMMENT[vol])
        # 件型层 E 区替换：从「% 件型层 E｜」标记行的前一行（% --- 行）到 \begin{document} 前
        lines = text.split('\n')
        ei = next(i for i, ln in enumerate(lines) if ln.startswith('% 件型层 E｜'))
        bi = next(i for i, ln in enumerate(lines) if ln == '\\begin{document}')
        new_lines = lines[:ei - 1] + EPREAMBLE.split('\n')[:-1] + lines[bi:]
        text2 = '\n'.join(new_lines)
        flow, blocks = parse_old(text2)
        assert len(blocks) == nkeys, '[%s] 附卷块数 %d ≠ %d' % (vol, len(blocks), nkeys)
        body = rebuild(flow, blocks, prefix, nkeys, vol)
        new_tex = text2[:text2.index('\\begin{document}')] + body
        io.open(src_p, 'w', encoding='utf-8', newline='').write(new_tex)
        # 双壳：唯一差＝[pure]
        pure = new_tex.replace('\\usepackage{qp-m3}', '\\usepackage[pure]{qp-m3}')
        assert pure != new_tex
        io.open(os.path.join(d, 'main-pure.tex'), 'w', encoding='utf-8', newline='').write(pure)
        print('[%s] 重产 OK：main.tex %d→%d 行｜题 %d 题 %d 块内联｜main-pure.tex 同步' % (
            vol, bak.count('\n') + 1, new_tex.count('\n') + 1, nkeys, len(blocks)))


if __name__ == '__main__':
    main()
