# -*- coding: utf-8 -*-
# 只读提取富矿三题（件4-#9、件2-#36、件5-#18）的完整对象层文本
# 方法：全文档 w:p 遍历（含表内段落），OMML 公式按对象读（m:t 全收）；按题号锚点窄读
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn

ROOT = r"C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第2章 直线与圆的方程/"
FILES = {
    "件4": ROOT + "4 直线的方程综合（共23题）.docx",
    "件2": ROOT + "2 直线的倾斜角与斜率（共49题）.docx",
    "件5": ROOT + "5 直线的交点坐标与距离公式（共43题）.docx",
}
TARGETS = {"件4": ("9",), "件2": ("36",), "件5": ("18",)}

def para_text(p):
    """按对象层读段落：w:t 文本 + m:t（OMML公式）+ w:br 换行，全部依序拼接"""
    parts = []
    for node in p._p.iter():
        tag = node.tag
        if tag == qn('w:t') or tag == qn('m:t'):
            parts.append(node.text or '')
        elif tag == qn('w:br'):
            parts.append(' ⏎ ')
    return ''.join(parts)

def dump(fname, qnums, out_path):
    doc = Document(FILES[fname])
    # 全文档段落（含表内）：按文档序
    paras = []
    body = doc.element.body
    for p in body.iter(qn('w:p')):
        paras.append(p)
    texts = [para_text_p := None] * len(paras)
    from docx.text.paragraph import Paragraph
    plist = [Paragraph(p, doc) for p in paras]
    ptexts = [para_text(p) for p in plist]
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"===== {fname} 全段落序号索引（含表内，共{len(ptexts)}段）=====\n")
        # 先输出题号锚点行索引
        f.write("--- 题号锚点行 ---\n")
        for i, t in enumerate(ptexts):
            s = t.strip()
            for q in qnums:
                if s.startswith(f"{q}．") or s.startswith(f"{q}.") or s.startswith(f"新序号：{q}．"):
                    f.write(f"[{i}] {s[:60]}\n")
        f.write("\n")
        # 窄读：题号行起至下一个题号行/【难度】后若干段
        for q in qnums:
            starts = [i for i, t in enumerate(ptexts)
                      if t.strip().startswith(f"{q}．") or t.strip().startswith(f"{q}.")]
            if not starts:
                f.write(f"!!!! {fname} 未找到题号 {q} !!!!\n")
                continue
            s0 = starts[0]
            f.write(f"\n===== {fname} 第{q}题（段{s0}起）=====\n")
            for i in range(s0, min(s0 + 30, len(ptexts))):
                t = ptexts[i]
                # 下题锚即止（从第二段起检测）
                if i > s0:
                    st = t.strip()
                    for qq in range(1, 60):
                        if st.startswith(f"{qq}．") or st.startswith(f"{qq}."):
                            i = len(ptexts)
                            break
                    if i == len(ptexts):
                        break
                f.write(f"[{i}] {t}\n")
            f.write(f"===== {fname} 第{q}题完 =====\n")

for fname, qnums in TARGETS.items():
    dump(fname, qnums, f"{fname}_目标题.txt")
print("done")
