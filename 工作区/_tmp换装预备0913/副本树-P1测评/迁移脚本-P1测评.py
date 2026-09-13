# -*- coding: utf-8 -*-
r"""试迁脚本-P1测评（副本树-P1测评 内；写入仅限本目录）
P1 测评本 overlay 换装试迁（答案制A正文 → 四制件，qp-m3p-overlay 挂载）：
  ① 答案册 body.tex【丁】（只读迁移源）→ 测-1~测-19 键账提取（值逐字节原样，禁改写）
  ② 双方案生成：
     案A＝方案草案 §1.2 测评行字面口径——逐题 \ti 块尾后题 ansblock（括线模）；
     案B＝件面物理不可行时的替代锚——卷末答案附卷页（新页 \jpthree 三栏，ansblock 同制，
         纯题档 \ifshowans 跳过整页＋\anskey 补偿发射保持两档 M3-ANSKEY 恒等）；
  ③ 专项：件面题数 vs 键账「差 1 键」核对（题面 \ti{N} 计数须剔注释行）；
     覆盖断言（9.1~9.4 分布）＋分制式（90分钟/100分、组行分值、\fenzhi 合计）保留核验；
  ④ 断言：键数＝19、锚唯一、原件行零删改（纯插入 diff）、两案均含 19 个 % ans: 源层锚。
产物：测评卷/main-换装A.tex / main-换装B.tex ＋ 双壳×4 ＋ 试迁键账-eval.json
红线：零 git；P1 成卷正件/答案册/骨架只读；一切写入限本副本树。
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "测评卷")
SRC_MAIN = os.path.join(PIECE, "main.tex")           # 只读对照基线（正件同 md5 拷贝）
BODY = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex"  # 只读迁移源

def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()

# ---------- ① 键账提取（body.tex【丁】段 测-1~19） ----------
blines = rd(BODY).splitlines()
start = next(i for i, l in enumerate(blines) if "【丁】测评卷答案" in l)
vals, pending = {}, []
for ln in blines[start:]:
    s = ln.strip()
    m = re.match(r"^% pair:(测-\d+)$", s)
    if m:
        pending.append(m.group(1)); continue
    m = re.match(r"^\\ansitem\{(\d+)\}\{(.+)\}\s*$", s)
    if m and pending:
        k = pending.pop(0)
        assert k == "测-%s" % m.group(1), "键号与题号错位：%s vs %s" % (k, m.group(1))
        vals[k] = m.group(2)
    if s == r"\end{multicols}" and vals:
        break
assert not pending, "缺值悬空键：%s" % pending
EXPECT = ["测-%d" % n for n in range(1, 20)]
assert list(vals.keys()) == EXPECT, "键账不齐：%s" % sorted(set(EXPECT) ^ set(vals))

# ---------- ② 件面题面提取 ＋ 差 1 键专项核对 ----------
src = rd(SRC_MAIN)
slines = src.splitlines()
ti_real = {}          # 题号 → 行索引（0-based），仅正文行
ti_comment = []       # 注释行里的 \ti 命中（差1键案源）
cont_re = re.compile(r"^\s*(\\qpfig|\\optline|\\xiexwei)")   # 题块续行；\ti{N+1} 起新题即断
for i, ln in enumerate(slines):
    if ln.strip().startswith("%"):
        if re.search(r"\\ti\{", ln):
            ti_comment.append((i + 1, ln.strip()[:70]))
        continue
    m = re.search(r"\\ti\{(\d+)\}\{", ln)
    if not m:
        continue
    else:
        n = int(m.group(1))
        assert n not in ti_real, "题号重复：%d" % n
        ti_real[n] = i
qnums = sorted(ti_real)
assert qnums == list(range(1, 20)), "件面题序不连续：%s" % qnums

# 原始朴素计数（义务总表口径复现）：\ti{ 全部出现次数（含注释）
naive = sum(len(re.findall(r"\\ti\{", ln)) for ln in slines)
diff1 = {
    "naive_ti_hits_incl_comment": naive,
    "comment_hits": ti_comment,
    "real_ti_questions": len(qnums),
    "answer_book_keys": len(vals),
    "key_face_pairing": "卷面题号 1~19 ↔ 答案册键 测-1~测-19 一一对应，无缺键无浮键"
                        if len(qnums) == len(vals) == 19 else "不齐！",
}
print("[差1键核对] 朴素 \\ti{ 命中＝%d（其中注释行命中＝%s），真实题面 \ti 题数＝%d，答案册测-N 键数＝%d"
      % (naive, ti_comment, len(qnums), len(vals)))

# ---------- ③ 覆盖断言＋分制式保留基准（迁移后须逐字仍在＝纯插入可证） ----------
cov = re.search(r"章覆盖＝(.+?)。\n", src, re.S).group(1)
sec_map = {}
for m in re.finditer(r"(9\.\d)×\d+（([\d,，]+)）", cov.replace("\n%", "\n").replace("%", "")):
    for q in re.split(r"[,，]", m.group(2)):
        sec_map.setdefault(int(q), m.group(1))
assert sorted(sec_map) == list(range(1, 20)) and len(set(sec_map.values())) == 4, "覆盖断言注释本身不齐"
zhis = [int(x) for x in re.findall(r"每小题\d+分，共(\d+)分|共(\d+)分(?=\\ 解答|.\s*解答)", src) for x in x if x]
fen = {int(m.group(1)): int(m.group(2)) for m in re.finditer(r"\\ti\{(\d+)\}\{\\fenzhi\{(\d+)\}", src)}
fmt_lines = {   # 分制式关键行（原样保留断言用）
    "jptime": r"（时间：90分钟\quad 分值：100分）",
    "组一": r"一、选择题}{：本题共8小题，每小题4分，共32分",
    "组二": r"二、选择题}{：本题共3小题，每小题6分，共18分",
    "组三": r"三、填空题}{：本题共3小题，每小题5分，共15分",
    "组四": r"四、解答题}{：本题共5小题，共35分",
}
assert fmt_lines["jptime"] in src, "分制式基线行缺失"
assert 32 + 18 + 15 + sum(fen.values()) == 100 and len(fen) == 5, "分值算不拢 100：%s" % fen
print("[分制式] P1 测评卷承件型卷式＝90分钟/100 分（非 M2 数学 120 分钟/150 分档）；"
      "组行分值 32+18+15+35=100；解答 \fenzhi %s 合计 35 ✓" % fen)

# ---------- ④ 插入构造 ----------
def block(n, indent="  "):
    k = "测-%d" % n
    out = ["%s\\begin{ansblock}[%s]" % (indent, k),
           "%s%% ans:%s" % (indent, k)]
    if n >= 10:
        out.append("%s\\setlength{\\anshang}{7.6mm}%% 题10起双位档（照答案册 body.tex 同值，块内局部）" % indent)
    out.append("%s\\ansitem{%d}{%s}" % (indent, n, vals[k]))
    out.append("%s\\end{ansblock}" % indent)
    return out

def insertions_A():
    """案A：逐题块尾后题 ansblock。返回 {行索引(插入在该行后): [新行]}"""
    ins = {}
    for n, i in ti_real.items():
        cand = i
        j = i + 1
        while j < len(slines):
            s = slines[j].strip()
            if s == "" or s.startswith("%"):
                j += 1; continue
            if cont_re.match(slines[j]):
                cand = j; j += 1; continue
            break
        ins[cand] = block(n)
    return ins

OVERLAY_PREAMBLE = [
    "",
    "% —— 换装 overlay 挂接（副本树试迁；七模块后、\\begin{document} 前，承 sty 头用法）——",
    "\\usepackage{qp-m3p-overlay}",
    "\\ansblockgrayfalse % P1 测评卷＝8开横放三栏不可回流件型：ansblock 一律括线模（草案 §1.2 测评行＋§5.1；试迁实测另见报告）",
    "% \\jpcol 局部补丁（试迁实证·必打）：PL1 \\jpcol vtop 只设 \\hsize 未设 \\linewidth，",
    "%   overlay 括线模/尾块 \\rule{\\linewidth} 按外层 382mm 出栏＝Overfull \\hbox 745pt×40。",
    "%   本补丁＝原件 \\jpcol 同体＋\\linewidth\\jpcolw 钉栏宽（零删改，\\AtBeginDocument 后置覆盖，纯插入）。",
    "\\AtBeginDocument{\\renewcommand{\\jpcol}[1]{\\raisebox{0pt}[0pt][0pt]{\\vtop{\\hsize\\jpcolw\\linewidth\\jpcolw\\parskip0pt\\parindent0pt\\fontsize{10.5pt}{17.7pt}\\selectfont\\relax#1}}}}",
]

def build(mode):
    """mode='A' 逐题后嵌；mode='B' 卷末答案附卷。返回 (text, n_blocks)"""
    ins = insertions_A() if mode == "A" else {}
    lines_out = []
    for i, ln in enumerate(slines):
        lines_out.append(ln)
        if i == 29:   # qp-figs \input 行（0-based 第30行）
            lines_out.extend(OVERLAY_PREAMBLE)
        if i in ins:
            lines_out.extend(ins[i])
        if ln.strip() == "\\dabiao":   # 卷末速查表后：件尾块（两档恒印）
            lines_out.append("  \\tailfill")
            if mode == "B":
                lines_out.append("  \\ifshowans\\else % B案双锚补丁：附卷页被整页跳过，纯题档在此补偿发射 19 键（两档 M3-ANSKEY 恒等，对号门两档可跑）")
                lines_out.append("  " + "".join("\\anskey{测-%d}" % n for n in range(1, 20)))
                lines_out.append("  \\fi")
    if mode == "B":
        # 附卷页插在最后一个 \jpthree 收尾之后、\end{document} 前
        k = max(i for i, ln in enumerate(lines_out) if ln.strip() == "}")
        app = ["", "% ===================== 第 4 页＝卷末答案附卷（案B：仅含详解档成页；纯题档整页跳过） =====================",
               "\\ifshowans", "\\newpage"]
        groups = [(1, 7), (8, 13), (14, 19)]
        app.append("\\jpthree{\\jplead")
        for gi, (a, b) in enumerate(groups):
            if gi > 0:
                app.append("}{\\jplead")
            if gi == 0:
                app.append("  \\par\\vskip 2.0mm\\noindent{\\fontsize{\\qpJTfSize}{17.7pt}\\selectfont\\heitiao 参考答案}"
                           "\\hspace{0.6em}{\\fontsize{\\qpJTeSize}{17.7pt}\\selectfont（单元素养测评卷（一）·含详解档）}\\par\\nopagebreak")
            for n in range(a, b + 1):
                app.extend(block(n))
        app += ["}", "", "\\fi"]
        lines_out = lines_out[:k + 1] + app + lines_out[k + 1:]
    return "\n".join(lines_out) + "\n", len(vals)

def pure_insert_assert(text, mode):
    """原件行零删改＝原文是本文件严格子序列（行级）"""
    new = text.splitlines()
    it = iter(new)
    kept = 0
    for ln in slines:
        for x in it:
            if x == ln:
                kept += 1; break
        else:
            raise AssertionError("原件行被删改（%s案）：%r" % (mode, ln[:60]))
    assert kept == len(slines), "子序列比对异常"
    assert text.count("% ans:测-") == 19 and text.count("\\begin{ansblock}[测-") == (19 if mode == "A" else 19), \
        "锚点数≠19（%s案）：%d/%d" % (mode, text.count("% ans:测-"), text.count("\\begin{ansblock}"))

banner = ("% —— 副本树-P1测评 试迁件（由 main.tex 机器迁移生成；正件 main.tex 只读对照）——\n"
          "% —— 案＝{mode}｜A＝逐题块尾 ansblock（草案 §1.2 测评行字面口径）／B＝卷末答案附卷（件面物理约束替代）——\n")

out = {}
for mode in ("A", "B"):
    text, n = build(mode)
    pure_insert_assert(text, mode)
    path = os.path.join(PIECE, "main-换装%s.tex" % mode)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(banner.format(mode=mode) + text)
    for shell, pure in (("true", "0"), ("false", "1")):
        sp = os.path.join(PIECE, "main-换装%s-%s.tex" % (mode, shell))
        with open(sp, "w", encoding="utf-8", newline="") as f:
            f.write("%% 试迁双壳·%s案·%s档\n\\def\\mthreepure{%s}\n\\input{main-换装%s.tex}\n"
                    % (mode, "含详解印本" if pure == "0" else "纯题", pure, mode))
    out[mode] = n
    print("[生成] main-换装%s.tex（%d 键 ansblock＋双壳）——纯插入断言过（原件 %d 行零删改）" % (mode, n, len(slines)))

with open(os.path.join(HERE, "试迁键账-eval.json"), "w", encoding="utf-8") as f:
    json.dump({"keys": len(vals), "vals": vals, "diff1_check": diff1,
               "coverage_map": {str(k): v for k, v in sorted(sec_map.items())},
               "fenzhi": {str(k): v for k, v in fen.items()}}, f, ensure_ascii=False, indent=1)
print("[键账] 试迁键账-eval.json（19 键值快照，钉值/对勘用）")
