# -*- coding: utf-8 -*-
r"""片F 参数扫描 v2：\tolerance 档（rel=500, ec=1em 固定，临时改动跑完还原）
用法：python 扫参_tol.py [tol列表]
"""
import os
import re
import shutil
import subprocess
import sys
import json

VF = r'C:\提示词\工作区\字替对照-0909\variantF'
OUT = r'C:\提示词\工作区\_tmp取证0909c\片F'
LAY = os.path.join(VF, 'qp-layout.tex')
SCAN = os.path.join(OUT, '拉伸行扫描.py')
TOLS = (sys.argv[1].split(',') if len(sys.argv) > 1 else
        ['9999', '6000', '4000', '3000', '2000', '1500'])


def read(p):
    return open(p, encoding='utf-8').read()


def write(p, s):
    open(p, 'w', encoding='utf-8', newline='').write(s)


def build(tag, tol):
    subprocess.run([sys.executable, 'postproc_daoxue.py'], cwd=VF, capture_output=True)
    for i in (1, 2):
        subprocess.run(['xelatex', '-interaction=nonstopmode', 'main.tex'], cwd=VF,
                       capture_output=True)
    log = read(os.path.join(VF, 'main.log'))
    e = len(re.findall(r'^! ', log, re.M))
    ov = len(re.findall(r'Overfull \\hbox', log))
    un = len(re.findall(r'Underfull \\hbox', log))
    pg = re.search(r'Output written on main.pdf \((\d+) pages', log)
    pdf = os.path.join(OUT, f'档_{tag}.pdf')
    shutil.copy(os.path.join(VF, 'main.pdf'), pdf)
    subprocess.run([sys.executable, SCAN, pdf, '--json', os.path.join(OUT, f'_scan_{tag}.json'),
                    '--quiet'], capture_output=True, text=True, encoding='utf-8')
    sc = json.load(open(os.path.join(OUT, f'_scan_{tag}.json'), encoding='utf-8'))
    rows = [r for r in sc['rows'] if 40 < r['y'] < 786]

    def design(r):
        if r['left'] in set(']．◆'):
            return True
        if r['left'] == '.' and r['gap_pt'] > 8:
            return True
        if r['left'] == '；' and r['right'] in 'ABCD':
            return True
        if r['gap_pt'] > 40:
            return True
        return False
    real = [r for r in rows if not design(r)]
    b5 = [r for r in real if r['gap_pt'] > 5]
    # p3 变式1 行 式→1 空档
    v1 = [r for r in real if r['page'] == 3 and 595 < r['y'] < 610]
    print(f'{tag:12s} tol={tol:5s} ov={ov} un={un} err={e} pg={pg.group(1) if pg else "?"} '
          f'去设计={len(real)} >5pt={len(b5)}处/{len({(r["page"],r["y"]) for r in b5})}行 '
          f'p3变式行={[(r["left"],r["right"],r["gap_pt"]) for r in v1]}')
    return {'tag': tag, 'tol': tol, 'ov': ov, 'un': un, 'real': len(real),
            'b5': len(b5), 'v1': [(r['left'], r['right'], r['gap_pt']) for r in v1]}


if __name__ == '__main__':
    lay0 = read(LAY)
    res = []
    try:
        for tol in TOLS:
            lay = lay0
            lay, n = re.subn(r'^\\tolerance=\d+', f'\\\\tolerance={tol}', lay, count=1, flags=re.M)
            assert n == 1, 'tolerance 补丁失败'
            write(LAY, lay)
            res.append(build(f'tol{tol}', tol))
    finally:
        write(LAY, lay0)
        print('--- 源码已还原 ---')
    json.dump(res, open(os.path.join(OUT, '_扫参_tol.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
