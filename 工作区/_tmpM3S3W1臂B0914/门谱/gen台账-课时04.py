# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时04.json（练习件版）。
承母版 工作区/_tmpM3S3母版0914/门谱/gen台账.py 复刻，写域改本片。
唯一写域：成卷/练习件/课时04-点斜式与斜截式/值台账-课时04.json。冻结 manifest 本体只读。
（S3 练习件产出清单＝main.tex＋双壳＋值台账 json，不产 件manifest.json。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时04-点斜式与斜截式'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '值台账底稿-课时04.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（22 键），件账只收练键序 E1~E16（拓区隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时04-E7': '括线；两问题 \liubai[24mm]；详解(1)(2) \\par\\noindent 每式独立成段'
                       '（catcode 口径：控制词后带空格断开，防 CJK 吸并入 csname）',
    '2章-练-课时04-E4': '括线；题面空位 \\kongda{x＋2y−2＝0或2x＋3y−6＝0}'
                       '（详解版印答、纯题版退定宽空线，两档等形）',
    '2章-练-课时04-E14': '括线；题面空位 \\kongda{x＋2y−6＝0}（同 E4 开关宏口径）',
}
CLEAN = {
    '2章-练-课时04-E6': '印面详解剔批A 检验句 ✓ 记号（亲算注记不印；检验句文句保留，承导学件04 冻面）；'
                       '值仅「a＝0；b＝4」照答案侧逐字',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋降档
    '2章-练-课时04-E1': ('单选', '四连排', ''), '2章-练-课时04-E2': ('单选', '单列', ''),
    '2章-练-课时04-E3': ('单选', '两连排', ''), '2章-练-课时04-E4': ('填空', '', ''),
    '2章-练-课时04-E5': ('解答', '', '16mm'), '2章-练-课时04-E6': ('解答', '', '16mm'),
    '2章-练-课时04-E7': ('解答', '', '24mm'), '2章-练-课时04-E8': ('解答', '', '24mm'),
    '2章-练-课时04-E9': ('解答', '', '32mm'), '2章-练-课时04-E10': ('解答', '', '32mm'),
    '2章-练-课时04-E11': ('单选', '四连排', ''), '2章-练-课时04-E12': ('单选', '四连排', ''),
    '2章-练-课时04-E13': ('单选', '两连排', ''), '2章-练-课时04-E14': ('填空', '', ''),
    '2章-练-课时04-E15': ('解答', '', '32mm'), '2章-练-课时04-E16': ('解答', '', '24mm'),
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
    '件': '课时04-点斜式与斜截式 练习件（M3 成卷轮 S3 W1 臂B·母版照抄件·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序 E1~E16 零重排；\\tihao 号＝\\ansitem 号同键同号',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang），实测两道超宽降档：'
               '题2(E2) 最宽槽A/D 42.3mm>四连排19.56mm 亦>两连排38.20mm→单列；'
               '题3(E3) strict 档 B/C/D 槽估宽 49.4~56.2pt 达槽宽91%~103%（D槽真超宽）→两连排；'
               '题13(E13) 最宽槽B/D 28.4mm>19.56mm→两连排；'
               '题1(E1)/题11(E11)/题12(E12) 四连排落位（双档0旗）；'
               '禁缩字号/负kern/删标点凑宽（零违例）。另：题11 题干段与选项行间置段落分隔'
               '（短题干接满宽选项行第三轮松行病灶，探针实证，母版单列选项同例）',
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
    'gen': 'W1臂B 门谱/gen台账-课时04.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时04.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时04.json → 片目录')
