# FX2: p#484全文 + tab逐处上下文 + 段尾空格扫描 + 既有m:rad/m:f样式采样 + 创作句线性数学复扫
from lxml import etree
import os, re

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
tree = etree.parse(os.path.join(BASE, "word", "document.xml"))
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

def ptext(p):
    return "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))

print("===== p#484 (A1定位 R=L/√3, r=h/4) =====")
print(ptext(paras[484]))

print("\n===== 创作句（含【编注】）线性数学复扫 =====")
pat = re.compile(r"[√²³⁴]|(?<=[a-zA-Z0-9）)]/[a-zA-Z0-9])")
for i, p in enumerate(paras):
    t = ptext(p)
    if "【编注】" in t and ("√" in t or re.search(r"[a-zA-Z]/[a-zA-Z0-9]", t) or "²" in t or "³" in t):
        print(f"p#{i}: {t[:120]}")

print("\n===== w:tab 全量逐处（段落+每tab前后文） =====")
tab_total = 0
tab_paras = []
for i, p in enumerate(paras):
    tabs = list(p.iter(f"{{{W}}}tab"))
    if not tabs:
        continue
    tab_paras.append(i)
    tab_total += len(tabs)
    # 线性化含tab占位
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            seq.append(node.text or "")
        elif node.tag == f"{{{W}}}tab":
            seq.append("⇥")
        elif node.tag == f"{{{M}}}oMath":
            seq.append("«OMML»")
    lin = "".join(seq)
    print(f"p#{i} tabs={len(tabs)}: {lin[:150]}")
print(f"TOTAL tab-paras={len(tab_paras)} tabs={tab_total}")
print("A1口径31段/88个 → 校:", len(tab_paras), tab_total)

print("\n===== 段尾空格扫描（最后文本元素为w:t且尾随空白） =====")
cnt = 0
for i, p in enumerate(paras):
    # 段内最后一个有文本的元素（w:t）
    ts = [t for t in p.iter(f"{{{W}}}t") if t.text]
    if not ts:
        continue
    last = ts[-1]
    # 是否是段内最后内容（其后无oMath/drawing等）——简化：只查最后一个w:t是否以空白结尾
    import re as _re
    m = _re.search(r"[ \u3000]+$", last.text)
    if m:
        cnt += 1
        print(f"p#{i} 尾随={[hex(ord(c)) for c in last.text[m.start():]]} 文本末30字: ...{last.text[-30:]!r}")
print("段尾空格计数:", cnt)

print("\n===== 既有 m:rad / m:f 样式采样 =====")
rad = body.findall(f".//{{{M}}}rad")
fr = body.findall(f".//{{{M}}}f")
print("m:rad count:", len(rad), " m:f count:", len(fr))
if rad:
    s = etree.tostring(rad[0], pretty_print=True).decode()
    # 去掉ns声明噪音
    s = re.sub(r'xmlns:\w+="[^"]*"', '', s)
    print("--- first m:rad ---"); print(s[:1200])
if fr:
    s = etree.tostring(fr[0], pretty_print=True).decode()
    s = re.sub(r'xmlns:\w+="[^"]*"', '', s)
    print("--- first m:f ---"); print(s[:1200])
