# -*- coding: utf-8 -*-
"""⑧轮债1 A3：钉死命令跑 六类底纹计数.py ×12（⑧_六类_*，不覆盖⑥轮报告）；同步盘瞬时锁重试。"""
import subprocess, sys, time, os

ROOT = r'C:/提示词'
REP = r'工作区/选必1成书修复-0905/②工具/报告'
CASES = [
    ('B',   '高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', '--jlp'),
    ('C',   '高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', '--jlp'),
    ('E',   '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', '--jlp'),
    ('F',   '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', '--jlp'),
    ('G',   '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', '--jlp'),
    ('H',   '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', '--jlp'),
    ('I1',  '高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', ''),
    ('I2',  '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', ''),
    ('X1',  '高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', ''),
    ('X2',  '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', ''),
    ('SM',  '高中数学/高中数学同步/人教B版选必1·使用说明.docx', ''),
    ('TOC', '高中数学/高中数学同步/人教B版选必1·册目录页.docx', ''),
]
NAME = {'B': 'B讲练1上', 'C': 'C讲练1下', 'E': 'E讲练92', 'F': 'F讲练90', 'G': 'G讲练68',
        'H': 'H讲练89', 'I1': 'I1清单1', 'I2': 'I2清单2', 'X1': 'X1衔接1', 'X2': 'X2衔接2',
        'SM': 'SM使用说明', 'TOC': 'TOC册目录页'}

fails = []
for code, docx, flag in CASES:
    out_txt = '%s/⑧_六类_%s.txt' % (REP, NAME[code])
    cmd = [sys.executable, '工具/六类底纹计数.py', docx, out_txt] + ([flag] if flag else [])
    ok = False
    for attempt in range(1, 5):   # 同步盘瞬时锁——重试不判死
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode == 0:
            ok = True
            break
        print('%s 第%d次失败 rc=%d stderr=%s' % (code, attempt, r.returncode, (r.stderr or '')[-200:]))
        time.sleep(2 * attempt)
    concl = ''
    if ok:
        with open(os.path.join(ROOT, out_txt), encoding='utf-8') as f:
            for line in f:
                if line.startswith('结论:'):
                    concl = line.strip()
                    break
    print('%-3s rc=0 %s ｜ %s' % (code, 'OK' if ok else 'FAIL', concl))
    if not ok:
        fails.append(code)
print('A3 运行汇总: %s' % ('12/12 跑通' if not fails else '失败件 %s' % fails))
