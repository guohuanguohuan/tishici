# -*- coding: utf-8 -*-
r"""编译三零-回流制.py — S5-W4 阶段二·四卷双档编译（各 ×2 遍）＋三零读数（Error/Overfull/Missing char）。
读数落 _M2P1/_编译三零读数.txt。"""
import io
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
XELATEX = r'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex.exe'
ROOT = r'C:/提示词/工作区/_tmp换装正装0914'
VOLUMES = [os.path.join(ROOT, p) for p in
           ('M2测评滚动/测评卷', 'M2测评滚动/滚动卷A', 'M2测评滚动/滚动卷B', 'P1测评本/测评卷')]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_编译三零读数.txt')

rep = []
for d in VOLUMES:
    name = os.path.basename(os.path.dirname(d)) + '/' + os.path.basename(d)
    for shell in ('main', 'main-pure'):
        passes = []
        ok = True
        for p in (1, 2):
            r = subprocess.run([XELATEX, '-interaction=nonstopmode', '-halt-on-error',
                                shell + '.tex'], cwd=d, capture_output=True)
            log = io.open(os.path.join(d, shell + '.log'), encoding='utf-8', errors='ignore').read()
            err = len(re.findall(r'^!', log, re.M))
            ovf = len(re.findall(r'Overfull \\[hv]box', log))
            und = len(re.findall(r'Underfull \\[hv]box', log))
            mis = len(re.findall(r'Missing character', log))
            ans = len(re.findall(r'M3-ANSKEY: ', log))
            pages = re.findall(r'Output written on .*? \((\d+) page', log)
            passes.append('遍%d exit=%d 错%d 溢%d under%d 缺字%d ANSKEY=%d 页%s'
                          % (p, r.returncode, err, ovf, und, mis, ans, pages[-1] if pages else '?'))
            if r.returncode != 0 or err or ovf or mis:
                ok = False
        rep.append('%s %s：%.60s' % (name, shell, '｜'.join(passes)))
        if not ok:
            rep.append('  红｜三零未过或编译失败（%s/%s）' % (name, shell))
        print(rep[-1])

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(rep) + '\n')
print('读数落盘：', OUT)
sys.exit(0)
