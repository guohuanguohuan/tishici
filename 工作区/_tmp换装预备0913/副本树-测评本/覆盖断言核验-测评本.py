# -*- coding: utf-8 -*-
r"""覆盖断言核验-测评本：迁移前后题面/题号/分值/组行/卷头制式逐项恒等 + 插入行白名单闭合

断言链（测评本「章覆盖断言」不在 tex 里，在台账的题号↔节映射上）：
  题面文本逐字节不变 + \ti 题号集不变 + \fenzhi 分值多重集不变 + \zuhang 组行不变
  ⇒ 台账八节分布读数（成卷/卷件值台账.md §一/§二、命制/命制-滚B-16题.md）迁移后仍真。
另：迁移插入/删除行必须全落在白名单内（ansblock 三行 + ansnote 解析行 + 换装四处改写），
    白名单外任何一行变动 = 越界，汇总里点名。
"""
import io, os, re, sys, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = [("测评卷", "测", 19), ("滚动卷A", "滚A", 16), ("滚动卷B", "滚B", 16)]
FAIL, PASS = [], [0]


def check(name, cond, detail=""):
    if cond:
        PASS[0] += 1
    else:
        FAIL.append(name + ("　" + detail if detail else ""))
    print(("  ✓ " if cond else "  ✗ ") + name + ("　" + detail if detail else ""))


DEFPAT = re.compile(r"^\\(re|new)?(new)?(command|environment|length|dimen|skip|if|counter|providecommand)\b")
ADD_OK = re.compile(r"^\+\s*(% ans:\S+|\\begin\{ansblock\}\[[^\]]+\]|\\end\{ansblock\}|"
                    r"\\ansitem\{\d+\}\{.*|\\ansnote\{解析\}\{.*|"
                    r"\\usepackage\{qp-m3\}|\\ansblockgrayfalse.*|\\providecommand\{\\ov\}.*|"
                    r"\\setlength\\linewidth\{\\jpcolw\}.*|\\ifshowans\\dabiao\\fi.*)$")
DEL_OK = re.compile(r"^\-\s*(\\input\{qp-[a-z]+\.tex\}|\\dabiao\s*$|%.*|)$")

for label, pref, nkeys in BOOKS:
    print("\n=== %s ===" % label)
    d = os.path.join(HERE, label)
    src = open(os.path.join(d, "main.src.tex"), encoding="utf-8").read()
    ans = {t: open(os.path.join(d, t + ".tex"), encoding="utf-8").read()
           for t in ("main", "main-pure", "main-ctl")}

    tipat = r"\\ti\{(\d+)\}\{"
    a_src = re.findall(tipat, src)
    for tag, s in ans.items():
        check("%s/%s：\\ti 题号序列逐字不变（%d 题）" % (label, tag, len(a_src)),
              re.findall(tipat, s) == a_src, "、".join(a_src))
    for tag, s in ans.items():
        check("%s/%s：题干正文（\\ti{N}{…} 全串）逐字不变" % (label, tag),
              re.findall(r"\\ti\{\d+\}\{(?:[^{}]|\{[^{}]*\})*\}", s, re.S) ==
              re.findall(r"\\ti\{\d+\}\{(?:[^{}]|\{[^{}]*\})*\}", src, re.S))
    fz = r"\\fenzhi\{([^}]*)\}"
    for tag, s in ans.items():
        check("%s/%s：\\fenzhi 分值多重集不变" % (label, tag),
              sorted(re.findall(fz, s)) == sorted(re.findall(fz, src)),
              " ".join(re.findall(fz, src)))
    zh = r"\\zuhang\{[^{}]*\}\{[^{}]*\}"
    for tag, s in ans.items():
        check("%s/%s：\\zuhang 组行不变（%d 处）" % (label, tag, len(re.findall(zh, src))),
              re.findall(zh, s) == re.findall(zh, src))
    for pat, what in [(r"时间：\d+分钟", "时间制式"), (r"分值：\d+分", "分值制式"),
                      (r"\\newcommand\{\\juanname\}\{[^}]*\}", "卷名定义"),
                      (r"\\jjuanming\}\{.*", "卷名宏体"), (r"\\jfuti\{.*", "副题宏体")]:
        m_src = re.findall(pat, src)
        for tag, s in ans.items():
            check("%s/%s：%s原样保留" % (label, tag, what), re.findall(pat, s) == m_src,
                  str([x[:26] for x in m_src[:1]]))
    for tag, s in ans.items():
        check("%s/%s：\\jpthree 三栏器调用次数不变（%d）" % (label, tag, src.count("\\jpthree")),
              s.count("\\jpthree") == src.count("\\jpthree"))
        check("%s/%s：栏宽 \\jpcolw=120.0mm 未改" % (label, tag), "{\\jpcolw}{120.0mm}" in s)
        ds = [l.strip() for l in src.splitlines() if DEFPAT.match(l.strip())]
        dn = [l.strip() for l in s.splitlines() if DEFPAT.match(l.strip())]
        diff = [x for x in dn if x not in ds] + [x for x in ds if x not in dn]
        allow = ("jpcol", "linewidth", "\\ov", "dabiao", "qp-m3", "ansblockgray")
        check("%s/%s：件型层定义除白名单外逐字不变（共 %d 条）" % (label, tag, len(ds)),
              all(any(a in x for a in allow) for x in diff),
              ("差异 " + " ⫶ ".join(x[:34] for x in diff[:2])) if diff else "")

    sli, ali = src.splitlines(), ans["main"].splitlines()
    u = list(difflib.unified_diff(sli, ali, n=0, lineterm=""))
    added = [l for l in u if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in u if l.startswith("-") and not l.startswith("---")]
    print("  插入行 %d，删除行 %d" % (len(added), len(removed)))
    bad = [l for l in added if not ADD_OK.match(l)]
    check("%s：插入行全在白名单内" % label, not bad,
          "越界：" + " ⫶ ".join(x[:44] for x in bad[:3]) if bad else "")
    bad = [l for l in removed if not DEL_OK.match(l)]
    check("%s：删除行全在白名单内（题面零删）" % label, not bad,
          "越界：" + " ⫶ ".join(x[:44] for x in bad[:3]) if bad else "")

    keys = re.findall(r"\\begin\{ansblock\}\[([^\]]+)\]", ans["main"])
    anchors = re.findall(r"% ans:(\S+)", ans["main"])
    items = re.findall(r"\\ansitem\{(\d+)\}", ans["main"])
    check("%s：ansblock 键数 == 键账 %d" % (label, nkeys), len(keys) == nkeys,
          "%s…%s" % (keys[0], keys[-1]))
    check("%s：每键配一条 %% ans: 件内锚且同序" % label, keys == anchors, "%d 锚" % len(anchors))
    check("%s：\\ansitem 题号集 == \\ti 题号集" % label,
          sorted(set(items), key=int) == sorted(set(a_src), key=int))
    check("%s：两档键数相同（印本档＝纯题档）" % label,
          len(re.findall(r"\\begin\{ansblock\}\[", ans["main"])) ==
          len(re.findall(r"\\begin\{ansblock\}\[", ans["main-pure"])))
    check("%s：对照件零迁移（只换装不回嵌）" % label, "\\begin{ansblock}" not in ans["main-ctl"])
    check("%s：速查表已包 \\ifshowans（纯题档不得漏答案表）" % label,
          "\\ifshowans\\dabiao\\fi" in ans["main"] and "\\ifshowans\\dabiao\\fi" in ans["main-pure"])

print("\n=== 汇总 ===")
print("通过 %d 项，未过 %d 项" % (PASS[0], len(FAIL)))
for f in FAIL:
    print("  ✗", f)
sys.exit(1 if FAIL else 0)
