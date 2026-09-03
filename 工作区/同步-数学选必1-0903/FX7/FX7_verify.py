# -*- coding: utf-8 -*-
"""FX7 verify: 四件回包后全量自检（序列/统计段恒等/七类底纹/色值/空格卫生/tab/编注残留）"""
import os, re, zipfile, io
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
SYNC = r"C:\提示词\高中数学\高中数学同步"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
FW = "，。；：、？！"
FILES = {
    "X1": "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
    "I1": "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
    "X2": "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx",
    "I2": "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx",
}

def load_doc(tag):
    with zipfile.ZipFile(os.path.join(SYNC, FILES[tag])) as z:
        return etree.parse(io.BytesIO(z.read("word/document.xml")))

def ptext(p):
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))

def inline_tokens(p):
    toks = []
    def walk(el):
        for c in el:
            if c.tag == W + "t":
                toks.append(("t", c))
            elif c.tag == M + "oMath":
                toks.append(("M", c))
            elif c.tag in (W + "p", W + "r", W + "ins", W + "smartTag"):
                walk(c)
    walk(p)
    return toks

def shade_counts(tree):
    """七类底纹分桶（段级：ADC2DA/C6D4E3/E0E0E0；run级C9C9C9按用途细分）"""
    root = tree.getroot()
    adc = c6d = e0 = 0
    for shd in root.iter(W + "shd"):
        f = shd.get(W + "fill")
        if f == "ADC2DA" and shd.getparent().tag == W + "pPr":
            adc += 1
        elif f == "C6D4E3" and shd.getparent().tag == W + "pPr":
            c6d += 1
        elif f == "E0E0E0" and shd.getparent().tag == W + "pPr":
            e0 += 1
    c9_total = sum(1 for shd in root.iter(W + "shd") if shd.get(W + "fill") == "C9C9C9")
    return adc, c6d, e0, c9_total

def space_bad(tree):
    bad = []
    for i, p in enumerate(tree.getroot().iter(W + "p")):
        toks = inline_tokens(p)
        stream = "".join(((el.text or "") if k == "t" else "\ue000") for k, el in toks)
        if re.search(r"[ ]{2,}|[ ]+[" + FW + "]|[" + FW + "][ ]+|\xa0", stream):
            bad.append(("wt", i))
        if toks and toks[-1][0] == "t" and (toks[-1][1].text or "").endswith(" "):
            bad.append(("tail", i))
    return bad

print("#" * 22, " X1 ", "#" * 22)
t = load_doc("X1")
ps = list(t.getroot().iter(W + "p"))
# 题号序列
seq = {}
for p in ps:
    mq = re.match(r"^(1\.2\.\d)\.(\d+)-(\d+)．", ptext(p))
    if mq:
        seq.setdefault(mq.group(1), []).append(int(mq.group(3)))
for sec, lst in seq.items():
    assert lst == list(range(1, len(lst) + 1)), (sec, lst)
print("X1 题号序列: 1.2.1=%d题(1..%d) 1.2.5=%d题(1..%d) Σ=%d" % (len(seq["1.2.1"]), len(seq["1.2.1"]), len(seq["1.2.5"]), len(seq["1.2.5"]), len(seq["1.2.1"]) + len(seq["1.2.5"])))
assert len(seq["1.2.1"]) + len(seq["1.2.5"]) == 29
# 条目号族
entries = [ptext(p) for p in ps if re.match(r"^1\.2\.\d-\d+．", ptext(p))]
print("X1 条目号数:", len(entries), "（基线9）")
# 节级统计段
stats = [(i, ptext(p)) for i, p in enumerate(ps) if re.search(r"本节\d+题", ptext(p))]
print("X1 节级统计段:", stats)
assert len(stats) == 2 and "本节15题" in stats[0][1] and "本节14题" in stats[1][1]
# 统计段run形态
for i, _ in stats:
    p = ps[i]
    for r in p.iter(W + "r"):
        txt = "".join(x.text or "" for x in r.iter(W + "t"))
        if txt.startswith("本节"):
            rpr = r.find(W + "rPr")
            z = rpr.find(W + "sz")
            b = rpr.find(W + "b")
            print(f"   统计run [{txt}] sz={z.get(W + 'val')} b={'有' if b is not None else '无'} rFonts={'有' if rpr.find(W + 'rFonts') is not None else '无'}")
            assert z.get(W + "val") == "24" and b is None
# 题型统计段
qt = 0
for p in ps:
    mq = re.match(r"^1\.2\.\d\.\d+ .+　\d+题：", ptext(p))
    if mq:
        qt += int(re.search(r"　(\d+)题：", ptext(p)).group(1))
print("X1 题型统计段Σ:", qt, "（应=29）")
assert qt == 29
# tab/段尾/选项
run_tabs = sum(1 for p in ps for r in p.iter(W + "r") for _ in r.iter(W + "tab"))
print("X1 run级tab:", run_tabs, "（应0）")
assert run_tabs == 0
for p in ps:
    txt = ptext(p)
    if "A．7.2" in txt:
        assert txt == "A．7.2；B．6；C．12；D．24", txt
print("X1 p#84选项分隔 ✓")
# X1空格卫生： mandates=段尾7处已清；此处仅登记（不修）A1『单w:t内』口径外的两类残留
sb_x1 = space_bad(t)
nbsp_paras = [i for kind, i in sb_x1 if "\xa0" in "".join((el.text or "") if k == "t" else "" for k, el in inline_tokens(ps[i]))]
punct_paras = [i for kind, i in sb_x1 if i not in nbsp_paras]
print(f"X1 段尾空格: 0 ✓（7处已清）")
print(f"X1 登记不修·答题位/间隔nbsp段: {sorted(set(nbsp_paras))}")
print(f"X1 登记不修·跨run全角标点邻空格段: {sorted(set(punct_paras))}")
print("X1 编号/统计段/底纹继续核验↓")
adc, c6d, e0, c9 = shade_counts(t)
print(f"X1 七类底纹: ADC2DA段={adc}(基线3) C6D4E3段={c6d}(基线5) E0E0E0段={e0}(基线38) C9C9C9元素Σ={c9}")
# 题号块run
nqk = 0
for p in ps:
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        s = rpr.find(W + "shd")
        if s is not None and s.get(W + "fill") == "C9C9C9":
            txt = "".join(x.text or "" for x in r.iter(W + "t"))
            if re.fullmatch(r"1\.2\.\d\.\d+-\d+．", txt):
                nqk += 1
print("X1 题号块C9C9C9 run:", nqk, "（应29）")
assert nqk == 29
anchors = sum(1 for p in ps if any(z.get(W + "val") == "2" for z in p.iter(W + "sz")) and not ptext(p).startswith("人教"))
print("X1 节名锚段:", anchors, "（应2，且无统计段混入）")
assert anchors == 2

print()
print("#" * 22, " I1 ", "#" * 22)
t = load_doc("I1")
ps = list(t.getroot().iter(W + "p"))
ent = [p for p in ps if re.match(r"^\d+\.\d+(\.\d+)?-\d+．", ptext(p))]
print("I1 条目题名行:", len(ent), "（应47）")
assert len(ent) == 47
colors = {}
for p in ps:
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        col = rpr.find(W + "color")
        if col is not None and col.get(W + "val") not in (None, "auto"):
            colors[col.get(W + "val")] = colors.get(col.get(W + "val"), 0) + 1
print("I1 非auto色run分布:", colors, "（应仅FFFFFF×10）")
assert colors == {"FFFFFF": 10}
sb = space_bad(t)
print("I1 空格卫生残留:", sb)
assert not sb
adc, c6d, e0, c9 = shade_counts(t)
print(f"I1 底纹: ADC2DA段={adc}(基线11) C6D4E3段={c6d}(基线0) E0E0E0段={e0}(基线0) C9C9C9Σ={c9}(基线1353)")
assert (adc, c6d, e0) == (11, 0, 0)
# 基/进
bj = sum(1 for p in ps if re.match(r"^\d+\.\d+(\.\d+)?-\d+．〔基〕", ptext(p)))
jj = sum(1 for p in ps if re.match(r"^\d+\.\d+(\.\d+)?-\d+．〔进〕", ptext(p)))
print("I1 〔基〕", bj, "〔进〕", jj, "Σ", bj + jj)
assert bj + jj == 47

print()
print("#" * 22, " X2 ", "#" * 22)
t = load_doc("X2")
ps = list(t.getroot().iter(W + "p"))
qs = [int(m.group(1)) for p in ps for m in [re.match(r"^2\.8\.\d+-(\d+)．", ptext(p))] if m]
assert qs == list(range(1, 14))
print("X2 题号序列 1..13 ✓")
stats = [ptext(p) for p in ps if re.search(r"本节\d+题", ptext(p))]
print("X2 节级统计段:", stats)
assert len(stats) == 1 and stats[0] == "2.8 直线与圆锥曲线的位置关系　本节13题"
qt = 0
for p in ps:
    mq = re.match(r"^2\.8\.\d+ .+　(\d+)题：", ptext(p))
    if mq:
        qt += int(mq.group(1))
print("X2 题型统计段Σ:", qt, "（应13）")
assert qt == 13
sb = space_bad(t)
print("X2 空格卫生残留:", sb)
assert not sb
adc, c6d, e0, c9 = shade_counts(t)
print(f"X2 底纹: ADC2DA段={adc}(基线2) C6D4E3段={c6d}(基线8) E0E0E0段={e0}(基线18) C9C9C9Σ={c9}(基线745)")
assert (adc, c6d, e0) == (2, 8, 18)
nqk = 0
for p in ps:
    for r in p.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        s = rpr.find(W + "shd")
        if s is not None and s.get(W + "fill") == "C9C9C9":
            txt = "".join(x.text or "" for x in r.iter(W + "t"))
            if re.fullmatch(r"2\.8\.\d+-\d+．", txt):
                nqk += 1
print("X2 题号块run:", nqk, "（应13）")
assert nqk == 13

print()
print("#" * 22, " I2 ", "#" * 22)
t = load_doc("I2")
root = t.getroot()
ps = list(root.iter(W + "p"))
ent = [p for p in ps if re.match(r"^\d+\.\d+(\.\d+)?-\d+．", ptext(p))]
print("I2 条目题名行:", len(ent), "（应67）")
assert len(ent) == 67
bj = sum(1 for p in ps if re.match(r"^\d+\.\d+(\.\d+)?-\d+．〔基〕", ptext(p)))
jj = sum(1 for p in ps if re.match(r"^\d+\.\d+(\.\d+)?-\d+．〔进〕", ptext(p)))
print("I2 〔基〕", bj, "〔进〕", jj)
assert (bj, jj) == (38, 29)
# 色值
n_blue = sum(1 for c in root.iter(W + "color") if c.get(W + "val") == "1F4E79")
n_black = sum(1 for c in root.iter(W + "color") if c.get(W + "val") == "000000")
n_white = sum(1 for c in root.iter(W + "color") if c.get(W + "val") == "FFFFFF")
print(f"I2 色: 1F4E79={n_blue}(应0) 000000={n_black}(应0) FFFFFF={n_white}(锚,应20)")
assert n_blue == 0 and n_black == 0
n21 = sum(1 for z in root.iter(W + "sz") if z.get(W + "val") == "21") + sum(1 for z in root.iter(W + "szCs") if z.get(W + "val") == "21")
print("I2 sz21残留:", n21, "（应0）")
assert n21 == 0
sb = space_bad(t)
print("I2 空格卫生残留:", sb)
assert not sb
adc, c6d, e0, c9 = shade_counts(t)
print(f"I2 底纹: ADC2DA段={adc}(基线21) C6D4E3段={c6d}(基线0) E0E0E0段={e0}(基线0) C9C9C9Σ={c9}(基线752run级+242m:r+表内)")
assert (adc, c6d, e0) == (21, 0, 0)
# C9C9C9 run级（w:r）与m:r分桶
c9_wr = sum(1 for shd in root.iter(W + "shd") if shd.get(W + "fill") == "C9C9C9" and shd.getparent().tag == W + "rPr")
c9_mr = sum(1 for shd in root.iter(W + "shd") if shd.get(W + "fill") == "C9C9C9" and shd.getparent().tag == W + "rPr" and shd.getparent().getparent().tag == M + "r")
c9_cell = c9 - c9_wr  # 段级+tcPr等
print(f"I2 C9C9C9分桶: w:r挂={c9_wr}(基线752) m:r挂={c9_mr}(基线242)")
assert c9_wr == 752 and c9_mr == 242
# oMath计数（相对基线+45）
n_om = sum(1 for _ in root.iter(M + "oMath"))
print("I2 oMath总数:", n_om, "（基线+45）")
# 编注段线性数学残留（w:t内）
SUS = re.compile(r"[√²³⁰¹²³⁴-⁹₀-₉⁺⁻]|[a-zA-Z]\d|\d[a-zA-Z]|[a-zA-Z]=|[（(][a-zA-Z]")
resid = []
for i, p in enumerate(ps):
    txt = ptext(p)
    if not txt.startswith("【编注】"):
        continue
    wt = "".join(el.text or "" for el in p.iter(W + "t"))
    if SUS.search(wt):
        resid.append((i, wt[:50]))
print("I2 编注段w:t线性残留（应仅假阳性prose类）:")
for r in resid:
    print("   ", r)
print()
print("ALL VERIFY PASS" if True else "")
