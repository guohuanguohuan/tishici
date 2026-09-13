# -*- coding: utf-8 -*-
r"""门-衔接覆盖.py — 衔接节练习件·知识点覆盖断言（照 manifest 注记核，臂H 片面新增）。

断言面（main.tex 剔注释后逐 \tieside 解析）：
  ①逐题难度词 ∈ {简单,中档,难}，且与题面库头标第4字段读数（批E §四 难度读数：
    简8＝练1/2/3/8/9/11/15/16＋中6＝练4/5/10/12/13/14＋难2＝练6/7）逐位相符。
  ②逐题知识点标 ∈ {一,二,三,四}（导学件知识导学分册 一判别式/二韦达/三方程组解法
    ＋探究点域 四＝直线与圆锥曲线位置关系：判定/弦长/切线）。
  ③覆盖断言：知识点集合 ≡ {一,二,三,四}（零缺漏）——衔接节知识体系全覆盖。
  ④题号连号 1..16 ＝ manifest 练键序 练1~16（在册核，与守恒门互证）。
用法: python 门-衔接覆盖.py     退出码: 0＝全过；1＝有红。红线：件树只读，零写入。
"""
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/衔接节'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/衔接节.manifest.json'

# 难度读数（题面库头标第4字段照录：存量 简/中/难，补题 0.65＝中、0.85 亲判简＝简单）
DIFF = ['简单', '简单', '简单', '中档', '中档', '难', '难',
        '简单', '简单', '中档', '简单', '中档', '中档', '中档', '简单', '简单']
# 知识点映射（导学件知识导学分册＋探究点域；账面登记见 值台账-衔接节.json「知识点映射」）
KN = ['二', '二', '二', '二', '一', '一', '二',
      '三', '三', '三', '三', '三', '三', '四', '四', '四']

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
body = '\n'.join(l.split('%', 1)[0] if not l.lstrip().startswith('%') else '' for l in src.split('\n'))
reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

ties = re.findall(r'\\tieside\{(简单|中档|难)\(知识点([一二三四])\)\}', body)
nums = [int(n) for n in re.findall(r'\\tihao\{(\d+)\}', body)]

check('\\tieside 计数=16（题题有标）', len(ties) == 16, f'{len(ties)}')
check('难度词序列≡题面库头标读数（简8＋中6＋难2）', [t[0] for t in ties] == DIFF,
      f'{[t[0] for t in ties]}')
check('知识点标序列≡映射账（一二三四域）', [t[1] for t in ties] == KN,
      f'{[t[1] for t in ties]}')
check('知识点覆盖断言：集合≡{一,二,三,四}（零缺漏）', set(t[1] for t in ties) == {'一', '二', '三', '四'},
      f'{sorted(set(t[1] for t in ties))}')
check('\\tihao 号序≡1..16 连号（在册核）', nums == list(range(1, 17)), f'{nums}')
manifest = json.load(open(MANIFEST, encoding='utf-8'))
keyseq = [k for k in manifest['键序'] if k.startswith('2章-练-')]
check('manifest 注记核：练习键 16 在册≡印面装配数', len(keyseq) == 16 and len(nums) == 16,
      f'manifest={len(keyseq)} 件={len(nums)}')

print()
print('衔接覆盖门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
