import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')

i = 72073
seg = xml[i:i+4000]
# 逐个 m:acc 块：提取 m:chr 的 val 与基底文本
for j, m in enumerate(re.finditer(r'<m:acc>.*?</m:acc>', seg, re.S)):
    blk = m.group(0)
    chr_m = re.search(r'<m:chr m:val="([^"]*)"/>', blk)
    base = ''.join(re.findall(r'<m:t[^>]*>([^<]*)</m:t>', blk))
    ctrl = re.search(r'<m:accPr>(.*?)</m:accPr>', blk, re.S)
    val = chr_m.group(1) if chr_m else '(无m:chr→默认上箭头)'
    cps = ' '.join(f'U+{ord(c):04X}' for c in val)
    print(f'acc#{j}: 基底={base!r} 重音符={val!r} [{cps}]')
