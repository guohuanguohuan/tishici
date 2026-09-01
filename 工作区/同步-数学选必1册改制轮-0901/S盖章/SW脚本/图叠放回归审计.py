# -*- coding: utf-8 -*-
"""
SW审计：图-图叠放回归扫描（基线PDF vs 改后PDF逐页图像矩形交叠面积对比）。
方法：COM逐件导PDF（自建实例Quit）→ PyMuPDF逐页取图像bbox → 页内两两求交面积，
件级汇总「总交叠面积/最大交叠对」对比：改后>基线即回归红旗。
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import win32com.client
import pythoncom
import fitz

BASE = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\S盖章\SW基线'
WORK = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\S盖章\SW工作'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\S盖章\SW脚本\漂移隔离\审计PDF'
os.makedirs(OUT, exist_ok=True)
FILES = {
    'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
MIN_AREA = 200  # pt²，小于此的交叠不记（微贴边不计）


def export_pdfs(pairs):
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        for src, dst in pairs:
            d = word.Documents.Open(os.path.abspath(src), ReadOnly=True, AddToRecentFiles=False)
            try:
                d.Repaginate()
                d.ExportAsFixedFormat(os.path.abspath(dst), 17)
                print('导出', os.path.basename(dst))
            finally:
                d.Close(False)
    finally:
        word.Quit()
        pythoncom.CoUninitialize()


def overlap_stat(pdf):
    doc = fitz.open(pdf)
    total, worst, n_pages_hit = 0.0, ('-', 0.0), 0
    for pno in range(doc.page_count):
        rects = [fitz.Rect(r['bbox']) for r in doc[pno].get_image_info()]
        page_ov = 0.0
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                inter = rects[i] & rects[j]
                a = inter.get_area() if not inter.is_empty else 0.0
                if a >= MIN_AREA:
                    total += a
                    page_ov += a
                    if a > worst[1]:
                        worst = ('页%d对%d-%d' % (pno + 1, i, j), a)
        if page_ov > 0:
            n_pages_hit += 1
    pages = doc.page_count
    doc.close()
    return pages, total, n_pages_hit, worst


def main():
    pairs = []
    for code, fn in FILES.items():
        pairs.append((os.path.join(BASE, fn), os.path.join(OUT, code + '_base.pdf')))
        pairs.append((os.path.join(WORK, fn), os.path.join(OUT, code + '_mod.pdf')))
    export_pdfs(pairs)
    print()
    print('| 件 | 基线页数 | 改后页数 | 基线交叠pt²(页数/最大对) | 改后交叠pt²(页数/最大对) | 判定 |')
    print('|---|---|---|---|---|---|')
    for code in FILES:
        pb, tb, nb, wb = overlap_stat(os.path.join(OUT, code + '_base.pdf'))
        pm, tm, nm, wm = overlap_stat(os.path.join(OUT, code + '_mod.pdf'))
        drift = pm - pb
        verdict = ('页漂移%+d' % drift if drift else '页0漂移') + ('；交叠回归+%.0fpt²' % (tm - tb) if tm > tb + 50 else '；交叠未增')
        print('| %s | %d | %d | %.0f (%d页, %s %.0f) | %.0f (%d页, %s %.0f) | %s |'
              % (code, pb, pm, tb, nb, wb[0], wb[1], tm, nm, wm[0], wm[1], verdict))


if __name__ == '__main__':
    main()
