# -*- coding: utf-8 -*-
r"""压字检测-测评本：印本档（答案回嵌后）逐栏「行叠字」扫描

三栏 `\jpcol` 零声明高，答案块插进栏内会把后续题面下推；真正要防的不是溢出而是行叠字。
判据（先滤数学噪声）：
  同页同栏两条视觉行（同 y0 碎片先合并）
  ① y 区间重叠 > 50% 短者行高  ② x 区间重叠 > 20pt
  ③ 两行各含 ≥3 汉字（分数/根式上下标天然重叠，靠此条排除）
并按「答案压题面／答案互压／题面互压」分类点名——只有前两类是回嵌引入的新风险。
"""
import io, os, sys
import pymupdf as fitz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
MM = 72.0 / 25.4
COLS = [(8.9, 128.9), (139.9, 259.9), (270.9, 390.9)]
BOOKS = [("测评卷", r"测评卷\main.pdf"), ("滚动卷A", r"滚动卷\滚A\main.pdf"),
         ("滚动卷B", r"滚动卷\滚B\main.pdf")]


def ncn(t):
    return sum(1 for ch in t if chr(0x4E00) <= ch <= chr(0x9FFF))


def isans(t):
    t = t.lstrip()
    return t.startswith("[答案]") or t.startswith("[解析]") or "答案]" in t[:9] or "解析]" in t[:9]


def scan(pdf):
    d = fitz.open(pdf)
    hits, detail = 0, []
    for pno, pg in enumerate(d, 1):
        vis = []
        for b in pg.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                bb = l["bbox"]
                t = "".join(s["text"] for s in l["spans"]).strip()
                if not t or bb[1] > 760:
                    continue
                xc = (bb[0] + bb[2]) / 2
                col = next((i for i, (a, z) in enumerate(COLS, 1) if a * MM - 8 <= xc <= z * MM + 8), 0)
                if col:
                    vis.append([pno, col, bb[0], bb[1], bb[2], bb[3], t])
        vis.sort(key=lambda r: (r[0], r[1], r[3]))
        merged = []
        for r in vis:
            if merged and r[0] == merged[-1][0] and r[1] == merged[-1][1] and abs(r[3] - merged[-1][3]) < 1.5:
                m = merged[-1]
                m[2] = min(m[2], r[2]); m[4] = max(m[4], r[4])
                m[3] = min(m[3], r[3]); m[5] = max(m[5], r[5]); m[6] += r[6]
            else:
                merged.append(list(r))
        for i in range(len(merged)):
            for j in range(i + 1, len(merged)):
                a, b2 = merged[i], merged[j]
                if a[0] != b2[0] or a[1] != b2[1]:
                    continue
                oy = min(a[5], b2[5]) - max(a[3], b2[3])
                h = min(a[5] - a[3], b2[5] - b2[3])
                ox = min(a[4], b2[4]) - max(a[2], b2[2])
                if not (h > 0 and oy > 0.50 * h and ox > 20 and ncn(a[6]) >= 3 and ncn(b2[6]) >= 3):
                    continue
                kind = "答案压题面" if (isans(a[6]) != isans(b2[6])) else \
                       ("答案互压" if (isans(a[6]) and isans(b2[6])) else "题面互压")
                hits += 1
                detail.append("%s：p%d栏%d 叠%.1fpt/行高%.1fpt｜%s ⨯ %s"
                              % (kind, a[0], a[1], oy, h, a[6][:14], b2[6][:14]))
    d.close()
    return hits, detail


rows = []
for label, rel in BOOKS:
    for face, fn in (("原印面", None), ("印本档", "main-fix.pdf"), ("纯题档", "main-pure-fix.pdf")):
        p = os.path.join(SRC, rel) if fn is None else os.path.join(HERE, label, fn)
        hits, detail = scan(p)
        n_ans = sum(1 for x in detail if x.startswith("答案"))
        rows.append((label, face, hits, n_ans, detail[:3]))
        print("%-6s %-4s 叠字 %d（其中涉答案块 %d）%s" % (label, face, hits, n_ans,
              "｜" + "；".join(d[:52] for d in detail[:2]) if detail else ""))

print("\n汇总：涉答案块的新增叠字 %d 处" % sum(r[3] for r in rows if r[1] == "印本档"))
with open(os.path.join(HERE, "压字检测读数.md"), "w", encoding="utf-8") as f:
    f.write("# 压字检测读数（补钉版印本档／纯题档 vs 原印面）\n\n"
            "判据：同栏两视觉行 y 重叠 >50% 短者行高 且 x 重叠 >20pt 且两行各含 ≥3 汉字。\n\n"
            "| 件 | 面 | 叠字处数 | 涉答案块 |\n|---|---|---|---|\n"
            + "\n".join("| %s | %s | %d | %d |" % (a, b, c, d) for a, b, c, d, _ in rows)
            + "\n\n## 明细（每件每面首 3 处）\n\n"
            + "\n".join("- %s %s：%s" % (a, b, "；".join(d) if d else "无") for a, b, c, d, dd in
                        [(x[0], x[1], x[2], x[4], None) for x in rows] for d in [dd] if True)
            + "\n")
