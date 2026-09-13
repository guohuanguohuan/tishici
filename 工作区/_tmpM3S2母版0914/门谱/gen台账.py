# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时01.json ＋ 件manifest.json（片目录）。
唯一写域：成卷/导学件/课时01-坐标法/{值台账-课时01.json, 件manifest.json}。冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import subprocess
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时01-坐标法'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open('值台账底稿.json', encoding='utf-8'))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入）
RENDER = {
    '2章-练-课时01-E8': '灰底；值行「证明见详解．」；详解四式 \\par\\noindent 每式独立成段'
                       '（catcode 口径：控制词后带空格断开，防 CJK 吸并入 csname）',
    '2章-练-课时01-E1': '灰底；详解 ▱ 经 \\pxparallelogram→NSC 子块路由（nscblk NSC-w500）',
    '2章-拓-课时01-T1': '括线；⟺→$\\iff$、坐标下标数学形；详解悬挂 \\qpind',
    '2章-拓-课时01-T2': '括线；⟺→$\\iff$、x_C/x₁→x_C/x_1 数学下标；\\leqslant 照录',
    '2章-练-课时01-E14': '括线；过程型「证明见详解．」',
    '2章-练-课时01-E2': '括线；多选四项辨析详解（可跨栏断）',
    '2章-练-课时01-E3': '括线；多选四项辨析详解（可跨栏断）',
}
CLEAN = {
    '2章-练-课时01-E6': '批A 答案栏检验句（x＝3…✓；x＝−5…✓）已剔除，值仅「P的坐标为3或−5．」',
    '2章-练-课时01-E15': '详解句号照录批A 原文「。」（E16 同）',
    '2章-练-课时01-E16': '详解句号照录批A 原文「。」',
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
        '值快照': '逐字全等' if it['键型'] in ('值', '过程') else
                  f"锚制（首锚(1)见详解；末锚{'等号不成立' if k.endswith('T1') else '在该矩形外．'}）",
        '估高行数': it['估高行数'],
        '判模': it['判模'],
        '渲染注记': RENDER.get(k, ('括线' if it['判模'] == '括线' else '灰底') +
                               ('；\\ansitem 单条' if it['键型'] == '值' else '；过程型「证明见详解．」')),
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗'),
    })

ledger = {
    '件': '课时01-坐标法 导学件（M3 成卷轮 S2 母版·题后紧跟答案制·全波母版）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–23＝探究1—18＋课堂评价19—23；ansitem 首参＝印面号，例/变式标签同号连排',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径；top-5 括线'
                  '（T2:15,E2:14,E3:14,E14:13,T1:11），第5/6名间隔 1 行（6th=E11:10）；'
                  '渲染面硬计数：灰底大矩形18＝ansrule 长线12＝5块×2＋尾框2（门谱实测）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=23 6页；false 同 3页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            '键账对平门.py 三源六腿 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗'],
    'gen': '门谱/gen台账.py 2026-09-14',
}

piece_manifest = {
    '片': '课时01-坐标法',
    '件型': '导学件（题后紧跟答案制·全波母版）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时01.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': {'批A-课时01-坐标法.md': json.load(
                       open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时01.manifest.json'),
                            encoding='utf-8'))['源件sha256'],
                   '课时01-坐标法.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时01-坐标法.md')),
                   '课时01-坐标法-答案侧.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时01-坐标法-答案侧.md'))},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时01.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时01.json ＋ 件manifest.json → 片目录')
