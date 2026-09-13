# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时14.json（练习件版）。
唯一写域：成卷/练习件/课时14-2.6.2双曲线性质/值台账-课时14.json。冻结 manifest 本体只读。
（S3 练习件产出清单＝main.tex＋双壳＋值台账 json，不产 件manifest.json。）
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/练习件/课时14-2.6.2双曲线性质'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = json.load(open(os.path.join(HERE, '值台账底稿.json'), encoding='utf-8'))
# 练习件键域过滤：底稿 vals 系答案侧全集（71 键），件账只收练键序 01~16（拓区隔离）
BASE['vals'] = {k: v for k, v in BASE['vals'].items() if k in BASE['keys']}

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入；练习件全线括线）
RENDER = {
    '2章-练-课时14-01': '括线；四小问值行照答案侧；详解(1)~(4) \\par\\noindent 每问独立成段',
    '2章-练-课时14-02': '括线；详解含验算句（S2 导学件同源宏文承入，句末 ．照批D）',
    '2章-练-课时14-03': '括线；单选四连排降档两连排（D 槽 70.5pt＞槽宽＋容差 61.5pt）',
    '2章-练-课时14-05': '括线；题面空位 \\kongda{2}（详解版印答、纯题版退定宽空线，两档等形）',
    '2章-练-课时14-07': '括线；单选四连排降档两连排（A~D 槽 81.4~86.6pt 全超容差）',
    '2章-练-课时14-11': '括线；单选四连排降档两连排（C/D 槽 70.5/81.0pt 超容差）',
    '2章-练-课时14-12': '括线；单选保持四连排（四槽 zero-fp 全过）',
    '2章-练-课时14-13': '括线；题面末 \\kongda{1}（题面库无空位标记，印答位依填空槽制补承）',
    '2章-练-课时14-14': '括线；值行「证明见解析。」（过程型，比对串照答案侧）',
    '2章-练-课时14-15': '括线；详解承导学件例54 宏文、句末标点照批D 定稿回改「。」',
    '2章-练-课时14-16': '括线；详解系臂C 依批D §7.1【14-16】自行宏化（导学件无先例块）；'
                       '句末「。」；链首分式改 \\dfrac 叠式（跨栏超宽 13.2pt 修复）',
}
CLEAN = {
    '2章-练-课时14-13': '题面库原句无空位标记，印答位 \\kongda{1} 承填空槽制补入（题面文字零改动）',
    '2章-练-课时14-15': '详解句末 ．→。照批D 定稿回改（小数点不动）；值照答案侧逐字',
    '2章-练-课时14-16': '验算句 ✓剔改「合」字样（承母版先例）；x=2 平方增根判定段承批D 补证全文',
}
SLOT = {  # 槽型对账（题面侧 ### 键｜槽型 头标实录）＋书写区＋选项槽位
    '2章-练-课时14-01': ('解答', '', '32mm'), '2章-练-课时14-02': ('解答', '', '16mm'),
    '2章-练-课时14-03': ('单选', '两连排', ''), '2章-练-课时14-04': ('解答', '', '16mm'),
    '2章-练-课时14-05': ('填空', '', ''), '2章-练-课时14-06': ('解答', '', '16mm'),
    '2章-练-课时14-07': ('单选', '两连排', ''), '2章-练-课时14-08': ('解答', '', '24mm'),
    '2章-练-课时14-09': ('解答', '', '16mm'), '2章-练-课时14-10': ('解答', '', '24mm'),
    '2章-练-课时14-11': ('单选', '两连排', ''), '2章-练-课时14-12': ('单选', '四连排', ''),
    '2章-练-课时14-13': ('填空', '', ''), '2章-练-课时14-14': ('解答', '', '16mm'),
    '2章-练-课时14-15': ('解答', '', '24mm'), '2章-练-课时14-16': ('解答', '', '24mm'),
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
    '件': '课时14-2.6.2双曲线性质 练习件（M3 成卷轮 S3 W2 臂C·题后紧跟答案制·照课时01母版体例）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–16＝manifest 练键序 2章-练-课时14-01~16 零重排；\\tihao 号＝\\ansitem 号同键同号',
    '括线判模口径': '练习件全线括线模（S3 波次方案 §四.3：导言 \\ansblockgrayfalse 一次置定、'
                  '件内不切换、灰底禁用）；渲染面硬计数：ansbg 灰底矩形0＝ansrule 长线34'
                  '＝16块×2＋尾框2（门谱实测）；>8行→括线模口径全线满足，逐键估高读数备查',
    '降档登记': '选项槽位默认四连排（0.25\\linewidth−0.25\\lxhang），makebox槽宽门 zero-fp 实测降档：'
               '题3(03) D槽70.5pt＞61.5pt（超9.0pt）→两连排；题7(07) A~D 槽81.4~86.6pt 全超→两连排；'
               '题11(11) C/D槽70.5/81.0pt→两连排；题12(12) 四槽全过保持四连排；'
               '禁缩字号/负kern/删标点凑宽（零违例）',
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 5页；false 同 2页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            '键账对平门.py 三源对平 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗',
            'CJK 审计 rg \\w+\\p{Han} 零命中'],
    'gen': '门谱/gen台账.py 2026-09-14',
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时14.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时14.json → 片目录')
