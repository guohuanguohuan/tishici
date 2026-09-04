# -*- coding: utf-8 -*-
"""十件导出齐后驱动：页尾空白断言（子步5封板项）＋v2断言①②⑤复跑（子步6封板项）。"""
import sys, io, os, shutil, subprocess, json
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

WS = r'C:\提示词\工作区\同步-数学选必1复合修复-0903'
PDF = os.path.join(WS, '子步5', 'pdf')
V2 = os.path.join(WS, '子步6', 'v2断言')
CODES = ['X1', 'I1', 'B', 'C', 'X2', 'I2', 'E', 'F', 'G', 'H']

# ①页尾空白断言
pairs = ['%s=%s' % (c, os.path.join(PDF, c + '.pdf')) for c in CODES]
r = subprocess.run([sys.executable, r'C:\提示词\工具\图定尺寸断言器.py', '--page-tail',
                    '--out', os.path.join(WS, '子步5', 'pagetail_子步5')] + pairs,
                   capture_output=True, text=True)
print(r.stdout[-1500:])
print(r.stderr[-500:] if r.returncode else '')

# ②PDF归集到 v2断言/pdf
for c in CODES:
    src = os.path.join(PDF, c + '.pdf')
    dst = os.path.join(V2, 'pdf', c + '.pdf')
    if os.path.exists(src):
        shutil.copy2(src, dst)
# ③首页裁剪＋断言①②⑤（含阴性对照）
NEG = r'C:\提示词\工作区\体系-双栏首页与PDFCreator主路径-0903\阴性对照证据\衔接2缺陷态.pdf'
for args in (['--make-p1'], ['--run', '--negative', NEG, '--neg-code', 'X2']):
    r = subprocess.run([sys.executable, r'C:\提示词\工具\首页断言集执行器.py'] + args +
                       ['--out', V2] + ['%s=x' % c for c in CODES],
                       capture_output=True, text=True)
    print(r.stdout[-1200:])
    print(r.stderr[-500:] if r.returncode else '')
print('=== 驱动完成 ===')
