# -*- coding: utf-8 -*-
"""S7 双断言跑门前置盘点：逐件 tex 侧宏用量＋pdf 侧读数，供参数化断言标定。只读。"""
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

ROOT = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
os.chdir(ROOT)

items = (sorted(glob.glob('导学件/课时*')) + ['导学件/衔接节-1.2.1前', '导学件/章末-本章总结提升']
         + sorted(glob.glob('练习件/课时*')) + ['拓展册/上册', '拓展册/下册',
           '测评卷', '滚动卷/滚A', '滚动卷/滚B', '答案册', '装配/册目录页'])

def body_files(it):
    fs = ['main.tex']
    if os.path.exists(os.path.join(it, 'body.tex')):
        fs.append('body.tex')
    return fs

def strip_comments(t):
    # 去注释行（% 起始，含行首空白）；不去行内 %（题面可能有，保守保留）
    return '\n'.join(ln for ln in t.split('\n') if not ln.lstrip().startswith('%'))

hdr = f"{'item':<30s} {'pg':>3s} zhent kongb kongda huax tjdnr ansl jiex inclg tikz tabul hang 2em 例1 变式 答案值"
print(hdr)
for it in items:
    txt = ''
    for s in body_files(it):
        p = os.path.join(it, s)
        if os.path.exists(p):
            txt += open(p, encoding='utf-8').read()
    body = strip_comments(txt)
    def c(pat, t=None):
        return len(re.findall(pat, t if t is not None else body))
    pdf = os.path.join(it, 'main.pdf')
    npg = -1
    nli1 = nbs = nans = -1
    if os.path.exists(pdf):
        d = pymupdf.open(pdf)
        npg = d.page_count
        full = re.sub(r'\s+', '', ''.join(p.get_text() for p in d))
        nli1 = full.count('例1[') if '例1[' in full else full.count('例1')
        nbs = full.count('变式1')
        nans = full.count('[答案]')
        d.close()
    print(f"{it:<30s} {npg:>3d} {c(r'\\zhentib'):>2} {c(r'\\kongbai'):>4} {c(r'\\kongda'):>3} "
          f"{c(r'\\huaxing'):>2} {c(r'\\tjdnr'):>2} {c(r'\\ansline'):>2} {c(r'\\jiexi'):>2} "
          f"{c(r'\\includegraphics'):>2} {c(r'\\tikz'):>2} {c(r'begin{tabular'):>2} "
          f"{c(r'\\hangindent'):>2} {c(r'\\hspace\*\{2em\}'):>2} {nli1:>3} {nbs:>3} {nans:>3}")
