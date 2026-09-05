# -*- coding: utf-8 -*-
"""同步盘 T8 dry 逐件复核 v2：流式、每件300s超时、挂死自动杀最新WINWORD孤儿、每件最多3试。
结果汇总落 报告/②B_T8_dry_同步盘.md"""
import subprocess, os, sys, io, time, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import psutil
src = r'高中数学\高中数学同步'
names = [
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
tool = os.path.join('工具', '表格规范执行器.py')
results = []
for n in names:
    f = os.path.join(src, n)
    got = None
    for att in range(1, 4):
        t0 = time.time()
        print('>>> %s att%d' % (n[:26], att), flush=True)
        try:
            p = subprocess.run(['python', tool, f, '--dry-run'], capture_output=True,
                               text=True, encoding='utf-8', timeout=300)
        except subprocess.TimeoutExpired:
            # 杀最新 WINWORD 孤儿
            ws = [p2 for p2 in psutil.process_iter(['name', 'create_time'])
                  if (p2.info['name'] or '').upper() == 'WINWORD.EXE']
            ws.sort(key=lambda x: x.info['create_time'], reverse=True)
            if ws:
                try:
                    ws[0].kill(); print('   killed orphan WINWORD', ws[0].pid, flush=True)
                except Exception as e:
                    print('   kill fail', e, flush=True)
            time.sleep(20)
            continue
        dt = time.time() - t0
        if p.returncode == 0 and 'Traceback' not in p.stderr:
            got = p.stdout.strip()
            print('   OK %.0fs' % dt, flush=True)
            print(got, flush=True)
            break
        print('   fail exit=%d %.0fs stderr=%s' % (p.returncode, dt, p.stderr[-200:]), flush=True)
        time.sleep(30)
    results.append((n, got))
out = []
for n, got in results:
    out.append('## %s\n%s\n' % (os.path.basename(n), got if got else '!! 未通过（Resilio锁阻塞）'))
rpt = os.path.join('工作区', '选必1成书修复-0905', '②工具', '报告', '②B_T8_dry_同步盘.md')
with open(rpt, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out))
bad = [n for n, got in results if not got]
print('SUMMARY: ok=%d fail=%d' % (len(results) - len(bad), len(bad)), flush=True)
for b in bad:
    print('  FAIL:', b, flush=True)
print('PERFILE2 DONE', flush=True)
