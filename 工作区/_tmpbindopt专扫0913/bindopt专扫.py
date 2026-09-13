# -*- coding: utf-8 -*-
"""bindopt 同类病专扫 0913（v2）：导学件12件 \bindopt（及等价）固定槽选项排（四连排0.25lw＋双盒0.5lw）
tex 侧清单 × PDF span 实测盒位——相邻选项墨宽真侵入 >2.5mm 记红；末槽墨过栏右缘（跨栏叠印）同判。
用法：python bindopt专扫.py [件1 ...]（缺省＝全12件，件名＝导学件下目录名）"""
import pymupdf, re, os, sys, json, unicodedata

ROOT = r"C:/提示词/工作区/M2-第1章量产0911/成卷"
OUT = os.path.dirname(os.path.abspath(__file__))
PIECES = ["课时01", "课时02", "课时03", "课时04", "课时05", "课时06",
          "课时07", "课时08", "课时09", "课时10", "衔接节-1.2.1前", "章末-本章总结提升"]

# 版面常数（qp-layout：A4 左右17.2mm，版心175.6mm，multicols{2} 栏距7.6mm ⇒ 栏宽\linewidth≈238.2pt）
PT2MM = 25.4 / 72.0
COL_L1, COL_L2 = 48.76, 308.52
COLW = (175.6 - 7.6) / 2 / 25.4 * 72.0          # ≈238.2pt
PITCH4 = 0.25 * COLW - 0.5 * 10.5               # ≈54.3pt（10.5pt 字号 0.5em）
PITCH2 = 0.5 * COLW - 1.0 * 10.5                # ≈108.6pt
PITCHX = PITCH2 - 0.5 * (11.0 / 25.4 * 72)      # 衔接\xlxopt 双盒＝0.5lw−0.5xhang−1em ≈93.0pt
THRESH_MM = 2.5

W25 = r"\dimexpr0.25\linewidth-0.5em\relax"
W50 = r"\dimexpr0.5\linewidth-1em\relax"
WXH = r"\dimexpr0.5\linewidth-0.5\xhang-1em\relax"


def grab_arg(s, i):
    depth, j = 0, i
    while j < len(s):
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("brace unbalanced: " + s[:80])


def slots_of(line):
    """行内等宽固定槽序列 [(宽宏,内容),...]"""
    out, i = [], 0
    pat = re.compile(r"\\makebox\[(\\dimexpr0\.(?:25|5)\\linewidth-(?:0\.5\\xhang-)?[.0-9]+em\\relax)\]\[l\]")
    while True:
        g = pat.search(line, i)
        if not g:
            break
        b = line.index("{", g.end())
        content, e = grab_arg(line, b)
        out.append((g.group(1), content))
        i = e
    return out


def norm_txt(s):
    r"""剥 TeX（含 \frac{a}{b}→ab、\sqrt{a}→√a 类命令保参）→NFKD→去组合符/空白，用于内容配对"""
    s = re.sub(r"\\penalty\d+", "", s)
    s = re.sub(r"\\sqrt(?:\[(.*?)\])?\{([^{}]*)\}", r"√\2", s)
    for c1, c2 in [("alpha", "α"), ("beta", "β"), ("gamma", "γ"), ("theta", "θ"),
                   ("lambda", "λ"), ("mu", "μ"), ("pi", "π"), ("perp", "⟂"),
                   ("parallel", "∥"), ("angle", "∠"), ("triangle", "△"),
                   ("circ", "∘"), ("cdot", "·"), ("times", "×"), ("pm", "±"),
                   ("in", "∈"), ("notin", "∉"), ("neq", "≠"), ("leq", "≤"), ("geq", "≥"),
                   ("rightarrow", "→"), ("Rightarrow", "⇒"), ("equiv", "≡")]:
        s = s.replace("\\" + c1, c2)
    for _ in range(8):
        s2 = re.sub(r"\\[a-zA-Z@]+\*?(\{[^{}]*\})", r"\1", s)
        if s2 == s:
            break
        s = s2
    s = re.sub(r"\\(?:fontsize|selectfont|noindent|quad|hspace)[{ ]*", " ", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?", "", s)
    s = re.sub(r"[{}\\\[\]$^&_\s()（）]", "", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("\u2212", "-").replace("\u2044", "/")
    return s


def tex_inventory(d):
    """主 tex 所有 ≥2 等宽固定槽行（bindopt 为主，含等价形制），按文档序"""
    path = os.path.join(ROOT, "导学件", d, "main.tex")
    lines = open(path, encoding="utf-8").read().splitlines()
    inv = []
    for n, line in enumerate(lines):
        ls = line.strip()
        sl = slots_of(ls)
        if len(sl) < 2:
            continue
        widths = {w for w, _ in sl}
        kind = "4连排" if len(sl) >= 4 else ("双盒" if (len(sl) == 2 and widths <= {W50, WXH}) else f"{len(sl)}槽")
        macro = ls.split()[0] if ls.startswith("\\") else "?"
        qid = "?"
        for m in range(n, max(n - 40, -1), -1):
            prev = lines[m]
            g = re.search(r"\\numboldjian\s*(\d+)", prev)
            if g:
                qid = "检" + g.group(1); break
            g = re.search(r"\\tihao\{(\d+)\}", prev)
            if g:
                qid = "题" + g.group(1); break
            g = re.search(r"\\liB\{([^}]*)\}", prev)
            if g:
                qid = "变[" + g.group(1) + "]"; break
            g = re.search(r"\\tjdnr\{[^}]*\}\{[^}]*\}\{([^}]*)\}", prev)
            if g:
                qid = "例[" + g.group(1).replace("\\textbf{", "").replace("}", "") + "]"; break
        inv.append(dict(file=d, line=n + 1, kind=kind, macro=macro, n=len(sl), qid=qid,
                        disp="|".join(norm_txt(c) for _, c in sl)[:200]))
    return inv


def key_of(s):
    """配对宽松键：仅留 CJK/拉丁/数字（丢弃数学符号、√、∘ 等抽取易失字符）"""
    return "".join(c for c in norm_txt(s)
                   if "\u4e00" <= c <= "\u9fff" or c.isascii() and (c.isalnum()))


def pdf_rows(d):
    """PDF 实测（rawdict 字级）：marker 字 A．/B．/C．/D．起点＝槽位；段墨宽按流序取段"""
    doc = pymupdf.open(os.path.join(ROOT, "导学件", d, "main.pdf"))
    rows = []
    for pno, pg in enumerate(doc):
        # 字符流（流序）：每项 (x0,x1,y0,y1,ch)
        chars, marks = [], []
        rd = pg.get_text("rawdict", flags=pymupdf.TEXT_INHIBIT_SPACES)
        for b in rd["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    bbox = s["bbox"]
                    for c in s.get("chars", []):
                        cb = c.get("bbox", bbox)
                        chars.append((cb[0], cb[2], cb[1], cb[3], c["c"]))
        for i, (x0, x1, y0, y1, ch) in enumerate(chars):
            if ch in "ABCD" and i + 1 < len(chars) and chars[i + 1][4] in "．.":
                marks.append(i)
        groups = []
        for i in marks:
            x0, by = chars[i][0], chars[i][3]
            placed = False
            for g in groups:
                if abs(by - g["by"]) > 2.5:
                    continue
                m = g["idx"]
                gap = x0 - chars[m[-1]][0]
                if len(m) >= 2:
                    p0 = chars[m[-1]][0] - chars[m[-2]][0]
                    base = PITCH4 if abs(p0 - PITCH4) < 6 else PITCH2
                    if abs(gap - base) > 7:
                        continue
                elif not (abs(gap - PITCH4) < 6 or abs(gap - PITCH2) < 7 or abs(gap - PITCHX) < 3.5):
                    continue                # 首距必落 0.25/0.5/xhang 槽档，拒并邻栏同行
                m.append(i); placed = True; break
            if not placed:
                groups.append(dict(by=by, idx=[i]))
        for gp in groups:
            idx = gp["idx"]
            if len(idx) < 2:
                continue
            by = gp["by"]
            xcap_lo, xcap_hi = (46, 300) if chars[idx[0]][0] < 290 else (306, 596)
            segs, joined = [], []
            for k, ii in enumerate(idx):
                j2 = idx[k + 1] if k + 1 < len(idx) else next(
                    (t for t in marks if t > ii), len(chars))
                xm = chars[ii][0]
                seg = [chars[t] for t in range(ii + 2, j2)   # 跳过 marker 字与其后的点号
                       if -10.5 < chars[t][3] - by < 13.5
                       and xcap_lo <= chars[t][0] <= xcap_hi
                       and chars[t][0] >= xm - 2]
                allc = [chars[ii], chars[ii + 1]] + seg
                segs.append((chars[ii][0], max(c[1] for c in allc)))
                joined.append("".join(c[4] for c in allc))
            pitches = [round(segs[k + 1][0] - segs[k][0], 1) for k in range(len(segs) - 1)]
            if all(abs(p - PITCH4) < 6 for p in pitches) and len(segs) >= 3:
                kind = "4连排"
            elif len(segs) == 2 and (abs(pitches[0] - PITCH2) < 8 or abs(pitches[0] - PITCHX) < 3.5):
                kind = "双盒"
            elif len(segs) == 2 and abs(pitches[0] - PITCH4) < 6:
                kind = "2槽(0.25?)"
            else:
                kind = "异形"
            colL = COL_L1 if segs[0][0] < 290 else COL_L2
            over = [round((segs[k][1] - segs[k + 1][0]) * PT2MM, 2) for k in range(len(segs) - 1)]
            slotw = PITCH4 if kind in ("4连排", "2槽(0.25?)") else PITCH2 if kind == "双盒" else PITCH4
            over_slot = round((segs[-1][1] - (segs[-1][0] + slotw)) * PT2MM, 2)
            over_col = round((segs[-1][1] - (colL + COLW)) * PT2MM, 2)
            rows.append(dict(page=pno + 1, y=round(by, 1), kind=kind, n=len(segs),
                             pitches=pitches, overlaps=over, over_col=over_col,
                             over_slot=over_slot, text=norm_txt("".join(joined))[:120],
                             key="|".join(key_of(j)[:8] for j in joined)))
    return sorted(rows, key=lambda r: (r["page"], r["y"]))


def pair(d, inv, rows, res):
    """tex↔PDF 键配对：等槽数＋各行宽松键（CJK/字母数字）按序命中"""
    used = set()
    for t in inv:
        slotstrs = [key_of(s) for s in t["disp"].split("|")]
        best = None
        for i, r in enumerate(rows):
            if i in used or r["n"] != t["n"] or r["kind"] != t["kind"]:
                continue
            rk = r["key"].split("|")
            ok = all(rk[k].startswith(slotstrs[k][:3]) if len(slotstrs[k]) >= 3
                     else rk[k] == slotstrs[k] for k in range(len(slotstrs)))
            if ok:
                best = i; break
        if best is None:
            res["unpaired_tex"].append(f"{d} L{t['line']} {t['kind']} {t['macro']} {t['disp'][:50]}")
            continue
        used.add(best)
        r = rows[best]
        worst = max(r["overlaps"]) if r["overlaps"] else -9
        red = worst > THRESH_MM or r["over_col"] > THRESH_MM
        res["recs"].append(dict(file=d, qid=t["qid"], line=t["line"], kind=t["kind"],
                                macro=t["macro"], page=r["page"], overlaps=r["overlaps"],
                                over_slot=r["over_slot"], over_col=r["over_col"], red=red,
                                plain=t["disp"]))
    for i, r in enumerate(rows):
        if i not in used:
            res["extras"].append(dict(file=d, **r))


def main():
    files = sys.argv[1:] or PIECES
    res = dict(recs=[], unpaired_tex=[], extras=[])
    for d in files:
        pair(d, tex_inventory(d), pdf_rows(d), res)
    n4 = sum(1 for r in res["recs"] if r["kind"] == "4连排")
    n2 = sum(1 for r in res["recs"] if r["kind"] == "双盒")
    print(f"=== bindopt 专扫 v2（红判：相邻真侵入>{THRESH_MM}mm 或 末槽墨越栏右缘>{THRESH_MM}mm）===")
    print(f"配对成功：{len(res['recs'])}（四连排 {n4} / 双盒 {n2}）；tex未配对 {len(res['unpaired_tex'])}；PDF额外槽行 {len(res['extras'])}")
    reds = [r for r in res["recs"] if r["red"]]
    print("--- 红项 ---")
    for r in reds:
        print(f"[红] {r['file']} p{r['page']} {r['qid']} L{r['line']} {r['kind']}({r['macro']}) "
              f"侵入{r['overlaps']}mm 越槽{r['over_slot']}mm 越栏{r['over_col']}mm | {r['plain'][:70]}")
    print(f"红 {len(reds)} / 通过 {len(res['recs']) - len(reds)}")
    if res["unpaired_tex"]:
        print("--- tex未配对（须人核）---"); [print("   ", x) for x in res["unpaired_tex"]]
    if res["extras"]:
        print("--- PDF额外槽行（非tex清单命中，含等价形制，同判）---")
        for e in res["extras"]:
            worst = max(e["overlaps"]) if e["overlaps"] else -9
            red = worst > THRESH_MM or e["over_col"] > THRESH_MM
            print(f"  {'[红]' if red else '[过]'} {e['file']} p{e['page']} {e['kind']} "
                  f"侵入{e['overlaps']} 越槽{e['over_slot']} 越栏{e['over_col']} | {e['text'][:60]}")
            res["recs"].append(dict(file=e["file"], qid="额外", line="-", kind=e["kind"],
                                    macro="extra", page=e["page"], overlaps=e["overlaps"],
                                    over_slot=e["over_slot"], over_col=e["over_col"], red=red,
                                    plain=e["text"]))
    reds = [r for r in res["recs"] if r["red"]]
    print(f"\n合计：排查 {len(res['recs'])} 槽行 / 红 {len(reds)}")
    json.dump(res, open(os.path.join(OUT, "扫描结果.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
