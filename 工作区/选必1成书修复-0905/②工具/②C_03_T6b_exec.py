# -*- coding: utf-8 -*-
"""②C_03_T6b_exec.py — T6b 正式执行（撤讲部/题型标题整行底纹 C6D4E3＋挂左竖条
single sz=18 space=3 color=auto）于 ②工具/副本 十件。
五道关：①exec 段数断言 vs ②工具对账.md §二基线 0/5/59/76/0/8/76/73/56/74
        ②ADC2DA 守恒（章/节标题底纹禁触）外部复核 前＝后
        ③竖条落地断言（pPr/pBdr/left val=single sz=18 space=3 color=auto 计数 前＋段数＝后）
          ＋C6D4E3 残留＝0 ＋跳过非标题＝0
        ④幂等 dry 二跑全 0 段 ⑤文本守恒（strict＋norm＋非 document.xml 部件全等）
落 报告/②C_T6b_exec.md"""
import sys, io, os, re, time, subprocess, importlib.util, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
RPT = os.path.join(HERE, '报告', '②C_T6b_exec.md')
TOOL = os.path.join(ROOT, '工具', '底纹批量器.py')

spec = importlib.util.spec_from_file_location('t6guard', os.path.join(HERE, '②C_文本守恒.py'))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)

NAMES = [
    '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
]
BASE_B = [0, 5, 59, 76, 0, 8, 76, 73, 56, 74]
SHORT = ['清单1', '衔接1(29)', '上(61)', '下(79)', '清单2', '衔接2(13)', '92', '90', '68', '89']


def run(args, tries=4, timeout=600):
    for att in range(1, tries + 1):
        try:
            p = subprocess.run(['python', TOOL] + args, capture_output=True, text=True,
                               encoding='utf-8', timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            print('    timeout att%d' % att, flush=True); time.sleep(15); continue
        if p.returncode == 0 and 'Traceback' not in (p.stderr or ''):
            return p.stdout.strip()
        print('    fail att%d rc=%d %s' % (att, p.returncode, (p.stderr or '')[-300:]), flush=True)
        time.sleep(15)
    return None


def probe(path):
    """返回 (C6D4E3段数, ADC2DA段数, 规格竖条段数, 非规格左框段数, 非规格左框属性组合分布)
    非规格左框＝源件既有的四边框条目段（top/left/bottom/right single sz=4 space=4 auto），
    与 T6b 无关、T6b 不触；断言口径为「前后不变」而非「＝0」。"""
    z = zipfile.ZipFile(path)
    try:
        doc = etree.fromstring(z.read('word/document.xml'))
    finally:
        z.close()
    c6 = adc = bar = barbad = 0
    badspec = {}
    for p in doc.iter(G.q('p')):
        ppr = p.find(G.q('pPr'))
        if ppr is None:
            continue
        sh = ppr.find(G.q('shd'))
        fl = (sh.get(G.q('fill')) or '').upper() if sh is not None else ''
        if fl == 'C6D4E3':
            c6 += 1
        elif fl == 'ADC2DA':
            adc += 1
        pb = ppr.find(G.q('pBdr'))
        if pb is not None:
            lf = pb.find(G.q('left'))
            if lf is not None:
                spec_ok = (lf.get(G.q('val')) == 'single' and lf.get(G.q('sz')) == '18'
                           and lf.get(G.q('space')) == '3' and lf.get(G.q('color')) == 'auto')
                if spec_ok:
                    bar += 1
                else:
                    barbad += 1
                    k = 'left %s/%s/%s/%s｜同级%s' % (
                        lf.get(G.q('val')), lf.get(G.q('sz')), lf.get(G.q('space')), lf.get(G.q('color')),
                        '+'.join(etree.QName(c).localname for c in pb))
                    badspec[k] = badspec.get(k, 0) + 1
    return c6, adc, bar, barbad, badspec


rows, raws = [], []
allok = True
for i, n in enumerate(NAMES):
    f = os.path.join(DST, n)
    print('=== [%d/10] %s ===' % (i + 1, SHORT[i]), flush=True)
    pre = G.snap(f)
    c6a, adca, bara, bada, badspeca = probe(f)
    out = run([f, '--only', 'b'])
    if out is None:
        allok = False; rows.append((SHORT[i], 'RUNFAIL', BASE_B[i])); continue
    raws.append(out)
    m = re.search(r'b\) 讲部/题型标题撤 C6D4E3＋挂左竖条：(\d+)\s*段（跳过非标题\s*(\d+)）；ADC2DA 守恒断言 (\w+)', out)
    got = int(m.group(1)) if m else -1
    skip = int(m.group(2)) if m else -1
    tooladc = m.group(3) if m else '?'
    post = G.snap(f)
    cmp = G.compare(pre, post)
    c6b, adcb, barb, badb, badspecb = probe(f)
    out2 = run([f, '--only', 'b', '--dry-run'])
    m2 = re.search(r'撤 C6D4E3＋挂左竖条：(\d+)\s*段（跳过非标题\s*(\d+)）', out2 or '')
    idem = int(m2.group(1)) if m2 else -1
    idem_skip = int(m2.group(2)) if m2 else -1

    c_cnt = (got == BASE_B[i]) and (c6a == BASE_B[i])
    c_adc = (adca == adcb) and tooladc == 'PASS'
    c_bar = (barb == bara + got) and (c6b == 0) and (skip == 0) and (badb == bada)
    c_idem = (idem == 0)
    c_cons = cmp['strict'] and cmp['norm']
    c_doc = (cmp['docxml_changed'] == (got > 0))
    ok = c_cnt and c_adc and c_bar and c_idem and c_cons and c_doc
    allok = allok and ok
    print('  基线%d 实得%d %s｜ADC2DA %d→%d(工具%s) %s｜规格竖条 %d→%d(应+%d) C6残留%d 跳过%d %s'
          % (BASE_B[i], got, 'PASS' if c_cnt else '!!FAIL', adca, adcb, tooladc,
             'PASS' if c_adc else '!!FAIL', bara, barb, got, c6b, skip,
             'PASS' if (barb == bara + got and c6b == 0 and skip == 0) else '!!FAIL'), flush=True)
    print('  既有非规格左框 %d→%d(应不变) %s｜幂等dry %d段(跳过%d) %s｜守恒 strict=%s norm=%s %s｜docxml改=%s %s'
          % (bada, badb, 'PASS' if badb == bada else '!!FAIL',
             idem, idem_skip, 'PASS' if c_idem else '!!FAIL', cmp['strict'], cmp['norm'],
             'PASS' if c_cons else '!!FAIL', cmp['docxml_changed'], 'PASS' if c_doc else '!!FAIL'), flush=True)
    for d in cmp['detail'][:5]:
        print('    !', d, flush=True)
    rows.append((SHORT[i], 'PASS' if ok else '!!FAIL', BASE_B[i], got, skip, adca, adcb, tooladc,
                 bara, barb, c6a, c6b, bada, badb, badspeca, idem, idem_skip, cmp,
                 c_cnt, c_adc, c_bar, c_idem, c_cons))

with open(RPT, 'w', encoding='utf-8') as fh:
    fh.write('# ②C T6b 正式执行报告 — 撤 C6D4E3＋挂左竖条（single sz=18 space=3 auto）\n\n')
    fh.write('- 时点：%s\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
    fh.write('- 工具：`工具\\底纹批量器.py --only b`\n')
    fh.write('- 对象：`②工具\\副本\\` 十件（T6a 已执行态；起点＝同步盘 ②-B 回写终态）\n')
    fh.write('- 基线：`②工具对账.md` §二 T6b 行＝0／5／59／76／0／8／76／73／56／74 段\n')
    fh.write('- 互斥纪律（②工具对账.md §四.3）：T3/T4 以 C6D4E3 识别题型标题，必须先于 T6b。'
             '②-B 已执行 T3/T4；本阶段执行前以 T3/T4 dry 复核十件 **0 改写**（20/20 PASS，'
             '证据 `②C_T3T4dry_前置复核.md`），证明识别口径未受 T6b 影响、无遗留工作面。\n\n')
    fh.write('## 一、五道关逐件结果\n\n')
    fh.write('| 件 | C6D4E3 前→后 | 撤＋挂段数（基线） | 计数断言 | 跳过非标题 | ADC2DA 前→后 | ADC2DA 守恒 | 规格左竖条 前→后 | 既有非规格左框 前→后 | 幂等 dry | 文本守恒 strict/norm | 判定 |\n')
    fh.write('|---|---|---|---|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        if r[1] == 'RUNFAIL':
            fh.write('| %s | — | —（基线%d） | — | — | — | — | — | — | — | — | !!RUNFAIL |\n' % (r[0], r[2]))
            continue
        (sh, st, base, got, skip, adca, adcb, tooladc, bara, barb, c6a, c6b,
         bada, badb, badspeca, idem, idem_skip, cmp, c1, c2, c3, c4, c5) = r
        fh.write('| %s | %d→%d | %d（%d） | %s | %d | %d→%d | %s（工具内断言 %s） | %d→%d（应＋%d）%s | %d→%d %s | %d 段（跳过 %d）%s | %s／%s %s | %s |\n' % (
            sh, c6a, c6b, got, base, 'PASS' if c1 else '**FAIL**', skip, adca, adcb,
            'PASS' if c2 else '**FAIL**', tooladc, bara, barb, got,
            'PASS' if barb == bara + got else '**FAIL**', bada, badb,
            'PASS' if badb == bada else '**FAIL**',
            idem, idem_skip, 'PASS' if c4 else '**FAIL**', cmp['strict'], cmp['norm'],
            'PASS' if c5 else '**FAIL**', st))
    fh.write('\n### 断言口径说明\n\n')
    fh.write('- **规格左竖条**＝`w:pPr/w:pBdr/w:left` 四属性恰为 `val=single`、`sz=18`（＝2.25pt）、`space=3`、`color=auto`；'
             '断言「后＝前＋本件撤底纹段数」且「C6D4E3 残留＝0」「跳过非标题＝0」。\n')
    fh.write('- **既有非规格左框**＝源件原有的四边框条目段（`w:pBdr` 四边 top/left/bottom/right 全为 `single sz=4 space=4 auto`，'
             '清单/讲部条目族），与 T6b 无关；断言口径为「前后计数不变」（T6b 不触），非「＝0」。逐件属性组合分布见下节。\n')
    fh.write('- **ADC2DA 守恒**＝章/节标题整行底纹禁触（②工具对账.md §四.3、附则\\讲练件底纹减法.md 保留清单）：'
             '本脚本外部计数前＝后，与工具内部 `assert adc_pre == adc_post` 双证。\n')
    fh.write('- **文本守恒**＝strict（body 文档序逐段 `w:t` 串接字面全等）＋norm（去空白含全角空格/nbsp/零宽归一化逐段零差异）'
             '＋非 `word/document.xml` 部件 MD5 全等（T6 只应改 document.xml）。\n')
    fh.write('- **docxml 指纹**＝改动件数应恰为「段数＞0」的件数（0 段件不得被重写）。\n\n')
    fh.write('### 既有非规格左框属性组合分布（逐件，前后一致）\n\n')
    for r in rows:
        if r[1] == 'RUNFAIL':
            continue
        fh.write('- %s：%s\n' % (r[0], '；'.join('%s ×%d' % kv for kv in sorted(r[14].items())) or '无'))
    fh.write('\n## 二、逐件工具原始输出\n\n')
    fh.write('\n'.join(raws) + '\n\n')
    fh.write('## 三、结论\n\n')
    fh.write('%s\n' % ('**十件全绿**：撤＋挂段数逐件恰等基线（C6D4E3 前计数亦逐件恰等基线）、跳过非标题 0、'
                       'ADC2DA 逐件守恒（内外双证）、规格左竖条数＝前值＋撤底纹段数、C6D4E3 残留 0、'
                       '既有非规格左框前后不变（零误触）、幂等 dry 二跑全 0 段、文本守恒 strict＋norm 零差异、'
                       '非 document.xml 部件零扰动。T6b 通过，可进 T6c。'
                       if allok else '**存在未通过项**，见上表 FAIL 标记，T6b 不得放行。'))
print('REPORT ->', RPT, flush=True)
print('SUMMARY allok=%s' % allok, flush=True)
