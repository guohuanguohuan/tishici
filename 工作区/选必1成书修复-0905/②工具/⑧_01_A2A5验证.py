# -*- coding: utf-8 -*-
"""⑧轮债1 A2/A5 验证：12件题量对照（锚值 vs 修后提取）＋A5回归件改后逐项比对。只读。"""
import sys, json, collections
sys.path.insert(0, r'C:/提示词/工具')
from extract_structure import structure   # 先导入（自重包 stdout）

BASE = r'C:/提示词/高中数学/高中数学同步'
CASES = [  # (件代号, 文件名, 期望题量锚)
    ('B',  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 61),
    ('C',  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 79),
    ('E',  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 92),
    ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 90),
    ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 68),
    ('H',  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 89),
    ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 0),
    ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 0),
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 29),
    ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 13),
    ('SM', '人教B版选必1·使用说明.docx', 2),   # ⑥轮口径值＝题号块签名段数2（图例演示段口径）
    ('TOC', '人教B版选必1·册目录页.docx', 0),
]
print('==== A2 修后提取按件型分列核验 ====')
rows = []
all_ok = True
for code, fn, exp in CASES:
    s = structure(BASE + '/' + fn)
    qs = s['questions']
    n = len(qs)
    ok = (n == exp)
    all_ok &= ok
    kinds = collections.Counter(x['kind'] for x in s['items'])
    diffs = dict(collections.Counter(x['diff'] for x in qs))
    rows.append({'code': code, 'file': fn, '锚值': exp, '修后提取': n, 'PASS': ok,
                 'kind计数': dict(sorted(kinds.items())), 'diff分布': diffs})
    print('%-3s 锚=%-3d 修后=%-3d %s kind=%s' % (code, exp, n, 'PASS' if ok else '←≠ FAIL', dict(sorted(kinds.items()))))
print('A2 汇总: %s' % ('12/12 全中' if all_ok else '存在 FAIL'))

print()
print('==== A5 回归件改后比对（物理简单卷14题） ====')
REG = r'C:/提示词/高中物理/高中物理同步/人教版必修3 第10章 静电场中的能量·简单卷（14题）.docx'
pre = json.load(open(r'C:/提示词/工作区/选必1成书修复-0905/②工具/⑧_05_A5回归件_改前基线.json', encoding='utf-8'))
s = structure(REG)
qs = s['questions']
kinds = dict(collections.Counter(x['kind'] for x in s['items']))
cont = all(int(qs[k]['no']) == int(qs[k-1]['no']) + 1 for k in range(1, len(qs)))
now = {'questions': [{'no': x['no'], 'diff': x['diff'], 'sec': x['sec'],
                      'start': x['start'], 'end': x['end']} for x in qs],
       'items_kind': dict(sorted(kinds.items())),
       'items_text': [x['text'] for x in s['items']]}
same_q = now['questions'] == pre['questions']
same_kind = now['items_kind'] == pre['items_kind']
same_text = now['items_text'] == pre['items_text']
print('questions=%d（改前 %d） 逐号连续=%s questions逐项全等=%s' % (len(qs), len(pre['questions']), cont, same_q))
print('items kind 计数全等=%s（%s vs %s）' % (same_kind, now['items_kind'], pre['items_kind']))
print('items text 序列全等=%s' % same_text)
print('A5 汇总: %s' % ('改后＝改前（14 连续＋kind 逐项不变）PASS' if (len(qs) == 14 and cont and same_q and same_kind and same_text) else 'FAIL'))

out = r'C:/提示词/工作区/选必1成书修复-0905/②工具/⑧_02_A2A5_实测.json'
json.dump({'A2': rows, 'A2汇总': '12/12' if all_ok else 'FAIL',
           'A5': {'改后questions': now['questions'], '改后kind': now['items_kind'],
                  'questions全等': same_q, 'kind全等': same_kind, 'text全等': same_text,
                  '结论': 'PASS' if (len(qs) == 14 and cont and same_q and same_kind and same_text) else 'FAIL'}},
          open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('落盘:', out)
