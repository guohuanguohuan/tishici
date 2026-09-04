import zipfile, re, sys

files = {
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
for k, f in files.items():
    z = zipfile.ZipFile(f)
    xml = z.read('word/document.xml').decode('utf-8')
    m = list(re.finditer(r'<w:sectPr.*?</w:sectPr>', xml, re.S))[-1]
    print(f'=== {k} 正文级sectPr ===')
    print(m.group(0)[:900].replace('><', '>\n<'))
    rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
    print('--- rels中header/footer相关 ---')
    for r in re.findall(r'<Relationship[^>]+(?:header|footer)[^>]*/>', rels):
        print(' ', r)
    print('--- 包内header/footer件 ---',
          [n for n in z.namelist() if re.search(r'(header|footer)\d*\.xml$', n)])
    st = z.read('word/settings.xml').decode('utf-8') if 'word/settings.xml' in z.namelist() else ''
    print('--- evenAndOddHeaders:', 'evenAndOddHeaders' in st)
    print()
