# -*- coding: utf-8 -*-
r"""gen台账-课时16.py — 由值台账底稿＋件级指纹产 值台账-课时16.json（练习件版）。
唯一写域：成卷/练习件/课时16-2.7.2抛物线性质/值台账-课时16.json。冻结 manifest 本体只读。
（照抄 W2臂B gen台账-课时08.py 工艺：底稿 vals 系答案侧全集 50 键，滤练键序 01~16 后才入台账——
过滤步不可删，不过滤则对平门三源红（导 5 键＋拓 29 键浮账）。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时16-2.7.2抛物线性质'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '底稿-课时16.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（50 键），件账只收练键序 01~16（拓区隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时16-01': '括线；多选四项单列 \\lxopt（导学件16 同款）',
    '2章-练-课时16-03': '括线；四小题 \\liubai[32mm]；题面小问裸行两行（照课时08 子题式，不用导学件宏 \\bindp）',
    '2章-练-课时16-10': '括线；四项单列 \\lxopt（初装两连排 C/D 槽 97.1pt＞strict 预警 90.2pt 降档）',
    '2章-练-课时16-13': '括线；详解 \\par\\noindent 独立成段（承导学件底稿）',
    '2章-练-课时16-15': '括线；两问 \\liubai[24mm]；题面小问裸行；详解逐小问 \\par\\noindent 独立成段',
    '2章-练-课时16-16': '括线；详解 \\par\\noindent 独立成段（承导学件底稿）',
}
CLEAN = {
    '2章-练-课时16-02': '印面详解剔校验句 \\ding 记号（「\\(|MF|=17/16\\) 记号」句文句保留）；值照答案侧逐字',
    '2章-练-课时16-05': '印面详解剔校验句 \\ding 记号（「校验：…=6」文句保留）；值照答案侧逐字',
    '2章-练-课时16-07': '印面详解剔回验句 \\ding 记号×2（「回验：…；…」文句保留）；值照答案侧逐字',
    '2章-练-课时16-16': '拓册引用「（到准线距离，焦半径公式见例 36）」→「（即到准线的距离）」改文句；'
                       '值照答案侧逐字',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋降档梯位
    '2章-练-课时16-01': ('多选', '单列', ''), '2章-练-课时16-02': ('解答', '', '16mm'),
    '2章-练-课时16-03': ('解答', '', '32mm'), '2章-练-课时16-04': ('解答', '', '16mm'),
    '2章-练-课时16-05': ('解答', '', '16mm'), '2章-练-课时16-06': ('解答', '', '16mm'),
    '2章-练-课时16-07': ('解答', '', '16mm'), '2章-练-课时16-08': ('解答', '', '16mm'),
    '2章-练-课时16-09': ('单选', '四连排', ''), '2章-练-课时16-10': ('单选', '单列', ''),
    '2章-练-课时16-11': ('单选', '四连排', ''), '2章-练-课时16-12': ('解答', '', '16mm'),
    '2章-练-课时16-13': ('解答', '', '16mm'), '2章-练-课时16-14': ('解答', '', '16mm'),
    '2章-练-课时16-15': ('解答', '', '24mm'), '2章-练-课时16-16': ('解答', '', '16mm'),
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
    '件': '课时16-2.7.2抛物线性质 练习件（M3 成卷轮 S3 W2 臂D·照抄课时01 母版体例·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序 01~16 零重排；\\tihao 号＝\\ansitem 号同键同号',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang＝19.10mm；strict 预警 16.23mm；'
               '两连排 37.28mm／strict 预警 31.8mm），实测（makebox槽宽门 门谱同源）：'
               '题1(16-01) 多选四项单列（导学件16 同款）；题10(16-10) 初装两连排，C/D 槽 97.1pt（34.3mm）'
               '＞strict 预警 90.2pt（31.8mm，占槽 92%）→ 依降档梯整题降单列复跑双档 0 旗；'
               '题9/11 四连排 8 槽 strict 零旗（原档）；禁缩字号/负kern/删标点凑宽（零违例）',
    '难度词派生标注': '本片 tieside 照同章导学件16 同题标签逐题承入（W2臂D 装配口径），'
                    '与题面侧头标难度档对应：简/0.85→简单（题1~10）、中→中档（题11~14）、'
                    '0.65 难槽补位对→难（题15/16，导学件16 变式15/16 同标）；'
                    '知识点 N 逐题：题1/3/4/7/8/10 知识点一、题2/5/6/12/13 知识点二、'
                    '题9/11/14/15/16 知识点三（零派生分歧）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 4页；false 同 2页',
    },
    '门谱': ['门-守恒对号-课时16.py（全绿）', '门-值快照键型判模-课时16.py（全绿）',
            '门-回流-课时16.py（全绿）', '键账对平门.py 三源对平 PASS',
            'makebox槽宽门.py zero-fp/strict 双档 0旗（槽8）',
            'CJK 审计 rg \\\\w+\\p{Han} 零命中'],
    'gen': '门谱/gen台账-课时16.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时16.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时16.json → 片目录')
