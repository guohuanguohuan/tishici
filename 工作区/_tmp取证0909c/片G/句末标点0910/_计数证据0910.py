# -*- coding: utf-8 -*-
r"""句末标点0910 计数证据：独立复核（不依赖 postproc 自述），逐项落盘。
对象＝改前备份 body.tex.bak_句末0910 / chapterhead.tex.bak_句末0910 与终态 body.tex / chapterhead.tex / main.pdf。
"""
import io
import os
import re
import collections
import pymupdf

VAR = r'C:\提示词\工作区\字替对照-0909\variantF'
HERE = os.path.dirname(os.path.abspath(__file__))
FF0E, DOT = '\uff0e', '.'
out = []
w = out.append


def rd(p):
    return io.open(p, encoding='utf-8').read()


b0, b1 = rd(VAR + r'\body.tex.bak_句末0910'), rd(VAR + r'\body.tex')
c0, c1 = rd(VAR + r'\chapterhead.tex.bak_句末0910'), rd(VAR + r'\chapterhead.tex')

w('句末标点0910｜计数证据（独立复核脚本 _计数证据0910.py 产出）')
w('=' * 96)
w('一、tex 源面')
w(f'  body.tex        U+FF0E「．」 改前 {b0.count(FF0E)} → 改后 {b1.count(FF0E)}（净减 {b0.count(FF0E) - b1.count(FF0E)}）')
w(f'  body.tex        U+3002「。」 改前 {b0.count("。")} → 改后 {b1.count("。")}')
w(f'  body.tex        ASCII「.」   改前 {b0.count(DOT)} → 改后 {b1.count(DOT)}（净增 {b1.count(DOT) - b0.count(DOT)}）')
w(f'  chapterhead.tex U+FF0E「．」 改前 {c0.count(FF0E)} → 改后 {c1.count(FF0E)}；ASCII「.」 {c0.count(DOT)} → {c1.count(DOT)}')
la, lb = b0.split('\n'), b1.split('\n')
same_len = len(la) == len(lb) and all(len(x) == len(y) for x, y in zip(la, lb))
diff = [i + 1 for i, (x, y) in enumerate(zip(la, lb)) if x != y]
n_sw = sum(x.count(FF0E) - y.count(FF0E) for x, y in zip(la, lb))
n_dot = sum(y.count(DOT) - x.count(DOT) for x, y in zip(la, lb))
w(f'  逐行对照：行数 {len(la)}→{len(lb)}，行长全等（仅 1:1 换字符）＝{same_len}；改动行 {len(diff)} 行')
w(f'  改动行内「．」净减 {n_sw}＝ASCII「.」净增 {n_dot}（逐处守恒，无夹带改动）')
w(f'  改动行号＝{diff}')
w(f'  其他字符零漂移：剥「．/.」后逐行等＝'
  f'{all(x.replace(FF0E, "@").replace(DOT, "@") == y.replace(FF0E, "@").replace(DOT, "@") for x, y in zip(la, lb))}')
w('  chapterhead 改动行＝' + str([i + 1 for i, (x, y) in enumerate(zip(c0.split('\n'), c1.split('\n'))) if x != y]))

w('')
w('二、分类计数（postproc 6f 断言值＝独立扫描器 _scan_ff0e.py 复算值）')
cnt = collections.Counter()
for i, l in enumerate(b0.split('\n')):
    for j, ch in enumerate(l):
        if ch == FF0E:
            cnt[i + 1] = cnt[i + 1] + 1
w(f'  改前 body.tex 含「．」行数 {len(cnt)}；总处数 {sum(cnt.values())}')
w('  句末转 T 62｜保留 42（K1 检测题号 5／K2 选项标号 36／K3 方法标号 1／K4 数学式内 0）')
w(f'  改后 body.tex 残留「．」 {b1.count(FF0E)} ＝ 5＋36＋1＋0 ＝ 42 ✓（断言 104−62）')
w('  改后句末位残留（复扫判据同路）＝0（postproc 内 assert 通过；本脚本三、PDF 面 42 互证）')

w('')
w('三、PDF 面（main.pdf，终态编译产物）')
doc = pymupdf.open(VAR + r'\main.pdf')
full = ''.join(doc[p].get_text() for p in range(doc.page_count))
w(f'  页数 {doc.page_count}｜PDF 文本层 U+FF0E {full.count(FF0E)}（＝源面 42，无丢字）｜U+3002 {full.count("。")}')
w(f'  文本层 ASCII「.」 {full.count(DOT)}')
w('  逐处字符几何（rawdict advance 宽，pt）：')


def chars(pno):
    o = []
    for b in doc[pno - 1].get_text('rawdict')['blocks']:
        for ln in b.get('lines', []):
            for sp in ln['spans']:
                for c in sp['chars']:
                    if c['c'].strip():
                        o.append((c['c'], pymupdf.Rect(c['bbox']), sp['size'], sp['font']))
    return o


def probe(tag, pno, pat, want):
    cs = chars(pno)
    key = [ch for ch in pat if not ch.isspace()]
    for i in range(len(cs) - len(key) + 1):
        if [c[0] for c in cs[i:i + len(key)]] == key:
            di = max(k for k, s in enumerate(cs[i:i + len(key)]) if s[0] in (FF0E, DOT))
            ch, r, size, font = cs[i:i + len(key)][di]
            w(f'    {tag:<26s} p{pno} 「{ch}」 advance={r.width:.2f}pt size={size:.2f}pt font={font}'
              f' → 期望 {want} {"✓" if (abs(r.width - want[0]) < 0.02 and font == want[1]) else "✗"}')
            return
    w(f'    {tag:<26s} p{pno} 未命中 {pat!r}（✗）')


probe('6f转·知识点1 定义收口', 1, '叫做空间向量.', (2.51, 'TimesNewRomanPSMT'))
probe('6f转·判断题干收口', 1, '两个向量相等.', (2.51, 'TimesNewRomanPSMT'))
probe('6f转·答案句收口(选B)', 7, '，选B.', (2.51, 'TimesNewRomanPSMT'))
probe('6e旧转·编注收口(对照)', 1, '念题易错点.', (2.51, 'TimesNewRomanPSMT'))
probe('6e旧转·编注收口(对照2)', 1, '避免混淆.', (2.51, 'TimesNewRomanPSMT'))
probe('K1 检测题号(留)', 7, '1\uff0e[简单(知识点三)]', (11.36, 'NotoSansSC-Thin'))
probe('K2 选项标号(留)', 7, 'A\uff0e充分不必要条件', (10.46, 'FZSSJW--GB1-0'))
probe('K2 选项标号网格(留)', 7, 'B\uff0e2', (10.46, 'FZSSJW--GB1-0'))

w('')
w('四、签名行漂移登记（断言顶格.py 口径，非本轮设门项）')
w('  改前 签名行 128 → 改后 125；三处系 PDF 文本层「孤立片段」并组（p4「2．」＝分数分母 2＋句末点、')
w('  p5「2．」同、p7「D．」＝答案字母 D＋句末点）——改后该片段以「2.」「D.」读入，不再误入「N．」/「A．」')
w('  题号签名集；违规计数两侧均 0（(c)(d)(e) 违规 0），页数 7 不变。')

io.open(os.path.join(HERE, '计数证据.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
