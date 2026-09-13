# -*- coding: utf-8 -*-
"""续作二·ROW_B 追加判据引文（过程对账 0826 复审轮纠错记录条，用§＋关键词定位）"""
import sys

T = '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何·删除台账.md'
OLD = '成品侧0826复审已改写为「过点A、B的切线斜率由联立判别式为零求得」——本轮 live 复扫该段现文无「y′」「求导」字样，故本行无成品删除动作、纯补登记'
NEW = ('成品侧0826复审已改写为「过点A、B的切线斜率由联立判别式为零求得」'
       '（判据＝过程对账·0826全库复审轮 纠错记录条明载「大招17典2题后反思求导段改写为联立判别式法（课标内解法改写例外）」）'
       '——本轮 live 复扫该段现文（成品el501＝转储L518）无「y′」「求导」字样，故本行无成品删除动作、纯补登记')

raw = open(T, 'rb').read().decode('utf-8')
crlf0, bare0 = raw.count('\r\n'), raw.count('\n') - raw.count('\r\n')
if raw.count(OLD) != 1:
    print('!! 锚点命中%d（应1）' % raw.count(OLD)); sys.exit(1)
if NEW in raw:
    print('!! 目标已存在，防重跑中止'); sys.exit(1)
out = raw.replace(OLD, NEW)
if out.count('\n') - out.count('\r\n') != bare0:
    print('!! 裸LF漂移，中止'); sys.exit(1)
if '--dry' in sys.argv:
    print('DRY OK  CRLF %d 裸LF %d' % (crlf0, bare0)); sys.exit(0)
open(T, 'wb').write(out.encode('utf-8'))
print('写入 ROW_B 判据引文：CRLF %d→%d｜裸LF %d 不变' % (crlf0, out.count('\r\n'), bare0))
