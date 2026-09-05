# -*- coding: utf-8 -*-
"""②D_R2_04_T7_exec.py — ②-D 重跑轮 T7（②-F 修复态＋T9 后基态；v2 迭代收敛版）。
v2 变更（FX-2，2026-09-05 清单2 断言失败根因修复后）：
  · 根因＝①第 1 页双栏区顶被头部单栏区压低（栏顶 dy≈66.6），工具固定阈 6pt 误判——工具已修
    （页感知栏顶判据，豁免节 dy 为第 1 页基准）；②前一分栏符回流可把原自然栏顶标题推离栏顶
    （清单2 2.2.2：313.5 界内 → 267.5），单轮 exec 计划不含它——exec 改为逐件迭代：
    exec→dry 复查，拟插符非零再 exec，至 dry 拟插符 0（≤4 轮，不收敛即停跑）。
  · 页数口径：T9 后基准读 报告/②D_R2_页数_T9后.txt（authoritative，早于任何 T7 插符）；
    闸门＝Σ(T7后−T9后) >+8 立即停跑按 LT-3 呈报。
0) 进程面复查。1) 测量面：T7 dry ×2 不动点＋结构计数硬对 T7_dry 基线；拟插符对派发基线差值记录。
2) exec 逐件迭代（序：衔接2→衔接1→清单1→上61→下79→清单2→92→90→68→89；已 exec 守卫＝bak 在且 dry 0）。
3) oMath 元素守恒终验（逐件＝②-F 锚）。
报告：报告/②D_R2_T7_dry_不动点.md、报告/②D_R2_T7_exec.md、报告/②D_R2_T7_oMath守恒.md"""
import sys, io, os, re, time, zipfile, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
RPT = os.path.join(HERE, '报告')
T7 = os.path.join(ROOT, '工具', '节标题栏顶器.py')
NAMES = [
    ('清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
    ('衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
    ('上61', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
    ('清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
    ('92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
    ('90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
    ('68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
]
BASE_SEC = {'清单1': 10, '衔接1': 2, '上61': 9, '下79': 1, '清单2': 20, '衔接2': 1, '92': 10, '90': 5, '68': 6, '89': 1}
BASE_EXEMPT = {'清单1': 1, '衔接1': 1, '上61': 1, '下79': 1, '清单2': 1, '衔接2': 1, '92': 1, '90': 1, '68': 1, '89': 1}
BASE_RIDE = {'清单1': 2, '衔接1': 0, '上61': 2, '下79': 0, '清单2': 3, '衔接2': 0, '92': 2, '90': 1, '68': 2, '89': 0}
DISPATCH_PLAN = {'清单1': 7, '衔接1': 1, '上61': 5, '下79': 0, '清单2': 15, '衔接2': 0, '92': 6, '90': 3, '68': 3, '89': 0}
OM_BASE = {'清单1': 396, '衔接1': 882, '上61': 3251, '下79': 2876, '清单2': 1156,
           '衔接2': 243, '92': 2705, '90': 2914, '68': 2359, '89': 4034}
T7_LINE = re.compile(r'节数 (\d+)｜已栏顶 (\d+)｜LT-4豁免 (\d+)｜随父 (\d+)｜拟插符 (\d+)｜当前页数 (\d+)')
EXEC_LINE = re.compile(r'执行：插符 (\d+)｜页数 (\d+)→\+(\d+)｜COM复核拟插标题栏顶 (\d+)/(\d+)')
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

def kill_winword_orphans():
    import psutil
    ws = [p for p in psutil.process_iter(['name', 'create_time'])
          if (p.info['name'] or '').upper() == 'WINWORD.EXE']
    for p in ws:
        try:
            p.kill()
            say('  杀 WINWORD 孤儿 pid%d' % p.pid)
        except Exception:
            pass
    return len(ws)

def run_tool(args, timeout):
    for att in range(1, 3):
        try:
            return subprocess.run(['python', T7] + args, capture_output=True, text=True,
                                  encoding='utf-8', timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            kill_winword_orphans()
            time.sleep(20)
    return None

def t9_pages():
    tab = {}
    with open(os.path.join(RPT, '②D_R2_页数_T9后.txt'), encoding='utf-8') as f:
        for ln in f:
            mm = re.search(r'^(人教B版选必1[^>]+) -> (\d+) pages', ln.strip())
            if mm:
                tab[mm.group(1)] = int(mm.group(2))
    return tab

say('=== 0) 进程面复查 ===')
say('  启动时 WINWORD 数 = %d' % kill_winword_orphans())
T9PG = t9_pages()
say('  T9后基准页数表：%s' % {k: v for k, v in list(T9PG.items())[:3]})

say('=== 1) 测量面：T7 dry ×2（全十件，不动点） ===')
dry1, dry2 = {}, {}
for run, bucket in ((1, dry1), (2, dry2)):
    for sh, n in NAMES:
        p = run_tool([os.path.join(DST, n), '--dry-run'], 600)
        m = T7_LINE.search(p.stdout) if p and p.returncode == 0 else None
        if not m:
            say('  !! dry%d %s 失败 %s' % (run, sh, (p.stderr[-200:] if p else 'timeout×2')))
            bucket[sh] = None
            continue
        bucket[sh] = tuple(int(x) for x in m.groups())
        say('  dry%d %-6s 节数%d 已栏顶%d 豁免%d 随父%d 拟插符%d 页数%d' % ((run, sh) + bucket[sh]))
ok_fix = all(dry1[sh] == dry2[sh] and dry1[sh] for sh, _ in NAMES)
say('  不动点（两轮全等）= %s' % ok_fix)
ok_struct = True
plan_dry = {}
for sh, _ in NAMES:
    if not dry1[sh]:
        ok_struct = False
        continue
    nsec, ntop, nex, nrd, nplan, pg = dry1[sh]
    plan_dry[sh] = nplan
    hits = (nsec == BASE_SEC[sh] and nex == BASE_EXEMPT[sh] and nrd == BASE_RIDE[sh])
    ok_struct = ok_struct and hits
    say('  %-6s 结构对平=%s 拟插符 %d（派发基线 %d，差 %+d）'
        % (sh, 'PASS' if hits else 'FAIL', nplan, DISPATCH_PLAN[sh], nplan - DISPATCH_PLAN[sh]))
say('  结构计数（节数/豁免/随父，版式无关）对 T7_dry 基线 = %s' % ok_struct)
with open(os.path.join(RPT, '②D_R2_T7_dry_不动点.md'), 'w', encoding='utf-8') as f:
    f.write('```text\n' + '\n'.join(OUT) + '\n```\n')
if not (ok_fix and ok_struct):
    say('!! 测量面未过——停止 exec')
    sys.exit(2)

say('=== 2) exec（逐件迭代至 dry 拟插符 0；闸门 Σ(T7后−T9后)>+8 停） ===')
EXEC_ORDER = ['衔接2', '衔接1', '清单1', '上61', '下79', '清单2', '92', '90', '68', '89']
by_name = dict(NAMES)
exec_rows = []
pages_post = {}
delta_total = 0
breach = False
aborted_at = None
for sh in EXEC_ORDER:
    n = by_name[sh]
    fp = os.path.join(DST, n)
    bak = fp + '.bak_栏顶'
    pg_t9 = T9PG[dict(NAMES)[sh]]
    if os.path.exists(bak):
        p = run_tool([fp, '--dry-run'], 600)
        m = T7_LINE.search(p.stdout) if p and p.returncode == 0 else None
        if m and int(m.group(5)) == 0:
            pages_post[sh] = int(m.group(6))
            d_pg = pages_post[sh] - pg_t9
            delta_total += d_pg
            exec_rows.append('%-6s 插符合计 0（dry 拟插 0，已 exec 态幂等重放）｜页数 %d→%d（%+d）｜累计 %+d'
                             % (sh, pg_t9, pages_post[sh], d_pg, delta_total))
            say('  ' + exec_rows[-1])
            continue
    n_ins_total = 0
    rounds = 0
    ok_file = True
    for it in range(1, 5):
        rounds = it
        p = run_tool([fp], 900)
        m = EXEC_LINE.search(p.stdout) if p and p.returncode == 0 else None
        if not m:
            say('  !! %s exec r%d 失败 %s' % (sh, it, (p.stderr[-200:] if p else 'timeout×2')))
            ok_file = False
            break
        n_ins, p_pre, p_delta, ok_n, all_n = map(int, m.groups())
        n_ins_total += n_ins
        say('  %s r%d 插符 %d 页数 %d→%d 栏顶 %d/%d' % (sh, it, n_ins, p_pre, p_pre + p_delta, ok_n, all_n))
        if not (ok_n == all_n):
            ok_file = False
            say('  !! %s r%d 栏顶复核未过——停跑' % (sh, it))
            break
        pd = run_tool([fp, '--dry-run'], 600)
        m2 = T7_LINE.search(pd.stdout) if pd and pd.returncode == 0 else None
        if m2 and int(m2.group(5)) == 0:
            pages_post[sh] = int(m2.group(6))
            break
        say('  %s r%d 后 dry 拟插符 %d——回流漂移，续迭代' % (sh, it, int(m2.group(5)) if m2 else -1))
    else:
        ok_file = False
        say('  !! %s 4 轮不收敛——停跑' % sh)
    if not ok_file:
        aborted_at = sh
        breach = True
        break
    d_pg = pages_post[sh] - pg_t9
    delta_total += d_pg
    line = '%-6s 插符合计 %d（dry 拟插 %d，%d 轮）｜页数 %d→%d（%+d）｜累计 %+d' % (
        sh, n_ins_total, plan_dry[sh], rounds, pg_t9, pages_post[sh], d_pg, delta_total)
    exec_rows.append(line)
    say('  ' + line)
    if delta_total > 8:
        breach = True
        aborted_at = sh
        say('  !! LT-3 硬闸门：全册页数实增 %+d > +8 ——立即停跑，余件不动' % delta_total)
        break

say('=== 3) oMath 元素守恒终验（T7 exec 后，逐件＝②-F 锚） ===')
om_rows = []
ok_om = True
for sh, n in NAMES:
    z = zipfile.ZipFile(os.path.join(DST, n))
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    c = sum(len(list(p.iter('{%s}oMath' % M))) for p in doc.iter('{%s}p' % W))
    hit = (c == OM_BASE[sh])
    ok_om = ok_om and hit
    om_rows.append('%-6s oMath=%5d 锚=%5d  %s' % (sh, c, OM_BASE[sh], 'PASS' if hit else '!!FAIL'))
    say('  ' + om_rows[-1])
    if not hit:
        say('  !! oMath 守恒破坏——立即停跑呈报')
        break
with open(os.path.join(RPT, '②D_R2_T7_oMath守恒.md'), 'w', encoding='utf-8') as f:
    f.write('# ②D 重跑轮 oMath 元素守恒（T7 exec 后；锚＝②-F 修复态基线）\n\n```text\n' + '\n'.join(om_rows) + '\n```\n')

say('=== 4) 汇总 ===')
say('页数实增（T7后−T9后）累计 = %+d（闸门 +8）；LT3_BREACH=%s；中断于=%s' % (delta_total, breach, aborted_at))
done_all = (aborted_at is None and not breach and ok_om)
say('SUMMARY fixpoint=%s struct=%s exec_done_all=%s oMath=%s delta=%+d' % (ok_fix, ok_struct, done_all, ok_om, delta_total))
with open(os.path.join(RPT, '②D_R2_T7_exec.md'), 'w', encoding='utf-8') as f:
    f.write('# ②D 重跑轮 T7 exec（v2 迭代收敛；断言面＝拟插标题栏顶率 100%×每轮；基态＝②-F 修复态＋T9 后）\n\n```text\n' + '\n'.join(exec_rows) + '\n```\n')
sys.exit(0 if done_all else 3)
