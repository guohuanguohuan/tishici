# FX2: 两个sectPr子元素明细（去命名空间噪音）＋头部节类型＋段[0]完整XML
from lxml import etree
import os

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
tree = etree.parse(os.path.join(BASE, "word", "document.xml"))
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

def dump_sect(sect, label):
    print(f"--- {label} ---")
    for ch in sect:
        q = etree.QName(ch)
        attrs = {etree.QName(k).localname: v for k, v in ch.attrib.items()}
        print(f"  <w:{q.localname}> {attrs}")

sect_head = paras[0].find(f"{{{W}}}pPr/{{{W}}}sectPr")
sect_body = body.find(f"{{{W}}}sectPr")
dump_sect(sect_head, "HEAD sectPr (in p[0])")
dump_sect(sect_body, "BODY-FINAL sectPr")

# 段[0]完整XML（不含sectPr也打印一份去掉sectPr的pPr）
print("\n--- p[0] full XML ---")
print(etree.tostring(paras[0], pretty_print=True).decode()[:6000])
