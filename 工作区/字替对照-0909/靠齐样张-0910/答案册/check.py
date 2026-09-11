"""答案册·靠齐样张自检（编译三 0 ＋ 恰 2 页 ＋ 关键几何/色值实测 ＋ 断言禁则 ＋ 拍板落位探针）。

口径：编译侧＝build2.txt 正则计数；PDF 侧＝pymupdf 直读（不依赖渲染器色管）。
跑法：python check.py（先 xelatex×2 → render.py）
"""
import collections
import os
import re

import numpy as np
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PT2MM = 25.4 / 72
MM2PT = 72 / 25.4

raw = open(os.path.join(HERE, "build2.txt"), encoding="utf-8", errors="replace").read()
print("① 编译三 0：error=%d overfull=%d missingchar=%d"
      % (len(re.findall(r"^! ", raw, re.M)), raw.count("Overfull"),
         len(re.findall("Missing character", raw))))
print("   （附）underfull=%d" % raw.count("Underfull"))

doc = pymupdf.open(os.path.join(HERE, "main.pdf"))
print("② 页数=%d（靶＝恰 2）" % len(doc))
for i, page in enumerate(doc, 1):
    print("   p%d 页面=%.1f×%.1fmm" % (i, page.rect.width * PT2MM, page.rect.height * PT2MM))

# ---------- ③ 断言禁则：行首标点（J2）／CJK-CJK 拉伸异常行（J4） ----------
HEAD_PUNCT = "。，、；：？！）］}』”’·—…"
bad = []
for i, page in enumerate(doc, 1):
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            txt = "".join(sp["text"] for sp in l["spans"]).strip()
            if txt and txt[0] in HEAD_PUNCT:
                bad.append((i, txt[:20]))
print("③ 行首标点（J2 靶＝0）＝%d %s" % (len(bad), bad[:3]))


def is_cjk(ch):
    o = ord(ch)
    return 0x3000 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF or 0x2018 <= o <= 0x201D


stretch = []
for i, page in enumerate(doc, 1):
    for b in page.get_text("rawdict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            for sp in l["spans"]:
                chars = sp["chars"]
                for a, c in zip(chars, chars[1:]):
                    if not (a["c"].strip() and c["c"].strip()):
                        continue
                    if is_cjk(a["c"]) and is_cjk(c["c"]):
                        gap = (c["bbox"][0] - a["bbox"][2]) * MM2PT
                        if gap > 0.5 * sp["size"]:
                            stretch.append((i, round(gap, 2), a["c"], c["c"]))
print("④ CJK-CJK 隙>0.5em 拉伸异常行（J4 靶＝0）＝%d %s" % (len(stretch), stretch[:4]))

# ---------- ⑤ 逐页几何实测 ----------
# J3 图文重叠：图（矢量路径并集）矩形 × 文本行 bbox（排除 <8pt 图内标签）
for i, page in enumerate(doc, 1):
    u = None
    for dr in page.get_drawings():
        r = dr["rect"]
        if (40 < r.y0 * PT2MM < 250 and 8.0 < max(r.width, r.height) * PT2MM < 100
                and r.width * PT2MM < 100):
            u = r if u is None else (u | r)
    if u is None:
        print("⑤p%d 无图（J3 不适用）" % i)
        continue
    ov = 0
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            if pymupdf.Rect(l["bbox"]).intersects(u) and max(s["size"] for s in l["spans"]) >= 8.0:
                ov += 1
    print("⑤p%d 图矩形 x %.2f–%.2f y %.2f–%.2fmm｜J3 图文重叠（除图内标签）＝%d（靶 0）"
          % (i, u.x0 * PT2MM, u.x1 * PT2MM, u.y0 * PT2MM, u.y1 * PT2MM, ov))

for i, page in enumerate(doc, 1):
    pix = page.get_pixmap(dpi=300, colorspace=pymupdf.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    px = 300 / 25.4
    body = img[: int(275 * px), :]
    cols = np.where((body < 160).any(axis=0))[0]
    print("⑤p%d 正文墨缘 左=%.2fmm 右=%.2fmm（版心 17.20–192.80mm）"
          % (i, cols[0] / px, cols[-1] / px))

    rowsum = (body < 160).sum(axis=1)
    idx = [j for j, v in enumerate(rowsum) if v > 0]
    segs, s, prev = [], idx[0], idx[0]
    for v in idx[1:]:
        if v - prev > 2:
            segs.append(s)
            s = v
        prev = v
    segs.append(s)
    gaps = collections.Counter(round((b - a) / px, 2) for a, b in zip(segs, segs[1:])
                               if 5.0 < (b - a) / px < 8.0)
    print("   行距主峰=%.2fmm top3=%s（18.0pt＝6.35mm）"
          % (gaps.most_common(1)[0][0], gaps.most_common(3)))

    band = img[int(90 * px):int(150 * px), :]
    col = np.median(band, axis=0)
    lo, hi = int(103 * px), int(107 * px)
    x = lo + int(np.argmin(col[lo:hi]))
    print("   栏线 x=%.2fmm 中位灰=%d（靶 105.0／灰 188／窗 170–210）" % (x / px, int(col[x])))

    sub = img[int(275 * px):, :]
    m = (sub > 195) & (sub < 248)
    rows = np.where(m.sum(axis=1) > 150)[0] + int(275 * px)
    band = img[rows[0]:rows[-1] + 1, :]
    bm = ((band > 195) & (band < 248)).mean(axis=0)
    bc = np.where(bm > 0.5)[0]
    print("   页码灰块 y=%.2f–%.2fmm 高=%.2fmm 宽=%.2fmm 底距页底=%.2fmm 左缘=%.2fmm 右缘=%.2fmm（靶 7.8／31.0／11.2）"
          % (rows[0] / px, rows[-1] / px, (rows[-1] - rows[0]) / px, (bc[-1] - bc[0]) / px,
             297 - rows[-1] / px, bc[0] / px, bc[-1] / px))
    # 页码数字墨色（H3 靶＝纯黑）：块内暗于 160 的像素最小灰
    num = band[:, bc[0]:bc[-1]]
    dk = num[num < 160]
    print("   页码数字最暗灰=%d（H3 靶＝纯黑 0；灰 76＝footgray 泄漏即为 76）"
          % (int(dk.min()) if dk.size else -1))

    L = body[:, int(16 * px):int(102 * px)]
    R = body[:, int(106 * px):int(194 * px)]
    def last(a_):
        r = np.where((a_ < 160).any(axis=1))[0]
        return r[-1] / px
    print("   双栏末墨 左=%.1fmm 右=%.1fmm（文本区底 277.0mm；#10 参差收尾）" % (last(L), last(R)))

    fonts = sorted({f[3].split("+")[-1] for f in page.get_fonts()})
    print("   字体=%s" % ", ".join(fonts))

# ---------- ⑥ 悬挂深度两档（#21/#22）＋ 题号→标签实隙（C4/C5） ----------
for i, page in enumerate(doc, 1):
    seen = {}
    for b in page.get_text("rawdict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            chars = [c for sp in l["spans"] for c in sp["chars"]]
            txt = "".join(c["c"] for c in chars)
            mm = re.match(r"^(\d+)\.", txt)
            if not mm or "[答案]" not in txt:
                continue
            j = next(k for k, c in enumerate(chars) if c["c"] == "[")
            right = max(c["bbox"][2] for c in chars[:j] if c["c"] != " ")
            depth = round((chars[j]["bbox"][0] - chars[0]["bbox"][0]) * PT2MM, 2)
            seen.setdefault(depth, []).append(mm.group(1))
    for k in sorted(seen):
        print("⑥p%d 悬挂深度=%.2fmm（题号 %s…%s，靶 单号 5.8／双位 7.6）"
              % (i, k, seen[k][0], seen[k][-1]))

# ---------- ⑦ 拍板落位探针 ----------
t1 = doc[0].get_text()
t2 = doc[1].get_text()
print("⑦ 页码 p1 含 75＝%s p2 含 76＝%s（拍板⑧ 全书连续·全品答案册实证起页 P75）"
      % ("75" in t1, "76" in t2))
for tag in ["[答案]", "[分析]", "[详解]", "[点睛]", "[解法一]", "[解法二]", "参考答案"]:
    print("   %-8s p1=%-5s p2=%-5s（拍板② 四标签＋并行解法＋⑨ 册名）" % (tag, tag in t1, tag in t2))
print("   册首行「参考答案」居中：中心=%.2fmm（版心中 105.00）"
      % next(((l["bbox"][0] + l["bbox"][2]) / 2 * PT2MM)
             for b in doc[0].get_text("dict")["blocks"] if b.get("type") == 0
             for l in b["lines"] if "参考答案" in "".join(s["text"] for s in l["spans"])
             and l["bbox"][1] * PT2MM < 30))
print("   【】残留＝%s（拍板② 半角标签）；「知识点」出现＝%d 次（拍板③ 不印）"
      % (bool(re.search(r"[【】]", t1 + t2)), (t1 + t2).count("知识点")))
# 0911 题型轮探针：①逐题「题型：××」行 ②「[题型总结]」说明块
print("   「题型：」行＝%d 处（0911 题型轮·靶 15＝逐题无漏）；「[题型总结]」块＝%d 处（靶 1）"
      % ((t1 + t2).count("题型："), (t1 + t2).count("[题型总结]")))
# 拍板④ 答案值平文：源件不得出现下划线/底纹手段（\underline、\colorbox、\ansul、shade）
src = open(os.path.join(HERE, "body.tex"), encoding="utf-8").read()
mod = "".join(open(os.path.join(HERE, f), encoding="utf-8").read()
              for f in ("qp-answ-blocks.tex", "qp-answ-layout.tex", "qp-answ-headfoot.tex"))
hits = [k for k in ("\\underline", "\\colorbox", "\\ansul", "shade", "\\uline") if k in src]
print("   答案值标记（拍板④ 平文）：body.tex 命中＝%s；模块内 \\colorbox 仅页码块＝%d 处"
      % (hits or "无", mod.count("\\colorbox")))
