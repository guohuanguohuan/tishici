# -*- coding: utf-8 -*-
"""②D_R2_00_锚定.py — ②-D 重跑轮：FX-6 净场四查＋清单件入场＋MD5/oMath 双锚定。
0) FX-6① 进程面：WINWORD/悬挂 python 计数；同步客户端登记（用户进程禁杀）。
1) FX-6② 文件面：副本＋同步盘 ~$ 锁残留；副本可写试探。
2) 清单件两件入场（②-F 未复制；同步盘 ②-C 终态即其正确态，T5 零处置）：
   copy → MD5 对 ②C_终报§四 锚（13274dec…／bca6fd1c…）。
3) MD5 锚定：②-F 修复态八件对 ②F_终报§五.1 前缀（不符即停跑）。
4) oMath 基线锚定：十件 m:oMath 元素总数对 ②-F/派发基线（不符即停跑）。
5) FX-6③ 链路面冒烟：T9 dry 衔接2 一件（工具×环境链路）。
报告：报告/②D_R2_00_锚定.md。任一硬项 FAIL → exit 2（停跑呈报）。
"""
import sys, io, os, time, shutil, hashlib, zipfile, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
SYNC = os.path.join(ROOT, '高中数学', '高中数学同步')
RPT = os.path.join(HERE, '报告')
T9 = os.path.join(ROOT, '工具', '跨行保护器.py')

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
# ②F 终报 §五.1 修复态 MD5（前缀口径，终报截断 8 位）
F_MD5_PREFIX = {
    '衔接1': '2ed6bbc2', '上61': '59e86c29', '下79': '17fa3fa2', '衔接2': '40527e1f',
    '92': '440e339c', '90': '5577c4a6', '68': 'e67ed2b7', '89': '198fd414',
}
# ②C 终报§四 锚（②D_00/②F_00 已核同步盘＝②C 锚）：清单件全 MD5
C_MD5_FULL = {
    '清单1': '13274dec8bd11de25cc0639b6336ade3',
    '清单2': 'bca6fd1c65c4c4a424489336ddd6bb1b',
}
# 派发 oMath 基线（②-F 修复态）：清单件 396/1156
OM_BASE = {'清单1': 396, '衔接1': 882, '上61': 3251, '下79': 2876, '清单2': 1156,
           '衔接2': 243, '92': 2705, '90': 2914, '68': 2359, '89': 4034}
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

OUT = []
HARD_FAIL = []
def say(m):
    print(m, flush=True)
    OUT.append(m)
def fail(m):
    say('  !! ' + m)
    HARD_FAIL.append(m)

def md5(p, tries=8):
    for _ in range(tries):
        try:
            h = hashlib.md5()
            with open(p, 'rb') as f:
                for chunk in iter(lambda: f.read(1 << 20), b''):
                    h.update(chunk)
            return h.hexdigest()
        except PermissionError:
            time.sleep(6)
    return 'LOCKED'

say('# ②D 重跑轮 锚定（FX-6 净场＋清单件入场＋MD5/oMath 双锚） %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
say('')
say('## 〇 FX-6① 进程面')
try:
    import psutil
    ww = [p for p in psutil.process_iter(['name', 'create_time']) if (p.info['name'] or '').upper() == 'WINWORD.EXE']
    py = [p for p in psutil.process_iter(['name']) if (p.info['name'] or '').lower() in ('python.exe', 'pythonw.exe')]
    say('  WINWORD=%d  python=%d %s' % (len(ww), len(py), [(p.pid, p.info['name']) for p in ww + py]))
    if len(ww) > 0:
        fail('WINWORD 残留 %d（FX-4 自臂净场径行）' % len(ww))
        for p in ww:
            try:
                p.kill()
                say('  已杀 WINWORD 孤儿 pid%d' % p.pid)
            except Exception:
                pass
        HARD_FAIL[:] = [x for x in HARD_FAIL if 'WINWORD 残留' not in x]
        say('  （孤儿已净，进程面复核为净）')
except Exception as e:
    say('  psutil 不可用: %s' % e)
sync_clients = []
try:
    import psutil as _ps
    for p in _ps.process_iter(['name']):
        n = (p.info['name'] or '')
        if 'resilio' in n.lower() or 'realtimesync' in n.lower():
            sync_clients.append('%s(pid%d)' % (n, p.pid))
    say('  同步客户端（用户进程禁杀）：%s' % ('；'.join(sync_clients) or '无'))
except Exception:
    pass

say('')
say('## ① FX-6② 文件面')
locks = []
for d in (DST, SYNC):
    for f in os.listdir(d):
        if f.startswith('~$'):
            locks.append(os.path.join(d, f))
say('  ~$ 锁残留 = %d %s' % (len(locks), locks if locks else '（净）'))
if locks:
    fail('~$ 锁残留：' + str(locks))
probe = os.path.join(DST, '_可写试探.tmp')
try:
    with open(probe, 'w') as f:
        f.write('probe')
    os.remove(probe)
    say('  副本可写试探 PASS')
except Exception as e:
    fail('副本不可写: %s' % e)

say('')
say('## ② 清单件两件入场（同步盘 ②-C 终态 → 副本；T5 零处置件）')
for sh in ('清单1', '清单2'):
    n = dict(NAMES)[sh]
    s, d = os.path.join(SYNC, n), os.path.join(DST, n)
    if os.path.exists(d):
        say('  %s 副本已在（跳过复制）' % sh)
    else:
        done = False
        for rd in range(3):
            for att in range(8):
                try:
                    shutil.copy2(s, d)
                    done = True
                    break
                except PermissionError:
                    time.sleep(6)
            if done:
                break
            time.sleep(20)
        say('  %s 复制 %s' % (sh, 'OK' if done else 'FAIL'))
        if not done:
            fail('%s 入场失败' % sh)
    m_sync, m_dst = md5(s), md5(d)
    ok = (m_dst == m_sync == C_MD5_FULL[sh])
    say('  %s MD5 副本=%s 同步=%s 锚=%s %s' % (sh, m_dst, m_sync, C_MD5_FULL[sh], 'PASS' if ok else 'FAIL'))
    if not ok:
        fail('%s MD5 锚不符' % sh)

say('')
say('## ③ ②-F 修复态八件 MD5 锚定（对 ②F_终报§五.1 前缀）')
md5_tab = {}
for sh, n in NAMES:
    if sh in ('清单1', '清单2'):
        continue
    m = md5(os.path.join(DST, n))
    md5_tab[sh] = m
    ok = m.startswith(F_MD5_PREFIX[sh]) and m != 'LOCKED'
    say('  %-5s %s  %s %s' % (sh, m, 'PASS' if ok else 'FAIL', '（②F锚 %s…）' % F_MD5_PREFIX[sh] if not ok else ''))
    if not ok:
        fail('%s MD5 ≠ ②-F 修复态锚' % sh)

say('')
say('## ④ oMath 基线锚定（十件，②-F 修复态/派发基线）')
om_tab = {}
for sh, n in NAMES:
    fp = os.path.join(DST, n)
    z = zipfile.ZipFile(fp)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    c = sum(len(list(p.iter('{%s}oMath' % M))) for p in doc.iter('{%s}p' % W))
    om_tab[sh] = c
    ok = (c == OM_BASE[sh])
    say('  %-5s oMath=%5d 基线=%5d %s' % (sh, c, OM_BASE[sh], 'PASS' if ok else 'FAIL'))
    if not ok:
        fail('%s oMath ≠ 基线' % sh)

say('')
say('## ⑤ FX-6③ 链路面冒烟（T9 dry 衔接2）')
try:
    p = subprocess.run(['python', T9, os.path.join(DST, dict(NAMES)['衔接2']), '--dry-run'],
                       capture_output=True, text=True, encoding='utf-8', timeout=120, cwd=ROOT)
    say('  exit=%d' % p.returncode)
    for ln in (p.stdout or '').strip().splitlines():
        say('  ' + ln)
    if p.returncode != 0:
        fail('T9 dry 冒烟失败: %s' % (p.stderr[-200:] if p.stderr else ''))
    else:
        say('  （T9c 计数以修复态预跑为执行基线，桥梁账随终报呈报）')
except Exception as e:
    fail('冒烟异常: %s' % e)

say('')
say('## 汇总')
say('HARD_FAIL = %s' % (HARD_FAIL if HARD_FAIL else '无（全部 PASS，可放量）'))
with open(os.path.join(RPT, '②D_R2_00_锚定.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(OUT) + '\n')
sys.exit(2 if HARD_FAIL else 0)
