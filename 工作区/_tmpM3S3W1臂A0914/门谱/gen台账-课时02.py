# -*- coding: utf-8 -*-
r"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时02.json（练习件版）。
唯一写域：成卷/练习件/课时02-倾斜角与斜率/值台账-课时02.json。冻结 manifest 本体只读。
（照抄母版 gen台账.py 工艺：底稿 vals 系答案侧全集 25 键，滤练键序 E1~E16 后才入台账——
过滤步不可删，不过滤则对平门三源红（导 5＋拓 4 共 9 键浮账）。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时02-倾斜角与斜率'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '底稿-课时02.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（25 键），件账只收练键序 E1~E16（拓区隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时02-E1': '括线；图债在途（国旗五星坐标图，解算不依赖图，「如图」占位保留）；'
                       '详解 ∵∴ 文字符走 TNR（探针实测有字形）',
    '2章-练-课时02-E6': '括线；多选 \\duoxuan 题号行后附；⟺ 宏化为 \\(\\Longleftrightarrow\\)（TNR 无 U+27FA，探针实测）',
    '2章-练-课时02-E8': '括线；批A 检验句「（合理性：…）」文句保留、句内 ✓ 记号剔（亲算注记不印）',
    '2章-练-课时02-E10': '括线；题面空位 \\kongda{(−∞,1)∪(1,+∞)}（详解版印答、纯题版退定宽空线，两档等形）',
    '2章-练-课时02-E11': '括线；题面空位 \\kongda{[√3/3, √3)}',
    '2章-练-课时02-E12': '括线；题面空位 \\kongda{[1,+∞)∪(−∞,−√3]}；详解每式独立成段（Underfull 治理）',
    '2章-练-课时02-E13': '括线；值行「−2−√3」；详解长式 \\par\\noindent 独立成段',
    '2章-练-课时02-E16': '括线；四小问 \\liubai[32mm]；详解逐小问 \\par\\noindent 独立成段',
}
CLEAN = {
    '2章-练-课时02-E1': '题面【注】图债行不入印面；值仅「C」照答案侧逐字',
    '2章-练-课时02-E5': '批A 详解尾「（注：本选项组为本卷补写——…）」系改形过程语，剔印面（题面侧【注】同不入）；'
                       '值仅「A」照答案侧逐字',
    '2章-练-课时02-E8': '批A 检验句尾 ✓ 记号剔（检验句文句保留）；值仅「B」照答案侧逐字',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋降档梯位
    '2章-练-课时02-E1': ('单选', '四连排', ''), '2章-练-课时02-E2': ('单选', '两连排', ''),
    '2章-练-课时02-E3': ('单选', '两连排', ''), '2章-练-课时02-E4': ('单选', '单列', ''),
    '2章-练-课时02-E5': ('单选', '单列', ''), '2章-练-课时02-E6': ('多选', '四连排', ''),
    '2章-练-课时02-E7': ('单选', '四连排', ''), '2章-练-课时02-E8': ('单选', '四连排', ''),
    '2章-练-课时02-E9': ('单选', '四连排', ''), '2章-练-课时02-E10': ('填空', '', ''),
    '2章-练-课时02-E11': ('填空', '', ''), '2章-练-课时02-E12': ('填空', '', ''),
    '2章-练-课时02-E13': ('解答', '', '16mm'), '2章-练-课时02-E14': ('解答', '', '16mm'),
    '2章-练-课时02-E15': ('解答', '', '16mm'), '2章-练-课时02-E16': ('解答', '', '32mm'),
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
    '件': '课时02-倾斜角与斜率 练习件（M3 成卷轮 S3 W1 臂A·照抄课时01 母版体例·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序 E1~E16 零重排；\\tihao 号＝\\ansitem 号同键同号',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang＝19.10mm；strict 预警 0.85×槽宽＝16.23mm），'
               '实测（门谱同源 ink_em 口径 10.5pt 档）：题2(E2) B槽17.9mm>16.23→两连排；'
               '题3(E3) C/D槽22.7mm>21.60（四连排零误报阈）→两连排；题4(E4) A/C槽37.0mm 占两连排槽37.28mm '
               '99%（>31.69 strict 预警）→单列；题5(E5) C槽40.9mm>39.78（两连排零误报阈）→单列；'
               '题1/6/7/8/9 最宽9.2~13.7mm≤16.23→四连排原档；禁缩字号/负kern/删标点凑宽（零违例）',
    '图债': 'E1 国旗五星坐标图（成品卷①原图未嵌入；答案侧注记「解算不依赖图」；题面「如图」占位保留，'
           '冻值不受影响；图工位补图后回冲印面）',
    '知识点预排注记': '难度词照题面侧头标第4字段逐字；知识点 N 系预排（本课时知识点一＝直线的倾斜角、'
                  '二＝直线的斜率、三＝倾斜角与斜率互求，照批A 课时切分描述；导学件课时02 尚未落盘，'
                  '落盘后如异动按变更协议回核）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 3页；false 同 2页',
    },
    '门谱': ['门-守恒对号-课时02.py（全绿）', '门-值快照键型判模-课时02.py（全绿）',
            '门-回流-课时02.py（全绿）', '键账对平门.py 三源对平 PASS',
            'makebox槽宽门.py zero-fp/strict 双档 0旗（槽28）',
            'CJK 审计 rg \\\\w+\\p{Han} 零命中'],
    'gen': '门谱/gen台账-课时02.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时02.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时02.json → 片目录')
