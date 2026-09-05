# -*- coding: utf-8 -*-
"""②E_04_主链.py — ②-E 主链驱动（步间串行、逐步 exit code 落账、断言 FAIL 即停）。
序（纠错轮流水线实序＋交接三.5 联动件先行）：
  ①②E_01 预期记录＋节页码定位（预期 start 底稿）
  ②②E_02 册目录重造（预期版输入）→ ③②E_03 装订单联动（预期版输入）
  ④盖章（册级连续页码.py --parts parts_②E.json，COM 收敛）→ ⑤②E_05 三源恒等核验
     —— 漂移则：以实测记录重造 ②E_02/②E_03（②E_05 已产出 节页码_②E.json 实测版）再核
  ⑥逐页巡检管线 --direct（全件19，ExportAsFixedFormat＋逐页 PNG）
  ⑦②E_07 断言批（242 四值＋首页断言＋图定尺寸＋oMath＋PNG 完整性）
用法: python ②E_04_主链.py [起始步]   （断点续跑：起始步∈1..7，默认1）
"""
import sys, io, os, subprocess, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RPT = os.path.join(HERE, '报告')
DST = os.path.join(HERE, '副本_②E')
XJ = os.path.join(HERE, '巡检_②E')
P = lambda *a: os.path.join(*a)

FILES19 = [
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
    ('TOC', '人教B版选必1·册目录页.docx'),
    ('SM', '人教B版选必1·使用说明.docx'),
    ('COVER', '人教B版选必1·封面.docx'),
    ('PF1X', '人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx'),
    ('PF1Q', '人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx'),
    ('PF1J', '人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx'),
    ('PF2X', '人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx'),
    ('PF2Q', '人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx'),
    ('PF2J', '人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx'),
]

def run(step, cmd, timeout, tail=4000):
    print('\n########## 步骤 %s：%s ##########' % (step, ' '.join(os.path.basename(c) if i == 1 else c for i, c in enumerate(cmd[:2]))), flush=True)
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=timeout, cwd=ROOT)
        out = (r.stdout or '') + ('\n[stderr]\n' + r.stderr if r.stderr else '')
        print(out[-tail:], flush=True)
        print('—— 步骤 %s exit=%d 耗时 %.0fs' % (step, r.returncode, time.time() - t0), flush=True)
        return r.returncode, out
    except subprocess.TimeoutExpired as e:
        print('!! 步骤 %s 超时 %ds（out=%r）' % (step, timeout, (e.stdout or b'')[-400:] if isinstance(e.stdout, bytes) else str(e.stdout)[-400:]), flush=True)
        return 9, 'TIMEOUT'

START = int(sys.argv[1]) if len(sys.argv) > 1 else 1
summary = {}

def rec(k, v):
    summary[k] = v

if START <= 1:
    rc, _ = run('①②E_01节页码预期', [sys.executable, P(HERE, '②E_01_预期记录与节页码.py')], 1500)
    rec('01', rc); assert rc == 0, '①节页码预期 FAIL——停'

if START <= 2:
    rc, _ = run('②②E_02册目录重造(预期版)', [sys.executable, P(HERE, '②E_02_册目录重造.py'),
                 P(RPT, '预期盖章记录_②E.md'), P(RPT, '节页码_②E_预期.json'), P(RPT, 'build_②E_预期.json')], 300)
    rec('02', rc); assert rc == 0, '②册目录重造 FAIL——停'

if START <= 3:
    rc, _ = run('③②E_03装订单联动(预期版)', [sys.executable, P(HERE, '②E_03_装订单联动.py'),
                 P(RPT, '预期盖章记录_②E.md'), P(DST, '人教B版选必1·装订单.md')], 300)
    rec('03', rc); assert rc == 0, '③装订单联动 FAIL——停'

if START <= 4:
    rc, out = run('④盖章(册级连续页码,COM收敛)', [sys.executable, P(ROOT, '工具', '册级连续页码.py'),
                  '--parts', P(HERE, 'parts_②E.json'), '--record', P(RPT, '②E_盖章记录.md')], 2400, tail=5000)
    rec('04', rc); assert rc == 0, '④盖章 FAIL——停'

if START <= 5:
    rc, out = run('⑤②E_05三源恒等核验', [sys.executable, P(HERE, '②E_05_三源恒等核验.py')], 1800)
    rec('05', rc)
    if rc == 2 and 'DRIFT' in out:
        print('—— 三源漂移：以实测记录重造 册目录/装订单（②E_05 已产 节页码_②E.json 实测版）——', flush=True)
        rc2, _ = run('⑤a②E_02册目录重造(实测版)', [sys.executable, P(HERE, '②E_02_册目录重造.py'),
                     P(RPT, '②E_盖章记录.md'), P(RPT, '节页码_②E.json'), P(RPT, 'build_②E.json')], 300)
        rc3, _ = run('⑤b②E_03装订单联动(实测版)', [sys.executable, P(HERE, '②E_03_装订单联动.py'),
                     P(RPT, '②E_盖章记录.md'), P(DST, '人教B版选必1·装订单.md')], 300)
        rec('05a', rc2); rec('05b', rc3)
        assert rc2 == 0 and rc3 == 0, '⑤重造 FAIL——停'
    else:
        assert rc == 0, '⑤三源恒等核验 FAIL——停'

if START <= 6:
    pairs = ['%s=%s' % (c, P(DST, f)) for c, f in FILES19]
    rc, _ = run('⑥逐页巡检管线(--direct,19件)', [sys.executable, P(ROOT, '工具', '逐页巡检管线.py'),
                '--direct', '--out', XJ] + pairs, 5400, tail=6000)
    rec('06', rc); assert rc == 0, '⑥巡检管线 FAIL（有件未过视觉门）——停'

if START <= 7:
    rc, _ = run('⑦②E_07断言批', [sys.executable, P(HERE, '②E_07_断言批.py')], 3000)
    rec('07', rc); assert rc == 0, '⑦断言批 FAIL——停'

print('\n===== 主链汇总 =====')
print(summary)
print('CHAIN_ALLOK=%s' % (all(v == 0 for v in summary.values())))
