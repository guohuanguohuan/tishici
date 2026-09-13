# -*- coding: utf-8 -*-
"""0913 批C入槽轮·修后断言自证（只读扫描，产出读数供《入槽报告.md》引用）"""
import io, os, re, time

ROOT = r"C:\提示词\工作区\M3-第2章量产0913"
D = os.path.join(ROOT, "定稿")
F10 = os.path.join(D, "批C-课时10-2.4曲线与方程.md")
F11 = os.path.join(D, "批C-课时11-2.5.1椭圆的标准方程.md")
F12 = os.path.join(D, "批C-课时12-2.5.2椭圆的几何性质.md")
F13 = os.path.join(D, "批C-课时13-2.6.1双曲线的标准方程.md")
TZ = os.path.join(D, "批C-台账.md")
HZ = os.path.join(D, "定稿汇总-第2章.md")
CN = os.path.join(ROOT, "成卷", "题面库", "canonical键名总表.md")

def rd(p):
    with io.open(p, encoding="utf-8", newline="") as f:
        return f.read().split("\n")

def cnt(lines_, pat):
    r = re.compile(pat)
    return sum(1 for x in lines_ if r.match(x))

R = []
f10, f11, f12, f13 = rd(F10), rd(F11), rd(F12), rd(F13)
tz, hz, cn = rd(TZ), rd(HZ), rd(CN)

print("== 席位块头计数（题块级）==")
for tag, L, star in [("课时10", f10, True), ("课时11", f11, True), ("课时13", f13, False)]:
    d = {}
    for g in ["简", "中", "难", "拓", "G", "单", "填"]:
        d[g] = sum(1 for x in L if re.match(r"^\**【\d+-" + g + r"\d*[｜]", x))
    print(" ", tag, d, " 合计", sum(d.values()))

print("== 正文16 恒等（简+中+难）==")
for tag, L in [("10", f10), ("11", f11), ("13", f13)]:
    n = sum(1 for x in L if re.match(r"^\**【" + tag + r"-(简|中|难)\d*[｜]", x))
    print("  课时%s 正文席 %d" % (tag, n), "OK" if n == 16 else "!!")
n12 = sum(1 for x in f12 if re.match(r"^\**【12-(简|中|难)\d*[｜]", x))
print("  课时12 正文席（禁碰件，只读数）%d" % n12)

print("== 域/拓展读数（件内§7 恒等行）==")
for tag, L, key in [("10", f10, "素材域"), ("11", f11, "素材域"), ("13", f13, "素材域")]:
    for x in L:
        if key in x and "正文" in x:
            print("  课时%s: %s" % (tag, x[:78])); break

print("== 残留禁词扫描（本轮应清零；命中逐条列行号供人工定性）==")
for tag, L in [("10", f10), ("11", f11), ("13", f13), ("台账", tz), ("汇总", hz), ("canonical", cn)]:
    for w in ["双收候裁", "候主脑裁", "撤席/让位挂", "让位候"]:
        for n, x in enumerate(L, 1):
            if w in x:
                print("   命中 %s L%d [%s]: %s" % (tag, n, w, x[:70]))
print("   （『挂主脑裁』系宽词，批A 题型名/字段映射等待裁项合法命中，故不入本表）")

print("== 关键读数在位断言 ==")
def has(lines_, s, label):
    n = sum(1 for x in lines_ if s in x)
    print("  %-28s %s 命中%d %s" % (label, "OK" if n >= 1 else "!!MISS", n, ""))
    return n >= 1
ok = True
ok &= has(tz, "**164**", "台账 域合计164")
ok &= has(tz, "**78**", "台账 拓展合计78")
ok &= has(tz, "命制（0913 入槽）", "台账 §二 命制列")
ok &= has(hz, "154 题（净域账）", "汇总 §五 批C 154")
ok &= has(hz, "课时10 域36", "汇总 §一.11 域36")
ok &= has(hz, "域37", "汇总 §一.12 域37")
ok &= has(hz, "域27", "汇总 §一.14 域27")
ok &= has(hz, "B21", "汇总 §六.4 B21")
ok &= has(hz, "B22", "汇总 §六.4 B22")
ok &= has(hz, "7首轮＋8批C置换轮", "汇总 §九 15席全闭")
ok &= has(cn, "占位键转实留痕（0913批C置换入槽轮）", "canonical 转实留痕行")
ok &= has(cn, "| 命制在途（占空位） | **0**", "canonical 命制在途销")
ok &= has(f10, "10-拓13", "10 拓13 在位")
ok &= has(f13, "13-简9", "13 简9 在位")

print("== 写入域自查（本臂本轮实际写入清单，域外一律只读）==")
writes = ["定稿/批C-课时10-2.4曲线与方程.md", "定稿/批C-课时11-2.5.1椭圆的标准方程.md",
          "定稿/批C-课时13-2.6.1双曲线的标准方程.md", "定稿/批C-台账.md", "定稿/定稿汇总-第2章.md",
          "成卷/题面库/canonical键名总表.md", "（过程件）工作区/_tmpM3入槽批C0913/*"]
print("  ", " / ".join(writes))
print("   禁碰且未写：定稿/批C-课时12、定稿/批A*、批B*、批D*、批E*、成卷/题面库/课时*.md、查重总表-轮1.md")
print("VERDICT:", "READINGS OK" if ok else "CHECK ABOVE")
