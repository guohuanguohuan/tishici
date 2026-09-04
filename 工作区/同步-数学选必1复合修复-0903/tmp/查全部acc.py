import zipfile, re

f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
xml = zipfile.ZipFile(f).read('word/document.xml').decode('utf-8')

# 全部 m:acc 块：基底文本、是否双字母、父上下文（是否在表格 w:tbl 内不好判，改看块前800字符有无 <w:tbl> 开且中间无 </w:tbl>）
hits = []
for m in re.finditer(r'<m:acc>.*?</m:acc>', xml, re.S):
    blk = m.group(0)
    base = ''.join(re.findall(r'<m:t[^>]*>([^<]*)</m:t>', blk))
    chr_m = re.search(r'<m:chr m:val="([^"]*)"/>', blk)
    val = chr_m.group(1) if chr_m else '(默认)'
    pre = xml[max(0, m.start()-60000):m.start()]
    in_tbl = pre.rfind('<w:tbl>') > pre.rfind('</w:tbl>')
    hits.append((m.start(), base, val, '表内' if in_tbl else '正文'))

print(f'共 {len(hits)} 个 m:acc')
print('双字母基底明细：')
for pos, base, val, loc in hits:
    if len(base) >= 2:
        cps = ' '.join(f'U+{ord(c):04X}' for c in val)
        print(f'  pos={pos} 基底={base!r} 符={cps} {loc}')
print()
print('单字母基底统计：', sum(1 for _,b,_,_ in hits if len(b)==1))
print('双字母在表内：', sum(1 for _,b,_,l in hits if len(b)>=2 and l=='表内'), '／在正文：', sum(1 for _,b,_,l in hits if len(b)>=2 and l=='正文'))
