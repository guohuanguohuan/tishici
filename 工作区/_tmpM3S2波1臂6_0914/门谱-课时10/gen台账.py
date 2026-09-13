# -*- coding: utf-8 -*-
"""gen台账.py — 由值台账底稿＋件级指纹产 值台账-课时10.json ＋ 件manifest.json（片目录）。
参数化自 母版 门谱/gen台账.py。唯一写域：成卷/导学件/课时10-2.4曲线与方程/
{值台账-课时10.json, 件manifest.json}。冻结 manifest 本体只读。
"""
import hashlib
import io
import json
import os
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = 'C:/提示词/工作区/M3-第2章量产0913/成卷/导学件/课时10-2.4曲线与方程'
M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = json.load(open(os.path.join(HERE, '值台账底稿-课时10.json'), encoding='utf-8'))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

# 逐键渲染/清洗注记（判模由底稿 items 判模字段承入）
RENDER = {
    '2章-导-课时10-G2': '灰底；装配层加「定义提示卡」\\zhuzhu（军师令·核账§C.4 前引观察落实；'
                       '两档等形不泄答）在印；题面〔图注〕照录为文本行',
    '2章-练-课时10-中1': '括线；值行「8」用全角直角引号「」（探针实证可印）',
    '2章-练-课时10-难1': '括线；槽型「多结论选择」不标多选（manifest 多选＝0，源卷未标）；'
                        '题面〔图注〕照录为文本行',
    '2章-练-课时10-难2': '括线；序号填空（②④），题面①~⑤结论行 \\bindp 逐行排',
    '2章-练-课时10-简5': '括线；详解含双点验算段（同族判别注不入印面）',
    '2章-练-课时10-中2': '括线；纯粹性完备性双向检验；✓→「成立」',
}
CLEAN = {
    '2章-练-课时10-简3': '详解 ✓→「成立」、⟺→\\iff（字形探针实证：✓⟺ 书宋/拉丁缺字禁用）',
    '2章-练-课时10-简7': '详解 C 项 ⟺→\\iff',
    '2章-导-课时10-G5': '详解 ✓→「成立」两处',
    '2章-练-课时10-难1': '详解 ✓→「成立」三处、⟺→「当且仅当」；'
                        '③ 切线斜率记号 m→k（避与曲线参数 m 相混；运算与源逐项同）',
    '2章-练-课时10-难2': '详解 ½→\\frac{1}{2}；穷尽性补核段照定稿 §9.4（源未给）',
    '2章-导-课时10-G4': '剔除句「不构成三角形——」破折号照录',
}
for it in BASE['items']:
    if it['键'] not in CLEAN:
        CLEAN[it['键']] = '值行逐字照录，零清洗；详解承定稿直转（✓⟺⟹ 三类字形已路由，见列头注）'

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
    '件': '课时10-2.4曲线与方程 导学件（M3 成卷轮 S2 波1 臂6·批C 之一·母版照抄制）',
    '口径': '键账 {keys,vals} 供 工具/键账对平门.py 直读；items 逐键读数＝值快照键型判模门落盘',
    '键账制式': '对平门 --ledger 同制式（{"keys":[…],"vals":{键:值}}）',
    'keys': BASE['keys'],
    'vals': BASE['vals'],
    'items': items,
    '印面连号制': '1–21＝探究1—16＋课堂评价17—21；ansitem 首参＝印面号，例/变式标签同号连排',
    '装配序': '探究点一 简1,2,3,7,8,10／探究点二 简4,5,6,9,中2／探究点三 中1,中3,中4,难1,难2／'
             '课堂评价 G1~G5（印17—21）；探究区按探究点分组、组内简→中→难',
    '括线判模口径': '块内容估高 wlen（全角1·ASCII0.5，剔\\命令）/23 栏宽字口径；est＞8 → 括线（承重墙），'
                  '本片括线 9 键（难2:30,难1:18,G3:16,简5:13,中1:12,G4:11,简3:10,简4:9,中2:9），'
                  '括末/灰首间隔＝9＞8（10th＝简8/G2:8）；'
                  '渲染面硬计数：灰底大矩形12＝21−9、ansrule 长线20＝9块×2＋尾框2、尾框（文档序末2线）在末页（门谱实测）',
    '观察注落实': {
        '来源': '军师令·补产批CA 核账 §C.4（_tmpM3补产批CA0913/核账.md L20）随片下发',
        '2章-导-课时10-G2': '已落实：装配层加「定义提示卡」\\zhuzhu（椭圆定义·折叠垂直平分线口径，'
                          '2.5.1 前引）于题干后，两档等形不泄答；落实数 1',
        '拓2/拓3/拓8/拓10/中7': '非本件键域（拓展册席/置换移出席），本件落实数 0；观察注随档移交拓展册工位',
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
    'gen': '门谱-课时10/gen台账.py 2026-09-14',
}

mf = json.load(open(os.path.join(M3ROOT, '成卷/题面库/manifest/课时10.manifest.json'),
                    encoding='utf-8'))
piece_manifest = {
    '片': '课时10-2.4曲线与方程',
    '件型': '导学件（题后紧跟答案制）·单源双档 main.tex＋\\mthreepure 壳',
    '冻结manifest': '../../题面库/manifest/课时10.manifest.json（本体勿动）',
    '冻结manifest键序': BASE['keys'],
    '源件sha256': {'批C-课时10-2.4曲线与方程.md': mf['源件sha256'],
                   '课时10-2.4曲线与方程.md': sha(os.path.join(
                       M3ROOT, '成卷/题面库/课时10-2.4曲线与方程.md')),
                   '课时10-2.4曲线与方程-答案侧.md': sha(os.path.join(
                       M3ROOT, '成卷/题面库/课时10-2.4曲线与方程-答案侧.md'))},
    'toolchain锁': ledger['toolchain锁'],
    '件指纹': ledger['指纹'],
    '键↔号': {it['键']: it['印面号'] for it in items},
    '多选门': '本片正文多选 0（10-难1 槽型「多结论选择」源卷未标多选、答案 BCD 不计多选门，'
             '汇总§十一课时10行多选＝0 维持）',
    '观察注落实': ledger['观察注落实'],
}

json.dump(ledger, open(os.path.join(PIECE, '值台账-课时10.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(piece_manifest, open(os.path.join(PIECE, '件manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值台账-课时10.json ＋ 件manifest.json → 片目录')
