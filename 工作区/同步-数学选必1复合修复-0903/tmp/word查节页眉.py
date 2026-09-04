import win32com.client as wc
import pythoncom, sys

files = {
    'B': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'H': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
pythoncom.CoInitialize()
word = wc.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for k, f in files.items():
        doc = word.Documents.Open(f, ReadOnly=True, AddToRecentFiles=False)
        print(f'=== {k}: 节数={doc.Sections.Count} 页数={doc.ComputeStatistics(2)} ===')
        for i in range(1, doc.Sections.Count + 1):
            s = doc.Sections(i)
            idx = s.Range.Information(3)  # wdActiveEndPageNumber? 用起始页
            start_pg = s.Range.Information(3)
            hs = []
            for name, hf in [('首', s.Headers(2)), ('奇', s.Headers(1)), ('偶', s.Headers(3))]:
                try:
                    txt = hf.Range.Text.replace('\r', ' ').replace('\x07', '')[:40] if hf.Exists else '不存在'
                    link = hf.LinkToPrevious
                except Exception as e:
                    txt, link = f'ERR:{e}', '?'
                hs.append(f'{name}:Exists={hf.Exists} Link={link} 文本="{txt}"')
            fs = []
            for name, hf in [('首', s.Footers(2)), ('奇', s.Footers(1)), ('偶', s.Footers(3))]:
                try:
                    txt = hf.Range.Text.replace('\r', ' ').replace('\x07', '')[:40] if hf.Exists else '不存在'
                except Exception as e:
                    txt = f'ERR:{e}'
                fs.append(f'{name}:"{txt}"')
            ps = s.PageSetup
            print(f'  节{i}: 起始页={start_pg} DifferentFirstPage={ps.DifferentFirstPageHeaderFooter} OddEven={ps.OddAndEvenPagesHeaderFooter}')
            print('    页眉', *hs, sep=' | ')
            print('    页脚', *fs, sep=' | ')
        doc.Close(False)
finally:
    word.Quit()
