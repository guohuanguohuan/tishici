# FX2: 探查header1/footer1结构 + p#65/p#484创作句 + 选项行tab + 段尾空格（原索引口径）
from lxml import etree
import os, re

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

for part in ("header1", "footer1"):
    t = etree.parse(os.path.join(BASE, "word", part + ".xml"))
    root = t.getroot()
    print(f"===== {part}.xml =====")
    for p in root.iter(f"{{{W}}}p"):
        # 段落线性化：w:t文本 + tab/br占位 + 域指令占位
        seq = []
        for node in p.iter():
            q = etree.QName(node).localname
            ns = node.tag
            if ns == f"{{{W}}}t":
                seq.append(node.text or "")
            elif ns == f"{{{W}}}tab":
                seq.append("<TAB>")
            elif ns == f"{{{W}}}instrText":
                seq.append("«" + (node.text or "") + "»")
            elif ns == f"{{{M}}}t":
                seq.append("«math:" + (node.text or "") + "»")
        print("PARA:", "".join(seq))
        print("--- run/w:t elements in order:")
        for r in p.findall(f"{{{W}}}r"):
            rpr = r.find(f"{{{W}}}rPr")
            info = []
            if rpr is not None:
                for e in rpr:
                    info.append(etree.QName(e).localname)
            for e in r:
                eq = etree.QName(e).localname
                if eq == "t":
                    print(f"  RUN[{','.join(info)}] t: {e.text!r}")
                elif eq == "tab":
                    print(f"  RUN[{','.join(info)}] TAB")
                elif eq == "fldChar":
                    print(f"  RUN[{','.join(info)}] fldChar:{e.get(f'{{{W}}}fldCharType')}")
                elif eq == "instrText":
                    print(f"  RUN[{','.join(info)}] instr:{e.text!r}")
        break  # 只看第一段（应只有一段）

# ---------- document.xml ----------
tree = etree.parse(os.path.join(BASE, "word", "document.xml"))
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

def ptext(p):
    return "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))

print("\n===== p#65 (A1定位 √2a) =====")
print(ptext(paras[65]))
print("XML:")
print(etree.tostring(paras[65], pretty_print=True).decode()[:4000])
