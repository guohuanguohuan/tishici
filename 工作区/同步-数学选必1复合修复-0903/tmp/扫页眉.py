import fitz, glob, os

base = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\pages_406\pdf'
for p in sorted(glob.glob(base + r'\*.pdf')):
    name = os.path.basename(p)[:-4]
    if name == '导出记录': continue
    doc = fitz.open(p)
    n = len(doc)
    hits = 0
    for i in range(n):
        if '羿郭工作室' in doc[i].get_text():
            hits += 1
    print(f'{name}: {n}页 含页眉文本页数={hits}')
    doc.close()
