# -*- coding: utf-8 -*-
#
# 收编：2026-08-27 选必1整册任务·F2收尾（来源轮次：A4样张首创五杠杆 → C5参数化定稿；此为工具文件夹唯一常驻版，A4/C5桌面scripts副本不再维护）
#
# 用法: python 工具/短行合并回退.py <decisions.json> <unpack_dir> <lect:0|1> <ans_efflen阈值，负数=不回退ANS>
# 功能: 按样张批准参数保守回退合并决策（讲部全放弃＋解答区接续段eff_len≥阈值保留换行）；每次须从 候选与决策.py 重建后只跑一次，重复运行会叠加

"""revert.py — 按样张批准参数回退合并决策（讲部全部放弃＋解答区接续段eff_len≥TH保留换行）
用法: python revert.py <decisions.json> <unpack_dir> <lect:0|1> <ans_efflen_threshold>
threshold<0 表示不回退ANS。重复运行会叠加——每次从gen_decisions重建后只跑一次。
"""
import sys, io, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from 紧凑化公共库 import *

DJ = os.path.abspath(sys.argv[1])
UNPACK = os.path.abspath(sys.argv[2])
LECT = sys.argv[3] == '1'
TH = float(sys.argv[4])

d = json.load(open(DJ, encoding='utf-8'))
tree, root, body = load(os.path.join(UNPACK, 'word', 'document.xml'))
kids = list(body)
n_lect = n_ans = 0
for x in d['items']:
    if x['决策'] != '合并':
        continue
    if x['zone'] == 'LECT' and LECT:
        x['决策'] = '保留'
        x['理由'] = '保守回退：讲部条目讲解合并整体放弃（层次优先；样张批准参数）'
        n_lect += 1
        continue
    if x['zone'] == 'ANS' and TH >= 0:
        t = para_text(kids[x['段索引']])
        if eff_len(t) >= TH:
            x['决策'] = '保留'
            x['理由'] = '保守回退：接续段较长(eff_len=%s≥%s)，并入成墙不利层次，保留换行（样张批准参数）' % (eff_len(t), TH)
            n_ans += 1
json.dump(d, open(DJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 重写review文件为最终版
OUT_TXT = DJ.rsplit('.', 1)[0] + '_最终决策清单.txt'
from collections import Counter
c = Counter(x['决策'] for x in d['items'])
with open(OUT_TXT, 'w', encoding='utf-8') as f:
    f.write('杠杆⑤短行合并逐条决策清单·最终版（讲部整体放弃=%s，ANS接续段eff_len≥%s保留）\n' % (LECT, TH))
    f.write('铁律=零字符增删，只动段落边界；合计初判%d条\n\n' % len(d['items']))
    for x in d['items']:
        f.write('%-10s %-4s %-4s %-8s %s\n' % (x['key'], x['kind'], x['zone'], x['决策'], x['原文摘要']))
    for b in d.get('items_br', []):
        f.write('BR       段%s   存量br  保留   %s\n' % (b['段索引'], b['上下文']))
print('回退讲部%d条，解答区eff_len>=%s共%d条；最终统计: %s' % (n_lect, TH, n_ans, dict(c)))
print('最终清单:', OUT_TXT)
