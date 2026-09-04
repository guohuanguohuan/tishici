# -*- coding: utf-8 -*-
"""抽取B/H讲部需背真实段落全文（供新图例行样例建模）。"""
import zipfile, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
BASE = r'C:\提示词\高中数学\高中数学同步'
for tag, fn in [('B', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
                ('H', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx')]:
    with zipfile.ZipFile(os.path.join(BASE, fn)) as z:
        doc = z.read('word/document.xml').decode('utf-8')
    rows = re.findall(r'<w:p[ >].*?</w:p>', doc, re.S)
    hit = 0
    for r in rows:
        text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', r))
        shds = set(re.findall(r'fill="(C9C9C9)"', r))
        # 讲部条目号段：「X.Y.Z-N．」或「X.Y-N．」起首且非题号块（四级）
        if shds and re.match(r'^\d+\.\d+(\.\d+)?-\d+．', text) and not re.match(r'^\d+\.\d+\.\d+\.\d+-', text):
            print('[%s] %s' % (tag, text[:100]))
            hit += 1
            if hit >= 4:
                break
    # 讲部标题行（方法讲解｜主题）
    for r in rows:
        text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', r))
        if '方法讲解' in text or '讲部' in text[:12]:
            print('[%s·讲部标题] %s' % (tag, text[:80]))
            break
