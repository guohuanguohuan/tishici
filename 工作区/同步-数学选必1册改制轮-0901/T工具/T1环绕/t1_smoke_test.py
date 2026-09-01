# -*- coding: utf-8 -*-
"""T1一次性测试脚本：Word COM开卷冒烟＋PDF导出＋环绕页定位渲染（自建实例、测完Quit）。"""
import os
import sys
import win32com.client
import pythoncom

BASE = os.path.dirname(os.path.abspath(__file__))
FILES = [
    os.path.join(BASE, '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
    os.path.join(BASE, '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
]
PDF = os.path.join(BASE, '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.pdf')

def main():
    pythoncom.CoInitialize()
    word = None
    try:
        word = win32com.client.DispatchEx('Word.Application')
        word.Visible = False
        word.DisplayAlerts = 0
        print('Word COM Version:', word.Version)
        for fp in FILES:
            doc = word.Documents.Open(fp, ReadOnly=True, AddToRecentFiles=False)
            pages = doc.ComputeStatistics(2)  # wdStatisticPages
            drawings = doc.InlineShapes.Count
            shapes = doc.Shapes.Count
            print('开卷冒烟 OK: %s | 页数=%d | InlineShapes=%d | Shapes=%d'
                  % (os.path.basename(fp), pages, drawings, shapes))
            doc.Close(False)
        # PDF导出（讲练件，ExportAsFixedFormat，§14）
        doc = word.Documents.Open(FILES[1], ReadOnly=True, AddToRecentFiles=False)
        doc.ExportAsFixedFormat(PDF, 17)  # wdExportFormatPDF
        print('PDF导出 OK:', PDF)
        doc.Close(False)
    finally:
        if word is not None:
            word.Quit()
            print('Word COM Quit OK')
        pythoncom.CoUninitialize()

    # PyMuPDF：定位环绕形态候选页（图片bbox在左、同页右侧有文字与其y区间重叠）并渲染PNG
    import fitz
    d = fitz.open(PDF)
    print('PDF页数:', d.page_count)
    cand = []
    for pno in range(d.page_count):
        page = d[pno]
        pw = page.rect.width
        imgs = page.get_image_info()
        texts = page.get_text('blocks')
        for im in imgs:
            b = im['bbox']
            if b[2] - b[0] > 40 and b[3] - b[1] > 40:  # 非小图标
                left_mid = (b[0] + b[2]) / 2 < pw * 0.55
                if not left_mid:
                    continue
                # 右侧有文字块与图片y区间重叠 → 四周环绕证据
                for tb in texts:
                    tx0, ty0, tx1, ty1, txt = tb[0], tb[1], tb[2], tb[3], tb[4]
                    if tx0 > b[2] - 5 and not (ty1 < b[1] + 3 or ty0 > b[3] - 3) and txt.strip():
                        cand.append((pno + 1, [round(x, 1) for x in b], txt.strip()[:18]))
                        break
        if len(cand) >= 2:
            break
    print('环绕候选页:', cand[:4])
    seen = []
    for pno, bbox, _ in cand:
        if pno in seen:
            continue
        seen.append(pno)
        if len(seen) > 2:
            break
    for pno in seen[:2]:
        page = d[pno - 1]
        pix = page.get_pixmap(dpi=130)
        out = os.path.join(BASE, 'PDF抽查_p%d.png' % pno)
        pix.save(out)
        print('渲染PNG:', out)
    d.close()

if __name__ == '__main__':
    sys.exit(main())
