# -*- coding: utf-8 -*-
"""探查 P1 答案册 body.tex 节结构＋键/解析分布（只读）。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex"
b = io.open(B, encoding='utf-8').read()
secs = [(m.start(), m.group(1)) for m in re.finditer(r'\\jietitle\{([^}]*)\}', b)]
secs.append((len(b), 'EOF'))
for (s, n1), (e, n2) in zip(secs, secs[1:]):
    seg = b[s:e]
    n_p = len(re.findall(r'(?m)^% pair:', seg))
    n_al = len(re.findall(r'\\ansline\{解析\}', seg))
    n_an = len(re.findall(r'\\ansnote', seg))
    if n_p or n_al:
        print('%-30s pair=%-3d ansline解析=%-2d ansnote=%d' % (n1, n_p, n_al, n_an))
# 练/拓 段键样例
for pref in ('练-课时91-', '练-课时92-', '练-课时93-', '练-课时94-', '拓-'):
    ks = re.findall(r'(?m)^% pair:(\S+)', b)
    mine = [k for k in ks if k.startswith(pref)][:3] + ['…'] + [k for k in ks if k.startswith(pref)][-2:]
    print(pref, len([k for k in ks if k.startswith(pref)]), mine)
