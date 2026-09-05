# -*- coding: utf-8 -*-
"""②E_00_净场锚定.py — ②-E 轮 FX-6 净场四查＋起点态 MD5 锚定＋入场复制。
①进程面/文件面检查（WINWORD/悬挂python/~$锁/可写试探）；②同步盘十件 MD5 对 ②D_R2_MD5_回写.md 锚；
③19件（十件＋9配页件）复制入 ②工具/副本_②E/；④副本 MD5 复核＝同步盘。证据：报告/②E_00_净场锚定.md"""
import sys, io, os, re, shutil, hashlib, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SYNC = os.path.join(ROOT, '高中数学', '高中数学同步')
DST = os.path.join(HERE, '副本_②E')
RPT = os.path.join(HERE, '报告')
os.makedirs(DST, exist_ok=True)

TEN = [
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
PEIYE = [
    ('使用说明', '人教B版选必1·使用说明.docx'),
    ('册目录页', '人教B版选必1·册目录页.docx'),
    ('封面', '人教B版选必1·封面.docx'),
    ('部封1衔接', '人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx'),
    ('部封1清单', '人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx'),
    ('部封1讲练', '人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx'),
    ('部封2衔接', '人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx'),
    ('部封2清单', '人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx'),
    ('部封2讲练', '人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx'),
    ('装订单', '人教B版选必1·装订单.md'),
]
ALL = TEN + PEIYE

OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

say('== FX-6 ①进程面 ==')
r = subprocess.run(['tasklist'], capture_output=True, text=True)
tl = r.stdout or ''
bad = [ln for ln in tl.splitlines() if re.search(r'WINWORD|PDFCreator', ln, re.I)]
py = [ln for ln in tl.splitlines() if 'python' in ln.lower()]
say('  WINWORD/PDFCreator 残留 = %d %s' % (len(bad), '净' if not bad else '!!' + str(bad)))
say('  python 进程 = %d（应仅本臂）' % len(py))

say('== FX-6 ②文件面 ==')
locks = [f for f in os.listdir(SYNC) if f.startswith('~$')]
say('  同步盘 ~$ 锁残留 = %d %s' % (len(locks), '净' if not locks else '!!' + str(locks)))
probe = os.path.join(DST, '_可写试探.tmp')
open(probe, 'w').write('x')
os.remove(probe)
say('  副本目录可写试探 = OK')

say('== 起点态 MD5 锚定（同步盘十件 vs ②D_R2_MD5_回写.md） ==')
anchor = {}
for ln in open(os.path.join(RPT, '②D_R2_MD5_回写.md'), encoding='utf-8'):
    m = re.match(r'\|\s*(\S+)\s*\|\s*([0-9a-f]{32})\s*\|\s*([0-9a-f]{32})\s*\|\s*(\w+)\s*\|', ln)
    if m:
        anchor[m.group(1)] = m.group(2)
assert len(anchor) == 10, anchor
ok_anchor = True
rows = []
for sh, n in TEN:
    got = md5(os.path.join(SYNC, n))
    hit = (got == anchor.get(sh))
    ok_anchor = ok_anchor and hit
    rows.append('| %s | %s | %s |' % (sh, got, 'PASS=②D锚' if hit else '!!FAIL 锚=%s' % anchor.get(sh)))
    say('  %-6s %s %s' % (sh, got[:12], 'PASS' if hit else '!!FAIL'))
say('起点态锚定十件全PASS = %s' % ok_anchor)
assert ok_anchor, '起点态≠②-D 回写终态——停跑'

say('== ③入场复制（19件 → 副本_②E） ==')
for sh, n in ALL:
    shutil.copy2(os.path.join(SYNC, n), os.path.join(DST, n))
    say('  入场 %s' % sh)

say('== ④副本 MD5 复核（副本 vs 同步盘，逐件） ==')
ok_cp = True
for sh, n in ALL:
    a, b = md5(os.path.join(SYNC, n)), md5(os.path.join(DST, n))
    if a != b:
        ok_cp = False
        say('  !! %s 副本≠同步盘' % sh)
say('入场复制 19/19 MD5 全等 = %s' % ok_cp)
assert ok_cp

with open(os.path.join(RPT, '②E_00_净场锚定.md'), 'w', encoding='utf-8') as f:
    f.write('# ②-E 净场四查＋起点态锚定＋入场复制（2026-09-06）\n\n```text\n' + '\n'.join(OUT) + '\n```\n\n'
            '| 件 | 同步盘MD5 | 对②D锚 |\n|---|---|---|\n' + '\n'.join(rows) + '\n')
print('REPORT_DONE', flush=True)
