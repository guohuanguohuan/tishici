# -*- coding: utf-8 -*-
# FX2b_edit：C件FX2b修复（原位重打包）。断言失败即中止不落盘。
# 范围：①Task1 创作句线性数学真阳性转oMath（8段中前4段clean单run，其余登记）
#      ②p#223「，；」内容级瑕疵纠错（去尾随全角逗号）
#      ③Task2=请见下一脚本；本脚本专注Task1 clean转换 + p#223内容纠错
import os, re, shutil, zipfile
from lxml import etree
from copy import deepcopy

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XMLSP = "{http://www.w3.org/XML/1998/namespace}space"
LOG = []

def E(tag):
    return etree.Element(tag)

# ---- 预检：原件document.xml未被他人改动 + 可写 ----
with zipfile.ZipFile(SRC) as z:
    cur_doc = z.read("word/document.xml")
with open(os.path.join(BASE, "unpacked", "word", "document.xml"), "rb") as f:
    probe_doc = f.read()
assert cur_doc == probe_doc, "原件document.xml与解包时不一致（他人改动？中止）"

doc = etree.parse(os.path.join(BASE, "unpacked", "word", "document.xml"))
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
assert len(paras) == 1072, f"段数异常 {len(paras)}"

# ---- OMML 建房（同FX2房型：literal √/² 匹配本卷既有oMath风格） ----
def m_r(text):
    r = E(f"{{{M}}}r")
    rpr = E(f"{{{W}}}rPr")
    f = E(f"{{{W}}}rFonts"); f.set(f"{{{W}}}cs", "Cambria Math")
    rpr.append(f); r.append(rpr)
    t = E(f"{{{M}}}t"); t.text = text
    r.append(t)
    return r

def ctrlpr():
    cp = E(f"{{{M}}}ctrlPr")
    rpr = E(f"{{{W}}}rPr")
    f = E(f"{{{W}}}rFonts"); f.set(f"{{{W}}}ascii", "Cambria Math"); f.set(f"{{{W}}}hAnsi", "Cambria Math")
    rpr.append(f); cp.append(rpr)
    return cp

def m_f(num_children, den_children):
    f = E(f"{{{M}}}f")
    fPr = E(f"{{{M}}}fPr"); fPr.append(ctrlpr()); f.append(fPr)
    num = E(f"{{{M}}}num")
    for c in num_children: num.append(c)
    den = E(f"{{{M}}}den")
    for c in den_children: den.append(c)
    f.append(num); f.append(den)
    return f

def m_rad(e_children):
    rad = E(f"{{{M}}}rad")
    radPr = E(f"{{{M}}}radPr")
    dh = E(f"{{{M}}}degHide"); dh.set(f"{{{M}}}val", "1")
    radPr.append(dh); radPr.append(ctrlpr())
    rad.append(radPr); rad.append(E(f"{{{M}}}deg"))
    e = E(f"{{{M}}}e")
    for c in e_children: e.append(c)
    rad.append(e)
    return rad

def om(children):
    o = E(f"{{{M}}}oMath")
    for c in children: o.append(c)
    return o

def para_full_lin(p):
    """显示线性化：w:t + oMath结构化（与round-trip核对基准）"""
    s = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            s.append(node.text or "")
        elif node.tag == f"{{{M}}}oMath":
            s.append(lin_node(node))
    return "".join(s)

def lin_node(node):
    if node.tag == f"{{{M}}}t":
        return node.text or ""
    q = etree.QName(node).localname
    if q == "rad":
        return "√" + "".join(lin_node(c) for c in node.find(f"{{{M}}}e"))
    if q == "f":
        return ("".join(lin_node(c) for c in node.find(f"{{{M}}}num")) + "/" +
                "".join(lin_node(c) for c in node.find(f"{{{M}}}den")))
    return "".join(lin_node(c) for c in node)

def convert_once(p, substr, omel):
    """在p内任一w:t节点中替换substr为oMath：为 run(before), oMath, run_after(after) 三兄弟。
       处理嵌套run（w:t在w:r内）。返回替换次数。"""
    for t in list(p.iter(f"{{{W}}}t")):
        if t.text and substr in t.text:
            run = t.getparent()
            assert run is not None and etree.QName(run).localname == "r", "w:t父非r"
            idx = t.text.index(substr)
            before, after = t.text[:idx], t.text[idx + len(substr):]
            # 原run的w:t置为before
            if before:
                t.text = before
                t.set(XMLSP, "preserve")
            else:
                run.remove(t)
            # 建 after-run（深拷贝run共享rPr）
            if after:
                r_after = deepcopy(run)
                # deepcopy出run的w:t（可能是before）；替换为after
                ta = r_after.findall(f"{{{W}}}t")
                if ta:
                    ta[0].text = after; ta[0].set(XMLSP, "preserve")
                else:
                    rt = E(f"{{{W}}}t"); rt.text = after; rt.set(XMLSP, "preserve")
                    r_after.append(rt)
            else:
                r_after = None
            # 插入 omel 与 r_after
            if r_after is not None:
                run.addnext(omel)
                omel.addnext(r_after)
            else:
                run.addnext(omel)
            return 1
    return 0

# ============ Task1：创作句线性数学转oMath（clean单run转换段） ============
# 判定：仅在w:t层（非m:t）含√/² 连缀表达式 => 真阳性。
# 本脚本处理4段clean单run转换；其余4段需跨run重建（另登记）。

# --- p#259 (原#260): 「√2a/2」 → m:f(√2a, 2) ---
p = paras[259]
lin0 = para_full_lin(p)
assert "、高√2a/2）" in lin0 and "√2a/2" in para_full_lin(p)
assert convert_once(p, "√2a/2", om([m_f([m_r("√2a")], [m_r("2")])])) == 1
assert para_full_lin(p) == lin0, "p#259 round-trip失败"
assert "√2a/2" not in "".join(t.text or "" for t in p.iter(f"{{{W}}}t")), "p#259 w:t残留√2a/2"
LOG.append("p#259(原#260):「√2a/2」(w:t层线性数学真阳性) → oMath[m:f(√2a,2)]；全线性化round-trip逐字一致；「√2a³/12」(跨run重建)登记待下轮。")

# --- p#363 (原#364): 「√2/2」 → m:f(√2, 2) ---
p = paras[363]
lin0 = para_full_lin(p)
assert "面积为√2/2勿误½" in lin0
assert convert_once(p, "√2/2", om([m_f([m_r("√2")], [m_r("2")])])) == 1
assert para_full_lin(p) == lin0, "p#363 round-trip失败"
assert "√2/2" not in "".join(t.text or "" for t in p.iter(f"{{{W}}}t")), "p#363 w:t残留√2/2"
LOG.append("p#363(原#364):「√2/2」→ oMath[m:f(√2,2)]；round-trip逐字一致。")

# --- p#479 (原#480): 「√3/6」「√3/3」两个 → m:f(√3,6)/m:f(√3,3) ---
p = paras[479]
lin0 = para_full_lin(p)
assert "内切圆半径系数√3/6，勿误作√3/3" in lin0
assert convert_once(p, "√3/6", om([m_f([m_r("√3")], [m_r("6")])])) == 1
assert convert_once(p, "√3/3", om([m_f([m_r("√3")], [m_r("3")])])) == 1
assert para_full_lin(p) == lin0, "p#479 round-trip失败"
rest = "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
assert "√3/6" not in rest and "√3/3" not in rest, "p#479 w:t残留√3/x"
LOG.append("p#479(原#480):「√3/6」「√3/3」→ oMath[m:f(√3,6)]/[m:f(√3,3)]；round-trip逐字一致。")

# --- p#492 (原#493): 「√3a/3=h/2」 → m:f(√3a,3)=m:f(h,2) ---
p = paras[492]
lin0 = para_full_lin(p)
assert "（当 √3a/3=h/2）" in lin0
assert convert_once(p, "√3a/3=h/2", om([m_f([m_r("√3a")], [m_r("3")]), m_r("="), m_f([m_r("h")], [m_r("2")])])) == 1
assert para_full_lin(p) == lin0, "p#492 round-trip失败"
assert "√3a/3=h/2" not in "".join(t.text or "" for t in p.iter(f"{{{W}}}t")), "p#492 w:t残留√3a/3=h/2"
LOG.append("p#492(原#493):「√3a/3=h/2」→ oMath[m:f(√3a,3),=,m:f(h,2)]；round-trip逐字一致。")

# ============ 内容级瑕疵核验（无需纠错） ============
# p#223(原224): wt层「°，；」仅因oMath被排除而相邻；显示层为「cos60°，«R=√(OE²+BE²)»；易错」——「，」与「；」被oMath隔开，非实标点缺陷。核验：不需纠错。
# p#436(原437): wt层「(h−1)/；」显示层「(h−1)/«√(h²+9)»；」——分数完整为(h-1)/√(h²+9)，非截断。核验：不需纠错。
LOG.append("内容级瑕疵核验：p#223(原224)「，；」与p#436(原437)「(h−1)/」均系w:t层假象（oMath被层提取排除导致相邻），显示层有oMath间隔、非真实缺陷——按§5核验结论：不改动。")

doc_bytes = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)

# ============ 重打包（原位） ============
backup = os.path.join(BASE, "C_backup_FX2b_after_task1.docx")
if not os.path.exists(backup):
    shutil.copy2(SRC, backup)
tmp_out = os.path.join(BASE, "C_new.docx")
replace = {"word/document.xml": doc_bytes}
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = replace.get(item.filename)
        if data is None:
            data = zin.read(item.filename)
        zout.writestr(item, data)
shutil.move(tmp_out, SRC)
print("OK 已写回原件:", SRC)
print("backup:", backup)
for line in LOG:
    print(line)
