# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时16.json ＋ 件manifest.json（片目录）。
唯一写域：成卷/导学件/课时16-2.7.2抛物线性质/{值台账-课时16.json, 件manifest.json}。冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时16-2.7.2抛物线性质'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open('值台账底稿.json', encoding='utf-8'))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入）
RENDER = {
    '2章-练-课时16-15': '括线；详解末段「＝−3/√41」后以「分母有理化得」拆式（断行校准，数学恒等）',
    '2章-拓-课时16-05': '括线；详解 |CN| 链改平方形（|CN|²=…≥24，即 |CN|≥2√6；断行校准，数学恒等）',
    '2章-拓-课时16-13': '括线；选项按定稿瑕疵⑤改排 A．−8　B．−4　C．4　D．12（答案 C 钉 4）',
    '2章-拓-课时16-10': '括线；题面「如图」无图，文字自足（定稿在案，残余风险登记）',
    '2章-拓-课时16-12': '括线；选项四槽拆双行（0.5\\linewidth 双盒制×2，槽宽门 zero-fp 红迁修复）',
}
CLEAN = {
    '全域': '〔亲算印证…〕〔校订注…〕〔卷③自带详解照录校订〕等审计尾注一律剔除；'
            '【验算】格并入详解末尾「（验算：…）」括注；题面「（　）」→\\nobreak(\\kongwei)、'
            '填空空位→\\kongbai{}',
    '全域-符号路由': '✓→\\ding{51}、✗→\\ding{55}（pifont）；⇒→$\\Rightarrow$、⇔→$\\Leftrightarrow$、'
                  '⟺→$\\iff$、∀→$\\forall$、∓→$\\mp$；−(U+2212)/–(U+2013) preamble '
                  '\\xeCJKDeclareCharClass 路由；▱→NSC 子块 \\pxparallelogram',
    '全域-断行校准': 'CJKglue 拉伸 plus 0.08→0.30em（探针 probe6—8 实证：窄栏详解长公式链行亏'
                  ' 0.08em 吸不住→badness 10000 必报 underfull；0.30em 后全数吸收；'
                  '\\emergencystretch 与降 rel/binop 罚两路均无效已证伪）',
    '全域-选项拆行': '拓16-12／课堂评价 G2 选项行拆双行（0.5\\linewidth 双盒制；题面文字零改）',
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
        '渲染注记': RENDER.get(k, (it['判模'] + '；\\ansitem 单条')),
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗'),
    })

ledger = {
    '件': '课时16-2.7.2抛物线性质 导学件（M3 成卷轮 S2 波1 臂5·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–50＝探究1—45＋课堂评价46—50；ansitem 首参＝印面号，例/变式标签同号连排；'
                '让位席拓16-18 无键留块（键集豁免登记在案，拓键实幅 01~30 且 18 不占键）',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径，est＝ceil＞8 → 括线；'
                  '本片括线 29 键（练03,12,14,15,16＋拓02,04,05,06,07,08,10,11,12,13,14,15,17,'
                  '23,24,25,26,27,28,29,30＋导G3,G4,G5），边界干净：灰底 max est=8／括线 min est=9；'
                  '渲染面硬计数：灰底大矩形21＝50−29、ansrule 长线60＝29块×2＋尾框2'
                  '（尾框以「笔记与错题整理」文本锚定其上下线；门谱实测）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本（钉后版 7c3930362be8a0a2bdf21bbf8ac16573），禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=50 12页；false 同 5页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            '键账对平门.py 三源六腿 PASS', 'makebox槽宽门.py zero-fp 0旗 PASS／strict 严报 2 旗'
            '（练16-08 C/D 或式选项行：估权 89% 系保守估计，实际墨宽≈74pt/109pt=68%，'
            '题面原文禁改、0.5 槽已极窄形，登记不判死）'],
    'gen': '门谱/gen台账.py 2026-09-14',
}

piece_manifest = {
    '片': '课时16-2.7.2抛物线性质',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时16.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': json.load(open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时16.manifest.json'),
                             encoding='utf-8'))['源件sha256'],
    '件源sha256': {'课时16-2.7.2抛物线性质.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时16-2.7.2抛物线性质.md')),
                 '课时16-2.7.2抛物线性质-答案侧.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时16-2.7.2抛物线性质-答案侧.md'))},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时16.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时16.json ＋ 件manifest.json → 片目录')
