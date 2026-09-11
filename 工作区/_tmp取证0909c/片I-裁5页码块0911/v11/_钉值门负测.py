# -*- coding: utf-8 -*-
"""钉值门负测（v11）：模拟 postproc 6g 回卷——素材探九变式1 答案值改回 \\sqrt{13}，
组装器须在素材加载后立即中止（非零退出＋门名报错），且不得写出 body.tex。
只在临时目录操作，不触生产件。"""
import os
import subprocess
import sys

SRC_DIR = r'C:/提示词/工作区/字替对照-0909/导学件答案册-v1'
TMP = r'C:/提示词/工作区/_tmp取证0909c/片I-裁5页码块0911/v11/_负测tmp'
os.makedirs(TMP, exist_ok=True)

# ① 篡改素材：全文 sqrt{7}→sqrt{13}（生产素材只读，写到 TMP）
mat = open(r'C:/提示词/工作区/_tmp取证0909c/片G/去答案0911/答案册素材0911.txt', encoding='utf-8').read()
assert r'\sqrt{7}' in mat
bad = mat.replace(r'\sqrt{7}', r'\sqrt{13}')
bad_mat = TMP + '/素材-回卷模拟.txt'
open(bad_mat, 'w', encoding='utf-8').write(bad)

# ② 脚本副本：仅 MAT 行改指篡改素材（正斜杠路径，Windows Python 可开）
lines = open(SRC_DIR + '/组装body.py', encoding='utf-8').read().splitlines(True)
hit = 0
for i, l in enumerate(lines):
    if l.startswith('MAT = '):
        lines[i] = "MAT = r'" + bad_mat + "'\n"
        hit += 1
assert hit == 1, hit
script = TMP + '/组装body-负测.py'
open(script, 'w', encoding='utf-8').write(''.join(lines))

# ③ 跑负测：期望非零退出＋stderr 含门名；期望 TMP 下无 body.tex 产出
r = subprocess.run([sys.executable, script], capture_output=True, text=True,
                   encoding='utf-8', errors='replace', cwd=TMP)
print('负测退出码 =', r.returncode)
print('stderr 尾 =', (r.stderr or '').strip().splitlines()[-1] if r.stderr else '(空)')
assert r.returncode != 0, '负测失败：门未拦截回卷值'
assert '钉值门触发' in (r.stderr or ''), '负测失败：报错非门名'
assert not os.path.exists(TMP + '/body.tex'), '负测失败：中止前已写出 body.tex'
print('负测 PASS：回卷值被钉值门拦截，组装中止无产出')
