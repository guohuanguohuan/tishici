# -*- coding: utf-8 -*-
"""A1审计：驱动既有工具（六类底纹计数、空位公式扫描）跑四件"""
import subprocess, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = r"C:\提示词\高中数学\高中数学同步"
REP = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_reports"
FILES = {
    "X1": "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
    "I1": "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
    "B":  "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",
    "C":  "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx",
}
for tag, name in FILES.items():
    docx = os.path.join(SRC, name)
    r = subprocess.run([sys.executable, r"C:\提示词\工具\六类底纹计数.py", docx,
                        os.path.join(REP, f"底纹_{tag}.txt")],
                       capture_output=True)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace')
    open(os.path.join(REP, f"底纹_{tag}.txt"), 'w', encoding='utf-8').write(out)
    print(f"== {tag} 底纹 rc={r.returncode}")
    print(out.strip()[-2000:] if len(out) > 2000 else out.strip())

# 空位公式扫描（升级版三签名）
docs = [os.path.join(SRC, n) for n in FILES.values()]
r = subprocess.run([sys.executable, r"C:\提示词\工具\空位公式扫描.py"] + docs,
                   capture_output=True)
out = (r.stdout + r.stderr).decode('utf-8', 'replace')
open(os.path.join(REP, "空位扫描_四件.txt"), 'w', encoding='utf-8').write(out)
print("== 空位扫描 rc=", r.returncode)
print(out[-3000:])
