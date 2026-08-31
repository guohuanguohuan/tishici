# -*- coding: utf-8 -*-
r"""章知识结构图生成（工具债⑦；公共规则§7绘图模板库条款N14、§5创作层⑥N13思维导图豁免、
高中同步总控任务A「章知识结构图与图例行对账」；规格书§1「章知识结构图（N14）」）

功能
----
从知识清单 docx（条目题名行＝节点唯一权威源）或条目清单 txt 提取本章全部条目，
按教材节分组生成章知识结构图（TikZ 思维导图，走 工具/绘图模板库.py mindmap_tree 模板，
矢量渲染 xelatex→PDF→PNG≥300dpi，另留 PDF 供矢量再导出），落盘插入辅助与断言报告。

硬要求（内置断言，任一不过＝FAIL 退出码 2，不交付）
----------------------------------------------------
A1 条目编号 1..N 连续无重复（题名行序列）。
A2 节点＝条目名子集且 100% 整章覆盖：节点集合 == 条目名集合；节点数 ≤ 条目数；
    节点标签＝条目题名行去掉「N．〔基/进〕」前缀后的全文（编号与标记不进节点，
    保「节点名＝条目名子集」严格成立）。
A3 黑白可辨：三级节点色（根/一级/叶）相对亮度阶梯相邻差 ≥0.35（含叶=白底=背景）；
    每张 PNG 实测灰度对比度（绘图模板库 check_grayscale：墨迹最深处 vs 底色）≥0.35。
A4 渲染位图 dpi ≥300（实测像素尺寸按 1:1 建议显示折算，即 dpi 即像素密度）。
A5 节点字号 \small（9pt）：思维导图节点标签属内容本体、豁免图内禁字（N13）；
    按 1:1 自然尺寸插入＝图内文字视觉高≈9pt（N12 目标值，≥6.5pt 下限）。

分组布局（47/67 条大节点量的分页方案，规格书：自动分页/分层、不糊不叠字）
------------------------------------------------------------------------
按教材节分组子图：每个二级节（N.N）一张子图（根＝节标题，一级＝三级小节 N.N.N，
叶＝条目）；该组叶数 > max-leaves（默认 20）时改按三级小节逐节出图（根＝小节标题，
一级＝条目名）；二级节标题行缺失时用 --section-titles 补名（教材目录口径），无补则仅节号。

源图配色提取
------------
--source-img 传源素材思维导图位图时提取色板（饱和像素 HSL 色相 24 桶直方图取主色相，
饱和度×计数加权），节点色取源色相、按相对亮度阶梯定槽（根0.29/一级0.65/叶白1.00——
黑白打印三级可辨）；无源图用默认色板（青绿/蓝族）。

用法
----
python 工具/章知识结构图生成.py --docx 清单.docx --out-dir 输出目录 \
    [--source-img 源思维导图.png ...] [--dpi 300] [--max-leaves 20] \
    [--section-titles '{"2.2":"直线及其方程"}']

输出（全部落 --out-dir）
------------------------
  章知识结构图_第NN组_<节号>.png / .pdf（PDF＝矢量留存；PNG＝Word 嵌入用）
  sources/…（TikZ 源码，源码即图）
  插入辅助.tsv（逐图：根节点/节点数/建议显示宽高cm/插入位说明）
  结构图报告.json（A1—A5 断言数字：条目数/节点数/逐图叶数/灰度实测/色板/亮度差）
"""
from __future__ import annotations

import colorsys
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import 绘图模板库 as tpl  # noqa: E402  （只读引用；扩参版 mindmap_tree/render 由本轮T5增参）

# ----------------------------- 常量与正则 -----------------------------

ENTRY_RE = re.compile(r"^(\d+)．〔(基|进)〕(.+)$")
ENTRY_RE_NOMARK = re.compile(r"^(\d+)．(.+)$")           # txt 容错（无〔基/进〕）
SEC_RE = re.compile(r"^(\d+(?:\.\d+)+)\s*(.*)$")

# 相对亮度阶梯（0.2126R+0.7152G+0.0722B 加权；目标相邻差≥0.35）
LUM_ROOT = 0.29
LUM_L1 = 0.65
LUM_LEAF = 1.00                                          # 白底（与背景同——叶靠黑框+黑字辨形）
LUM_GAP_MIN = 0.35

DEFAULT_HUES = [175.0, 210.0]                            # 青绿/蓝（选必1源思维导图同族）

CM_PER_IN = 2.54


# ----------------------------- 提取 -----------------------------

def extract_flow_docx(path):
    """知识清单 docx → (件标题, flow)；flow＝文档序 [(\"sec\",节标题)|(\"ent\",(no,mark,name))]。"""
    import docx
    d = docx.Document(str(path))
    doc_title, flow = "", []
    for p in d.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if not doc_title:
            doc_title = t
            continue
        style = (p.style.name or "")
        if style.startswith("Heading") or style.startswith("标题"):
            m = SEC_RE.match(t)
            if m and m.group(2):
                flow.append(("sec", t))
                continue
        m = ENTRY_RE.match(t)
        if m:
            flow.append(("ent", (int(m.group(1)), m.group(2), m.group(3).strip())))
    return doc_title, flow


def extract_flow_txt(path):
    """条目清单 txt → 同 docx 结构。节标题行「N.N 标题」；条目行「N．〔基〕名」或「N．名」。"""
    doc_title, flow = "", []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        t = raw.strip()
        if not t:
            continue
        if not doc_title:
            doc_title = t
            continue
        m = ENTRY_RE.match(t)
        if m:
            flow.append(("ent", (int(m.group(1)), m.group(2), m.group(3).strip())))
            continue
        m = ENTRY_RE_NOMARK.match(t)
        if m:
            flow.append(("ent", (int(m.group(1)), "", m.group(2).strip())))
            continue
        m = SEC_RE.match(t)
        if m and m.group(2):
            flow.append(("sec", t))
    return doc_title, flow


# ----------------------------- 配色 -----------------------------

def rel_lum(rgb):
    r, g, b = (c / 255.0 for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _hls_to_rgb(h, l, s):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, l, s)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def hue_at_luminance(h, s, target_lum):
    """给定色相/饱和度，二分 HLS 亮度使相对亮度逼近 target（容差0.005）。"""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if rel_lum(_hls_to_rgb(h, mid, s)) < target_lum:
            lo = mid
        else:
            hi = mid
    l = (lo + hi) / 2
    assert abs(rel_lum(_hls_to_rgb(h, l, s)) - target_lum) <= 0.005, \
        "亮度定槽失败 h=%s s=%s" % (h, s)
    return _hls_to_rgb(h, l, s), l


def extract_hues(png_paths, top=4):
    """源思维导图位图 → 主色相列表（饱和像素色相24桶直方图，饱和度×计数加权）。"""
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return None
    weights = {}
    for pth in png_paths:
        arr = np.asarray(Image.open(str(pth)).convert("RGB").resize((160, 160)))
        for row in arr:
            for r, g, b in row:
                h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
                if s < 0.25 or l < 0.12 or l > 0.92:    # 跳过近白/近黑/灰
                    continue
                k = int(h * 360) // 15
                weights[k] = weights.get(k, 0) + float(s)
    if not weights:
        return None
    ks = sorted(weights, key=lambda k: -weights[k])[:top]
    return [k * 15 + 7.5 for k in ks]


def class_colors(hues):
    """色相列表 → 三级节点色（根/L1/叶）＋xcolor 定义行、填充/边框名、色值、亮度、阶梯差。"""
    hues = list(hues) if hues else []
    h_root = hues[0] if hues else DEFAULT_HUES[0]
    h_l1 = hues[1 % len(hues)] if len(hues) > 1 else DEFAULT_HUES[1]
    s_root = 0.75                                          # 深槽提饱和保彩印观感
    root, _ = hue_at_luminance(h_root, s_root, LUM_ROOT)
    l1, _ = hue_at_luminance(h_l1, 0.70, LUM_L1)
    leaf = (255, 255, 255)
    defs = (r"\definecolor{mmRootFill}{RGB}{%d,%d,%d}" % root
            + "\n" + r"\definecolor{mmLOneFill}{RGB}{%d,%d,%d}" % l1)
    fills = {"root": "mmRootFill", "l1": "mmLOneFill", "l2": "white"}
    draws = {"root": "black!75", "l1": "black!55", "l2": "black!45"}
    cols = {"root": root, "l1": l1, "l2": leaf}
    lums = {k: rel_lum(v) for k, v in cols.items()}
    gaps = [abs(lums["root"] - lums["l1"]), abs(lums["l1"] - lums["l2"])]
    assert all(g >= LUM_GAP_MIN - 0.005 for g in gaps), \
        "A3 FAIL 节点色亮度阶梯差<0.35: %s" % gaps
    return defs, fills, draws, cols, lums, gaps


# ----------------------------- LaTeX -----------------------------

_TEX_ESC = (("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
            ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
            ("^", r"\textasciicircum{}"))


def tex_escape(s):
    for ch, rep in _TEX_ESC:
        s = s.replace(ch, rep)
    return s


_BREAK_BEFORE = "的与和及、，：；）（／/"        # 优先在连接词/标点前折行


def wrap_title(t):
    """节标题折行（root anchor=east 用）：名称超8字对半折两行，断点向连接词/标点微调。"""
    m = re.match(r"^(\d+(?:\.\d+)+)\s*(.*)$", t)
    if not m:
        return tex_escape(t)
    num, name = m.group(1), m.group(2)
    if len(name) > 8:
        mid = (len(name) + 1) // 2
        cand = [i for i in range(max(2, mid - 3), min(len(name) - 1, mid + 3) + 1)
                if name[i] in _BREAK_BEFORE]
        if cand:
            mid = min(cand, key=lambda i: abs(i - mid))
        name = name[:mid] + r" \\ " + name[mid:]
    return tex_escape("%s %s" % (num, name))


# ----------------------------- 主流程 -----------------------------

def run(docx=None, txt=None, out_dir=".", source_imgs=(), dpi=300,
        max_leaves=20, section_titles=None):
    assert dpi >= 300, "A4 FAIL dpi=%s<300" % dpi
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # ---- 提取（保留标题/条目文档序交错）----
    doc_title, flow = (extract_flow_docx(docx) if docx else extract_flow_txt(txt))
    entries_all = [e for k, e in flow if k == "ent"]

    # ---- A1 编号连续 ----
    nums = [e[0] for e in entries_all]
    assert nums == list(range(1, len(nums) + 1)), \
        "A1 FAIL 条目编号不连续: %s…" % str(nums[:12])

    # ---- 分组（重放 flow；二级节=组，三级小节=组内子块）----
    section_titles = section_titles or {}
    groups = []            # {key,title,children:[(小节标题|None,[条目…])…]}
    cur2 = None
    cur_sub = None

    def group_for(key, heading_text):
        if groups and groups[-1]["key"] == key:
            return groups[-1]
        title = heading_text or ("%s %s" % (key, section_titles.get(key, ""))
                                 if section_titles.get(key) else key)
        g = {"key": key, "title": title.strip(), "children": []}
        groups.append(g)
        return g

    for kind, val in flow:
        if kind == "sec":
            no = SEC_RE.match(val).group(1)
            if no.count(".") == 1:
                cur2 = no
                group_for(cur2, val)
                cur_sub = None
            else:                                # 三级小节
                cur2 = no.rsplit(".", 1)[0]
                g = group_for(cur2, None)
                cur_sub = (val, [])
                g["children"].append(cur_sub)
        else:
            assert groups, "条目出现在任何节标题之前: %s" % str(val)
            g = groups[-1]
            if cur_sub is not None:
                cur_sub[1].append(val)
            else:                                # 节直挂条目：并入同一直挂块
                if g["children"] and g["children"][-1][0] is None:
                    g["children"][-1][1].append(val)
                else:
                    g["children"].append((None, [val]))

    # ---- 出图计划（组叶数>max_leaves → 按三级小节拆图）----
    plan = []                # [(根标题, [(一级标题|None, [条目])…])]
    for g in groups:
        leaves = sum(len(c[1]) for c in g["children"])
        if leaves <= max_leaves:
            plan.append((g["title"], g["children"]))
        else:
            for sub_title, ents in g["children"]:
                if sub_title is not None:
                    plan.append((sub_title, [(None, ents)]))
                elif len(ents) > max_leaves:     # 节直挂超限（罕见）→ 对半分
                    half = (len(ents) + 1) // 2
                    plan.append((g["title"] + "（上）", [(None, ents[:half])]))
                    plan.append((g["title"] + "（下）", [(None, ents[half:])]))
                else:
                    plan.append((g["title"], [(None, ents)]))

    # ---- A2 节点＝条目名子集＋100% 覆盖 ----
    node_names = [e[2] for _r, children in plan for _s, ents in children for e in ents]
    entry_names = [e[2] for e in entries_all]
    assert set(node_names) <= set(entry_names), \
        "A2 FAIL 节点名非条目名子集: %s" % (set(node_names) - set(entry_names))
    assert len(node_names) == len(entry_names), \
        "A2 FAIL 覆盖不完整 节点%d != 条目%d" % (len(node_names), len(entry_names))
    assert len(set(node_names)) == len(node_names), "A2 FAIL 节点重复"
    assert len(node_names) <= len(entry_names)

    # ---- 配色（源图色板提取 / 默认）----
    hues = extract_hues(source_imgs) if source_imgs else None
    defs, fills, draws, cols, lums, gaps = class_colors(hues)

    # ---- 逐图渲染（走 绘图模板库.mindmap_tree 模板）----
    from PIL import Image
    records = []
    for i, (root_title, children) in enumerate(plan, 1):
        m = SEC_RE.match(root_title)
        root_no = m.group(1) if m else "组%02d" % i
        tree = []
        for sub, ents in children:
            names = [tex_escape(e[2]) for e in ents]
            if sub is not None:
                tree.append((tex_escape(sub), names))
            else:
                tree.extend((n, []) for n in names)
        spec = tpl.mindmap_tree(
            wrap_title(root_title), tree,
            slot=1.15, x_l1=4.6, x_l2=10.3, root_x=4.35, root_anchor="east",
            root_font=r"\normalsize\bfseries", l1_font=r"\small\bfseries",
            l2_font=r"\small",
            root_fill=fills["root"], l1_fill=fills["l1"], l2_fill=fills["l2"],
            root_draw=draws["root"], l1_draw=draws["l1"], l2_draw=draws["l2"],
            l1_text_width=4.8, l2_text_width=6.2, extra_defs=defs)
        png = out / ("章知识结构图_第%02d组_%s.png" % (i, root_no.replace(".", "-")))
        tpl.render(spec, png, dpi=dpi, keep_pdf=True)
        gray = dict(tpl.LAST_REPORT)
        w_px, h_px = Image.open(str(png)).size
        w_cm, h_cm = w_px / dpi * CM_PER_IN, h_px / dpi * CM_PER_IN
        # A3 后半：灰度对比度实测
        assert gray.get("contrast") is not None and gray["contrast"] >= LUM_GAP_MIN, \
            "A3 FAIL %s 灰度对比度 %s < 0.35" % (png.name, gray.get("contrast"))
        # A4/A5 版面断言：1:1 显示不超版心宽、不超单页可用高
        assert w_cm <= 18.0, "A4 FAIL 图宽超版心18cm: %s %.2f" % (png.name, w_cm)
        assert h_cm <= 24.5, "A4 FAIL 图高超单页可用高24.5cm: %s %.2f" % (png.name, h_cm)
        records.append({
            "序号": i, "根节点": root_title, "文件": png.name,
            "节点数(叶)": sum(len(c[1]) for c in children),
            "px": [w_px, h_px], "建议显示宽cm": round(w_cm, 2),
            "建议显示高cm": round(h_cm, 2), "灰度对比度": gray["contrast"],
            "底色L": gray.get("bg"), "墨迹L5%": gray.get("text_L"),
            "dpi": dpi,
        })

    # ---- 插入辅助 tsv ----
    tsv = out / "插入辅助.tsv"
    with tsv.open("w", encoding="utf-8-sig") as f:
        f.write("序号\t文件\t根节点\t节点数(叶)\t建议显示宽cm\t建议显示高cm\t插入位置\n")
        for r in records:
            f.write("%s\t%s\t%s\t%s\t%s\t%s\t知识清单件文内开头标题与〔基〕/〔进〕图例行之后，按序号顺序依次排列\n"
                    % (r["序号"], r["文件"], r["根节点"], r["节点数(叶)"],
                       r["建议显示宽cm"], r["建议显示高cm"]))

    report = {
        "件": doc_title, "条目数": len(entries_all),
        "断言": {"A1编号连续1..N": "PASS N=%d" % len(entries_all),
                 "A2节点=条目名子集且100%覆盖":
                     "PASS 节点%d=条目%d，子集校验通过" % (len(node_names), len(entry_names)),
                 "A3亮度阶梯差": ["%.3f" % g for g in gaps],
                 "A3灰度对比度": ["%s=%.3f" % (r["文件"], r["灰度对比度"]) for r in records],
                 "A4dpi": dpi,
                 "A5节点字号": "\\small=9pt，1:1 显示即目标值"},
        "色板来源": "源图色相提取" if hues else "默认色板",
        "源图色相": hues, "三级色RGB": {k: list(v) for k, v in cols.items()},
        "三级色相对亮度": {k: round(v, 3) for k, v in lums.items()},
        "分组": [{"根": r["根节点"], "叶数": r["节点数(叶)"]} for r in records],
        "逐图": records,
    }
    (out / "结构图报告.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="章知识结构图生成（N14，工具债⑦）")
    ap.add_argument("--docx", help="知识清单 docx（条目题名行＝权威源）")
    ap.add_argument("--txt", help="条目清单 txt（备用输入）")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--source-img", nargs="*", default=[], help="源素材思维导图位图")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--max-leaves", type=int, default=20)
    ap.add_argument("--section-titles", default=None,
                    help='JSON：缺失二级节标题补名，如 {"2.2":"直线及其方程"}')
    a = ap.parse_args(argv)
    titles = json.loads(a.section_titles) if a.section_titles else None
    rep = run(docx=a.docx, txt=a.txt, out_dir=a.out_dir, source_imgs=a.source_img,
              dpi=a.dpi, max_leaves=a.max_leaves, section_titles=titles)
    print("PASS 条目数=%d 组数=%d 色板=%s" % (rep["条目数"], len(rep["逐图"]), rep["色板来源"]))
    for r in rep["逐图"]:
        print("  %s 叶%d 灰度%.3f 显示%.1fx%.1fcm"
              % (r["文件"], r["节点数(叶)"], r["灰度对比度"],
                 r["建议显示宽cm"], r["建议显示高cm"]))


if __name__ == "__main__":
    main(sys.argv[1:])
