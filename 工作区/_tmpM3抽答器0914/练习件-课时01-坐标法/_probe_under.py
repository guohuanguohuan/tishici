# -*- coding: utf-8 -*-
"""_probe_under.py — multicolundershoot=14pt 消 Overfull 验证探针（过程件）。"""
import os
import re
import subprocess

D = os.path.dirname(os.path.abspath(__file__))
XE = 'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex.exe'
SHELL = open(os.path.join(D, 'ansbook-true.tex'), encoding='utf-8').read()
body = open(os.path.join(D, 'ansbook.tex'), encoding='utf-8').read()
body2 = body.replace('\\ansblockgrayfalse',
                     '\\ansblockgrayfalse\n% —— 平衡容差回调（末栏平衡微超 12.99pt＞sty 默认 8pt 吸收窗；'
                     'multicol 原生旋钮，sty 零改） ——\n\\multicolundershoot=14pt%')
open(os.path.join(D, 'probeU_body.tex'), 'w', encoding='utf-8', newline='\n').write(body2)
sh = SHELL.replace('\\input{ansbook.tex}', '\\input{probeU_body.tex}')
open(os.path.join(D, 'probeU.tex'), 'w', encoding='utf-8', newline='\n').write(sh)
for p in range(2):
    subprocess.run([XE, '-interaction=nonstopmode', 'probeU.tex'], cwd=D,
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
log = open(os.path.join(D, 'probeU.log'), encoding='utf-8', errors='replace').read()
print('overfull=', log.count('Overfull'), 'underfull=', log.count('Underfull'),
      'err=', len(re.findall(r'^!', log, re.M)), 'miss=', log.count('Missing character'))
import fitz
d = fitz.open(os.path.join(D, 'probeU.pdf'))
print('pages=', len(d))
d.close()
