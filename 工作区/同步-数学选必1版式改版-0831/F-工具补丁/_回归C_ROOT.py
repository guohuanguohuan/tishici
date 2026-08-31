# -*- coding: utf-8 -*-
"""任务C回归：全库对齐垃圾图回扫.py ROOT参数化。
①--root覆盖：临时树（高中数学/高中数学同步/）内放 X1副本.docx（真实件）＋带jc命中合成件
  → scan 正常出清单（ROOT自查行＋命中行＋合计）＋退出码0；
②默认推导：直接跑 scan（脚本位于 提示词根/工具/ → ROOT=提示词根），扫描74件、出合计、退出码0。
"""
import os, sys, shutil, subprocess, zipfile

WS = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(WS))), '工具', '全库对齐垃圾图回扫.py')
PROMPT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(WS)))   # WS上三级＝提示词根

# ---- ① --root 覆盖 ＋ X1副本 ----
tree = os.path.join(WS, '回归C-root', '高中数学', '高中数学同步')
os.makedirs(tree, exist_ok=True)
shutil.copyfile(os.path.join(WS, '..', 'W-X1衔接1', 'X1工作副本.docx'), os.path.join(tree, 'X1副本.docx'))

CT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'''
RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
DOCREL = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'''
DOC = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
       '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
       '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:t>居中段落（scan应计jc非左1）</w:t></w:r></w:p>'
       '</w:body></w:document>')
syn = os.path.join(tree, '回归C-带命中.docx')
with zipfile.ZipFile(syn, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', CT)
    z.writestr('_rels/.rels', RELS)
    z.writestr('word/document.xml', DOC)
    z.writestr('word/_rels/document.xml.rels', DOCREL)

r = subprocess.run([sys.executable, TOOL, 'scan', '--root', os.path.join(WS, '回归C-root')],
                   capture_output=True, text=True, encoding='utf-8',
                   env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
print('①--root覆盖 退出码=%d' % r.returncode)
print(r.stdout.strip())
if r.returncode != 0:
    print(r.stderr[-2000:]); raise SystemExit('①失败')
out = r.stdout
assert ('ROOT=%s' % os.path.join(WS, '回归C-root')) in out, 'ROOT覆盖未生效'
assert '扫描2件' in out, '件数不符'
assert '回归C-带命中.docx | jc非左:1' in out, '命中清单行缺失'
assert '合计' in out
print('①PASS\n')

# ---- ② 默认推导（真库scan，只读不落盘） ----
r = subprocess.run([sys.executable, TOOL, 'scan'],
                   capture_output=True, text=True, encoding='utf-8',
                   env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
print('②默认推导 退出码=%d' % r.returncode)
lines = r.stdout.strip().splitlines()
print('\n'.join(lines[:6])); print('...(中间省略)...'); print('\n'.join(lines[-3:]))
if r.returncode != 0:
    print(r.stderr[-2000:]); raise SystemExit('②失败')
assert ('ROOT=%s' % PROMPT_ROOT) in lines[0], '默认推导不符: ' + lines[0]
import re as _re
m = _re.search(r'扫描(\d+)件', lines[0])
assert m and int(m.group(1)) == 74, '扫描件数≠74: ' + lines[0]
assert lines[-1].startswith('合计')
print('②PASS（默认ROOT正确推导至提示词根，74件全扫，合计落盘）')
print('任务C回归全部PASS')
