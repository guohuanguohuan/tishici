# -*- coding: utf-8 -*-
"""gen台账19.py — 由值台账底稿＋件级指纹产 值台账-课时19.json ＋ 件manifest.json（片目录）。
唯一写域：成卷/导学件/课时19-章末总结与复习/{值台账-课时19.json, 件manifest.json}。冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时19-章末总结与复习'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open(os.path.join(HERE, '值台账底稿-课时19.json'), encoding='utf-8'))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

RENDER = {
    '2章-练-课时19-03': '括线；A13 勘误依教材原文「距离和」判椭圆右半（定稿 §三.2，批E-台账 §五.7 留痕）',
    '2章-练-课时19-08': '括线；轮2亲算①-3 全推导详解（三问结构），∎ 改「证毕」文读',
    '2章-练-课时19-10': '括线；题面「如图」系冻结题面原文，本件无源图尺寸可回补，存照（残余风险登记）',
    '2章-练-课时19-13': '括线；Δ=240 照答案侧（亲算②-3 括注「Δ=60」系约简口径笔误，不采）',
    '2章-练-课时19-16': '括线；值行「x_A」下划线字符经 {\\catcode`\\_=12} 组内局部化照字印出（值字节零改动）；'
                     '题面「如图所示」系冻结题面原文，本件无源图尺寸可回补，存照（残余风险登记）',
    '2章-导-课时19-G3': '括线；源订正版题面（直线 x−y+3=0），源答案 e=√5 不受影响',
}
CLEAN = {
    '2章-练-课时19-03': '教材 A13 勘误依原文：前批速算「双曲线左支」之误已修正为椭圆右半（定稿 §三.2）',
    '2章-练-课时19-10': '题面「如图」冻结原文保留，无源图尺寸可回补，存照（残余风险登记）',
    '2章-练-课时19-13': '详解回验 Δ=240 照答案侧；亲算②-3 括注「Δ=60」为笔误，不影响「Δ>0」结论，不采',
    '2章-导-课时19-G3': '源题面直线「x−y+2=0」系笔误（P(1,4) 不满足，1−4+2=−1≠0），订正为 x−y+3=0（抽验报告-批EG5 §2.1 双路线盲验确认订正必要）；值不受影响',
    '2章-练-课时19-16': '题面「如图所示」冻结原文保留，无源图尺寸可回补，存照（残余风险登记）',
}

items = []
for it in BASE['items']:
    k = it['键']
    items.append({
        '键': k,
        '印面号': it['印面号'],
        '键型': it['键型'],
        '值tex': it['值tex'],
        '值源': it['值源'],
        '值快照': '逐字全等',
        '估高行数': it['估高行数'],
        '判模': it['判模'],
        '渲染注记': RENDER.get(k, ('括线' if it['判模'] == '括线' else '灰底') + '；\\ansitem 单条'),
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗'),
    })

ledger = {
    '件': '课时19-章末总结与复习 导学件（M3 成卷轮 S2 波1 补位臂4b·母版照抄制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–21＝基础回归（教材复习题A组）1—6＋压轴收尾（2.8压轴池）7—16＋课堂评价17—21；'
                  'ansitem 首参＝印面号，例/变式标签同号连排（例1/变式2/…/例16＋G1~G5＝17~21）',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径；估高>8 括线（13 键：'
                  '08:32,15:17,12:16,16:16,10:15,13:15,G3:13,03:13,G1:11,G5:11,09:10,G4:9,06:9），'
                  '灰底 8 键（04:8,02:6,11:7,G2:7,01:5,05:5,07:5,14:5）；'
                  '第13名(9)>第14名(8) 间隔1行；渲染面硬计数：灰底大矩形8＝ansrule 长线28＝13块×2＋尾框2（门谱实测）；'
                  '19 件适配注：章末件末页自然含 G4/G5 括线块与尾框同页（零强制跳页铁律下排布，末页线6＝括线4＋尾框2），'
                  '18 件「末页孤框恰2线」系其版面巧合，非母版体例要求（体例仅锁 \\tailfill 无参置尾＋两档恰1）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=21 7页；false 同 4页',
    },
    '门谱': ['门-守恒对号19.py（全绿）', '门-值快照键型判模19.py（全绿）', '门-回流19.py（全绿·含CJK审计零命中）',
            '键账对平门.py 三源六腿 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗（槽24；'
            '例7/例9/G1 三行宽选项照 18-G1 先例改 2×2 双盒 0.5\\linewidth）'],
    'gen': '门谱/gen台账19.py 2026-09-14',
}

piece_manifest = {
    '片': '课时19-章末总结与复习',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时19.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': {'批E-课时19-章末总结与复习.md': json.load(
                       open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时19.manifest.json'),
                            encoding='utf-8'))['源件sha256'],
                   '课时19-章末总结与复习.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时19-章末总结与复习.md')),
                   '课时19-章末总结与复习-答案侧.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时19-章末总结与复习-答案侧.md'))},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时19.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时19.json ＋ 件manifest.json → 片目录')
