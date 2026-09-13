# -*- coding: utf-8 -*-
"""只读探查⑤：丁区 51 键值串控制序列＋危险字符扫描，以及三件件面宏名 vs qp-m3 定义覆盖检查。"""
import io, os, re, sys, json
sys.stdout = io.TextIOWWrapper = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = r"C:/提示词/工作区/M2-第1章量产0911/成卷/答案册"
STY = r"C:/提示词/工作区/_tmpM3toolchain0913/qp-m3.sty"
CJ = r"C:/提示词/工作区/M2-第1章量产0911/成卷"

lines = io.open(os.path.join(ROOT, "body.tex"), encoding="utf-8").read().split("\n")
i0 = next(i for i, l in enumerate(lines) if "【丁】" in l)
cur, recs = None, []
for ln in lines[i0:]:
    s = ln.strip()
    m = re.match(r"^% pair:(\S+)$", s)
    if m:
        cur = {"key": m.group(1), "item": None, "note": None}
        recs.append(cur); continue
    if not cur:
        continue
    m = re.match(r"^\\ansitem\{(\d+)\}\{(.*)\}$", s)
    if m and cur["item"] is None:
        cur["item"] = m.group(2); continue
    m = re.match(r"^\\ansline\{(.+?)\}\{(.*)\}$", s)
    if m:
        cur["note"] = m.group(2)

pairs = {r["key"]: (r["item"] or "") for r in recs}
snap = {k: v for k, v in json.load(io.open(os.path.join(ROOT, "值快照.json"), encoding="utf-8")).items()
        if k.startswith(("测-", "滚A-", "滚B-"))}
print("键数:", len(pairs), "快照键数:", len(snap), "键集相等:", set(pairs) == set(snap),
      "值恒等:", pairs == snap)

blob = " ".join((r["item"] or "") + " " + (r["note"] or "") for r in recs)
cs = sorted(set(re.findall(r"\\[a-zA-Z]+", blob)))
sty = io.open(STY, encoding="utf-8").read()
miss = [c for c in cs if c not in sty]
print("值串控制序列数:", len(cs), "| sty 未定义:", miss)
for ch in ("#", "\\\\\\", "$$"):
    pass
print("含 # 键:", [r["key"] for r in recs if "#" in ((r["item"] or "") + (r["note"] or ""))])
print("含行内注释 %% 键:", [r["key"] for r in recs if "%" in ((r["item"] or "") + (r["note"] or ""))])
print("含 \\ov 键数:", sum(1 for r in recs if "\\ov{" in ((r["item"] or "") + (r["note"] or ""))))

# 件面使用宏 vs qp-m3 ∪ 件内定义
stynames = set(re.findall(r"\\(?:re)?newcommand\*?\{\\([a-zA-Z@]+)\}", sty))
stynames |= set(re.findall(r"\\NewDocumentCommand\{\\([a-zA-Z@]+)\}", sty))
stynames |= set(re.findall(r"\\newenvironment\{([a-zA-Z@]+)\}", sty))
stynames |= set(re.findall(r"\\(?:newlength|newdimen|newsavebox)\{?\\([a-zA-Z@]+)", sty))
stynames |= set(re.findall(r"\\newif\\([a-zA-Z@]+)", sty))
stynames |= set(re.findall(r"\\definecolor\{([a-zA-Z0-9]+)\}", sty))
stynames |= set(re.findall(r"\\setCJKfamilyfont\{([a-zA-Z@]+)\}", sty))
kernel = set("""documentclass usepackage begin end input geometry setlength renewcommand renewcommand par noindent
hfil hfill hspace quad qquad noindent nointerlineskip vskip vskip vglue bigskip smallskip raisebox hbox vtop vbox
textwidth linewidth columnwidth bp unitlength mm pt dimexpr numexpr ifnum fi else ifdim newcommand makebox rule color
colorbox textcolor definecolor hskip kern rm defaultfont fontsize selectfont rm S T M L igname undefined hrule
noalign hline multicols label ref pagestyle fancyfoot fancyhead fancyhf addtolength advance left right big Big bigg
mathrm mathbf mathit mathsf operatorname frac dfrac tfrac sqrt angle triangle overrightarrow cdot times le ge ne
langle rangle varphi theta alpha beta gamma pi in notin subset cup cap emptyset circ ^{ }_{ parskip parindent
raggedbottom flushbottom linespread emergencystretch tolerance clubpenalty widowpenalty binoppenalty relpenalty
arraystretch tabcolsep arrayrulewidth multicolssetlength twocolsep columnsep columnseprule topmargin rightmargin
oddsidemargin evensidemargin textheight textwidth topskip skipabovecaptions z@ newbox savebox global setbox box
rlap smash rotatebox mathstrut strut depth height width totalheight depth longtablesizing xits""".split())
for name in ("测评卷", "滚动卷/滚A", "滚动卷/滚B"):
    p = os.path.join(CJ, name, "main.tex")
    t = io.open(p, encoding="utf-8").read()
    body = t[t.index("\\begin{document}"):]
    used = set(re.findall(r"\\([a-zA-Z@]+)", body))
    loc = set(re.findall(r"\\(?:re)?newcommand\*?\{\\([a-zA-Z@]+)\}", t))
    loc |= set(re.findall(r"\\newdimen\\([a-zA-Z@]+)", t))
    loc |= set(re.findall(r"\\newlength\{\\([a-zA-Z@]+)\}", t))
    loc |= set(re.findall(r"\\newenvironment\{([a-zA-Z@]+)\}", t))
    loc |= set(re.findall(r"\\definecolor\{([a-zA-Z0-9]+)\}", t))
    unmet = sorted(u for u in used if u not in stynames and u not in loc and u not in kernel)
    print("\n%s: begin{document} 后使用宏中 qp-m3 未定义（须六宏补载/件内已有）→ %s" % (name, unmet))
