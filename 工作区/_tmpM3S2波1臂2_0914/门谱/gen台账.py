# -*- coding: utf-8 -*-
"""gen台账.py — M3 S2 波1臂2（04/05/06）·由 值台账底稿-<件>.json ＋ 片目录指纹产
成卷/导学件/<片>/值台账-课时NN.json ＋ 件manifest.json。
母版件＝工作区/_tmpM3S2母版0914/门谱/gen台账.py（结构照抄，两处按本片口径改：
  ①括线判模口径登记＝承重墙阈值制「估高＞8 行」（非母版 top-5 制），逐键估高入 items；
  ②件manifest「源件sha256」＝自算三件（定稿件/题面侧/答案侧）dict（冻结 manifest 该字段
    为单一字符串，结构不同，故不承用其值，只承 题面侧/答案侧 路径）。
唯一写域＝片目录两件 json；底稿与冻结 manifest 只读。
用法: python gen台账.py <04|05|06>
"""
import hashlib
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
HERE = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1] if len(sys.argv) > 1 else '04'

CONF = {
    '04': dict(
        dir='课时04-点斜式与斜截式', jietitle='2.2.2 直线的点斜式与斜截式',
        dinggao='批A-课时04-点斜式与斜截式.md',
        连号制='1—22＝探究1—17（例1—例12＋变式，含拓T1＝印面17）＋课堂评价18—22；'
              'ansitem 首参＝印面号，例/变式标签同号连排，G 组收尾恒5',
        多选=0,
        render={
            '2章-练-课时04-E10': '括线（估高9）；三命题分问 \\par\\noindent 独立成段',
            '2章-练-课时04-E4': '括线（估高12）；截距分类三问 \\par\\noindent 独立成段；'
                               '值行零截距检验句照录',
            '2章-练-课时04-E2': '括线（估高12）；值行区间族；详解末「临界图法同件源」句照录',
            '2章-拓-课时04-T1': '括线（估高25）；两问 \\par\\noindent 分段；不等式链 \\geqslant 照录；'
                               '题后书写位 16mm→10mm（末页左栏灰底盒 G1 顶到版心下沿致 Overfull \\vbox '
                               '5.68pt，收书写位 6mm 后三零复守——片侧版面微调，不动 sty）',
            '2章-练-课时04-E7': '灰底；值行含 −U+2212／＝ 全角照直排；两问 \\par\\noindent 分段',
            '2章-练-课时04-E9': '灰底；三小问 \\par\\noindent 分段',
            '2章-练-课时04-E5': '灰底；三点判定 \\par\\noindent 分段；\\neq 路由',
            '2章-练-课时04-E15': '灰底；三小问 \\par\\noindent 分段；\\parallel／\\perp 路由',
            '2章-练-课时04-E14': '灰底；\\geqslant 与 \\(\\Rightarrow\\) 链；两问分段',
            '2章-练-课时04-E16': '灰底；值行含全角＋／＝照直排；两问分段',
            '2章-练-课时04-E13': '灰底；题首（预习注：…）行照录＝题面（课时05 截距式预告）',
            '2章-练-课时04-E12': '灰底；题首（预习注：…）行照录；①②分类 \\par\\noindent 分段',
            '2章-练-课时04-E3': '灰底；详解「比对常数项须为 −1」重复句照录批A 原文',
        },
        clean={
            '2章-练-课时04-E6': '批A 检验句「✓」字符删除，句意照录（「（检验：…直线唯一．）」）',
            '2章-练-课时04-E3': '批A 详解重复表述照录，零删改',
            '2章-练-课时04-E13': '题首（预习注：…）照录，注内 \\(x/a+y/b=1\\) 全角＋/＝线性化为半角',
            '2章-练-课时04-E12': '题首（预习注：…）照录，注内式线性化同 E13',
            '2章-练-课时04-E14': '题首（预习注：…）照录，注内式线性化同 E13',
            '2章-练-课时04-E16': '题首（预习注：…）照录，注内式线性化同 E13',
            '2章-拓-课时04-T1': '批A 图引「由 l₁（过(−4,2) 与原点）」改为「由临界位置（过(-4,2)与原点方向）」，'
                               '图号符号不入印面',
            '2章-练-课时04-E2': '批A「⟹」→\\(\\Rightarrow\\)；区间并 ∪→\\cup；∈→\\in',
            '2章-练-课时04-E10': '批A「。」照录批A 文体；b≠0→\\neq',
        },
    ),
    '05': dict(
        dir='课时05-两点式与一般式', jietitle='2.2.2 直线的两点式与一般式',
        dinggao='批A-课时05-两点式与一般式.md',
        连号制='1—24＝探究1—19（四点：两点式1—4／一般式5—12／截距式13—17／拓展直线系18—19）'
              '＋课堂评价20—24；ansitem 首参＝印面号',
        多选=0,
        render={
            '2章-练-课时05-E3': '括线（估高9）；四选项式子长→\\lxopt 逐行；A/B/C/D 逐项辨析分段',
            '2章-练-课时05-E15': '括线（估高11）；三段 \\par\\noindent；「直线型」引号改全角',
            '2章-练-课时05-E16': '括线（估高16）；六小问逐问 \\par\\noindent 独立成段＋说明段',
            '2章-练-课时05-E17': '括线（估高10）；值行含全角括号长串照录；详解末「本选项组为本卷补写」注照录',
            '2章-练-课时05-E18': '括线（估高11）；值行「A（定点(9,−4)，证明见详解）」照录（仅 true 层印，'
                               'false 档 ansblock 整块吞）；改形注照录',
            '2章-练-课时05-E19': '括线（估高16）；题首（提示：…需选学§2.2.4）行照录；①②④逐命题分段',
            '2章-练-课时05-E20': '括线（估高26）；题首（提示：同05-E19…）行照录；12 段 \\par\\noindent；'
                               'B′→B\'（数学撇号）；≤/≥→\\leqslant/\\geqslant',
            '2章-练-课时05-E21': '括线（估高11）；四边逐边 \\par\\noindent；文本箭头→改 \\(\\rightarrow\\)',
            '2章-练-课时05-E22': '括线（估高12）；两问分段；⊥→\\perp；「……」省略号照录',
            '2章-拓-课时05-T6': '括线（估高13）；(1)(2)分段；不等式链 \\geqslant；(*) 标号照录',
            '2章-拓-课时05-T7': '括线（估高14）；|PA|·|PB| 长链在等号处断段（防 Underfull \\hbox，'
                               '实测两处拆分后 unf 2→0）',
            '2章-拓-课时05-T8': '括线（估高21）；(1)(2)(3)分段＋①②分类；末段「按源卷核对注」照录（源误更正登记）',
        },
        clean={
            '2章-练-课时05-E5': '批A「m＝0时x系数−3≠0 ✓」✓ 字符删除，句意照录',
            '2章-导-课时05-G2': '批A「故"同号"完整覆盖 ✓」✓ 删除；直引号改全角引号',
            '2章-练-课时05-E22': '批A「互为相反数 ✓」✓ 删除；⊥→\\perp',
            '2章-拓-课时05-T8': '批A 三处「✓」删除留句；「"y＝(4/3)x±3"」直引号改全角；±→\\pm',
            '2章-练-课时05-E6': '批A 详解括注「（若相同则…仅说明…）」含源件省略号，照录零改',
            '2章-练-课时05-E16': '批A ⟺×6→\\(\\iff\\)；²→^{2}；≠→\\neq',
            '2章-练-课时05-E17': '批A 详解「左＝…右＝…」全角等号线性化为数学形；改形注照录',
            '2章-练-课时05-E19': '批A 0≤θ＜2π→\\(0\\leqslant\\theta<2\\pi\\)；√/²/∈ 路由',
            '2章-练-课时05-E20': '批A |sin|≤1→\\leqslant；√((x−3)²＋y²)→\\sqrt{(x-3)^{2}+y^{2}}；φ→\\varphi',
            '2章-导-课时05-G4': '批A「S＝(1/2)||a||b||」双竖线照录为 \\(||a||b||\\)（绝对值连写）',
            '2章-练-课时05-E15': '批A 直引号「"直线y＝x−1的方程"」改全角引号',
        },
    ),
    '06': dict(
        dir='课时06-两条直线的位置关系', jietitle='2.2.3 两条直线的位置关系',
        dinggao='批B-课时06-两条直线的位置关系.md',
        连号制='1—21＝探究1—16（平行与垂直判定1—9／交点·共点与综合10—14／拓展应用15—16）'
              '＋课堂评价17—21；ansitem 首参＝印面号',
        多选=2,
        render={}, clean={},
    ),
}
C = CONF[tag]
PIECE = os.path.join(ROOT, '成卷/导学件', C['dir'])
BASE = json.load(open(os.path.join(HERE, f'值台账底稿-{tag}.json'), encoding='utf-8'))
FROZEN = json.load(open(os.path.join(ROOT, f'成卷/题面库/manifest/课时{tag}.manifest.json'),
                        encoding='utf-8'))


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def _readings():
    """双档 log 实读：errors/Overfull/Underfull/Missing character + 页数 + ANSKEY 数。"""
    out = {}
    for f in ('main-true', 'main-false'):
        lp = os.path.join(PIECE, f + '.log')
        log = open(lp, encoding='utf-8', errors='replace').read()
        m = re.search(r'Output written on .*\((\d+) pages', log)
        out[f] = (f"errors={len(re.findall('^! ', log, re.M))} missing={len(re.findall('Missing character', log))}"
                  f" Overfull={len(re.findall('Overfull', log))}"
                  f" Underfull={len(re.findall('Underfull', log))}"
                  f" ANSKEY={len(re.findall('M3-ANSKEY: ', log))}"
                  f" {m.group(1) if m else '?'}页")
    return out


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


items = []
for it in BASE['items']:
    k = it['键']
    items.append({
        '键': k,
        '印面号': it['印面号'],
        '键型': it['键型'],
        '值tex': it['值tex'],
        '值源': it['值源'],
        '值快照': '逐字全等' if it['键型'] in ('值', '过程') else '锚制',
        '估高行数': it['估高行数'],
        '判模': it['判模'],
        '渲染注记': C['render'].get(k, ('括线' if it['判模'] == '括线' else '灰底')
                              + '；\\ansitem 单条＋\\ansnote{{详解}}'),
        '清洗注记': C['clean'].get(k, '逐字照录，零清洗'),
    })

ledger = {
    '件': f'课时{tag}-{C["dir"].split("-")[-1]} 导学件（M3 成卷轮 S2 波1臂2·题后紧跟答案制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '节标题': C['jietitle'],
    '印面连号制': C['连号制'],
    '括线判模口径': '承重墙阈值制：块估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径 ＞8 行→括线'
                  '（派工单§三.1 口径，严于母版 top-5 制，属已登记偏差）；'
                  '括线键＝' + '、'.join(it['键'].rsplit('-', 1)[-1] for it in items if it['判模'] == '括线') +
                  '；渲染面硬计数＝灰底大矩形' + str(sum(1 for it in items if it['判模'] == '灰底')) +
                  '／ansrule 长线' + str(2 * sum(1 for it in items if it['判模'] == '括线') + 2) + '（门谱实测）',
    '多选键数': C['多选'],
    'toolchain锁': {'file': 'qp-m3.sty', 'md5': md5(os.path.join(PIECE, 'qp-m3.sty')),
                   '注记': '本地挂载副本，禁改保 md5；破损即停'},
    '指纹': {
        'main.tex.md5': md5(os.path.join(PIECE, 'main.tex')),
        'main-true.pdf.md5': md5(os.path.join(PIECE, 'main-true.pdf')),
        'main-false.pdf.md5': md5(os.path.join(PIECE, 'main-false.pdf')),
        '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
        '双档读数': _readings(),
    },
    '门谱': ['门-守恒对号.py', '门-值快照键型判模.py', '门-回流.py',
            '键账对平门.py 三腿对平', 'makebox槽宽门.py zero-fp/strict 双档'],
    'gen': '门谱/gen台账.py 2026-09-14',
}

piece_manifest = {
    '片': C['dir'],
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳（main-true/main-false）',
    '冻结manifest': f'../../题面库/manifest/课时{tag}.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': {
        f'定稿/{C["dinggao"]}': sha(os.path.join(ROOT, '定稿', C['dinggao'])),
        FROZEN['题面侧']: sha(os.path.join(ROOT, '成卷/题面库', os.path.basename(FROZEN['题面侧']))),
        FROZEN['答案侧']: sha(os.path.join(ROOT, '成卷/题面库', os.path.basename(FROZEN['答案侧']))),
    },
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
}

json.dump(ledger, open(os.path.join(PIECE, f'值台账-课时{tag}.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'值台账-课时{tag}.json ＋ 件manifest.json → {PIECE}')
