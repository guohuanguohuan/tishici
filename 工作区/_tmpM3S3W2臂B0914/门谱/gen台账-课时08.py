# -*- coding: utf-8 -*-
r"""gen台账-课时08.py — 由值台账底稿＋件级指纹产 值台账-课时08.json（练习件版）。
唯一写域：成卷/练习件/课时08-直线与圆的位置关系/值台账-课时08.json。冻结 manifest 本体只读。
（照抄母版 gen台账.py 工艺：底稿 vals 系答案侧全集 21 键，滤练键序 T1~T16 后才入台账——
过滤步不可删，不过滤则对平门三源红（导 5 键浮账）。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时08-直线与圆的位置关系'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '底稿-课时08.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（21 键），件账只收练键序 T1~T16（拓区隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时08-T2': '括线；选项两连排（A槽22.7mm 超四连排 strict 预警）',
    '2章-练-课时08-T4': '括线；选项两连排（D槽27.8mm 超四连排 strict 预警）',
    '2章-练-课时08-T5': '括线；选项两连排（B槽24.0mm 超四连排 strict 预警）；'
                       '题面与选项块间空行分段（血泪清单§四.6 治 underfull，印面不变）',
    '2章-练-课时08-T11': '括线；题面空位 \\kongda{相切}（详解版印答、纯题版退定宽空线，两档等形）',
    '2章-练-课时08-T12': '括线；题面空位 \\kongda{[√2, +∞)}',
    '2章-练-课时08-T13': '括线；题面空位 \\kongda{(−∞, −5√2/4)∪(5√2/4, +∞)}',
    '2章-练-课时08-T14': '括线；题面空位 \\kongda{√3}',
    '2章-练-课时08-T15': '括线；三问 \\liubai[32mm]；详解逐小问 \\par\\noindent 独立成段；'
                        '题面空位行（求 a 的值）无印答',
    '2章-练-课时08-T16': '括线；两问 \\liubai[24mm]；详解逐小问 \\par\\noindent 独立成段',
}
CLEAN = {
    '2章-练-课时08-T15': '亲算行「2 = r ✓ 是切线」✓ 记号剔（检验句文句保留）；'
                        '题面侧【注】抽验销项行不入印面；值仅「(1) x=3 或 3x−4y−5=0；(2) a=0 或 a=4/3；'
                        '(3) a=−3/4」照答案侧逐字',
    '2章-练-课时08-T16': '题面侧【注】阿氏圆撞族行不入印面；源示意图去图（批B 台账同注：全部数学信息'
                        '在文字中，无信息损失）；值仅「(1) x²+y²=36；(2) 一定进入，航行时间 1 小时」照答案侧逐字',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋降档梯位
    '2章-练-课时08-T1': ('单选', '四连排', ''), '2章-练-课时08-T2': ('单选', '两连排', ''),
    '2章-练-课时08-T3': ('单选', '四连排', ''), '2章-练-课时08-T4': ('单选', '两连排', ''),
    '2章-练-课时08-T5': ('单选', '两连排', ''), '2章-练-课时08-T6': ('单选', '四连排', ''),
    '2章-练-课时08-T7': ('单选', '四连排', ''), '2章-练-课时08-T8': ('单选', '四连排', ''),
    '2章-练-课时08-T9': ('单选', '四连排', ''), '2章-练-课时08-T10': ('单选', '四连排', ''),
    '2章-练-课时08-T11': ('填空', '', ''), '2章-练-课时08-T12': ('填空', '', ''),
    '2章-练-课时08-T13': ('填空', '', ''), '2章-练-课时08-T14': ('填空', '', ''),
    '2章-练-课时08-T15': ('解答', '', '32mm'), '2章-练-课时08-T16': ('解答', '', '24mm'),
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
    '件': '课时08-直线与圆的位置关系 练习件（M3 成卷轮 S3 W2 臂B·照抄课时01 母版体例·题后紧跟答案制）',
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
               '实测（门谱同源 ink_em 口径 10.5pt 档）：题2(T2) A槽22.7mm>16.23→两连排；'
               '题4(T4) D槽27.8mm>16.23→两连排；题5(T5) B槽24.0mm>16.23→两连排；'
               '题1/3/6/7/8/9/10 最宽7.4~14.9mm≤16.23→四连排原档；禁缩字号/负kern/删标点凑宽（零违例）',
    '难度词派生标注': '题面侧头标第 4 字段系裸数值（批B 冻结口径），派生标注照同章导学件09 同族口径：'
                    '0.94/0.85→简单、0.65→中档（T2/T4/T9/T12/T15/T16＝中档，余简单）；'
                    '知识点 N 照导学件08 知识导学三分册：一＝直线与圆的位置关系、二＝圆的弦长问题、'
                    '三＝圆的切线方程；T16（阿氏圆应用·跨分册）预排归知识点一（导学件08 无独立分册，'
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
    '门谱': ['门-守恒对号-课时08.py（全绿）', '门-值快照键型判模-课时08.py（全绿）',
            '门-回流-课时08.py（全绿）', '键账对平门.py 三源对平 PASS',
            'makebox槽宽门.py zero-fp/strict 双档 0旗（槽40）',
            'CJK 审计 rg \\\\w+\\p{Han} 零命中'],
    'gen': '门谱/gen台账-课时08.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时08.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时08.json → 片目录')
