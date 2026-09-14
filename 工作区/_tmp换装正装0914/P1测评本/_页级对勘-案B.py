# -*- coding: utf-8 -*-
"""P1 测评本·案B 页级对勘（只读比对；读数写 _门谱读数/_页级对勘-案B.md）。

承 M2 测评滚动波3 _页级对勘-案B.py 同制，P1 侧适配：原印面＝本树 main.src.pdf
（成卷/装配/测评本/测评卷/main.pdf 逐字节快照）。

面：原印面＝main.src.pdf｜印本档＝main.pdf｜纯题档＝main-pure.pdf。
核验：
  C 题面零漂移——原印面每页每一非空行（归一后）须现于印本档同页（案B 题面未动 ⇒ 期望 0 缺）；
    纯题档期望缺段＝卷末答案速查表行（案2 决议：纯题档隐去），余行 0 缺。
  附卷断言——印本档末页（新增）含「参考答案」头＋19 处 `[答案]`；纯题档无附卷页且全文无 `[答案]`。
  像素层——150dpi samples 逐页 md5：印本档 p1..3 ↔ 原印面 p1..3（期望逐字节同＝题面像素零差硬门）；
    纯题档 p1..2 同；p3＝速查表隐去设计内差异页（算差并登记）。
版面变更点清单（案B）：①附卷 p4＝新增（印本档末页，含尾块）；②纯题档速查表隐去；③纯题档附卷整页跳过。
"""
import io, os, re, sys, hashlib, unicodedata
import pymupdf as fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "测评卷")
NKEYS = 19

L = ["# P1 测评本·案B 页级对勘读数（波5，2026-09-14）\n"]


def norm(s):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s))


def pmd5(pg):
    return hashlib.md5(pg.get_pixmap(dpi=150).samples).hexdigest()


def pdiff(pg_a, pg_b):
    a, b = pg_a.get_pixmap(dpi=150).samples, pg_b.get_pixmap(dpi=150).samples
    if len(a) != len(b):
        return -1.0
    return 100.0 * sum(1 for x, y in zip(a, b) if x != y) / len(a)


def main():
    orig = fitz.open(os.path.join(PIECE, "main.src.pdf"))
    true = fitz.open(os.path.join(PIECE, "main.pdf"))
    pure = fitz.open(os.path.join(PIECE, "main-pure.pdf"))
    L.append("## 测评卷（原 %d 页｜true %d 页＝+1 附卷｜pure %d 页）" % (len(orig), len(true), len(pure)))
    raw = {k: [pg.get_text() for pg in d] for k, d in [("原", orig), ("真", true), ("纯", pure)]}
    for name, key in [("印本档", "真"), ("纯题档", "纯")]:
        miss = []
        for pno in range(len(orig)):
            tgt = norm(raw[key][pno])
            for ln in raw["原"][pno].split("\n"):
                q = norm(ln)
                if len(q) >= 2 and q not in tgt:
                    miss.append((pno + 1, q[:30]))
        L.append("- %s 缺原段 %d 行%s" % (name, len(miss),
                ("｜" + " ⫶ ".join("p%d:%s" % m for m in miss[:10])) if miss else "（题面零漂移）"))
    tlast = true[len(true) - 1].get_text()
    tall, pall = "".join(raw["真"]), "".join(raw["纯"])
    nlast = len(re.findall(r"\[\s*答案\s*\]", tlast))
    L.append("- 附卷在印面：true 末页含「参考答案」头＝%s｜末页 `[答案]`×%d（期望 %d）｜true 全卷 `[答案]`×%d"
             % ("参考答案" in tlast, nlast, NKEYS, tall.count("[答案]")))
    L.append("- 纯题档零泄答：`[答案]`×%d（期望 0）｜「参考答案」头＝%s（期望 False）"
             % (pall.count("[答案]"), "参考答案" in pall))
    rows, px_bad = [], 0
    for i in range(len(orig)):
        m0, m1, m2 = pmd5(orig[i]), pmd5(true[i]), pmd5(pure[i])
        d1 = "同" if m0 == m1 else "%.4f%%" % pdiff(orig[i], true[i])
        d2 = "同" if m0 == m2 else "%.4f%%" % pdiff(orig[i], pure[i])
        if m0 != m1:
            px_bad += 1
        rows.append("p%d:原↔真 %s｜原↔纯 %s" % (i + 1, d1, d2))
    L.append("- 像素(150dpi samples md5)：" + "；".join(rows))
    L.append("- 题面像素逐页同原印面（硬门）：true %d/%d 页同——%s｜附卷 p%d＝新增（版面变更点①）｜"
             "pure p3 差＝速查表隐去（版面变更点②③，设计内）"
             % (len(orig) - px_bad, len(orig), "PASS" if px_bad == 0 else "FAIL", len(true)))
    # 附卷页行样（目验索引用）
    samp = [ln for ln in tlast.split("\n") if ln.strip()][:6]
    L.append("- 附卷末页行样：" + " ⫶ ".join(s.replace("\n", "") for s in samp[:4]))
    for d in (orig, true, pure):
        d.close()
    txt = "\n".join(L) + "\n"
    open(os.path.join(HERE, "_门谱读数", "_页级对勘-案B.md"), "w", encoding="utf-8").write(txt)
    print(txt)


main()
