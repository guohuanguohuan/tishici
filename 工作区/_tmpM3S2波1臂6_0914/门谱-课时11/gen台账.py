# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时11.json ＋ 件manifest.json（片目录）。
参数化自 门谱-课时10/gen台账.py。唯一写域：成卷/导学件/课时11-2.5.1椭圆的标准方程/
{值台账-课时11.json, 件manifest.json}。冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时11-2.5.1椭圆的标准方程'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open(os.path.join(HERE, '值台账底稿-课时11.json'), encoding='utf-8'))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入）
RENDER = {
    '2章-练-课时11-简7': '括线；例1＝开放劣构选条件①/②＋(2)参数分类，多问计1；值行含全角＜＞（探针实证可印）',
    '2章-练-课时11-简6': '括线；例10＝\\duoxuan 多选标记（本片唯一多选，ACD）；照订正版收录'
                        '（源「a²≤2b²」笔误已订 a²≥2b²，亲算⑥注记1）',
    '2章-练-课时11-难1': '括线；例15＝焦点三角形外接/内切圆复合最值（t 换元＋均值）',
    '2章-练-课时11-难2': '括线；变式16＝内心×重心构形；题面「离心率」前引照录（替换建议见观察注）',
    '2章-练-课时11-中4': '括线；变式14＝焦半径向量约束，详解含 B 点回代验算行',
    '2章-练-课时11-中2': '括线；变式12＝平行四边形模型（源详解含图，印面不放图）',
    '2章-练-课时11-简8': '灰底；命制席（11-命1 §九原案照录）；值行全角＋＝照录',
    '2章-练-课时11-简9': '灰底；命制席（11-命2 §九原案照录）',
    '2章-练-课时11-简10': '括线；命制席（11-命3 §九原案照录）；「离心率」前引照录（替换建议见观察注）',
    '2章-导-课时11-G2': '灰底；轨迹两可（椭圆或线段）辨析单选',
}
CLEAN = {
    '2章-练-课时11-难1': '详解③源引「由11-中5通式」（该席已整块移拓15）——印面去悬空交叉引用，'
                        '通式本体现写；「⟹」→数学推导连接，✓类无',
    '2章-练-课时11-简3': '详解承定稿直验口径（两位置简验，避「通径最短」一般证前引 2.5.3）；'
                        '「装配时如严检可前置结论卡」句属过程性口令不印',
    '2章-练-课时11-简6': '详解为独立推导（|OP| 范围法）；源解析笔误照订正版（a²≥2b²）；'
                        '「✓/✗」→「成立/不成立」',
    '2章-练-课时11-简1': '详解验算行 ✓→「成立」两处',
    '2章-练-课时11-简8': '详解 ✓→「成立」两处；辨析注随行',
    '2章-练-课时11-简9': '详解 ✓→「成立」两处',
    '2章-练-课时11-简10': '详解「⟹」→数学推导连接；验算行 ✓→「成立」两处',
    '2章-练-课时11-中1': '题设引号「存在P」照录；源【亲算】双路线注不入印面',
    '2章-导-课时11-G5': '详解「⟹」→「则」衔接',
}
for it in BASE['items']:
    if it['键'] not in CLEAN:
        CLEAN[it['键']] = '值行逐字照录，零清洗；详解承定稿直转（字形已路由，见列头注）'

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
        '渲染注记': RENDER.get(k, ('括线' if it['判模'] == '括线' else '灰底') + '；\\ansitem 单条'),
        '清洗注记': CLEAN.get(k, '逐字照录，零清洗'),
    })

ledger = {
    '件': '课时11-2.5.1椭圆的标准方程 导学件（M3 成卷轮 S2 波1 臂6·批C 之二·母版照抄制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–21＝探究1—16＋课堂评价17—21；ansitem 首参＝印面号，例/变式标签同号连排',
    '装配序': '探究点一 简7,8,2,3,4／探究点二 简1,9,10,5／探究点三 简6(多选),中1,中2,中3,中4／'
             '探究点四 难1,难2／课堂评价 G1~G5（印17—21）；探究区按探究点分组、组内简→中→难',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径；est＞8 → 括线（承重墙），'
                  '本片括线 11 键（难1:16,中4:15,简7:13,简6:13,中2:13,难2:11,简1:11,简4:10,简3:10,'
                  '简10:10,中1:10），括末/灰首间隔＝10＞8（12th＝简2:8）；'
                  '渲染面硬计数：灰底大矩形10＝21−11、ansrule 长线24＝11块×2＋尾框2、'
                  '尾框（文档序末2线）在末页（门谱实测）',
    '观察注落实': {
        '来源': '军师令·补产批CA 核账 §C.5（_tmpM3补产批CA0913/核账.md L17/L21/L26）随片下发',
        '2章-练-课时11-难2': '题面照录在印（设问词「离心率」2.5.2 前引照录不改）；'
                           '装配替换建议入台账：S4 可换问「求 a/c 或(|PF₁|+|PF₂|)/|F₁F₂| 之比」消前引；落实数 1',
        '2章-练-课时11-简10': '「离心率」前引同难2（命制席照录不改）；装配替换建议入台账：'
                            'S4 可换问「求 a/c 或(|PF₁|+|PF₂|)/|F₁F₂| 之比」消前引；落实数 1',
        '2章-练-课时11-简3': '详解承定稿直验口径（两位置简验）照贴，前引「通径最短」一般证已避；落实数 1',
        '2章-练-课时11-中3': '白名单「所求不明」复读行——亲算钉死后题面照录在印（核账§C.5 行10）；落实数 1',
        '中6（拓16席）/拓2': '非本件键域（拓展册席/撤位让位席），本件落实数 0；前引行注随席移拓展',
    },
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': 'true 0错0溢0under0缺字 ANSKEY=21 6页；false 同 3页',
    },
    '门谱': ['门-守恒对号.py（全绿）', '门-值快照键型判模.py（全绿）', '门-回流.py（全绿）',
            '键账对平门.py 三源对平 PASS', 'makebox槽宽门.py zero-fp/strict 双档 0旗'],
    'gen': '门谱-课时11/gen台账.py 2026-09-14',
}

mf = json.load(open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时11.manifest.json'),
                    encoding='utf-8'))
piece_manifest = {
    '片': '课时11-2.5.1椭圆的标准方程',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时11.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': {'批C-课时11-2.5.1椭圆的标准方程.md': mf['源件sha256'],
                   '课时11-2.5.1椭圆的标准方程.md': sha(os.path.join(
                       M3ROOT, '成卷/题面库/课时11-2.5.1椭圆的标准方程.md')),
                   '课时11-2.5.1椭圆的标准方程-答案侧.md': sha(os.path.join(
                       M3ROOT, '成卷/题面库/课时11-2.5.1椭圆的标准方程-答案侧.md'))},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
    '多选门': '本片正文多选 1（简6，\\duoxuan 在印）≤4 合规；难1 答案 BCD 类多结论不涉及',
    '观察注落实': ledger['观察注落实'],
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时11.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时11.json ＋ 件manifest.json → 片目录')
