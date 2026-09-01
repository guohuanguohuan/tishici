# -*- coding: utf-8 -*-
# 独立断言（不复用工具内部逻辑）：挂载+盖章后三件副本的锚/域/版面/N/start实测
import sys, io, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def q(t): return '{%s}%s' % (W, t)

CASES = [  # (文件, 件型尾段, N期望, start期望, 章段)
    ('X2挂载.docx', '衔接', 4, 1, '第2章'),
    ('B挂载.docx', '讲练', 156, 1, '第1章'),
    ('C挂载.docx', '讲练', 156, 79, '第1章'),
]
BRAND = '羿郭工作室·'

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

fails = []
def ck(cond, msg):
    print(('  [OK] ' if cond else '  [FAIL] ') + msg)
    if not cond:
        fails.append(msg)

for path, suffix, n_exp, start_exp, chap in CASES:
    print('=' * 66)
    print('##', path)
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    styles = etree.fromstring(z.read('word/styles.xml'))
    body = doc.find(q('body'))
    docx_s = z.read('word/document.xml').decode('utf-8')
    settings = z.read('word/settings.xml').decode('utf-8')

    # Normal真实styleId
    normal = None
    for st in styles.findall(q('style')):
        nm = st.find(q('name'))
        if st.get(q('type')) == 'paragraph' and nm is not None and (nm.get(q('val')) or '').lower() == 'normal':
            normal = st.get(q('styleId'))
    print('  Normal styleId =', normal)

    # 节标题与锚段
    sid3 = None
    for st in styles.findall(q('style')):
        nm = st.find(q('name'))
        if nm is not None and (nm.get(q('val')) or '').strip().lower() in ('heading 3', '标题 3', '标题3'):
            sid3 = st.get(q('styleId'))
    secs, anchors = [], []
    for p in body.iter(q('p')):
        ppr = p.find(q('pPr'))
        ps = ppr.find(q('pStyle')) if ppr is not None else None
        if ps is None:
            continue
        v = ps.get(q('val'))
        if v == sid3:
            secs.append(p)
        if v == 'JieMingMao':
            anchors.append(p)
    ck(len(anchors) == len(secs), '锚段数=%d = 节标题数=%d' % (len(anchors), len(secs)))
    ck(all(a.getnext() is p for a, p in zip(anchors, secs)), '锚段逐节标题直接前驱（%d/%d）' % (sum(1 for a, p in zip(anchors, secs) if a.getnext() is p), len(secs)))
    # 锚段形态：1pt白、无隐藏、无底纹边框、无禁排属性；内容=节标题剥统计段
    a_ok = v_ok = f_ok = txt_ok = 0
    stat = re.compile(r'（第\d+(?:[—–-]\d+)?题|　?本节\d+题')
    for a, s in zip(anchors, secs):
        rpr = a.find(q('r')).find(q('rPr')) if a.find(q('r')) is not None else None
        if rpr is not None and rpr.find(q('color')) is not None and rpr.find(q('color')).get(q('val')) == 'FFFFFF':
            c_ok = True
            szs = [e.get(q('val')) for e in rpr.findall(q('sz'))] or None
            if szs is None:  # 走样式解析
                szs = [e.get(q('val')) for e in a.iter(q('sz'))]
            c_ok = c_ok and szs and szs[0] == '2'
            a_ok += 1 if c_ok else 0
        if a.find('.//%s' % q('vanish')) is None and a.find('.//%s' % q('shd')) is None and a.find('.//%s' % q('pBdr')) is None:
            v_ok += 1
        ppr = a.find(q('pPr'))
        sp = ppr.find(q('spacing')) if ppr is not None else None
        if sp is not None and sp.get(q('line')) == '20' and sp.get(q('lineRule')) == 'exact' \
           and ppr.find(q('keepNext')) is None and ppr.find(q('keepLines')) is None:
            f_ok += 1
        title = para_text(s)
        m = stat.search(title)
        expect = (title[:m.start()] if m else title).rstrip('　 ')
        if para_text(a) == expect:
            txt_ok += 1
    ck(a_ok == len(anchors), '锚段1pt白字（sz=2半点）=%d/%d' % (a_ok, len(anchors)))
    ck(v_ok == len(anchors), '锚段无隐藏/底纹/边框=%d/%d' % (v_ok, len(anchors)))
    ck(f_ok == len(anchors), '锚段line=20 exact＋无禁排属性=%d/%d' % (f_ok, len(anchors)))
    ck(txt_ok == len(anchors), '锚段内容=节号节名（剥统计段）=%d/%d' % (txt_ok, len(anchors)))

    # 锚样式
    stl = None
    for st in styles.findall(q('style')):
        if st.get(q('styleId')) == 'JieMingMao':
            stl = st
    ck(stl is not None, '锚样式JieMingMao在位')
    if stl is not None:
        nm = stl.find(q('name'))
        bo = stl.find(q('basedOn'))
        sp = stl.find(q('pPr')).find(q('spacing'))
        rpr = stl.find(q('rPr'))
        ck(nm is not None and nm.get(q('val')) == '节名锚', '锚样式name=节名锚（STYLEREF按名解析）')
        ck(bo is not None and bo.get(q('val')) == normal, '锚样式basedOn=%s=真实Normal（非字面量悬空）' % normal)
        ck(sp is not None and sp.get(q('line')) == '20' and sp.get(q('lineRule')) == 'exact', '锚样式行距固定1磅')
        ck(rpr is not None and rpr.find(q('color')).get(q('val')) == 'FFFFFF' and rpr.find(q('sz')).get(q('val')) == '2'
           and rpr.find(q('vanish')) is None, '锚样式1pt白非隐藏')

    # 页眉页脚同串
    rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    relmap = {r_.get('Id'): r_.get('Target') for r_ in rels}
    hrefs = [h for h in doc.iter(q('headerReference'))]
    frefs = [f for f in doc.iter(q('footerReference'))]
    ck(len(hrefs) == 1 and len(frefs) == 1, '单页眉+单页脚引用（%d/%d）' % (len(hrefs), len(frefs)))
    first_anchor_txt = para_text(anchors[0]) if anchors else None
    for ref, kind in ((hrefs[0], 'header'), (frefs[0], 'footer')):
        nmz = 'word/' + relmap[ref.get('{%s}id' % R)].lstrip('/')
        xml = z.read(nmz).decode('utf-8')
        root = etree.fromstring(z.read(nmz))
        paras = root.findall(q('p'))
        vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml))
        m = re.fullmatch(r'(.+)（共(\d+)页）　(.+)　第(\d+)页', vis)
        ck(len(paras) == 1, '%s单段' % kind)
        jc = paras[0].find(q('pPr')).find(q('jc'))
        ck(jc is not None and jc.get(q('val')) == 'left', '%s jc=left' % kind)
        flds = [fc.get(q('fldCharType')) for fc in root.iter(q('fldChar'))]
        instrs = [it.text for it in root.iter(q('instrText'))]
        ck(flds == ['begin', 'separate', 'end', 'begin', 'separate', 'end'], '%s 两组复杂域序=%s' % (kind, flds))
        ck(any('STYLEREF' in (i or '') and '节名锚' in (i or '') for i in instrs), '%s STYLEREF"节名锚"域=%r' % (kind, instrs))
        ck(any(re.fullmatch(r'\s*PAGE\s*', i or '') for i in instrs), '%s PAGE域' % kind)
        ck('fldSimple' not in xml and 'NUMPAGES' not in xml, '%s 无fldSimple/NUMPAGES' % kind)
        szs = set(re.findall(r'<w:sz w:val="(\d+)"/>', xml))
        ck(szs == {'18'}, '%s 全run=18半点(9pt): %r' % (kind, sorted(szs)))
        ck('宋体' in xml and 'Times New Roman' in xml, '%s 宋体+TNR' % kind)
        ck(m is not None and int(m.group(2)) == n_exp, '%s N=%s（期望%d）' % (kind, m.group(2) if m else '?', n_exp))
        ck(m is not None and int(m.group(4)) == start_exp, '%s X缓存=%s（期望%d）' % (kind, m.group(4) if m else '?', start_exp))
        ck(m is not None and m.group(1).endswith(suffix) and chap in m.group(1), '%s 前段=%r' % (kind, m.group(1) if m else '?'))
        ck(m is not None and m.group(3) == first_anchor_txt, '%s 节名缓存=首锚段文本' % kind)
    # 页眉页脚同内容（可见文本一致）
    h_xml = z.read('word/' + relmap[hrefs[0].get('{%s}id' % R)].lstrip('/')).decode('utf-8')
    f_xml = z.read('word/' + relmap[frefs[0].get('{%s}id' % R)].lstrip('/')).decode('utf-8')
    vis_h = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', h_xml))
    vis_f = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', f_xml))
    ck(vis_h == vis_f, '页眉=页脚同串（可见文本一致）')

    # sectPr
    sp_ = body.findall(q('sectPr'))[-1]
    mar = sp_.find(q('pgMar'))
    pnt = sp_.find(q('pgNumType'))
    ck(mar.get(q('header')) == '283' and mar.get(q('footer')) == '850', 'pgMar header=283 footer=850')
    ck(pnt is not None and pnt.get(q('start')) == str(start_exp), 'pgNumType start=%s（期望%d）' % (pnt.get(q('start')) if pnt is not None else '?', start_exp))
    ck('<w:titlePg' not in docx_s, '无titlePg')
    ck('<w:updateFields' in settings and 'evenAndOddHeaders' not in settings, 'settings updateFields+无奇偶页不同')
    z.close()

print('=' * 66)
print('独立断言总结：', 'ALL PASS' if not fails else 'FAIL %d项' % len(fails))
for f_ in fails:
    print('  -', f_)
sys.exit(0 if not fails else 1)
