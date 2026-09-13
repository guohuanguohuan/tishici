# -*- coding: utf-8 -*-
r"""gen台账.py — M3 S2 波1 补位1glm 课时02：由值台账底稿＋件级指纹产
值台账-课时02.json ＋ 件manifest.json（写域仅片目录两 json；冻结 manifest 本体只读）。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时02-倾斜角与斜率'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(io.open(os.path.join(HERE, '值台账底稿-课时02.json'), encoding='utf-8'))
FRZ = json.load(io.open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时02.manifest.json'),
                        encoding='utf-8'))


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


RULED = {'2章-拓-课时02-T1', '2章-拓-课时02-T2', '2章-拓-课时02-T4'}
DEF_RENDER = '灰底；\\ansitem 单条＋\\ansnote{详解} 悬挂 \\qpind'
DEF_CLEAN = '逐字照录，零清洗'
RENDER = {
    '2章-拓-课时02-T2': '括线；键型＝过程(换算)：值含数学下标（k_AB 之 _），text 模式不可逐字'
                        '排版，tex 侧取 LaTeX 换算形，快照按「首锚 (1) \\(k ＋末锚 ．＋'
                        '长度带 0.8–2.0×（实测 1.26x）」核（母版体例说明 坑7 定式）',
    '2章-拓-课时02-T1': '括线；值行含 θ∈/＋∞/−∞/π 等记号，CJK 字库直排逐字全等',
    '2章-拓-课时02-T4': '括线；块估高 10 行（>8 阈），跨 4/5 页可断',
    '2章-练-课时02-E5': '灰底；选项组为本卷补写（题面库【注】在案），C/D 两槽拆全宽行'
                        '（原半宽槽 C 估宽 116.2pt＞槽 109pt 占 107%，叠印险）',
}
CLEAN = {}

items = []
for it in BASE['items']:
    k = it['键']
    row = {'键': k, '印面号': it['印面号'], '键型': it['键型'], '值tex': it['值tex'],
           '值源': it['值源'], '值快照': it['值快照'], '估高行数': it['估高行数'],
           '判模': it['判模'],
           '渲染注记': RENDER.get(k, ('括线；跨栏可断' if k in RULED else DEF_RENDER)),
           '清洗注记': CLEAN.get(k, DEF_CLEAN)}
    items.append(row)

rd = BASE['双档读数']
read_txt = (f"true 错{rd['true']['err']}溢{rd['true']['over']}under{rd['true']['under']}"
            f"缺字{rd['true']['miss']} ANSKEY={rd['true']['ans']} {rd['true']['pages']}页；"
            f"false 错{rd['false']['err']}溢{rd['false']['over']}under{rd['false']['under']}"
            f"缺字{rd['false']['miss']} ANSKEY={rd['false']['ans']} {rd['false']['pages']}页")

台账 = {
    '件': '课时02-倾斜角与斜率 导学件（M3 成卷轮 S2 波1·题后紧跟答案制·单源双档）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–25＝课时练习 E1—E16（1—16）＋拓展变式 T1—T4（17—20）＋课堂评价 '
                 'G1—G5（21—25）；ansitem 首参＝印面号，与 manifest 逻辑键序（G 前练中拓后）'
                 '同集不同序，装配序登记于 门-守恒对号',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径；'
                   '承重墙＝估高 **>8 行** 才转括线（禁放宽），断言 括线集 ≡ {估高>8}：'
                   '括线3块（T2:12,T4:10,T1:9）；顶格 8 行两键（G3/E15）按严格 >8 口径留灰底'
                   '不转；渲染面硬计数：灰底大矩形22＝25−3、ansrule 长线8＝3块×2＋尾框2、'
                   '尾框线末页上下恰夹尾块文本2条（T4 括线块跨 4/5 页，其跨页 hairline'
                   '另计不混入尾框判定，门谱实测）',
    '件侧版面偏差登记': [
        '①拓展变式20（T4）题后书写位 \\xiexwei 16mm→10mm：原状 true 档末页左栏平衡溢 '
        'Overfull \\vbox 9.08pt（不可断灰底块横跨栏切点），扫描实证减 6mm（≈17pt）归零；'
        '改后双档三零且 true 仍 5 页、false 仍 3 页；取值仍在同侪件书写位梯内，未越制。',
        '②T1/T2 值行键型登记：T1＝值型逐字全等（θ∈[0,π/2) 等记号 CJK 字库直排零缺字）；'
        'T2＝过程(换算)型（k_AB 下标线 _ 入 text 模式即炸数学移位串烧全行——实测 22 缺字＋'
        '76.3pt 溢出，故照母版坑7 定式取 LaTeX 换算形，锚＋长度带核）。',
        '③变式13（E5）选项行改制：C/D 由 0.5\\linewidth 半宽槽二连排改全宽单列二行'
        '（C 估宽 116.2pt＞槽 109pt 占 107%，makebox 不裁剪真叠印险）；题面文本零改动，'
        '与 衔接节 偏差③ 同型；改后 zero-fp 档 槽38/旗0。',
        '④makebox 槽宽门：zero-fp 档 38 槽／旗 0（PASS）；strict 档余 6 旗'
        '（A/B 等占槽 87%，超 85% 预警线 ≤2.4pt 但＜槽宽、无叠印，估值器口径），'
        '登记为印前复核抽榜项，非红（衔接节同口径先例在案）。',
    ],
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                    '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
             'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
             'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
             '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
             '双档读数': read_txt},
    '门谱': ['门-守恒对号.py（全绿：锚25≡块25≡manifest25；ANSKEY 两档各25同序；'
             '印面号1..25连号；false 泄答词0；尾块两档恰1；false3≤true5）',
             '门-值快照键型判模.py（全绿：值快照 24 逐字＋1 过程型锚带（T2）；'
             '承重墙 括线集≡{估高>8}；渲染面灰底22/长线8/尾框2；双档三零）',
             '门-回流.py（全绿：强制跳页原子×0；CJK审计0命中）',
             '键账对平门.py 三源六腿 PASS（底稿↔manifest键序↔行首锚↔编译锚，25↔25）',
             'makebox槽宽门.py zero-fp 38槽/旗0 PASS；strict 旗6（87%预警线，登记复核，见偏差④）'],
    'gen': '门谱-课时02/gen台账.py 2026-09-14（补位1glm 接盘续作）',
}

件manifest = {
    '片': '课时02-倾斜角与斜率',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时02.manifest.json（本体勿动）',
    '冻结manifest键序': FRZ['键序'],
    '源件sha256': {
        '批A-课时02-倾斜角与斜率.md': sha(os.path.join(
            M3ROOT, '定稿/批A-课时02-倾斜角与斜率.md')),
        '课时02-倾斜角与斜率.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时02-倾斜角与斜率.md')),
        '课时02-倾斜角与斜率-答案侧.md': sha(os.path.join(
            M3ROOT, '成卷/题面库/课时02-倾斜角与斜率-答案侧.md')),
    },
    'toolchain锁': 台账['toolchain锁'],
    '件指纹': 台账['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

for field, fn in (('源件sha256', '批A-课时02-倾斜角与斜率.md'),):
    assert 件manifest['源件sha256'][fn] == FRZ[field], f'{fn} sha 与冻结 manifest 不符'
json.dump(台账, io.open(os.path.join(PIECE, '值台账-课时02.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(件manifest, io.open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('双档读数：', read_txt)
print('sty md5 ：', 台账['toolchain锁']['md5'])
print('→', os.path.join(PIECE, '值台账-课时02.json'))
print('→', os.path.join(PIECE, '件manifest.json'))
