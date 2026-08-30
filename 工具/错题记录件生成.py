# -*- coding: utf-8 -*-
"""错题记录件生成.py — 2026-08-30 拍板独立错题记录件生成（可复用）

口径（公共规则§11错题记录件条款＋§7排版硬规则＋高中同步总控任务E，2026-08-30用户拍板改独立件）：
  每单位（章）一个独立 docx：A4／四边边距850缇（1.5厘米）／无页眉无页脚（配页件属性——
  不计页、不设页脚页码与页眉）／docDefaults 显式 宋体＋Times New Roman＋21半点（五号）／
  pPrDefault spacing 0-0-288-auto（行距1.2）／全部段落左对齐。
  内容＝①标题行（普通加粗段落「第X章 章名·错题记录」，不属标题体系）＋
        ②答案用法提醒句（整句挂 w:shd C9C9C9 底纹、不加粗）：
          「卡壳超过10分钟立即看答案学方法，不死磕；看懂后遮住答案重做」（2026-08-30 GN对齐§11文本：原常量尾多一句号，已去——T2裁决项③）＋
        ③三列表「题号｜错因｜重做日期」（表头行加粗＋C9C9C9底纹；表格细实线边框 single sz=4）＋
        ④错因示例行（表头行下小字说明行，合并3列、小五18半点、不加粗不进错题行计数）：
          「知识不会／方法没想到／计算错／审题错」＋
        ⑤40条空行（题号列留空由学生自填，行高320缇atLeast≈0.56cm，错题多者复印加页）。
  表格总行数断言＝42（表头1＋示例1＋空行40）；生成后自断言（XML级）＋提示 COM 开卷核单页。
用法: python 工具/错题记录件生成.py <册别> <章号> <章名> <输出docx>
  例: python 工具/错题记录件生成.py 人教B版选必1 1 空间向量与立体几何 "人教B版选必1·错题记录（第1章）.docx"
"""
import sys, os, zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

FILL = 'C9C9C9'
REMIND = '卡壳超过10分钟立即看答案学方法，不死磕；看懂后遮住答案重做'
EXAMPLE = '知识不会／方法没想到／计算错／审题错'
HEADERS = ['题号', '错因', '重做日期']
N_EMPTY = 40
ROW_H = 320            # 空行行高（缇，atLeast）
COLS = [2000, 5200, 3006]   # 题号｜错因｜重做日期（合计10206＝A4宽11906−850×2）
XMLNS = 'xmlns:w="%s"' % W

def _r(text, bold=False, shd=False, sz=None):
    rpr = ''
    if bold:
        rpr += '<w:b/>'
    if sz is not None:
        rpr += '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (sz, sz)
    if shd:
        rpr += '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % FILL
    rpr = '<w:rPr>%s</w:rPr>' % rpr if rpr else ''
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, text)

def _p(runs_xml, jc=True):
    ppr = '<w:pPr><w:jc w:val="left"/></w:pPr>' if jc else ''
    return '<w:p>%s%s</w:p>' % (ppr, runs_xml)

def _cell(w, runs_xml, gridspan=1):
    tcpr = '<w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s</w:tcPr>' % (
        w, '<w:gridSpan w:val="%d"/>' % gridspan if gridspan > 1 else '')
    return '<w:tc>%s%s</w:tc>' % (tcpr, _p(runs_xml))

def build_document_xml(ch_no, ch_name):
    title = '第%s章 %s·错题记录' % (ch_no, ch_name)
    # 表头行
    hdr = '<w:tr>' + ''.join(
        _cell(COLS[i], _r(HEADERS[i], bold=True, shd=True)) for i in range(3)) + '</w:tr>'
    # 错因示例行（合并3列、小字18半点）
    ex = ('<w:tr><w:trPr><w:trHeight w:val="280" w:hRule="atLeast"/></w:trPr>'
          + _cell(sum(COLS), _r(EXAMPLE, sz=18), gridspan=3) + '</w:tr>')
    # 40 空行（题号列留空）
    empties = ''.join(
        '<w:tr><w:trPr><w:trHeight w:val="%d" w:hRule="atLeast"/></w:trPr>%s</w:tr>'
        % (ROW_H, ''.join(_cell(wd, '') for wd in COLS)) for _ in range(N_EMPTY))
    borders = ''.join(
        '<w:%s w:val="single" w:sz="4" w:space="0" w:color="auto"/>' % s
        for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
    tbl = ('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>'
           '<w:tblBorders>%s</w:tblBorders>'
           '<w:tblLayout w:type="fixed"/></w:tblPr>'
           '<w:tblGrid>%s</w:tblGrid>%s%s%s</w:tbl>'
           % (sum(COLS), borders,
              ''.join('<w:gridCol w:w="%d"/>' % wd for wd in COLS), hdr, ex, empties))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document %s><w:body>'
            '%s%s%s'
            '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" '
            'w:header="283" w:footer="283" w:gutter="0"/></w:sectPr>'
            '</w:body></w:document>'
            % (XMLNS,
               _p(_r(title, bold=True)),
               _p(_r(REMIND, shd=True)),
               tbl))

STYLES_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<w:styles %s><w:docDefaults>'
              '<w:rPrDefault><w:rPr>'
              '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
              'w:eastAsia="宋体" w:cs="Times New Roman"/>'
              '<w:sz w:val="21"/><w:szCs w:val="21"/>'
              '<w:lang w:val="en-US" w:eastAsia="zh-CN"/>'
              '</w:rPr></w:rPrDefault>'
              '<w:pPrDefault><w:pPr>'
              '<w:spacing w:before="0" w:after="0" w:line="288" w:lineRule="auto"/>'
              '</w:pPr></w:pPrDefault>'
              '</w:docDefaults></w:styles>' % XMLNS)

CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                 '<Default Extension="xml" ContentType="application/xml"/>'
                 '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                 '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
                 '</Types>')

ROOT_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
             '</Relationships>')

DOC_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '</Relationships>')

def generate(book, ch_no, ch_name, out):
    assert re.match(r'^\d+$', str(ch_no)), '章号必须阿拉伯数字: %r' % ch_no
    doc_xml = build_document_xml(ch_no, ch_name)
    d = os.path.dirname(os.path.abspath(out))
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', CONTENT_TYPES)
        z.writestr('_rels/.rels', ROOT_RELS)
        z.writestr('word/_rels/document.xml.rels', DOC_RELS)
        z.writestr('word/document.xml', doc_xml)
        z.writestr('word/styles.xml', STYLES_XML)
    return doc_xml

def verify(out):
    """XML 级自断言（重读产出件）。返回断言清单 [(项, PASS/FAIL, 实测值)]。"""
    z = zipfile.ZipFile(out)
    names = z.namelist()
    doc = z.read('word/document.xml').decode('utf-8')
    sty = z.read('word/styles.xml').decode('utf-8')
    root = etree.fromstring(doc.encode('utf-8'))
    a = []
    # 包级：无页眉页脚部件、无引用
    hf_parts = [n for n in names if re.match(r'word/(header|footer)\d*\.xml$', n)]
    a.append(('无页眉/页脚部件', not hf_parts, str(hf_parts)))
    a.append(('无headerReference/footerReference',
              'headerReference' not in doc and 'footerReference' not in doc, ''))
    # 页面：A4＋850四边
    a.append(('pgSz A4 11906×16838',
              '<w:pgSz w:w="11906" w:h="16838"/>' in doc, ''))
    a.append(('pgMar 四边850',
              all(('w:%s="850"' % s) in doc for s in ('top', 'right', 'bottom', 'left')), ''))
    # docDefaults：宋体+TNR+21半点；pPrDefault 0-0-288-auto
    a.append(('docDefaults 宋体+TNR',
              'w:eastAsia="宋体"' in sty and 'w:ascii="Times New Roman"' in sty, ''))
    a.append(('docDefaults 21半点', '<w:sz w:val="21"/>' in sty, ''))
    a.append(('pPrDefault 0-0-288-auto',
              '<w:spacing w:before="0" w:after="0" w:line="288" w:lineRule="auto"/>' in sty, ''))
    # 内容：标题行/提醒句底纹/表格42行
    txts = [''.join(t.text or '' for t in p.iter(q('t'))) for p in root.iter(q('p'))]
    nonempty = [t for t in txts if t.strip()]
    a.append(('标题行在位', any(re.match(r'^第\d+章 .+·错题记录$', t) for t in nonempty), str(nonempty[:1])))
    a.append(('提醒句在位', REMIND in nonempty, ''))
    tbls = root.findall('.//' + q('tbl'))
    rows = tbls[0].findall(q('tr')) if tbls else []
    a.append(('表格唯一', len(tbls) == 1, str(len(tbls))))
    a.append(('表格行数42=表头1+示例1+空40', len(rows) == 1 + 1 + N_EMPTY, str(len(rows))))
    hdr_cells = rows[0].findall(q('tc')) if rows else []
    hdr_txt = [''.join(t.text or '' for t in c.iter(q('t'))) for c in hdr_cells]
    a.append(('表头三列文字', hdr_txt == HEADERS, str(hdr_txt)))
    hdr_bold = all(c.find('.//' + q('rPr')).find(q('b')) is not None for c in hdr_cells) if hdr_cells else False
    hdr_shd = all(c.find('.//' + q('shd')).get(q('fill')) == FILL
                  for c in hdr_cells if c.find('.//' + q('shd')) is not None) and len(hdr_cells) == 3
    a.append(('表头加粗', hdr_bold, ''))
    a.append(('表头C9C9C9底纹', hdr_shd, ''))
    a.append(('细实线边框 single sz=4',
              doc.count('<w:insideH w:val="single" w:sz="4"') == 1
              and doc.count('<w:insideV w:val="single" w:sz="4"') == 1
              and doc.count('<w:top w:val="single" w:sz="4"') == 1, ''))
    ex_txt = ''.join(t.text or '' for t in rows[1].iter(q('t'))) if len(rows) > 1 else ''
    a.append(('错因示例行在位（小字18）', ex_txt == EXAMPLE and '<w:sz w:val="18"/>' in doc, ex_txt[:24]))
    empty_ok = all(not ''.join(t.text or '' for t in tr.iter(q('t'))).strip()
                   for tr in rows[2:])
    a.append(('空行40条全空（题号列留空）', empty_ok and len(rows) - 2 == N_EMPTY, ''))
    # 全左对齐
    n_jc = doc.count('<w:jc w:val="left"/>')
    n_p = doc.count('<w:p>') + doc.count('<w:p ')
    a.append(('全段落左对齐（%d/%d）' % (n_jc, n_p), n_jc == n_p, ''))
    return a

def main():
    book, ch_no, ch_name, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    generate(book, ch_no, ch_name, out)
    a = verify(out)
    for n, ok, extra in a:
        print('  ', 'PASS' if ok else 'FAIL', n, ('｜' + extra) if (extra and not ok) else '')
    bad = [n for n, ok, _ in a if not ok]
    print('错题记录件生成：%s（第%s章 %s）→ %s ｜断言 %d/%d %s'
          % (book, ch_no, ch_name, out, len(a) - len(bad), len(a),
             'ALL PASS' if not bad else 'FAIL:' + ';'.join(bad)))

if __name__ == '__main__':
    main()
