import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')
ms = list(re.finditer(r'<w:sectPr', xml))
i = ms[0].start()
print('=== C 嵌入sectPr 前1500字符（原始）===')
print(xml[max(0, i-1500):i])
print()
print('=== 该sectPr本体 ===')
j = xml.find('</w:sectPr>', i)
print(xml[i:j+11])
# 统计 revision 标记
print()
print('全文 w:ins 数:', xml.count('<w:ins '), '｜w:del 数:', xml.count('<w:del '), '｜sdt 数:', xml.count('<w:sdt>'))
