# -*- coding: utf-8 -*-
"""FX1-B 续修·权威分类：枚举35个纯标点C9C9C9 run，打印邻居，输出人工分类
分类规则（主会话口径）：
  SURFACE（值外分隔标点/值末标点 → 缩回，删shd）
  KEEP  （合法：多值各标各的边界括号/值内复合括号/证明链内标点/留白间隙）"""
import zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
PATH = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
with zipfile.ZipFile(PATH) as z:
    root = etree.fromstring(z.read('word/document.xml'))
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')
punct_only = re.compile(r'^[，．。、；：,.;:()\[\]（）　 ]+$')

def om_gray(om):
    return any(shd.get(f'{{{W}}}fill') == 'C9C9C9' for shd in om.iter(f'{{{W}}}shd'))
def om_lin(om):
    return ''.join(e.text or '' for e in om.iter() if etree.QName(e).localname == 't')

tot = 0
surf = []
keep = []
for idx, p in enumerate(paras):
    # 文档序子元素（跳过pPr）
    seq = []
    for c in p:
        ln = etree.QName(c).localname
        if ln == 'pPr':
            continue
        if ln == 'r':
            t = c.find(f'{{{W}}}t')
            txt = t.text if t is not None and t.text else ''
            shd = c.find(f'{{{W}}}rPr/{{{W}}}shd')
            fill = shd.get(f'{{{W}}}fill') if shd is not None else ''
            seq.append(('r', txt, fill))
        elif ln == 'oMath':
            seq.append(('m', om_lin(c), 'G' if om_gray(c) else ''))
    for bi, (rk, tx, fl) in enumerate(seq):
        if rk != 'r' or fl != 'C9C9C9' or not punct_only.match(tx):
            continue
        tot += 1
        prev = seq[bi-1] if bi > 0 else None
        nxt = seq[bi+1] if bi+1 < len(seq) else None
        def f(x):
            if not x: return '<SEP/END>'
            rk2, tx2, fl2 = x
            if rk2 == 'm': return f'⟨{tx2}⟩'
            return f'{"▮" if fl2=="C9C9C9" else ""}{tx2!r}'
        print(f'p#{idx} [{tx!r}] prev={f(prev)}  nxt={f(nxt)}')
print('TOTAL=', tot)

# 自动初判（供人工复核）：值末标点= ; 
