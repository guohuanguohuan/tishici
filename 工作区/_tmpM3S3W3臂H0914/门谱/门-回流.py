# -*- coding: utf-8 -*-
r"""门-回流.py — M3 S3 课时01 练习件母版·回流门（零强制跳页）＋件型纪律断言。

断言面：main.tex 剔注释后：
  ①强制版面原子零出现：\newpage \clearpage \pagebreak \vbox \vtop \ketangboxed
    \columnbreak \eject \vfill（\vbox 系 M2「右栏全空」病灶根因；\vfill 手动凑版禁用，
    尾空由 \tailfill 无参形承当）。
  ②练习件件型纪律：\begin{ketang} ×0（课堂评价属导学件 G5 域，练习件不设）；
    \tailfill 恰 1（尾页填充块每件恰一处，置 \end{multicols} 前）；
    \duoxuan 计数＝manifest 期望值多选数（本件 2＝E2/E3，≤4 合规）；
    \liubai 计数＝片内解答题数（本件 7）且逐题 [16mm]（无小问默认档，cap 40mm 内）；
    \kongda 计数＝1（E7 填空印答位，两档等形开关宏）。
用法: python 门-回流.py     退出码: 0＝全过；1＝有红。
"""
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/衔接节'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/衔接节.manifest.json'
BAD = ['\\newpage', '\\clearpage', '\\pagebreak', '\\vbox', '\\vtop',
       '\\ketangboxed', '\\columnbreak', '\\eject', '\\vfill']

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

for w in BAD:
    n = body.count(w)
    check(f'{w} ×0', n == 0, f'{n}')

n_ketang = body.count('\\begin{ketang}')
check('\\begin{ketang} ×0（练习件不设课堂评价）', n_ketang == 0, f'{n_ketang}')
n_tail = len(re.findall(r'\\tailfill(?![a-zA-Z])', body))
check('\\tailfill 恰1（尾块每件恰一处）', n_tail == 1, f'{n_tail}')

manifest = json.load(open(MANIFEST, encoding='utf-8'))
exp_duo = manifest['期望值']['多选数']
n_duo = len(re.findall(r'\\duoxuan(?![a-zA-Z])', body))
check(f'\\duoxuan 计数＝manifest 期望值多选数 {exp_duo}（≤4）', n_duo == exp_duo, f'{n_duo}')

# 衔接节槽配实录（题面库头标逐键）：单选2（练14/15）＋多选0＋填空1（练2）＋解答13；
# 书写区高度照小问数梯：练1（4问）/练8（3问）32mm，练4/5/6（2问）24mm，无小问 16mm 默认档。
LIUBAI_H = ['32mm', '16mm', '24mm', '24mm', '24mm', '16mm', '32mm',
            '16mm', '16mm', '16mm', '16mm', '16mm', '16mm']
n_jieda = sum(1 for k in manifest['键序'] if k.startswith('2章-练-'))
n_liubai = len(re.findall(r'\\liubai(?![a-zA-Z])', body))
liubai_h = re.findall(r'\\liubai\[([0-9.]+mm)\]', body)
check(f'\\liubai 计数＝解答题数 {n_jieda}（以头标槽型实录 13 为准）', n_liubai == 13, f'{n_liubai}')
check('\\liubai 逐题高度＝小问数梯（4/3问32mm・2问24mm・无问16mm；16~40mm 带内）',
      liubai_h == LIUBAI_H, f'{liubai_h}')

n_kongda = len(re.findall(r'\\kongda(?![a-zA-Z])', body))
check('\\kongda 计数＝1（练2 填空印答位）', n_kongda == 1, f'{n_kongda}')

print()
print('回流门：', '全绿（零强制跳页＋件型纪律合规）' if not reds else f'红：{reds}')
sys.exit(0 if not reds else 1)
