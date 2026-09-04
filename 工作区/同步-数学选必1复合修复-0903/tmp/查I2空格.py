import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')
# 找「范围」单元格（清单件开头倾斜角范围表）
for m in re.finditer('范围', xml):
    seg = xml[max(0, m.start()-200):m.start()+1500]
    if '0°' in seg or '取值' in seg:
        # 抽该行的单元格纯文本
        cells = re.findall(r'<w:tc>.*?</w:tc>', seg, re.S)
        for c in cells:
            t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', c))
            print('单元格:', repr(t[:60]))
        break
