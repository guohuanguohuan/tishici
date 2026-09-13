import io
B = chr(92)
src = io.open('repro.tex', encoding='utf-8').read()
cands = [l for l in src.split('\n') if l.startswith(B + 'ansnote{')]
print('cands:', len(cands))
L = [l for l in cands if B + 'par' in l][0]
print('match len', len(L))
PN = B + 'par' + B + 'noindent'
assert L.count(PN) == 4, L.count(PN)
v1 = src.replace(L, L.replace(PN, B + 'par '))
v2 = src.replace(L, L.replace(PN, B + 'noindent'))
i = L.rindex(PN)
v3 = src.replace(L, L[:11] + L[13:i] + L[i:])
for name, body in [('v1', v1), ('v2', v2), ('v3', v3)]:
    io.open(name + '.tex', 'w', encoding='utf-8', newline='').write(body)
print('ok')
