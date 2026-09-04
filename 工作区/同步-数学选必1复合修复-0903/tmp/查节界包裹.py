import zipfile, re

for k, f in [('B', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
             ('C', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
             ('H', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
             ('E', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
             ('G', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx')]:
    xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')
    ms = list(re.finditer(r'<w:sectPr', xml))
    print(f'=== {k}: sectPr数={len(ms)} ===')
    for j, m in enumerate(ms[:-1]):  # 除正文级外的嵌入sectPr
        pre = xml[max(0, m.start()-120):m.start()]
        wrapped = '<w:pPr>' in pre[-60:] or pre.rstrip().endswith('<w:pPr>')
        print(f'  嵌入#{j} pos={m.start()}({m.start()/len(xml):.2%}) 前120字符尾部: ...{pre[-70:]!r}')
        print(f'    → {"包在pPr内（合法）" if wrapped else "裸插body（非法！）"}')
