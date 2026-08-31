# -*- coding: utf-8 -*-
"""M1盖章·自检④＋②缓存抽查：COM重开全十件——页数与盖章记录一致；每件抽3页（首/中/末）断言
调整页码（wdActiveEndAdjustedPageNumber=3）== start+件内页−1（≥3页/部分）。落盘 自检COM输出.txt/.json"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client

BASE = os.path.dirname(os.path.abspath(__file__))
PROD = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
EXPECT = [  # (件名, start, 盖章页数)
    ('人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 1, 20),
    ('人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 1, 20),
    ('人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 1, 78),
    ('人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 79, 78),
    ('人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 1, 4),
    ('人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 1, 40),
    ('人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 1, 47),
    ('人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 48, 51),
    ('人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 99, 36),
    ('人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 135, 63),
]

rows = []
fail = 0
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for name, start, stamped in EXPECT:
        p = os.path.join(PROD, name)
        doc = word.Documents.Open(os.path.abspath(p), ReadOnly=True, AddToRecentFiles=False)
        try:
            pages = doc.ComputeStatistics(2)
            pg_ok = (pages == stamped)
            if not pg_ok:
                fail += 1
            mids = sorted({1, (pages + 1) // 2, pages})
            samples = []
            for within in mids:
                rng = doc.GoTo(What=1, Which=1, Count=within)   # wdGoToPage=1, wdGoToAbsolute=1
                adj = rng.Information(1)                          # wdActiveEndAdjustedPageNumber=1（含pgNumType start）
                exp = start + within - 1
                ok = (adj == exp)
                if not ok:
                    fail += 1
                samples.append((within, adj, exp, ok))
            rows.append({'file': name, 'start': start, 'stamped': stamped, 'measured': pages,
                         'pages_ok': pg_ok, 'samples': samples})
            print('%s | 实测%d/盖章%d %s | 抽样 %s'
                  % (name[:40], pages, stamped, 'OK' if pg_ok else 'MISMATCH',
                     ' '.join('p%d=%d(exp%d)%s' % (w, a, e, 'OK' if ok else 'FAIL')
                              for w, a, e, ok in samples)))
        finally:
            doc.Close(False)
finally:
    word.Quit()

json.dump(rows, open(os.path.join(BASE, '自检COM结果.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
with open(os.path.join(BASE, '自检COM输出.txt'), 'w', encoding='utf-8') as f:
    for r in rows:
        f.write('%s\tstart=%d\t实测=%d\t盖章=%d\t%s\n' % (r['file'], r['start'], r['measured'],
                r['stamped'], 'OK' if r['pages_ok'] else 'MISMATCH'))
        for within, adj, exp, ok in r['samples']:
            f.write('  件内页%d -> 调整页码%d (预期%d) %s\n' % (within, adj, exp, 'OK' if ok else 'FAIL'))
    f.write('FAIL总数=%d\n' % fail)
print('FAIL总数=%d' % fail)
sys.exit(1 if fail else 0)
