# -*- coding: utf-8 -*-
r"""M2 测评本（3 件：测评卷／滚动卷A／滚动卷B）锚点迁移试迁脚本——换装轮副本树内作业。

依据：工作区/_tmp换装预备0913/换装方案草案.md §1（锚点迁移法＋三件型插入规则表「测评/滚动」行）
      ＋义务总表.md §一.3（测评本 3 件 51 键；题后 ansblock；三栏一律括线模；卷面分值/覆盖断言不动）。
红线：M2 成卷正件只读——本脚本仅 open('r') 读原件；一切写入限 副本树-测评本/；零 git。
断言：①键账 19/16/16＝51（等于义务总表）；②件面 \ti 题号集＝键号集（无悬空键）；
      ③值串与答案册 body.tex \ansitem 逐字恒等，并与 答案册/值快照.json 三方恒等（钉值零漂移）；
      ④锚点未命中/多命中即停；⑤拆不出即整串迁入并登记「共键」（禁猜）——丁区一键一 \ansitem，
        本轮预期 0 拆分组 0 共键，若实测非 0 即停待裁。
"""
import io
import os
import re
import sys
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
CJ = r"C:/提示词/工作区/M2-第1章量产0911/成卷"          # 只读源树
ANSBODY = CJ + "/答案册/body.tex"                        # 只读迁移源
SNAP = CJ + "/答案册/值快照.json"                        # 只读值快照（钉值基线）

SIX = ["qp-fonts.tex", "qp-layout.tex", "qp-parts.tex",
       "qp-headfoot.tex", "qp-titles.tex", "qp-blocks.tex"]

# 件登记表：目录名 → (源相对路径, 键前缀, 应迁键数)
ITEMS = [
    ("测评卷", "测评卷/main.tex", "测-", 19),
    ("滚动卷A", "滚动卷/滚A/main.tex", "滚A-", 16),
    ("滚动卷B", "滚动卷/滚B/main.tex", "滚B-", 16),
]


def read(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return f.read()


def write(p, s):
    d = os.path.dirname(p)
    if d:
        os.makedirs(d, exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


# ---------- 1. 键内容提取（答案册丁区：一键一 ansitem ＋ 可选 ansline 解析） ----------
body = read(ANSBODY)
lines = body.split("\n")
i0 = next(i for i, l in enumerate(lines) if "【丁】" in l)          # 丁＝测评卷＋滚动卷A/B 分区
cur, recs = None, []
for ln in lines[i0:]:
    s = ln.strip()
    m = re.match(r"^% pair:(\S+)$", s)
    if m:
        cur = {"key": m.group(1), "item": None, "note": None}
        recs.append(cur)
        continue
    if cur is None:
        continue
    m = re.match(r"^\\ansitem\{(\d+)\}\{(.*)\}$", s)
    if m and cur["item"] is None:
        cur["item"] = (m.group(1), m.group(2))
        continue
    m = re.match(r"^\\ansline\{(.+?)\}\{(.*)\}$", s)
    if m:
        assert cur["note"] is None, "解析行多于一条：%s（禁猜即停）" % cur["key"]
        cur["note"] = (m.group(1), m.group(2))

KMAP = {r["key"]: r for r in recs}
assert len(KMAP) == 51, "丁区键数 %d ≠ 51" % len(KMAP)

# 值三方恒等（body ↔ 值快照）
snap = json.load(io.open(SNAP, encoding="utf-8"))
snap_d = {k: v for k, v in snap.items() if k.startswith(("测-", "滚A-", "滚B-"))}
assert set(snap_d) == set(KMAP), "值快照丁区键集与 body 不等"
bad = [k for k in KMAP if snap_d[k] != (KMAP[k]["item"] or (None, ""))[1]]
assert not bad, "值快照 vs body 不等键：%s" % bad

# ---------- 2. 逐件迁移 ----------
def block_of(key, num, value, note):
    """ansblock 插入体（括线模由件导言 \ansblockgrayfalse 全局给定）。"""
    out = "\\begin{ansblock}[%s]\n%% ans:%s\n\\ansitem{%s}{%s}" % (key, key, num, value)
    if note:
        out += "\n\\ansnote{%s}{%s}" % (note[0], note[1])
    out += "\n\\end{ansblock}"
    return out


TOTAL, LOG = 0, []
UNCERTAIN = []

for dirname, relpath, prefix, want in ITEMS:
    src = read(os.path.join(CJ, relpath))
    outdir = os.path.join(HERE, dirname)
    write(os.path.join(outdir, "main.src.tex"), src)        # 原样对照件（不编译）

    tex = src
    # 2.1 qp-m3 换装：六宏 \input → \usepackage{qp-m3}
    sixblock = "\n".join("\\input{%s}" % f for f in SIX)
    assert tex.count(sixblock) == 1, "%s 六宏 \input 块未整块命中" % dirname
    tex = tex.replace(sixblock,
                      "\\usepackage{qp-m3}\n"
                      "\\ansblockgrayfalse   % 换装（测评/滚动＝8 开三栏件）：答案块一律括线模（方案草案§1.2.5/§5.1）\n"
                      "\\providecommand{\\ov}[1]{\\overrightarrow{#1}}   % 答案册 body 局部宏随值串迁入（丁区 10 键值含 \\ov）",
                      1)

    # 2.2 \jpcol 钉栏宽：qp-m3 括线/灰底以 \linewidth 取宽，\vtop 器内 \linewidth 仍是整页 \textwidth→必炸
    old_jpcol = ("\\newcommand{\\jpcol}[1]{\\raisebox{0pt}[0pt][0pt]{\\vtop{\\hsize\\jpcolw\\parskip0pt\\parindent0pt\n"
                 "  \\fontsize{10.5pt}{17.7pt}\\selectfont\\relax#1}}}")
    new_jpcol = ("\\newcommand{\\jpcol}[1]{\\raisebox{0pt}[0pt][0pt]{\\vtop{\\hsize\\jpcolw\\parskip0pt\\parindent0pt\n"
                 "  \\setlength\\linewidth{\\jpcolw}\\setlength\\columnwidth{\\jpcolw}   % 换装补钉：qp-m3 括线盒按 \\linewidth 取宽\n"
                 "  \\fontsize{10.5pt}{17.7pt}\\selectfont\\relax#1}}}")
    assert tex.count(old_jpcol) == 1, "%s \\jpcol 定义未整块命中" % dirname
    tex = tex.replace(old_jpcol, new_jpcol, 1)

    # 2.3 卷末答案速查表随开关吞（纯题版不得漏答案）
    n_db = len(re.findall(r"^  \\dabiao$", tex, re.M))
    assert n_db == 1, "%s 件末 \\dabiao 命中 %d 处（须 1）" % (dirname, n_db)
    assert tex.count("\n  \\dabiao\n") == 1, "%s 件末 \\dabiao 行未命中" % dirname
    tex = tex.replace("\n  \\dabiao\n",
                      "\n  \\ifshowans\\dabiao\\fi   % 换装：速查表＝答案承载件，纯题档随开关吞（防漏答案）\n", 1)

    # 2.4 答案逐题回嵌：\\ti 块（含其后 \\optline/\\qpart 续行）块尾插 ansblock
    ls = tex.split("\n")
    ins = []                     # (行号, 插入体)
    ti_re = re.compile(r"^  \\ti\{(\d+)\}")
    cont_re = re.compile(r"^  \\(optline|qpart)\{")
    n = 0
    for i, l in enumerate(ls):
        m = ti_re.match(l)
        if not m:
            continue
        num = m.group(1)
        key = prefix + num
        if key not in KMAP:
            UNCERTAIN.append((dirname, "题 %s 无对应键（悬空题号）" % num))
            continue
        j = i
        while j + 1 < len(ls) and cont_re.match(ls[j + 1]):
            j += 1
        rec = KMAP[key]
        assert rec["item"], "键 %s 无 ansitem 值" % key
        ins.append((j, block_of(key, rec["item"][0], rec["item"][1], rec["note"]), rec))
        n += 1
    assert n == want, "%s 插入 %d ≠ 应迁 %d" % (dirname, n, want)
    for j, blk, rec in reversed(ins):
        pad = "  " if ls[j].startswith("  ") else ""
        ls.insert(j + 1, pad + blk.replace("\n", "\n" + pad))
    tex = "\n".join(ls)

    # 断言：ansblock 配平＋键账
    assert tex.count("\\begin{ansblock}") == tex.count("\\end{ansblock}") == want
    keys_in = re.findall(r"^\\begin\{ansblock\}\[(\S+)\]$", tex, re.M) + \
              re.findall(r"^  \\begin\{ansblock\}\[(\S+)\]$", tex, re.M)
    keys_in = sorted(set(re.findall(r"\\begin\{ansblock\}\[(\S+)\]", tex)))
    wantkeys = sorted(prefix + str(i) for i in range(1, want + 1))
    assert keys_in == wantkeys, "%s 件内键集与键账不等：%s" % (dirname, set(keys_in) ^ set(wantkeys))

    # 双档产物件：main.tex＝印本档（默认含详解）；main-pure.tex＝纯题档（[pure]）
    write(os.path.join(outdir, "main.tex"), tex)
    write(os.path.join(outdir, "main-pure.tex"), tex.replace("\\usepackage{qp-m3}",
                                                            "\\usepackage[pure]{qp-m3}", 1))
    # 对照件（只换装不迁移）：隔离「换装本身」的版面漂移
    ctl = read(os.path.join(CJ, relpath))
    ctl = ctl.replace(sixblock, "\\usepackage{qp-m3}\n\\ansblockgrayfalse", 1)
    ctl = ctl.replace(old_jpcol, new_jpcol, 1)
    write(os.path.join(outdir, "main-ctl.tex"), ctl)

    TOTAL += n
    LOG.append((dirname, want, sum(1 for _, _, r in ins if r["note"]), n_db))

print("迁移键数合计:", TOTAL)
for d, w, notes, db in LOG:
    print("  %-8s 键 %2d（其中带解析 %d 条）｜速查表随开关吞 %d 处" % (d, w, notes, db))
print("拆分不确定点/共键（禁猜登记）:", UNCERTAIN if UNCERTAIN else "0")

with io.open(os.path.join(HERE, "_迁移日志-测评本.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write("# 测评本试迁迁移日志（机器生成）\n\n| 件 | 迁移键 | 带解析 | 速查表吞 |\n|---|---|---|---|\n")
    for d, w, notes, db in LOG:
        f.write("| %s | %d | %d | %d |\n" % (d, w, notes, db))
    f.write("\n合计键数：%d（义务总表 §一.3 靶 51）\n\n## 逐键明细\n\n| 键 | 锚 | 值（截 60）| 解析 |\n|---|---|---|---|\n")
    for d, w, notes, db in LOG:
        pass
    for k in sorted(KMAP, key=lambda x: (x.split("-")[0], int(x.split("-")[1]))):
        r = KMAP[k]
        f.write("| %s | 题后 ansblock | %s | %s |\n" % (
            k, r["item"][1].replace("|", "\\|")[:60], ("有（%s）" % r["note"][0]) if r["note"] else "—"))
    f.write("\n拆分不确定点：%s\n" % (UNCERTAIN if UNCERTAIN else "无（丁区一键一 \\ansitem，0 拆分组 0 共键）"))
