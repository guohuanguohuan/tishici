# -*- coding: utf-8 -*-
"""②C_01_T3T4dry复核.py — T6b 前置互斥证据：T3/T4 dry 复核十件（②-B 回写态副本），
应 0 改写（T3/T4 已在 ②-B 收敛），证明 T6b 撤 C6D4E3 不会遗留未识别的 T3/T4 工作面。
纯 lxml（无 COM），逐件超时重试兜底同步盘瞬锁。落 报告/②C_T3T4dry_前置复核.md"""
import sys, io, os, subprocess, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DST = os.path.join(ROOT, '工作区', '选必1成书修复-0905', '②工具', '副本')
RPT = os.path.join(ROOT, '工作区', '选必1成书修复-0905', '②工具', '报告', '②C_T3T4dry_前置复核.md')
NAMES = [
    '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
]
TOOLS = [('T3 统计段独立成行器', os.path.join(ROOT, '工具', '统计段独立成行器.py')),
         ('T4 题型名前缀去除器', os.path.join(ROOT, '工具', '题型名前缀去除器.py'))]


def run(tool, f):
    for att in range(1, 4):
        try:
            p = subprocess.run(['python', tool, f, '--dry-run'], capture_output=True,
                               text=True, encoding='utf-8', timeout=300, cwd=ROOT)
        except subprocess.TimeoutExpired:
            print('   timeout att%d' % att, flush=True); time.sleep(15); continue
        if p.returncode == 0 and 'Traceback' not in (p.stderr or ''):
            return p.stdout.strip()
        print('   fail att%d rc=%d %s' % (att, p.returncode, (p.stderr or '')[-200:]), flush=True)
        time.sleep(15)
    return None


blocks = []
summary = []
for label, tool in TOOLS:
    for n in NAMES:
        f = os.path.join(DST, n)
        print('>>> %s %s' % (label[:2], n[:28]), flush=True)
        out = run(tool, f)
        blocks.append('%s\n' % (out if out else '### %s — %s\n!! 未通过\n' % (label, n)))
        if out is None:
            summary.append((label, n, 'RUNFAIL', ''))
            continue
        lines = out.splitlines()
        key = ''
        zero = False
        if label.startswith('T3'):
            key = next((l for l in lines if l.startswith('拆分：')), lines[0] if lines else '')
            m1 = re.search(r'节统计段\s*(\d+)', key)
            m2 = re.search(r'题型统计段\s*(\d+)', key)
            m3 = re.search(r'幂等跳过（已独立）\s*(\d+)', key)
            zero = bool(m1 and m2 and m1.group(1) == '0' and m2.group(1) == '0')
            key += '　⟹ 幂等跳过 %s' % (m3.group(1) if m3 else '?')
        else:
            key = next((l for l in lines if '改写' in l), lines[0] if lines else '')
            m1 = re.search(r'改写\s*(\d+)', key)
            m2 = re.search(r'幂等\s*(\d+)', key)
            m3 = re.search(r'节名不符保留\s*(\d+)', key)
            zero = bool(m1 and m1.group(1) == '0')
            key += '　⟹ 幂等 %s／不符保留 %s' % (m2.group(1) if m2 else '?', m3.group(1) if m3 else '?')
        summary.append((label, n, 'PASS(0改写)' if zero else '!! CHECK', key))
        print('   ', key, flush=True)

with open(RPT, 'w', encoding='utf-8') as f:
    f.write('# ②C T6b 前置互斥复核 — T3/T4 dry 十件 0 改写证明\n\n')
    f.write('- 时点：%s\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
    f.write('- 对象：`②工具/副本/` 十件（刚从同步盘 ②-B 回写终态重新复制，MD5 见 ②C_副本重置_MD5.md）\n')
    f.write('- 依据：②工具对账.md §四互斥纪律 3「T6b 撤 C6D4E3 底纹是识别口径断点：T3/T4 以 C6D4E3 识别题型标题，必须先于 T6b」\n')
    f.write('- 目的：T6b 执行前证明 T3/T4 工作面已收敛（0 改写），即 T6b 撤底纹不会造成 T3/T4 漏识别、无遗留处置\n\n')
    f.write('## 汇总\n\n| 工具 | 件 | 判定 | 关键行 |\n|---|---|---|---|\n')
    for (label, n, st, key) in summary:
        f.write('| %s | %s | %s | %s |\n' % (label, n.replace('人教B版选必1 ', ''), st, key.replace('|', '｜')))
    f.write('\n## 逐件原始输出\n\n')
    f.write('\n'.join(blocks))
print('REPORT ->', RPT, flush=True)
bad = [s for s in summary if not s[2].startswith('PASS')]
print('SUMMARY total=%d pass=%d nonpass=%d' % (len(summary), len(summary) - len(bad), len(bad)), flush=True)
for b in bad:
    print('  NONPASS:', b[0], b[1], b[2], b[3], flush=True)
