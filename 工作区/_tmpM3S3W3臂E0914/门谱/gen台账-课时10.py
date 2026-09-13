# -*- coding: utf-8 -*-
r"""gen台账-课时10.py — 由值台账底稿＋件级指纹产 值台账-课时10.json（练习件版）。
唯一写域：成卷/练习件/课时10-2.4曲线与方程/值台账-课时10.json。冻结 manifest 本体只读。
（照抄母版 gen台账.py 工艺：底稿 vals 系答案侧全集，滤练键序 简1~简10/中1~中4/难1~难2 后才入
台账——过滤步不可删，不过滤则对平门三源红（导 5 键浮账）。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时10-2.4曲线与方程'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '底稿-课时10.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（21 键），件账只收练键序 16 键（拓区隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时10-简7': '括线；选项单列 \\lxopt（逐行选项，无槽宽约束）',
    '2章-练-课时10-简8': '括线；选项两连排（B槽26.2mm＞四连排容差21.60mm，真算落位两连排）',
    '2章-练-课时10-简10': '括线；三小问 \\liubai[32mm]；详解逐小问 \\par\\noindent 独立成段',
    '2章-练-课时10-中1': '括线；两问 \\liubai[24mm]；详解逐小问 \\par\\noindent 独立成段',
    '2章-练-课时10-难1': '括线；选项单列 \\lxopt；图注「“8”字形双纽线示意，照录自源」文字照录'
                        '（源示意图去图：批B 台账同注口径，图债登记回执）',
    '2章-练-课时10-难2': '括线；题面空位 \\kongda{②④}（详解版印答、纯题版退定宽空线，两档等形）',
}
CLEAN = {
    '2章-练-课时10-中2': '定稿检验句「都满足斜率方程✓／都在轨迹上✓」✓ 记号剔（文句保留）；'
                        '推导箭头 → 宏化（\\Longrightarrow）；值仅「x²/4+y²=1（x≠±2）」照答案侧逐字',
    '2章-练-课时10-简9': '亲算行抛物线定义类比语挂 S4 装配观察（定稿§九9.1 注记随行，印面零清洗）',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋选项槽位
    '2章-练-课时10-简1': ('解答', '', '16mm'), '2章-练-课时10-简2': ('解答', '', '16mm'),
    '2章-练-课时10-简3': ('解答', '', '16mm'), '2章-练-课时10-简4': ('解答', '', '16mm'),
    '2章-练-课时10-简5': ('解答', '', '16mm'), '2章-练-课时10-简6': ('解答', '', '16mm'),
    '2章-练-课时10-简7': ('单选', '单列', ''), '2章-练-课时10-简8': ('单选', '两连排', ''),
    '2章-练-课时10-简9': ('解答', '', '16mm'), '2章-练-课时10-简10': ('解答', '', '32mm'),
    '2章-练-课时10-中1': ('解答', '', '24mm'), '2章-练-课时10-中2': ('解答', '', '16mm'),
    '2章-练-课时10-中3': ('解答', '', '16mm'), '2章-练-课时10-中4': ('解答', '', '16mm'),
    '2章-练-课时10-难1': ('多结论选择', '单列', ''), '2章-练-课时10-难2': ('填空', '', ''),
}

items = []
for it in BASE['items']:
    k = it['键']
    slot, opt, liubai = SLOT[k]
    items.append({
        '键': k,
        '印面号': it['印面号'],
        '键型': it['键型'],
        '槽型': slot,
        '选项槽位': opt or ('四连排' if slot in ('单选', '多选') else '—'),
        '书写区高': liubai or '—',
        '值tex': it['值tex'],
        '值源': it['值源'],
        '值快照': it['值快照'],
        '估高行数': it['估高行数'],
        '判模': it['判模'],
        '渲染注记': RENDER.get(k, '括线；\\ansitem 单条'),
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗'),
    })

ledger = {
    '件': '课时10-2.4曲线与方程 练习件（M3 成卷轮 S3 W3 臂E·照抄课时01 母版体例·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序 简1~简10/中1~中4/难1~难2 零重排；\\tihao 号＝\\ansitem 号同键同号',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang＝19.10mm；四连排容差 21.60mm，'
               'strict 预警 0.85×槽宽＝16.23mm；两连排槽宽 37.28mm、预警 31.69mm），'
               '实测（降档读数.py ink_em 口径）：题8(简8) B槽26.2mm＞21.60→两连排（≤31.69 原档落位）；'
               '题7(简7)/题15(难1) 题面侧实录单列 \\lxopt 逐行选项，无槽宽约束；'
               '禁缩字号/负kern/删标点凑宽（零违例）',
    '入槽登记': '批C 置换轨②：简8~简10 三席＝命制 10-命1回修/命2/命3回修 入槽，'
               '挤出原中5~中7 三席移拓展册（→10-拓13/拓14/拓15，域内保留）；'
               '原拓1（-2 项）同题双列撤位、拓2 相应销项——授权链＝主裁（规格书背书）＋报备用户'
               '（军师账审§八），定稿§6/§9.5 登记随行',
    '难度词派生标注': '题面侧头标难度照录派生：简→简单、0.65（中）→中档（批C 派生同批B 口径）、难→难；'
                    '知识点 N 照导学件10 知识导学三分册：一＝曲线的方程与方程的曲线、'
                    '二＝求轨迹方程·直接法、三＝由方程研究曲线（印面 \\tieside 逐题实录见 main.tex）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5（7c3930362be8a0a2bdf21bbf8ac16573）；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 4页；false 同 2页',
    },
    '门谱': ['门-守恒对号-课时10.py（全绿）', '门-值快照键型判模-课时10.py（全绿）',
            '门-回流-课时10.py（全绿）', '键账对平门.py 三源对平 PASS',
            'makebox槽宽门.py zero-fp/strict 双档 0旗',
            'CJK 审计 rg \\[a-zA-Z]+\\p{Han} 零命中'],
    'gen': '门谱/gen台账-课时10.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时10.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时10.json → 片目录')
