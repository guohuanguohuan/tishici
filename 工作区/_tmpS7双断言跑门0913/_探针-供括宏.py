# -*- coding: utf-8 -*-
"""找 qp-*.tex 定义体含全角（的宏（TeX 注释语义剥离后）。"""
import os

def strip_c(t):
    out = []
    for ln in t.split('\n'):
        i, n, cut = 0, len(ln), len(ln)
        while i < n:
            ch = ln[i]
            if ch == '\\':
                i += 2
                continue
            if ch == '%':
                cut = i
                break
            i += 1
        out.append(ln[:cut])
    return '\n'.join(out)

ROOT = r'C:\提示词\工作区\M2-第1章量产0911\成卷'
for it in ['导学件/课时06', '导学件/课时01', '拓展册/上册', '导学件/衔接节-1.2.1前']:
    print('=====', it)
    for fn in sorted(os.listdir(os.path.join(ROOT, it))):
        if not fn.endswith('.tex'):
            continue
        t = strip_c(open(os.path.join(ROOT, it, fn), encoding='utf-8').read())
        for ln in t.split('\n'):
            if '（' in ln and ('newcommand' in ln or 'renewcommand' in ln or '\\def' in ln):
                print(' ', fn + ':', ln.strip()[:104])
