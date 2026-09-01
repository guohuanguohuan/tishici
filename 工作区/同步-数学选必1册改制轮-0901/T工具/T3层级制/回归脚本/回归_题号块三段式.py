# -*- coding: utf-8 -*-
"""回归_题号块三段式.py — 层级制题号/条目号改版工具回归（A'改制轮·工具债③·T3）
场景：①旧全局号B副本→层级制重编（61题节内连续＋2条目＋区间括注联动＋文件名恒等）
     ②幂等二跑（文本改写=0）③层级制输入漏参硬失败（续卷防呆）④--sec-continue跨卷接续
     ⑤--sec-start显式映射。全部在工作区副本上跑，禁止触碰产出文件夹。"""
import sys, os, shutil, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
D = os.path.join(ROOT, '测试副本')
TOOL = r'C:\提示词\工具\题号块三段式.py'
SRC_B = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
T1 = os.path.join(D, 'R1_B层级制（61题）.docx')
T2 = os.path.join(D, 'R2_B续卷（61题）.docx')
T3 = os.path.join(D, 'R3_B显式映射（61题）.docx')

ok = True
def gate(cond, msg):
    global ok
    print(('  PASS ' if cond else '  FAIL ') + msg)
    ok = ok and cond

def run(*args):
    r = subprocess.run([sys.executable, TOOL] + list(args), capture_output=True, text=True,
                       encoding='utf-8', errors='replace', cwd=D)
    return r

def main():
    shutil.copyfile(SRC_B, T1)
    shutil.copyfile(SRC_B, T2)
    shutil.copyfile(SRC_B, T3)
    # ① 旧全局号 → 层级制
    r1 = run(T1, os.path.join(D, 'R1_登记.md'))
    gate(r1.returncode == 0 and '题族 61（1.1.1=10;1.1.2=4;1.1.3=10;1.2.1=9;1.2.2=7;1.2.3=8;1.2.4=13）' in r1.stdout
         and '条目族 2' in r1.stdout and '文件名恒等 题61' in r1.stdout,
         '①旧全局号重编：61题七节序列＋条目2＋文件名恒等61')
    gate('区间括注删 7' in r1.stdout, '①区间括注联动：删7处（授权差异②）')
    # ② 幂等二跑
    r2 = run(T1, os.path.join(D, 'R1_登记_idem.md'))
    gate(r2.returncode == 0 and '文本改写 0' in r2.stdout and '幂等跳过 题61/条2' in r2.stdout,
         '②幂等：二跑文本改写0、题61/条2全跳过')
    # ③ 层级制输入漏参硬失败（先编成层级制，再以错位起点重跑）
    r_pre = run(T2, os.path.join(D, 'R2_pre.md'))
    r3 = run(T2, os.path.join(D, 'R2_fail.md'), '--sec-start', '1.1.1=2')
    gate(r_pre.returncode == 0 and r3.returncode != 0 and '节内期望序号' in (r3.stderr + r3.stdout),
         '③层级制输入序列错位即硬失败（漏参防呆）')
    # ④ --sec-continue 跨卷接续（T2已层级化起始1；还原旧态后以T1为前卷重编）
    shutil.copyfile(SRC_B, T2)
    r4 = run(T2, os.path.join(D, 'R2_登记.md'), '--sec-continue', T1)
    gate(r4.returncode == 0 and '1.1.1=20;1.1.2=8;1.1.3=20;1.2.1=18;1.2.2=14;1.2.3=16;1.2.4=26' in r4.stdout,
         '④--sec-continue：各节起始=前卷末号+1（1.1.1→11..20）')
    # ⑤ --sec-start 显式映射
    r5 = run(T3, os.path.join(D, 'R3_登记.md'), '--sec-start', '1.1.1=101')
    gate(r5.returncode == 0 and '1.1.1=110' in r5.stdout and '1.1.2=4' in r5.stdout,
         '⑤--sec-start：1.1.1=101..110、其余节缺省1')
    print('回归结论：' + ('通过' if ok else '不通过'))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
