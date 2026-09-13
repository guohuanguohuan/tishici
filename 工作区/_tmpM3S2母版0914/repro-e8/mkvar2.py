import io
B = chr(92)
src = io.open('repro.tex', encoding='utf-8').read()
cands = [l for l in src.split('\n') if l.startswith(B + 'ansnote{')]
L = [l for l in cands if B + 'par' in l][0]
PN = B + 'par' + B + 'noindent'
assert L.count(PN) == 4
# v4: \par\noindent 后的 所以 换成 ASCII
v4 = src.replace(L, L.replace('所以' + B + '(|AB|=|AC|', 'SuoYi' + B + '(|AB|=|AC|'))
# v5: 换另一对常用 CJK（我们）
v5 = src.replace(L, L.replace('所以' + B + '(|AB|=|AC|', '我们' + B + '(|AB|=|AC|'))
# v6: \par\noindent 与 所以 之间加空格
v6 = src.replace(L, L.replace(PN + '所以', PN + ' 所以'))
# v7: \noindent 换 \indent
v7 = src.replace(L, L.replace(PN + '所以', B + 'par' + B + 'indent所以'))
for name, body in [('v4', v4), ('v5', v5), ('v6', v6), ('v7', v7)]:
    io.open(name + '.tex', 'w', encoding='utf-8', newline='').write(body)
print('ok')
