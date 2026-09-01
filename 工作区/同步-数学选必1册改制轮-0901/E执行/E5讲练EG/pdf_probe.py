# -*- coding: utf-8 -*-
"""pdf_probe.py — 导出docx前2页PDF并跑E5抽查校验（页眉页脚同串/节名域/字号/四值灰度）"""
import sys, os
import win32com.client

def export_first2(docx, pdf):
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(os.path.abspath(docx), ReadOnly=True, AddToRecentFiles=False)
        try:
            d.Repaginate()
            d.ExportAsFixedFormat(os.path.abspath(pdf), 17, False, 0, 3, 1, 2, 7, True, True, 0, 0, 0, 0)
            # 3=wdExportFromTo
        finally:
            d.Close(False)
    finally:
        word.Quit()

def check(pdf):
    import fitz
    doc = fitz.open(pdf)
    print('pages:', doc.page_count)
    for pno in range(doc.page_count):
        pg = doc[pno]
        text = pg.get_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        hdr = lines[0] if lines else ''
        print('--- p%d 首行(页眉): %r' % (pno + 1, hdr))
        print('    末行(页脚): %r' % (lines[-1] if lines else ''))
        assert '羿郭工作室' in hdr and '第2章 平面解析几何·讲练' in hdr, '页眉同串缺失'
        assert '第' in lines[-1] and '页' in lines[-1], '页脚页码缺失'
        # 字号抽样：正文span size≈12pt、页眉页脚≈9pt
        sizes = {}
        for b in pg.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                for sp in ln['spans']:
                    t = sp['text'].strip()
                    if not t:
                        continue
                    sizes.setdefault(round(sp['size'], 1), []).append(t[:10])
        top = sorted(sizes.items(), key=lambda kv: -len(kv[1]))
        print('    span字号分布(TOP5):', [(k, len(v)) for k, v in top[:5]])
        # 9pt 页眉页脚存在性
        assert any(abs(k - 9) < 0.6 for k in sizes), '页眉页脚9pt未见'
    # 灰度四值（矢量层）
    import collections
    fills = collections.Counter()
    for pno in range(doc.page_count):
        for d in doc[pno].get_drawings():
            f = d.get('fill')
            if f:
                g = round(sum(f[:3]) / 3 * 255)
                fills[g] += 1
    print('矢量fill灰度分布:', dict(sorted(fills.items())))
    doc.close()

if __name__ == '__main__':
    docx, pdf = sys.argv[1], sys.argv[2]
    if not os.path.exists(pdf):
        export_first2(docx, pdf)
    check(pdf)
