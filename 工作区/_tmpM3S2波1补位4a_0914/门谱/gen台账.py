# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时17.json ＋ 件manifest.json（片目录）。
唯一写域：成卷/导学件/课时17-2.8①压轴综合一/{值台账-课时17.json, 件manifest.json}。冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时17-2.8①压轴综合一'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '值台账底稿.json'),
                      encoding='utf-8'))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入）
RENDER = {
    '2章-练-课时17-11': '括线；值含字面 {}，tex 以 \\{ \\} 印制（值快照门归一化比对，门头注注册）',
    '2章-拓-课时17-04': '括线；值行「或」后加 \\hspace{0pt plus 1.5em} 弹性胶（断行校准，零字形；'
                        '门剔除归一注册）——长值 ansitem 首行 justify 拉伸整改配套',
    '2章-拓-课时17-16': '括线；长值 ansitem 首行 justify 拉伸曾致 [答案] 标签内胶裂距'
                        '（印面目验 0914 在案），经全域标签原子化整改后复验干净',
    '2章-拓-课时17-18': '括线；选项四槽拆双行（0.5\\linewidth 双盒制×2；题面文字零改）——'
                        '槽宽门 strict 档原 2 旗（槽1/4 估 99%、槽3/4 估 101%）迁修复，改后 strict 旗 0',
    '2章-拓-课时17-01': '括线；选项 A、B、C 照冻 manifest 指令印「〔图嵌，数值未回〕」'
                        '（\\lxopt 单列；定稿瑕疵⑤在案，下游补图项）',
    '2章-导-课时17-G4': '括线；填空留白 7mm→6mm（false 末栏平衡 3.3pt 超盒矫正，双档同源）',
    '2章-导-课时17-G5': '括线；填空留白 7mm→6mm（同上矫正配套）',
    '2章-拓-课时17-17': '括线；例17 解题留白 12mm→10.5mm（false 末栏平衡同源矫正）',
}
CLEAN = {
    '全域': '〔亲算印证…〕〔校订注…〕〔3章件N-#N 自带详解照录校订…〕等审计尾注一律剔除；'
            '【验算】格并入详解末尾「（验算：…）」括注；题面「（　）」→\\nobreak(\\kongwei)、'
            '填空空位→\\kongbai{}；详解内交叉引用改件内（例2/变式2/例4/例17/例19）；'
            '详解内 ∎ 消、✓→\\ding{51}；批D 导学 G5 补产五题（G1—G5）详解同口径清洗回嵌',
    '全域-符号路由': '✓→\\ding{51}、✗→\\ding{55}（pifont）；⇒→$\\Rightarrow$、⇔→$\\Leftrightarrow$、'
                  '⟺→$\\iff$、∈、∪、≤、≥、⊥→\\perp、∠→\\angle、△→\\triangle（数学命令制）；'
                  '−(U+2212)/–(U+2013) preamble \\xeCJKDeclareCharClass 路由；▱→NSC 子块 \\pxparallelogram',
    '全域-断行校准': 'CJKglue 拉伸 plus 0.30em（课时16 实证校准承入）；拓17-04 值行弹性胶一处'
                  '（见 RENDER 注记）',
    '全域-标签原子化': '\\renewcommand{\\anlabel}[1]{\\mbox{#1}}（preamble，sty 零改）：长值 ansitem '
                   '首行 justify 拉伸曾入 [答案] 标签内 CJK 胶致印面裂距（拓17-04/16，目验 0914）；'
                   '\\mbox 壳令标签定宽不参调，标签样式零改；[详解] 标签同壳一致',
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
        '值快照': '逐字全等（门归一化后）',
        '估高行数': it['估高行数'],
        '判模': it['判模'],
        '渲染注记': RENDER.get(k, (it['判模'] + '；\\ansitem 单条')),
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗'),
    })

ledger = {
    '件': '课时17-2.8①压轴综合一 导学件（M3 成卷轮 S2 波1 补位臂4a·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–42＝探究1—37＋课堂评价38—42；ansitem 首参＝印面号，例/变式标签同号连排；'
                '键↔号映射（装配序）：练 01→1,04→2,02→3,05→4,07→5,11→6,13→7,12→8,14→9,10→10,'
                '03→11,09→12,06→13,16→14,08→15,15→16；拓 03→17,17→18,18→19,19→20,01→21,05→22,'
                '07→23,12→24,13→25,08→26,11→27,04→28,06→29,09→30,10→31,14→32,15→33,16→34,'
                '20→35,21→36,02→37；导G1—G5→38—42',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令，值＋详解合并）/23 栏宽字口径，'
                  'est＝ceil＞8 → 括线；本片括线 39 键、灰底 3 键（练04,05,06），边界干净：'
                  '灰底 max est=8／括线 min est=9；渲染面硬计数：灰底大矩形3＝42−39、'
                  'ansrule 长线80＝39块×2＋尾框2（尾框以「笔记与错题整理」文本锚定其上下线；门谱实测）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本（钉后版 7c3930362be8a0a2bdf21bbf8ac16573），禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=42 14页；false 同 4页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            'audit17.py 静态审计（缺包0 多包0，括线39/灰底3）',
            '键账对平门.py 三源对平（结果见门谱读数件）',
            'makebox槽宽门.py zero-fp 旗0 PASS／strict 旗0 PASS'
            '（拓17-18 选项双盒改制后两档全过，无残旗）'],
    'gen': '门谱/gen台账.py 2026-09-14',
}

piece_manifest = {
    '片': '课时17-2.8①压轴综合一',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时17.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': json.load(open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时17.manifest.json'),
                             encoding='utf-8'))['源件sha256'],
    '件源sha256': {'课时17-2.8①压轴综合一.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时17-2.8①压轴综合一.md')),
                 '课时17-2.8①压轴综合一-答案侧.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时17-2.8①压轴综合一-答案侧.md'))},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时17.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时17.json ＋ 件manifest.json → 片目录')
