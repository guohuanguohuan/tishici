# -*- coding: utf-8 -*-
# S7收尾批·值一致性断言（只读）：body.tex 渲染值 ↔ 值快照.json 逐键比对
import io, json, re, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def tex(s):
    return s.replace('√', r'\(\surd\)').replace('×', r'$\times$')

snap = json.load(open('值快照.json', encoding='utf-8'))
lines = open('body.tex', encoding='utf-8').read().splitlines()

RE_PAIR = re.compile(r'^%\s*pair:(\S+)')
RE_ITEM = re.compile(r'^\\(?:ansline|ansitem|dansitem)\{([^}]*)\}\{(.*)\}\s*$')

pairs, mismatch, checked, npair = [], [], 0, 0
for ln in lines:
    m = RE_PAIR.match(ln)
    if m:
        pairs.append(m.group(1)); npair += 1; continue
    m = RE_ITEM.match(ln)
    if not m or not pairs:
        continue
    label, content = m.group(1), m.group(2)
    if label == '解析':
        continue
    keys = pairs; pairs = []
    vals = [snap[k] for k in keys]
    if all(k.split('-')[-1].startswith('判') for k in keys) and len(keys) > 1:
        exp = r'\quad '.join('(%d)%s' % (i + 1, tex(v)) for i, v in enumerate(vals))
    elif all(k.split('-')[-1].startswith('评') for k in keys) and len(keys) > 1:
        exp = '；'.join('%d．%s' % (i + 1, tex(v)) for i, v in enumerate(vals))
    elif len(keys) > 1:  # 探组：例1 X；变式1 Y
        exp = '；'.join('%s %s' % (k.split('-')[3], tex(v)) for k, v in zip(keys, vals))
    else:
        exp = tex(vals[0])
    checked += len(keys)
    if content != exp:
        mismatch.append((keys, exp, content))

print('pair 键数:', npair, '｜比对键数:', checked, '｜json 键数:', len(snap))
if mismatch:
    print('不一致 %d 组：' % len(mismatch))
    for keys, exp, got in mismatch[:8]:
        print(' 键:', keys)
        print('  期望:', exp[:120])
        print('  实际:', got[:120])
    sys.exit(1)
print('body.tex ↔ 值快照.json 全键一致')

src = open('组装S5.py', encoding='utf-8').read()
probes = [
    (r'(1)\((-8,8,4)\)', '练04-2'),
    (r'D（\(\left(2,2,\dfrac{4}{3}\right)\)', '练04-10'),
    (r'\(A_{1}(-1,-2,0)\)，\(B_{1}(3,-1,-2)\)', '练04-13'),
    (r'\{4,\ 4\sqrt{2},\ 4\sqrt{3}\}', '练04-15(3)'),
    (r'150^{\circ}', '练06-9'),
    (r'\overrightarrow{DC}', '课05预习填空'),
    (r'×\quad (6)√', '课02判5'),
    ('①②③⑤假；④真', '拓-001'),
    (r'\(\left(\dfrac{1}{4},\dfrac{1}{2}\right)\)', '拓-053'),
    (r'\((-3,3,-3)\)', '课06评5'),
]
bad = 0
for probe, name in probes:
    ok = probe in src
    bad += (not ok)
    print(('V表含新值 ' if ok else 'V表缺新值 ') + name)
sys.exit(1 if (mismatch or bad) else 0)
