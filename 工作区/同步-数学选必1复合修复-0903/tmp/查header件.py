import zipfile

for k, f in [('B', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
             ('C', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
             ('H', r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx')]:
    z = zipfile.ZipFile(f)
    h = z.read('word/header1.xml').decode('utf-8')
    print(f'=== {k} header1.xml 长度={len(h)} ===')
    print(h[:600])
    print('...')
    # Content_Types 声明
    ct = z.read('[Content_Types].xml').decode('utf-8')
    print('  header声明:', 'header' in ct, '| footer声明:', 'footer' in ct)
    print()
