# -*- coding: utf-8 -*-
"""续作二·ROW_B 判据引文出处更正（前次误归 0826 节；逐字引文实系 0825 补充登记节，另补 0826 节实测句）"""
import sys

T = '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·删除台账.md'
OLD = ('（判据＝过程对账·0826全库复审轮 纠错记录条明载「大招17典2题后反思求导段改写为联立判别式法'
       '（课标内解法改写例外）」）')
NEW = ('（判据两处：过程对账·「补充登记（装配期隐藏题扫描发现，2026-08-25）」节纠错记录条「大招17典2题后反思求导段改写为'
       '联立判别式法（课标内解法改写例外）」；过程对账·「2026-08-26 全库复审轮（6子代理并行＋总控交叉验证；第2章部分）」节「回潮剔除项清理」条'
       '「题269反思求导段改联立判别式法（导数属选必2）」）')

raw = open(T, 'rb').read().decode('utf-8')
crlf0, bare0 = raw.count('\r\n'), raw.count('\n') - raw.count('\r\n')
if raw.count(OLD) != 1:
    print('!! 锚点命中%d（应1）' % raw.count(OLD)); sys.exit(1)
if NEW in raw:
    print('!! 已更正过，防重跑中止'); sys.exit(1)
out = raw.replace(OLD, NEW)
if out.count('\n') - out.count('\r\n') != bare0 or out.count('\r\n') != crlf0:
    print('!! 行尾漂移，中止'); sys.exit(1)
if '--dry' in sys.argv:
    print('DRY OK  CRLF %d 裸LF %d' % (crlf0, bare0)); sys.exit(0)
open(T, 'wb').write(out.encode('utf-8'))
print('更正 ROW_B 判据出处：CRLF %d→%d｜裸LF %d 不变' % (crlf0, out.count('\r\n'), bare0))
