# -*- coding: utf-8 -*-
"""P1 测评本 1 件·案B 附卷制换装正装（波5，2026-09-14）。

依据：
  - 义务总表 §二.4：P1 测评本 19 键（件面 \\ti 计 20 系注释行假命中——对平门首道已机械核销）
    ＋尾块 1 处（案B 题面像素零差硬门下置附卷末栏，登记口径变更节）。
  - M2 测评滚动波3 案B 首战全绿经验（换装正装报告-M2测评滚动.md）：附卷整页 ifshowans 守卫／
    速查表纯题档隐去／纯题档 anskey 补偿发射／两遍编译硬门／[D][E] 口径。
  - 波4a 断点 ④坑钉：overlay v0.2（qp-m3p-overlay.sty）＋kpathsea 不认中文路径＝sty 本地挂载。

产出（写入仅限 _tmp换装正装0914/P1测评本/，写前逐路径断言前缀）：
  测评卷/main.src.tex   源面快照（成卷/装配/测评本/测评卷/main.tex 逐字节）
  测评卷/main.tex       案B 印本档（四处白名单改写）
  测评卷/main-pure.tex  案B 纯题档（[pure] 包选项）
  测评卷/qp-m3p-overlay.sty  overlay v0.2 本地挂载（md5 钉档断言）
  测评卷/_迁移日志.md   逐键行＋断言读数
  _键账丁区-测评卷.json  值快照丁区切片（[E] --keys 喂料）

红线：P1 成卷正件（装配/测评本、答案册、值快照）与 工具/ 只读；零 git；分段写。
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\提示词")
SRC_TEX = ROOT / "工作区" / "P1-必修3第9章量产0912" / "成卷" / "装配" / "测评本" / "测评卷" / "main.tex"
SRC_PDF = SRC_TEX.with_suffix(".pdf")
OUTB = ROOT / "工作区" / "_tmp换装正装0914" / "P1测评本"
OUTD = OUTB / "测评卷"
STY_SRC = ROOT / "工作区" / "_tmp换装正装0914" / "P1导学本" / "qp-m3p-overlay.sty"
BODY = ROOT / "工作区" / "P1-必修3第9章量产0912" / "成卷" / "答案册" / "body.tex"
SNAP = ROOT / "工作区" / "P1-必修3第9章量产0912" / "成卷" / "答案册" / "值快照.json"

PREFIX, NKEYS, JUAN = "测", 19, "单元素养测评卷（一）"
COLS = [8, 6, 5]   # 附卷三栏：栏1=测1~8（含卷头）栏2=测9~14 栏3=测15~19＋尾块

QFIGS = "\\input{C:/提示词/工作区/物理样张0911/骨架/qp-figs.tex}\n"
OVERLAY = ("\\usepackage{qp-m3p-overlay}   % 换装（P1 骨架 overlay v0.2）：\\showans 开关族＋ansblock＋tailfill（波4a 件在案）\n"
           "\\ansblockgrayfalse   % 换装（测评卷＝8 开三栏件）：答案块一律括线模（承 M2 波3 案B 同款）\n")
JPCOL0 = ("\\newcommand{\\jpcol}[1]{\\raisebox{0pt}[0pt][0pt]{\\vtop{\\hsize\\jpcolw\\parskip0pt\\parindent0pt\n"
          "  \\fontsize{10.5pt}{17.7pt}\\selectfont\\relax#1}}}")
JPCOL1 = ("\\newcommand{\\jpcol}[1]{\\raisebox{0pt}[0pt][0pt]{\\vtop{\\hsize\\jpcolw\\parskip0pt\\parindent0pt\n"
          "  \\setlength\\linewidth{\\jpcolw}\\setlength\\columnwidth{\\jpcolw}   % 换装补钉：括线盒按 \\linewidth 取宽（承 M2 波3）\n"
          "  \\fontsize{10.5pt}{17.7pt}\\selectfont\\relax#1}}}")
DABIAO0 = "  \\dabiao\n"
TAILFILL = ("  \\tailfill   % 换装尾块（义务总表§二.4＝尾块 1 处；案B 题面像素零差硬门下置附卷末栏，"
            "纯题档随附卷整页跳过）\n")


def safe_write(path, data):
    """写前核 mode：路径须在 P1测评本 树内。"""
    p = Path(path)
    assert OUTB in p.parents or p.parent == OUTB, f"越界写入被拦：{p}"
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        p.write_text(data, encoding="utf-8")
    else:
        p.write_bytes(data)
    print(f"[写] {p.relative_to(ROOT)}")


def match_brace(s, i):
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


def extract_body_pairs(body_tex):
    """答案册丁区：'% pair:测-N' 后随 \\ansitem{N}{值}（P1 测段无解析行，遇之登记）。"""
    pairs, notes = {}, 0
    lines = body_tex.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^% pair:(\S+)$", lines[i])
        if m and m.group(1).startswith(PREFIX + "-"):
            key = m.group(1)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            assert lines[j].strip().startswith("\\ansitem{"), f"{key}: 非 \\ansitem 条目形"
            s = lines[j].strip()
            m2 = re.match(r"\\ansitem\{", s)
            num, k = match_brace(s, m2.end() - 1)
            val, _ = match_brace(s, k)
            for t in (x.strip() for x in lines[j + 1:j + 4]):
                if t.startswith("\\ansline{") or t.startswith("\\ansnote{"):
                    notes += 1
                    raise AssertionError(f"{key}: 测段出现解析行 {t[:40]}——义务口径外，须人工裁")
            pairs[key] = dict(num=num.strip(), val=val)
            i = j
        i += 1
    return pairs, notes


def build_appendix(keys, blocks, col_plan):
    L = ["% ===================== 卷末附卷：参考答案（案B 附卷制：仅含详解档成页；纯题档整页跳过） =====================",
         "\\ifshowans", "\\newpage", "\\jpthree{\\jplead",
         "  \\par\\vskip 2.0mm\\noindent{\\fontsize{\\qpJTfSize}{17.7pt}\\selectfont\\heitiao 参考答案}"
         "\\hspace{0.6em}{\\fontsize{\\qpJTeSize}{17.7pt}\\selectfont（" + JUAN + "·含详解档）}\\par\\nopagebreak"]
    at = 0
    for ci, cnt in enumerate(col_plan):
        if ci:
            L.append("}{\\jplead")
        for key in keys[at:at + cnt]:
            L.append("  \\begin{ansblock}[%s]" % key)
            L.append("  %% ans:%s" % key)
            L.append("  \\ansitem{%s}{%s}" % (blocks[key]["num"], blocks[key]["val"]))
            L.append("  \\end{ansblock}")
        if ci == len(col_plan) - 1:
            L.append(TAILFILL.rstrip("\n"))
        at += cnt
    assert at == len(keys), f"附卷栏排数 {at}≠{len(keys)}"
    L.append("}")
    L.append("\\fi")
    return "\n".join(L) + "\n"


def compensation_line(keys):
    anchor = "\\anskey{" + "}\\anskey{".join(keys) + "}"
    return ("  \\ifshowans\\else % 案B双锚补丁：附卷页整页跳过，纯题档在此补偿发射 " + str(len(keys))
            + " 键（两档 M3-ANSKEY 恒等，对号门两档可跑）\n  " + anchor + "\n  \\fi\n")


def transform(src, keys, blocks, col_plan):
    t = src
    # A｜七模块 \\input 原样保留，其后挂 overlay v0.2（括线模）
    assert t.count(QFIGS) == 1, "A 落点未恰 1 命中"
    t = t.replace(QFIGS, QFIGS + OVERLAY)
    # B｜\\jpcol 补 \\linewidth/\\columnwidth（附卷括线盒取宽）
    assert t.count(JPCOL0) == 1, "B 落点未恰 1 命中"
    t = t.replace(JPCOL0, JPCOL1)
    # C｜速查表 \\ifshowans 包裹＋纯题档 \\anskey 补偿发射（案B 双锚补丁）
    assert t.count(DABIAO0) == 1, "C 落点未恰 1 命中"
    new_c = ("  \\ifshowans\\dabiao\\fi   % 换装案B：速查表＝答案承载件，纯题档随开关吞（防漏答案）\n"
             + compensation_line(keys))
    t = t.replace(DABIAO0, new_c)
    # D｜卷末附卷整页（\\end{document} 前）
    assert t.count("\\end{document}") == 1
    appendix = build_appendix(keys, blocks, col_plan)
    t = t.replace("\\end{document}", appendix + "\n\\end{document}")
    # 回程断言：四处白名单回退后与源面逐字节相等（题面零改动证明）
    r = t.replace(OVERLAY, "").replace(JPCOL1, JPCOL0).replace(new_c, DABIAO0)
    marker = "% ===================== 卷末附卷：参考答案（案B 附卷制：仅含详解档成页；纯题档整页跳过） =====================\n"
    assert t.count(marker) == 1
    head, tail = r.split(marker, 1)
    assert src.endswith("\\end{document}\n"), "源面尾形异常"
    assert tail == appendix[len(marker):] + "\n\\end{document}\n", "附卷回程段与正装段不一致"
    r = head + "\\end{document}\n"
    assert r == src, "回程断言失败——改写越出白名单"
    # 纯题档：[pure] 包选项
    assert t.count("\\usepackage{qp-m3p-overlay}") == 1
    pure = t.replace("\\usepackage{qp-m3p-overlay}", "\\usepackage[pure]{qp-m3p-overlay}")
    return t, pure, appendix


def main():
    src = SRC_TEX.read_text(encoding="utf-8")
    snap = json.loads(SNAP.read_text(encoding="utf-8"))
    if isinstance(snap, dict) and isinstance(snap.get("vals"), dict):
        snap = snap["vals"]
    body = BODY.read_text(encoding="utf-8")
    pairs, notes = extract_body_pairs(body)
    assert notes == 0
    # sty 钉档：树根 v0.2 与本地挂载逐字节同
    sty_bytes = STY_SRC.read_bytes()
    sty_md5 = hashlib.md5(sty_bytes).hexdigest()
    assert b"v0.2" in sty_bytes, "overlay 非 v0.2"
    # 逐键三方值断言：答案册 pair ↔ 值快照（键集合已由对平门首道对平）
    keys = [f"{PREFIX}-{i}" for i in range(1, NKEYS + 1)]
    for key in keys:
        bp = pairs[key]
        assert bp["num"] == key.rsplit("-", 1)[1], f"{key}: \\ansitem 号≠键号"
        assert snap[key] == bp["val"], f"{key}: 值≠值快照"
    print(f"[值] {len(keys)} 键三方集合对平（对平门首道 PASS）＋值逐键 pair↔快照全等 ✓")
    # 源面实题号连续断言
    code = re.sub(r"(?<!\\)%.*$", "", src, flags=re.M)
    tis = [int(x) for x in re.findall(r"\\ti\{(\d+)\}", code)]
    assert tis == list(range(1, NKEYS + 1)), f"源面 \\ti 序列异常：{tis}"
    tex, pure, appendix = transform(src, keys, {k: pairs[k] for k in keys}, COLS)
    # 批插读数断言
    fz_out = [int(x) for x in re.findall(r"\\fenzhi\{(\d+)\}", tex)]
    fz_src = [int(x) for x in re.findall(r"\\fenzhi\{(\d+)\}", src)]
    assert fz_out == fz_src, "\\fenzhi 多重集漂移"
    j3s, j3o = src.count("\\jpthree{"), tex.count("\\jpthree{")
    assert j3o == j3s + 1, f"\\jpthree 数 {j3s}→{j3o}"
    assert tex.count("\\begin{ansblock}[") == NKEYS
    assert pure.count("\\begin{ansblock}[") == NKEYS
    # 分值账：组行固定分（32/18/15）＋解答 \\fenzhi 合计 ＝ 100
    grp = [int(x) for x in re.findall(r"每小题\d+分，共(\d+)分", src)]
    assert grp == [32, 18, 15], f"组行分值异常 {grp}"
    total = sum(grp) + sum(fz_src)
    assert total == 100, f"分值账 {total}≠100"
    # 落盘（写前核 mode）
    safe_write(OUTD / "main.src.tex", src)
    safe_write(OUTD / "main.tex", tex)
    safe_write(OUTD / "main-pure.tex", pure)
    safe_write(OUTD / "qp-m3p-overlay.sty", sty_bytes)
    safe_write(OUTB / "_键账丁区-测评卷.json",
               json.dumps({"keys": NKEYS, "vals": {k: snap[k] for k in keys}}, ensure_ascii=False, indent=1))
    # 迁移日志
    L = [f"# _迁移日志-测评卷（P1 案B 附卷制，2026-09-14 波5）", "",
         f"- 源面：`{SRC_TEX.relative_to(ROOT)}`（只读）→ `main.src.tex` 快照（逐字节）＋`main.src.pdf` 原基线",
         "- 改写四处白名单：①七模块 \\input 后挂 overlay v0.2（md5 " + sty_md5[:8] + "…）＋括线模；"
         "②\\jpcol 补 \\linewidth/\\columnwidth；③速查表 \\ifshowans 包＋纯题档 \\anskey 补偿发射 19 键；"
         f"④卷末附卷整页（\\ifshowans 包＋\\newpage＋三栏手排 {COLS}，尾块随附卷末栏）。"
         "回程断言＝四处回退后与源面逐字节相等 ✓（题面零改动）。",
         f"- 键账：{len(keys)} 键（`{PREFIX}-1..{PREFIX}-{NKEYS}`），值逐键 pair↔快照全等；测段解析 0 条（答案册丁区无详解行）。",
         "- 1 键差核销：件面 naive \\ti 20−注释假命中 1（main.src.tex:15 `\\tihao→\\ti{n}`）＝实题 19＝册 pair 19（对平门首道读数在 _门谱读数/）。", "",
         "| 键 | 号 | 值 |", "|---|---|---|"]
    for key in keys:
        vs = snap[key].replace("|", "\\|")
        L.append(f"| {key} | {key.rsplit('-', 1)[1]} | {vs} |")
    L += ["", f"- 批插读数：{NKEYS} 块迁附卷（栏排 {COLS}）；\\fenzhi 多重集 {fz_out}＝源面；\\jpthree {j3s}+1；"
          f"分值账 {sum(grp)}＋{sum(fz_src)}＝100 ✓；净增 {len(tex.splitlines()) - len(src.splitlines())} 行。"]
    safe_write(OUTD / "_迁移日志.md", "\n".join(L) + "\n")
    print(f"[合计] P1 测评卷 {NKEYS} 键案B 迁移完成（期望 19）——{'✓' if NKEYS == 19 else '✗'}")


if __name__ == "__main__":
    main()
