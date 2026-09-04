import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')
seg = xml[72073:72073+4000]
ms = list(re.finditer(r'<m:acc>.*?</m:acc>', seg, re.S))
for j in (0, 2, 4):
    print(f'===== acc#{j} 原文 =====')
    print(ms[j].group(0).replace('><', '>\n<'))
    print()
