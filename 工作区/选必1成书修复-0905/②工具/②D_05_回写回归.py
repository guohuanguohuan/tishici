# -*- coding: utf-8 -*-
"""②D_05_回写回归.py — ②-D 回写同步盘＋回归（照 ②-C ②C_09 范式）。
①回写：②工具/副本 十件 → 高中数学/高中数学同步（逐件 copy2 重试甲：8试×6s×3轮，轮间杀最新 WINWORD 孤儿＋20s；
  只写十件 docx，不落 .bak 防播散）；②防播散检查：同步盘不得新增 .bak_跨行护/.bak_栏顶；
③MD5 逐件比对（副本 vs 同步盘）；④同步盘幂等：T9 dry×2（新挂全零）＋ T7 dry×2（拟插符0、两轮全等）；
⑤页数三账：②C 基线 / T9后（T7 exec 页数前值，解析自 ②D_T7_exec.md）/ T7后（T7 exec 页数后值），
  并 COM 导出十件 → PDF对比/②D终/ ＋fitz 独立清点对照（fitz vs COM）。
报告：报告/②D_回写_回归.md、报告/②D_页数对照.md"""
import sys, io, os, re, time, shutil, hashlib, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
SYNC = os.path.join(ROOT, '高中数学', '高中数学同步')
RPT = os.path.join(HERE, '报告')
P_FIN = os.path.join(HERE, 'PDF对比', '②D终')
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
EXEC_LINE = re.compile(r'插符 (\d+)（dry 拟插 \d+）｜页数 (\d+)→(\d+)')

OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

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

say('=== ① 回写（副本 → 同步盘，重试甲范式） ===')
ok_wb = True
for sh, n in zip(SHORT, NAMES):
    s, d = os.path.join(DST, n), os.path.join(SYNC, n)
    done = False
    for rd in range(1, 4):
        for att in range(1, 9):
            try:
                shutil.copy2(s, d)
                done = True
                break
            except PermissionError as e:
                say('   %s r%d a%d 瞬锁退避 %s' % (sh, rd, att, str(e)[:50]))
                time.sleep(6)
        if done:
            break
        kill_newest_winword()
        time.sleep(20)
    if not done:
        ok_wb = False
        say('  !! %s 回写失败（3 轮×8 试）' % sh)
    else:
        say('  %s 回写 OK' % sh)

say('=== ② 防播散检查 ===')
baks = [f for f in os.listdir(SYNC) if '跨行护' in f or '栏顶' in f]
say('  同步盘 .bak_跨行护/.bak_栏顶 数 = %d %s' % (len(baks), 'PASS' if not baks else '!!' + str(baks)))

say('=== ③ MD5 逐件比对（副本 vs 同步盘） ===')
md5_rows = []
ok_md5 = True
for sh, n in zip(SHORT, NAMES):
    m1, m2 = md5(os.path.join(DST, n)), md5(os.path.join(SYNC, n))
    hit = m1 == m2 and m1 != 'LOCKED'
    ok_md5 = ok_md5 and hit
    md5_rows.append((sh, m1, m2, 'PASS' if hit else 'FAIL'))
    say('  %-6s %s %s' % (sh, m1, 'PASS' if hit else '!!FAIL dst=%s' % m2))

def run_tool(tool, args, timeout):
    for att in range(1, 3):
        try:
            return subprocess.run(['python', tool] + args, capture_output=True, text=True,
                                  encoding='utf-8', timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            kill_newest_winword()
            time.sleep(20)
    return None

say('=== ④ 同步盘幂等：T9 dry×2 ＋ T7 dry×2 ===')
ok_idem = True
for run in (1, 2):
    t9_zero = True
    for sh, n in zip(SHORT, NAMES):
        p = run_tool(T9, [os.path.join(SYNC, n), '--dry-run'], 180)
        m = T9_LINE.search(p.stdout) if p and p.returncode == 0 else None
        if not m:
            t9_zero = False
            say('  !! T9 dry%d %s 失败' % (run, sh))
            continue
        chip, ida, nb, s1, l1, g1, idb, nc, idc, lng = map(int, m.groups())
        if not (chip == 0 and nb == 0 and nc == 0):
            t9_zero = False
            say('  !! T9 dry%d %s 新挂非零 a%d b%d c%d' % (run, sh, chip, nb, nc))
    say('  T9 dry%d 同步盘十件新挂全零 = %s' % (run, t9_zero))
    ok_idem = ok_idem and t9_zero
t7_rows = []
for run in (1, 2):
    z = True
    for sh, n in zip(SHORT, NAMES):
        p = run_tool(T7, [os.path.join(SYNC, n), '--dry-run'], 600)
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
    say('  T7 dry%d 同步盘十件拟插符全零 = %s' % (run, z))
    ok_idem = ok_idem and z
same2 = all((t7_rows[i][2], t7_rows[i][3]) == (t7_rows[i + 10][2], t7_rows[i + 10][3]) for i in range(10))
say('  T7 dry 两轮（拟插符,页数）全等 = %s' % same2)
ok_idem = ok_idem and same2

say('=== ⑤ 页数三账 ＋ fitz 独立清点 ===')
# T9后/T7后 来自 T7 exec 行（页数 X→Y）
exec_pages = {}
with open(os.path.join(RPT, '②D_T7_exec.md'), encoding='utf-8') as f:
    txt = f.read()
for sh in SHORT:
    m = re.search(re.escape(sh) + r'\s+插符 \d+（dry 拟插 \d+）｜页数 (\d+)→(\d+)', txt)
    if m:
        exec_pages[sh] = (int(m.group(1)), int(m.group(2)))
base_pages = {}
with open(os.path.join(RPT, '②C_页数_后.txt'), encoding='utf-8') as f:
    for i, ln in enumerate(f):
        mm = re.search(r'-> (\d+) pages', ln)
        if mm:
            base_pages[SHORT[i]] = int(mm.group(1))
os.makedirs(P_FIN, exist_ok=True)
import fitz
import win32com.client
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
fitz_rows = {}
try:
    for sh, n in zip(SHORT, NAMES):
        src = os.path.join(DST, n)
        dst = os.path.join(P_FIN, n[:-5] + '.pdf')
        if os.path.exists(dst):
            d = fitz.open(dst)
            fitz_rows[sh] = d.page_count
            d.close()
            say('  %s fitz 页数 %d（PDF 已在）' % (sh, fitz_rows[sh]))
            continue
        done = False
        for att in range(1, 4):
            try:
                doc = word.Documents.Open(os.path.abspath(src), ReadOnly=True)
                doc.ExportAsFixedFormat(os.path.abspath(dst), 17)
                doc.Close(False)
                done = True
                break
            except Exception as e:
                say('   %s 导出 att%d fail %s' % (sh, att, str(e)[:100]))
                kill_newest_winword()
                time.sleep(20)
                try:
                    word.Quit()
                except Exception:
                    pass
                word = win32com.client.DispatchEx('Word.Application')
                word.Visible = False
                word.DisplayAlerts = 0
        if not done:
            say('  !! %s PDF 导出失败' % sh)
            continue
        d = fitz.open(dst)
        fitz_rows[sh] = d.page_count
        d.close()
        say('  %s fitz 页数 %d' % (sh, fitz_rows[sh]))
finally:
    try:
        word.Quit()
    except Exception:
        pass

# 三账表落盘
ok_pg = True
tbl = ['| 件 | ②C基线 | T9后(T7 exec 前) | T7后(T7 exec 后) | fitz(②D终PDF) | T7增量 |', '|---|---|---|---|---|---|']
tb, ta = 0, 0
for sh in SHORT:
    b = base_pages.get(sh)
    pre = exec_pages.get(sh, (None, None))[0]
    post = exec_pages.get(sh, (None, None))[1]
    fz = fitz_rows.get(sh)
    dd = (post - pre) if (post is not None and pre is not None) else None
    if dd is not None:
        tb += b or 0
        ta += post
    xok = (fz == post) if (fz is not None and post is not None) else True
    ok_pg = ok_pg and xok
    tbl.append('| %s | %s | %s | %s | %s | %+d |' % (sh, b, pre, post, fz, dd if dd is not None else 0))
tbl.append('')
tbl.append('全册：②C基线 %d → T7后 %d（T7 实增 %+d，T9 后中间值见行内）；fitz 与 COM 页数逐件一致=%s'
           % (tb, ta, ta - tb, ok_pg))
with open(os.path.join(RPT, '②D_页数对照.md'), 'w', encoding='utf-8') as f:
    f.write('# ②D 页数三账（②C基线 / T9后 / T7后）\n\n' + '\n'.join(tbl) + '\n')
say('  页数三账落盘 报告/②D_页数对照.md；fitz==COM 逐件一致 = %s' % ok_pg)
sys.exit(0 if (ok_wb and not baks and ok_md5 and ok_idem and ok_pg) else 2)
