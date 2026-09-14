# -*- coding: utf-8 -*-
"""冒烟括线.py — 括线模（\ansblockgrayfalse）合成样本冒烟（波2·试迁不确定点3 销项）。

试迁报告-练习本 §五.3：「括线模路径未实证——拓展册上/下批插前须先以一件长答块冒烟」。
拓区实测值单行形（最长 135 单位 ≈ 3 行），无自然长块——以拓-004 合成加长详解（估 >8 行）
强制括线模，验证：true 档 hairline 括线块正常印、pure 档整块吞、双档三零、可跨栏。
产物落 _冒烟括线/（本树内），不触批插件。
"""
import io
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(HERE, '_冒烟括线')
S = os.path.join(HERE, 'M2练习本', '上册')

shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)
for f in os.listdir(S):
    p = os.path.join(S, f)
    if os.path.isfile(p) and (f.startswith('qp-') or f in ('main.tex', 'render.py')):
        shutil.copyfile(p, os.path.join(D, f))
shutil.copytree(os.path.join(S, 'figs'), os.path.join(D, 'figs'))

tex = io.open(os.path.join(D, 'main.tex'), encoding='utf-8').read()
pat = re.compile(r'\\begin\{ansblock\}\[拓-004\]\n.*?\\end\{ansblock\}', re.S)
old = pat.search(tex)
assert old, '拓-004 块未命中'
fill = ('（括线模冒烟·合成加长段）' + '向量分解必先取定基底，基底须不共面；共面向量组的线性表出未必唯一，'
        '故基底判据恒取无关组，零向量不可作基底。' * 3)
new = ('\\ansblockgrayfalse % 括线模强制样本（承重墙判据冒烟：估高 >8 行·合成加长）\n'
       '\\begin{ansblock}[拓-004]\n% ans:拓-004\n'
       '\\ansitem{4}{(1)\\(0\\)；(2)\\(1\\)；(3)\\(1\\)；(4)\\(-1\\)}\n'
       '\\ansnote{详解}{' + fill + '}\n'
       '\\ansnote{点睛}{投影与数量积互化须验符号；等体积法求距离先补形再代入，避免建系盲区。}\n'
       '\\ansnote{追问}{若改为共面基底，表出系数不唯一，须另加定长约束方可定解。}\n'
       '\\end{ansblock}\n'
       '\\ansblockgraytrue % 括线模样本收束（默认灰底复位）')
tex = tex[:old.start()] + new + tex[old.end():]
with io.open(os.path.join(D, 'main.tex'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(tex)
head = '%% 括线模冒烟壳（波2·拓-004 合成长详解样本）\n\\def\\mthreepure{%d}\n\\input{main.tex}\n'
for name, flag in (('main-true.tex', 0), ('main-pure.tex', 1)):
    with io.open(os.path.join(D, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(head % flag)
print('[probe] 就位：拓-004 括线模合成样本（fill %d 单位≈%d 行）' % (len(fill), -(-len(fill) // 47)))
