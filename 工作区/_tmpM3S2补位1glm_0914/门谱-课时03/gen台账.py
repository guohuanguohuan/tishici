# -*- coding: utf-8 -*-
r"""gen台账.py — M3 S2 波1 补位1glm 课时03：由值台账底稿＋件级指纹产
值台账-课时03.json ＋ 件manifest.json（写域仅片目录两 json；冻结 manifest 本体只读）。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时03-方向向量与法向量'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(io.open(os.path.join(HERE, '值台账底稿-课时03.json'), encoding='utf-8'))
FRZ = json.load(io.open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时03.manifest.json'),
                        encoding='utf-8'))


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


RULED = {'2章-练-课时03-E2', '2章-练-课时03-E6',
         '2章-练-课时03-E7', '2章-练-课时03-E8'}
DEF_RENDER = '灰底；\\ansitem 单条＋\\ansnote{详解} 悬挂 \\qpind'
DEF_CLEAN = '逐字照录，零清洗'
RENDER = {
    '2章-练-课时03-E8': '括线；块估高 11 行（>8 阈），两支互反证明同块，跨栏可断',
    '2章-练-课时03-E2': '括线；块估高 10 行；(1)(2) 两问 \\par\\noindent 分段，跨栏可断',
    '2章-练-课时03-E6': '括线；块估高 10 行；(1)(2) 两问含一般式讨论，跨栏可断',
    '2章-练-课时03-E7': '括线；块估高 10 行；(1)(2) 两问含点法式一般形，跨栏可断',
    '2章-练-课时03-E14': '灰底；值行含下标 ₀₁（探针实证本件字库直排零缺字）',
    '2章-导-课时03-G1': '灰底；详解含 ±(3/5,4/5) 双支与 C 选项四组合辨析',
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
    '件': '课时03-方向向量与法向量 导学件（M3 成卷轮 S2 波1·题后紧跟答案制·单源双档）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1—16＝考点探究（探究点一 E3,E1,E2,E4,E5,E12,E15→1—7；探究点二 '
                 'E8,E11,E14,E13→8—11；探究点三 E6,E7,E9,E10,E16→12—16）＋'
                 '17—21＝课堂检测 G1—G5；ansitem 首参＝印面号，与 manifest 逻辑键序'
                 '（G 前练后）同集不同序，装配序登记于 门-守恒对号；'
                 '本课时拓展槽空置（批A§三 在案，不硬凑），无拓键',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径；'
                   '承重墙＝估高 **>8 行** 才转括线（禁放宽），断言 括线集 ≡ {估高>8}：'
                   '括线4块（E8:11,E2:10,E6:10,E7:10）；顶格 8 行两键（E5/E11）按严格 >8 '
                   '口径留灰底不转；渲染面硬计数：灰底大矩形17＝21−4、ansrule 长线10＝'
                   '4块×2＋尾框2、尾框线末页恰2（门谱实测）',
    '件侧版面偏差登记': [
        '①首装即三零：true 5 页/false 2 页，双档两遍编译 0错0溢0under0缺字，'
        '无书写位调高、无选项改制（槽宽门双模 槽16/旗0）。',
        '②记号字体探针（过程件 探针-课时03字形）：₀₁θ∈∞√⊥≠−＋ 本件字库直排零缺字，'
        '值行 Unicode 逐字可排版；唯 ⟺(U+27FA) 缺字 → 详解（E14/G2）以 \\iff 换算，'
        '值行无此字符零波及。',
        '③详解换算登记：批A 纯文本数学式（AB→/√/²/±/·/×/⊥/₀ 等）→ \\(\\overrightarrow{AB}\\)'
        ' 等 LaTeX 形；provenance 括注（【亲算落账】格）剔除，教学性括注（辨析/验证/另解）'
        '保留并压缩为（辨析：…）（验证：…）形（E12/E13/E15/E16/G1 等）。',
        '④预习位（知识点填空＋判断正误4条）系件侧自教材 §2.2.1 下半节组织，零键零答案'
        '（口令④前口径），与母版/课时02 同制。',
    ],
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                    '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
             'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
             'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
             '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
             '双档读数': read_txt},
    '门谱': ['门-守恒对号.py（全绿：锚21≡块21≡manifest21；ANSKEY 两档各21同序；'
             '印面号1..21连号；false 泄答词0；尾块两档恰1；false2≤true5）',
             '门-值快照键型判模.py（全绿：值快照21/21 逐字全等（0清洗0过程）；'
             '承重墙 括线集≡{估高>8}；渲染面灰底17/长线10/末页2；双档三零）',
             '门-回流.py（全绿：强制跳页原子×0；CJK审计0命中）',
             '键账对平门.py 三源六腿 PASS（底稿↔manifest键序↔行首锚↔编译锚，21↔21）',
             'makebox槽宽门.py zero-fp 16槽/旗0 PASS；strict 16槽/旗0 PASS'],
    'gen': '门谱-课时03/gen台账.py 2026-09-14（补位1glm 首装）',
}

件manifest = {
    '片': '课时03-方向向量与法向量',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时03.manifest.json（本体勿动）',
    '冻结manifest键序': FRZ['键序'],
    '源件sha256': {
        '批A-课时03-方向向量与法向量.md': sha(os.path.join(
            M3ROOT, '定稿/批A-课时03-方向向量与法向量.md')),
        '课时03-方向向量与法向量.md': sha(os.path.join(
            M3ROOT, '成卷/题面库/课时03-方向向量与法向量.md')),
        '课时03-方向向量与法向量-答案侧.md': sha(os.path.join(
            M3ROOT, '成卷/题面库/课时03-方向向量与法向量-答案侧.md')),
    },
    'toolchain锁': 台账['toolchain锁'],
    '件指纹': 台账['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

for field, fn in (('源件sha256', '批A-课时03-方向向量与法向量.md'),):
    assert 件manifest['源件sha256'][fn] == FRZ[field], f'{fn} sha 与冻结 manifest 不符'
json.dump(台账, io.open(os.path.join(PIECE, '值台账-课时03.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(件manifest, io.open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('双档读数：', read_txt)
print('sty md5 ：', 台账['toolchain锁']['md5'])
print('→', os.path.join(PIECE, '值台账-课时03.json'))
print('→', os.path.join(PIECE, '件manifest.json'))
