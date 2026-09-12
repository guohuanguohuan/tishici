# 批5a 图探针：讲和练 Q8/Q38/Q52/Q65 元素区间 → media 文件映射＋提取
import os, sys, hashlib, shutil
from docx import Document
from docx.oxml.ns import qn

SRC = r"C:\提示词\高中物理\参考\组卷网\知识图鉴·单元讲练测（2019人教版）\人教版必修第3册\第9章静电场及其应用讲和练.docx"
DST = r"C:\提示词\工作区\_tmpP1成卷0912\批5a\figs"
RANGES = {8: (104, 114), 38: (682, 695), 52: (931, 945), 65: (1125, 1138)}

doc = Document(SRC)
body = doc.element.body
pi = -1
hits = []  # (elem_idx, rid, partname)
for child in body.iterchildren():
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        pi += 1
        for blip in child.iter(qn('a:blip')):
            rid = blip.get(qn('r:embed'))
            if rid:
                hits.append((pi, rid))
    elif tag == 'tbl':
        pi += 1  # 与 dump_docx 计数口径一致（表格占一号）

rels = doc.part.rels
for q, (a, b) in RANGES.items():
    for idx, rid in hits:
        if a <= idx <= b:
            part = rels[rid].target_part
            print('Q%d elem=%d rid=%s -> %s' % (q, idx, rid, part.partname))

# 提取（原样字节，零加工）
os.makedirs(DST, exist_ok=True)
for q, (a, b) in RANGES.items():
    n = 0
    for idx, rid in hits:
        if a <= idx <= b:
            n += 1
            part = rels[rid].target_part
            ext = os.path.splitext(str(part.partname))[1]
            name = '过关%d-图%d%s' % (q, n, ext)
            data = part.blob
            with open(os.path.join(DST, name), 'wb') as f:
                f.write(data)
            print('提取 %s  %d B  md5=%s' % (name, len(data), hashlib.md5(data).hexdigest()))
