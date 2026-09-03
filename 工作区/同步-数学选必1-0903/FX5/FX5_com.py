# -*- coding: utf-8 -*-
"""FX5-G COM verification (ReadOnly, self-spawned instance, Quit after use)"""
import sys, os

TARGET = sys.argv[1] if len(sys.argv) > 1 else r'C:\提示词\工作区\同步-数学选必1-0903\tmp\FX5_G\G_fixed.docx'

import win32com.client
import pythoncom
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(TARGET, ReadOnly=True, AddToRecentFiles=False)
    print('opened OK (no repair dialog):', os.path.basename(TARGET))
    print('Sections.Count =', doc.Sections.Count)
    sec1 = doc.Sections(1)
    print('TextColumns.Count =', sec1.PageSetup.TextColumns.Count)
    if sec1.PageSetup.TextColumns.Count >= 2:
        try:
            print('TextColumns spacing pt =', round(sec1.PageSetup.TextColumns(1).SpaceAfter, 1))
        except Exception:
            try:
                print('TextColumns spacing pt =', round(sec1.PageSetup.TextColumns.Spacing, 1))
            except Exception as e:
                print('TextColumns spacing: (n/a)', e)
    print('PageSetup: PageW×H pt =', round(sec1.PageSetup.PageWidth, 1), '×', round(sec1.PageSetup.PageHeight, 1),
          '| margins T/B/L/R pt =', round(sec1.PageSetup.TopMargin, 1), round(sec1.PageSetup.BottomMargin, 1),
          round(sec1.PageSetup.LeftMargin, 1), round(sec1.PageSetup.RightMargin, 1),
          '| header dist =', round(sec1.PageSetup.HeaderDistance, 1), '| footer dist =', round(sec1.PageSetup.FooterDistance, 1))
    print('StartingNumber =', sec1.Headers(1).PageNumbers.StartingNumber)
    print('DifferentFirstPage =', sec1.Headers(1).PageNumbers.NumberStyle and '' or '', '| OddAndEven =', word.ActiveDocument.Sections(1).Headers(1).PageNumbers.Count and '' or '')
    try:
        print('OddAndEvenPagesHeaderFooter =', doc.Sections(1).PageSetup.DifferentFirstPageHeaderFooter)
    except Exception:
        pass
    print('Page count (COMputed) =', doc.ComputeStatistics(2))  # wdStatisticPages
    print('OMaths.Count =', doc.OMaths.Count)
    hdr = sec1.Headers(1).Range.Text.strip()
    ftr = sec1.Footers(1).Range.Text.strip()
    print('HEADER:', repr(hdr[:90]))
    print('FOOTER:', repr(ftr[:90]))
    first = doc.Paragraphs(1).Range.Text.strip()
    print('First paragraph:', repr(first[:40]))
    # first page fields resolution
    print('Header fields on p1 sample pages:')
    doc.Repaginate()
    print('Pages after repaginate =', doc.ComputeStatistics(2))
    doc.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print('COM DONE')
