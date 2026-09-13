# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-衔接节.json（练习件版·W3臂H）。
唯一写域：成卷/练习件/衔接节/值台账-衔接节.json。冻结 manifest 本体只读。
（S3 练习件产出清单＝main.tex＋双壳＋值台账 json；不产 件manifest.json。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/衔接节'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '值台账底稿.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（27 键），件账只收练键序 练1~16（拓区隔离＋导学域隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-衔接-2': '括线；题面空位 \\kongda{21}（详解版印答、纯题版退定宽空线，两档等形）',
    '2章-练-衔接-10': '括线；长值行 \\begingroup\\rightskip=0pt plus 1fil 包裹防溢'
                     '（值内零改，字节级全等；承导学件同位档去 \\allowbreak 恢复逐字）',
    '2章-练-衔接-14': '括线；选项两连排（四连排严格档全旗降档，真算读数见「降档登记」）',
    '2章-练-衔接-15': '括线；选项两连排（四连排严格档全旗降档，真算读数见「降档登记」）',
}
CLEAN = {
    '2章-练-衔接-1': '详解承导学件衔接节印面档（批E §七 provenance 括注剔除、教学性括注保留、'
                   '句号「。」→「．」梯级统一）；值逐字照答案侧',
    '2章-练-衔接-5': '批E 详解 ∎ 收束记号不印（导学件同口径）；值「证毕（Δ=4m²+9>0）」逐字快照',
    '2章-练-衔接-16': '批E §七 详解链内结论笔误（选①②/选①③ 范围互换，与其自列不等式矛盾）'
                    '已由导学件印面档校正：①②⇒2<t<3、①③⇒1<t<2，与答案侧值一致；值逐字照答案侧',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋降档
    '2章-练-衔接-1': ('解答', '', '32mm'), '2章-练-衔接-2': ('填空', '', ''),
    '2章-练-衔接-3': ('解答', '', '16mm'), '2章-练-衔接-4': ('解答', '', '24mm'),
    '2章-练-衔接-5': ('解答', '', '24mm'), '2章-练-衔接-6': ('解答', '', '24mm'),
    '2章-练-衔接-7': ('解答', '', '16mm'), '2章-练-衔接-8': ('解答', '', '32mm'),
    '2章-练-衔接-9': ('解答', '', '16mm'), '2章-练-衔接-10': ('解答', '', '16mm'),
    '2章-练-衔接-11': ('解答', '', '16mm'), '2章-练-衔接-12': ('解答', '', '16mm'),
    '2章-练-衔接-13': ('解答', '', '16mm'), '2章-练-衔接-14': ('单选', '两连排', ''),
    '2章-练-衔接-15': ('单选', '两连排', ''), '2章-练-衔接-16': ('解答', '', '16mm'),
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
        '清洗注记': CLEAN.get(k, '详解承导学件衔接节印面档（provenance 括注剔除）；'
                             '值逐字照录，零清洗'),
    })

ledger = {
    '件': '衔接节 练习件（M3 成卷轮 S3 W3 臂H·练习位独立·题后紧跟答案制·S3 线末位片）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序 练1~16 零重排；\\tihao 号＝\\ansitem 号同键同号',
    '知识点映射': '知识点一＝一元二次方程的判别式｜二＝根与系数的关系（韦达定理）｜'
                '三＝方程（组）的解法（代入消元/换元/对称构造）｜四＝直线与圆锥曲线的位置关系'
                '（判定/弦长/切线，承导学件探究点一~三域）——前三域照导学件知识导学分册，'
                '第四域为补题 3 题所在 2.8 本课域；覆盖断言 门-衔接覆盖.py 全绿（{一,二,三,四}零缺漏）',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang），探针真算（槽宽门 strict 档）：'
               '题14（练14）C/D 槽估值 60.4pt＞预警线 46.2pt、题15（练15）四槽 64.1~64.6pt＞46.2pt'
               '→ 双双降两连排（0.5\\linewidth−0.5\\lxhang−0.25em），落位后零误报/严格双档 8 槽全过'
               '（52%~61%）；禁缩字号/负kern/删标点凑宽（零违例）',
    '槽配偏差登记': '衔接节练习位＝存量13保真＋补3（预备课位），槽配 单选2＋填空1＋解答13、多选0'
                 '（manifest 期望值在案），非课时件 10选4填2解 基线；难度 简8＋中6＋难2 照批E §四'
                 '（难2 席由存量题占位，批E 台账 §五.10 已登记）',
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
            '门-衔接覆盖.py（全绿·知识点覆盖断言）', '键账对平门.py 三源对平 PASS',
            'makebox槽宽门.py zero-fp/strict 双档 0旗', 'CJK 审计 rg \\\\w+\\p{Han} 零命中',
            '前置闸 对号门 --strict（题面库片面，exit 0）＋manifest 三源 sha256 零漂'],
    'gen': '门谱/gen台账.py（W3臂H 改注记版）2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-衔接节.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-衔接节.json → 片目录')
