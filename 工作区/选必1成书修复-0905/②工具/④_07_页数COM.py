# -*- coding: utf-8 -*-
"""④轮步骤6c：COM 页数改前/改后实测（照 _pagecount.py 惯例——DispatchEx、ReadOnly、
AddToRecentFiles=False、CoInitialize；逐件重试×3＋杀最新 WINWORD 孤儿照 ②C_08 甲范式）。
改前面＝副本_④轮_改前（同步盘字节复制——禁直开同步盘原件）；改后面＝副本_④轮。
对照：预期盖章记录_②E.md（X1=15/I1=15/B=65/C=62/X2=5/I2=32/E=58/F=58/G=47/H=73，SM=2/TOC=1）
  改前应逐件＝盖章；改后逐件＝改前（B 允许位移——遗留3项内容修复偏差，决策③只登记不回滚）。
落盘 报告/④_页数_改前.json／④_页数_改后.json／④_页数对照.txt（逐件 flush，可断点续跑）。"""
import io, sys, os, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
DST = os.path.join(BASE, '副本_④轮')
DST_PRE = os.path.join(BASE, '副本_④轮_改前')
REP = os.path.join(BASE, '报告')
FILES = [
    ('I1清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 15),
    ('X1衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 15),
    ('B讲练1上', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 65),
    ('C讲练1下', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 62),
    ('I2清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 32),
    ('X2衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 5),
    ('E讲练92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 58),
    ('F讲练90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 58),
    ('G讲练68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 47),
    ('H讲练89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 73),
    ('SM使用说明', '人教B版选必1·使用说明.docx', 2),
    ('TOC册目录页', '人教B版选必1·册目录页.docx', 1),
]

def kill_newest_winword():
    try:
        import psutil
        ws = [p for p in psutil.process_iter(['name', 'create_time'])
              if (p.info['name'] or '').upper() == 'WINWORD.EXE']
        ws.sort(key=lambda x: x.info['create_time'], reverse=True)
        if ws:
            ws[0].kill()
            print('   killed orphan WINWORD %s' % ws[0].pid, flush=True)
    except Exception as e:
        print('   kill fail %s' % e, flush=True)

def measure(tag, folder):
    out_path = os.path.join(REP, '④_页数_%s.json' % tag)
    done = {}
    if os.path.exists(out_path):
        done = json.load(open(out_path, encoding='utf-8'))
    import win32com.client, pythoncom
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        for code, fn, _exp in FILES:
            if code in done:
                continue
            src = os.path.join(folder, fn)
            got = None
            for att in range(1, 4):
                t0 = time.time()
                try:
                    d = word.Documents.Open(os.path.abspath(src), ReadOnly=True,
                                            AddToRecentFiles=False)
                    d.Repaginate()
                    got = d.ComputeStatistics(2)   # wdStatisticPages
                    d.Close(False)
                    print('  %s %-10s %d pages（%.0fs）' % (tag, code, got, time.time() - t0), flush=True)
                    break
                except Exception as e:
                    print('  %s %-10s att%d fail %s' % (tag, code, att, str(e)[:100]), flush=True)
                    kill_newest_winword()
                    time.sleep(15)
                    try:
                        word.Quit()
                    except Exception:
                        pass
                    word = win32com.client.DispatchEx('Word.Application')
                    word.Visible = False
                    word.DisplayAlerts = 0
            if got is None:
                print('  %s %-10s FAIL 3试' % (tag, code), flush=True)
                sys.exit(2)
            done[code] = got
            json.dump(done, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    finally:
        try:
            word.Quit()
        except Exception:
            pass
        pythoncom.CoUninitialize()
    return done

pre = measure('改前', DST_PRE)
post = measure('改后', DST)
lines = []
ok_pre = ok_post = True
for code, fn, exp in FILES:
    a, b = pre.get(code), post.get(code)
    r1 = (a == exp)
    r2 = (b == a) or (code == 'B讲练1上')   # B 允许位移（决策③）——位移仍逐件登记
    ok_pre = ok_pre and r1
    ok_post = ok_post and r2
    lines.append('%-10s 盖章 %2d｜改前 %s %s｜改后 %s %s%s' % (
        code, exp, a, 'OK' if r1 else '←≠',
        b, 'OK' if b == a else ('（位移登记—遗留3项内容修复）' if code == 'B讲练1上' else '←≠'),
        '' if b == a else '（改前 %d）' % a))
    print(lines[-1], flush=True)
lines.append('改前＝盖章逐件 %s｜改后＝改前逐件 %s（B 位移登记豁免）' % (ok_pre, ok_post))
with open(os.path.join(REP, '④_页数对照.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print(lines[-1], flush=True)
sys.exit(0 if (ok_pre and ok_post) else 1)
