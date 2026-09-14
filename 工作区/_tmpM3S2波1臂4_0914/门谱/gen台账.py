# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时14.json ＋ 件manifest.json（片目录）。
适配自母版门谱 gen台账.py（_tmpM3S2母版0914/门谱）：PIECE/BASE→课时14。
唯一写域：成卷/导学件/课时14-2.6.2双曲线性质/{值台账-课时14.json, 件manifest.json}。
冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时14-2.6.2双曲线性质'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '值台账底稿-课时14.json'), encoding='utf-8'))
FMANI = json.load(open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时14.manifest.json'),
                       encoding='utf-8'))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入）
RENDER = {
    '2章-练-课时14-15': '括线（est=26）；详解 DA·DB 印面作 \\overrightarrow 点积形（印面符号口径）',
    '2章-练-课时14-16': '括线（est=41，全片最高）；平方增根判定段承批D补足',
    '2章-拓-课时14-28': '括线（est=18）；验算 AP/AQ 点积印 \\overrightarrow 形；选项坐标 A(1,0)..D(4,0) 2-up',
    '2章-拓-课时14-29': '括线（est=28）；倍角有向正切按批D承入',
    '2章-拓-课时14-30': '括线（est=28）；值含 ∪(U+222A)/∞(U+221E) 文字模逐字照录，首编渲染零缺字，免 preamble 路由补钉',
    '2章-拓-课时14-33-6': '括线（est=17）；题面 QM·QN 印 \\overrightarrow 形（值行字节级照录不动）',
    '2章-拓-课时14-33-7': '括线（est=16）；值含下划线 k_AB·k_OM（文字模），\\catcode 行内局域切换照录渲染，源字节零漂',
    '2章-拓-课时14-33-11': '括线（est=23）；题面/详解 CN=3ND 印绝对值形 |CN|=3|ND|（印面符号口径，值行不动）',
    '2章-拓-课时14-33-13': '括线（est=16）',
    '2章-练-课时14-05': '括线（est=12）',
    '2章-拓-课时14-23': '灰底＋\\ansnote{点睛}（教材第二定义引题，详解直接法不引名目，批D §四口径承入）',
    '2章-拓-课时14-24': '括线（est=9）＋\\ansnote{点睛}（同上口径）',
    '2章-拓-课时14-27': '灰底＋\\ansnote{点睛}（同上口径）',
}
CLEAN = {
    '2章-拓-课时14-33-7': '(1) 弦长算式印面清洗为「根差平方」分步（数学等价，亲算复验一致）；验算句源件号「14-12」印面作「例24」；详解「且」前补逗号系断行微调（语义不变）',
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
        '渲染注记': RENDER.get(k, ('括线' if it['判模'] == '括线' else '灰底') + '；\\ansitem 单条；题面/详解逐字装配'),
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗'),
    })

ledger = {
    '件': '课时14-2.6.2双曲线性质（2.6.2）导学件（M3 成卷轮 S2 波1 臂4·母版照抄制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–71＝探究1—66＋课堂评价67—71；ansitem 首参＝印面号，例/变式标签同号连排',
    '印面号↔键': {it['键']: it['印面号'] for it in items},
    '多选门': '本片多选1道（拓14-12，印面40）≤4 合规，成卷未增；印面带 \\duoxuan\\hspace{0.6em} 标记',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径，判据 est>8 行（承重墙）；'
                  '本片括线 32 键（top：练16 est=41、拓29/30 est=28、练15 est=26），第32/33名间隔 9>8（33rd=导G2 est=8）；'
                  '渲染面硬计数：灰底大矩形39＝71−32，ansrule 长线66＝32块×2＋尾框2（门谱实测）；'
                  '迭代史：首轮 RULED=∅ 跑读数，32 键 est>8 一轮全数包装入列（1 轮，≤2 轮限内）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=71 18页；false 同 8页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            '键账对平门.py 三源 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗',
            'CJK 审计 rg \'\\\\[a-zA-Z]+\\p{Han}\' main.tex 零命中'],
    'gen': '门谱/gen台账.py 2026-09-14（臂4 适配版·课时14）',
}

piece_manifest = {
    '片': '课时14-2.6.2双曲线性质',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时14.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': {'批D-课时14-2.6.2双曲线性质.md': FMANI['源件sha256'],
                   '课时14-2.6.2双曲线性质.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时14-2.6.2双曲线性质.md')),
                   '课时14-2.6.2双曲线性质-答案侧.md': sha(os.path.join(M3ROOT, '成卷/题面库/课时14-2.6.2双曲线性质-答案侧.md'))},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时14.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时14.json ＋ 件manifest.json → 片目录')
