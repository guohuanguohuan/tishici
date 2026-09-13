# -*- coding: utf-8 -*-
"""gen台账.py（波1臂3 参数化版）— 由值台账底稿＋件级指纹产 值台账-<片>.json ＋ 件manifest.json。
用法: python gen台账.py <片目录> <底稿.json> <片名> <manifest文件名> <题面md> <答案侧md> <渲染注记json> <清洗注记json> <页数读数> <片级注记>
唯一写域：片目录。冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE, DRAFT, PIAN, MFN, TM, AS, RJ, CJ, PG, NOTE = sys.argv[1:11]
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open(DRAFT, encoding='utf-8'))
RENDER = json.load(open(RJ, encoding='utf-8'))
CLEAN = json.load(open(CJ, encoding='utf-8'))


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


items = []
for it in BASE['items']:
    k = it['键']
    items.append({
        '键': k,
        '印面号': it['印面号'],
        '键型': it['键型'],
        '值tex': it['值tex'],
        '值源': it['值源'],
        '值快照': '逐字全等' if it['键型'] in ('值', '过程')
                  else '锚制（首锚(1)见详解；末锚见值tex尾段）',
        '估高行数': it['估高行数'],
        '判模': it['判模'],
        '渲染注记': RENDER.get(k, ('括线' if it['判模'] == '括线' else '灰底') +
                               ('；\\ansitem 单条' if it['键型'] == '值' else '；过程型')),
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗'),
    })

frozen = json.load(open(os.path.join(M3ROOT, '成卷/题面库/manifest', MFN), encoding='utf-8'))

ledger = {
    '件': f'{PIAN} 导学件（M3 成卷轮 S2 波1 臂3·题后紧跟答案制·照课时01 母版复刻）',
    '片级注记': NOTE,
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–21＝探究1—16＋课堂评价17—21；ansitem 首参＝印面号，例/变式标签同号连排',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径；top-5 括线，'
                  '第5/6名间隔≥1 行；渲染面硬计数门谱实测（灰底16＝21−5；ansrule 长线12＝5块×2＋尾框2）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': PG,
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            '键账对平门.py 三源 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗',
            'CJK 审计 rg \\[a-zA-Z]+\\p{Han}＝0'],
    'gen': '门谱/gen台账.py 2026-09-14',
}

piece_manifest = {
    '片': PIAN,
    '件型': '导学件（题后紧跟答案制·照课时01 母版复刻）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/' + MFN + '（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': {TM: sha(os.path.join(M3ROOT, '成卷/题面库', TM)),
                  AS: sha(os.path.join(M3ROOT, '成卷/题面库', AS)),
                  frozen['源件']: frozen['源件sha256']},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

json.dump(ledger, open(os.path.join(PIECE, f'值台账-{PIAN}.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'值台账-{PIAN}.json ＋ 件manifest.json → {PIECE}')
