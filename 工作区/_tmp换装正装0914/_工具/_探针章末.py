# -*- coding: utf-8 -*-
"""探针：章末件 书写位与结构线分布。"""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
tex = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'M2导学本',
                           '章末-本章总结提升', 'main.src.tex'), encoding='utf-8').read()
pat = re.compile(r'\\(zhankong\{\d+mm\}|huaxing\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\}'
                 r'|liB\{[^}]*\}|begin\{multicols\}|end\{multicols\}|columnbreak|zhantou\{[^}]*\}'
                 r'|pingtou\{[^}]*\}|section\*?\{[^}]*\}|part\*?\{[^}]*\})')
for m in pat.finditer(tex):
    print('%6d  %s' % (m.start(), m.group(0).replace('\n', ' ')[:70]))
