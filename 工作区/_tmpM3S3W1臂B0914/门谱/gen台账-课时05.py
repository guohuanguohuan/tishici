# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时05.json（练习件版）。
承臂B 门谱/gen台账-课时04.py 复刻，写域改本片。
唯一写域：成卷/练习件/课时05-两点式与一般式/值台账-课时05.json。冻结 manifest 本体只读。
（S3 练习件产出清单＝main.tex＋双壳＋值台账 json，不产 件manifest.json。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时05-两点式与一般式'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '值台账底稿-课时05.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（24 键），件账只收练键序 16 键（拓区隔离＋前移6席空号非键）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时05-E7': '括线；两连排选项（0.5\\linewidth−0.5\\lxhang−0.25em ×2行）零降档落位'
                       '（catcode 口径：控制词后带空格断开，防 CJK 吸并入 csname）',
    '2章-练-课时05-E11': '括线；题面空位 \\kongda{2x−y＋1＝0}'
                        '（详解版印答、纯题版退定宽空线，两档等形）',
    '2章-练-课时05-E19': '括线；题面空位 \\kongda{②④}；题首（提示：…§2.2.4…）行＝印面照录',
    '2章-练-课时05-E20': '括线；题面空位 \\kongda{4√3/3或12√3}；题首（提示：同05-E19…）行＝印面照录',
    '2章-练-课时05-E17': '括线；详解尾（注：本选项组为本卷补写…）照导学件05 冻面保留（回编自T2改形）',
    '2章-练-课时05-E18': '括线；详解尾（注：本选项组为本卷补写…）照导学件05 冻面保留（回编自T4改形）',
    '2章-练-课时05-E22': '括线；详解(1) 课时03法向量括注照导学件05 冻面保留',
}
CLEAN = {}
SLOT = {  # 槽型对账（题面侧 头标实录）＋书写区＋选项槽位
    '2章-练-课时05-E2': ('单选', '四连排', ''), '2章-练-课时05-E3': ('单选', '单列', ''),
    '2章-练-课时05-E5': ('单选', '单列', ''), '2章-练-课时05-E6': ('单选', '单列', ''),
    '2章-练-课时05-E7': ('单选', '两连排', ''), '2章-练-课时05-E9': ('单选', '单列', ''),
    '2章-练-课时05-E10': ('单选', '单列', ''), '2章-练-课时05-E11': ('填空', '', ''),
    '2章-练-课时05-E15': ('解答', '', '16mm'), '2章-练-课时05-E16': ('解答', '', '32mm'),
    '2章-练-课时05-E17': ('单选', '单列', ''), '2章-练-课时05-E18': ('单选', '四连排', ''),
    '2章-练-课时05-E19': ('填空', '', ''), '2章-练-课时05-E20': ('填空', '', ''),
    '2章-练-课时05-E21': ('解答', '', '16mm'), '2章-练-课时05-E22': ('解答', '', '24mm'),
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
    '件': '课时05-两点式与一般式 练习件（M3 成卷轮 S3 W1 臂B·母版照抄件·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序（跳号对号档零重排：E2/E3/E5/E6/E7/E9/E10/E11/E15/E16/E17~E22；'
                '前移6席 E1/E4/E8/E12/E13/E14 留空号非键，键面已入课时04）；\\tihao 号＝\\ansitem 号同键同号',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang）；本片预设三道连排'
               '（题1(E2)/题12(E18) 四连排、题5(E7) 两连排）＋余六道单列（题2/3/4/6/7/11＝E3/E5/E6/E9/E10/E17），'
               'makebox槽宽门 zero-fp＋strict 双档全 0 旗（槽12 过12）——零降档；'
               '全部选项行前置空行分段（04 题11 短题干病灶预防口径，探针实证）；'
               '禁缩字号/负kern/删标点凑宽（零违例）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 5页；false 同 2页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            '键账对平门.py 三源对平 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗',
            'CJK 审计 rg \\\\w+\\p{Han} 零命中'],
    'gen': 'W1臂B 门谱/gen台账-课时05.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时05.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时05.json → 片目录')
