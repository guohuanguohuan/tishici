# -*- coding: utf-8 -*-
r"""跑门批E补冻.py —— M3 S1 批E G5 补冻 对号门执行器（复用 成卷/题面库/对号门.py，不改动该件）。

1) 批E 课时18/19 --strict（G5 补冻验收，21 键）＋衔接节 strict（恒等复跑）；
2) 受影响全集报告态（当前 manifest 目录 17 片＝批A 五片＋批B 五片＋批D 四片＋批E 三片，报告态恒 exit 0）。
   批D 四片（14~17）titles 由本轮注入（对号门.py 本体 TITLES 仅载批A/B，射程扩展仍留总闸轮）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TMUB = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913', '成卷', '题面库'))
sys.path.insert(0, TMUB)
import 对号门  # noqa: E402

对号门.TITLES.update({
    '课时14': '2.6.2双曲线性质',
    '课时15': '2.7.1抛物线方程',
    '课时16': '2.7.2抛物线性质',
    '课时17': '2.8①压轴综合一',
    '课时18': '2.8②压轴综合二',
    '课时19': '章末总结与复习',
    '衔接节': '',
})

rc = 0
print('== 批E 课时18/19 strict（G5 补冻验收） ==')
for name in ('课时18', '课时19'):
    try:
        对号门.check_slice(name, strict=True)
    except SystemExit as e:
        rc = e.code or 1
print('== 衔接节 strict（恒等复跑） ==')
try:
    对号门.check_slice('衔接节', strict=True)
except SystemExit as e:
    rc = rc or (e.code or 1)
print('== 受影响全集报告态（manifest 目录全片） ==')
sys.argv = ['对号门.py']
try:
    对号门.main()
except SystemExit as e:
    rc = rc or (e.code or 0)
print('跑门批E补冻：strict+报告态 exit=%d（恒 0 要求＝%s）' % (rc, '达标' if rc == 0 else '未达标'))
sys.exit(rc)
