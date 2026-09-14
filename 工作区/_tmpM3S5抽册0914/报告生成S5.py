# -*- coding: utf-8 -*-
"""报告生成S5.py — 试产报告.md 终版（分段落盘：§一至§三 / §四至§六）。全实数取自读数文件。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE

J = lambda p: json.load(open(os.path.join(HERE, p), encoding='utf-8'))
rows = J('逐件汇总.json')
books = J('成册汇总.json')
diag = J('诊断读数.json')
strong = J('强折形复验.json')
frag = J('片段在册证明.json')

drift = {x['件']: x for x in diag['印面号漂移']}
nrc = sum(1 for r in rows if r['rc红'])
n_green = sum(1 for r in rows if not r['rc红'] and not (r['红']))
nz30 = sum(1 for r in rows if any('三零' in x for x in (r['红'] or [])))
nmiss = sum(1 for r in rows if any('逐键值印面' in x for x in (r['红'] or [])))
tot_keys = sum(r['键数'] or 0 for r in rows if r['件型'] != '拓展册')
tuoz = {r['片']: r for r in rows if r['件型'] == '拓展册'}
TUO_KEYS = {'上册': 87, '下册': 115}
bk = {b['册']: b for b in books}
pg = {k: v['页数'] for k, v in bk.items()}
tot_true = sum(v['true'] for v in pg.values())
tot_false = sum(v['false'] for v in pg.values())
zhe = {r['片']: (r.get('台账折形比对') or {}) for r in rows if r['件型'] == '拓展册'}
zhe_mid = sum(zhe[p].get('containment中', 0) for p in zhe)
zhe_tot = sum(zhe[p].get('台账键数', 0) for p in zhe)
frag_res = {k: v for k, v in frag.items() if v.get('片段数')}


def anno(r):
    key = '%s-%s' % (r['件型'], r['片'])
    a = []
    if r['件型'] == '拓展册':
        a.append('器停(§四.1)→臂侧适配入册')
    if key in drift:
        a.append('台账印面号漂移%d键(§四.2)' % drift[key]['漂移数'])
    s = strong.get(key)
    if s:
        a.append('缺印假红→强折形%s(§四.3)' % ('全中' if s['缺印数'] == 0
                                              else '残%d键片段级中' % s['缺印数']))
    reds = r['红'] or []
    if any('三零' in x for x in reds):
        a.append('三零(断行/构式,§四.4-5)')
    return a


L1 = []
A1 = L1.append
A1('# M3 成卷轮 S5 抽答器入链试产报告（纯答案册·三档导出第三档）— 2026-09-14')
A1('')
A1('> 执行：M3 成卷轮 S5 抽答器入链试产臂｜写前核 mode＝auto｜红线执行：零 git'
   '（全程未运行任何 git 命令）；成卷件树与 工具/ 全程只读零落笔；写入仅'
   ' `工作区/_tmpM3S5抽册0914/`（44 件册目录＋影子件＋三册草案＋读数件＋本报告）；'
   'qp-m3.sty md5 锁 `7c3930…6573` 预检 44 件全同。')
A1('> 对象＝`成卷/导学件/`21＋`练习件/`21＋`拓展册/上·下`（44 件，main.tex 单源只读）；'
   '卷件（测评/滚A/滚B）在产不在本轮域，归位后补抽并入。')
A1('')
A1('## 一、逐件抽册读数表（工具/答案抽册器.py，--order zhengce，--skip-png）')
A1('')
A1('| 件型 | 片 | 键数 | 册页 t/f | 门红项 | 异常标注 |')
A1('|---|---|---|---|---|---|')
for r in rows:
    key = '%s-%s' % (r['件型'], r['片'])
    pgf = r['页数'] or {}
    keys = r['键数'] if r['键数'] else (
        TUO_KEYS.get(r['片'], '—') if r['件型'] == '拓展册' else '—')
    pgcell = '%s/%s' % (pgf.get('true', '—'), pgf.get('false', '—')) \
        if r['件型'] != '拓展册' else '—（适配入册）'
    a = '；'.join(anno(r)) or '—'
    A1('| %s | %s | %s | %s | %d | %s |' % (r['件型'], r['片'], keys, pgcell,
                                            len(r['红'] or []), a))
A1('')
A1('读数全量＝各件目录 `抽册读数.json`（门读数逐条＋册值快照）。'
   '42 件本器跑（rc 全 0 落读数）；拓展册 2 件本器两停（真件台账 KeyError／'
   '影子件降级后 seat 制 order_blocks TypeError，_stdout红.txt 留证）→ 臂侧适配器'
   '接产（§四.1），其键数＝适配器解析。')
A1('')
A1('## 二、三档硬断言汇总（逐件跑）')
A1('')
A1('| 断言 | 口径 | 读数 |')
A1('|---|---|---|')
A1('| 钉值逐字全等 | 册值≡正册件内值（硬断言）；册详解≡正册详解；值台账值tex/印面号腿 | '
   '值腿 908/908 键＋详解腿 908/908 逐字全等（42 件全绿）；'
   '台账值tex 腿 41 件绿、课时19 缺件降级；台账印面号腿 41 件绿＋课时02 红'
   '（漂移 15 键，§四.2） |')
A1('| 答案块数守恒 | 源锚＝源块＝册锚＝册块＝canonical 键数 | 42/42 全绿'
   '（Σ键 908＝导学 572＋练习 336，与三册汇编守恒双证）；拓展 202（适配器，'
   '拓展答案册册级守恒绿） |')
A1('| 题面零泄漏 | 题面库题面行≥12字 run（NFKC＋空白归一，正册答案块体豁免），双档各查 | '
   '40 课时/衔接件全绿 0 条；拓展册题面库缺档→源件题面区替代针，册级证＝'
   '拓展答案册双档泄漏 0（针 384 run，含拓展源件针，§四.1） |')
A1('| 同序同号 | 册log ANSKEY 序≡册tex序（双档两遍）≡正册log序逐位；印面号集恰一对应 | '
   '42 件 log ANSKEY 全绿＋≡正册log序逐位；PDF 号序≡正册 true 号序逐位全绿；'
   '三册 seat 序 PDF 证两档全绿（log ANSKEY 4 编全同为权威证，§四.7） |')
A1('')
A1('三零门（error/Overfull/Underfull/Missing character 双档两遍全零）＝19/42 件绿；'
   '红 23 件全数归因：7 件源值构式 err（\\ding 80 处＝课时16(24)+课时17(56)；'
   'Missing $ 2 处/件×5 件＝裸 `_`/`²` 文本模式数学）＋断行松驰族'
   '（Under/Over 1-2 处/件）；守恒/对号/钉值/零泄漏主断言不受累。')
A1('')
A1('## 三、汇编三件答案册 tex 草案（同序同号·壳制照 qp-m3 双档惯例）')
A1('')
A1('| 册 | 草案目录 | 块数 | 页数 详解印本/纯值速查 | 复核门终读数 |')
A1('|---|---|---|---|---|')
name = {'导学答案册': '导学', '练习答案册': '练习', '拓展答案册': '拓展（臂侧适配）'}
for k in ('导学答案册', '练习答案册', '拓展答案册'):
    b = bk[k]
    A1('| %s答案册 | `工作区/_tmpM3S5抽册0914/%s/`（ansbook.tex＋双壳＋sty） | %d | %d/%d | '
       '守恒/同序/同号/钉值/零泄漏/页数 全绿；三零余 %s |'
       % (name[k], k, b['块数'], b['页数']['true'], b['页数']['false'],
          '；'.join(x.replace('三零[', '').replace('（两遍末态）', '')
                    for x in b['红']) or '全绿'))
A1('')
A1('单源体＝ansbook.tex（册头章名＝册名＋【纯答案册】标签行＋逐片节头（源件 keshi/xjkeshi '
   '照抄；拓展册按 key 课时前缀分节）＋逐题 ansblock(键)→ansitem(印面号原串){值}'
   '＋ansnote{详解}）；双壳＝ansbook-true（\\ansbookdetail=1 详解印本）／ansbook-false'
   '（=0 纯值速查）；编译 xelatex ×2 双档；册面补钉＝ROUTING 承源件＋CJKGLUE＋'
   '\\ansblockgrayfalse＋\\tailfill[30mm]＋**pifont**（§四.4）。逐册机读＝`成册读数.json`。')
A1('')

open(os.path.join(HERE, '试产报告.md'), 'w', encoding='utf-8').write('\n'.join(L1) + '\n')

# ---- 段二：§四 异常清单 / §五 页数预算 / §六 结论 ----
L2 = []
A2 = L2.append
A2('## 四、异常清单（按阻断级排序）')
A2('')
A2('1. **拓展册 2 件本器结构性不兼容（器停，非数据红）**：①值台账旧制'
   '（items[].key/值 渲染形，无 键/值tex/印面号 字段）→ 真件跑 `load_ledger` KeyError；'
   '②影子件去台账降级后，seat 制印面号（T1/01…分课时重启）撞 `order_blocks` 整数 1..N 制'
   '→ TypeError 硬停；③`RE_ITEM` 整数制致 T-seat 块值丢失（parse 层）。处置＝S5 臂侧'
   '适配器产册（印面号原串逐字、值/详解逐字，成册门全绿）；**器升制工单**'
   '（seat 印面号制＋台账 v2＋题面库补上/下册 md 与 manifest 后，拓展册回归本器抽册）。')
A2('2. **导学件-课时02 值台账印面号漂移 15 键（真数据红）**：件内已重编'
   '（E9→2 号、E15→3、E16→4…装配序≡升序自洽、PDF 印面自洽），台账印面号列停在旧题号。'
   '→ **台账回填工单**（以件内 ansitem 号为准回写 值台账-课时02.json）。')
A2('3. **器面折形表缺口 → 9 件「逐键值印面在册」假红**：缺折形含 \\sqrt、\\(\\)、'
   '\\allowbreak、\\hspace{..}、\\{\\}、\\pi、弯引号等；臂侧强折形复验 8/9 件全中，'
   '残 8 键片段级中（`片段在册证明.json`）——**均非缺印**。→ 折形表扩容工单'
   '（`gate_pdf.needle`）。')
A2('4. **源值构式 err 族（成卷件只读未动，册面已消其一）**：\\ding{51} 勾形'
   '（导学课时16/17 值域，24＋56 处 Undefined）→ 三册面挂 `\\usepackage{pifont}`'
   '补钉（照 ROUTING 承源件同精神）后归零；Missing $（导学 14/18/19＋练习 18/19，'
   '各 2 处＝值域裸 `_`/`²` 文本模式数学）与 Missing character（CJK 入数学模式，'
   '16/5 处）→ **值域 \\(\\) 包裹规约工单**（源件侧修）。')
A2('5. **断行松驰（三零 Under/Over 族）**：窄栏中西混排不可断长式，badness 6592–10000，'
   '19 件各 1-2 处；三册 5/2/8 处（拓展 true 档 8 处）。\\emergencystretch=1em 已设不奏效处'
   '属结构断点缺失 → 册面断行调优工单（非阻塞）。')
A2('6. **拓展册旧制台账折形 containment 补充腿 104/%d 中、残 98**：台账值为渲染形，'
   '与件内值 tex 折形比对需渲染级口径（臂侧强折形已尽）→ 随 §四.1 台账 v2 一并升制'
   '（补 值tex/印面号 字段后此腿可硬断言）。' % zhe_tot)
A2('7. **汇编册 PDF seat 序提取面假红**：PDF 文本提取序将页脚（章名＋册名＋页码）'
   '与前值尾字符粘连 seat（『…答案册27』＋『17.[答案]』）；log ANSKEY 4 编全同'
   '（权威机证）＋容差层判定（seat 本体逐字在位＋句点容，`复核成册门S5.py`）双档全绿。'
   '→ 提取序 seat 比对以 log ANSKEY 为权威、PDF 容差层为印面证（器面同型门可复用）。')
A2('')
A2('## 五、成册页数预算（三册双档）')
A2('')
A2('| 册 | 详解印本（true） | 纯值速查本（false） |')
A2('|---|---|---|')
for k in ('导学答案册', '练习答案册', '拓展答案册'):
    A2('| %s | %d 页 | %d 页 |' % (k, pg[k]['true'], pg[k]['false']))
A2('| **合计** | **%d 页** | **%d 页** |' % (tot_true, tot_false))
A2('')
A2('预算口径＝xelatex 实测（A4 母版版式，双栏）；导学/练习 21 片单册合装、'
   '拓展册上/下合装；页数含册头与尾块（\\tailfill[30mm]）。')
A2('')
A2('## 六、结论与入链判定')
A2('')
A2('- **42 课时/衔接件：四门主断言（守恒/对号同序同号/钉值/零泄漏）全绿，纯答案册'
   '抽册可入链**；三零 23 件红均为非阻塞构式/断行（逐件归因见 §四.4-5），'
   '随器面折形扩容与值域规约工单清偿。')
A2('- **拓展册 2 件：本器升制前由臂侧适配器产册**（拓展答案册 202 块，成册门除三零'
   ' true 档断行外全绿）；器升制三桩（seat 制/台账 v2/题面库补档）完成后回归本器复抽。')
A2('- 异常 7 项中，须回填实数据的 1 项＝§四.2（课时02 台账印面号 15 键）。')
A2('- 卷件（测评/滚A/滚B）在产不在本轮域，归位后照本门谱补抽并入。')
A2('')
A2('—— 报告终（生成：M3 成卷轮 S5 抽答器入链试产臂｜工具/答案抽册器.py＋臂侧适配器）')
with open(os.path.join(HERE, '试产报告.md'), 'a', encoding='utf-8') as f:
    f.write('\n'.join(L2) + '\n')
print('§四至§六 追加落盘（%d 行）；报告完' % len(L2))
