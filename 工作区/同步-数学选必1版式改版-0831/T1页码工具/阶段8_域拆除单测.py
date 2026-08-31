# -*- coding: utf-8 -*-
"""阶段8子进程：页脚域拆除单测——rebuild_footer 对三种旧起态（PAGE+NUMPAGES复杂域并存、
fldSimple、多段落页脚）均整段重建为新文案、无NUMPAGES/fldSimple残留。"""
import sys, os, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import importlib.util

spec = importlib.util.spec_from_file_location('myl', r'C:\Users\28120\Desktop\提示词\工具\册级连续页码.py')
myl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(myl)
sys.stdout = io.TextIOWrapper(os.fdopen(1, 'wb', closefd=False), encoding='utf-8', line_buffering=True)

HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
RPR21 = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>'
         '<w:sz w:val="21"/></w:rPr>')
def r(t, pr=RPR21):
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (pr, t)
FLD = ('<w:r>%s<w:fldChar w:fldCharType="begin"/></w:r><w:r>%s<w:instrText xml:space="preserve"> NUMPAGES </w:instrText></w:r>'
       '<w:r>%s<w:fldChar w:fldCharType="separate"/></w:r><w:r>%s<w:t>433</w:t></w:r>'
       '<w:r>%s<w:fldChar w:fldCharType="end"/></w:r>') % (RPR21, RPR21, RPR21, RPR21, RPR21)
P_SIMPLE = '<w:p><w:pPr><w:jc w:val="left"/></w:pPr><w:fldSimple w:instr=" PAGE "><w:r>%s<w:t>5</w:t></w:r></w:fldSimple></w:p>' % RPR21

cases = {
    'PAGE+NUMPAGES复杂域并存': HDR + '<w:p><w:pPr><w:jc w:val="left"/></w:pPr>'
        + r('第1章·讲练　第') + myl.page_field(37) + r('页（全册共') + FLD + r('页）') + '</w:p></w:ftr>',
    'fldSimple页码': HDR + P_SIMPLE + '</w:ftr>',
    '多段落页脚': HDR + '<w:p>' + r('旧串件标识　第1页') + '</w:p><w:p>' + r('第二段多余内容') + '</w:p></w:ftr>',
}
for name, ftr in cases.items():
    out = myl.rebuild_footer(ftr, 80, 155, '第1章·讲练')
    vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', out))
    ok = (vis == '第1章·讲练（共155页）　第80页'
          and out.count('fldCharType="begin"') == 1 and out.count('fldCharType="end"') == 1
          and 'NUMPAGES' not in out and 'fldSimple' not in out
          and '<w:jc w:val="left"/>' in out and out.count('<w:sz w:val="18"/>') >= 6)
    print('  %s %s -> 可见文本=%r 域b/e=1 无NUMPAGES/fldSimple=%s'
          % ('PASS' if ok else 'FAIL', name, vis, 'NUMPAGES' not in out and 'fldSimple' not in out))
    assert ok, name
print('阶段8完成：3种旧起态整段重建全过（NUMPAGES/fldSimple拆除验证）')
