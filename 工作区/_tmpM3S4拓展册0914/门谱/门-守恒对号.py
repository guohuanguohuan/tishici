# -*- coding: utf-8 -*-
r"""门-守恒对号.py — M3 S4 拓展册·答案块守恒断言（双档双册）＋对号门＋键序源交叉＋撤席跳号＋尾块门。

结构照抄 _tmpM3S3母版0914/门谱/门-守恒对号.py，键序源换 S4 台账（生成册tex.py 即真相）。

断言面（上册 87 键／下册 115 键，键序源＝值台账-{上,下册}.json）：
  ①tex 层：行首注释锚 % ans:键 ≡ ansblock[键] ≡ 台账键序（序列逐位，非仅集合）；
      \ansitem 席号序列 ≡ 台账键末段席号（逐字串）；\tailfill 恰 1/册；
      键全为 2章-拓- 前缀；撤席跳号核对（10缺1、11缺2、12缺27、14缺13/31、16缺18）；
      manifest 交叉：批A（课时01/02/04/05）与批D（课时14~17）台账逐课时键序 ≡ manifest 拓键序，
      批C（课时10~13）manifest 拓键＝0（自构键未入库·残余项在案）；
      \ansnote{详解} 计数＝席数/册。
  ②log 层：M3-ANSKEY 键序 true ≡ false ≡ 台账键序（逐位相等）。
  ③PDF 层（fitz 文本抽取）：true 印面号序 ≡ 台账席号序列（逐位）；[答案] 总计＝席数；
      [详解] ≡ tex ansnote 计数；false：[答案]=0、[详解]=0、泄答词＝0；页数 false ≤ true。
用法: python 门-守恒对号.py
退出码: 0＝全过；1＝有红。红线：件树与题面库/定稿只读，本脚本零写入。
"""
import io
import json
import os
import re
import sys

import fitz  # pymupdf

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/拓展册'
MANI = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest'
VOLS = {'上册': 87, '下册': 115}
LESSONS_MANI = {'上册': ('01', '02', '04', '05'), '下册': ('14', '15', '16', '17')}
LESSONS_SELF = {'上册': ('10', '11', '12', '13'), '下册': ()}
# 裁断口径①：撤席跳号不重编号
CHEXI = {'10': [1], '11': [2], '12': [27], '14': [13, 31], '16': [18]}

RE_ANCHOR = re.compile(r'^[ \t]*%[ \t]*ans:(\S+)', re.M)
RE_BLOCK = re.compile(r'\\begin\{ansblock\}\[([^\]]+)\]')
RE_NUM = re.compile(r'\\ansitem\{([^}]+)\}')
RE_NOTE = re.compile(r'\\ansnote\{详解\}')
RE_KEYLOG = re.compile(r'^M3-ANSKEY: (.+)$', re.M)
RE_PDF_NUM = re.compile(r'(T\d+|\d+(?:-\d+)*)\.\s*\[答案\]')

reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

ledger_all = []
for vol, nseat in VOLS.items():
    print(f'======== {vol}（席数 {nseat}）========')
    d = os.path.join(BASE, vol)
    src = open(os.path.join(d, 'main.tex'), encoding='utf-8').read()
    led = json.load(open(os.path.join(d, f'值台账-{vol}.json'), encoding='utf-8'))
    keyseq = led['keys']
    ledger_all.append(keyseq)
    labels = ['-'.join(k.split('-')[3:]) for k in keyseq]  # 席号字面：02/T1/32-1（子席含母席）

    print('== ① tex 层 ==')
    anchors = RE_ANCHOR.findall(src)
    blocks = RE_BLOCK.findall(src)
    check(f'锚数={nseat}', len(anchors) == nseat, f'{len(anchors)}')
    check(f'块数={nseat}', len(blocks) == nseat, f'{len(blocks)}')
    check('锚集合≡台账键集合(双向diff)', set(anchors) == set(keyseq),
          f'缺{sorted(set(keyseq) - set(anchors))[:5]} 浮{sorted(set(anchors) - set(keyseq))[:5]}')
    check('块集合≡锚集合(双向diff)', set(blocks) == set(anchors), '')
    check('锚序＝块序＝台账键序（逐位）', anchors == blocks == keyseq, '')
    nums = RE_NUM.findall(src)
    check(f'ansitem 数={nseat}', len(nums) == nseat, f'{len(nums)}')
    check('ansitem 席号序≡台账末段席号（逐字串·逐位）', nums == labels,
          f'首歧{next((i for i, (a, b) in enumerate(zip(nums, labels)) if a != b), -1)}')
    tail = src.count('\\tailfill')
    check('\\tailfill 恰 1/册', tail == 1, f'{tail}')
    bad = [k for k in keyseq if not k.startswith('2章-拓-')]
    check('键全为 2章-拓- 前缀', not bad, f'{bad[:3]}')

    # 撤席跳号核对（按母席号算：数字席＋子席母号；子席 32-1 形的 32 为母席）
    from collections import defaultdict
    parents = defaultdict(set)
    for k in keyseq:
        m = re.fullmatch(r'2章-拓-课时(\d+)-(\d+)(?:-(\d+))?', k)
        if m:
            parents[m.group(1)].add(int(m.group(2)))
    okcx, cxmsg = True, []
    for les in sorted(parents):
        seats = parents[les]
        absent = [n for n in range(1, max(seats) + 1) if n not in seats]
        exp = CHEXI.get(les, [])
        if absent != exp:
            okcx = False
            cxmsg.append(f'课时{les} 缺{absent}≠裁断{exp}')
    covered = sorted(set(parents) | set(CHEXI))
    if sorted(parents) != sorted(CHEXI):
        okcx = False
        cxmsg.append(f'数字席课时覆盖{sorted(parents)}≠裁断{sorted(CHEXI)}')
    check('撤席跳号≡裁断口径（10缺1/11缺2/12缺27/14缺13·31/16缺18）', okcx, '；'.join(cxmsg))

    # manifest 交叉（批A/批D 入库键序；批C 自构键未入库=残余项在案）
    for les in LESSONS_MANI[vol]:
        mani = json.load(open(os.path.join(MANI, f'课时{les}.manifest.json'), encoding='utf-8'))
        mtk = [k for k in mani['键序'] if k.startswith('2章-拓-')]
        ltk = [k for k in keyseq if f'-课时{les}-' in k]
        check(f'课时{les} 台账键序≡manifest拓键序', ltk == mtk,
              f'账{len(ltk)}/库{len(mtk)}')
    for les in LESSONS_SELF[vol]:
        mani = json.load(open(os.path.join(MANI, f'课时{les}.manifest.json'), encoding='utf-8'))
        mtk = [k for k in mani['键序'] if k.startswith('2章-拓-')]
        check(f'课时{les}（批C 自构键）manifest拓键=0', not mtk, f'{len(mtk)}')

    note_cnt = len(RE_NOTE.findall(src))
    check(f'ansnote{{详解}} 计数={nseat}（键键有详解）', note_cnt == nseat, f'{note_cnt}')

    print('== ② log 层 ==')
    logs = {}
    for tag in ('true', 'false'):
        t = open(os.path.join(d, f'main-{tag}.log'), encoding='utf-8', errors='replace').read()
        logs[tag] = RE_KEYLOG.findall(t)
    for tag in ('true', 'false'):
        check(f'{tag} ANSKEY 集合≡台账键集(双向diff)', set(logs[tag]) == set(keyseq),
              f'{len(logs[tag])}键')
    check('两档 ANSKEY 逐位同序（同装配序编译·恒等）', logs['true'] == logs['false'] == keyseq, '')

    print('== ③ PDF 层 ==')
    pdf = {}
    for tag in ('true', 'false'):
        doc = fitz.open(os.path.join(d, f'main-{tag}.pdf'))
        pdf[tag] = {'n': len(doc), 'text': '\n'.join(p.get_text() for p in doc)}
        doc.close()

    tnums = RE_PDF_NUM.findall(pdf['true']['text'])
    check('true 印面号序≡台账席号序（逐位·对号门）', tnums == labels,
          f'{len(tnums)}枚｜首歧{next((i for i, (a, b) in enumerate(zip(tnums, labels)) if a != b), -1)}'
          + (f'｜差样{[x for x, y in zip(tnums, labels) if x != y][:3]}' if tnums != labels else ''))
    check(f'true [答案] 总计={nseat}', pdf['true']['text'].count('[答案]') == nseat,
          f'{pdf["true"]["text"].count("[答案]")}')
    det = pdf['true']['text'].count('[详解]')
    check('true [详解] ≡tex ansnote 计数', det == note_cnt, f'{det}/{note_cnt}')
    dian = pdf['true']['text'].count('[点睛]')
    check('true [点睛] 总计=0（本册 \\ansnote 仅详解形·sty 印 [#1] 无点睛通路）', dian == 0, f'{dian}')
    for w in ('[答案]', '[详解]', '[点睛]'):
        check(f'false {w}＝0', pdf['false']['text'].count(w) == 0,
              f'{pdf["false"]["text"].count(w)}')
    for w in ('证明见详解', '证明过程'):
        check(f'false 泄答词「{w}」＝0', pdf['false']['text'].count(w) == 0,
              f'{pdf["false"]["text"].count(w)}')
    check('页数 false≤true', pdf['false']['n'] <= pdf['true']['n'],
          f'true={pdf["true"]["n"]} false={pdf["false"]["n"]}')
    print()

print('======== 双册汇总 ========')
check('两册键数合计=202（批A10＋批C77＋批D115）', sum(len(k) for k in ledger_all) == 202,
      f'{[len(k) for k in ledger_all]}')
check('两册键集无交（上/下互斥）', not (set(ledger_all[0]) & set(ledger_all[1])), '')
print()
print('守恒对号门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
