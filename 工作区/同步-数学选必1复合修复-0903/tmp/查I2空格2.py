import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')
# 倾斜角范围表：找「0°≤α」或「倾斜角」
for pat in ['0°≤α', '倾斜角的取值', '倾斜角']:
    idxs = [m.start() for m in re.finditer(pat, xml)]
    print(pat, '命中', len(idxs), idxs[:6])
i = xml.find('0°≤')
if i != -1:
    seg = xml[max(0, i-3000):i+3000]
    rows = re.findall(r'<w:tr[ >].*?</w:tr>', seg, re.S)
    print(f'邻近行数={len(rows)}')
    for r in rows:
        cells = re.findall(r'<w:tc>.*?</w:tc>', r, re.S)
        txt = [''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', c))[:30] for c in cells]
        print('  行:', txt)
