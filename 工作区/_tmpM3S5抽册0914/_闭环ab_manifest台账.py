# -*- coding: utf-8 -*-
"""闭环 a＋b（工单 §三.8／§六.2 件侧同批办）。
闭环a：课时02 件manifest.json `键↔号` 字段语义确认＋刷新——
  语义＝印面号快照（三证：①课时01 同字段与台账印面号/件内实印 0 漂；
  ②母版体例说明 §六「键↔号映射见 值台账」＝该词指印面号映射；③体例说明件manifest
  职责仅「键序＋sha＋锁」，键↔号系派生快照非独立口径）→ 按印面号语义刷新 15 键
  ＝S5 已回填台账值（＝件内 ansitem 实印）。
  文件级 sha 钉核查：件manifest.json 无外部 sha 钉（题面库 manifest 钉题面库 md、
  台账指纹钉 main.tex/pdf、toolchain 锁钉 sty——均不含本件）→ 未钉直改＋变更注记登记。
闭环b：值台账-课时02.json 「印面连号制」注记勘误——E 段号序＝装配序非键尾号序
  （E2 实印 9、E9 实印 2），旧注「E1—E16（1—16）」按段聚合虽真、按尾号读即误
  （台账旧值即此误读产物），改为装配序实映射表述。其余字段零动。零 git。
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
PD = os.path.join(CJ, '导学件', '课时02-倾斜角与斜率')

# —— 闭环a：件manifest 键↔号 刷新 ——
mm_path = os.path.join(PD, '件manifest.json')
mm = json.load(open(mm_path, encoding='utf-8'))
lt = json.load(open(os.path.join(PD, '值台账-课时02.json'), encoding='utf-8'))
led = {it['键']: it['印面号'] for it in lt['items']}
kv = mm['键↔号']
diff = {k: (kv[k], led[k]) for k in kv if led[k] != kv[k]}
assert len(kv) == len(led), '键集规模不等'
assert set(kv) == set(led), '键集不等'
for k in kv:
    kv[k] = led[k]
after = sum(1 for k in kv if led[k] != kv[k])
assert not diff or after == 0, '刷新未落'
note = ('；0914 S5-W2 闭环a：键↔号 字段按印面号语义刷新 15 键'
        '（E9→2、E15→3、E16→4、E7→5、E14→6、E10→7、E6→8、E2→9、E8→10、E3→11、'
        'E4→12、E5→13、E11→14、E12→15、E13→16，＝值台账 0914 回冲后值＝件内 ansitem 实印；'
        '语义三证与无 sha 钉核查见 _tmpM3S5抽册0914/器升制报告.md §闭环a）')
if 'S5-W2 闭环a' not in mm.get('变更注记', ''):
    mm['变更注记'] = mm.get('变更注记', '') + note
json.dump(mm, open(mm_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('闭环a：键↔号 刷新 %d 键（语义＝印面号快照，未钉直改＋变更注记登记）' % len(diff))

# —— 闭环b：值台账 印面连号制 注记勘误 ——
lt_path = os.path.join(PD, '值台账-课时02.json')
lt['印面连号制'] = ('1–25＝装配序连号：课时练习 E 段 1—16＋拓展变式 T1—T4（17—20）＋'
                    '课堂评价 G1—G5（21—25）。E 段号序＝件内装配序，非键尾号序'
                    '（实印映射 E1:1、E9:2、E15:3、E16:4、E7:5、E14:6、E10:7、E6:8、E2:9、'
                    'E4:10、E3:11、E8:12、E5:13、E11:14、E12:15、E13:16——逐键以 items[].印面号 '
                    '为准）；ansitem 首参＝印面号，与 manifest 逻辑键序（G 前练中拓后）同集不同序，'
                    '装配序登记于 门-守恒对号（0914 S5-W2 闭环b 勘误：原注「E1—E16（1—16）」'
                    '按段聚合虽真、按尾号读即误，系台账旧值误读之源）')
json.dump(lt, open(lt_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('闭环b：印面连号制 注记勘误落库（其余字段零动）')
