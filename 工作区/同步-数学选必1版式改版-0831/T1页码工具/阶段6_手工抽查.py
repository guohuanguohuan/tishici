# -*- coding: utf-8 -*-
"""阶段6子进程：手工抽查2节——独立路径（不走SEC_RE正则，按整段文本精确匹配再取页），
对照工具输出值。结果写 阶段6结果.json。独立短生命周期进程。"""
import sys, os, io, json, gc
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import win32com.client, pythoncom

BASE = os.path.dirname(os.path.abspath(__file__))
rows = [ln.rstrip('\n').split('\t') for ln in open(os.path.join(BASE, '5a行.tsv'), encoding='utf-8')
        if ln.strip() and not ln.startswith('#')]
assert rows, '5a行.tsv为空'
targets = {c[2]: int(c[4]) for c in rows}          # 节标题全文 -> 工具部分内页码
pick = [rows[0][2], rows[-1][2]]                   # 首节＋末节

res = {'picked': []}
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(os.path.join(BASE, 'P3', 'B.docx'), ReadOnly=True, AddToRecentFiles=False)
    doc.Repaginate()
    try:
        for full in pick:
            hit = None
            for para in doc.Paragraphs:            # 独立线性精确匹配（非正则）
                t = para.Range.Text.rstrip('\r\x07\x0b\x0c \u3000')
                if t == full:
                    hit = para.Range.Information(3)
                    break
            assert hit is not None, '手工抽查未找到段落: %r' % full[:40]
            tool_val = targets[full]
            assert hit + 1 - 1 == tool_val, '抽查不符: %r 亲测件内页=%d 工具部分内页码=%d' % (full[:40], hit, tool_val)
            res['picked'].append({'title': full, 'in_page_com': hit, 'tool_part_page': tool_val})
            print('  ✓ %s… 亲测COM件内页=%d ↔ 工具部分内页码=%d' % (full[:34], hit, tool_val))
    finally:
        doc.Close(False)
        doc = None
finally:
    json.dump(res, open(os.path.join(BASE, '阶段6结果.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    gc.collect()
    try:
        word.Quit()
    except Exception as e:
        print('Quit告警(容忍):', e)
    word = None
    gc.collect()
    try:
        pythoncom.CoUninitialize()
    except Exception:
        pass
print('阶段6完成：2节独立复核一致')
