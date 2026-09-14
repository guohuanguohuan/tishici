# -*- coding: utf-8 -*-
r"""印面对账练习.py — [E] 件面等价腿·练习本 12 件（对集合不对数·波1 印面对账.py 同制）。

口径：件面真源＝main.tex 诸 ansblock 内件宏标签：
  \ansitem{L}{…} → true 印面应现 `L.[答案]`；\ansnote{解析}{…} → 应现 `[解析]`。
判定：true 各标签计数＝件面期望计数（计数相等而集合不同亦红）；pure 全零（泄答红）。
用法: python 印面对账练习.py   # 全 12 件，退出码 0/1
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
import pymupdf
HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.join(HERE, '..', 'M2练习本')
PIECES = ['课时%02d' % i for i in range(1, 11)] + ['上册', '下册']


def blocks_labels(tex):
    out = []
    for m in re.finditer(r'\\begin\{ansblock\}\[([^\]]+)\]\n(.*?)\\end\{ansblock\}', tex, re.S):
        for l in m.group(2).split('\n'):
            mi = re.match(r'\\(ansitem|ansnote|anssub)\{([^}]+)\}\{', l.strip())
            if mi:
                out.append((mi.group(1), mi.group(2)))
    return out


def pdf_txt(f):
    doc = pymupdf.open(f)
    return ''.join(p.get_text() for p in doc)


def main():
    bad = 0
    for piece in PIECES:
        d = os.path.join(TREE, piece)
        tex = io.open(os.path.join(d, 'main.tex'), encoding='utf-8').read()
        want_item, want_note, want_sub = {}, {}, {}
        for inner, L in blocks_labels(tex):
            bucket = {'ansitem': want_item, 'ansnote': want_note, 'anssub': want_sub}[inner]
            bucket[L] = bucket.get(L, 0) + 1
        t, p = pdf_txt(os.path.join(d, 'main-true.pdf')), pdf_txt(os.path.join(d, 'main-pure.pdf'))
        reds = []
        got_item = {L: len(re.findall(r'(?<![\w）)])' + re.escape(L) + r'\s*\.\s*\[答案\]', t)) for L in want_item}
        got_note = {L: t.count('[' + L + ']') for L in want_note}
        got_sub = {L: len(re.findall(r'(?<![\d）)])' + re.escape(L) + r'(?![\d）.])', t)) for L in want_sub}
        if got_item != want_item:
            reds.append('true ansitem区 %s≠期望 %s' % (got_item, want_item))
        if got_note != want_note:
            reds.append('true ansnote区 %s≠期望 %s' % (got_note, want_note))
        if got_sub != want_sub:
            reds.append('true anssub续行 %s≠期望 %s' % (got_sub, want_sub))
        leak_i = sum(len(re.findall(re.escape(L) + r'\s*\.\s*\[答案\]', p)) for L in want_item)
        leak_n = sum(p.count('[' + L + ']') for L in want_note)
        leak_s = sum(len(re.findall(r'(?<![\d）)])' + re.escape(L) + r'(?![\d）.])', p)) for L in want_sub)
        if leak_i or leak_n or leak_s:
            reds.append('pure 泄答：item %d note %d sub %d' % (leak_i, leak_n, leak_s))
        if reds:
            bad += 1
            print('[红] %s：%s' % (piece, '｜'.join(reds)[:200]))
        else:
            print('[过] %s：item 区 %d｜note 区 %d｜anssub 续行 %d｜pure 全零' %
                  (piece, sum(want_item.values()), sum(want_note.values()), sum(want_sub.values())))
    print('印面对账（练习本）：%s' % ('FAIL %d 件红' % bad if bad else '全过 12 件'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
