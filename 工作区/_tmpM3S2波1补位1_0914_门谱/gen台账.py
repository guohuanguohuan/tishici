# -*- coding: utf-8 -*-
r"""gen台账.py — M3 S2 波1 臂1 衔接节：由值台账底稿＋件级指纹产
值台账-衔接节.json ＋ 件manifest.json（写域仅片目录两 json；冻结 manifest 本体只读）。
"""
import hashlib
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/衔接节'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(io.open(os.path.join(HERE, '值台账底稿-衔接节.json'), encoding='utf-8'))
FRZ = json.load(io.open(os.path.join(M3ROOT, '成卷/题面库/manifest/衔接节.manifest.json'),
                        encoding='utf-8'))


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


RULED = {'2章-练-衔接-1', '2章-练-衔接-6', '2章-练-衔接-7', '2章-练-衔接-8'}
# 逐键渲染/清洗注记（缺省见 DEF_*）
DEF_RENDER = '灰底；\\ansitem 单条＋\\ansnote{详解} 悬挂 \\qpind'
DEF_CLEAN = '逐字照录，零清洗'
RENDER = {
    '2章-练-衔接-8': '括线；详解三小问各 \\par\\noindent 独立成段（catcode 口径：控制词后带空格'
                     '断开，防 CJK 吸并入 csname）',
    '2章-练-衔接-1': '括线；四小问同块，跨栏可断',
    '2章-练-衔接-6': '括线；(1)(2) 两问同块，跨栏可断',
    '2章-练-衔接-7': '括线；块内容估高 9 行（>8 阈）',
    '2章-练-衔接-10': '灰底；值行含 2 枚 \\allowbreak 断行提示＋行包 \\rightskip 弹性伸缩',
    '2章-导-衔接-探5': '灰底；值行含斜率 k 的 $\\pm$ 双支',
    '2章-练-衔接-4': '灰底；值行含 $k=2/(c-1)$ 分式（ASCII 斜杠照答案侧形）',
}
CLEAN = {
    '2章-练-衔接-10': '版面加 \\allowbreak×2（TeX 吞随空、墨面零变化）；值快照按「剔 '
                      '\\\\allowbreak\\\\s* 后逐字全等」核；另包 '
                      '\\begingroup\\rightskip=0pt plus 1fil\\relax…\\endgroup 消该行 '
                      'Underfull \\hbox（纯符号串无 CJK 胶可伸）',
}

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
    '件': '衔接节 导学件（M3 成卷轮 S2 波1臂1·题后紧跟答案制·单源双档）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–27＝考点探究1—6（探1—探6）＋课堂评价7—11（G1—G5）＋课后练习12—27'
                 '（练-1—练-16）；ansitem 首参＝印面号，与 manifest 逻辑键序（G 前探后）'
                 '同集不同序，装配序登记于 门-守恒对号',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径；'
                   '承重墙＝估高 **>8 行** 才转括线（禁放宽），断言 括线集 ≡ {估高>8}：'
                   '括线4块（练-8:11,练-6:11,练-7:9,练-1:9）；顶格 8 行三键'
                   '（探5/探2/G2）按严格 >8 口径留灰底不转；渲染面硬计数：'
                   '灰底大矩形23＝27−4、ansrule 长线10＝4块×2＋尾框2、尾框线末页恰2（门谱实测）',
    '件侧版面偏差登记': [
        '①书写位 \\xiexwei 上调 7 处（练习19/20/21/23/24/27 12—14mm→18mm、练习22 10mm→16mm）：'
        'true 档原状末栏平衡溢 Overfull \\vbox 75.09pt（不可断灰底块横跨栏切点），'
        '扫描实证 Δ合计≥+37mm 归零；改后双档三零且 true 仍 6 页、false 仍 3 页；'
        '取值仍在母版/同侪件实测梯 7—18mm 内（母版上限 18mm），未越制。',
        '②2章-练-衔接-10 值行外包 \\begingroup\\rightskip=0pt plus 1fil\\relax…\\endgroup：'
        '该行系纯符号串（无 CJK 可伸胶），行尾必然短空致 Underfull \\hbox badness 10000；'
        '\\ansitem 的 \\par 在包内分组结束，故 \\rightskip 生效且不外溢，墨面零变化。',
        '③第7题（G1）选项由 0.25\\linewidth 四连排改 0.5\\linewidth 二连排×2 行：'
        '原四连排末槽「D．不能确定」估值 57.8pt＞槽宽 54.5pt（占槽 106%，叠印风险），'
        '改制后占槽 53%；形制与本件其余 4 选项题（例1/G2/G3/练-14/练-15）一致。',
        '④makebox 槽宽门：zero-fp 档 28 槽／旗 0（PASS）；strict 档余 2 旗'
        '（例1 选项 B/D「存在 m 有…交点」占槽 87%，超 85% 预警线 2.4pt 但＜槽宽、无叠印），'
        '登记为印前复核抽榜项，非红。',
    ],
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                    '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
             'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
             'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
             '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
             '双档读数': read_txt},
    '门谱': ['门-守恒对号.py（全绿：锚27≡块27≡manifest27；ANSKEY 两档各27同序；'
             '印面号1..27连号；false 泄答词0；尾块两档恰1；false3≤true6）',
             '门-值快照键型判模.py（全绿：值快照27/27（含1键\\allowbreak清洗制）；'
             '承重墙 括线集≡{估高>8}；渲染面灰底23/长线10/末页2；双档三零）',
             '门-回流.py（全绿：强制跳页原子×0；CJK审计0命中）',
             '键账对平门.py 三源六腿 PASS（底稿↔manifest键序↔行首锚↔编译锚，27↔27）',
             'makebox槽宽门.py zero-fp 28槽/旗0 PASS；strict 旗2（87%预警线，登记复核，见偏差④）'],
    'gen': '门谱-衔接节/gen台账.py 2026-09-14',
}

件manifest = {
    '片': '衔接节',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/衔接节.manifest.json（本体勿动）',
    '冻结manifest键序': FRZ['键序'],
    '源件sha256': {
        '批E-衔接节.md': sha(os.path.join(M3ROOT, '定稿/批E-衔接节.md')),
        '衔接节.md': sha(os.path.join(M3ROOT, '成卷/题面库/衔接节.md')),
        '衔接节-答案侧.md': sha(os.path.join(M3ROOT, '成卷/题面库/衔接节-答案侧.md')),
    },
    'toolchain锁': 台账['toolchain锁'],
    '件指纹': 台账['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

# 冻结 manifest 自证：三源件 sha 与外账逐一对合
for field, fn in (('源件sha256', '批E-衔接节.md'), ('题面侧sha256', '衔接节.md'),
                  ('答案侧sha256', '衔接节-答案侧.md')):
    assert 件manifest['源件sha256'][fn] == FRZ[field], f'{fn} sha 与冻结 manifest 不符'
json.dump(台账, io.open(os.path.join(PIECE, '值台账-衔接节.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(件manifest, io.open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('双档读数：', read_txt)
print('sty md5 ：', 台账['toolchain锁']['md5'])
print('→', os.path.join(PIECE, '值台账-衔接节.json'))
print('→', os.path.join(PIECE, '件manifest.json'))
