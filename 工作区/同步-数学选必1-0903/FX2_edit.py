# -*- coding: utf-8 -*-
# FX2主编辑：C件5项修复（原位重打包）。断言失败即中止不落盘。
# 修复1 删文内标题段+sectPr折叠；修复2 页眉页脚品牌前缀；修复3 88处选项tab归一；
# 修复4 段尾空格10处；修复5 两处创作句线性数学转oMath。
import os, re, shutil, zipfile, sys
from lxml import etree
from copy import deepcopy

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XMLSP = "{http://www.w3.org/XML/1998/namespace}space"
LOG = []

def E(tag):
    return etree.Element(tag)

# ---- 预检：原件未被他人改动＋可写 ----
with zipfile.ZipFile(SRC) as z:
    cur_doc = z.read("word/document.xml")
with open(os.path.join(BASE, "word", "document.xml"), "rb") as f:
    orig_doc = f.read()
assert cur_doc == orig_doc, "原件document.xml与解包时不一致（他人改动？中止）"
with open(SRC, "r+b") as f:
    pass  # 可写性探测（被锁则抛错中止）

# ============ 载入 ============
doc = etree.parse(os.path.join(BASE, "word", "document.xml"))
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
assert len(paras) == 1073, f"段数异常 {len(paras)}"

# ============ 修复1：删文内标题段 + sectPr折叠 ============
p0 = paras[0]
t0 = "".join(t.text or "" for t in p0.iter(f"{{{W}}}t"))
assert t0 == "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）", t0
head_sect = p0.find(f"{{{W}}}pPr/{{{W}}}sectPr")
assert head_sect is not None
hdr_ref = head_sect.find(f"{{{W}}}headerReference")
ftr_ref = head_sect.find(f"{{{W}}}footerReference")
pgnum = head_sect.find(f"{{{W}}}pgNumType")
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
assert hdr_ref is not None and hdr_ref.get(f"{{{W}}}type") == "default" and hdr_ref.get(R) == "rId351"
assert ftr_ref is not None and ftr_ref.get(f"{{{W}}}type") == "default" and ftr_ref.get(R) == "rId347"
assert pgnum is not None and pgnum.get(f"{{{W}}}start") == "54"
cols1 = head_sect.find(f"{{{W}}}cols"); assert cols1 is not None and cols1.get(f"{{{W}}}num") == "1"
sect_break_paras = [p for p in paras if p.find(f"{{{W}}}pPr/{{{W}}}sectPr") is not None]
assert len(sect_break_paras) == 1 and sect_break_paras[0] is p0  # 头部节内容仅此一段→折叠

body_sect = body.find(f"{{{W}}}sectPr")
assert body_sect is not None
cols2 = body_sect.find(f"{{{W}}}cols")
assert cols2.get(f"{{{W}}}num") == "2" and cols2.get(f"{{{W}}}space") == "425" and cols2.get(f"{{{W}}}sep") == "1"
assert body_sect.find(f"{{{W}}}headerReference") is None and body_sect.find(f"{{{W}}}footerReference") is None and body_sect.find(f"{{{W}}}pgNumType") is None

def pgpair(s):
    return (dict(s.find(f"{{{W}}}pgSz").attrib), dict(s.find(f"{{{W}}}pgMar").attrib))
assert pgpair(head_sect) == pgpair(body_sect), "pgSz/pgMar不一致"

body_sect.insert(0, ftr_ref)   # 移动（lxml自动从原父移除）
body_sect.insert(0, hdr_ref)   # → [headerReference, footerReference, pgSz, ...]
pgSz = body_sect.find(f"{{{W}}}pgSz")
pgSz.addnext(pgnum)            # → pgSz, pgNumType, cols, docGrid（schema序）
body.remove(p0)
assert len(body.findall(f"{{{W}}}sectPr")) == 1
assert len(body.findall(f".//{{{W}}}p/{{{W}}}pPr/{{{W}}}sectPr")) == 0
assert body.find(f"{{{W}}}sectPr/{{{W}}}headerReference") is not None
assert body.find(f"{{{W}}}sectPr/{{{W}}}footerReference") is not None
assert body.find(f"{{{W}}}sectPr/{{{W}}}pgNumType").get(f"{{{W}}}start") == "54"
paras = body.findall(f"{{{W}}}p")
assert len(paras) == 1072
assert paras[0].findall(f"{{{W}}}r") and "".join(t.text or "" for t in paras[0].iter(f"{{{W}}}t")) == "1.2.5 空间中的距离"
LOG.append("修复1：删除段[0]文内标题「…（下）·讲练件（79题）」（ADC2DA整行底纹+底边框，头部单栏节唯一内容段）；headerReference(rId351)/footerReference(rId347)/pgNumType(start=54)自头部节sectPr并入正文末sectPr（pgSz/pgMar两节一致、cols=2/space=425/sep=1/docGrid保留，type=continuous与cols=1随隔断段消亡）；全文折叠为单一sectPr；新首段=节名锚「1.2.5 空间中的距离」。")

# ============ 修复3：选项分隔tab归一（88处） ============
def inline_seq(p):
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            seq.append(("text", node.text or "", node))
        elif node.tag == f"{{{W}}}tab":
            seq.append(("tab", "", node))
        elif node.tag == f"{{{M}}}oMath":
            seq.append(("math", "", node))
    return seq

def classify(p):
    seq = inline_seq(p)
    out = []
    for k, (kind, txt, el) in enumerate(seq):
        if kind != "tab":
            continue
        before = False
        for j in range(k - 1, -1, -1):
            if seq[j][0] == "math" or (seq[j][0] == "text" and seq[j][1].strip()):
                before = True; break
        if not before:
            out.append((el, "LEAD")); continue
        nx = None
        for j in range(k + 1, len(seq)):
            if seq[j][0] == "math":
                nx = ("math", ""); break
            if seq[j][0] == "text" and seq[j][1].strip():
                nx = ("text", seq[j][1].lstrip()); break
        if nx and (nx[1].startswith("；") or re.match(r"^[ABCD](．|$)", nx[1])):
            out.append((el, "SEP"))
        else:
            out.append((el, "OTHER?"))
    return out

pre = []
for p in paras:
    pre.extend(classify(p))
seps = [x for x in pre if x[1] == "SEP"]
leads = [x for x in pre if x[1] == "LEAD"]
others = [x for x in pre if x[1] == "OTHER?"]
assert len(seps) == 88, f"SEP={len(seps)}"
assert len(others) == 0
sep_para_count = len(set(el.getparent().getparent() for el, _ in seps))
LOG.append(f"修复3预检：全卷w:tab共{len(pre)}处＝选项分隔SEP 88处（{sep_para_count}段，与A1口径31段/88处一致）＋行首缩进LEAD {len(leads)}处（非A1派单项，保留并登记）。")

del_A = del_B = rep_C = 0
ws_absorbed = 0
tab_para_lines = []
for p in paras:
    cls = classify(p)
    if not any(k == "SEP" for _, k in cls):
        continue
    for el, kind in cls:
        if kind != "SEP":
            continue
        seq = inline_seq(p)
        idx = None
        for k2, (kk, tt, e) in enumerate(seq):
            if e is el:
                idx = k2; break
        assert idx is not None
        li = idx - 1; ws_els = []
        while li >= 0 and seq[li][0] == "text" and not seq[li][1].strip():
            ws_els.append(seq[li][2]); li -= 1
        ri = idx + 1
        while ri < len(seq) and seq[ri][0] == "text" and not seq[ri][1].strip():
            ws_els.append(seq[ri][2]); ri += 1
        pv, nx = seq[li], seq[ri]
        pv_txt = pv[1].rstrip() if pv[0] == "text" else ("«math»" if pv[0] == "math" else None)
        nx_txt = nx[1].lstrip() if nx[0] == "text" else ("«math»" if nx[0] == "math" else None)
        assert pv_txt and nx_txt, "SEP邻接异常"
        assert nx_txt.startswith("；") or re.match(r"^[ABCD](．|$)", nx_txt), f"SEP右邻异常 {nx_txt!r}"
        for w_el in ws_els:
            run = w_el.getparent()
            run.remove(w_el)
            content_left = [c for c in run if etree.QName(c).localname not in ("rPr",)]
            if not content_left:
                run.getparent().remove(run)
            ws_absorbed += 1
        prev_semi = pv_txt.endswith("；")
        next_semi = nx_txt.startswith("；")
        if pv[0] == "text":  # 边界防御：去尾随空白（实际数据中为no-op）
            pv[2].text = pv[2].text.rstrip()
            if pv[2].text:
                pv[2].set(XMLSP, "preserve")
        run = el.getparent()
        if prev_semi or next_semi:
            run.remove(el)
            content_left = [c for c in run if etree.QName(c).localname not in ("rPr",)]
            if not content_left:
                run.getparent().remove(run)
            if prev_semi: del_A += 1
            else: del_B += 1
        else:
            if nx[0] == "text":
                nx[2].text = nx[2].text.lstrip()
                if nx[2].text:
                    nx[2].set(XMLSP, "preserve")
            t = E(f"{{{W}}}t"); t.text = "；"
            run.replace(el, t)
            rep_C += 1
    tab_para_lines.append("".join(("«math»" if n[0] == "math" else (n[1] if n[0] == "text" else "⇥")) for n in inline_seq(p)))
assert del_A + del_B + rep_C == 88
LOG.append(f"修复3处置：A型「…；⇥选项」冗余tab删除{del_A}处；B型「内容⇥；…」冗余tab删除{del_B}处；C型无「；」分隔tab→全角「；」{rep_C}处；合计88处；吸收间隔空白only节点{ws_absorbed}个（§7⑥全角标点前后零空格）。")
post = []
for p in paras:
    post.extend(classify(p))
assert not [x for x in post if x[1] in ("SEP", "OTHER?")]
assert len([x for x in post if x[1] == "LEAD"]) == len(leads)
with open(os.path.join(BASE, "tab_paras_after.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(tab_para_lines))

# ============ 修复4：段尾空格清零 ============
def para_tail_ws(p):
    seq = [n for n in p.iter() if n.tag in (f"{{{W}}}t", f"{{{W}}}drawing", f"{{{M}}}oMath")]
    while seq and seq[-1].tag == f"{{{W}}}drawing":
        seq.pop()
    if not seq:
        return None
    last = seq[-1]
    if last.tag != f"{{{W}}}t":
        return None  # 段末为oMath等：非w:t尾随
    if last.text and re.search(r"[ \u3000]+$", last.text):
        return last
    return None

tails = [t for t in (para_tail_ws(p) for p in paras) if t is not None]
assert len(tails) == 10, f"段尾空格预检={len(tails)}"
stripped = []
for t in tails:
    m = re.search(r"[ \u3000]+$", t.text)
    stripped.append(repr(t.text[m.start():]))
    t.text = t.text[:m.start()]
    if t.text:
        t.set(XMLSP, "preserve")
assert not [t for t in (para_tail_ws(p) for p in paras) if t is not None]
LOG.append(f"修复4：真段末元素尾随空格清零10处（全部半角0x20：{', '.join(stripped)}）；【答案】…　【知识点】段内全角空格白名单未触及（仅动段末元素）。")

# ============ 修复5：创作句线性数学转oMath ============
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

def m_f(num_children, den_children):
    f = E(f"{{{M}}}f")
    fPr = E(f"{{{M}}}fPr"); fPr.append(ctrlpr()); f.append(fPr)
    num = E(f"{{{M}}}num")
    for c in num_children: num.append(c)
    den = E(f"{{{M}}}den")
    for c in den_children: den.append(c)
    f.append(num); f.append(den)
    return f

def om(children):
    o = E(f"{{{M}}}oMath")
    for c in children: o.append(c)
    return o

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

def para_full_lin(p):
    s = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            s.append(node.text or "")
        elif node.tag == f"{{{M}}}oMath":
            s.append(lin_node(node))
    return "".join(s)

def replace_in_run(p, substr, omel):
    for r in p.findall(f"{{{W}}}r"):
        ts = r.findall(f"{{{W}}}t")
        if len(ts) != 1 or ts[0].text is None or substr not in ts[0].text:
            continue
        t = ts[0]
        a = t.text.index(substr); b = a + len(substr)
        before, after = t.text[:a], t.text[b:]
        t.text = before
        t.set(XMLSP, "preserve")
        if after:
            r_after = deepcopy(r)
            ta = r_after.findall(f"{{{W}}}t")[0]
            ta.text = after; ta.set(XMLSP, "preserve")
            r.addnext(r_after)
        r.addnext(omel)   # [r(before), oMath, r_after(after)]
        return
    raise AssertionError(f"未找到 {substr!r}")

p65 = paras[64]
lin65 = para_full_lin(p65)
assert "底面边长为√2a，勿当作a代入。" in lin65, "p65定位失败"
replace_in_run(p65, "√2a", om([m_rad([m_r("2")]), m_r("a")]))
assert para_full_lin(p65) == lin65, "p65 round-trip失败"
assert len(list(p65.iter(f"{{{M}}}oMath"))) == 1

p484 = paras[483]
lin484 = para_full_lin(p484)
assert "R=L/√3" in lin484 and "r=h/4" in lin484, "p484定位失败"
replace_in_run(p484, "R=L/√3", om([m_r("R"), m_r("="), m_f([m_r("L")], [m_rad([m_r("3")])])]))
replace_in_run(p484, "r=h/4", om([m_r("r"), m_r("="), m_f([m_r("h")], [m_r("4")])]))
assert para_full_lin(p484) == lin484, "p484 round-trip失败"
assert len(list(p484.iter(f"{{{M}}}oMath"))) == 2
LOG.append("修复5：p#65「√2a」→oMath[m:rad(degHide)=2·a]；p#484「R=L/√3」→oMath[R,=,m:f(L,m:rad3)]与「r=h/4」→oMath[r,=,m:f(h,4)]（m:rad/m:f/m:ctrlPr按本卷既有OMML房型构造，Cambria Math）；两段全线性化round-trip逐字一致，前后文字run的rPr原样深拷贝。")

doc_bytes = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)

# ============ 修复2：页眉页脚前缀 ============
def patch_hf(path):
    t = etree.parse(path)
    ps = t.getroot().findall(f".//{{{W}}}p")
    assert len(ps) == 1, f"{path}段数{len(ps)}"
    p = ps[0]
    first_t = next(p.iter(f"{{{W}}}t"), None)
    assert first_t is not None and first_t.text == "人教B版选必1 第1章 空间向量与立体几何·讲练", repr(first_t.text if first_t is not None else None)
    first_t.text = "羿郭工作室·" + first_t.text
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            seq.append(node.text or "")
        elif node.tag == f"{{{W}}}instrText":
            seq.append("«" + (node.text or "").strip() + "»")
    full = "".join(seq)
    exp = ("羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·讲练（共114页）·本3/共6本　"
           "«STYLEREF \"节名锚\"»1.2.5 空间中的距离　第«PAGE»54页")
    assert full == exp, f"同串不符: {full!r}"
    return etree.tostring(t, xml_declaration=True, encoding="UTF-8", standalone=True)

hdr_bytes = patch_hf(os.path.join(BASE, "word", "header1.xml"))
ftr_bytes = patch_hf(os.path.join(BASE, "word", "footer1.xml"))
LOG.append("修复2：header1.xml/footer1.xml两处首run w:t文本前插「羿郭工作室·」（域结构零触碰：fldChar三段/instrText/PAGE缓存54不动）；补后同串逐字断言通过：「羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·讲练（共114页）·本3/共6本　{STYLEREF节名锚}　第{PAGE}页」。")

# ============ 重打包（原位） ============
backup = os.path.join(BASE, "C_orig_backup.docx")
shutil.copy2(SRC, backup)
tmp_out = os.path.join(BASE, "C_new.docx")
replace = {"word/document.xml": doc_bytes, "word/header1.xml": hdr_bytes, "word/footer1.xml": ftr_bytes}
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
