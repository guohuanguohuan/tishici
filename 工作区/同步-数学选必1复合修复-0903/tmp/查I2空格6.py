import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')
for m in re.finditer(r'<w:t[^>]*>范围</w:t>', xml):
    # 所在行
    t0 = xml.rfind('<w:tr\b', 0, m.start())
    t0 = xml.rfind('<w:tr', 0, m.start())
    t1 = xml.find('</w:tr>', m.start())
    row = xml[t0:t1]
    cells = re.findall(r'<w:tc>.*?</w:tc>', row, re.S)
    txt = []
    for c in cells:
        t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', c))
        mt = ''.join(re.findall(r'<m:t[^>]*>([^<]*)</m:t>', c))
        txt.append((t + ('⟨OMML:' + mt + '⟩' if mt else ''))[:60])
    print(f'pos={m.start()} 行单元格数={len(cells)}: {txt}')
