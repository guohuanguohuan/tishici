# -*- coding: utf-8 -*-
"""⑦轮步骤1：衔接件 X1/X2 芯片补挂后 COM 重导 PDF＋逐页巡检（④_08 范式裁剪版）。
导出：副本_④轮/<X1,X2>.docx → PDF对比/④轮PDF/<同名>.pdf（原位覆盖；旧件先留档 ⑦改前PDF留档/）
巡检（fitz，对 ⑦改前留档）：页数恒等｜书签条数恒等（vs 成书交付/全件PDF）｜逐页文字层全等
  （芯片补挂＝纯格式，文字层应零差异；页数变动即排版漂移、FAIL）。
落盘 报告/⑦_导出巡检.json。"""
import io, sys, os, json, time, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
DST = os.path.join(BASE, '副本_④轮')
PDFO = os.path.join(BASE, 'PDF对比', '④轮PDF')
PDFOLD = os.path.join(BASE, 'PDF对比', '⑦改前PDF留档')
PDF5 = r'C:\提示词\工作区\选必1成书修复-0905\成书交付\全件PDF'
REP = os.path.join(BASE, '报告')
FILES = [
    ('X1衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
    ('X2衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
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

os.makedirs(PDFOLD, exist_ok=True)
for code, fn in FILES:
    old = os.path.join(PDFO, fn[:-5] + '.pdf')
    bak = os.path.join(PDFOLD, fn[:-5] + '.pdf')
    if os.path.exists(old) and not os.path.exists(bak):
        shutil.copyfile(old, bak)
        print('  留档 %s' % fn[:-5] + '.pdf', flush=True)

import win32com.client, pythoncom
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for code, fn in FILES:
        src = os.path.join(DST, fn)
        dst = os.path.join(PDFO, fn[:-5] + '.pdf')
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

print('== 逐页巡检（vs ⑦改前留档；书签 vs 全件PDF） ==', flush=True)
import fitz
out = {}
ok_all = True
for code, fn in FILES:
    newp = os.path.join(PDFO, fn[:-5] + '.pdf')
    oldp = os.path.join(PDFOLD, fn[:-5] + '.pdf')
    old5 = os.path.join(PDF5, fn[:-5] + '.pdf')
    dn, do, d5 = fitz.open(newp), fitz.open(oldp), fitz.open(old5)
    pg_same = (dn.page_count == do.page_count)
    toc_same = (len(dn.get_toc()) == len(d5.get_toc()))
    diffs = []
    if pg_same:
        for i in range(dn.page_count):
            if dn[i].get_text() != do[i].get_text():
                diffs.append(i + 1)
    txt_ok = (len(diffs) == 0)
    ok = pg_same and toc_same and txt_ok
    ok_all = ok_all and ok
    out[code] = {'pages_new': dn.page_count, 'pages_old': do.page_count,
                 'toc_new': len(dn.get_toc()), 'toc_5': len(d5.get_toc()),
                 'diff_pages': diffs, 'page_same': pg_same, 'toc_same': toc_same,
                 'text_ok': txt_ok, 'ok': ok}
    print('  %-10s 页 %d/%d %s｜书签 %d/%d %s｜文字差异页 %s %s' % (
        code, dn.page_count, do.page_count, 'OK' if pg_same else '←≠',
        len(dn.get_toc()), len(d5.get_toc()), 'OK' if toc_same else '←≠',
        diffs if diffs else '0', 'PASS' if ok else '←FAIL'), flush=True)
    dn.close(); do.close(); d5.close()
with open(os.path.join(REP, '⑦_导出巡检.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('⑦_01 巡检合计 PASS＝%s' % ok_all, flush=True)
sys.exit(0 if ok_all else 1)
