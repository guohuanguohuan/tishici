import zipfile, re

pieces = {
 'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
 'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
 'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
base = r'C:\提示词\高中数学\高中数学同步\\'
for k, fn in pieces.items():
    xml = zipfile.ZipFile(base + fn).read('word/document.xml').decode('utf-8')
    ms = list(re.finditer(r'<w:sectPr', xml))
    info = []
    for j, m in enumerate(ms[:-1]):
        pre = xml[:m.start()]
        # 找最近的未闭合 <w:pPr>：最后出现的 <w:pPr> 是否晚于最后出现的 </w:pPr>
        wrapped = pre.rfind('<w:pPr>') > pre.rfind('</w:pPr>')
        blk = xml[m.start():xml.find('</w:sectPr>', m.start())]
        pgnum = re.search(r'<w:pgNumType[^/]*/>', blk)
        href = 'H' if 'headerReference' in blk else '-'
        info.append(f"嵌入#{j}@{m.start()/len(xml):.1%} {'pPr内' if wrapped else '★裸body'} refs={href} {pgnum.group(0) if pgnum else ''}")
    body = xml[ms[-1].start():xml.find('</w:sectPr>', ms[-1].start())]
    bhref = 'H/F' if 'headerReference' in body else '-'
    bpg = re.search(r'<w:pgNumType[^/]*/>', body)
    info.append(f"正文级 refs={bhref} {bpg.group(0) if bpg else ''}")
    print(f'{k}: ' + '｜'.join(info))
