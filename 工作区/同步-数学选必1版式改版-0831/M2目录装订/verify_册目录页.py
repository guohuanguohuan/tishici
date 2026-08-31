# -*- coding: utf-8 -*-
"""M2：册目录页验证（XML级 + COM实测）。只读自建实例，用完Quit。"""
import zipfile, re, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
WS = os.path.dirname(os.path.abspath(__file__))
DOCX = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WS, '人教B版选必1·册目录页.docx')
res = {}

z = zipfile.ZipFile(DOCX)
names = z.namelist()
xml = z.read('word/document.xml').decode('utf-8')
paras = re.findall(r'<w:p\b.*?</w:p>', xml, re.S)

def txt(p): return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))

rows = [p for p in paras if '<w:tab w:val="right" w:leader="dot" w:pos="10206"/>' in p]
title = [p for p in paras if '册目录页' in txt(p) and '·' in txt(p) and len(txt(p)) < 20]
ind0 = [p for p in rows if '<w:ind' not in p]
ind420 = [p for p in rows if 'w:left="420"' in p]
ind840 = [p for p in rows if 'w:left="840"' in p]
bold_rows = [p for p in rows if '<w:b/>' in p]
sz18 = [p for p in rows if '<w:sz w:val="18"/>' in p]
sz24 = [p for p in rows if '<w:sz w:val="24"/>' in p]
jc_left = len([p for p in paras if '<w:jc w:val="left"/>' in p])
no_font = [p for p in paras if 'w:eastAsia="宋体"' not in p]

res['xml'] = {
  '总段数(含标题)': len(paras),
  '目录行数(带点线制表位)': len(rows),
  '列头+章2+件型6+节级25=34': len(rows) == 34,
  '缩进0/420/840行数': [len(ind0), len(ind420), len(ind840)],
  '缩进分布=列头1+章2 | 件型6 | 节级25': [len(ind0), len(ind420), len(ind840)] == [3, 6, 25],
  '加粗行(2章行)': len(bold_rows),
  '加粗行=2': len(bold_rows) == 2,
  '18半点行/24半点行': [len(sz18), len(sz24)],
  '字号分布=32行/24半点2行/18半点32行': [len(sz18), len(sz24)] == [32, 2] and '<w:sz w:val="32"/>' in paras[0],
  '全部段落jc=left': jc_left == len(paras),
  '全部run显式rFonts宋体/TNR': len(no_font) == 0,
  '无页眉页脚部件': not any(('header' in n or 'footer' in n) for n in names),
  'A4(11906x16838)': 'w:w="11906"' in xml and 'w:h="16838"' in xml,
  'pgMar全850': '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="850" w:footer="850" w:gutter="0"/>' in xml,
  'docGrid非lines': 'w:type="lines"' not in xml,
  'core.title==文件名': f'<dc:title>{os.path.splitext(os.path.basename(DOCX))[0]}</dc:title>' in z.read('docProps/core.xml').decode('utf-8'),
  'creator空': '<dc:creator/>' in z.read('docProps/core.xml').decode('utf-8'),
  '文内开头标题=文件名': txt(paras[0]) == os.path.splitext(os.path.basename(DOCX))[0],
  '标题ADC2DA+底边框': 'w:fill="ADC2DA"' in paras[0] and '<w:bottom w:val="single"' in paras[0],
  'settings含updateFields': 'updateFields' in z.read('word/settings.xml').decode('utf-8'),
  '节级行25(括注题量)': len([p for p in rows if re.search(r'（\d+题）', txt(p)) and 'w:left="840"' in p]),
}
# 页码列抽取（供落盘）
res['页码列'] = [txt(p) for p in rows]

# ---------- COM ----------
import pythoncom, win32com.client
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(DOCX, ReadOnly=True, AddToRecentFiles=False)
    doc.Repaginate()
    ps = doc.PageSetup
    res['com'] = {
        '页数': doc.ComputeStatistics(2),
        '页数==1': doc.ComputeStatistics(2) == 1,
        'PageWidth_pt': round(ps.PageWidth, 1), 'PageHeight_pt': round(ps.PageHeight, 1),
        'A4实测(595.3x841.9±1)': abs(ps.PageWidth - 595.3) < 1 and abs(ps.PageHeight - 841.9) < 1,
        '边距pt(上下左右=42.5)': [round(ps.TopMargin, 1), round(ps.BottomMargin, 1), round(ps.LeftMargin, 1), round(ps.RightMargin, 1)],
        '段落数': doc.Paragraphs.Count,
    }
    doc.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()

ok = True
for k, v in res['xml'].items():
    if isinstance(v, bool) and not v: ok = False
for k, v in res['com'].items():
    if isinstance(v, bool) and not v: ok = False
res['全部布尔项通过'] = ok
json.dump(res, open(os.path.join(WS, 'verify_册目录页.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in res['xml'].items(): print(f'{k}: {v}')
for k, v in res['com'].items(): print(f'COM {k}: {v}')
print('PASS' if ok else 'FAIL')
