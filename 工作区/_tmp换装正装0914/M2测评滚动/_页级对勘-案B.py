# -*- coding: utf-8 -*-
r"""M2 测评滚动·案B 页级对勘（只读比对；读数写 _门谱读数/_页级对勘-案B.md）

面：原印面＝成卷件 main.pdf（只读靶）｜印本档＝案B main.pdf｜纯题档＝案B main-pure.pdf。
核验：
  C 题面零漂移——原印面每页每一非空行（归一后）须现于印本档同页（案B 题面未动 ⇒ 期望 0 缺）；
    纯题档期望缺段＝卷末答案速查表行（案2 决议：纯题档隐去），余行 0 缺。
  附卷断言——印本档末页（新增）含「参考答案」头＋N 处 `N. [答案]`；纯题档无附卷页且全文无 `[答案]`。
  像素层——150dpi 栅栏 samples 逐页 md5：印本档 p1..N ↔ 原印面 p1..N（期望逐字节同）；
    纯题档 p1..N-1 同；速查表页/附卷页为设计内差异页，算差并登记。
版面变更点清单（案B）：①附卷页＝新增（印本档末页）；②纯题档速查表隐去；③纯题档附卷整页跳过。
"""
import io, os, re, sys, hashlib, unicodedata
import pymupdf as fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
BOOKS = [("测评卷", r"测评卷\main.pdf", "测", 19),
         ("滚动卷A", r"滚动卷\滚A\main.pdf", "滚A", 16),
         ("滚动卷B", r"滚动卷\滚B\main.pdf", "滚B", 16)]


def norm(s):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s))


def pmd5(pg):
    return hashlib.md5(pg.get_pixmap(dpi=150).samples).hexdigest()


def pdiff(pg_a, pg_b):
    """逐字节差占比（不同 md5 时的次级读数）。"""
    a, b = pg_a.get_pixmap(dpi=150).samples, pg_b.get_pixmap(dpi=150).samples
    if len(a) != len(b):
        return -1.0
    d = sum(1 for x, y in zip(a, b) if x != y)
    return 100.0 * d / len(a)


def main():
    L = ["# M2 测评滚动·案B 页级对勘读数（2026-09-14 波3）\n"]
    for label, rel, pref, nkeys in BOOKS:
        orig = fitz.open(os.path.join(SRC, rel))
        true = fitz.open(os.path.join(HERE, label, "main.pdf"))
        pure = fitz.open(os.path.join(HERE, label, "main-pure.pdf"))
        L.append("\n## %s（原 %d 页｜true %d 页＝+1 附卷｜pure %d 页）"
                 % (label, len(orig), len(true), len(pure)))
        # ---- C 题面行零漂移（逐页行集包含）----
        raw = {k: [pg.get_text() for pg in d] for k, d in [("原", orig), ("真", true), ("纯", pure)]}
        for name, doc in [("印本档", true), ("纯题档", pure)]:
            miss = []
            for pno in range(len(orig)):
                tgt = norm(raw["真" if name == "印本档" else "纯"][pno])
                for ln in raw["原"][pno].split("\n"):
                    q = norm(ln)
                    if len(q) >= 2 and q not in tgt:
                        miss.append((pno + 1, q[:30]))
            L.append("- %s 缺原段 %d 行%s" % (name, len(miss),
                    ("｜" + " ⫶ ".join("p%d:%s" % m for m in miss[:8])) if miss else "（题面零漂移）"))
        # ---- 附卷断言 ----
        tlast = true[len(true) - 1].get_text()
        ntrue = len(re.findall(r"\[\s*答案\s*\]", tlast))
        head = "参考答案" in tlast
        tall = "".join(raw["真"])
        pall = "".join(raw["纯"])
        L.append("- 附卷在印面：true 末页含「参考答案」头＝%s｜末页 `[答案]`×%d（期望 %d）｜true 全卷 `[答案]`×%d"
                 % (head, ntrue, nkeys, tall.count("[答案]")))
        L.append("- 纯题档零泄答：`[答案]`×%d（期望 0）｜「参考答案」头＝%s（期望 False）"
                 % (pall.count("[答案]"), "参考答案" in pall))
        # ---- 像素层 ----
        rows = []
        for i in range(len(orig)):
            m0, m1, m2 = pmd5(orig[i]), pmd5(true[i]), pmd5(pure[i])
            d1 = "同" if m0 == m1 else "%.4f%%" % pdiff(orig[i], true[i])
            d2 = "同" if m0 == m2 else "%.4f%%" % pdiff(orig[i], pure[i])
            rows.append("p%d:原↔真 %s｜原↔纯 %s" % (i + 1, d1, d2))
        extra = ""
        if len(true) > len(orig):
            extra = "｜附卷 p%d＝新增（版面变更点①）" % len(true)
        L.append("- 像素(150dpi samples md5)：" + "；".join(rows) + extra
                 + "｜纯题档速查表隐去页/行＝设计内差异（版面变更点②③）")
        for d in (orig, true, pure):
            d.close()
    txt = "\n".join(L) + "\n"
    open(os.path.join(HERE, "_页级对勘-案B.md"), "w", encoding="utf-8").write(txt)
    print(txt)


main()
