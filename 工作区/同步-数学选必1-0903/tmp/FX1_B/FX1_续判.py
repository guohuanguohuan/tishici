# -*- coding: utf-8 -*-
"""FX1-B 续修：35个灰底run逐个判定（放行/缩归值）
判定逻辑：
  A) 合法放行（不动）：OMML整块覆盖（§7合法挂法）——该run非纯标点且属公式挂点，或标点是公式整体一部分
  B) 越界缩底（拆run/缩shd）：值本身之外的分隔标点/叙述词文字被盖灰
逐run打印：段号｜文本｜run前/后邻居（文本+oMath线性化）｜灰底run边界（前灰值/后灰值）｜初判"""
import zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
PATH = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
with zipfile.ZipFile(PATH) as z:
    root = etree.fromstring(z.read('word/document.xml'))
paras = root.find(f'{{{W}}}body').findall(f'{{{W}}}p')
punct_only = re.compile(r'^[，．。、；：,.;:()\[\]（）　]+$')

def om_lin(om):
    return ''.join(e.text or '' for e in om.iter() if etree.QName(e).localname == 't')

def run_info(r):
    """返回(run文本或'oMath:..', 灰底fill或'')"""
    t = r.find(f'{{{W}}}t')
    txt = t.text if t is not None and t.text else ''
    shd = r.find(f'{{{W}}}rPr/{{{W}}}shd')
    fill = shd.get(f'{{{W}}}fill') if shd is not None else ''
    return txt, fill

# 对每个含纯标点灰底run的段，重建run与oMath的交错序列，标出灰底范围
for i, p in enumerate(paras):
    # 构建该段子元素序列（按文档顺序）：每个元素为 ('r', text, fill) 或 ('m', lin, is_gray)
    seq = []
    # p 的子元素直接遍历，但 oMath 可能嵌在 pPr 后面的 w:r / m:oMath；用迭代器按文档序
    # word 段落结构：pPr 之后是一列 w:r 或 m:oMath（.// 会丢失顺序，改用 p.iterchildren())
    relevant = []
    drop_pPr = [c for c in p if etree.QName(c).localname != 'pPr']
    for c in drop_pPr:
        if etree.QName(c).localname == 'r':
            txt, fill = run_info(c)
            relevant.append(('r', txt, fill))
        elif etree.QName(c).localname == 'oMath':
            # 检查该om整块是否挂灰（m:r rPr shd 或 ctrlPr）
            lin = om_lin(c)
            grays = [el for el in c.iter(f'{{{W}}}shd') if el.get(f'{{{W}}}fill') == 'C9C9C9']
            relevant.append(('m', lin, 'GRAY' if grays else ''))
    has_punct_gray = any(rk == 'r' and fl == 'C9C9C9' and punct_only.match(tx) for rk, tx, fl in relevant)
    if not has_punct_gray:
        continue
    print(f'===== p#{i} =====')
    parts = []
    for rk, tx, fl in relevant:
        if rk == 'r':
            parts.append(f'[{fl and ("▮"+tx)} or tx]')
        else:
            parts.append(f'⟨{tx}⟩')
    print('  ', ''.join(parts))
    # 逐个标点灰run判定邻居
    for bi in range(len(relevant)):
        rk, tx, fl = relevant[bi]
        if rk == 'r' and fl == 'C9C9C9' and punct_only.match(tx):
            prev = relevant[bi-1] if bi > 0 else None
            nxt = relevant[bi+1] if bi+1 < len(relevant) else None
            def fmt(x):
                if not x: return ''
                rk2, tx2, fl2 = x
                if rk2 == 'r': return f'{"▮" if fl2=="C9C9C9" else ""}({tx2})'
                return f'⟨{tx2}⟩'
            print(f'    p#{i} 越界候选 [{tx!r}]  prev={fmt(prev)}  nxt={fmt(nxt)}')
