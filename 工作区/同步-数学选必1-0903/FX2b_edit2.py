# -*- coding: utf-8 -*-
# FX2b_edit2：跨run true-positive 创作句线性数学转oMath（p#272/p#555/p#803/p#3 + p#259余√2a³/12）
# 注意：这些段的线性数学夹在既有oMath之间，本脚本仅转换「纯w:t片段内」可独立成式子的子串，
# 不重排已有oMath顺序（守卫§5「原样保留」交错顺序）。0增量替换。
import os, re, shutil, zipfile
from lxml import etree
from copy import deepcopy

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XMLSP = "{http://www.w3.org/XML/1998/namespace}space"
LOG = []

def E(tag): return etree.Element(tag)

# ---- 预检：原件document.xml未被改动 + 载入 ----
with zipfile.ZipFile(SRC) as z:
    cur_doc = z.read("word/document.xml")
with open(os.path.join(BASE, "unpacked2", "document.xml"), "rb") as f:
    probe_doc = f.read()
assert cur_doc == probe_doc, "原件document.xml与Task1后快照不一致（他人改动？中止）"
doc = etree.parse(os.path.join(BASE, "unpacked2", "document.xml"))
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
assert len(paras) == 1072, f"段数异常 {len(paras)}"

def m_r(text):
    r = E(f"{{{M}}}r"); rpr = E(f"{{{W}}}rPr")
    f = E(f"{{{W}}}rFonts"); f.set(f"{{{W}}}cs", "Cambria Math")
    rpr.append(f); r.append(rpr); t = E(f"{{{M}}}t"); t.text = text; r.append(t); return r

def ctrlpr():
    cp = E(f"{{{M}}}ctrlPr"); rpr = E(f"{{{W}}}rPr")
    f = E(f"{{{W}}}rFonts"); f.set(f"{{{W}}}ascii", "Cambria Math"); f.set(f"{{{W}}}hAnsi", "Cambria Math")
    rpr.append(f); cp.append(rpr); return cp

def m_f(num_children, den_children):
    f = E(f"{{{M}}}f"); fPr = E(f"{{{M}}}fPr"); fPr.append(ctrlpr()); f.append(fPr)
    num = E(f"{{{M}}}num"); [num.append(c) for c in num_children]
    den = E(f"{{{M}}}den"); [den.append(c) for c in den_children]
    f.append(num); f.append(den); return f

def m_rad(e_children):
    rad = E(f"{{{M}}}rad"); radPr = E(f"{{{M}}}radPr")
    dh = E(f"{{{M}}}degHide"); dh.set(f"{{{M}}}val", "1")
    radPr.append(dh); radPr.append(ctrlpr())
    rad.append(radPr); rad.append(E(f"{{{M}}}deg"))
    e = E(f"{{{M}}}e"); [e.append(c) for c in e_children]
    rad.append(e); return rad

def om(children):
    o = E(f"{{{M}}}oMath"); [o.append(c) for c in children]; return o

def para_disp(p):
    s = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t": s.append(node.text or "")
        elif node.tag == f"{{{M}}}oMath": s.append(lin_node(node))
    return "".join(s)

def lin_node(node):
    if node.tag == f"{{{M}}}t": return node.text or ""
    q = etree.QName(node).localname
    if q == "rad": return "√" + "".join(lin_node(c) for c in node.find(f"{{{M}}}e"))
    if q == "f": return ("".join(lin_node(c) for c in node.find(f"{{{M}}}num")) + "/" +
                         "".join(lin_node(c) for c in node.find(f"{{{M}}}den")))
    if q == "sSup":
        e = node.find(f"{{{M}}}e"); sup = node.find(f"{{{M}}}sup")
        return "".join(lin_node(c) for c in e) + "^(" + "".join(lin_node(c) for c in sup) + ")"
    return "".join(lin_node(c) for c in node)

# ==================== p#272 (原#273) ====================
# 显示：…基本不等式 S=KN·«KL≤((KN+KL)»/2)² 取最值。
# w:t纯片段里的「/2)²」紧贴既有oMath之后，非独立式子（是既有oMath的延续「/2)²」）。
# 判定：此「/2)²」是跨oMath的分式/上下标延续，重构会重排既有oMath顺序→违反§5交错序守卫。
# 按「不重排既有oMath、零增量」原则，登记保留。核验结论：p#272的「²」是既有oMath「KL≤((KN+KL)/2)²」的跨块延续，
# 正确形态应在oMath内（m:sSup），属「伴既有oMath的内容级重构」——因m:t层已含/2)²，此处登记知悉不动。
p = paras[272]
disp0 = para_disp(p)
LOG.append("p#272(原#273):「·/2)²」为既有oMath [KL≤((KN+KL)] 的跨块延续（完整式=KL≤((KN+KL)/2)²），w:t层「/2)²」+已有oMath「KL≤((KN+KL)」共同构成一件数学内容；重构需重排既有oMath→按§5交错序守卫与零增量原则登记知悉，不改动。")

# ==================== p#803 (原#804) ====================
# 显示：最后由 «R²=r²+(»半高)² 型勾股关系…
# w:t「半高)²」+ 已有oMath「R²=r²+(」共同构成「R²=r²+(半高)²」。
# 同理：跨块内容级重构，登记知悉。
p = paras[803]
LOG.append("p#803(原#804):「半高)²」为既有oMath [R²=r²+(] 的跨块延续（完整式=R²=r²+(半高)²），登记知悉；不改动。")

# ==================== p#3 (原#4) ====================
# 显示：再对点线距用 «d=√(»|a|²−(a·b/|b|«)²)»、对点面距用…
# w:t「|a|²−(a·b/|b|」夹在两既有oMath之间，与「d=√(」「)²)」共同构成「d=√(|a|²−(a·b/|b|)²)」。
# 此段是唯一带「²」散点且可整体归一的情形，但跨3个既有oMath；重构会重排既有oMath交错序。
# 按§5守卫登记知悉。核验：「|a|²」如需独立可在既有oMath内m:sSup，属内容级重构。
p = paras[3]
LOG.append("p#3(原#4):「|a|²−(a·b/|b|」夹于既有「d=√(」「)²)」两oMath之间，共同构成完整距离公式；重构需重排既有oMath交错序→按§5守卫登记知悉，不改动。")

# ==================== p#555 (原#556) ====================
# 显示：…球半径 «r=√6a»/12；最后由 √3×正方体棱长=2r 解出正方体棱长…（正方体外接球半径«=(√3»/2)×棱长…
# w:t里「√3×正方体棱长=2r」与「√3」是相互独立的散点数学。这些「√3」配文字「正方体棱长=2r」。
# 「√3×正方体棱长=2r」中「√3」是纯w:t、可独立转m:rad(3)；但整句做oMath会让汉字进入公式框→违反§7文字/公式分离。
# 判定：仅「√3」可独立转m:rad(3)（无汉字、纯w:t）。执行转换。
p = paras[555]
disp0 = para_disp(p)
# 收集所有w:t（嵌套）逐节点替换
def convert_in_wt(p, substr, omel):
    for t in list(p.iter(f"{{{W}}}t")):
        if t.text and substr in t.text:
            run = t.getparent()
            idx = t.text.index(substr)
            before, after = t.text[:idx], t.text[idx+len(substr):]
            if before:
                t.text = before; t.set(XMLSP, "preserve")
            else:
                run.remove(t)
            r_after = None
            if after:
                r_after = deepcopy(run)
                ta = r_after.findall(f"{{{W}}}t")
                if ta:
                    ta[0].text = after; ta[0].set(XMLSP, "preserve")
                else:
                    rt = E(f"{{{W}}}t"); rt.text = after; rt.set(XMLSP, "preserve"); r_after.append(rt)
            if r_after is not None:
                run.addnext(omel); omel.addnext(r_after)
            else:
                run.addnext(omel)
            return 1
    return 0
# 逐个「√3」→ m:rad(3)。注意0增量：m:rad「√3」的线性化=「√3」，与原w:t文本「√3」全等。
n = 0
for sub in ["√3"]:
    while True:
        if convert_in_wt(p, sub, om([m_rad([m_r("3")])])) == 1:
            n += 1
        else:
            break
assert n >= 1, f"p#555 转换数不足 n={n}"
assert para_disp(p) == disp0, "p#555 round-trip失败"
# 确认汉字未入公式框（oMath仅含3）
for om_el in p.iter(f"{{{M}}}oMath"):
    assert not any("\u4e00" <= ch <= "\u9fff" for ch in "".join(t.text or "" for t in om_el.iter(f"{{{M}}}t"))), "汉字入公式框"
LOG.append(f"p#555(原#556):「√3」(纯w:t、无汉字) → oMath[m:rad(3)] {n}处；round-trip逐字一致；「√3×正方体棱长=2r」句中「正方体棱长=2r」含汉字不转（§7文字/公式分离）。")

# ==================== p#259 余：「正四面体体积√2 /12」 ====================
# 显示：…高««√2a»/«2»»），正四面体体积√2«a³»/12，共用面…
# w:t「√2」+ 既有oMath[a³] + w:t「/12」构成「√2a³/12」。√2是纯w:t可独立转m:rad(2)。
p = paras[259]
disp0 = para_disp(p)
if "√2" in "".join(t.text or "" for t in p.iter(f"{{{W}}}t")):
    nn = 0
    for sub in ["√2"]:
        while True:
            if convert_in_wt(p, sub, om([m_rad([m_r("2")])])) == 1:
                nn += 1
            else:
                break
    assert nn >= 1, f"p#259 √2 转换不足 {nn}"
    assert para_disp(p) == disp0, "p#259 √2 round-trip失败"
    LOG.append(f"p#259(原#260):「√2」(纯w:t) → oMath[m:rad(2)] {nn}处；「√2a³/12」中a³为既有oMath、保序不动，√2转独立m:rad(2)。round-trip逐字一致。")
else:
    LOG.append("p#259: w:t无√2，跳过。")

doc_bytes = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)

backup = os.path.join(BASE, "C_backup_FX2b_after_task1.docx")
already = os.path.exists(backup)
tmp_out = os.path.join(BASE, "C_new.docx")
replace = {"word/document.xml": doc_bytes}
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = replace.get(item.filename)
        if data is None:
            data = zin.read(item.filename)
        zout.writestr(item, data)
shutil.move(tmp_out, SRC)
print("OK 已写回", SRC)
for line in LOG:
    print(line)
