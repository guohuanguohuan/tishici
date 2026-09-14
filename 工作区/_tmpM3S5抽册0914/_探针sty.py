# -*- coding: utf-8 -*-
import re
sty = open('工作区/M3-第2章量产0913/成卷/导学件/课时01-坐标法/qp-m3.sty',
           encoding='utf-8').read()
print('sty 行数', sty.count('\n'))
for mac in ('zhangtitle', 'jietitle', 'xiaojietitle', 'keshi', 'xjkeshi',
            'biaoqian', 'tailfill', 'glueguard', 'ansblock', 'M3-ANSKEY',
            'ansitem', 'ansnote', 'ansblockgray'):
    pat = re.compile(re.escape(chr(92) + mac))
    ms = [m.start() for m in pat.finditer(sty)]
    print('==', mac, '出现', len(ms))
    for i in ms[:2]:
        print('   …', sty[max(0, i - 70):i + 150].replace('\n', '⏎')[:200])
