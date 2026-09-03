# -*- coding: utf-8 -*-
"""FX7 edit I2 part3: 修复part1重建时被扁平化的4个oMath（p#28 x≠0；p#487 e=√2、y=±x；p#867 x²）
原理：把文本run中的该片段切出、包成oMath（m:r裸形态，与既有吸收形态一致），零字符增删。"""
import os, re, zipfile, io, shutil, copy
from lxml import etree

WK = r"C:\提示词\工作区\同步-数学选必1-0903\FX7"
SYNC = r"C:\提示词\高中数学\高中数学同步"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
XMLSPACE = "{http://www.w3.org/XML/1998/namespace}space"
name = "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx"
src = os.path.join(SYNC, name)

z = zipfile.ZipFile(src)
t = etree.parse(io.BytesIO(z.read("word/document.xml")))
root = t.getroot()
ps = list(root.iter(W + "p"))

FIX = {
    28: ["x≠0"],
    487: ["e=√2", "y=±x"],
    867: ["x²"],
}

def wrap_fragment(p, frag):
    """在段落直接子级中找包含frag的文本run，切分为 前+oMath(frag)+后"""
    for r in list(p):
        if r.tag != W + "r":
            continue
        wts = r.findall(W + "t")
        if len(wts) != 1:
            continue
        txt = wts[0].text or ""
        pos = txt.find(frag)
        if pos < 0:
            continue
        before, after = txt[:pos], txt[pos + len(frag):]
        mrpr = r.find(W + "rPr")
        # oMath
        om = etree.Element(M + "oMath")
        mr = etree.SubElement(om, M + "r")
        mt = etree.SubElement(mr, M + "t")
        mt.set(XMLSPACE, "preserve")
        mt.text = frag
        idx = list(p).index(r)
        parts = []
        if before:
            r1 = etree.Element(W + "r")
            if mrpr is not None:
                r1.append(copy.deepcopy(mrpr))
            t1 = etree.SubElement(r1, W + "t")
            t1.set(XMLSPACE, "preserve")
            t1.text = before
            parts.append(r1)
        parts.append(om)
        if after:
            r3 = etree.Element(W + "r")
            if mrpr is not None:
                r3.append(copy.deepcopy(mrpr))
            t3 = etree.SubElement(r3, W + "t")
            t3.set(XMLSPACE, "preserve")
            t3.text = after
            parts.append(r3)
        p.remove(r)
        for k, node in enumerate(parts):
            p.insert(idx + k, node)
        return True
    return False

for pi, frags in FIX.items():
    for f in frags:
        ok = wrap_fragment(ps[pi], f)
        assert ok, f"p#{pi} 未找到扁平片段 {f!r}"
        print(f"p#{pi}: {f!r} 已包回oMath")

# 字符守恒复核（三段全文不变）
def ptext(p):
    return "".join(el.text or "" for el in p.iter() if el.tag in (W + "t", M + "t"))

EXPECT = {
    28: "【编注】 由方向向量n=(x,y)读斜率k=y/x（x≠0）；易错点：x=0时斜率不存在但方向向量仍存在（关联条目：直线的点斜式方程）。",
    487: "【编注】 实虚轴相等的特例、渐近线互相垂直且e=√2；易错点：方程x²−y²=λ（λ≠0）的渐近线恒为y=±x（关联条目：双曲线的几何性质）。",
    867: "【编注】 二次齐次方程除以x²化为关于k=y/x的二次方程，两根即两直线斜率（关联条目：齐次式）。",
}
for pi, exp in EXPECT.items():
    got = ptext(ps[pi])
    assert got == exp, (pi, got)
    print(f"p#{pi} 字符守恒 ✓")

# 全20段最终结构dump（人工过目）
for pi in sorted(list(FIX) + [12, 22, 210, 230, 316, 336, 364, 394, 416, 492, 569, 665, 673, 682, 730, 776, 799, 852]):
    p = ps[pi]
    seq = []
    for c in p:
        ln = etree.QName(c).localname
        if ln == "r":
            txt = "".join(x.text or "" for x in c.iter(W + "t"))
            if txt:
                seq.append("T" + repr(txt[:22]))
        elif ln == "oMath":
            txt = "".join(x.text or "" for x in c.iter(M + "t"))
            seq.append("M" + repr(txt[:22]))
    print(f"p#{pi}: " + " | ".join(seq))

buf = io.BytesIO()
t.write(buf, xml_declaration=True, encoding="UTF-8", standalone=True)
newdoc = buf.getvalue()
tmp = os.path.join(WK, "tmp_pack_I2c.docx")
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = newdoc if item.filename == "word/document.xml" else zin.read(item.filename)
        zout.writestr(item, data)
with zipfile.ZipFile(tmp) as zf:
    assert zf.testzip() is None
shutil.move(tmp, src)
print("I2 repacked (part3)")
