import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')
i = 29066
seg = xml[i-2500:i+2500]
# 去掉冗长 rPr/pPr 便于看结构
seg2 = re.sub(r'<w:(rPr|pPr)>.*?</w:\1>', '⟨\1⟩', seg, flags=re.S)
seg2 = re.sub(r'<w:rPr/>', '', seg2)
print(seg2.replace('><', '>\n<')[:4000])
