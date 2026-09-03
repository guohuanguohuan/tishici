# -*- coding: utf-8 -*-
# FX2b_edit3：Task2 选项分隔归一。命名空间正确：distinguish w:t vs m:t。稳定锚点、两阶段收集→执行。
# 归一目标：选项区「X．值；X．值；X．值；X．值」（X=A/B/C/D）。
# 操作：①「X．；」(同run '．；' 文本) →「X．」去杂散分号（改w:t text）
#      ②值后空格w:t（下一下一 token 是字母）→「；」
#      ③值后缺分隔（值后 token 直接是下一字母）→在字母rpr之前插独立「；」run
import os, re, shutil, zipfile
from lxml import etree

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2b_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XMLSP = "{http://www.w3.org/XML/1998/namespace}space"
LOG = []
def E(tag): return etree.Element(tag)

with zipfile.ZipFile(SRC) as z:
    cur_doc = z.read("word/document.xml")
with open(os.path.join(BASE, "unpacked4", "document.xml"), "rb") as f:
    probe_doc = f.read()
assert cur_doc == probe_doc, "原件document.xml与快照不一致（他人改动？中止）"
doc = etree.parse(os.path.join(BASE, "unpacked4", "document.xml"))
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
assert len(paras) == 1072

def om_lin(node):
    if node.tag == f"{{{M}}}t": return node.text or ""
    q = etree.QName(node).localname
    if q == "rad": return "√(" + "".join(om_lin(c) for c in node.find(f"{{{M}}}e")) + ")"
    if q == "f": return ("«" + "".join(om_lin(c) for c in node.find(f"{{{M}}}num")) + "»/«" +
                         "".join(om_lin(c) for c in node.find(f"{{{M}}}den")) + "»")
    if q == "d": return "(" + "".join(om_lin(c) for c in node.findall(f"{{{M}}}e")) + ")"
    return "".join(om_lin(c) for c in node)

def collect(p):
    """命名空间正确的token收集：仅w:t与m:oMath与w:tab。"""
    seq = []
    for node in p.iter():
        tag = node.tag
        if tag == f"{{{W}}}t":
            seq.append(("t", node.text or "", node))
        elif tag == f"{{{M}}}oMath":
            seq.append(("m", om_lin(node), node))
        elif tag == f"{{{W}}}tab":
            seq.append(("tab", "", node))
    return seq

def para_disp(p):
    return ''.join(('«'+t+'»' if k=='m' else t) for k,t,el in collect(p))

def set_txt(t, s):
    t.text = s
    if s:
        t.set(XMLSP, "preserve")

def make_semi_run():
    r = E(f"{{{W}}}r")
    t = E(f"{{{W}}}t"); t.text = "；"; t.set(XMLSP, "preserve")
    r.append(t)
    return r

def normalize_opt(p):
    seq = collect(p)
    a_idx = None
    for i, (k, tx, el) in enumerate(seq):
        if k == "t" and tx == "A":
            a_idx = i; break
    if a_idx is None:
        return (False, 0, "无A")
    n = len(seq)
    letter_map = ["A","B","C","D"]
    changed = 0
    cur = a_idx
    for li in range(4):
        letter = letter_map[li]
        if cur >= n or seq[cur][0] != "t" or seq[cur][1] != letter:
            return (False, changed, "字母%s缺失@%d" % (letter, cur))
        cur += 1
        # 'X．' 或 'X．；'
        if cur < n and seq[cur][0] == "t" and seq[cur][1].startswith("．"):
            dot_tx = seq[cur][1]
            dot_el = seq[cur][2]
            if dot_tx == "．；":
                set_txt(dot_el, "．"); changed += 1
                seq[cur] = ("t", "．", dot_el)
            elif dot_tx != "．":
                # '．数值' 或其它 —— 不动（保守跳过），继续
                pass
            cur += 1
        # 值区
        val_end = cur
        while val_end < n:
            kk, tt, ee = seq[val_end]
            if kk == "t" and tt in ("；", "B", "C", "D"):
                break
            val_end += 1
        # 值后分隔
        if li < 3:
            if val_end < n:
                nxt_k, nxt_t, nxt_el = seq[val_end]
                if nxt_k == "t" and nxt_t in ("B","C","D"):
                    # 缺分隔：在字母run之前插 '；' run
                    parent_r = nxt_el.getparent()   # w:r
                    grp = parent_r.getparent()      # w:p
                    grp.insert(list(grp).index(parent_r), make_semi_run())
                    changed += 1
                elif nxt_k == "t" and nxt_t == "；":
                    # 检查分隔前是否有空格t（全角标点前零空格）——空格t在其前
                    # 空格在分隔前一个token（值-oMath与'；'之间不应有空格t）
                    # 若 val_end的前一token是空格t，则删掉
                    if val_end - 1 >= 0 and seq[val_end-1][0] == "t" and seq[val_end-1][1].strip() == "":
                        sp_el = seq[val_end-1][2]
                        sp_run = sp_el.getparent()
                        sp_run.remove(sp_el)
                        content_left = [c for c in sp_run if etree.QName(c).localname not in ("rPr",)]
                        if not content_left:
                            sp_run.getparent().remove(sp_run)
                        changed += 1
                    pass
                elif nxt_k == "t" and nxt_t.strip() == "":
                    set_txt(nxt_el, "；"); changed += 1
                else:
                    pass
                cur = val_end + (1 if (nxt_k=="t" and nxt_t=="；") else 0)
            else:
                cur = val_end
        else:
            cur = val_end
    return (True, changed, "")

TARGETS = [266, 273, 281, 297, 804, 1037]
for idx in TARGETS:
    p = paras[idx]
    disp0 = para_disp(p)
    ok, changed, msg = normalize_opt(p)
    disp1 = para_disp(p)
    LOG.append(f"p#{idx}: ok={ok} changed={changed} {msg}")
    LOG.append(f"    前置=«{disp0[-70:]}»")
    LOG.append(f"    后置=«{disp1[-70:]}»")

# 校验：同一w:t run内真杂散 'X．；' 残留
print("=== 校验：同w:t run内含「．；」的真杂散残留 ===")
bad = 0
for i, p in enumerate(paras):
    for t in p.iter(f"{{{W}}}t"):
        if t.text and "．；" in t.text:
            bad += 1
            print(f"  p#{i}: «{t.text}»")
            break
print("残留段数:", bad)

doc_bytes = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
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
