# -*- coding: utf-8 -*-
"""_probe_overfull.py — 练习件册 true 档 Overfull\\vbox 12.99pt 归因探针（过程件，非产件）。"""
import os
import re
import subprocess

D = os.path.dirname(os.path.abspath(__file__))
XE = 'C:/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex.exe'
BODY = open(os.path.join(D, 'ansbook.tex'), encoding='utf-8').read()
SHELL = open(os.path.join(D, 'ansbook-true.tex'), encoding='utf-8').read()


def cut_block(body, key):
    b = '\\begin{ansblock}[' + key + ']'
    e = '\\end{ansblock}'
    i = body.find(b)
    assert i >= 0, key
    j = body.find(e, i) + len(e)
    return body[:i] + body[j:]


def run(name, body):
    p = os.path.join(D, name + '_body.tex')
    open(p, 'w', encoding='utf-8', newline='\n').write(body)
    sh = SHELL.replace('\\input{ansbook.tex}', '\\input{' + name + '_body.tex}')
    open(os.path.join(D, name + '.tex'), 'w', encoding='utf-8', newline='\n').write(sh)
    subprocess.run([XE, '-interaction=nonstopmode', name + '.tex'], cwd=D,
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
    log = open(os.path.join(D, name + '.log'), encoding='utf-8', errors='replace').read()
    m = re.search(r'Overfull[^\n]*', log)
    pages = len(re.findall(r'^\[\d+', log, re.M))
    print(name, 'overfull=', log.count('Overfull'), 'pages~', pages,
          (m.group(0)[:50] if m else ''))


RB = '\\raggedbottom' + '\n' + '\\begin{multicols}{2}'
run('probeC2', BODY.replace('\\begin{multicols}{2}', RB))          # raggedbottom
run('probeD2', cut_block(BODY, '2章-练-课时01-E16'))                 # 去 E16
run('probeE2', cut_block(cut_block(BODY, '2章-练-课时01-E16'),
                         '2章-练-课时01-E15'))                      # 去 E15+E16
run('probeF2', cut_block(cut_block(cut_block(BODY, '2章-练-课时01-E16'),
                                   '2章-练-课时01-E15'),
                         '2章-练-课时01-E14'))                      # 去 E14~E16
run('probeG2', cut_block(BODY, '2章-练-课时01-E14'))                 # 去 E14（最长详解）
run('probeH2', cut_block(BODY, '2章-练-课时01-E8'))                  # 去 E8（par\\noindent 详解）
