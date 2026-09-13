# -*- coding: utf-8 -*-
r"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时06.json（练习件版）。
唯一写域：成卷/练习件/课时06-两条直线的位置关系/值台账-课时06.json。冻结 manifest 本体只读。
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

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时06-两条直线的位置关系'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '底稿-课时06.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（21 键），件账只收练键序 T1~T16（拓区隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时06-T8': '括线；多选 \\duoxuan 题号行后附，选项 \\lxopt 单列',
    '2章-练-课时06-T10': '括线；多选 \\duoxuan 题号行后附，选项 \\lxopt 单列',
    '2章-练-课时06-T11': '括线；题面空位 \\kongda{−1}（详解版印答、纯题版退定宽空线，两档等形）',
    '2章-练-课时06-T12': '括线；题面空位 \\kongda{1}',
    '2章-练-课时06-T13': '括线；双空逐空 \\kongda{(1,1)}/\\kongda{√10}；'
                        '题面「（提示：…）」选学注印入（\\tieside 后、题面前，照课时05 E13/E14 先例）',
    '2章-练-课时06-T14': '括线；两小问逐空 \\kongda{m=1 或 6}/\\kongda{m=3 或 −4}',
    '2章-练-课时06-T15': '括线；\\liubai[24mm]；题面 ▱ 经 \\pxparallelogram→NSC 子块路由'
                        '（nscblk NSC-w500）',
    '2章-练-课时06-T16': '括线；\\liubai[24mm]；题面「（提示：…）」选学注印入，'
                        '注内公式宏化 \\(S=|BC|\\cdot h/2=|x_By_C-x_Cy_B|/2\\)（避 ½ 字形风险）',
}
CLEAN = {
    '2章-练-课时06-T3': '题面【注】不入印面；值仅「D」照答案侧逐字',
    '2章-练-课时06-T4': '题面【注】不入印面；值仅「C」照答案侧逐字',
    '2章-练-课时06-T7': '印面详解剔亲算过程语省略号残片（原「两直线 −√2x−(2+√2)y…」半句，'
                       '剔后「系数检验：…」句意完整）；值仅「B」照答案侧逐字',
    '2章-练-课时06-T14': '题面【注】不入印面；值仅小问括号格式照答案侧逐字',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋降档（终档槽档普查.py 实测）
    '2章-练-课时06-T1': ('单选', '两连排', ''), '2章-练-课时06-T2': ('单选', '两连排', ''),
    '2章-练-课时06-T3': ('单选', '四连排', ''), '2章-练-课时06-T4': ('单选', '两连排', ''),
    '2章-练-课时06-T5': ('单选', '两连排', ''), '2章-练-课时06-T6': ('单选', '两连排', ''),
    '2章-练-课时06-T7': ('单选', '四连排', ''), '2章-练-课时06-T8': ('多选', '单列', ''),
    '2章-练-课时06-T9': ('单选', '两连排', ''), '2章-练-课时06-T10': ('多选', '单列', ''),
    '2章-练-课时06-T11': ('填空', '', ''), '2章-练-课时06-T12': ('填空', '', ''),
    '2章-练-课时06-T13': ('填空', '', ''), '2章-练-课时06-T14': ('填空', '', ''),
    '2章-练-课时06-T15': ('解答', '', '24mm'), '2章-练-课时06-T16': ('解答', '', '24mm'),
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
    '件': '课时06-两条直线的位置关系 练习件（M3 成卷轮 S3 W2 臂A·照抄练习件线母版体例·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序 T1~T16 零重排；\\tihao 号＝\\ansitem 号同键同号',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang＝19.10mm；strict 预警 0.85×槽宽＝16.23mm），'
               '实测（门谱同源 ink_em 口径 10.5pt 档）：初版 strict 1旗＝题2(T2) D槽「D．①②③」'
               '估宽16.6mm＝四连排槽87%（>85% 预警）→降两连排（复跑 D槽16.7mm 占45%）后清零；'
               '终档＝题3/7(T3/T7) 四连排原档（最宽38.3/26.8pt 占71%/49%）、'
               '题1/2/4/5/6/9 两连排（最宽70.5/47.2/68.2/60.0/53.1/65.1pt 占66/45/64/57/50/61%）、'
               '题8/10(T8/T10 多选) 单列；禁缩字号/负kern/删标点凑宽（零违例）',
    '图债': '无（全件零图依赖，题面无「如图」占位，includegraphics 零处）',
    '清洗口径': '印面 ✓ 记号全剔（检验句文句保留，rg 实测 0 残留）；详解句号照录批B 原文「。」',
    '难度词口径': '照题面 \\tieside 第1字段：0.94→简单、0.85→中档、0.65→中档；'
                '全件仅题11(T11) 简单，余15键中档',
    '知识点口径': '知识点系预排：一＝两直线平行判定、二＝垂直判定、三＝交点与综合（照批A/B 课时切分）；'
                '导学件课时06 尚未落盘（件目录仅 sty），落盘后如异动按变更协议回核',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 4页；false 同 2页',
    },
    '门谱': ['门-守恒对号-课时06.py（全绿）', '门-值快照键型判模-课时06.py（全绿）',
            '门-回流-课时06.py（全绿）', '键账对平门.py 三源对平 PASS',
            'makebox槽宽门.py zero-fp/strict 双档 0旗（槽32）',
            'CJK 审计 rg \\\\w+\\p{Han} 零命中'],
    'gen': '门谱/gen台账-课时06.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时06.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时06.json → 片目录')
