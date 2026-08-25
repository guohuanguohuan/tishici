# -*- coding: utf-8 -*-
"""pdf_export.py — §14 PDF 导出（PDFCreator 主路径：快照→PrintOut→轮询spool→取件删除）
用法: python pdf_export.py <docx> <outpdf> [pages: all|5]"""
import sys, io, os, time, glob, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

SPOOL = os.path.expandvars(r'%LOCALAPPDATA%\Temp\PDFCreator\Spool')

def export(src, outpdf, pages='all'):
    src = os.path.abspath(src)
    outpdf = os.path.abspath(outpdf)
    before = set(os.listdir(SPOOL)) if os.path.isdir(SPOOL) else set()
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
        word.ActivePrinter = 'PDFCreator'
        if pages == 'all':
            d.PrintOut(Background=False)
        else:
            # 前5页：wdPrintFromTo=3 起始1 结束5
            d.PrintOut(Background=False, Range=3, From='1', To='5')
        # 轮询 spool 新 pdf
        deadline = time.time() + 300
        newpdf = None
        while time.time() < deadline:
            time.sleep(2)
            cur = set(os.listdir(SPOOL)) if os.path.isdir(SPOOL) else set()
            new = [f for f in cur - before if f.lower().endswith('.pdf')]
            if new:
                newpdf = os.path.join(SPOOL, sorted(new)[0])
                # 等文件写完（大小稳定）
                s1 = os.path.getsize(newpdf); time.sleep(2)
                if os.path.getsize(newpdf) == s1:
                    break
        d.Close(False)
        if newpdf is None:
            print('ERROR: spool 无新 pdf')
            return 1
        # 经验：端口监视器拉起的隐藏 PDFCreator.exe 会占用任务 pdf——重试+按§4⑧⑨处置（本任务自己的实例）
        import subprocess
        for attempt in range(6):
            try:
                shutil.move(newpdf, outpdf)
                break
            except PermissionError:
                time.sleep(5)
                if attempt >= 2:
                    subprocess.run(['taskkill', '/f', '/im', 'PDFCreator.exe'], capture_output=True)
        else:
            print('ERROR: spool 文件持续占用')
            return 1
        inf = newpdf[:-4] + '.inf'
        if os.path.exists(inf): os.remove(inf)
        # 残留清查（§4⑨）：spool 中本会话新增的 .inf/.pdf 尾巴
        if os.path.isdir(SPOOL):
            for f in set(os.listdir(SPOOL)) - before:
                p = os.path.join(SPOOL, f)
                try:
                    if os.path.isfile(p): os.remove(p)
                except OSError:
                    pass
        print('OK', outpdf, os.path.getsize(outpdf) // 1024, 'KB')
        return 0
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

if __name__ == '__main__':
    export(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'all')
