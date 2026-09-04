import win32com.client as wc
import pythoncom

OUT = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\tmp\word查节页眉_结果.txt'
lines = []
pythoncom.CoInitialize()
word = wc.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    f = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'
    doc = word.Documents.Open(f, ReadOnly=True, AddToRecentFiles=False, ConfirmConversions=False)
    lines.append(f'节数={doc.Sections.Count}')
    for i in range(1, doc.Sections.Count + 1):
        s = doc.Sections(i)
        ps = s.PageSetup
        lines.append(f'节{i}: DifferentFirstPage={ps.DifferentFirstPageHeaderFooter} OddEven={ps.OddAndEvenPagesHeaderFooter}')
        for name, idx in [('首', 2), ('奇', 1), ('偶', 3)]:
            hf = s.Headers(idx)
            txt = hf.Range.Text.replace('\r', ' ').replace('\x07', '')[:50] if hf.Exists else '(不存在)'
            lines.append(f'  页眉-{name}: Exists={hf.Exists} LinkToPrev={hf.LinkToPrevious} 文本="{txt}"')
        for name, idx in [('首', 2), ('奇', 1)]:
            hf = s.Footers(idx)
            txt = hf.Range.Text.replace('\r', ' ').replace('\x07', '')[:50] if hf.Exists else '(不存在)'
            lines.append(f'  页脚-{name}: Exists={hf.Exists} 文本="{txt}"')
    doc.Close(False)
finally:
    word.Quit()
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
print('DONE ->', OUT)
