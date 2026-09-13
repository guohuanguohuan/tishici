# -*- coding: utf-8 -*-
"""S1 收口·总表 vs manifest 复账（终验②）。只读两处；输出逐项判定。"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TMUB = r"C:/提示词/工作区/M3-第2章量产0913/成卷/题面库"
ZB = os.path.join(TMUB, 'canonical键名总表.md')
MANI = os.path.join(TMUB, 'manifest')

text = open(ZB, encoding='utf-8', newline='').read()
fails = []

# ---- ① manifest 全集：21 片、552 键 ----
mani = {}
for f in sorted(os.listdir(MANI)):
    if f.endswith('.manifest.json'):
        m = json.load(open(os.path.join(MANI, f), encoding='utf-8'))
        mani[f[:-len('.manifest.json')]] = m
if len(mani) != 21:
    fails.append('manifest 片数 %d != 21' % len(mani))
tot = sum(m['期望值']['键数'] for m in mani.values())
if tot != 552:
    fails.append('manifest 合计键 %d != 552' % tot)

# ---- ② §三 台账逐行 vs manifest（时戳/键数/指针/态） ----
row_re = re.compile(r'^\| (衔接节|课时\d{2}B?) \| ([\d:.T+-]+) \| ([^|]+) \| ([^|]+) \| `manifest/([^`]+)` \| ([^|]+) \|$', re.M)
ledger = row_re.findall(text)
if len(ledger) != 21:
    fails.append('§三 台账行数 %d != 21' % len(ledger))
for name, ts, keys_cell, multi, mf, state in ledger:
    m = mani.get(name)
    if not m:
        fails.append('台账行 %s 无对应 manifest' % name); continue
    if m['冻时戳'] != ts:
        fails.append('%s 时戳不符：表%s vs manifest%s' % (name, ts, m['冻时戳']))
    n = int(re.match(r'\s*(\d+)', keys_cell).group(1))
    if m['期望值']['键数'] != n:
        fails.append('%s 键数不符：表%d vs manifest%d' % (name, n, m['期望值']['键数']))
    if '已冻' not in state:
        fails.append('%s 态非已冻：%s' % (name, state))
    if mf != '%s.manifest.json' % name:
        fails.append('%s manifest 指针不符：%s' % (name, mf))

# ---- ③ §一 已冻读数 21 片 552 ----
m21 = re.search(r'\| 已冻（S1 并账 (\d+) 片） \| \*\*(\d+)\*\*', text)
if not m21 or m21.group(1) != '21' or m21.group(2) != '552':
    fails.append('§一 已冻行读数不符：%s' % (m21.groups() if m21 else '未找到'))

# ---- ④ §二 批C 四片键列 vs manifest 键序（区间展开） ----
sec_heads = [(m.start(), m.group(1)) for m in re.finditer(r'^### (课时1[0-3]) ', text, re.M)]
bounds = [s[0] for s in sec_heads] + [text.find('### 课时14 ')]
for i, (pos, name) in enumerate(sec_heads):
    sec = text[pos:bounds[i + 1]]
    if '〔补产在途〕' in sec or '〔补产在途·批C〕' in sec:
        fails.append('%s §二节仍含〔补产在途〕' % name)
    want = {'2章-导-%s-G%d' % (name, k) for k in range(1, 6)}
    want |= {'2章-练-%s-简%d' % (name, k) for k in range(1, 11)}
    want |= {'2章-练-%s-中%d' % (name, k) for k in range(1, 5)}
    want |= {'2章-练-%s-难%d' % (name, k) for k in range(1, 3)}
    got = set()
    if re.search(r'`2章-导-%s-G1`~`G5`' % name, sec):
        got |= {'2章-导-%s-G%d' % (name, k) for k in range(1, 6)}
    if re.search(r'`2章-练-%s-简1`~`简10`' % name, sec):
        got |= {'2章-练-%s-简%d' % (name, k) for k in range(1, 11)}
    if re.search(r'`中1`~`中4`' % (), sec):
        got |= {'2章-练-%s-中%d' % (name, k) for k in range(1, 5)}
    if re.search(r'`难1`~`难2`', sec) or '`难1`（件13-#25 借入）、`难2`' in sec:
        got |= {'2章-练-%s-难%d' % (name, k) for k in range(1, 3)}
    if want - got:
        fails.append('%s §二键列缺：%s' % (name, sorted(want - got)))
    mk = mani[name]['键序']
    if set(mk) != want or len(mk) != 21:
        fails.append('%s manifest 键集与 21 键口径不符' % name)

# ---- ⑤ 指令单要点落位抽查 ----
gate = text[text.find('多选门（每课时正文多选'):]
if '批C 四片' not in gate[:160]:
    fails.append('多选门句未含「批C 四片」')
for probe in ('「简席×5」系练习席误记', '`命2改`→`…-简10`', '系 G5 块内小标', '键列法已确',
              '〔已冻·批C 2026-09-14T00:05:11+0800〕→ `课时10', '〔已冻·批C 2026-09-14T00:05:11+0800〕→ `课时11',
              '〔已冻·批C 2026-09-14T00:05:11+0800〕→ `课时12', '〔已冻·批C 2026-09-14T00:05:11+0800〕→ `课时13'):
    if probe not in text:
        fails.append('指令单要点未落：%s' % probe)
# 拓区读数照令不改（10:14 席／13:6 席）
if '（域账拓展14 席，拓1 撤位席不设键净拓14' not in text or '（域账拓展6 席；27＝G5 5＋正文16＋拓6）' not in text:
    fails.append('拓区读数与令不符')
# 待裁3 项现状（L22 措辞留主脑未动／多选门并账在位／L22 行标在位）
if '命制在途 8' not in text:
    fails.append('待裁1 基线消失（应留主脑未动）')
if '批A（已冻 0913T22:30，115 题次已并入上「已冻」读数）' not in text:
    fails.append('待裁3 行标不在位')

print('复账：manifest %d 片 %d 键｜台账 %d 行｜判定：%s' % (len(mani), tot, len(ledger), '全等零差 ✓' if not fails else '✗'))
for f in fails:
    print('  - %s' % f)
sys.exit(1 if fails else 0)
