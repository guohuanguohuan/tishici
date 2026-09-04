# -*- coding: utf-8 -*-
"""R1：册目录页.docx 六件级行 w:shd 命名空间 w:fill=C9C9C9 核验＋全件裸 fill= 残留扫描（只读）"""
import sys, io, json, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
from docx import Document
from docx.oxml.ns import qn

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
P1 = r'C:\提示词\高中数学\高中数学同步\人教B版选必1·册目录页.docx'
TARGET = [3, 4, 5, 9, 10, 11]

doc = Document(P1)
print('== 六件级行段级 w:shd（python-docx 属性层）==')
ok_all = True
for i in TARGET:
    p = doc.paragraphs[i]
    pPr = p._p.pPr
    shd = pPr.find(qn('w:shd')) if pPr is not None else None
    if shd is None:
        fill = None; keys = []
    else:
        fill = shd.get(qn('w:fill'))
        keys = list(shd.attrib.keys())
    naked = [k for k in keys if '}' not in k]
    ok = fill == 'C9C9C9' and not naked
    ok_all &= ok
    print('%s 段%02d: w:fill=%s 属性=%s 裸属性=%s | %s' % ('PASS' if ok else 'FAIL', i, fill, keys, naked, p.text[:34]))

print('== 全件 XML 层 w:shd 枚举＋裸 fill 扫描 ==')
zf = zipfile.ZipFile(P1)
n_shd = n_wfill = n_bare = 0
bare_ctx = []
shd_keys_seen = set()
for part in zf.namelist():
    if not part.endswith('.xml'):
        continue
    raw = zf.read(part).decode('utf-8', 'ignore')
    for m in re.finditer(r'<w:shd\b[^>]*?/?>', raw):
        seg = m.group(0)
        n_shd += 1
        shd_keys_seen.update(re.findall(r'([\w:]+)=', seg))
        for bm in re.finditer(r'(?<![:\w])fill\s*=', seg):
            n_bare += 1
            bare_ctx.append((part, seg[:120]))
        if re.search(r'\bw:fill=', seg):
            n_wfill += 1
    # 全包任意位置裸 fill=（不限 w:shd 内）
    for bm in re.finditer(r'<[^>]+?[^:\w]fill\s*=', raw):
        pass
print('w:shd 元素总数=%d，其中带 w:fill= 的=%d，带裸 fill= 的=%d' % (n_shd, n_wfill, n_bare))
print('w:shd 上出现过的属性名:', sorted(shd_keys_seen))
if bare_ctx:
    print('裸 fill 现场:', bare_ctx[:5])
ok_r1 = ok_all and n_bare == 0 and n_wfill >= 6
print('R1 总判:', 'PASS' if ok_r1 else 'FAIL')
