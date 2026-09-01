# -*- coding: utf-8 -*-
"""构建B_navonly.docx：基线B＋仅导航表手术（页数隔离测试用）。"""
import sys
sys.path.insert(0, r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\S盖章\SW脚本')
import 导航表节内口径 as NAV

NAV.WORK = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\S盖章\SW脚本\漂移隔离'
res, fails = NAV.process('B', 'B_navonly.docx', False)
if res:
    print('B_navonly: 改写%d笔 合计%d 断言%s' % (res['n_cells'], res['grand'],
          '全过' if not fails else '失败:' + ';'.join(fails)))
else:
    print('失败:', fails)
