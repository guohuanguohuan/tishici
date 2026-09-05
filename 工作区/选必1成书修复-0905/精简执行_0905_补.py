# -*- coding: utf-8 -*-
# 补充修边：总控 L56 新括注与主句措辞重复，收敛一字（同纪律：唯一命中断言）
# 注记（2026-09-06 收尾-A·复审N8处置）：本脚本＝执行时点存档，内嵌 old/new 与注记仅反映执行当时文本；盘上终态已随精简轮收紧，逐字重跑将被唯一命中断言安全拦截，勿以本脚本内容为现行口径依据。
import io, os
BASE = r'C:\提示词'
ZK = os.path.join(BASE, '高中同步总控.md')
LOG = os.path.join(BASE, '工作区', '选必1成书修复-0905', '精简对账.md')
old = '照公共规则§11现行文本执行（要素枚举均照公共规则§11现行文本——含部分封面'
new = '照公共规则§11现行文本执行（要素枚举同该条款——含部分封面'
s = io.open(ZK, encoding='utf-8', newline='').read()
assert s.count(old) == 1, '未唯一命中'
before = len(s)
s = s.replace(old, new, 1)
io.open(ZK, 'w', encoding='utf-8', newline='').write(s)
print('高中同步总控.md: %d → %d（净减 %d）' % (before, len(s), before - len(s)))
# 对账补登
t = io.open(LOG, encoding='utf-8', newline='').read()
t = t.replace('| 高中同步总控.md | 20183 | 19977 | 206 | ≤20,000 | 是 |',
              '| 高中同步总控.md | 20183 | %d | %d | ≤20,000 | 是 |' % (len(s), 20183 - len(s)))
t = t.replace('| 重申合并 | 12 | 339 |', '| 重申合并 | 13 | 347 |')
row = '| 64 | 高中同步总控.md | L56 | 重申合并 | %d | %d | %d | 新括注与主句「照§11现行文本」措辞重复，收敛为「同该条款」；指引对象不变。 |' % (len(old), len(new), len(old) - len(new))
t = t.replace('\n\n', '\n' + row + '\n') if False else t
# 追加到逐处对账表尾
lines = t.split('\n')
for i in range(len(lines) - 1, -1, -1):
    if lines[i].startswith('| 63 |'):
        lines.insert(i + 1, row)
        break
io.open(LOG, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('对账已补登')
