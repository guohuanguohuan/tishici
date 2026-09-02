# -*- coding: utf-8 -*-
"""A''通用全链驱动：归一→线性数学→题号重编→题干底纹→答案值→双栏→页数。用法: python 全链.py <docx> <linkage|base> [navtable]"""
import subprocess, sys, os
T = r'C:\提示词\工具'
f = sys.argv[1]; mode = sys.argv[2] if len(sys.argv) > 2 else 'base'
navt = ['--navtable'] if len(sys.argv) > 3 and sys.argv[3] == 'navtable' else []
reg = os.path.splitext(os.path.basename(f))[0] + '-reg.md'

def run(tool, *args, tag=''):
    r = subprocess.run([sys.executable, os.path.join(T, tool)] + list(args),
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    ok = r.returncode == 0
    tail = (r.stdout or r.stderr).strip().split('\n')[-3:]
    print('[%s]%s %s' % ('OK' if ok else 'FAIL', tag, ' | '.join(tail)[:220]))
    if not ok:
        print(r.stderr[-1200:]); sys.exit(1)

run('归一签名.py', f, '--mode', 'both', tag='归一')
run('创作句线性数学签名.py', f, '--priority', 'all', tag='线性数学')
if mode == 'qingdan':
    pass                                  # 清单件：条目号维持（题号工具跳过）、题干底纹整件跳过
else:
    if mode == 'linkage':
        run('题号块三段式.py', f, reg, '--linkage', tag='题号')
    else:
        run('题号块三段式.py', f, reg, tag='题号')
    run('解析块浅底挂载.py', f, tag='题干底纹')
run('答案值分型改标.py', f, tag='答案值')
run('双栏改制工具.py', f, *(navt), tag='双栏')
run('word_check.py', f, tag='页数')
