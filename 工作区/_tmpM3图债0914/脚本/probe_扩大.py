# -*- coding: utf-8 -*-
"""图债工位：扩大搜索——4 卷 + 组卷网模块8 全部 docx 中找未命中债题的源段落与邻图。"""
import io, os, glob
from docx import Document
from docx.oxml.ns import qn

OUTDIR = r"C:\提示词\工作区\_tmpM3图债0914\源证"
SRC = r"C:\提示词\高中数学\高中数学同步"
VOLS = [
    ("卷①", "人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx"),
    ("卷②", "人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx"),
    ("卷③", "人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx"),
    ("卷④", "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx"),
]
M8 = sorted(glob.glob(r"C:\提示词\高中数学\参考\组卷网\高中数学解题大招（二级结论）荟萃\04_原始资料\模块8解析几何\*.docx"))

# 未命中债题：宽签名
WIDE = [
    ("13-变式16", ["猫", "机器鼠", "机器猫"]),
    ("14-例20",  ["同心圆", "半径分别是"]),
    ("14-例46",  ["青花瓷", "花瓶", "双曲面"]),
    ("14-变式47", ["唐山", "石家庄号", "邯郸"]),
    ("14-变式49", ["篮球"]),
    ("14-变式53", ["教堂", "南非"]),
    ("15-例23",  ["隧道", "集装箱", "卡车"]),
    ("18-12",    ["ty+1", "t y + 1", "内切圆"]),
    ("18-变式15", ["连接而成", "上半椭圆"]),
    ("19-变式10", ["公共焦点", "离心率之积"]),
    ("19-例16",  ["2p1x", "2p₁x", "-2px", "交曲线C"]),
]

VML = "{urn:schemas-microsoft-com:vml}imagedata"

def para_images(p):
    out = []
    for blip in p._p.findall(".//" + qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if rid:
            out.append(rid)
    for imd in p._p.findall(".//" + VML):
        rid = imd.get(qn("r:id"))
        if rid:
            out.append(rid)
    return out

files = [("四卷/" + k, os.path.join(SRC, v)) for k, v in VOLS] + \
        [("模块8/" + os.path.basename(p), p) for p in M8]

report = []
for label, path in files:
    try:
        doc = Document(path)
    except Exception as e:
        report.append(f"!! {label} 打不开: {e}")
        continue
    paras = doc.paragraphs
    texts = [p.text for p in paras]
    for dkey, sigs in WIDE:
        for sig in sigs:
            for i, t in enumerate(texts):
                if sig in t:
                    near = []
                    for j in range(max(0, i - 4), min(len(paras), i + 6)):
                        rids = para_images(paras[j])
                        if rids:
                            near.append((j, rids))
                    ctx = t[:70].replace("\n", " ")
                    report.append(f"[{dkey}] {label} 「{sig}」@段{i}：「{ctx}…」 邻图:{near if near else '无'}")

with io.open(os.path.join(OUTDIR, "扩大搜索.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print(len(report), "行")
for line in report:
    print(line)
