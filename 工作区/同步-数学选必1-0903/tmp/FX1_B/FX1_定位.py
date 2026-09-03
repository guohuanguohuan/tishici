# -*- coding: utf-8 -*-
"""FX1-B 定位脚本：标题段p#0全文XML、题1.2.1.2-2全块、w:tab分布、段尾空格分布"""
import re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
tree = etree.parse(r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX1_B\unzipped\word\document.xml')
root = tree.getroot()
body = root.find(f'{{{W}}}body')
paras = body.findall(f'{{{W}}}p')
print(f'总段数={len(paras)}')

def para_text(p):
    """段落文字流：w:t文本 + w:tab记为<TAB> + oMath线性化摘要"""
    parts = []
    for el in p.iter():
        tag = etree.QName(el).localname
        if tag == 't' and el.text:
            parts.append(el.text)
        elif tag == 'tab':
            parts.append('<TAB>')
    return ''.join(parts)

def para_text_notab(p):
    parts = []
    for el in p.iter():
        tag = etree.QName(el).localname
        if tag == 't' and el.text:
            parts.append(el.text)
    return ''.join(parts)

# 1) 标题段 p#0 完整XML
print('=' * 30, 'P#0 标题段 XML', '=' * 30)
x = etree.tostring(paras[0], encoding='unicode', pretty_print=True)
print(x[:4000])

# 2) 找题1.2.1.2-2 题号块段
print('=' * 30, '题1.2.1.2-2 定位', '=' * 30)
idx_122 = None
for i, p in enumerate(paras):
    t = para_text_notab(p)
    if t.strip().startswith('1.2.1.2-2'):
        idx_122 = i
        print(f'题号块段 p#{i}: {t[:80]}')
        break
if idx_122 is not None:
    # 输出该题全块直到下一个题号块（正则 ^\d+\.\d+\.\d+\.\d+-\d+．）
    pat = re.compile(r'^\d+(\.\d+){3}-\d+')
    end = len(paras)
    for j in range(idx_122 + 1, len(paras)):
        t = para_text_notab(paras[j]).strip()
        if pat.match(t):
            end = j
            break
    print(f'块范围 p#{idx_122}..p#{end - 1}，共{end - idx_122}段')
    for j in range(idx_122, end):
        p = paras[j]
        # 段落底纹
        shd = p.find(f'{{{W}}}pPr/{{{W}}}shd')
        shd_s = f' shd={shd.get(f"{{{W}}}fill")}' if shd is not None else ''
        txt = para_text(p)
        print(f'p#{j}{shd_s}: {txt}')
        # oMath 线性化（前3个）
        for k, om in enumerate(p.findall(f'.//{{{W}}}oMath')):
            lin = ''.join(el.text or '' for el in om.iter() if etree.QName(el).localname == 't')
            print(f'    oMath#{k}: {lin}')

# 3) w:tab 分布
print('=' * 30, 'w:tab 分布', '=' * 30)
tab_count = 0
for i, p in enumerate(paras):
    tabs = p.findall(f'.//{{{W}}}tab')
    if tabs:
        tab_count += len(tabs)
        print(f'p#{i} ({len(tabs)}tab): {para_text(p)[:120]}')
print(f'w:tab总数={tab_count}')

# 4) 段尾空格（末元素w:t尾随空格）
print('=' * 30, '段尾空格分布', '=' * 30)
trailing = 0
for i, p in enumerate(paras):
    # 找段内最后一个w:t（跳过纯空标记）
    last_t = None
    for el in p.iter():
        if etree.QName(el).localname == 't':
            last_t = el
    if last_t is not None and last_t.text and last_t.text != last_t.text.rstrip():
        trailing += 1
        disp = last_t.text[-25:]
        print(f'p#{i}: 尾部={[disp]!r}')
print(f'段尾空格段数={trailing}')
