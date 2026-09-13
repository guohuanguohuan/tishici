# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时14-2.6.2双曲线性质/main.tex'
mode = sys.argv[1]
BS = chr(92)
seg2 = (BS + 'par' + BS + 'noindent （ii）韦达分子分母化简'
        + BS + '(4k^{2}+3+4k^{2}+k^{2}-3=9k^{2}' + BS + ')、'
        + BS + '(4k^{2}+3-4k^{2}+k^{2}-3=k^{2}' + BS + ')，比值9合。')
s = open(p, encoding='utf-8').read()
if mode == 'remove2':
    assert seg2 in s, '（ii）段未找到'
    s = s.replace(seg2, '')
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print('（ii）段已移除')
elif mode == 'restore':
    if seg2 not in s:
        anchor = '上合；'
        assert anchor in s
        s = s.replace(anchor, anchor + seg2, 1)
        open(p, 'w', encoding='utf-8', newline='\n').write(s)
        print('（ii）段已还原')
    else:
        print('（ii）段本在')
