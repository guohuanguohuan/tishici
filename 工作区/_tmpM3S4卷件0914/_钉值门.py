# -*- coding: utf-8 -*-
# S4 卷件钉值门：件面 ansitem 值串 ↔ 台账钉值逐键全等 + PDF 印面速查行抽查
# 用法: python _钉值门.py 测|滚A|滚B
import re, sys, io

BASE = 'C:/提示词/工作区/M3-第2章量产0913/成卷'
BS = chr(92)

EXPECT = {
 '测': {
  '2章-测-1': 'A', '2章-测-2': 'C', '2章-测-3': 'A', '2章-测-4': 'C（两圆并取）',
  '2章-测-5': 'A', '2章-测-6': 'B（两条射线）', '2章-测-7': 'm=-' + BS + 'dfrac{1}{2}',
  '2章-测-8': '[2' + BS + 'sqrt{3},4)', '2章-测-9': 'AB', '2章-测-10': 'BCD',
  '2章-测-11': 'BCD', '2章-测-12': 'y=1', '2章-测-13': '(x-1)^{2}+y^{2}=4',
  '2章-测-14': '1+' + BS + 'sqrt{3}', '2章-测-15': '(1)', '2章-测-16': '(1)',
  '2章-测-17': '-' + BS + 'dfrac{4}{3}', '2章-测-18': BS + 'dfrac{2' + BS + 'sqrt{3}}{3}',
  '2章-测-19': 'a=1',
 },
 '滚A': {
  '2章-滚A-1': 'A', '2章-滚A-2': 'B', '2章-滚A-3': 'B（①③）', '2章-滚A-4': 'C',
  '2章-滚A-5': 'B（45', '2章-滚A-6': 'x^{2}+y^{2}-2x+2y-3=0', '2章-滚A-7': 'D（2）',
  '2章-滚A-8': 'ACE', '2章-滚A-9': 'ACD', '2章-滚A-10': BS + 'dfrac{9}{4}',
  '2章-滚A-11': BS + 'dfrac{13}{5}', '2章-滚A-12': BS + 'dfrac{' + BS + 'sqrt{2}}{2}',
  '2章-滚A-13': '3x+2y+1=0', '2章-滚A-14': '3', '2章-滚A-15': 'a=-1', '2章-滚A-16': '2' + BS + 'sqrt{51}',
 },
 '滚B': {
  '2章-滚B-1': 'B', '2章-滚B-2': '4+' + BS + 'sqrt{3}', '2章-滚B-3': 'x^{2}+y^{2}-4x-2y-20=0',
  '2章-滚B-4': 'C', '2章-滚B-5': '(2,2)', '2章-滚B-6': 'A（3）', '2章-滚B-7': 'C',
  '2章-滚B-8': 'ACD', '2章-滚B-9': 'AD', '2章-滚B-10': 'B', '2章-滚B-11': 'y^{2}=2x',
  '2章-滚B-12': '4', '2章-滚B-13': 'y^{2}=8x', '2章-滚B-14': '(8,0)', '2章-滚B-15': BS + 'dfrac{4}{3}',
  '2章-滚B-16': 'm=1',
 },
}

DABIAO = {
 '测': ['ACACABAAABBCD', '略'],
 '滚A': ['ABBBB', '略'],
 '滚B': ['BABCC', '略'],
}


def run(juan, piece, pdf):
    want = EXPECT[juan]
    tex = open(piece, encoding='utf-8').read()
    pat = re.compile(BS * 2 + 'begin' + BS + '{ansblock' + BS + '}\\[([^]]+)\\](.*?)' + BS * 2 + 'end' + BS + '{ansblock' + BS + '}', re.S)
    blocks = {m.group(1): m.group(2) for m in pat.finditer(tex)}
    bad = []
    if len(blocks) != len(want):
        bad.append('块数 %d ≠ 期望 %d' % (len(blocks), len(want)))
    for k, w in want.items():
        body = blocks.get(k)
        if body is None:
            bad.append(k + ' 缺块'); continue
        got = None
        for ln in body.splitlines():
            t = ln.strip()
            if t.startswith(chr(92) + 'ansitem{'):
                j2 = t.find('{', t.find('{') + 1)
                got = t[j2 + 1: t.rfind('}')]
                break
        if got is None or w not in got.replace(' ', ''):
            bad.append('%s: got=%r want~%r' % (k, got, w))
    pages = -1
    try:
        import pymupdf
        doc = pymupdf.open(pdf)
        ptxt = ''.join(p.get_text() for p in doc).replace(' ', '').replace('\n', '')
        for snip in DABIAO[juan]:
            if snip not in ptxt:
                bad.append('PDF 印面缺: ' + snip)
        pages = doc.page_count
    except Exception as e:
        bad.append('PDF 读数失败 %r' % e)
    if bad:
        print('[FAIL] %s 钉值门 %d 项:' % (juan, len(bad)))
        for b in bad: print('  -', b)
        return 1
    print('[PASS] %s 钉值门：%d 键值全等｜PDF %d 页｜速查行抽查 %d 项过' % (juan, len(want), pages, len(DABIAO[juan])))
    return 0


if __name__ == '__main__':
    j = sys.argv[1]
    d = {'测': '测评卷', '滚A': '滚动卷/滚A', '滚B': '滚动卷/滚B'}[j]
    sys.exit(run(j, BASE + '/' + d + '/main.tex', BASE + '/' + d + '/main.pdf'))
