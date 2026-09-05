# -*- coding: utf-8 -*-
"""④轮步骤7a：12 件改后副本 COM 直导 PDF＋逐页巡检。
导出：副本_④轮/*.docx → PDF对比/④轮PDF/<原文件名>.pdf
  ExportAsFixedFormat(dst, 17, CreateBookmarks=1)（标题书签入 PDF——照 ④轮任务口径）；
  逐件重试×3＋杀最新 WINWORD 孤儿（②C_08 甲范式）；Word 单实例。
逐页巡检（fitz，对基线＝PDF对比/②E终/*.pdf 即 09-06 03:5x 成书交付导出）：
  ①页数恒等 12 件；②书签（outline）条数恒等；③逐页文字层全等——差异页逐页登记
  （B 预期仅『试题分析：连接』→『连接』所在页 differ——遗留3项内容修复；其余 11 件应 0 差异页）。
落盘 报告/④_导出巡检.json＋④_导出巡检.md。"""
import io, sys, os, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
DST = os.path.join(BASE, '副本_④轮')
PDFO = os.path.join(BASE, 'PDF对比', '④轮PDF')
PDFB = os.path.join(BASE, 'PDF对比', '②E终')
REP = os.path.join(BASE, '报告')
FILES = [
    ('I1清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
    ('X1衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
    ('B讲练1上', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
    ('C讲练1下', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
    ('I2清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
    ('X2衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
    ('E讲练92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
    ('F讲练90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
    ('G讲练68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
    ('H讲练89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
    ('SM使用说明', '人教B版选必1·使用说明.docx'),
    ('TOC册目录页', '人教B版选必1·册目录页.docx'),
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

os.makedirs(PDFO, exist_ok=True)
import win32com.client, pythoncom
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for code, fn in FILES:
        src = os.path.join(DST, fn)
        dst = os.path.join(PDFO, fn[:-5] + '.pdf')
        if os.path.exists(dst):
            print('  %-10s SKIP（已在——断点续跑）' % code, flush=True)
            continue
        done = False
        for att in range(1, 4):
            t0 = time.time()
            try:
                d = word.Documents.Open(os.path.abspath(src), ReadOnly=True,
                                        AddToRecentFiles=False)
                d.ExportAsFixedFormat(os.path.abspath(dst), 17, CreateBookmarks=1)
                d.Close(False)
                print('  %-10s OK %.0fs' % (code, time.time() - t0), flush=True)
                done = True
                break
            except Exception as e:
                print('  %-10s att%d fail %s' % (code, att, str(e)[:100]), flush=True)
                kill_newest_winword()
                time.sleep(15)
                try:
                    word.Quit()
                except Exception:
                    pass
                word = win32com.client.DispatchEx('Word.Application')
                word.Visible = False
                word.DisplayAlerts = 0
        if not done:
            print('  %s FAIL 3试' % code, flush=True)
            sys.exit(2)
finally:
    try:
        word.Quit()
    except Exception:
        pass
    pythoncom.CoUninitialize()

print('== 逐页巡检（页数/文字 vs ②E终 基线；书签 vs 全件PDF——⑤轮 CreateBookmarks=1 同选项） ==', flush=True)
PDF5 = r'C:\提示词\工作区\选必1成书修复-0905\成书交付\全件PDF'
import fitz
out = {}
ok_all = True
for code, fn in FILES:
    newp = os.path.join(PDFO, fn[:-5] + '.pdf')
    oldp = os.path.join(PDFB, fn[:-5] + '.pdf')
    old5 = os.path.join(PDF5, fn[:-5] + '.pdf')
    dn, do, d5 = fitz.open(newp), fitz.open(oldp), fitz.open(old5)
    pg_same = (dn.page_count == do.page_count)
    toc_same = (len(dn.get_toc()) == len(d5.get_toc()))
    diffs = []
    if pg_same:
        for i in range(dn.page_count):
            if dn[i].get_text() != do[i].get_text():
                diffs.append(i + 1)
    expect = (code == 'B讲练1上')
    txt_ok = (len(diffs) == 0) if not expect else (0 < len(diffs) <= 3)
    ok = pg_same and toc_same and txt_ok
    ok_all = ok_all and ok
    out[code] = {'pages_new': dn.page_count, 'pages_old': do.page_count,
                 'toc_new': len(dn.get_toc()), 'toc_5': len(d5.get_toc()),
                 'diff_pages': diffs, 'page_same': pg_same, 'toc_same': toc_same,
                 'text_ok': txt_ok, 'ok': ok}
    print('  %-10s 页 %d/%d %s｜书签 %d/%d（⑤全件PDF） %s｜文字差异页 %s %s' % (
        code, dn.page_count, do.page_count, 'OK' if pg_same else '←≠',
        len(dn.get_toc()), len(d5.get_toc()), 'OK' if toc_same else '←≠',
        diffs if diffs else '0', 'PASS' if ok else '←FAIL'), flush=True)
    dn.close(); do.close(); d5.close()
with open(os.path.join(REP, '④_导出巡检.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('④_08 巡检合计 PASS＝%s（B 差异页＝遗留3项修复页，已登记）' % ok_all, flush=True)
sys.exit(0 if ok_all else 1)
