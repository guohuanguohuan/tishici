# FX2精查：①tab分类（LEAD/SEP）精确计数 ②真段末元素尾随空格 ③创作句全线性化（w:t+m:t分列）线性数学定位
from lxml import etree
import os, re

BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
tree = etree.parse(os.path.join(BASE, "word", "document.xml"))
body = tree.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")

# ---------- ① tab分类 ----------
# 段内inline序列：[(kind, text/None, element)] kind in {'text','tab','math'}
def inline_seq(p):
    seq = []
    for r in p.iter():
        if r.tag == f"{{{W}}}t":
            seq.append(("text", r.text or "", r))
        elif r.tag == f"{{{W}}}tab":
            seq.append(("tab", None, r))
        elif r.tag == f"{{{M}}}oMath":
            # oMath整体计一项（其m:t不再单列——iter会走到，需排除）
            seq.append(("math", None, r))
    return seq

def classify_tabs():
    sep_list, lead_list, other_list = [], [], []
    for i, p in enumerate(paras):
        # 重新遍历：iter会把oMath内m:t漏进W:t? 不会——m:t在M ns。但w:t在oMath内? 不存在。
        seq = []
        for node in p.iter():
            if node.tag == f"{{{W}}}t":
                seq.append(("text", node.text or "", node))
            elif node.tag == f"{{{W}}}tab":
                seq.append(("tab", "", node))
            elif node.tag == f"{{{M}}}oMath":
                seq.append(("math", "", node))
        # 逐tab分类
        for k, (kind, _, el) in enumerate(seq):
            if kind != "tab":
                continue
            # 向前找最近有效内容（非空白text、math）
            before = False
            for j in range(k - 1, -1, -1):
                if seq[j][0] == "math":
                    before = True; break
                if seq[j][0] == "text" and seq[j][1].strip():
                    before = True; break
            # 向后找最近有效内容文本
            after_txt = None
            for j in range(k + 1, len(seq)):
                if seq[j][0] == "math":
                    after_txt = "«math»"; break
                if seq[j][0] == "text" and seq[j][1].strip():
                    after_txt = seq[j][1].lstrip(); break
            prev_txt = None
            for j in range(k - 1, -1, -1):
                if seq[j][0] == "math":
                    prev_txt = "«math»"; break
                if seq[j][0] == "text" and seq[j][1].strip():
                    prev_txt = seq[j][1].rstrip(); break
            if not before:
                lead_list.append((i, el))
            elif after_txt and re.match(r"^[ABCD]．", after_txt):
                sep_list.append((i, el, prev_txt[-6:] if prev_txt else "", after_txt[:4]))
            else:
                other_list.append((i, prev_txt[-8:] if prev_txt else "", (after_txt or "")[:8]))
    return sep_list, lead_list, other_list

sep, lead, other = classify_tabs()
print(f"SEP tabs={len(sep)} in {len(set(x[0] for x in sep))} paras")
print(f"LEAD tabs={len(lead)} in {len(set(x[0] for x in lead))} paras")
print(f"OTHER tabs={len(other)}")
for i, pv, nx in other:
    print(f"  OTHER p#{i} prev=…{pv!r} next={nx!r}")
print("SEP明细（段号×每段数）:")
from collections import Counter
c = Counter(x[0] for x in sep)
print(dict(sorted(c.items())))

# SEP中「；」邻接细分
# 对每个sep tab取前后紧邻字符（含空格跳过前的原始串）
print("\nSEP上下文明细:")
for i, el, pv, nx in sep:
    print(f"  p#{i} prev=…{pv!r} next={nx!r}")

# ---------- ② 真段末元素尾随空格 ----------
print("\n===== 真段末尾随空格 =====")
cnt = 0
for i, p in enumerate(paras):
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            seq.append(("text", node))
        elif node.tag == f"{{{W}}}tab":
            seq.append(("tab", node))
        elif node.tag == f"{{{M}}}oMath":
            seq.append(("math", node))
        elif node.tag == f"{{{W}}}drawing":
            seq.append(("draw", node))
    # 去掉末尾的tab/draw
    while seq and seq[-1][0] in ("tab", "draw"):
        seq.pop()
    if not seq:
        continue
    k, el = seq[-1]
    if k == "text" and el.text and re.search(r"[ \u3000]+$", el.text):
        m = re.search(r"[ \u3000]+$", el.text)
        cnt += 1
        print(f"  p#{i} 末元素w:t 尾随={el.text[m.start():]!r} …{el.text[-25:]!r}")
    elif k == "math":
        # 段末为oMath：无w:t尾随（不属本项）
        pass
print("真段末尾随空格计数:", cnt)

# ---------- ③ 创作句（【编注】段）全线性化，w:t中含数学签名 ----------
print("\n===== 创作句w:t线性数学（√/²/³/字母斜杠/上下标字符） =====")
sig = re.compile(r"√|[²³⁰¹⁴-⁹]|[a-zA-Z0-9）)]\s*/\s*[a-zA-Z0-9(]|=[a-zA-Z]")
for i, p in enumerate(paras):
    full_w = ""
    has_bianzhu = False
    math_t = ""
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            full_w += node.text or ""
        elif node.tag == f"{{{M}}}t":
            math_t += node.text or ""
    if "【编注】" in full_w:
        # 只看w:t里的签名
        for mm in sig.finditer(full_w):
            s = max(0, mm.start() - 12)
            print(f"  p#{i} w:t线性: …{full_w[s:mm.end()+12]}…")
        if not sig.search(full_w):
            pass
print("（同段m:t内容参照——用于判断数学是否已入公式框）")
