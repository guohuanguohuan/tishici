# -*- coding: utf-8 -*-
"""批6章末件排版整形：①页脚 \qpceming 换 A 版册名；②12 型块去强制 \\columnbreak、逐块包 \\vbox 防拆块。"""
import io, re, os

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'M2-第1章量产0911', '成卷', '导学件', '章末-本章总结提升', 'main.tex')
p = os.path.normpath(p)
s = io.open(p, encoding='utf-8').read()

# 1) footer param renew (documented reuse entry; module semantics untouched)
old = r'\renewcommand{\qpjianming}{导学件}'
new = (r'\renewcommand{\qpjianming}{导学件}' '\n'
       r'\renewcommand{\qpceming}{高中数学\quad 选择性必修第一册(人教A版)}  % 模块默认册名＝B版样张源，本件属人教A版，偶页页脚随实（参数宏复用入口，非模块语义改动）')
assert s.count(old) == 1
s = s.replace(old, new)

# 2) section 1 (题型归类): drop forced column breaks, wrap each block in \vbox
i0 = s.index(r'\huaxing{题}{型}{归}{类}')
i1 = s.index(r'\end{multicols}')
sec = s[i0:i1]
sec = sec.replace('\n\\columnbreak\n', '\n')

parts = re.split(r'(?m)^(?=\\lxing\{)', sec)
out = []
for part in parts:
    if part.startswith('\\lxing{'):
        part = part.rstrip() + '\n}\n\n'
        part = '\\vbox{\n' + part
    out.append(part)
sec = ''.join(out)
s = s[:i0] + sec + s[i1:]

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('vbox count:', s.count('\\vbox{'), '| columnbreak left:', s.count('\\columnbreak'), '| qpceming:', s.count('\\renewcommand{\\qpceming}'))
