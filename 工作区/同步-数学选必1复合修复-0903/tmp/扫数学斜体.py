import zipfile, re

pieces = {
 'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
 'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
 'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
base = r'C:\提示词\高中数学\高中数学同步\\'
import collections
for k, fn in pieces.items():
    xml = zipfile.ZipFile(base + fn).read('word/document.xml').decode('utf-8')
    cnt = collections.Counter()
    # 逐 run 判定：m:r 内（OMML）与 w:r 内（纯文本run）
    for m in re.finditer(r'<m:r>(.*?)</m:r>', xml, re.S):
        blk = m.group(1)
        t = ''.join(re.findall(r'<m:t[^>]*>([^<]*)</m:t>', blk))
        if any(0x1D400 <= ord(c) <= 0x1D7FF for c in t):
            rf = re.search(r'<w:rFonts[^/]*/>', blk)
            cnt['OMML:' + (rf.group(0)[:60] if rf else '无rFonts')] += 1
    for m in re.finditer(r'<w:r>.*?</w:r>', xml, re.S):
        blk = m.group(0)
        if '<m:' in blk: continue
        t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', blk))
        if any(0x1D400 <= ord(c) <= 0x1D7FF for c in t):
            cnt['w:r纯文本'] += len([c for c in t if 0x1D400 <= ord(c) <= 0x1D7FF])
    if cnt:
        print(k, dict(cnt))
print('扫描完')
