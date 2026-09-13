# -*- coding: utf-8 -*-
"""gen台账18.py — 由值台账底稿＋件级指纹产 值台账-课时18.json ＋ 件manifest.json（片目录）。
唯一写域：成卷/导学件/课时18-2.8②压轴综合二/{值台账-课时18.json, 件manifest.json}。冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时18-2.8②压轴综合二'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open(os.path.join(HERE, '值台账底稿-课时18.json'), encoding='utf-8'))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

RENDER = {
    '2章-练-课时18-03': '括线；值行「S_max」下划线字符经 {\\catcode`\\_=12} 组内局部化照字印出（值字节零改动）',
    '2章-练-课时18-06': '括线；源详解 k₁k₂ 化简笔误（源 −k²−4k）经亲算复算订正为 −4k（结论不变，清洗留痕）',
    '2章-练-课时18-09': '括线；条件选择双路详解，唯一性回验（越界根舍）随文；⇒改「得/即」文读',
    '2章-导-课时18-G1': '括线；0914 撤换回冲版（3章件17-#19）自撰亲算详解，含 p=2 特例回验',
}
CLEAN = {
    '2章-练-课时18-06': '源详解 k₁k₂=(k²x₁x₂+k(x₁+x₂)+1)·k²=−4k，源稿末步误书「−k²−4k」，本轮复算订正（结论「随k变」不变）',
    '2章-练-课时18-14': '题面「如图」系冻结题面原文，本件无源图尺寸可回补，存照（残余风险登记）',
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
    '件': '课时18-2.8②压轴综合二 导学件（M3 成卷轮 S2 波1 补位臂4b·母版照抄制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–21＝探究1—16＋课堂评价17—21；ansitem 首参＝印面号，例/变式标签同号连排',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径；估高>8 括线（18 键：'
                  '16:33,09:31,04:23,14:23,G1:21,03:21,13:21,15:21,07:19,12:18,08:17,02:15,'
                  '06:15,11:15,05:14,10:13,01:12,G3:10），灰底 3 键（G5:8,G2:7,G4:5）；'
                  '第18名(10)>第19名(8) 间隔2行；渲染面硬计数：灰底大矩形3＝ansrule 长线38＝18块×2＋尾框2（门谱实测）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=21 9页；false 同 4页',
    },
    '门谱': ['门-守恒对号18.py（全绿）', '门-值快照键型判模18.py（全绿）', '门-回流18.py（全绿·含CJK审计零命中）',
            '键账对平门.py 三源六腿 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗（槽20）'],
    'gen': '门谱/gen台账18.py 2026-09-14',
}

piece_manifest = {
    '片': '课时18-2.8②压轴综合二',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时18.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': {'批E-课时18-2.8②压轴综合二.md': json.load(
                       open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时18.manifest.json'),
                            encoding='utf-8'))['源件sha256'],
                   '课时18-2.8②压轴综合二.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时18-2.8②压轴综合二.md')),
                   '课时18-2.8②压轴综合二-答案侧.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时18-2.8②压轴综合二-答案侧.md'))},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时18.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时18.json ＋ 件manifest.json → 片目录')
