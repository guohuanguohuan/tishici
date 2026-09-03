# FX2: p#484完整run结构 + p#65/p#484 oMath计数确认 + SEP tab所在run的rPr与邻接空格 + 段[0]有无书签
from lxml import etree
import os

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
tree = etree.parse(os.path.join(BASE, "word", "document.xml"))
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

for idx in (484, 65):
    p = paras[idx]
    n_omath = len(list(p.iter(f"{{{M}}}oMath")))
    print(f"===== p#{idx} oMath数={n_omath} =====")
    for r in p.findall(f"{{{W}}}r"):
        rpr = r.find(f"{{{W}}}rPr")
        shd = rpr.find(f"{{{W}}}shd") if rpr is not None else None
        txts = [t.text for t in r.findall(f"{{{W}}}t")]
        mark = f" SHD={shd.get(f'{{{W}}}fill')}" if shd is not None else ""
        if txts:
            print(f"  RUN{mark}: {txts}")
    if idx == 484:
        print("  -- raw XML --")
        s = etree.tostring(p, pretty_print=True).decode()
        import re as _re
        s = _re.sub(r'xmlns:\w+="[^"]*"', '', s)
        print(s[:3500])

# 段[0]书签/其他元素检查
p0 = paras[0]
print("===== 段[0] 子元素 =====")
for ch in p0:
    print(" ", etree.QName(ch).localname)
print("bookmarkStart in p0:", len(list(p0.iter(f"{{{W}}}bookmarkStart"))))
# 全文bookmark中是否有引用段0位置的书签（bookmarks按名字配对即可，删段不影响name配对除非唯一实例在段0）
bk0 = [(b.get(f"{{{W}}}name"), b.get(f"{{{W}}}id")) for b in p0.iter(f"{{{W}}}bookmarkStart")]
print("段0 bookmarkStart:", bk0)

# SEP tab邻接空格检查（p#362等）
print("\n===== SEP tab所在run上下文（前run末字符/后run首字符） =====")
import re
def seq_of(p):
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            seq.append(("text", node.text or "", node))
        elif node.tag == f"{{{W}}}tab":
            seq.append(("tab", "", node))
        elif node.tag == f"{{{M}}}oMath":
            seq.append(("math", "", node))
    return seq

targets = (362, 267, 274, 282, 298, 805, 1038, 625, 1066, 72, 129)
for i in targets:
    p = paras[i]
    seq = seq_of(p)
    for k, (kind, txt, el) in enumerate(seq):
        if kind != "tab":
            continue
        # 前后最近text（原始、不strip）
        pv = None
        for j in range(k-1, -1, -1):
            if seq[j][0] == "math": pv = "«math»"; break
            if seq[j][0] == "text" and seq[j][1].strip(): pv = repr(seq[j][1][-4:]); break
        nx = None
        for j in range(k+1, len(seq)):
            if seq[j][0] == "math": nx = "«math»"; break
            if seq[j][0] == "text" and seq[j][1].strip(): nx = repr(seq[j][1][:4]); break
        # 该tab是否段首（前无内容）
        lead = pv is None
        if not lead:
            print(f"  p#{i} tab: prev={pv} next={nx}")
