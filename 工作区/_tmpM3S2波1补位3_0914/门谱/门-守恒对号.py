# -*- coding: utf-8 -*-
r"""门-守恒对号.py — M3 S2 波1 补位臂3·答案块守恒断言（双档）＋对号门＋尾块门＋页数门。
逻辑承臂4 门谱（_tmpM3S2波1臂4_0914/门谱）逐字；PIECE/MANIFEST/NKEY 参数化（argv＝09|14|15）。
用法: python 门-守恒对号.py 15     退出码: 0＝全过；1＝有红。
"""
import io
import json
import os
import re
import sys

import fitz  # pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 片规 import piece

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = piece(sys.argv[1] if len(sys.argv) > 1 else '09')
PIECE, MANIFEST, NKEY = P['piece'], P['mani'], P['nkey']

RE_ANCHOR = re.compile(r'^[ \t]*%[ \t]*ans:(\S+)', re.M)
RE_BLOCK = re.compile(r'\\begin\{ansblock\}\[([^\]]+)\]')
RE_NUM = re.compile(r'\\ansitem\{(\d+)\}\{')
RE_NOTE = re.compile(r'\\ansnote\{详解\}')
RE_KEYLOG = re.compile(r'^M3-ANSKEY: (.+)$', re.M)
RE_PDF_NUM = re.compile(r'(\d+)\.\s*\[答案\]')

reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
manifest = json.load(open(MANIFEST, encoding='utf-8'))
keyseq = manifest['键序']

print('== ① tex 层 ==')
anchors = RE_ANCHOR.findall(src)
blocks = RE_BLOCK.findall(src)
check(f'锚数={NKEY}', len(anchors) == NKEY, f'{len(anchors)}')
check(f'块数={NKEY}', len(blocks) == NKEY, f'{len(blocks)}')
check('锚集合≡manifest键集合(双向diff)', set(anchors) == set(keyseq) and len(set(anchors)) == NKEY,
      f'缺{sorted(set(keyseq) - set(anchors))} 浮{sorted(set(anchors) - set(keyseq))}')
check('块集合≡锚集合(双向diff)', set(blocks) == set(anchors), '')
check('锚序＝印面装配序（登记用，非逻辑键序）', anchors == blocks, '')
nums = [int(n) for n in RE_NUM.findall(src)]
check(f'ansitem 号序≡1..{NKEY} 连号', nums == list(range(1, NKEY + 1)), f'{len(nums)}枚')
note_cnt = len(RE_NOTE.findall(src))
check(f'ansnote{{详解}} 计数={NKEY}（键均有详解行）', note_cnt == NKEY, f'{note_cnt}')

print('== ② log 层 ==')
logs = {}
for tag in ('true', 'false'):
    t = open(os.path.join(PIECE, f'main-{tag}.log'), encoding='utf-8', errors='replace').read()
    logs[tag] = RE_KEYLOG.findall(t)
check('true ANSKEY 集合≡manifest(双向diff)', set(logs['true']) == set(keyseq), f'{len(logs["true"])}键')
check('false ANSKEY 集合≡manifest(双向diff)', set(logs['false']) == set(keyseq), f'{len(logs["false"])}键')
check('两档 ANSKEY 逐位同序（同装配序编译）', logs['true'] == logs['false'], '')

print('== ③ PDF 层 ==')
pdf = {}
for tag in ('true', 'false'):
    doc = fitz.open(os.path.join(PIECE, f'main-{tag}.pdf'))
    pdf[tag] = {'n': len(doc), 'text': '\n'.join(p.get_text() for p in doc)}
    doc.close()

tnums = [int(m) for m in RE_PDF_NUM.findall(pdf['true']['text'])]
check(f'true 号序≡1..{NKEY} 连号(对号门)', tnums == list(range(1, NKEY + 1)), f'{len(tnums)}枚')
check(f'true [答案] 总计={NKEY}', pdf['true']['text'].count('[答案]') == NKEY,
      f'{pdf["true"]["text"].count("[答案]")}')
check('true [详解] 计数≡tex ansnote', pdf['true']['text'].count('[详解]') == note_cnt,
      f'{pdf["true"]["text"].count("[详解]")}/{note_cnt}')
check('false [答案]＝0', pdf['false']['text'].count('[答案]') == 0,
      f'{pdf["false"]["text"].count("[答案]")}')
check('false [详解]＝0', pdf['false']['text'].count('[详解]') == 0,
      f'{pdf["false"]["text"].count("[详解]")}')
for w in ('证明见详解', '证明过程', '答案'):
    check(f'false 泄答词「{w}」＝0', pdf['false']['text'].count(w) == 0,
          f'{pdf["false"]["text"].count(w)}')
check('尾块「笔记与错题整理」true 恰1', pdf['true']['text'].count('笔记与错题整理') == 1,
      f'{pdf["true"]["text"].count("笔记与错题整理")}')
check('尾块「笔记与错题整理」false 恰1', pdf['false']['text'].count('笔记与错题整理') == 1,
      f'{pdf["false"]["text"].count("笔记与错题整理")}')
check('页数 false≤true', pdf['false']['n'] <= pdf['true']['n'],
      f'true={pdf["true"]["n"]} false={pdf["false"]["n"]}')

print()
print('守恒对号门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
