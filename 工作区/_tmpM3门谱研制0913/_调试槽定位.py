# -*- coding: utf-8 -*-
"""调试2：dimexpr 解析探针。"""
import re, io, sys, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
spec_mod = importlib.util.spec_from_file_location('gate', r'C:/提示词/工具/makebox槽宽门.py')
g = importlib.util.module_from_spec(spec_mod)
spec_mod.loader.exec_module(g)

w = r'\dimexpr0.25\linewidth-0.5em\relax'
s2 = w.replace('\\dimexpr', '').replace('\\relax', '').strip()
print('after replace:', repr(s2))
toks = re.findall(r'([+-]?)\s*([0-9.]+)\s*(\\linewidth|\\xhang|\\lxhang|mm|em|pt)', s2)
print('toks:', toks)
residue = re.sub(r'\\linewidth|\\xhang|\\lxhang|[0-9.]+(?:mm|em|pt)|[+\-\s]', '', s2)
print('residue:', repr(residue))
print('parse:', g.parse_dimexpr_mm(w, 10.5, 84.0, 13.0, 7.6))
