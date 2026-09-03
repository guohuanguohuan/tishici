# -*- coding: utf-8 -*-
"""B代理·细查：册目录页列头行/制表位原始XML；使用说明/封面/部分封面全文；主题图哈希复用核对。只读。"""
import io, re, sys, zipfile, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SYNC = r'C:\提示词\高中数学\高中数学同步'

def runs_text(p):
    return ''.join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', p))

print('########## 册目录页·列头行与代表行原始XML ##########')
z = zipfile.ZipFile(SYNC + r'\人教B版选必1·册目录页.docx')
doc = z.read('word/document.xml').decode('utf-8')
paras = re.findall(r'<w:p\b[^>]*>.*?</w:p>', doc, re.S)
for i in (1, 2, 3, 6):
    p = paras[i]
    print(f'--- p{i:02d} 全XML（{len(p)}B）：')
    print(p[:2200])
    print()
z.close()

print('########## 封面·全文（逐段） ##########')
z = zipfile.ZipFile(SYNC + r'\人教B版选必1·封面.docx')
doc = z.read('word/document.xml').decode('utf-8')
for i, p in enumerate(re.findall(r'<w:p\b[^>]*>.*?</w:p>', doc, re.S)):
    t = runs_text(p)
    if t.strip():
        szs = set(re.findall(r'<w:sz w:val="(\d+)"/>', p))
        jc = re.search(r'<w:jc w:val="([^"]+)"', p)
        print(f'  p{i:02d} [sz={sorted(szs)} jc={jc.group(1) if jc else "-"}] {t}')
z.close()

print()
print('########## 使用说明·全文（逐段含底纹/边框登记） ##########')
z = zipfile.ZipFile(SYNC + r'\人教B版选必1·使用说明.docx')
doc = z.read('word/document.xml').decode('utf-8')
for i, p in enumerate(re.findall(r'<w:p\b[^>]*>.*?</w:p>', doc, re.S)):
    t = runs_text(p)
    if not t.strip():
        continue
    shds = re.findall(r'w:fill="([0-9A-Fa-f]{6})"', p)
    pbdr = '<w:pBdr>' in p
    szs = set(re.findall(r'<w:sz w:val="(\d+)"/>', p))
    print(f'  p{i:02d} [sz={sorted(szs)} fill={shds} pBdr={int(pbdr)}] {t}')
z.close()

print()
print('########## 部分封面×6·全文＋主题图哈希 ##########')
PC = ['人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx',
      '人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx',
      '人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx',
      '人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx',
      '人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx',
      '人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx']
for fn in PC:
    z = zipfile.ZipFile(SYNC + '\\' + fn)
    doc = z.read('word/document.xml').decode('utf-8')
    print(f'【{fn.split("·部分封面")[1]}】')
    for i, p in enumerate(re.findall(r'<w:p\b[^>]*>.*?</w:p>', doc, re.S)):
        t = runs_text(p)
        if not t.strip():
            continue
        szs = sorted(set(re.findall(r'<w:sz w:val="(\d+)"/>', p)))
        print(f'  p{i:02d} [sz={szs}] {t}')
    # 图与哈希
    rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
    media = dict(re.findall(r'Id="([^"]+)"[^>]*Target="media/([^"]+)"', rels))
    for rid, mfn in media.items():
        data = z.read('word/media/' + mfn)
        h = hashlib.md5(data).hexdigest()
        ext = mfn.rsplit('.', 1)[-1].lower()
        exts = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', doc)
        cx, cy = (int(exts.group(1)), int(exts.group(2))) if exts else (0, 0)
        print(f'  主题图：{mfn} md5={h} {len(data)}B 格式={ext} extent={cx}x{cy}EMU={cx/360000:.2f}x{cy/360000:.2f}cm')
    z.close()
    print()
