# -*- coding: utf-8 -*-
r"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时07.json（练习件版）。
唯一写域：成卷/练习件/课时07-圆的方程/值台账-课时07.json。冻结 manifest 本体只读。
（照抄 W1臂A gen台账-课时02.py 工艺：底稿 vals 系答案侧全集 21 键（练16＋导5），
滤练键序 T1~T16 后才入台账——过滤步不可删，不过滤则对平门三源红（导 5 键浮账）。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时07-圆的方程'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '底稿-课时07.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（21 键），件账只收练键序 T1~T16（拓区隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时07-T7': '括线；多选 \\duoxuan 题号行后附，选项 \\lxopt 单列',
    '2章-练-课时07-T10': '括线；多选 \\duoxuan 题号行后附，选项两连排（短选项降档两连排）',
    '2章-练-课时07-T11': '括线；题面空位 \\kongda{x²+y²−4x+6y+8=0}'
                        '（详解版印答、纯题版退定宽空线，两档等形）',
    '2章-练-课时07-T12': '括线；题面空位 \\kongda{(x−1)²+y²=9（答案不唯一）}'
                        '（开放题载答案侧全值含尾注）',
    '2章-练-课时07-T13': '括线；三空逐空 \\kongda{64}/\\kongda{4}/\\kongda{[3−2√2, 3+2√2]}',
    '2章-练-课时07-T14': '括线；两空逐空 \\kongda{(−2,−4)}/\\kongda{5}',
    '2章-练-课时07-T15': '括线；\\liubai[32mm]；(3) 导数三分支照批B 落盘版照录',
    '2章-练-课时07-T16': '括线；\\liubai[16mm]',
}
CLEAN = {
    '2章-练-课时07-T15': '题面【注】（8x→8y 系批B 勘误过程语）不入印面；值照答案侧逐字',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋降档（终档槽档普查.py 实测）
    '2章-练-课时07-T1': ('单选', '两连排', ''), '2章-练-课时07-T2': ('单选', '单列', ''),
    '2章-练-课时07-T3': ('单选', '两连排', ''), '2章-练-课时07-T4': ('单选', '两连排', ''),
    '2章-练-课时07-T5': ('单选', '两连排', ''), '2章-练-课时07-T6': ('单选', '两连排', ''),
    '2章-练-课时07-T7': ('多选', '单列', ''), '2章-练-课时07-T8': ('单选', '四连排', ''),
    '2章-练-课时07-T9': ('单选', '四连排', ''), '2章-练-课时07-T10': ('多选', '两连排', ''),
    '2章-练-课时07-T11': ('填空', '', ''), '2章-练-课时07-T12': ('填空', '', ''),
    '2章-练-课时07-T13': ('填空', '', ''), '2章-练-课时07-T14': ('填空', '', ''),
    '2章-练-课时07-T15': ('解答', '', '32mm'), '2章-练-课时07-T16': ('解答', '', '16mm'),
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
    '件': '课时07-圆的方程 练习件（M3 成卷轮 S3 W2 臂A·照抄练习件线母版体例·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序 T1~T16 零重排；\\tihao 号＝\\ansitem 号同键同号',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang＝19.10mm；strict 预警 0.85×槽宽＝16.23mm；'
               '两连排槽 37.44mm、预警 31.82mm），实测（门谱同源 ink_em 口径 10.5pt 档）：'
               '初版 strict 4旗（四连排原档超 85% 预警槽）→降题2(T2) 单列、题3/6(T3/T6) 两连排后清零；'
               '终档＝题8/9(T8/T9) 四连排原档（最宽39.4/21.0pt 占72%/39%）、'
               '题1/3/4/5/6/10 两连排（最宽85.1/52.0/87.9/85.8/50.4/59.9pt 占80/49/83/81/48/56%）、'
               '题2 单列（单选）、题7 单列（多选）；禁缩字号/负kern/删标点凑宽（零违例）',
    '图债': '无（全件零图依赖，题面无「如图」占位，includegraphics 零处）',
    '清洗口径': '印面 ✓ 记号全剔（检验句文句保留，rg 实测 0 残留）；详解句号照录批B 原文「。」',
    '难度词口径': '照题面 \\tieside 第1字段：0.94→简单、0.85→中档、0.65→中档；'
                '题1/2/4/8/12(T1/T2/T4/T8/T12) 简单，余11键中档',
    '知识点口径': '照导学件 zsd 知识导学口径：一＝圆的标准方程、二＝点与圆位置关系、'
                '三＝一般方程与表圆条件；zsd 与 tjdnr 异序，已作异动回核点登记',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 3页；false 同 2页',
    },
    '门谱': ['门-守恒对号-课时07.py（全绿）', '门-值快照键型判模-课时07.py（全绿）',
            '门-回流-课时07.py（全绿）', '键账对平门.py 三源对平 PASS',
            'makebox槽宽门.py zero-fp/strict 双档 0旗（槽32）',
            'CJK 审计 rg \\\\w+\\p{Han} 零命中'],
    'gen': '门谱/gen台账-课时07.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时07.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时07.json → 片目录')
