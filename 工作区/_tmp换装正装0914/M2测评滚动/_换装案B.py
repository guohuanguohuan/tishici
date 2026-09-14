# -*- coding: utf-8 -*-
"""M2 测评＋滚动卷 3 件·案B 附卷制换装正装（波3，2026-09-14）。

依据：
  - 军师账审-收口轮0913 §九 终裁：零高固定栏承件族例外＝案B 附卷制（答案块迁卷末附卷）；
    卷末速查表纯题档 \\ifshowans 隐去；纯题档 \\anskey 补偿发射保两档键账恒等。
  - 副本树-测评本/试迁报告-测评本.md：案A 值迁移 51/51 全绿＋覆盖断言 132 项过（块体值可信源）。
  - 副本树-P1测评/测评卷/main-换装B.tex：案B 形制原型（\\ifshowans 附卷整页＋\\anskey 双锚补丁）。

产出（写入仅限 _tmp换装正装0914/M2测评滚动/）：
  <件>/main.src.tex   源面快照（diff 基线）
  <件>/main.tex       案B 印本档
  <件>/main-pure.tex  案B 纯题档（[pure] 包选项）
  <件>/qp-m3.sty      钉后版本地挂载（md5 钉档断言）
  <件>/_迁移日志.md   逐键行＋断言读数

红线：M2 成卷正件只读；零 git；源件解析全部只读打开。
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\提示词")
SRCB = ROOT / "工作区" / "M2-第1章量产0911" / "成卷"
TRIALB = ROOT / "工作区" / "_tmp换装预备0913" / "副本树-测评本"
OUTB = ROOT / "工作区" / "_tmp换装正装0914" / "M2测评滚动"
STY_SRC = ROOT / "工作区" / "_tmp换装正装0914" / "M2练习本" / "课时01" / "qp-m3.sty"
STY_MD5 = "7c3930362be8a0a2bdf21bbf8ac16573"
BODY = SRCB / "答案册" / "body.tex"
SNAP = SRCB / "答案册" / "值快照.json"

# 附卷三栏块分布（初版；编译后按 [D] 栏底读数允许重排）
PIECES = [
    dict(dir="测评卷", src=SRCB / "测评卷" / "main.tex", trial=TRIALB / "测评卷" / "main.tex",
         prefix="测", n=19, juan="单元素养测评卷（一）",
         cols=[8, 6, 5]),   # 栏1=测-1..8 栏2=测-9..14 栏3=测-15..19（5 解析）
    dict(dir="滚动卷A", src=SRCB / "滚动卷" / "滚A" / "main.tex", trial=TRIALB / "滚动卷A" / "main.tex",
         prefix="滚A", n=16, juan="滚动测评卷（A）",
         cols=[6, 6, 4]),   # 栏3=滚A-13..16（4 解析）
    dict(dir="滚动卷B", src=SRCB / "滚动卷" / "滚B" / "main.tex", trial=TRIALB / "滚动卷B" / "main.tex",
         prefix="滚B", n=16, juan="滚动测评卷（B）",
         cols=[6, 6, 4]),
]

PRE6 = ("\\input{qp-fonts.tex}\n\\input{qp-layout.tex}\n\\input{qp-parts.tex}\n"
        "\\input{qp-headfoot.tex}\n\\input{qp-titles.tex}\n\\input{qp-blocks.tex}\n")
PRE3 = ("\\usepackage{qp-m3}\n"
        "\\ansblockgrayfalse   % 换装（测评/滚动＝8 开三栏件）：答案块一律括线模（方案草案§1.2.5/§5.1）\n"
        "\\providecommand{\\ov}[1]{\\overrightarrow{#1}}   % 答案册 body 局部宏随值串迁入（丁区 10 键值含 \\ov）\n")

PATCH0 = ("\\vtop{\\hsize\\jpcolw\\parskip0pt\\parindent0pt\n"
          "  \\fontsize{10.5pt}{17.7pt}\\selectfont\\relax#1}}}")
PATCH1 = ("\\vtop{\\hsize\\jpcolw\\parskip0pt\\parindent0pt\n"
          "  \\setlength\\linewidth{\\jpcolw}\\setlength\\columnwidth{\\jpcolw}   % 换装补钉：qp-m3 括线盒按 \\linewidth 取宽\n"
          "  \\fontsize{10.5pt}{17.7pt}\\selectfont\\relax#1}}}")


def match_brace(s, i):
    """s[i]=='{'，返回 (花括号内容, 闭括号后索引)；跳过 \\'\\' 转义。"""
    assert s[i] == "{"
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("花括号不配平")


def parse_ansitem_args(s, tag):
    """'\\\\ansitem{N}{VAL}' → (N, VAL)。"""
    m = re.match(r"\\ansitem\{", s)
    if not m:
        raise ValueError(f"{tag}: 非 \\ansitem 形")
    n, k = match_brace(s, m.end() - 1)
    val, _ = match_brace(s, k)
    return n.strip(), val


def parse_macro_arg(s, macro):
    """'\\\\ansnote{解析}{…}'／'\\\\ansline{解析}{…}' → (标签, 体)。"""
    m = re.match(r"\\" + macro + r"\{", s)
    if not m:
        raise ValueError(f"非 \\{macro} 形")
    label, k = match_brace(s, m.end() - 1)
    body, _ = match_brace(s, k)
    return label.strip(), body


RE_BLOCK = re.compile(
    r"^  \\begin\{ansblock\}\[(?P<key>[^\]]+)\]\n(?P<body>.*?)^  \\end\{ansblock\}\n",
    re.S | re.M)


def extract_trial_blocks(trial_tex, prefix, n):
    """案A 试迁件 → {键: 块体(含 % ans: 锚行)}，键序断言 1..n。"""
    blocks = {}
    order = []
    for m in RE_BLOCK.finditer(trial_tex):
        key = m.group("key")
        if not key.startswith(prefix + "-"):
            continue
        blocks[key] = m.group("body")
        order.append(key)
    want = [f"{prefix}-{i}" for i in range(1, n + 1)]
    assert order == want, f"{prefix}: 案A 键序异常 {order}"
    assert len(blocks) == n
    return blocks, want


def extract_body_pairs(body_tex):
    """答案册 body.tex：'% pair:键' 后随 \\ansitem{N}{值}（＋可选 \\ansline{解析}{…}）。"""
    pairs = {}
    lines = body_tex.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^% pair:(\S+)$", lines[i])
        if m:
            key = m.group(1)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if not lines[j].strip().startswith("\\ansitem{"):
                i = j
                continue  # 非条目形 pair（如预习填空 \\ansline 群答形）非丁区口径，跳过
            n, val = parse_ansitem_args(lines[j].strip(), f"body:{key}")
            note = None
            k = j + 1
            while k < len(lines) and k <= j + 3:
                t = lines[k].strip()
                if t.startswith("\\ansline{"):
                    lab, nb = parse_macro_arg(t, "ansline")
                    if lab == "解析":
                        note = nb
                    break
                if t.startswith("% pair:") or t.startswith("\\ansitem{"):
                    break
                k += 1
            pairs[key] = dict(num=n, val=val, note=note)
            i = j
        i += 1
    return pairs


def block_parts(key, body):
    """块体 → (num, 值串, 解析串|None)；断言块内锚＝键、号＝键号。"""
    m = re.search(r"^  % ans:(\S+)$", body, re.M)
    assert m and m.group(1) == key, f"{key}: 块内源锚异常"
    lines = [ln.strip() for ln in body.strip().split("\n") if ln.strip()]
    item = [ln for ln in lines if ln.startswith("\\ansitem{")]
    assert len(item) == 1, f"{key}: \\ansitem 非 1 条"
    num, val = parse_ansitem_args(item[0], key)
    note = None
    for ln in lines:
        if ln.startswith("\\ansnote{"):
            lab, nb = parse_macro_arg(ln, "ansnote")
            assert lab == "解析", f"{key}: 标签={lab}"
            note = nb
    want_num = key.rsplit("-", 1)[1]
    assert num == want_num, f"{key}: \\ansitem 号 {num}≠键号"
    return num, val, note


def build_appendix(pc, blocks, keys, col_plan):
    """案B 附卷：\\ifshowans 整页包（P1 原型形制），三栏 \\jpthree 手排，块体自案A 逐字迁入。"""
    lines = ["% ===================== 卷末附卷：参考答案（案B 附卷制：仅含详解档成页；纯题档整页跳过） =====================",
             "\\ifshowans", "\\newpage", "\\jpthree{\\jplead",
             "  \\par\\vskip 2.0mm\\noindent{\\fontsize{\\qpJTfSize}{17.7pt}\\selectfont\\heitiao 参考答案}"
             "\\hspace{0.6em}{\\fontsize{\\qpJTeSize}{17.7pt}\\selectfont（" + pc["juan"] + "·含详解档）}\\par\\nopagebreak"]
    at = 0
    for ci, cnt in enumerate(col_plan):
        if ci:
            lines.append("}{\\jplead")
        for key in keys[at:at + cnt]:
            lines.append("  \\begin{ansblock}[%s]" % key)
            lines.append(blocks[key].rstrip("\n"))
            lines.append("  \\end{ansblock}")
        at += cnt
    assert at == len(keys), f"{pc['prefix']}: 附卷栏排数 {at}≠{len(keys)}"
    lines.append("}")
    lines.append("\\fi")
    return "\n".join(lines) + "\n"


def compensation_line(pc, keys):
    anchor = "\\anskey{" + "}\\anskey{".join(keys) + "}"
    return ("  \\ifshowans\\else % 案B双锚补丁：附卷页整页跳过，纯题档在此补偿发射 " + str(len(keys))
            + " 键（两档 M3-ANSKEY 恒等，对号门两档可跑）\n  " + anchor + "\n  \\fi\n")


def transform(pc, blocks, keys, col_plan):
    """源面 → 案B 印本档文本（四处白名单改写，逐处断言恰 1 次命中）。"""
    src = pc["src"].read_text(encoding="utf-8")
    t = src
    # A｜六宏 → qp-m3 钉后版三行
    assert t.count(PRE6) == 1, f"{pc['prefix']}: 六宏 \\input 块未恰 1 命中"
    t = t.replace(PRE6, PRE3)
    # B｜\\jpcol 补 \\linewidth（三栏括线盒取宽，试迁 §五 反例必需）
    assert t.count(PATCH0) == 1, f"{pc['prefix']}: \\jpcol 补钉落点未恰 1 命中"
    t = t.replace(PATCH0, PATCH1)
    # C｜速查表 \\ifshowans 包裹＋纯题档 \\anskey 补偿发射（案B 双锚补丁，P1 原型形制）
    old_c = "  \\dabiao\n"
    assert t.count(old_c) == 1, f"{pc['prefix']}: \\dabiao 调用行未恰 1 命中"
    comp = compensation_line(pc, keys)
    new_c = ("  \\ifshowans\\dabiao\\fi   % 换装案B：速查表＝答案承载件，纯题档随开关吞（防漏答案）\n" + comp)
    t = t.replace(old_c, new_c)
    # D｜卷末附卷（\\end{document} 前）
    assert t.count("\\end{document}") == 1
    appendix = build_appendix(pc, blocks, keys, col_plan)
    t = t.replace("\\end{document}", appendix + "\n\\end{document}")
    # 回程断言：四处白名单回退后须与源面逐字节相等（题面零改动证明）
    r = t.replace(PRE3, PRE6).replace(PATCH1, PATCH0).replace(new_c, old_c)
    marker = "% ===================== 卷末附卷：参考答案（案B 附卷制：仅含详解档成页；纯题档整页跳过） =====================\n"
    assert t.count(marker) == 1
    head, tail = r.split(marker, 1)
    assert src.endswith("\\end{document}\n"), f"{pc['prefix']}: 源面尾形异常"
    assert tail == appendix[len(marker):] + "\n\\end{document}\n", f"{pc['prefix']}: 附卷回程段与正装段不一致"
    r = head + "\\end{document}\n"
    assert r == src, f"{pc['prefix']}: 回程断言失败——改写越出白名单"
    # 纯题档：[pure] 包选项
    assert t.count("\\usepackage{qp-m3}\n") == 1
    pure = t.replace("\\usepackage{qp-m3}\n", "\\usepackage[pure]{qp-m3}\n")
    return t, pure, appendix


def fenzhi_account(tex, prefix):
    """\\fenzhi 多重集与分值账（选择题组按每题分×题数计）。"""
    vals = [int(x) for x in re.findall(r"\\fenzhi\{(\d+)\}", tex)]
    return vals


def main():
    log_lines = []
    snap = json.loads(SNAP.read_text(encoding="utf-8"))
    body = BODY.read_text(encoding="utf-8")
    pairs = extract_body_pairs(body)
    md5 = hashlib.md5(STY_SRC.read_bytes()).hexdigest()
    assert md5 == STY_MD5, f"qp-m3.sty 钉后版 md5 不符：{md5}"
    print(f"[sty] 钉后版 md5 {md5} ✓")
    body_keys = {k for k in pairs}
    snap_keys = {k for k in snap}
    for pc in PIECES:
        pre = pc["prefix"]
        print(f"==== {pc['dir']}（{pre}-1..{pre}-{pc['n']}）====")
        trial_tex = pc["trial"].read_text(encoding="utf-8")
        blocks, keys = extract_trial_blocks(trial_tex, pre, pc["n"])
        # 逐键三方值断言：案A 块体 ↔ 答案册 pair ↔ 值快照（解析含 \\ansline→\\ansnote 形换对）
        rows = []
        for key in keys:
            num, val, note = block_parts(key, blocks[key])
            bp = pairs[key]
            assert bp["num"] == num and bp["val"] == val, f"{key}: 值≠答案册"
            assert snap[key] == val, f"{key}: 值≠值快照"
            if note is None:
                assert bp["note"] is None, f"{key}: 答案册有解析而块无"
            else:
                assert bp["note"] == note, f"{key}: 解析≠答案册"
            rows.append((key, num, val, note))
        print(f"  值断言 {len(rows)}/{len(rows)} 全等（案A块↔册pair↔快照，解析 {sum(1 for r in rows if r[3])} 条）")
        tex, pure, appendix = transform(pc, blocks, keys, pc["cols"])
        outdir = OUTB / pc["dir"]
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "main.src.tex").write_text(pc["src"].read_text(encoding="utf-8"), encoding="utf-8")
        (outdir / "main.tex").write_text(tex, encoding="utf-8")
        (outdir / "main-pure.tex").write_text(pure, encoding="utf-8")
        (outdir / "qp-m3.sty").write_bytes(STY_SRC.read_bytes())
        # 回程断言已证题面零改动 ⇒ \\ti 序列/题干/\\zuhang/\\jpthree 排布与卷头制式全部承源
        fz = fenzhi_account(tex, pre)
        fzs = fenzhi_account(pc["src"].read_text(encoding="utf-8"), pre)
        assert fz == fzs, f"{pre}: \\fenzhi 多重集漂移"
        j3_src = pc["src"].read_text(encoding="utf-8").count("\\jpthree{")
        j3_new = tex.count("\\jpthree{")
        assert j3_new == j3_src + 1, f"{pre}: \\jpthree 数 {j3_src}→{j3_new}（预期 +1 附卷页）"
        ins = len(tex.split("\n")) - len(pc["src"].read_text(encoding="utf-8").split("\n"))
        print(f"  批插：{len(keys)} 块迁附卷（栏排 {pc['cols']}）；\\fenzhi {fz}；\\jpthree {j3_src}+1；净增 {ins} 行")
        # 迁移日志
        L = [f"# _迁移日志-{pc['dir']}（案B 附卷制，2026-09-14 波3）", "",
             f"- 源面：`{pc['src'].relative_to(ROOT)}`（只读）→ `main.src.tex` 快照",
             "- 改写四处白名单：①六宏→qp-m3 钉后版（括线模＋\\ov）；②\\jpcol 补 \\linewidth；"
             "③速查表 \\ifshowans 包＋纯题档 \\anskey 补偿发射；④卷末附卷（\\ifshowans 整页包，三栏手排 "
             f"{pc['cols']}）。回程断言＝四处回退后与源面逐字节相等 ✓（题面零改动）。",
             f"- 键账：{len(keys)} 键（`{pre}-1..{pre}-{pc['n']}`）三方值全等：案A试迁块体↔答案册 pair↔值快照；"
             f"解析 {sum(1 for r in rows if r[3])} 条随迁（\\ansnote{{解析}}）。", "",
             "| 键 | 号 | 值 | 解析 |", "|---|---|---|---|"]
        for key, num, val, note in rows:
            vs = val.replace("|", "\\|")
            ns = ("有" if note else "—")
            L.append(f"| {key} | {num} | {vs} | {ns} |")
        (outdir / "_迁移日志.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        log_lines.append((pc, rows, fz, ins))
    total = sum(len(r) for _, r, _, _ in log_lines)
    print(f"[合计] 3 件 {total} 键（期望 51）——{'✓' if total == 51 else '✗'}")


if __name__ == "__main__":
    main()
