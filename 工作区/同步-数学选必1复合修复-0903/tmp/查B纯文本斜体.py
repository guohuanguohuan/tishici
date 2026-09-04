import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')
for m in re.finditer(r'<w:r>.*?</w:r>', xml, re.S):
    blk = m.group(0)
    if '<m:' in blk: continue
    t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', blk))
    bad = [c for c in t if 0x1D400 <= ord(c) <= 0x1D7FF]
    if bad:
        rf = re.search(r'<w:rFonts[^/]*/>', blk)
        # 段落上下文：前300字符的纯文本
        pre = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml[max(0,m.start()-1500):m.start()]))[-30:]
        print(f"pos={m.start()} 字={''.join(bad)} 字体={rf.group(0) if rf else '默认'} 上文=…{pre}")
