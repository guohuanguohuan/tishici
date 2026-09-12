# -*- coding: utf-8 -*-
# 收尾轮B·件面实核：导学件 9.4 命制条数分解（＋练习件 9.4 头注计数核对）
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'C:\提示词\工作区\P1-必修3第9章量产0912\成卷'
BS = chr(92)


def body(p):
    t = io.open(p, encoding='utf-8').read().split('\n')
    return t[t.index(BS + 'begin{document}') + 1:]


def cnt(b, cmd):
    pre = BS + cmd
    return sum(1 for l in b if l.startswith(pre))


D = ROOT + r'\导学件\9.4静电的防止与利用\main.tex'
L = ROOT + r'\练习件\9.4静电的防止与利用\main.tex'
b = body(D)
print('导学件9.4 件面实数：判断 %d（zhenhead %d 组）／例1 %d／变式1 %d／拓展延伸 %d／课堂评价 %d ＝ %d 条' % (
    cnt(b, 'zhentib'), cnt(b, 'zhenhead'), cnt(b, 'tjdnr'), cnt(b, 'liB'),
    cnt(b, 'tuoZhan'), cnt(b, 'jiancestem'),
    cnt(b, 'zhentib') + cnt(b, 'tjdnr') + cnt(b, 'liB') + cnt(b, 'tuoZhan') + cnt(b, 'jiancestem')))
lb = body(L)
print('练习件9.4 件面实数：题 %d（ti 号行）／难度题型标 %d' % (
    sum(1 for l in lb if l.startswith(BS + 'tihao{')),
    sum(1 for l in lb if BS + 'tieside{' in l)))


def head_notes(p, tag, keys):
    t = io.open(p, encoding='utf-8').read().split('\n')
    for i, l in enumerate(t[:40], 1):
        if l.lstrip().startswith('%') and any(k in l for k in keys):
            print(tag, '头注行%d：%s' % (i, l.strip()[:140]))


head_notes(D, '导学件9.4', ['命制', '条', '判断 6'])
head_notes(L, '练习件9.4', ['命制', '条', '总分', '16'])
