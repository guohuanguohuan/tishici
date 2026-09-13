# -*- coding: utf-8 -*-
r"""测评本试迁·页级对勘（只读比对，读数写本目录 对勘-页级读数.md）

四面一靶：
  原印面 = M2 成卷件 main.pdf（只读靶）
  印本档 = 本树 main.pdf（showans=true，答案回嵌题后）
  纯题档 = 本树 main-pure.pdf（showans=false）
  对照件 = 本树 main-ctl.pdf（只换装不迁移 → 隔离「换装本身」的漂移）

核验：
  A 页几何——列底越界 / 越右界。手排三栏 `\jpcol` 用
    `\raisebox{0pt}[0pt][0pt]{\vtop{…}}`，声明高度与深度都是 0pt，
    TeX 永远看不到栏高 → log 里不可能出 Overfull \vbox，
    「零错零溢出」不可作凭，必须拿 PDF 坐标验。
  B 值零漂移——值快照丁区每键值须现于印本档同页（分强/弱两级判）。
  C 题面零漂移——原印面每一非空行（归一后）须现于新面同页。
"""
import io, json, os, re, sys, unicodedata
import pymupdf as fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
BOOKS = [("测评卷", r"测评卷\main.pdf", "测", 19),
         ("滚动卷A", r"滚动卷\滚A\main.pdf", "滚A", 16),
         ("滚动卷B", r"滚动卷\滚B\main.pdf", "滚B", 16)]

MM = 72.0 / 25.4                      # 1mm = 2.83465pt
TEXT_BOT = (284.2 - 17.6) * MM        # 版心下沿 = 266.6mm = 755.7pt
FOOT_Z = 762.0                        # y0 超此值判为页脚区，不计栏底
COLS = [(8.9, 128.9), (139.9, 259.9), (270.9, 390.9)]   # 三栏 x 区间 mm
TOL = 3.0                             # 越界容差 pt

MACRO_DROP = r"(overrightarrow|dfrac|frac|sqrt|left|right|circ|angle|perp|leq|geq|quad|qquad|varphi|phi|pi|psi|sigma|omega|lambda|mu|nu|rho|tau|chi|delta|gamma|beta|epsilon|varepsilon|zeta|eta|kappa|theta|alpha|cos|tan|sin|log|ln|lg|text|mathrm|mathbf|hat|overline|cdot|times|div|pm|mp|in|notin|subset|subseteq|cup|cap|emptyset|vec|ov)"


def norm(s):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s))


def skeleton(s):
    """值串/PDF 文本 → 只留字母数字汉字（先剥掉 LaTeX 宏名与组合用符）"""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\\" + MACRO_DROP, "", s)
    s = re.sub(r"\\.", "", s)
    s = "".join(ch for ch in unicodedata.normalize("NFD", s)
                if not unicodedata.combining(ch))
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]", "", s)


def blocks(doc):
    out = []
    for pno, pg in enumerate(doc, 1):
        for b in pg.get_text("blocks"):
            x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
            xc = (x0 + x1) / 2.0
            col = next((i for i, (a, z) in enumerate(COLS, 1)
                        if a * MM - 8 <= xc <= z * MM + 8), 0)
            out.append({"page": pno, "col": col, "x0": x0, "x1": x1,
                        "y0": y0, "y1": y1, "t": norm(txt)})
    return out


def geom(bl):
    """逐页逐栏：栏底（非页脚块最大 y1）、越下界块数、越右界块数"""
    rows, over_b, over_r = [], [], []
    for pno in sorted({b["page"] for b in bl}):
        for col in (1, 2, 3):
            sel = [b for b in bl if b["page"] == pno and b["col"] == col]
            body = [b for b in sel if b["y0"] < FOOT_Z]
            bottom = max((b["y1"] for b in body), default=0.0)
            bad_b = [b for b in body if b["y1"] > TEXT_BOT + TOL]
            bad_r = [b for b in body if b["x1"] > COLS[col - 1][1] * MM + TOL]
            for b in bad_b:
                over_b.append("p%d栏%d 底%.0f「%s」" % (pno, col, b["y1"], b["t"][:16]))
            for b in bad_r:
                over_r.append("p%d栏%d 右%.0f「%s」" % (pno, col, b["x1"], b["t"][:16]))
            rows.append((pno, col, bottom, len(bad_b), len(bad_r)))
    return rows, over_b, over_r


def main():
    snap = json.load(open(os.path.join(SRC, "答案册", "值快照.json"), encoding="utf-8"))
    L = ["# 测评本试迁·页级对勘读数\n",
         "口径：1mm=%.4fpt；版心下沿 %.1fpt（266.6mm）；栏 x 区间 %s pt；容差 %.1fpt。"
         % (MM, TEXT_BOT, [(round(a * MM), round(z * MM)) for a, z in COLS], TOL, ),
         "",
         "注：`\jpcol` 是 `\raisebox{0pt}[0pt][0pt]{\vtop{…}}`——声明高/深均 0pt，",
         "TeX 看不到栏高，log 里不可能出 Overfull \\vbox；溢出只能靠下面几何读数判。\n"]

    for label, rel, pref, nkeys in BOOKS:
        orig = os.path.join(SRC, rel)
        mine = os.path.join(HERE, label)
        faces = {"原印面": orig,
                 "印本档": os.path.join(mine, "main.pdf"),
                 "纯题档": os.path.join(mine, "main-pure.pdf"),
                 "对照件": os.path.join(mine, "main-ctl.pdf")}
        faces = {k: v for k, v in faces.items() if os.path.exists(v)}
        docs = {k: fitz.open(v) for k, v in faces.items()}
        L.append("\n## %s（键账 %d）\n" % (label, nkeys))

        # ---------- A 几何 ----------
        L.append("### A 页几何（越下界＝栏内容底过版心；越右界＝超出本栏 x 上沿）\n")
        L.append("| 面 | 页数 | 页:栏→栏底pt（占版心%） | 越下界 | 越右界 |")
        L.append("|---|---|---|---|---|")
        for k, d in docs.items():
            rows, ob, orr = geom(blocks(d))
            cell = " ".join("%d:%d=%.0f(%.0f%%)" % (p, c, btm, 100 * btm / TEXT_BOT)
                            for p, c, btm, _, _ in rows)
            L.append("| %s | %d | %s | %d%s | %d%s |" % (
                k, len(d), cell, len(ob),
                ("：" + "；".join(ob[:3])) if ob else "",
                len(orr), ("：" + "；".join(orr[:3])) if orr else ""))
        L.append("")

        # ---------- C 题面行零漂移 ----------
        raw = {k: [pg.get_text() for pg in d] for k, d in docs.items()}
        ntxt = {k: [norm(x) for x in v] for k, v in raw.items()}
        skut = {k: [skeleton(x) for x in v] for k, v in raw.items()}
        L.append("### B/C 零漂移\n")
        for k in docs:
            if k == "原印面":
                continue
            miss_strong, miss_weak = [], []
            npg = len(ntxt["原印面"])
            for pno in range(1, npg + 1):
                nb, nsk = ntxt[k][pno - 1], skut[k][pno - 1]
                for ln in raw["原印面"][pno - 1].split("\n"):
                    q = norm(ln)
                    if len(q) < 2:
                        continue
                    if q not in nb:
                        if skeleton(ln) in nsk:
                            continue                      # 剥宏名/组合符后命中 → 记归一差异非漂移
                        miss_strong.append((pno, q[:36]))
            extra = len(ntxt[k]) - npg
            L.append("- %s：原印面行未在同页复现 %d 行；页数差 %+d%s"
                     % (k, len(miss_strong), extra,
                        ("｜" + " ⫶ ".join("p%d:%s" % m for m in miss_strong[:6])) if miss_strong else ""))

        # ---------- B 值零漂移 ----------
        if "印本档" in docs:
            strong = "".join(skut["印本档"])

            def issub(a, b):          # a 是否为 b 的保序子序列
                it = iter(b)
                return all(ch in it for ch in a)

            hit = mid = miss = 0
            bad = []
            for i in range(1, nkeys + 1):
                key = "%s-%d" % (pref, i)
                val = snap.get(key)
                if val is None:
                    bad.append("%s 快照无此键"); miss += 1; continue
                probe = skeleton(val)[:14]
                if not probe:
                    bad.append("%s 值剥完为空←%s" % (key, val[:20])); miss += 1
                elif probe in strong:
                    hit += 1
                elif issub(probe, strong):
                    mid += 1; bad.append("%s 保序命中←%s" % (key, val[:24]))
                else:
                    miss += 1; bad.append("%s 未命中←%s" % (key, val[:24]))
            L.append("- 值零漂移：快照丁区 %d 键 → 子串强命中 %d ＋ 保序命中 %d ＝ %d/%d，未命中 %d%s"
                     % (nkeys, hit, mid, hit + mid, nkeys, miss,
                        ("｜" + " ;; ".join(bad)) if bad else ""))

        # ---------- 换装本身：对照件 vs 原印面 ----------
        if "对照件" in docs:
            same = skut["原印面"] == skut["对照件"]
            diff = []
            for i in range(min(len(skut["原印面"]), len(skut["对照件"]))):
                if skut["原印面"][i] != skut["对照件"][i]:
                    a, b = skut["原印面"][i], skut["对照件"][i]
                    j = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
                    diff.append("p%d@%d 原「%s」新「%s」" % (i + 1, j, a[j:j + 26], b[j:j + 26]))
            L.append("- 换装本身（对照件 vs 原印面，剥宏名/组合符后逐页比）：%s%s"
                     % ("完全相同" if same else "有差异",
                        ("｜" + " ⫶ ".join(diff[:4])) if diff else ""))
        for d in docs.values():
            d.close()

    txt = "\n".join(L) + "\n"
    open(os.path.join(HERE, "对勘-页级读数.md"), "w", encoding="utf-8").write(txt)
    print(txt)


main()
