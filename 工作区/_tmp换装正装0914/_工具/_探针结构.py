# -*- coding: utf-8 -*-
"""探针：课时件 探段→ketang 之间的结构线（liB/xiaojie/zhankong/jiancestem 等）。"""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TREE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'M2导学本')
piece = sys.argv[1] if len(sys.argv) > 1 else '课时01'
tex = io.open(os.path.join(TREE, piece, 'main.src.tex'), encoding='utf-8').read()
tj = [m.start() for m in re.finditer(r'\\tjdnr\{', tex)]
ko = tex.find('\\vbox')
if ko < 0:
    ko = tex.find('\\begin{ketang}')
print('tjdnr@', tj, 'ket_open@', ko)
segs = tj + [ko]
for i in range(len(segs) - 1):
    a, b = segs[i], segs[i + 1]
    print('--- seg %d: [%d,%d) ---' % (i, a, b))
    for m in re.finditer(r'\\(liB|xiaojie|zhankong|jiancestem|zhentib|zhenhead|ketang|multicols|huaxing|liangshi)\b', tex[a:b]):
        print('  @%d \\%s' % (a + m.start(), m.group(1)))
