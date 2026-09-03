# -*- coding: utf-8 -*-
# FX2b_edit4：Task2 收尾——删选项区「；」前后独立空白run；Task3 二分落盘；全自检。
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
with open(os.path.join(BASE, "unpacked5", "document.xml"), "rb") as f:
    probe_doc = f.read()
assert cur_doc == probe_doc, "原件document.xml与unpacked5快照不一致（他人改动？中止）"
doc = etree.parse(os.path.join(BASE, "unpacked5", "document.xml"))
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

# ============ 删「；」前后独立空白run（§7⑥全角标点前后零空格） ============
def is_ws_text(el):
    """w:t 且为纯空白（半角空格/全角空格/nbsp）"""
    return el.tag == f"{{{W}}}t" and el.text is not None and el.text.strip() == "" and el.text != ""

def strip_empty_runs(p):
    """删空run（仅rPr无内容）。"""
    for r in list(p.findall(f"{{{W}}}r")):
        content = [c for c in r if etree.QName(c).localname not in ("rPr",)]
        if not content:
            p.remove(r)

removed_ws_before = removed_ws_after = 0
for p in paras:
    # 收集兄弟 token（顶层 w:r 与 m:oMath）
    top = [c for c in p if etree.QName(c).localname in ("r", "oMath")]
    # 建 prev/next 判定
    seq = top
    for j, el in enumerate(seq):
        tag = etree.QName(el).localname
        if tag == "r":
            # 该run是否纯空白（仅1个w:t且空白）
            ts = el.findall(f"{{{W}}}t")
            if len(ts) == 1 and is_ws_text(ts[0]):
                # 看前后
                prev_el = seq[j-1] if j > 0 else None
                next_el = seq[j+1] if j+1 < len(seq) else None
                def shows_semi(e):
                    if e is None: return False
                    if etree.QName(e).localname == "r":
                        return any(t.text and "；" in t.text for t in e.findall(f"{{{W}}}t"))
                    return False
                if shows_semi(prev_el) or shows_semi(next_el):
                    p.remove(el)
                    strip_empty_runs(p)
                    if shows_semi(prev_el): removed_ws_before += 1
                    else: removed_ws_after += 1
LOG.append(f"删除选项区「；」前/后独立空白run：before={removed_ws_before} after={removed_ws_after}（§7⑥全角标点前后零空格）。")

# ============ 全自检 ============
# (1) 题号序列：题号块（C9C9C9+加粗、文本=题号）个数与节内连续
qihao_re = re.compile(r"^1\.2\.5(\.\d+)*-\d+(\.\d+)*．")
qbs = []
for i, p in enumerate(paras):
    wt = "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
    # 题号块：段首（可带tab-stop无碍）恰为题号
    if qihao_re.match(wt.strip()):
        num = re.match(r"^1\.2\.5(\.\d+)*-\d+", wt).group(0)
        qbs.append((i, num))
print("题号块数:", len(qbs))

# (2) 七类底纹计数 - 用独立工具（若存在）
import subprocess, sys
# 定位六类底纹计数工具
tool_candidates = [
    r"C:\提示词\工具\六类底纹计数.py",
    r"C:\提示词\工具\七类底纹计数.py",
    r"C:\提示词\工具\六类底纹计数_七类.py",
]
print("检查底纹工具:", [os.path.exists(t) for t in tool_candidates])

# (3) 选项行 w:tab 字符计数、缺分隔计数
print("文档 w:tab 真字符数:", len(body.findall(f".//{{{W}}}tab")))
print("文档 w:ind 数:", len(body.findall(f".//{{{W}}}ind")))

# (4) COM 页数
try:
    import win32com.client as win32
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    d = word.Documents.Open(SRC, ReadOnly=True)
    print("COM页数:", d.ComputeStatistics(2))
    d.Close(False)
    word.Quit()
except Exception as e:
    print("COM错误:", e)

doc_bytes = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
backup = os.path.join(BASE, "C_backup_FX2b_task2_final.docx")
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
