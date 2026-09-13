# -*- coding: utf-8 -*-
r"""门-守恒对号-课时07.py — M3 S3 W2臂A 课时07 练习件（母版派生·常数换片）·答案块守恒断言（双档）＋对号门＋拓区隔离＋尾块门＋页数门。

断言面：
  ①tex 层：行首注释锚 % ans:键 ≡ ansblock[键] ≡ manifest 练键序（E1~E16，16 键，
      集合双向 diff＋逐位序）；拓区隔离：件内零 2章-拓/测/滚 键（S4 域，不入印面）。
  ②log 层：M3-ANSKEY 键序（true/false 两档各 16）≡ manifest 练键序（逐位相等）；
      拓区隔离 log 侧同断言。
  ③PDF 层（fitz 文本抽取）：
      true ：「N. [答案]」号序 ≡ 1..16 严格连号（对号门）；[答案] 总计 16；
              [详解] 计数 ≡ tex \ansnote{详解} 计数；
      false：[答案]＝0、[详解]＝0、泄答词（证明见详解/证明过程/[答案]/[详解]）＝0；
      尾块「笔记与错题整理」两档恰 1；页数 false ≤ true。
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

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时07-圆的方程'
MANIFEST = 'C:/提示词/工作区/M3-第2章量产0913/成卷/题面库/manifest/课时07.manifest.json'

RE_ANCHOR = re.compile(r'^[ \t]*%[ \t]*ans:(\S+)', re.M)
RE_BLOCK = re.compile(r'\\begin\{ansblock\}\[([^\]]+)\]')
RE_NUM = re.compile(r'\\ansitem\{(\d+)\}\{')
RE_NOTE = re.compile(r'\\ansnote\{详解\}')
RE_KEYLOG = re.compile(r'^M3-ANSKEY: (.+)$', re.M)
RE_PDF_NUM = re.compile(r'(\d+)\.\s*\[答案\]')
BAD_PREFIX = ('2章-拓-', '2章-测-', '2章-滚-')

reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

src = open(os.path.join(PIECE, 'main.tex'), encoding='utf-8').read()
manifest = json.load(open(MANIFEST, encoding='utf-8'))
keyseq = [k for k in manifest['键序'] if k.startswith('2章-练-')]

print('== ① tex 层 ==')
anchors = RE_ANCHOR.findall(src)
blocks = RE_BLOCK.findall(src)
check('锚数=16', len(anchors) == 16, f'{len(anchors)}')
check('块数=16', len(blocks) == 16, f'{len(blocks)}')
check('锚集合≡manifest练键集合(双向diff)', set(anchors) == set(keyseq) and len(set(anchors)) == 16,
      f'缺{sorted(set(keyseq) - set(anchors))} 浮{sorted(set(anchors) - set(keyseq))}')
check('块集合≡锚集合(双向diff)', set(blocks) == set(anchors), '')
check('锚序＝manifest练键序＝印面装配序', anchors == blocks == keyseq, '')
nums = [int(n) for n in RE_NUM.findall(src)]
check('ansitem 号序≡1..16 连号', nums == list(range(1, 17)), f'{nums if len(nums) != 16 else "16枚"}')
note_cnt = len(RE_NOTE.findall(src))
check('ansnote{详解} 计数=16（题后紧跟制·键键有详解）', note_cnt == 16, f'{note_cnt}')
ext = [k for k in set(anchors) | set(blocks) if k.startswith(BAD_PREFIX)]
check('拓区隔离：件键集零 拓/测/滚 前缀', not ext, f'{ext}')
for tagk in ('2章-拓-', '2章-测-', '2章-滚-'):
    n = src.count(tagk)
    check(f'拓区隔离：tex 全文「{tagk}」×0', n == 0, f'{n}')

print('== ② log 层 ==')
logs = {}
for tag in ('true', 'false'):
    t = open(os.path.join(PIECE, f'main-{tag}.log'), encoding='utf-8', errors='replace').read()
    logs[tag] = RE_KEYLOG.findall(t)
check('true ANSKEY 集合≡manifest练键集(双向diff)', set(logs['true']) == set(keyseq), f'{len(logs["true"])}键')
check('false ANSKEY 集合≡manifest练键集(双向diff)', set(logs['false']) == set(keyseq), f'{len(logs["false"])}键')
check('两档 ANSKEY 16 逐位同序（同装配序编译）', logs['true'] == logs['false'], '')
extl = [k for k in set(logs['true']) | set(logs['false']) if k.startswith(BAD_PREFIX)]
check('拓区隔离：log 两档键集零 拓/测/滚 前缀', not extl, f'{extl}')

print('== ③ PDF 层 ==')
pdf = {}
for tag in ('true', 'false'):
    doc = fitz.open(os.path.join(PIECE, f'main-{tag}.pdf'))
    pdf[tag] = {'n': len(doc), 'text': '\n'.join(p.get_text() for p in doc)}
    doc.close()

tnums = [int(m) for m in RE_PDF_NUM.findall(pdf['true']['text'])]
check('true 号序≡1..16 连号(对号门)', tnums == list(range(1, 17)), f'{len(tnums)}枚')
check('true [答案] 总计=16', pdf['true']['text'].count('[答案]') == 16,
      f'{pdf["true"]["text"].count("[答案]")}')
check('true [详解] 计数≡tex ansnote', pdf['true']['text'].count('[详解]') == note_cnt,
      f'{pdf["true"]["text"].count("[详解]")}/{note_cnt}')
check('false [答案]＝0', pdf['false']['text'].count('[答案]') == 0,
      f'{pdf["false"]["text"].count("[答案]")}')
check('false [详解]＝0', pdf['false']['text'].count('[详解]') == 0,
      f'{pdf["false"]["text"].count("[详解]")}')
for w in ('证明见详解', '证明过程', '[答案]', '[详解]'):
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
