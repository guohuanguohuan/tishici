# 批5b 图位映射：各源 docx →（元素序号, 序号内第几张, media 文件名, 像素尺寸, md5）全清单
# 计数口径与 dump_docx.py --index 一致：body 直接子元素 p/tbl 逐个 +1
import os, hashlib, sys
from docx import Document
from docx.oxml.ns import qn
from PIL import Image

SRC = {
    '简单卷': r"C:\提示词\高中物理\高中物理同步\人教版必修3 第9章 静电场及其应用·简单卷（10题）.docx",
    '中档卷': r"C:\提示词\高中物理\高中物理同步\人教版必修3 第9章 静电场及其应用·中档卷（27题）.docx",
    '冲刺卷': r"C:\提示词\高中物理\高中物理同步\人教版必修3 第9章 静电场及其应用·冲刺卷（4题）.docx",
    '讲和练': r"C:\提示词\高中物理\参考\组卷网\知识图鉴·单元讲练测（2019人教版）\人教版必修第3册\第9章静电场及其应用讲和练.docx",
    'g47': r"C:\提示词\高中物理\参考\组卷网\备战高考·107微专题模型精讲精练\8静电场\第47讲库仑力作用下的平衡问题和变速运动问题-2023届高三物理高考复习101微专题模型精讲精练.docx",
    'g48': r"C:\提示词\高中物理\参考\组卷网\备战高考·107微专题模型精讲精练\8静电场\第48讲非点电荷电场强度的叠加及计算的五种方法-2023届高三物理高考复习101微专题模型精讲精练.docx",
    'g49': r"C:\提示词\高中物理\参考\组卷网\备战高考·107微专题模型精讲精练\8静电场\第49讲电场线与等势线（面）的应用-2023届高三物理高考复习101微专题模型精讲精练.docx",
}

out = open(r"C:\提示词\工作区\_tmpP1成卷0912\批5b\_图位映射.txt", 'w', encoding='utf-8')
for tag, path in SRC.items():
    doc = Document(path)
    body = doc.element.body
    rels = doc.part.rels
    pi = -1
    for child in body.iterchildren():
        kind = child.tag.split('}')[-1]
        if kind not in ('p', 'tbl'):
            continue
        pi += 1
        n = 0
        for blip in child.iter(qn('a:blip')):
            rid = blip.get(qn('r:embed'))
            if not rid or rid not in rels:
                continue
            part = rels[rid].target_part
            data = part.blob
            name = str(part.partname).split('/')[-1]
            md5 = hashlib.md5(data).hexdigest()[:8]
            try:
                tmp = os.path.join(r"C:\提示词\工作区\_tmpP1成卷0912\批5b", '_px.tmp')
                open(tmp, 'wb').write(data)
                with Image.open(tmp) as im:
                    w, h = im.size
            except Exception:
                w = h = -1
            n += 1
            out.write(f"{tag}\t[{pi}]\t#{n}\t{name}\t{w}x{h}\t{md5}\n")
out.close()
print('done')
