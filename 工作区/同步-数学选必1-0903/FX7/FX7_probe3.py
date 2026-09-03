# -*- coding: utf-8 -*-
"""FX7 probe3: I2细节——①315段oMath结构 ③编注线性数学 ④sz21 ⑤空格卫生 ⑥灰底越界"""
import os, re
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

tree = etree.parse(os.path.join(WK, "unpack", "I2", "word", "document.xml"))
ps = list(tree.getroot().iter(W + "p"))
print("I2 段落数:", len(ps))

def ptext(p):
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))

print("=" * 25, "① p#315 oMath 内 m:r 逐个（shd/color）", "=" * 25)
p = ps[315]
for om in p.iter(M + "oMath"):
    print("--- oMath block:")
    for mr in om.iter(M + "r"):
        txt = "".join(t.text or "" for t in mr.iter(M + "t"))
        rpr = mr.find(W + "rPr")
        shd = col = szv = None
        if rpr is not None:
            s = rpr.find(W + "shd")
            shd = s.get(W + "fill") if s is not None else None
            c = rpr.find(W + "color")
            col = c.get(W + "val") if c is not None else None
            z = rpr.find(W + "sz")
            szv = z.get(W + "val") if z is not None else None
        print(f"    m:r [{txt}] shd={shd} color={col} sz={szv}")

print()
print("=" * 25, "③ 【编注】段线性数学（w:t内为真阳性）", "=" * 25)
# 嫌疑字符模式：√ ² ³ ₀-₉ ⁺ ⁻ θ λ μ Δ π ≠ ≥ ≤ × 或 字母数字等号连缀
SUS = re.compile(r"[√²³⁰¹²³⁴-⁹₀-₉⁺⁻×÷≈≤≥≠]|[a-zA-Z]\d|\d[a-zA-Z]|[a-zA-Z]=|[（(][a-zA-Z]")
tp = 0
fp = 0
for i, p in enumerate(ps):
    t_all = ptext(p)
    if "【编注】" not in t_all[:6]:
        continue
    # w:t 文本
    wt_texts = [el.text or "" for el in p.iter(W + "t")]
    wt_join = "".join(wt_texts)
    if not SUS.search(wt_join):
        continue
    mt_texts = [el.text or "" for el in p.iter(M + "t")]
    if mt_texts:
        # 有公式：需逐run看嫌疑出现在w:t还是m:t
        pass
    print(f"I2 p#{i}:")
    print(f"    全文: {t_all[:170]}")
    print(f"    w:t拼接: {repr(wt_join[:170])}")
    # 标出w:t内的嫌疑子串
    for m in SUS.finditer(wt_join):
        s = max(0, m.start() - 12)
        e = min(len(wt_join), m.end() + 18)
        print(f"    w:t嫌疑: …{repr(wt_join[s:e])}…")
        break  # 每段首例即可，细节编辑时再逐个
    tp += 1
print("含嫌疑w:t的【编注】段数:", tp)

print()
print("=" * 25, "④ sz=21 run 逐个", "=" * 25)
cnt21 = 0
for i, p in enumerate(ps):
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        z = rpr.find(W + "sz")
        if z is not None and z.get(W + "val") == "21":
            wt = "".join(t.text or "" for t in r.iter(W + "t"))
            has_img = any(True for _ in r.iter(W + "drawing"))
            has_om = any(True for _ in r.iter(M + "oMath"))
            has_mt = any((t.text or "").strip() for t in r.iter(M + "t"))
            zc = rpr.find(W + "szCs")
            print(f"I2 p#{i} sz21: w:t={repr(wt[:30])} img={has_img} oMath={has_om} m:t非空={has_mt} szCs={zc.get(W+'val') if zc is not None else None}")
            cnt21 += 1
print("sz21 run总数:", cnt21)

print()
print("=" * 25, "⑤ I2 空格卫生", "=" * 25)
for i, p in enumerate(ps):
    t_all = ptext(p)
    wt_join = "".join(el.text or "" for el in p.iter(W + "t"))
    mt_join = "".join(el.text or "" for el in p.iter(M + "t"))
    issues = []
    if re.search(r"  +", wt_join):
        issues.append("w:t双半空格")
    if re.search(r"  +", mt_join):
        issues.append("m:t双半空格(公式内)")
    if re.search(r"[ ]+[，。；：、？！]", wt_join):
        issues.append("w:t全角前空格")
    if re.search(r"[ ]+[，。；：、？！]", mt_join):
        issues.append("m:t全角前空格(公式内)")
    if "\xa0" in wt_join:
        issues.append(f"w:t nbsp×{wt_join.count(chr(160))}")
    if "\xa0" in mt_join:
        issues.append(f"m:t nbsp×{mt_join.count(chr(160))}(公式内)")
    last = None
    for el in p.iter():
        if el.tag in (W + "t", M + "t"):
            last = el
    if last is not None and last.text and re.search(r"[ \u00A0]+$", last.text):
        issues.append(f"段尾空格({etree.QName(last).localname})")
    if issues:
        print(f"I2 p#{i} {issues}: {repr(t_all[:80])}")
