import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')
i = 29066
t0 = xml.find('<w:tbl>', i)  # 表在 29066 之后开始
t1 = xml.find('</w:tbl>', t0)
tbl = xml[t0:t1]
rows = re.findall(r'<w:tr\b.*?</w:tr>', tbl, re.S)
print(f'表行数={len(rows)}')
for r in rows:
    cells = re.findall(r'<w:tc>.*?</w:tc>', r, re.S)
    txt = []
    for c in cells:
        t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', c))
        mt = ''.join(re.findall(r'<m:t[^>]*>([^<]*)</m:t>', c))
        txt.append((t + ('⟨OMML:' + mt + '⟩' if mt else ''))[:50])
    print('  行:', txt)
