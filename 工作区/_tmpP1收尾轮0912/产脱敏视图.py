# -*- coding: utf-8 -*-
r"""产脱敏视图.py —— 收尾轮A·测评脱敏视图生成器（供复跑盲解）。

输入＝剥注改后 成卷/测评卷/main.tex；变换＝①删全部整行 % 注释（含件头/槽注/分页横幅）
②\dabiao 速查宏体置空（定义行保留、体＝{}，调用点不动）；断言＝输出「答案」0 处、
「（矢量）」「（指大小）」在位（题面印字非泄密）、行数>0。输出＝本目录 测评-脱敏视图.txt。
"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = r'C:\提示词\工作区\P1-必修3第9章量产0912\成卷\测评卷\main.tex'
DST = r'C:\提示词\工作区\_tmpP1收尾轮0912\测评-脱敏视图.txt'

lines = open(SRC, encoding='utf-8').read().split('\n')

# ② \dabiao 宏体置空：定位定义行与其收尾 `\par}` 行
try:
    i0 = next(i for i, l in enumerate(lines) if re.match(r'^\s*\\newcommand\{\\dabiao\}', l))
    i1 = next(i for i in range(i0 + 1, len(lines)) if re.match(r'^\s*\\par\}\s*$', lines[i]))
except StopIteration:
    sys.exit('中止：\dabiao 宏体边界未找到')
body = [l for l in lines[i0:i1 + 1] if '答案' in l]
lines[i0:i1 + 1] = [r'\newcommand{\dabiao}{}']

# ① 删整行注释
out = [l for l in lines if not l.lstrip().startswith('%')]

txt = '\n'.join(out)
errs = []
if '答案' in txt:
    hits = [i + 1 for i, l in enumerate(out) if '答案' in l]
    errs.append(f'正文残留「答案」行：{hits}')
for needle in ('拉力（矢量）不变', '库仑力增大（指大小）'):
    if needle not in txt:
        errs.append(f'题面印字缺失：{needle}')
if len(out) < 50:
    errs.append(f'行数异常：{len(out)}')
if errs:
    sys.exit('中止：' + '；'.join(errs))

open(DST, 'w', encoding='utf-8', newline='\n').write(txt)
import os
print(f'OK 输出 {DST}')
print(f'行数 {len(out)}（源 {len(lines)}）；宏体清除键值行 {len(body)} 条；字节 {os.path.getsize(DST)}；「答案」计数 0')
