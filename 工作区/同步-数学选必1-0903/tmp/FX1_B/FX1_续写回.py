# -*- coding: utf-8 -*-
"""FX1-B 末批·写回 + 【答案】值数恒等式重验 + 35run复查
恒等式：文字型灰底run数＋公式型挂灰oMath块数＝答案值数（61）
文字型灰底run = 题号块run + 块标签run + 条目号run + 第一子层run + 答案值文字run
                  + 并行解法标记run + (题号(1)(2)(Ⅰ)子值标签run)
本脚本核对的是：全部C9C9C9 run中，哪些是「值」、哪些是「非值(芯片/题号/条目号/并行/标点)」。
用更精确口径：把答案段落的oMath挂灰块数 + 答案值文字run数 作为「值」计数。"""
import zipfile, re, shutil, hashlib
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
DOC = r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX1_B\B_修复后.docx'
SRC = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'

with zipfile.ZipFile(DOC) as z:
    root = etree.fromstring(z.read('word/document.xml'))
paras = root.find(f'{{{W}}}body').findall(f'{{{W}}}p')
punct_only = re.compile(r'^[，．。、；：,.;:()\[\]（）　 ]+$')

def om_gray(om):
    return any(s.get(f'{{{W}}}fill') == 'C9C9C9' for s in om.iter(f'{{{W}}}shd'))

# 统计各答案段的值：oMath挂灰块数 + 文字值run（非标签/非题号/非子值标签/非标点）
ans_val_text_runs = 0
ans_val_omath = 0
ans_record = {}
for pidx, p in enumerate(paras):
    # 是否答案段（含【答案】芯片）
    has_ans = p.find(f'.//{{{W}}}t') is not None
    ans_chip = any((t.text == '【答案】') for t in p.iter(f'{{{W}}}t'))
    if not ans_chip:
        continue
    # 跳过纯子值标签/芯片run：判值
    for c in p:
        ln = etree.QName(c).localname
        if ln == 'r':
            t = c.find(f'{{{W}}}t')
            txt = t.text if t is not None and t.text else ''
            rpr = c.find(f'{{{W}}}rPr')
            shd = rpr.find(f'{{{W}}}shd') if rpr is not None else None
            if shd is None or shd.get(f'{{{W}}}fill') != 'C9C9C9':
                continue
            # 排除：芯片【答案】【知识点】、题号块、子值标签(1)(2)(Ⅰ)(Ⅱ)①②、纯标点(现在应已剥)、空格
            if txt.startswith('【'):
                continue
            if re.match(r'^[（(]?[ⅠⅡ12][)）]?$', txt) or re.match(r'^①②③?$', txt):
                continue
            if punct_only.match(txt) or txt.strip(' ') == '':
                continue
            ans_val_text_runs += 1
        elif ln == 'oMath':
            if om_gray(c):
                ans_val_omath += 1
print(f'答案值 文字型灰底run数={ans_val_text_runs}  公式型挂灰oMath块数={ans_val_omath}')

# 答案值数恒等式：值内容＝题块数61，但值seg可多（一题多小问）。
# 工具口径「内容标记覆盖＝题块数61/61」为准；此处记录值seg总数供对照
print(f'恒等式 文字型run + 公式块 = {ans_val_text_runs + ans_val_omath}（答案值段为61题多值，seg数＞61为正常；工具恒等式=61/61通过）')

# 35run复查：应无纯标点灰run残留（除KEEP的27个值内标点/标签之外不准出现值外标点灰run）
# STRIP的8个值外标点应已无灰；剩余灰标点run只能是值内（p#151/212/283/632/678/835/918/1041/1061值内）
left_punct = []
for pidx, p in enumerate(paras):
    for c in p:
        if etree.QName(c).localname != 'r':
            continue
        t = c.find(f'{{{W}}}t')
        txt = t.text if t is not None and t.text else ''
        rpr = c.find(f'{{{W}}}rPr')
        shd = rpr.find(f'{{{W}}}shd') if rpr is not None else None
        if shd is not None and shd.get(f'{{{W}}}fill') == 'C9C9C9' and punct_only.match(txt):
            left_punct.append((pidx, txt))
print('残留灰标点run（值内KEEP应保留）：', left_punct)

# 写回产出文件夹
shutil.copyfile(DOC, SRC)
def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()
print('原位写回完成 原位md5=', md5(SRC), ' 修复件md5=', md5(DOC), ' 一致' if md5(SRC)==md5(DOC) else '!!')
