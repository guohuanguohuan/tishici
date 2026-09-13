# -*- coding: utf-8 -*-
"""只读探查：qp-m3.sty 宏名集 vs 测评卷/滚动卷 main.tex 件内局部宏名集（撞名清单）。"""
import io, re, os, sys

ROOT = r"C:/提示词"
STY = os.path.join(ROOT, "工作区/_tmpM3toolchain0913/qp-m3.sty")

RE_DEF = [
    r"\\(?:re)?newcommand\*?\{\\([a-zA-Z@]+)\}",
    r"\\NewDocumentCommand\{\\([a-zA-Z@]+)\}",
    r"\\newenvironment\{([a-zA-Z@]+)\}",
    r"\\newlength\{\\([a-zA-Z@]+)\}",
    r"\\newdimen\{?\\([a-zA-Z@]+)",
    r"\\newif\\([a-zA-Z@]+)",
    r"\\newsavebox\{\\([a-zA-Z@]+)\}",
    r"\\definecolor\{([a-zA-Z0-9]+)\}",
]

def defs_of(path):
    t = io.open(path, encoding="utf-8").read()
    out = set()
    for r in RE_DEF:
        out |= set(re.findall(r, t))
    return t, out

t_sty, sty_names = defs_of(STY)
print("qp-m3.sty 定义名数:", len(sty_names))

for name in ["测评卷", "滚动卷/滚A", "滚动卷/滚B"]:
    p = os.path.join(ROOT, "工作区/M2-第1章量产0911/成卷", name, "main.tex")
    t, loc = defs_of(p)
    collide = sorted(loc & sty_names)
    print("\n---", name, "局部宏名数:", len(loc))
    print("撞名:", " ".join(collide))
    # qpJT* 参数使用面
    used = sorted(set(re.findall(r"\\(qpJT[A-Za-z]+)", t)))
    print("main 使用 qpJT* 参数:", " ".join(used))
    print("  其中 sty 未定义:", " ".join(x for x in used if x not in sty_names))
    # 六宏里定义的 qpJT 参数
    allsix = set()
    for f in ["qp-fonts.tex", "qp-layout.tex", "qp-parts.tex", "qp-headfoot.tex", "qp-titles.tex", "qp-blocks.tex"]:
        _, d = defs_of(os.path.join(os.path.dirname(p), f))
        allsix |= d
    print("六宏定义名数:", len(allsix))
    print("六宏有、sty 无（缺宏风险）:", " ".join(sorted(allsix - sty_names)))
    print("main 全文用到的宏名 - sty 定义集（粗算，含 LaTeX 内建）: 略")
