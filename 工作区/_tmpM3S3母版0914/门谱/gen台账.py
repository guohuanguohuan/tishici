# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时01.json（练习件版）。
唯一写域：成卷/练习件/课时01-坐标法/值台账-课时01.json。冻结 manifest 本体只读。
（S3 练习件产出清单＝main.tex＋双壳＋值台账 json＋体例说明，不产 件manifest.json。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时01-坐标法'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '值台账底稿.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（23 键），件账只收练键序 E1~E16（拓区隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时01-E1': '括线；详解 ▱ 经 \\pxparallelogram→NSC 子块路由（nscblk NSC-w500）',
    '2章-练-课时01-E8': '括线；值行「证明见详解．」；详解四式 \\par\\noindent 每式独立成段'
                       '（catcode 口径：控制词后带空格断开，防 CJK 吸并入 csname）',
    '2章-练-课时01-E7': '括线；题面空位 \\kongda{2}（详解版印答、纯题版退定宽空线，两档等形）',
    '2章-练-课时01-E15': '括线；详解句号照录批A 原文「。」（E16 同）',
    '2章-练-课时01-E16': '括线；详解句号照录批A 原文「。」',
}
CLEAN = {
    '2章-练-课时01-E6': '印面详解剔批A 检验句两处 ✓ 记号（亲算注记不印；检验句文句保留）；'
                       '值仅「P的坐标为3或−5．」照答案侧逐字',
    '2章-练-课时01-E15': '详解句号照录批A 原文「。」（E16 同）',
    '2章-练-课时01-E16': '详解句号照录批A 原文「。」',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋降档
    '2章-练-课时01-E1': ('单选', '两连排', ''), '2章-练-课时01-E2': ('多选', '单列', ''),
    '2章-练-课时01-E3': ('多选', '单列', ''), '2章-练-课时01-E4': ('填空', '', ''),
    '2章-练-课时01-E5': ('填空', '', ''), '2章-练-课时01-E6': ('填空', '', ''),
    '2章-练-课时01-E7': ('填空', '', ''), '2章-练-课时01-E8': ('解答', '', '16mm'),
    '2章-练-课时01-E9': ('解答', '', '16mm'), '2章-练-课时01-E10': ('解答', '', '16mm'),
    '2章-练-课时01-E11': ('解答', '', '16mm'), '2章-练-课时01-E12': ('解答', '', '16mm'),
    '2章-练-课时01-E13': ('解答', '', '16mm'), '2章-练-课时01-E14': ('解答', '', '16mm'),
    '2章-练-课时01-E15': ('单选', '两连排', ''), '2章-练-课时01-E16': ('单选', '单列', ''),
}

items = []
for it in BASE['items']:
    k = it['键']
    slot, opt, liubai = SLOT[k]
    items.append({
        '键': k,
        '印面号': it['印面号'],
        '键型': it['键型'],
        '槽型': slot,
        '选项槽位': opt or ('四连排' if slot in ('单选', '多选') else '—'),
        '书写区高': liubai or '—',
        '值tex': it['值tex'],
        '值源': it['值源'],
        '值快照': it['值快照'],
        '估高行数': it['估高行数'],
        '判模': it['判模'],
        '渲染注记': RENDER.get(k, '括线；\\ansitem 单条'),
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗'),
    })

ledger = {
    '件': '课时01-坐标法 练习件（M3 成卷轮 S3 母版·题后紧跟答案制·练习件线全波母版）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序 E1~E16 零重排；\\tihao 号＝\\ansitem 号同键同号',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang），实测全件五道选择题均超宽降档：'
               '题1(E1) A槽24.0mm>19.56mm→两连排；题2(E2)/题3(E3) 最宽槽74.0/135.4mm>两连排'
               '37.28~38.20mm→单列；题15(E15) 四槽21.0~30.3mm>19.10mm→两连排；'
               '题16(E16) B/D槽46.9/61.1mm>37.28mm→单列；禁缩字号/负kern/删标点凑宽（零违例）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 4页；false 同 2页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            '键账对平门.py 三源对平 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗',
            'CJK 审计 rg \\\\w+\\p{Han} 零命中'],
    'gen': '门谱/gen台账.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时01.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时01.json → 片目录')
