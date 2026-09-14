# -*- coding: utf-8 -*-
"""_台账印面号回填.py — ①真数据红销案：课时02 值台账 印面号 15 键回填。
口径：以件内 ansitem 首参为准（试产报告 §四.2 主裁），抽册器同源解析（工具/答案抽册器.parse_piece）
取 键→印面号 权威映射；写入对象＝值台账-课时02.json items[].印面号 字段，其余字段零动。
红线：成卷件树除本台账外只读；零 git。"""
import importlib.util
import json
import os
import sys

HERE = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
TOOL = os.path.join(REPO, '工具', '答案抽册器.py')
PIECE = os.path.join(REPO, '工作区', 'M3-第2章量产0913', '成卷', '导学件',
                     '课时02-倾斜角与斜率')
LEDGER = os.path.join(PIECE, '值台账-课时02.json')

_spec = importlib.util.spec_from_file_location('ansbook_tool', TOOL)
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

# 1) 件内权威映射（与抽册侧同源解析：锚 % ans:键 ＋ \ansitem{N}）
piece = T.parse_piece(PIECE)
mapping = {b['key']: b['num'] for b in piece['blocks']}
nums = sorted(mapping.values())
assert nums == list(range(1, len(nums) + 1)), '件内印面号非 1..N 恰一：%s' % nums[:8]
print('件内 ansitem 权威映射：%d 键（1..%d 恰一）' % (len(mapping), len(nums)))

# 2) 台账读入＋回填前快照
raw = open(LEDGER, encoding='utf-8').read()
led = json.loads(raw)
led_keys = [it['键'] for it in led['items']]
assert set(led_keys) == set(mapping), '台账键集≠件内键集'
# 往返保形核验：indent=1 ensure_ascii=False 重排须逐字还原（证原文件同制式，回填只动值）
assert json.dumps(led, ensure_ascii=False, indent=1) + '\n' == raw or \
       json.dumps(led, ensure_ascii=False, indent=1) == raw, '台账 JSON 制式与 indent=1 不合，停手待核'

# 3) 仅印面号字段回填（其余字段零触碰）
diff = []
for it in led['items']:
    k = it['键']
    new = mapping[k]
    if it.get('印面号') != new:
        diff.append({'键': k, '旧': it.get('印面号'), '新': new})
        it['印面号'] = new
print('漂移键数＝%d（同号键 %d）' % (len(diff), len(mapping) - len(diff)))
for d in sorted(diff, key=lambda x: x['新']):
    print('  %-22s %2d → %2d' % (d['键'], d['旧'], d['新']))

# 4) 零动断言：keys/vals/其余字段逐字不变（对照快照重排）
snap = json.loads(raw)
for it, old in zip(led['items'], snap['items']):
    for f in old:
        if f != '印面号':
            assert it[f] == old[f], '字段 %s/%s 被误动' % (it['键'], f)
    assert set(it) == set(old), '字段集变动'
assert led['keys'] == snap['keys'] and led['vals'] == snap['vals'], 'keys/vals 被动'

# 5) 落盘（分段写：先副本后替换，留回冲前原件）
open(os.path.join(HERE, '_回冲前-值台账-课时02.json'), 'w',
     encoding='utf-8').write(raw)
out = json.dumps(led, ensure_ascii=False, indent=1)
if raw.endswith('\n'):
    out += '\n'
tmp = LEDGER + '.tmp'
open(tmp, 'w', encoding='utf-8', newline='').write(out)
os.replace(tmp, LEDGER)
print('回填落盘：%s' % LEDGER)
json.dump({'件内映射': mapping, '漂移': sorted(diff, key=lambda x: x['新']),
           '漂移键数': len(diff), '同号键数': len(mapping) - len(diff),
           '台账': LEDGER.replace('\\', '/')},
          open(os.path.join(HERE, '_台账印面号回填读数.json'), 'w',
               encoding='utf-8'), ensure_ascii=False, indent=1)
