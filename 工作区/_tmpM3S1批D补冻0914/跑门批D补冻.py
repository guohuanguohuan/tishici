# -*- coding: utf-8 -*-
r"""跑门批D补冻.py —— M3 S1 批D G5 补冻 对号门执行器（复用 成卷/题面库/对号门.py，不改动该件）。

1) 批D 课时14~17 --strict（G5 补冻验收，71/36/50/42 键）；
2) 全集 strict 复跑（当前 manifest 目录 21 片＝衔接节＋批A 五片＋批B 五片＋批C 四片＋批D 四片＋批E 两片，
   验收态任一断言不等 exit 1；补冻零漂＝全集仍全 ✓）。
对号门.py 本体 TITLES 已含课时10~19（批C/批D/批E 轮先后增注），本轮零注入零改动。
跑法：python 跑门批D补冻.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TMUB = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913', '成卷', '题面库'))
sys.path.insert(0, TMUB)
import 对号门  # noqa: E402

rc = 0
print('== 批D 课时14~17 strict（G5 补冻验收） ==')
for name in ('课时14', '课时15', '课时16', '课时17'):
    try:
        对号门.check_slice(name, strict=True)
    except SystemExit as e:
        rc = e.code or 1
print('== 全集 strict 复跑（manifest 目录 21 片） ==')
sys.argv = ['对号门.py', '--strict']
try:
    对号门.main()
except SystemExit as e:
    rc = rc or (e.code or 0)
print('跑门批D补冻：批D 四片 strict＋全集 strict exit=%d（恒 0 要求＝%s）'
      % (rc, '达标' if rc == 0 else '未达标'))
sys.exit(rc)
