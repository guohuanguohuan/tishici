# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时06B-2.2.4点到直线距离.json（练习件版）。
照抄 母版门谱 gen台账 同构，换 PIECE/SLOT/RENDER/CLEAN/降档登记；唯一写域：片目录值台账 json。
冻结 manifest 本体只读。（S3 练习件产出清单＝main.tex＋双壳＋值台账 json，不产 件manifest.json。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时06B-2.2.4点到直线距离'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '值台账底稿.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（21 键），件账只收练键序 T1~T16（拓区隔离；照抄勿删）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时06B-T10': '括线；\\duoxuan 多选标题号行后附；答案多字母 AB 照答案侧规范化值照录（禁件内重排）',
    '2章-练-课时06B-T11': '括线；题面空位 \\kongda{2x+3y−8=0 或 6x+9y−10=0}（详解版印答、纯题版退定宽空线，'
                          '两档等形；空位值＝答案侧「值：」行同串，印答与 ansitem 同源零漂）',
    '2章-练-课时06B-T12': '括线；题面空位 \\kongda{4/25}（两档等形开关宏）',
    '2章-练-课时06B-T13': '括线；题面空位 \\kongda{2+√2}（两档等形开关宏）',
    '2章-练-课时06B-T14': '括线；题面空位 \\kongda{1}（两档等形开关宏）',
    '2章-练-课时06B-T15': '括线；两问 \\liubai[24mm]{解答书写区}（两问档）',
    '2章-练-课时06B-T16': '括线；单问 \\liubai[16mm]{解答书写区}（默认档）；详解四段 \\par\\noindent 独立成段'
                          '（catcode 口径：控制词后带空格断开，防 CJK 吸并入 csname）',
}
CLEAN = {
    '2章-练-课时06B-T1': '题面/详解句号「。」→「．」印面化；数学线性化（\\sqrt、分数斜线）',
    '2章-练-课时06B-T7': '详解「⇔」→\\(\\Leftrightarrow\\)；①圈号照录（CJK 字符）',
    '2章-练-课时06B-T10': '详解「⇔」→\\(\\Leftrightarrow\\)',
    '2章-练-课时06B-T15': '值行「（1）3√5/5；（2）C(−13/5, 31/5)。」答案侧字节级照录（值尾「。」保留）；'
                          '详解句号印面化「．」',
    '2章-练-课时06B-T16': '值行「能，P(1/9, 37/18)。」答案侧字节级照录（值尾「。」保留）；'
                          '详解句号印面化「．」；终检句两处 ✓ 记号剔除（亲算注记不印，检验句文句保留）；'
                          '「½」→(1/2) 线性化',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋选项槽位＋书写区
    '2章-练-课时06B-T1': ('单选', '两连排', ''), '2章-练-课时06B-T2': ('单选', '四连排', ''),
    '2章-练-课时06B-T3': ('单选', '四连排', ''), '2章-练-课时06B-T4': ('单选', '四连排', ''),
    '2章-练-课时06B-T5': ('单选', '两连排', ''), '2章-练-课时06B-T6': ('单选', '两连排', ''),
    '2章-练-课时06B-T7': ('单选', '四连排', ''), '2章-练-课时06B-T8': ('单选', '两连排', ''),
    '2章-练-课时06B-T9': ('单选', '四连排', ''), '2章-练-课时06B-T10': ('多选', '四连排', ''),
    '2章-练-课时06B-T11': ('填空', '', ''), '2章-练-课时06B-T12': ('填空', '', ''),
    '2章-练-课时06B-T13': ('填空', '', ''), '2章-练-课时06B-T14': ('填空', '', ''),
    '2章-练-课时06B-T15': ('解答', '', '24mm'), '2章-练-课时06B-T16': ('解答', '', '16mm'),
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
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗（题面/详解通例：句号印面化、数学线性化）'),
    })

ledger = {
    '件': '课时06B-2.2.4点到直线距离 练习件（M3 成卷轮 S3 W1臂C·母版照抄件·选学补位课时）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '选学注记': '本件系选学补位课时（人教B版§2.2.4），序位于课时06（§2.2.3）与课时07（§2.3.1）之间'
              '（canonical 键名总表显式登记，字符串序 06<06B<07 免特判）；印面 \\keshi 标「（选学）」'
              '＋件首 \\zhuzhu 选学注记一行（批B-课时06 T13/T16 前引注同口径，导学件 06B 承接）',
    '印面连号制': '1–16＝manifest 练键序 T1~T16 零重排；\\tihao 号＝\\ansitem 号同键同号；'
                '本片键式＝T 式（canonical 批B 口径），非母版批A E 式',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang，槽宽门按 lxhang=7.6mm 计 54.3pt/'
              '四连槽·106.1pt/两连槽），实测四题超宽降档：题1(T1) C槽88.9pt＝31.25mm>四连槽54.3pt'
              '→两连排（余量84%）；题5(T5) D槽47.9pt＝16.84mm>严格档预警线46.2pt（85%×槽宽）→两连排；'
              '题6(T6) A/D槽69.3pt＝24.36mm>四连槽→两连排；题8(T8) B槽66.1pt＝23.23mm>四连槽→两连排'
              '（余量62%）；余题2/3/4/7/9/10 四连排在槽合规（最宽题7 A/B槽43.6pt＝80%）；'
              '禁缩字号/负kern/删标点凑宽（零违例）',
    '难度词口径': '题面侧头标第 4 字段未带档位词，照题面库全库主档映射：0.94→简单、0.85→中档、'
                '0.65→中档；知识点 N 照导学件 06B 知识导学分册映射（一 点到直线的距离／'
                '二 两平行直线间的距离／三 对称与光线反射）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 4页；false 同 2页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            '键账对平门.py 三源对平 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗（槽40）',
            'CJK 审计 rg \\\\w+\\p{Han} 零命中', '对号门.py --片 课时06B --strict 全过（21键相等零缺漏）',
            'manifest 三源 sha256 零漂'],
    'gen': '门谱/gen台账.py 2026-09-14（W1臂C）',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时06B-2.2.4点到直线距离.json'), 'w',
                       encoding='utf-8'), ensure_ascii=False, indent=1)
print('值台账-课时06B-2.2.4点到直线距离.json → 片目录')
