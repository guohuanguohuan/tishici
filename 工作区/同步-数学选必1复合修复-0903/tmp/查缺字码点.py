import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')

# 找所有「加法」出现点，看哪个附近3k字符内有 OB
for m in re.finditer('加法', xml):
    seg = xml[m.start():m.start()+4000]
    if 'OB' in seg:
        # 抽取该段所有 w:t 与 m:t 文本
        texts = re.findall(r'<(?:w|m):t[^>]*>([^<]*)</(?:w|m):t>', seg)
        joined = ''.join(texts)
        print('位置:', m.start())
        print('纯文本(前150):', joined[:150])
        print()
        print('码点明细（前60字符）:')
        for ch in joined[:60]:
            cp = ord(ch)
            tag = ' <== 非常规' if cp > 0x2500 and cp < 0x4E00 else ''
            print(f'  U+{cp:04X} {ch!r}{tag}')
        # 看该段是否有 OMML 组合字符（m:groupChr / m:bar / m:acc）
        for pat in ['m:groupChr', 'm:bar', 'm:acc', 'm:chr', '20D7', '2192']:
            n = seg.count(pat)
            if n: print(f'  [结构] {pat} x{n}')
        break
