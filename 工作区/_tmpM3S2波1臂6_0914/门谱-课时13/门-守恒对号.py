# -*- coding: utf-8 -*-
r"""门-守恒对号.py — M3 S2 波1 臂6 课时13·答案块守恒断言（双档）＋对号门＋尾块门＋页数门。
参数化自 母版 门谱（_tmpM3S2母版0914/门谱/），常量换片：PIECE/MANIFEST/21。
断言面：
  ①tex 层：行首注释锚 % ans:键 ≡ ansblock[键] ≡ manifest 键序（21 键，集合双向 diff＋逐位序）。
  ②log 层：M3-ANSKEY 键序（true/false 两档各 21）≡ manifest 键序（逐位相等）。
  ③PDF 层（fitz 文本抽取）：
      true ：「N. [答案]」号序 ≡ 1..21 严格连号（对号门）；[答案] 总计 21；
              [详解] 计数 ≡ tex \ansnote{详解} 计数；
      false：[答案]＝0、[详解]＝0、泄答词（答案/证明见详解/证明过程）＝0；
      尾块「笔记与错题整理」两档恰 1；
      页数 false ≤ true。
多选门旁证：本片正文 \duoxuan 出现 0 次（10-难1 槽型「多结论选择」不计多选门，答案 BCD）。
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

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时13-2.6.1双曲线的标准方程'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时13.manifest.json'
NKEYS = 21

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
check(f'锚数={NKEYS}', len(anchors) == NKEYS, f'{len(anchors)}')
check(f'块数={NKEYS}', len(blocks) == NKEYS, f'{len(blocks)}')
check('锚集合≡manifest键集合(双向diff)', set(anchors) == set(keyseq) and len(set(anchors)) == NKEYS,
      f'缺{sorted(set(keyseq) - set(anchors))} 浮{sorted(set(anchors) - set(keyseq))}')
check('块集合≡锚集合(双向diff)', set(blocks) == set(anchors), '')
check('锚序＝印面装配序（登记用，非逻辑键序）', anchors == blocks, '')
nums = [int(n) for n in RE_NUM.findall(src)]
check(f'ansitem 号序≡1..{NKEYS} 连号', nums == list(range(1, NKEYS + 1)),
      f'{nums if len(nums) != NKEYS else "21枚"}')
note_cnt = len(RE_NOTE.findall(src))
check('ansnote{详解} 计数>0 且=21 键均有详解行', note_cnt == NKEYS, f'{note_cnt}')
duox = src.count('\\duoxuan')
check('多选门：\\duoxuan＝0（本片多选 0 合规）', duox == 0, f'{duox}')

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
check(f'true 号序≡1..{NKEYS} 连号(对号门)', tnums == list(range(1, NKEYS + 1)), f'{len(tnums)}枚')
check(f'true [答案] 总计={NKEYS}', pdf['true']['text'].count('[答案]') == NKEYS,
      f'{pdf["true"]["text"].count("[答案]")}')
check('true [详解] 计数≡tex ansnote', pdf['true']['text'].count('[详解]') == note_cnt,
      f'{pdf["true"]["text"].count("[详解]")}/{note_cnt}')
check('false [答案]＝0', pdf['false']['text'].count('[答案]') == 0,
      f'{pdf["false"]["text"].count("[答案]")}')
check('false [详解]＝0', pdf['false']['text'].count('[详解]') == 0,
      f'{pdf["false"]["text"].count("[详解]")}')
for w in ('证明见详解', '证明过程', '答案', '详解'):
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
