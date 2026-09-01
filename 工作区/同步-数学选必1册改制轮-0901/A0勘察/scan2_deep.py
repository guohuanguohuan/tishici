# -*- coding: utf-8 -*-
"""A0勘察第二轮：定点深挖疑点（只读）"""
import zipfile, json, re, io
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
BASE = r'C:\提示词\高中数学\高中数学同步'
FILES = {
 'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
 'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 'C':  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
 'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F':  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G':  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 'H':  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
LABEL_LINE = ('【答案】', '【知识点】')
BLOCK_HEAD = ('【分析】', '【详解】', '【点睛】', '【编注】', '【大招指引】', '【题后反思】', '【温馨提醒】')
RE_QIHAO = re.compile(r'^(\d+)\s*[．.](?!\d)')

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(W + 't'))

def pstyle(p):
    pPr = p.find(W + 'pPr')
    if pPr is None:
        return ''
    ps = pPr.find(W + 'pStyle')
    return ps.get(W + 'val', '') if ps is not None else ''

def first_sz(p):
    for r in p.iter(W + 'r'):
        if any((t.text or '') for t in r.findall(W + 't')):
            rpr = r.find(W + 'rPr')
            if rpr is not None and rpr.find(W + 'sz') is not None:
                return rpr.find(W + 'sz').get(W + 'val')
            return '-'
    return None  # 空段/无文本段

def classify(p, text):
    pPr = p.find(W + 'pPr')
    shd_p = None
    if pPr is not None:
        sh = pPr.find(W + 'shd')
        if sh is not None:
            shd_p = (sh.get(W + 'fill') or '').upper()
    ps = pstyle(p)
    is_title = (shd_p in ('ADC2DA', 'C6D4E3')) or ('标题' in ps) or re.search(r'(?i)heading', ps)
    m = RE_QIHAO.match(text)
    if m and not is_title:
        rest = text[m.end():].lstrip()
        return 'qihao' if rest.startswith('（') or rest.startswith('(') else 'tiaomu'
    if is_title:
        return 'title'
    for lab in LABEL_LINE + BLOCK_HEAD:
        if text.startswith(lab):
            return 'label'
    return 'other'

out = {}
for code, fn in FILES.items():
    z = zipfile.ZipFile(BASE + '\\' + fn)
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(W + 'body')
    o = {}

    # a) 图形态（正确命名空间）+ drawing子元素标签抽样
    n_inline = sum(1 for _ in doc.iter(WP + 'inline'))
    n_anchor = sum(1 for _ in doc.iter(WP + 'anchor'))
    tags = {}
    for dr in doc.iter(W + 'drawing'):
        for ch in dr:
            tags[etree.QName(ch).localname] = tags.get(etree.QName(ch).localname, 0) + 1
    o['img_wp'] = {'inline': n_inline, 'anchor': n_anchor, 'drawing_child_tags': tags}

    # b) sz × 段落分类交叉（正文流，不含表内）
    cross = {}
    for p in body.findall(W + 'p'):
        t = ptext(p)
        c = classify(p, t)
        s = first_sz(p)
        key = (c, s)
        cross[str(key)] = cross.get(str(key), 0) + 1
    o['sz_x_class'] = cross

    # c) P:AUTO 段落底纹挂点抽样（E/F/H/I2）
    auto_samples = []
    auto_by_class = {}
    for p in body.findall(W + 'p'):
        pPr = p.find(W + 'pPr')
        if pPr is None:
            continue
        sh = pPr.find(W + 'shd')
        if sh is None:
            continue
        fill = (sh.get(W + 'fill') or '').upper()
        if fill not in ('C9C9C9', 'ADC2DA', 'C6D4E3', 'F2F2F2'):
            t = ptext(p)
            c = classify(p, t)
            key = fill or 'EMPTY'
            auto_by_class[key + '/' + c] = auto_by_class.get(key + '/' + c, 0) + 1
            if len(auto_samples) < 5 and key == 'AUTO':
                auto_samples.append(t[:36])
    o['pshd_other_by_class'] = auto_by_class
    o['pshd_AUTO_samples'] = auto_samples

    # e) docDefaults 完整（rPr sz 有无；pPr line 完整）
    styles = etree.fromstring(z.read('word/styles.xml'))
    dd = styles.find(W + 'docDefaults')
    rpd = dd.find(W + 'rPrDefault/' + W + 'rPr') if dd is not None else None
    ppd = dd.find(W + 'pPrDefault/' + W + 'pPr') if dd is not None else None
    sz_dd = rpd.find(W + 'sz').get(W + 'val') if rpd is not None and rpd.find(W + 'sz') is not None else None
    line_dd = None
    if ppd is not None:
        sp = ppd.find(W + 'spacing')
        if sp is not None:
            line_dd = (sp.get(W + 'line'), sp.get(W + 'lineRule'), sp.get(W + 'before'), sp.get(W + 'after'))
    o['docDef'] = {'rPr_sz': sz_dd, 'pPr_line': line_dd}
    # Normal样式id与名称
    for st in styles.findall(W + 'style'):
        nm = st.find(W + 'name')
        if st.get(W + 'type') == 'paragraph' and nm is not None and (nm.get(W + 'val') or '').lower() in ('normal', '正文'):
            szn = st.find(W + 'rPr/' + W + 'sz')
            o['normal_id'] = {'id': st.get(W + 'styleId'), 'sz': szn.get(W + 'val') if szn is not None else None}
            break

    # f) 通式句验证
    n_ts = 0; n_idd = 0
    for t in (ptext(p) for p in body.findall(W + 'p')):
        if '题型通式' in t or '通式' in t:
            n_ts += 1
        if '识别信号' in t:
            n_idd += 1
    o['tongshi_check'] = {'含通式': n_ts, '含识别信号': n_idd}

    # g) 【答案】行文本抽样2条
    ans_s = []
    for p in body.findall(W + 'p'):
        t = ptext(p)
        if t.startswith('【答案】') and len(ans_s) < 2:
            ans_s.append(t[:70])
    o['ans_samples'] = ans_s

    # j) 讲部条目半角/全角分计 + 讲部标题样本（C6D4E3段）
    tm_half = 0; tm_full = 0
    for p in body.findall(W + 'p'):
        t = ptext(p)
        m = re.match(r'^(\d+)\s*[．.](?!\d)', t)
        if not m:
            continue
        c = classify(p, t)
        if c == 'tiaomu':
            if re.match(r'^\d+．', t):
                tm_full += 1
            else:
                tm_half += 1
    o['tiaomu_form'] = {'全角N．': tm_full, '半角N.': tm_half}

    # k) 节标题（ADC2DA段）pStyle抽样
    jie_ps = {}
    for p in body.findall(W + 'p'):
        pPr = p.find(W + 'pPr')
        if pPr is None:
            continue
        sh = pPr.find(W + 'shd')
        if sh is not None and (sh.get(W + 'fill') or '').upper() == 'ADC2DA':
            ps = pstyle(p) or '(none)'
            jie_ps[ps] = jie_ps.get(ps, 0) + 1
    o['jie_pstyle'] = jie_ps

    # I2杂色底纹抽样
    if code == 'I2':
        misc = []
        for p in body.findall(W + 'p'):
            pPr = p.find(W + 'pPr')
            if pPr is None:
                continue
            sh = pPr.find(W + 'shd')
            if sh is not None and (sh.get(W + 'fill') or '').upper() not in ('C9C9C9', 'ADC2DA', 'C6D4E3', 'F2F2F2', 'AUTO'):
                if len(misc) < 6:
                    misc.append(((sh.get(W + 'fill') or '').upper(), ptext(p)[:30]))
        o['i2_misc_shd'] = misc

    # G专项：题号块run继承链（Normal/样式sz解析）
    if code == 'G':
        # 找G的节标题段落（应为「2.6.1」等文本形态）——按文本正则找
        g_jie = []
        for p in body.findall(W + 'p'):
            t = ptext(p)
            if re.match(r'^2\.\d+(\.\d+)?\s', t) and len(t) < 60:
                pPr = p.find(W + 'pPr')
                sh = pPr.find(W + 'shd') if pPr is not None else None
                g_jie.append({'t': t[:44], 'pstyle': pstyle(p), 'sz': first_sz(p),
                              'shd': (sh.get(W + 'fill') if sh is not None else None)})
        o['g_jiebiaoti'] = g_jie[:12]
        # G样式表里含sz的段落样式
        gst = []
        for st in styles.findall(W + 'style'):
            szel = st.find(W + 'rPr/' + W + 'sz')
            if szel is not None:
                gst.append({'id': st.get(W + 'styleId'), 'name': (st.find(W + 'name').get(W + 'val') if st.find(W + 'name') is not None else ''), 'sz': szel.get(W + 'val')})
        o['g_styles_with_sz'] = gst[:12]

    out[code] = o
    z.close()

with io.open(r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\A0勘察\scan2_out.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('ok saved scan2_out.json')
