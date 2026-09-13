# -*- coding: utf-8 -*-
r"""跑门批E.py —— M3 S1 批E 对号门执行器（复用 成卷/题面库/对号门.py，不改动该件）。

1) 批E 三片 --strict（验收态，不等 exit 1）；
2) 全集报告态（批B 五片＋批E 三片＝8 片，报告态恒 exit 0）。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TMUB = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913', '成卷', '题面库'))
sys.path.insert(0, TMUB)
import 对号门  # noqa: E402

对号门.TITLES.update({
    '课时18': '2.8②压轴综合二',
    '课时19': '章末总结与复习',
    '衔接节': '',
})

rc = 0
print('== 批E 三片 strict ==')
for name in ('衔接节', '课时18', '课时19'):
    try:
        对号门.check_slice(name, strict=True)
    except SystemExit as e:
        rc = e.code or 1
print('== 全集报告态（8 片） ==')
sys.argv = ['对号门.py']
try:
    对号门.main()
except SystemExit as e:
    rc = rc or (e.code or 0)
print('跑门批E：strict+报告态 exit=%d（报告态恒 0 要求＝%s）' % (rc, '达标' if rc == 0 else '未达标'))
sys.exit(rc)
