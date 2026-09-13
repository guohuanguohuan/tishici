# -*- coding: utf-8 -*-
"""gen台账.py — M3 S2 波1 补位臂3·课时15 值台账-课时15.json ＋ 件manifest.json 产账。
适配自臂4 门谱 gen台账.py：PIECE/BASE/FMANI→课时15；底稿取本目录（补位臂3 门-值快照键型判模.py
2026-09-14 改制后复跑落盘版）。唯一写域：成卷/导学件/课时15-2.7.1抛物线方程/{值台账-课时15.json,
件manifest.json}。冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时15-2.7.1抛物线方程'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open(os.path.join(HERE, '值台账底稿-课时15.json'), encoding='utf-8'))
FMANI = json.load(open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时15.manifest.json'),
                       encoding='utf-8'))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（est 自底稿 items）
RENDER = {
    '2章-拓-课时15-01': '括线（est=23）；值行公式原子密集，组内 \\parfillskip=0pt\\rightskip=0pt plus 1fil '
                    'ragged 排（承 sty 槽宏同款），值字节零改动；臂4 临终 \\emergencystretch 3em 违例 hack 已撤',
    '2章-拓-课时15-09': '括线（est=15）；灯柱支架题详解向量/坐标印面照录',
    '2章-导-课时15-G5': '灰底；验算 |MF|=5 印根式形（值行字节级照录）',
}
RULED_NOTE = '括线（est=见 items）；\\ansitem 单条；题面/详解逐字装配'

items = []
for it in BASE['items']:
    k = it['键']
    if k in RENDER:
        note = RENDER[k]
    elif it['判模'] == '括线':
        note = f"括线（est={it['估高行数']}）；\\ansitem 单条；题面/详解逐字装配"
    else:
        note = '灰底；\\ansitem 单条；题面/详解逐字装配'
    items.append({
        '键': k,
        '印面号': it['印面号'],
        '键型': it['键型'],
        '值tex': it['值tex'],
        '值源': it['值源'],
        '值快照': '逐字全等',
        '估高行数': it['估高行数'],
        '判模': it['判模'],
        '渲染注记': note,
        '清洗注记': '逐字照录，零清洗',
    })

ledger = {
    '件': '课时15-2.7.1抛物线方程（2.7.1）导学件（M3 成卷轮 S2 波1 补位臂3·母版照抄制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–36＝探究1—31＋课堂评价32—36；ansitem 首参＝印面号，例/变式标签同号连排',
    '印面号↔键': {it['键']: it['印面号'] for it in items},
    '多选门': '本片多选3道（拓15-03/04/06＝变式26/27/29，印面26/27/29）选项均≤4 合规；'
            '多选数系批D §五.4 拓展清单源构既成（中档多选×3），非装配增删；'
            '母版「全件多选恒≤2道」系课时01实践注记，本片超1道已登记上报',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径，判据 est>8 行（承重墙）；'
                  '本片括线 15 键（top：拓06 est=25、拓01 est=23、练15 est=20、练14 est=19、拓04 est=17），'
                  '第15/16名间隔1（15th=练01 est=9、16th=导G5 est=8）；'
                  '渲染面硬计数：灰底大矩形21＝36−15，ansrule 长线32＝15块×2＋尾框2（门谱实测）；'
                  '迭代史：RULED 载臂4 括线键-课时15.json 一轮全数包装（1 轮，≤2 轮限内）',
    '改制注记': '补位臂3 2026-09-14 两件：①选项行 8 条 4-up（0.25\\linewidth-0.5em）→2-up '
              '（0.5\\linewidth-1em，承课时14 家法），治槽宽门旗（改前 zero-fp 旗2／strict 旗10→改后双档 0旗）；'
              '②拓15-01 值行 ragged 排治 underfull×2（见渲染注记）。均题面装配层，答案字节零改动',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=36 10页；false 同 5页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿·末页尾框几何定位版）', '门-回流.py（全绿）',
            '键账对平门.py 三源 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗',
            'CJK 审计 rg \'\\\\[a-zA-Z]+\\p{Han}\' main.tex 零命中'],
    'gen': '门谱/gen台账.py 2026-09-14（补位臂3 适配版·课时15）',
}

piece_manifest = {
    '片': '课时15-2.7.1抛物线方程',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时15.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': {'批D-课时15-2.7.1抛物线方程.md': FMANI['源件sha256'],
                   '课时15-2.7.1抛物线方程.md': FMANI['题面侧sha256'],
                   '课时15-2.7.1抛物线方程-答案侧.md': FMANI['答案侧sha256']},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时15.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时15.json ＋ 件manifest.json → 片目录')
