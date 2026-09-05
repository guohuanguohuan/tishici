# -*- coding: utf-8 -*-
"""②D_00_净场重置.py — ②-D 前置：FX-6 净场四查＋副本重置＋②-C 终态锚核验＋链路面冒烟。
①进程面：WINWORD/python 进程清点（孤儿处置仅在超时范式内杀新生 WINWORD，用户进程禁杀）。
②文件面：同步盘与 ②工具/副本 无 ~$ 锁残留；副本可写试探。
③锚核验：同步盘十件 MD5 == ②C_终报 §四 留档值（②-C 终态锚）。
④副本重置：同步盘 → ②工具/副本 十件（逐件 8 试×退避 6s 抗 Resilio/RealTimeSync 瞬锁），MD5 逐件一致。
⑤链路面冒烟：T9 dry 衔接2（zip 级，计数对照 dry 基线）＋ T7 dry 衔接2（COM 级最小件）。
报告：报告/②D_00_净场重置.md"""
import sys, io, os, time, hashlib, shutil, subprocess, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SYNC = os.path.join(ROOT, '高中数学', '高中数学同步')
BASE = os.path.join(ROOT, '工作区', '选必1成书修复-0905', '②工具')
DST = os.path.join(BASE, '副本')
RPTDIR = os.path.join(BASE, '报告')
T9 = os.path.join(ROOT, '工具', '跨行保护器.py')
T7 = os.path.join(ROOT, '工具', '节标题栏顶器.py')

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
SHORT = ['清单1', '衔接1(29)', '上61', '下79', '清单2', '衔接2(13)', '92', '90', '68', '89']

# ②C_终报 §四 留档 MD5（副本＝同步盘，②-C 终态）
ANCHOR = {
    '清单1': '13274dec8bd11de25cc0639b6336ade3',
    '衔接1(29)': 'b25c641594d857670d4a3fcd201417a5',
    '上61': '9c3e65d306ae2bab31ccacc5d2fd5d0b',
    '下79': 'f8ec78be1545e06935218469221e9390',
    '清单2': 'bca6fd1c65c4c4a424489336ddd6bb1b',
    '衔接2(13)': 'c41a8717d9eddf6216d767c1120ecee8',
    '92': 'cfcf5b91d20d24bc5e0692a30787fa27',
    '90': '1fcadf33fa47554d996d7df34804d31a',
    '68': '1a29171ca60c7df88f2544a9666d36e3',
    '89': 'cc6229b384b056c9d48af808cecdd778',
}
# T9 dry 基线（②工具对账 §二 / T9_dry.md）：衔接2 = 芯片52｜节1/讲部0/题型8｜短64｜长5
SMOKE_T9 = dict(chip=52, sec=1, lect=0, grp=8, short=64, long=5)


def md5(p, tries=6):
    for _ in range(tries):
        try:
            h = hashlib.md5()
            with open(p, 'rb') as f:
                for chunk in iter(lambda: f.read(1 << 20), b''):
                    h.update(chunk)
            return h.hexdigest()
        except PermissionError:
            time.sleep(5)
    return 'LOCKED'


LOG = []
def say(msg):
    print(msg, flush=True)
    LOG.append(msg)


say('=== ① 进程面（FX-6-1） ===')
import psutil
procs = [(p.pid, p.info['name']) for p in psutil.process_iter(['name'])
         if (p.info['name'] or '').upper() in ('WINWORD.EXE', 'PYTHON.EXE', 'PYTHONW.EXE')]
say('  WINWORD/python 进程数 = %d %s' % (len(procs), procs if procs else '（净）'))
sync_cli = [(p.pid, p.info['name']) for p in psutil.process_iter(['name'])
            if 'Resilio' in (p.info['name'] or '') or 'RealTimeSync' in (p.info['name'] or '')]
say('  同步客户端（用户进程，禁杀）：' + ('; '.join('%s(pid%d)' % (n, pid) for pid, n in sync_cli) or '无'))

say('=== ② 文件面（FX-6-2） ===')
lock_hits = []
for d in (SYNC, DST):
    if os.path.isdir(d):
        for fn in os.listdir(d):
            if fn.startswith('~$'):
                lock_hits.append(os.path.join(d, fn))
say('  ~$ 锁残留 = %d %s' % (len(lock_hits), lock_hits if lock_hits else '（净）'))
try:
    tptest = os.path.join(DST, '~$②D_可写试探.tmp')
    with open(tptest, 'w') as f:
        f.write('t')
    os.remove(tptest)
    say('  副本可写试探 PASS')
    ok_write = True
except Exception as e:
    say('  副本可写试探 FAIL: %s' % e)
    ok_write = False

say('=== ③ 同步盘 MD5 对 ②C_终报§四 锚核验 ===')
ok_anchor = True
for n, sh in zip(NAMES, SHORT):
    m = md5(os.path.join(SYNC, n))
    hit = (m == ANCHOR[sh])
    ok_anchor = ok_anchor and hit
    say('  %-10s %s %s' % (sh, m, 'PASS' if hit else '!!FAIL(锚=%s)' % ANCHOR[sh]))

say('=== ④ 副本重置（同步盘 → ②工具/副本） ===')
ok_copy = True
md5_rows = []
for n, sh in zip(NAMES, SHORT):
    s, d = os.path.join(SYNC, n), os.path.join(DST, n)
    done = False
    for att in range(1, 9):
        try:
            if os.path.exists(d):
                os.remove(d)
            shutil.copy2(s, d)
            done = True
            break
        except PermissionError as e:
            say('   %s att%d 瞬锁退避: %s' % (sh, att, str(e)[:60]))
            time.sleep(6)
    if not done:
        ok_copy = False
        say('  !! %s 复制失败' % sh)
        continue
    ms, md_ = md5(s), md5(d)
    same = (ms == md_ == ANCHOR[sh])
    ok_copy = ok_copy and same
    md5_rows.append((sh, os.path.getsize(d), md_, 'PASS' if same else 'FAIL'))
    say('  %-10s %s  src=%s dst=%s %s' % (sh, os.path.getsize(d), ms[:12], md_[:12], 'PASS' if same else '!!FAIL'))

say('=== ⑤ 链路面冒烟（FX-6-3） ===')
T9_LINE = re.compile(r'a\) 芯片插WJ (\d+) 处（幂等 (\d+)）｜b\) 标题keepLines 新挂 (\d+)（节(\d+)/讲部(\d+)/题型(\d+)，幂等 (\d+)）｜'
                     r'c\) oMath短段keepLines 新挂 (\d+)（幂等 (\d+)；长段 (\d+) 登记不挂）')
T7_LINE = re.compile(r'节数 (\d+)｜已栏顶 (\d+)｜LT-4豁免 (\d+)｜随父 (\d+)｜拟插符 (\d+)｜当前页数 (\d+)')
xj2 = os.path.join(DST, NAMES[5])
ok_smoke = True
p = subprocess.run(['python', T9, xj2, '--dry-run'], capture_output=True, text=True,
                   encoding='utf-8', timeout=120, cwd=ROOT)
m = T9_LINE.search(p.stdout)
if p.returncode == 0 and m:
    chip, _, nb, sec, lect, grp, _, nc, _, lng = map(int, m.groups())
    hit = (chip, sec, lect, grp, nc, lng) == (SMOKE_T9['chip'], SMOKE_T9['sec'], SMOKE_T9['lect'],
                                              SMOKE_T9['grp'], SMOKE_T9['short'], SMOKE_T9['long'])
    ok_smoke = ok_smoke and hit
    say('  T9 dry 衔接2: 芯片%d 节%d/讲部%d/题型%d 短%d 长%d %s'
        % (chip, sec, lect, grp, nc, lng, 'PASS(对平dry基线)' if hit else '!!FAIL'))
else:
    ok_smoke = False
    say('  !! T9 dry 衔接2 冒烟失败 exit=%d %s' % (p.returncode, p.stderr[-200:]))
t0 = time.time()
p = subprocess.run(['python', T7, xj2, '--dry-run'], capture_output=True, text=True,
                   encoding='utf-8', timeout=300, cwd=ROOT)
m = T7_LINE.search(p.stdout)
if p.returncode == 0 and m:
    nsec, ntop, nex, nrd, nplan, pg = map(int, m.groups())
    hit = (nsec, nex, nplan) == (1, 1, 0) and pg >= 5
    ok_smoke = ok_smoke and hit
    say('  T7 dry 衔接2: 节数%d 已栏顶%d 豁免%d 随父%d 拟插符%d 页数%d %.0fs %s'
        % (nsec, ntop, nex, nrd, nplan, pg, time.time() - t0, 'PASS' if hit else '!!FAIL'))
else:
    ok_smoke = False
    say('  !! T7 dry 衔接2 冒烟失败 exit=%d %s' % (p.returncode, p.stderr[-300:]))

ALLOK = ok_write and (len(lock_hits) == 0) and ok_anchor and ok_copy and ok_smoke
out = os.path.join(RPTDIR, '②D_00_净场重置.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('# ②D 净场＋重置（FX-6）— %s\n\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
    f.write('```text\n' + '\n'.join(LOG) + '\n```\n\n')
    f.write('| 件 | 字节 | 副本MD5（=同步盘=②C锚） | 判定 |\n|---|---|---|---|\n')
    for sh, sz, m_, st in md5_rows:
        f.write('| %s | %d | %s | %s |\n' % (sh, sz, m_, st))
    f.write('\n结论：**%s**\n' % ('净场四查全绿＋重置十件 MD5 对 ②C_终报§四 逐件 PASS' if ALLOK else '存在 FAIL 项，见上——禁止放量'))
say('=== 报告落盘: %s ===' % out)
say('SUMMARY ALLOK=%s (write=%s lock=%d anchor=%s copy=%s smoke=%s)'
    % (ALLOK, ok_write, len(lock_hits), ok_anchor, ok_copy, ok_smoke))
sys.exit(0 if ALLOK else 2)
