# -*- coding: utf-8 -*-
"""②C_02_T6a_exec.py — T6a 正式执行（E0E0E0→F2F2F2，pPr 级）于 ②工具/副本 十件。
四道关：①exec 计数断言 vs ②工具对账.md §二基线 0/38/131/123/0/18/161/164/118/138
        ②幂等 dry 二跑全 0 改写 ③文本守恒（strict 逐段全等＋去空白归一化零差异＋
        非 document.xml 部件全等）④残留断言（十件 w:shd fill=E0E0E0 ＝0）
逐件超时重试兜底同步盘/杀软瞬锁。落 报告/②C_T6a_exec.md"""
import sys, io, os, re, time, subprocess, importlib.util, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
RPT = os.path.join(HERE, '报告', '②C_T6a_exec.md')
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
BASE_A = [0, 38, 131, 123, 0, 18, 161, 164, 118, 138]
SHORT = ['清单1', '衔接1(29)', '上(61)', '下(79)', '清单2', '衔接2(13)', '92', '90', '68', '89']


def run(args, tries=4, timeout=600):
    last = ''
    for att in range(1, tries + 1):
        try:
            p = subprocess.run(['python', TOOL] + args, capture_output=True, text=True,
                               encoding='utf-8', timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            last = 'timeout'; print('    timeout att%d' % att, flush=True); time.sleep(15); continue
        if p.returncode == 0 and 'Traceback' not in (p.stderr or ''):
            return p.stdout.strip()
        last = (p.stderr or '')[-300:]
        print('    fail att%d rc=%d %s' % (att, p.returncode, last), flush=True)
        time.sleep(15)
    return None


def count_e0(path):
    z = zipfile.ZipFile(path)
    try:
        doc = etree.fromstring(z.read('word/document.xml'))
    finally:
        z.close()
    n = 0
    for shd in doc.iter(G.q('shd')):
        if (shd.get(G.q('fill')) or '').upper() == 'E0E0E0':
            n += 1
    return n


rows = []
raws = []
allok = True
for i, n in enumerate(NAMES):
    f = os.path.join(DST, n)
    print('=== [%d/10] %s ===' % (i + 1, SHORT[i]), flush=True)
    pre = G.snap(f)
    e0_pre = count_e0(f)
    out = run([f, '--only', 'a'])
    if out is None:
        allok = False; rows.append((SHORT[i], n, 'RUNFAIL', BASE_A[i], '', '', '')); continue
    raws.append(out)
    m = re.search(r'a\) E0E0E0→F2F2F2：(\d+)\s*处（([^）]*)）', out)
    got = int(m.group(1)) if m else -1
    lvl = m.group(2) if m else '?'
    post = G.snap(f)
    cmp = G.compare(pre, post)
    out2 = run([f, '--only', 'a', '--dry-run'])
    m2 = re.search(r'a\) E0E0E0→F2F2F2：(\d+)\s*处', out2 or '')
    idem = int(m2.group(1)) if m2 else -1
    e0_post = count_e0(f)
    cnt_ok = (got == BASE_A[i])
    idem_ok = (idem == 0)
    cons_ok = cmp['strict'] and cmp['norm']
    res_ok = (e0_post == 0) and (e0_pre == BASE_A[i])
    ok = cnt_ok and idem_ok and cons_ok and res_ok and cmp['docxml_changed'] == (got > 0)
    allok = allok and ok
    print('  基线%d 实得%d %s｜幂等dry %d %s｜守恒 strict=%s norm=%s %s｜E0E0E0 %d→%d %s｜docxml改=%s'
          % (BASE_A[i], got, 'PASS' if cnt_ok else '!!FAIL', idem, 'PASS' if idem_ok else '!!FAIL',
             cmp['strict'], cmp['norm'], 'PASS' if cons_ok else '!!FAIL',
             e0_pre, e0_post, 'PASS' if res_ok else '!!FAIL', cmp['docxml_changed']), flush=True)
    for d in cmp['detail'][:5]:
        print('    !', d, flush=True)
    rows.append((SHORT[i], n, 'PASS' if ok else '!!FAIL', BASE_A[i], got, lvl, idem,
                 e0_pre, e0_post, cmp, cnt_ok, idem_ok, cons_ok, res_ok))

with open(RPT, 'w', encoding='utf-8') as fh:
    fh.write('# ②C T6a 正式执行报告 — E0E0E0→F2F2F2（pPr 级）\n\n')
    fh.write('- 时点：%s\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
    fh.write('- 工具：`工具\\底纹批量器.py --only a`（执行态自动留 `.bak_底纹批`）\n')
    fh.write('- 对象：`②工具\\副本\\` 十件（从同步盘 ②-B 回写终态重新复制，MD5 见 `②C_副本重置_MD5.md`）\n')
    fh.write('- 基线：`②工具对账.md` §二 T6a 行＝0／38／131／123／0／18／161／164／118／138 处（全 pPr 级）\n')
    fh.write('- 前置互斥证据：T3/T4 dry 十件 0 改写已复核（`②C_T3T4dry_前置复核.md`，20/20 PASS）\n\n')
    fh.write('## 一、四道关逐件结果\n\n')
    fh.write('| 件 | 基线 | 实得 | 计数断言 | 层级 | 幂等 dry | 文本守恒 strict/norm | E0E0E0 前→后 | 残留断言 | 判定 |\n')
    fh.write('|---|---|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        if r[2] == 'RUNFAIL':
            fh.write('| %s | %d | — | — | — | — | — | — | — | !!RUNFAIL |\n' % (r[0], r[3]))
            continue
        (sh, n, st, base, got, lvl, idem, e0a, e0b, cmp, c1, c2, c3, c4) = r
        fh.write('| %s | %d | %d | %s | %s | %d %s | %s／%s%s | %d→%d | %s | %s |\n' % (
            sh, base, got, 'PASS' if c1 else '**FAIL**', lvl or '—', idem,
            'PASS' if c2 else '**FAIL**', cmp['strict'], cmp['norm'],
            '' if c3 else ' **FAIL**', e0a, e0b, 'PASS' if c4 else '**FAIL**', st))
    fh.write('\n- 文本守恒口径：strict＝body 文档序逐段 w:t 串接字面全等；norm＝去空白（含全角空格/nbsp/零宽）归一化逐段零差异；')
    fh.write('另断非 `word/document.xml` 部件 MD5 全等（T6 只应改 document.xml）。\n')
    fh.write('- 残留断言：exec 后十件 `w:shd fill=E0E0E0` 计数＝0；exec 前计数＝基线（证副本起点＝②-B 回写态、底纹未被 ②-B 触动）。\n\n')
    fh.write('## 二、逐件工具原始输出\n\n')
    fh.write('\n'.join(raws) + '\n\n')
    fh.write('## 三、结论\n\n')
    fh.write('%s\n' % ('**十件全绿**：计数逐件恰等基线、幂等 dry 二跑全 0、文本守恒（strict＋norm）逐件零差异、'
                       'E0E0E0 残留 0、非 document.xml 部件零扰动。T6a 通过，可进 T6b。'
                       if allok else '**存在未通过项**，见上表 FAIL 标记，T6a 不得放行。'))
print('REPORT ->', RPT, flush=True)
print('SUMMARY allok=%s' % allok, flush=True)
