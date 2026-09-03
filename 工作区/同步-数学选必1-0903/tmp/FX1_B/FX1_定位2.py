# -*- coding: utf-8 -*-
"""FX1-B 定位2：p#260 OMML结构逐块、段尾空格w:t/m:t区分、p#85/289/411/445 run结构"""
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
tree = etree.parse(r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX1_B\unzipped\word\document.xml')
root = tree.getroot()
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')

def lin_omath(om):
    return ''.join(el.text or '' for el in om.iter() if etree.QName(el).localname == 't')

# 1) p#260 详解段：逐子元素（w:r文字 / m:oMath线性化）+ 关键oMath完整XML
print('=' * 25, 'p#260 详解段内容流', '=' * 25)
p = paras[260]
for child in p:
    ln = etree.QName(child).localname
    if ln == 'r':
        t = child.find(f'{{{W}}}t')
        txt = t.text if t is not None else ''
        rpr = child.find(f'{{{W}}}rPr')
        shd = rpr.find(f'{{{W}}}shd') if rpr is not None else None
        shd_s = f'[shd={shd.get(f"{{{W}}}fill")}]' if shd is not None else ''
        print(f'  w:r{shd_s}: {txt!r}')
    elif ln == 'oMath':
        print(f'  m:oMath: {lin_omath(child)!r}')
    else:
        print(f'  <{ln}>')

# 关键：解得后的oMath完整XML（含 x=1 z=-2 的）
print('=' * 25, 'p#260 全部oMath线性化+定位x=1/z=-2', '=' * 25)
oms = p.findall(f'.//{{{M}}}oMath')
for k, om in enumerate(oms):
    s = lin_omath(om)
    print(f'oMath#{k}: {s!r}')
    if '解得' not in s and ('=1' in s or '=-2' in s or '=2' in s):
        pass
# oMath内含x=1或z=-2的完整XML
for k, om in enumerate(oms):
    s = lin_omath(om)
    if ('x=1' in s.replace(' ','')) or ('z=-2' in s.replace(' ','')):
        print(f'---- oMath#{k} 完整XML ----')
        print(etree.tostring(om, encoding='unicode')[:6000])

# 2) 段尾空格：区分w:t（正文）与m:t（公式）
print('=' * 25, '段尾空格区分 w:t / m:t', '=' * 25)
cnt_w, cnt_m = 0, 0
for i, para in enumerate(paras):
    last_t = None
    last_ns = None
    for el in para.iter():
        ln = etree.QName(el).localname
        if ln == 't' and el.text and el.text != el.text.rstrip():
            # 记录最后一个带尾随空格的t（同时确认它是否为段内最后文本元素）
            pass
    # 真正口径：段内最后一个t元素（w:t或m:t）
    last_any = None
    for el in para.iter():
        if etree.QName(el).localname == 't':
            last_any = el
    if last_any is not None and last_any.text and last_any.text != last_any.text.rstrip():
        ns = etree.QName(last_any).namespace
        kind = 'w:t' if ns == W else ('m:t' if ns == M else '?')
        if kind == 'w:t':
            cnt_w += 1
        else:
            cnt_m += 1
        print(f'p#{i} [{kind}]: {last_any.text[-20:]!r}')
print(f'w:t段尾空格={cnt_w}  m:t段尾空格={cnt_m}')

# 3) p#85/289/411/445 选项行run结构（tab前后邻接文本）
print('=' * 25, '选项行tab邻接结构', '=' * 25)
for i in (85, 289, 411, 445):
    para = paras[i]
    print(f'--- p#{i} ---')
    seq = []
    for r in para.findall(f'{{{W}}}r'):
        for ch in r:
            ln = etree.QName(ch).localname
            if ln == 't' and ch.text:
                seq.append(('t', ch.text))
            elif ln == 'tab':
                seq.append(('TAB', ''))
    print(seq)
