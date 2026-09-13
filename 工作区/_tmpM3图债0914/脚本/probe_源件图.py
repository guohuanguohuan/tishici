# -*- coding: utf-8 -*-
"""图债工位：源件四卷 docx 对象层摸图。
只读源件；输出 源证/源件摸图.txt（每签名题文的邻近内嵌图判定）＋ 源证/全部内嵌图清单.txt。"""
import io, os, re
from docx import Document
from docx.oxml.ns import qn

SRC = r"C:\提示词\高中数学\高中数学同步"
OUTDIR = r"C:\提示词\工作区\_tmpM3图债0914\源证"
VOLS = {
    "卷①": "人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx",
    "卷②": "人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx",
    "卷③": "人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx",
    "卷④": "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx",
}

# (债键, 卷, 定位签名列表)
DEBTS = [
    ("02-E1",  "卷①", ["嫦娥五号", "国旗制法", "五星的位置"]),
    ("10-G2",  "卷②", ["折痕", "折叠"]),
    ("12-例15", "卷②", ["短轴长", "平面四边形"]),
    ("13-变式16", "卷③", ["猫捉老鼠", "机器鼠"]),
    ("14-例20", "卷③", ["同心圆", "两组同心圆"]),
    ("14-变式34", "卷③", ["第二象限的一个交点"]),
    ("14-例39", "卷③", ["野生保护区"]),
    ("14-例46", "卷③", ["青花瓷", "单叶双曲面"]),
    ("14-变式47", "卷③", ["唐山号", "钓鱼岛"]),
    ("14-变式49", "卷③", ["篮球"]),
    ("14-变式53", "卷③", ["大教堂", "南非"]),
    ("15-例23", "卷③", ["单行隧道", "横断面"]),
    ("16-变式39", "卷③", ["外角平分线"]),
    ("17-拓01", "卷④", ["斜率为 1 的直线", "斜率为1的直线", "弦 AB 的长", "弦AB的长"]),
    ("18-12",  "卷④", ["内切圆的圆心", "以 AB 为直径", "以AB为直径"]),
    ("18-变式15", "卷④", ["上半椭圆"]),
    ("19-变式10", "卷④", ["公共焦点", "第二、四象限的公共点"]),
    ("19-例16", "卷④", ["交曲线", "作直线交"]),
]

def para_images(p):
    """返回该段内嵌图的 (rId, 图片文件名) 列表（对象层：w:drawing/w:pict/w:object→blip）。"""
    out = []
    for blip in p._p.findall(".//" + qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if rid:
            out.append(rid)
    # VML 旧式（w:pict → v:imagedata）
    VML = "{urn:schemas-microsoft-com:vml}imagedata"
    for imd in p._p.findall(".//" + VML):
        rid = imd.get(qn("r:id"))
        if rid:
            out.append(rid)
    # OLE 对象（公式/图）
    for imd in p._p.findall(".//" + qn("w:object")):
        pass
    return out

def para_ole(p):
    return [o for o in p._p.findall(".//" + qn("w:object"))]

report = []
inv = []
for vkey, fn in VOLS.items():
    path = os.path.join(SRC, fn)
    doc = Document(path)
    paras = doc.paragraphs
    # 全卷内嵌图清单
    n_img = 0
    img_rows = []
    for i, p in enumerate(paras):
        rids = para_images(p)
        if rids:
            for rid in rids:
                try:
                    part = doc.part.related_parts[rid]
                    img_rows.append((i, rid, part.partname, len(part.blob)))
                except KeyError:
                    img_rows.append((i, rid, "?", -1))
                n_img += 1
    inv.append(f"### {vkey} {fn}\n段数={len(paras)} 内嵌图={n_img}")
    for r in img_rows:
        inv.append(f"  段{r[0]:5d} {r[1]} {r[2]} {r[3]}B")
    inv.append("")
    # 签名定位
    texts = [p.text for p in paras]
    for dkey, vol, sigs in DEBTS:
        if vol != vkey:
            continue
        hits = []
        for sig in sigs:
            for i, t in enumerate(texts):
                if sig in t:
                    hits.append((i, sig))
        if not hits:
            report.append(f"[{dkey}] {vkey} 未命中签名 {sigs}")
            continue
        seen = set()
        for i, sig in hits:
            if sig in seen:
                continue
            seen.add(sig)
            # 邻域 ±6 段找图/OLE
            near = []
            for j in range(max(0, i - 6), min(len(paras), i + 8)):
                rids = para_images(paras[j])
                ole = para_ole(paras[j])
                if rids or ole:
                    near.append((j, "IMG" if rids else "OLE", rids))
            ctx = texts[i][:60].replace("\n", " ")
            report.append(f"[{dkey}] {vkey} 签名「{sig}」@段{i}：「{ctx}…」 邻域图: {near if near else '无'}")

with io.open(os.path.join(OUTDIR, "源件摸图.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))
with io.open(os.path.join(OUTDIR, "全部内嵌图清单.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(inv))
print("债务判定行：")
print("\n".join(report))
