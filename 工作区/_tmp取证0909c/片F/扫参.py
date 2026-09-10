# -*- coding: utf-8 -*-
r"""片F 参数扫描：relpenalty × emergencystretch 矩阵（临时改动，跑完自动还原）
用法：python 扫参.py [ec列表，逗号分隔]
每档：改 qp-layout.tex＋postproc_daoxue.py → postproc → xelatex×2 → 记三0/页数/拉伸行 → 快照 PDF
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
PP = os.path.join(VF, 'postproc_daoxue.py')
SCAN = os.path.join(OUT, '拉伸行扫描.py')

EC_LIST = (sys.argv[1].split(',') if len(sys.argv) > 1 else
           ['0em', '0.25em', '0.5em', '0.75em', '1em', '1.5em', '2em'])


def read(p):
    return open(p, encoding='utf-8').read()


def write(p, s):
    open(p, 'w', encoding='utf-8', newline='').write(s)


def patch(ec, rel):
    lay = read(LAY)
    lay, n1 = re.subn(r'^\\emergencystretch=[\d.]+em', f'\\\\emergencystretch={ec}', lay,
                      count=1, flags=re.M)
    lay, n2 = re.subn(r'^\\relpenalty=\d+', f'\\\\relpenalty={rel}', lay, count=1, flags=re.M)
    assert n1 == 1 and n2 == 1, f'qp-layout 补丁失败 n1={n1} n2={n2}'
    write(LAY, lay)
    pp = read(PP)
    pp, n3 = re.subn(r'(\\\\begin\{multicols\}\{2\}\\n\\\\emergencystretch=)[\d.]+em',
                     lambda m: m.group(1) + ec, pp, count=1)
    assert n3 == 1, f'postproc 补丁失败 n3={n3}'
    write(PP, pp)


def build(tag, ec, rel):
    subprocess.run([sys.executable, 'postproc_daoxue.py'], cwd=VF, capture_output=True)
    for i in (1, 2):
        subprocess.run(['xelatex', '-interaction=nonstopmode', 'main.tex'], cwd=VF,
                       capture_output=True)
    log = read(os.path.join(VF, 'main.log'))
    e = len(re.findall(r'^! ', log, re.M))
    ov = len(re.findall(r'Overfull \\hbox', log))
    un = len(re.findall(r'Underfull \\hbox', log))
    mc = len(re.findall(r'Missing character', log, re.I))
    pg = re.search(r'Output written on main.pdf \((\d+) pages', log)
    pdf = os.path.join(OUT, f'档_{tag}.pdf')
    shutil.copy(os.path.join(VF, 'main.pdf'), pdf)
    subprocess.run([sys.executable, SCAN, pdf, '--json', os.path.join(OUT, f'_scan_{tag}.json'),
                    '--quiet'], capture_output=True, text=True, encoding='utf-8')
    sc = json.load(open(os.path.join(OUT, f'_scan_{tag}.json'), encoding='utf-8'))
    rows = [x for x in sc['rows'] if 40 < x['y'] < 786]
    ccc = [x for x in rows if x['kind'] == 'CJK-CJK']
    # 设计隙白名单（quad/2em）外的 CJK-CJK
    real = [x for x in ccc if not (23.0 < x['gap_pt'] < 25.0 or 11.5 < x['gap_pt'] < 13.5
                                   or 6.3 < x['gap_pt'] < 6.7 or 20.0 < x['gap_pt'] < 21.5)]
    print(f'{tag:14s} ec={ec:6s} rel={rel} err={e} ov={ov} un={un} mc={mc} '
          f'pg={pg.group(1) if pg else "?"} 空档行={len({(x["page"], x["y"]) for x in rows})} '
          f'CJK-CJK={len(ccc)}处/{len({(x["page"], x["y"]) for x in ccc})}行 '
          f'去设计={len(real)}处/{len({(x["page"], x["y"]) for x in real})}行')
    return {'tag': tag, 'ec': ec, 'rel': rel, 'err': e, 'ov': ov, 'un': un, 'mc': mc,
            'pg': pg.group(1) if pg else '?',
            'lines': len({(x['page'], x['y']) for x in rows}), 'cc': len(ccc),
            'cc_lines': len({(x['page'], x['y']) for x in ccc}),
            'real': len(real), 'real_lines': len({(x['page'], x['y']) for x in real}),
            'real_rows': real}


if __name__ == '__main__':
    lay0, pp0 = read(LAY), read(PP)
    results = []
    try:
        for ec in EC_LIST:
            patch(ec, 500)
            results.append(build(f'ec{ec}', ec, 500))
    finally:
        write(LAY, lay0)
        write(PP, pp0)
        print('--- 源码已还原 ---')
    json.dump(results, open(os.path.join(OUT, '_扫参结果.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\n汇总：')
    for r in results:
        print(f"ec={r['ec']:6s} rel={r['rel']} ov={r['ov']} un={r['un']} pg={r['pg']} "
              f"real={r['real']}处/{r['real_lines']}行")
        for x in r['real_rows']:
            print(f"     p{x['page']} y={x['y']} {x['left']!r}→{x['right']!r} {x['gap_pt']}pt")
