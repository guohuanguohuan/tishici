# -*- coding: utf-8 -*-
"""②D_04_T7_exec.py — T7 节标题栏顶器（修复后）dry×2 不动点 ＋ 逐件 exec（+8 页硬闸门）。
0) 进程面复查（WINWORD 新生孤儿即杀——本轮脚本自产，FX-4 授权面内）。
1) 测量面：T7 dry 连跑两次全十件，不动点（两轮逐件 节数/已栏顶/豁免/随父/拟插符/页数 全等）；
   结构计数对 T7_dry 基线（节数 10/2/9/1/20/1/10/5/6/1、豁免各1、随父 2/0/2/0/3/0/2/1/2/0）；
   拟插符对派发基线 7/1/5/0/15/0/6/3/3/0（差值记录——T7_dry 系②-A 前旧版式所登，随 T5/T3/T9 重排漂移属预期）。
2) exec 逐件（序：衔接2冒烟→衔接1→清单1→上61→下79→清单2→92→90→68→89）：
   记录 插符数/页数前(T9后)→页数后(T7后)/栏顶率断言；累计页数增量 >+8 立即停跑按 LT-3 呈报。
   已 exec 守卫：.bak_栏顶 在 且 dry 拟插符 0 → 幂等重放跳过（下79/89/衔接2 天然拟插 0 无 bak，可重跑）。
报告：报告/②D_T7_dry_不动点.md、报告/②D_T7_exec.md"""
import sys, io, os, re, time, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
# 结构基线（版式无关）：节数 / 豁免 / 随父（T7_dry.md 登记值）
BASE_SEC = {'清单1': 10, '衔接1': 2, '上61': 9, '下79': 1, '清单2': 20, '衔接2': 1, '92': 10, '90': 5, '68': 6, '89': 1}
BASE_EXEMPT = {'清单1': 1, '衔接1': 1, '上61': 1, '下79': 1, '清单2': 1, '衔接2': 1, '92': 1, '90': 1, '68': 1, '89': 1}
BASE_RIDE = {'清单1': 2, '衔接1': 0, '上61': 2, '下79': 0, '清单2': 3, '衔接2': 0, '92': 2, '90': 1, '68': 2, '89': 0}
# 派发基线：拟插符（②-A 前旧版式，diff 记录不硬卡）
DISPATCH_PLAN = {'清单1': 7, '衔接1': 1, '上61': 5, '下79': 0, '清单2': 15, '衔接2': 0, '92': 6, '90': 3, '68': 3, '89': 0}
T7_LINE = re.compile(r'节数 (\d+)｜已栏顶 (\d+)｜LT-4豁免 (\d+)｜随父 (\d+)｜拟插符 (\d+)｜当前页数 (\d+)')
EXEC_LINE = re.compile(r'执行：插符 (\d+)｜页数 (\d+)→\+(\d+)｜COM复核拟插标题栏顶 (\d+)/(\d+)')

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

say('=== 0) 进程面复查 ===')
n0 = kill_winword_orphans()
say('  启动时 WINWORD 数 = %d' % n0)

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
    d = nplan - DISPATCH_PLAN[sh]
    say('  %-6s 结构对平=%s 拟插符 %d（派发基线 %d，差 %+d）'
        % (sh, 'PASS' if hits else 'FAIL', nplan, DISPATCH_PLAN[sh], d))
say('  结构计数（节数/豁免/随父，版式无关）对 T7_dry 基线 = %s' % ok_struct)
if not (ok_fix and ok_struct):
    say('!! 测量面未过——停止 exec')
    with open(os.path.join(RPT, '②D_T7_dry_不动点.md'), 'w', encoding='utf-8') as f:
        f.write('```text\n' + '\n'.join(OUT) + '\n```\n')
    sys.exit(2)

say('=== 2) exec（逐件，+8 页硬闸门） ===')
EXEC_ORDER = ['衔接2', '衔接1', '清单1', '上61', '下79', '清单2', '92', '90', '68', '89']
by_name = dict(NAMES)
exec_rows = []
pages_pre = {}
pages_post = {}
delta_total = 0
breach = False
aborted_at = None
for sh in EXEC_ORDER:
    n = by_name[sh]
    fp = os.path.join(DST, n)
    bak = fp + '.bak_栏顶'
    pre_pages = dry1[sh][5]
    if os.path.exists(bak):
        p = run_tool([fp, '--dry-run'], 600)
        m = T7_LINE.search(p.stdout) if p and p.returncode == 0 else None
        if m and int(m.group(5)) == 0:
            pages_pre[sh] = pages_post[sh] = int(m.group(6))
            exec_rows.append('%-6s 已 exec 态（bak_栏顶 在且拟插符0）→ 幂等重放跳过；页数 %d'
                             % (sh, int(m.group(6))))
            say('  ' + exec_rows[-1])
            continue
    p = run_tool([fp], 900)
    m = EXEC_LINE.search(p.stdout) if p and p.returncode == 0 else None
    if not m:
        say('  !! %s exec 失败 %s' % (sh, (p.stderr[-300:] if p else 'timeout×2')))
        aborted_at = sh
        breach = True
        break
    n_ins, p_pre, p_delta, ok_n, all_n = map(int, m.groups())
    pages_pre[sh], pages_post[sh] = p_pre, p_pre + p_delta
    delta_total += p_delta
    line = '%-6s 插符 %d（dry 拟插 %d）｜页数 %d→%d（%+d）｜栏顶 %d/%d %s｜累计 %+d' % (
        sh, n_ins, plan_dry[sh], p_pre, p_pre + p_delta, p_delta, ok_n, all_n,
        'PASS' if (ok_n == all_n and n_ins == plan_dry[sh]) else 'FAIL', delta_total)
    exec_rows.append(line)
    say('  ' + line)
    if not (ok_n == all_n and n_ins == plan_dry[sh]):
        aborted_at = sh
        breach = True
        say('  !! %s 断言未过——停跑' % sh)
        break
    if delta_total > 8:
        breach = True
        aborted_at = sh
        say('  !! LT-3 硬闸门：全册页数实增 %+d > +8 ——立即停跑，余件不动' % delta_total)
        break
say('=== 3) 汇总 ===')
say('页数实增（T7后−T9后）累计 = %+d（闸门 +8）；LT3_BREACH=%s；中断于=%s' % (delta_total, breach, aborted_at))
done_all = (aborted_at is None and not breach)
say('SUMMARY fixpoint=%s struct=%s exec_done_all=%s delta=%+d' % (ok_fix, ok_struct, done_all, delta_total))
with open(os.path.join(RPT, '②D_T7_exec.md'), 'w', encoding='utf-8') as f:
    f.write('# ②D T7 exec（修复后工具；断言面＝拟插标题栏顶率 100%）\n\n```text\n' + '\n'.join(exec_rows) + '\n```\n')
sys.exit(0 if done_all else 3)
