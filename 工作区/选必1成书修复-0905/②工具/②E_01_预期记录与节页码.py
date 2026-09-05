# -*- coding: utf-8 -*-
"""②E_01_预期记录与节页码.py — ②-E 链条第一步（交接§三.5 序：节页码先行）。
①由 ②-D 终报权威页数（T7后 15/15/65/62/32/5/58/58/47/73＝430）合成 预期盖章记录_②E.md
  （同 册级连续页码.py --record 表格式，供 节页码定位.py --record 与 册目录重造 输入）；
②跑 工具/节页码定位.py @parts_②E.json --record 预期记录 --json → 节页码_②E_预期.json。
预期值仅作先行联动底稿；盖章（②E_04）实测后 三源恒等核验 兜底，漂移则全链以实测重造。"""
import sys, io, os, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RPT = os.path.join(HERE, '报告')

TEN = [
    ('清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', '第1章·清单'),
    ('衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', '第1章·衔接'),
    ('上61', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', '第1章·讲练'),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', '第1章·讲练'),
    ('清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', '第2章·清单'),
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', '第2章·衔接'),
    ('92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', '第2章·讲练'),
    ('90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', '第2章·讲练'),
    ('68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', '第2章·讲练'),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', '第2章·讲练'),
]
# ②-D 终报 §六 权威页数（T7后，COM 实测；同步盘=副本终态已 MD5 锚定）
PAGES = {'清单1': 15, '衔接1': 15, '上61': 65, '下79': 62, '清单2': 32, '衔接2': 5,
         '92': 58, '90': 58, '68': 47, '89': 73}
ORDER = ['衔接1', '清单1', '上61', '下79', '衔接2', '清单2', '92', '90', '68', '89']
PART = {'衔接1': (1, 1), '清单1': (2, 2), '上61': (3, 3), '下79': (3, 3),
        '衔接2': (4, 4), '清单2': (5, 5), '92': (6, 6), '90': (6, 6), '68': (6, 6), '89': (6, 6)}
NAME = {sh: n for sh, n, _ in TEN}
TAG = {sh: t for sh, _, t in TEN}

# ① 预期记录
rows, total = [], 0
start_of = {}
for sh in ORDER:
    pi, bk = PART[sh]
    part_pages = sum(PAGES[s] for s in ORDER if PART[s][0] == pi)
    start_of[sh] = start_of.get(sh) or (1 + sum(PAGES[s] for s in ORDER if PART[s][0] == pi and ORDER.index(s) < ORDER.index(sh)))
    rows.append('| P%d | 本%d | %s | %d | %d | %s | %d |' % (pi, bk, NAME[sh], PAGES[sh], start_of[sh], TAG[sh], part_pages))
    total += PAGES[sh]
rec = ['# 部分独立页码盖章记录（同串版） — 人教B版选必1',
       '',
       '【②-E 预期版底稿（2026-09-06）：数字＝②-D 终报 §六 T7后 COM 实测页数推算，非盖章实测；',
       '供 节页码定位/册目录重造/装订单联动 先行联动；权威版＝②E_盖章记录.md（册级连续页码.py --record），',
       '三源恒等核验以实测为准，漂移则全链重造。】',
       '',
       '| 部分 | 本 | 件 | 页数 | start | 件标识 | N（部分总页数） |',
       '|---|---|---|---|---|---|---|'] + rows + [
       '', '恒等式：每部分首件start=1；同部分后件start＝前件start+页数；N＝部分内各件页数之和；全册合计%d页。' % total]
open(os.path.join(RPT, '预期盖章记录_②E.md'), 'w', encoding='utf-8').write('\n'.join(rec) + '\n')
print('预期记录落盘（全册合计%d页；P3=%d、P6=%d）' % (
    total,
    sum(PAGES[s] for s in ORDER if PART[s][0] == 3),
    sum(PAGES[s] for s in ORDER if PART[s][0] == 6)))

# ② 节页码定位（预期 start 底稿）
out_json = os.path.join(RPT, '节页码_②E_预期.json')
r = subprocess.run([sys.executable, os.path.join(ROOT, '工具', '节页码定位.py'),
                    '@' + os.path.join(HERE, 'parts_②E.json'),
                    '--record', os.path.join(RPT, '预期盖章记录_②E.md'), '--json'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace',
                   timeout=1200, cwd=ROOT)
print('节页码定位 exit=%d' % r.returncode)
print((r.stderr or '')[:800])
open(out_json, 'w', encoding='utf-8').write(r.stdout or '')
import json
payload = json.loads(r.stdout)
zhit = [f['name'][:20] for f in payload['files'] if f.get('zero_hit')]
nsec = sum(len(f['sections']) for f in payload['files'])
print('节页码预期版：%d 件、节命中合计 %d、0命中件=%s' % (len(payload['files']), nsec, zhit))
print('DONE_01')
