# -*- coding: utf-8 -*-
"""②D_R2_07_幂等终验.py — 副本终态（T9+T7 后）四工具面幂等终验＋MD5 落盘。
T9 dry ×2（a/b/c 新挂全零，XML 面快）＋ T7 dry ×2（拟插符全零、两轮（拟插,页数）全等，COM 面）
＋十件 MD5（副本终态，未回写——LT-3 停在回写前）。
报告：报告/②D_R2_幂等终验.md、报告/②D_R2_MD5_副本终态.md"""
import sys, io, os, re, time, hashlib, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
RPT = os.path.join(HERE, '报告')
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
SHORT = ['清单1', '衔接1', '上61', '下79', '清单2', '衔接2', '92', '90', '68', '89']
T9_LINE = re.compile(r'a\) 芯片插WJ (\d+) 处（幂等 (\d+)）｜b\) 标题keepLines 新挂 (\d+)（节(\d+)/讲部(\d+)/题型(\d+)，幂等 (\d+)）｜'
                     r'c\) oMath短段keepLines 新挂 (\d+)（幂等 (\d+)；长段 (\d+) 登记不挂）')
T7_LINE = re.compile(r'节数 (\d+)｜已栏顶 (\d+)｜LT-4豁免 (\d+)｜随父 (\d+)｜拟插符 (\d+)｜当前页数 (\d+)')

OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

def kill_newest_winword():
    try:
        import psutil
        ws = [p for p in psutil.process_iter(['name', 'create_time'])
              if (p.info['name'] or '').upper() == 'WINWORD.EXE']
        ws.sort(key=lambda x: x.info['create_time'], reverse=True)
        if ws:
            ws[0].kill()
            say('   杀 WINWORD 孤儿 pid%d' % ws[0].pid)
    except Exception as e:
        say('   kill fail %s' % e)

def run_tool(tool, args, timeout):
    for att in range(1, 3):
        try:
            return subprocess.run(['python', tool] + args, capture_output=True, text=True,
                                  encoding='utf-8', timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            kill_newest_winword()
            time.sleep(20)
    return None

ok = True
say('=== T9 dry ×2（副本终态，a/b/c 新挂须全零） ===')
for run in (1, 2):
    z = True
    for sh, n in zip(SHORT, NAMES):
        p = run_tool(T9, [os.path.join(DST, n), '--dry-run'], 180)
        m = T9_LINE.search(p.stdout) if p and p.returncode == 0 else None
        if not m:
            z = False
            say('  !! T9 dry%d %s 失败' % (run, sh))
            continue
        chip, ida, nb, s1, l1, g1, idb, nc, idc, lng = map(int, m.groups())
        if not (chip == 0 and nb == 0 and nc == 0):
            z = False
            say('  !! T9 dry%d %s 新挂非零 a%d b%d c%d' % (run, sh, chip, nb, nc))
    say('  T9 dry%d 十件新挂全零 = %s' % (run, z))
    ok = ok and z

say('=== T7 dry ×2（副本终态，拟插符须全零且两轮全等） ===')
t7_rows = []
for run in (1, 2):
    z = True
    for sh, n in zip(SHORT, NAMES):
        p = run_tool(T7, [os.path.join(DST, n), '--dry-run'], 600)
        m = T7_LINE.search(p.stdout) if p and p.returncode == 0 else None
        if not m:
            z = False
            say('  !! T7 dry%d %s 失败' % (run, sh))
            continue
        nsec, ntop, nex, nrd, nplan, pg = map(int, m.groups())
        t7_rows.append((run, sh, nplan, pg))
        if nplan != 0:
            z = False
            say('  !! T7 dry%d %s 拟插符 %d 非零' % (run, sh, nplan))
    say('  T7 dry%d 十件拟插符全零 = %s' % (run, z))
    ok = ok and z
same2 = len(t7_rows) == 20 and all((t7_rows[i][2], t7_rows[i][3]) == (t7_rows[i + 10][2], t7_rows[i + 10][3]) for i in range(10))
say('  T7 dry 两轮（拟插符,页数）全等 = %s' % same2)
ok = ok and same2

say('=== 副本终态 MD5（十件；未回写） ===')
md5_rows = []
for sh, n in zip(SHORT, NAMES):
    h = hashlib.md5()
    with open(os.path.join(DST, n), 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    md5_rows.append('| %s | %s |' % (sh, h.hexdigest()))
    say('  %-6s %s' % (sh, h.hexdigest()))
with open(os.path.join(RPT, '②D_R2_MD5_副本终态.md'), 'w', encoding='utf-8') as f:
    f.write('# ②D 重跑轮 副本终态 MD5（＝②-F 修复态＋T9＋T7；LT-3 停在回写前，未写同步盘）\n\n'
            '| 件 | MD5 |\n|---|---|\n' + '\n'.join(md5_rows) + '\n')
say('=== 汇总 ===')
say('SUMMARY IDEMPOTENT=%s' % ok)
with open(os.path.join(RPT, '②D_R2_幂等终验.md'), 'w', encoding='utf-8') as f:
    f.write('```text\n' + '\n'.join(OUT) + '\n```\n')
sys.exit(0 if ok else 2)
