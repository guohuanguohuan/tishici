# -*- coding: utf-8 -*-
"""片G 三0扫描器：读 xelatex log，输出 error/overfull/underfull/missing char/warning/页数。"""
import re
import sys

def scan(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    out = {}
    out['pages'] = (re.search(r'Output written on .*\((\d+) page', s) or [None, '?'])[1]
    out['error'] = len(re.findall(r'^!', s, re.M))
    out['overfull'] = len(re.findall(r'Overfull \\\\hbox', s))
    out['underfull'] = len(re.findall(r'Underfull \\\\hbox', s))
    out['underfull_vbox'] = len(re.findall(r'Underfull \\\\vbox', s))
    out['missing_char'] = len(re.findall(r'Missing character', s))
    out['latex_warning'] = len(re.findall(r'LaTeX Warning', s))
    out['font_warning'] = len(re.findall(r'Package .* Warning', s))
    return out

if __name__ == '__main__':
    for p in sys.argv[1:]:
        d = scan(p)
        print(p, d)
