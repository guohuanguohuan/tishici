# -*- coding: utf-8 -*-
"""A0勘察：选必1册十件内容件XML级现状勘察（只读，不写任何docx）
输出：A0勘察/scan_out.json + 控制台摘要
口径注记：字号=显式w:sz出现处计数（w:r与m:r的rPr内均计，w:szCs不重复计）；
解析块清点=body直接子级段落流分类统计（表格内段落不入解析块计数，单独计）。"""
import zipfile, json, re, sys, io
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
PR = '{http://schemas.openxmlformats.org/package/2006/relationships}'

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
FOUR = ('C9C9C9', 'ADC2DA', 'C6D4E3', 'F2F2F2')
LABEL_LINE = ('【答案】', '【知识点】')          # 单行标签行
BLOCK_HEAD = ('【分析】', '【详解】', '【点睛】', '【编注】', '【大招指引】', '【题后反思】', '【温馨提醒】')
RE_QIHAO = re.compile(r'^(\d+)\s*[．.](?!\d)')   # 段首 N．
BLUE = '1F4E79'

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(W + 't'))

def para_has_omml(p):
    return any(True for _ in p.iter(M + 'oMath'))

def para_has_drawing(p):
    return any(True for _ in p.iter(W + 'drawing'))

def classify(p, text):
    """段落流分类（body直接子级）"""
    st = (p.find(W + 'pPr/' + W + 'pStyle') is not None)
    pPr = p.find(W + 'pPr')
    pstyle = ''
    if pPr is not None:
        ps = pPr.find(W + 'pStyle')
        if ps is not None:
            pstyle = ps.get(W + 'val', '')
    shd_p = None
    if pPr is not None:
        sh = pPr.find(W + 'shd')
        if sh is not None:
            shd_p = (sh.get(W + 'fill') or '').upper()
    # 结构标题判定：段落级 ADC2DA/C6D4E3 或 pStyle Heading/标题
    is_title = (shd_p in ('ADC2DA', 'C6D4E3')) or bool(re.search(r'(?i)heading|jiebiaoti|beijingbiaoti', pstyle)) or ('标题' in pstyle)
    m = RE_QIHAO.match(text)
    if m and not is_title:
        rest = text[m.end():].lstrip()
        if rest.startswith('（') or rest.startswith('('):
            return 'qihao'          # 题号块（带括注）
        return 'tiaom'              # 疑似条目号（无括注）
    if is_title:
        return 'title'
    for lab in LABEL_LINE:
        if text.startswith(lab):
            return 'ansline'
    for lab in BLOCK_HEAD:
        if text.startswith(lab):
            return 'blockhead'
    if '题型通式' in text:
        return 'tongshi'
    return 'other'

def scan(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    out = {'file': path.split('\\')[-1]}
    doc = etree.fromstring(z.read('word/document.xml'))
    styles = etree.fromstring(z.read('word/styles.xml'))
    settings = etree.fromstring(z.read('word/settings.xml')) if 'word/settings.xml' in names else None

    # ---- run字号分布（document正文；w:r与m:r挂点分记）----
    szdist = {}
    sz_math = {}
    nosz = 0
    for rpr in doc.iter(W + 'rPr'):
        par = rpr.getparent()
        sz = rpr.find(W + 'sz')
        if sz is None:
            continue
        v = sz.get(W + 'val')
        tag = etree.QName(par).localname
        if tag == 'r':
            szdist[v] = szdist.get(v, 0) + 1
        elif tag == 'r' and False:
            pass
        else:
            sz_math[v] = sz_math.get(v, 0) + 1
    # 无显式sz的正文run（w:r且有文本）
    for r in doc.iter(W + 'r'):
        if not any((t.text or '') for t in r.findall(W + 't')):
            continue
        rpr = r.find(W + 'rPr')
        if rpr is None or rpr.find(W + 'sz') is None:
            nosz += 1
    out['sz_dist'] = dict(sorted(szdist.items(), key=lambda x: -x[1]))
    out['sz_math_r'] = sz_math
    out['run_nosz'] = nosz

    # ---- 段落spacing分布（document，含表格；分body直接子级与表内）----
    def spacing_of(p):
        pPr = p.find(W + 'pPr')
        if pPr is None:
            return 'NO_PPR'
        sp = pPr.find(W + 'spacing')
        if sp is None:
            return 'inherit'
        ln = sp.get(W + 'line'); lr = sp.get(W + 'lineRule') or '(none)'
        before = sp.get(W + 'before'); after = sp.get(W + 'after')
        return f'line={ln}/{lr}/b={before}/a={after}'
    sp_body = {}; sp_tbl = {}
    body = doc.find(W + 'body')
    tbl_paras = {}
    for tbl in body.iter(W + 'tbl'):
        for p in tbl.iter(W + 'p'):
            tbl_paras[id(p)] = p
    for p in body.findall(W + 'p'):
        k = spacing_of(p); sp_body[k] = sp_body.get(k, 0) + 1
    for p in tbl_paras.values():
        k = spacing_of(p); sp_tbl[k] = sp_tbl.get(k, 0) + 1
    out['spacing_body'] = sp_body
    out['spacing_tbl'] = sp_tbl

    # ---- docGrid / sectPr ----
    sects = []
    for sect in doc.iter(W + 'sectPr'):
        pg = sect.find(W + 'pgSz')
        mar = sect.find(W + 'pgMar')
        dg = sect.find(W + 'docGrid')
        sects.append({
            'pgSz': (pg.get(W + 'w'), pg.get(W + 'h')) if pg is not None else None,
            'header': mar.get(W + 'header') if mar is not None else None,
            'footer': mar.get(W + 'footer') if mar is not None else None,
            'mar': [mar.get(W + k) for k in ('top', 'right', 'bottom', 'left')] if mar is not None else None,
            'docGrid': ({'type': dg.get(W + 'type'), 'linePitch': dg.get(W + 'linePitch')} if dg is not None else None),
        })
    out['sects'] = sects

    # ---- docDefaults / Normal ----
    dd = styles.find(W + 'docDefaults')
    def rpr_dump(rpr):
        if rpr is None:
            return None
        d = {}
        for el in rpr:
            t = etree.QName(el).localname
            d[t] = dict(el.attrib)
        return d
    if dd is not None:
        rpd = dd.find(W + 'rPrDefault/' + W + 'rPr')
        ppd = dd.find(W + 'pPrDefault/' + W + 'pPr')
        out['docDefaults_rPr'] = rpr_dump(rpd)
        out['docDefaults_pPr'] = rpr_dump(ppd)
    normal = None
    for st in styles.findall(W + 'style'):
        if st.get(W + 'type') == 'paragraph' and st.find(W + 'name') is not None and st.find(W + 'name').get(W + 'val') in ('Normal', 'normal', '正文'):
            normal = {'id': st.get(W + 'styleId'), 'rPr': rpr_dump(st.find(W + 'rPr')), 'pPr': rpr_dump(st.find(W + 'pPr'))}
            break
    out['normal'] = normal
    # 样式「节名锚」存在性
    anchor_style = [st.get(W + 'styleId') for st in styles.findall(W + 'style') if st.find(W + 'name') is not None and '节名锚' in (st.find(W + 'name').get(W + 'val') or '')]
    out['anchor_style_ids'] = anchor_style

    # ---- 四色底纹：run级（w:r与m:r挂点分记）/段落级 ----
    shd_run = {c: 0 for c in FOUR}; shd_run_math = {c: 0 for c in FOUR}
    shd_para = {c: 0 for c in FOUR}; shd_other_run = {}
    for sh in doc.iter(W + 'shd'):
        fill = (sh.get(W + 'fill') or '').upper()
        par = sh.getparent().getparent()
        if etree.QName(sh.getparent()).localname == 'pPr':
            # 段落级
            if fill in FOUR:
                shd_para[fill] += 1
            else:
                shd_other_run.setdefault('P:' + (fill or 'EMPTY'), 0)
                shd_other_run['P:' + (fill or 'EMPTY')] += 1
            continue
        tag = etree.QName(par).localname
        if fill in FOUR:
            if tag == 'r':
                shd_run[fill] += 1
            else:
                shd_run_math[fill] += 1
        else:
            shd_other_run[fill or 'EMPTY'] = shd_other_run.get(fill or 'EMPTY', 0) + 1
    out['shd_run'] = shd_run; out['shd_run_math'] = shd_run_math
    out['shd_para'] = shd_para
    out['shd_other'] = shd_other_run

    # ---- 图形态 ----
    n_inline = sum(1 for _ in doc.iter(W + 'inline'))
    n_anchor = sum(1 for _ in doc.iter(W + 'anchor'))
    n_drawing = sum(1 for _ in doc.iter(W + 'drawing'))
    n_pict = sum(1 for _ in doc.iter(W + 'pict'))
    media = [n for n in names if n.startswith('word/media/')]
    rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    rel_img = [rl for rl in rels if 'image' in (rl.get('Type') or '')]
    out['img'] = {'inline': n_inline, 'anchor': n_anchor, 'drawing': n_drawing, 'pict': n_pict,
                  'media': len(media), 'rels_img': len(rel_img)}

    # ---- 段落流分类（题号/条目/解析块清点/节标题）----
    paras = body.findall(W + 'p')
    seq = []
    texts = []
    for p in paras:
        t = ptext(p)
        texts.append(t)
        seq.append(classify(p, t))
    n_qihao = seq.count('qihao'); n_tiaom = seq.count('tiaom')
    n_ansline = seq.count('ansline'); n_blockhead = seq.count('blockhead')
    n_tongshi = seq.count('tongshi'); n_title = seq.count('title')
    # 解析块段落清点：ansline + blockhead + 各块后续段（到边界止） + tongshi
    n_block_body = 0
    for i, c in enumerate(seq):
        if c == 'blockhead':
            j = i + 1
            while j < len(seq) and seq[j] == 'other':
                n_block_body += 1
                j += 1
        elif c == 'ansline':
            j = i + 1
            while j < len(seq) and seq[j] == 'other':   # 折行的答案行续段（罕见）也计入
                n_block_body += 1
                j += 1
    # 标签分类型计数
    lab_counts = {}
    for t in texts:
        for lab in LABEL_LINE + BLOCK_HEAD:
            if t.startswith(lab):
                lab_counts[lab] = lab_counts.get(lab, 0) + 1
                break
    out['counts'] = {'qihao_blocks': n_qihao, 'tiaomu_like': n_tiaom, 'ansline': n_ansline,
                     'blockhead': n_blockhead, 'tongshi': n_tongshi, 'title_paras': n_title,
                     'block_follow_paras': n_block_body,
                     'jiexi_para_total': n_ansline + n_blockhead + n_block_body + n_tongshi,
                     'total_paras': len(paras)}
    out['label_counts'] = lab_counts

    # 三段式/两段式形态
    san = 0; liang = 0; other_qh = 0
    qh_samples = []
    for i, c in enumerate(seq):
        if c != 'qihao':
            continue
        t = texts[i]
        rest = RE_QIHAO.sub('', t)[:40]
        if '衔接必会' in t:
            liang += 1
        elif t.count('·') >= 2:
            san += 1
        else:
            other_qh += 1
        if len(qh_samples) < 3 or i > len(seq) - 3:
            qh_samples.append(t[:60])
    out['qihao_form'] = {'三段式(两·)': san, '两段式(衔接必会)': liang, '其他': other_qh, 'samples': qh_samples[:6]}

    # 题号块底纹/加粗抽样（前3后1）
    qh_fmt = []
    idxs = [i for i, c in enumerate(seq) if c == 'qihao']
    pick = idxs[:3] + idxs[-1:] if idxs else []
    for i in pick:
        p = paras[i]
        runs = p.findall(W + 'r')
        info = []
        for r_ in runs[:3]:
            rpr = r_.find(W + 'rPr')
            b = rpr is not None and rpr.find(W + 'b') is not None and rpr.find(W + 'b').get(W + 'val') != '0'
            sh = rpr.find(W + 'shd') if rpr is not None else None
            szv = rpr.find(W + 'sz').get(W + 'val') if rpr is not None and rpr.find(W + 'sz') is not None else '-'
            txt = ''.join(tt.text or '' for tt in r_.findall(W + 't'))[:16]
            info.append({'t': txt, 'b': bool(b), 'shd': (sh.get(W + 'fill') if sh is not None else None), 'sz': szv})
        qh_fmt.append(info)
    out['qihao_fmt_samples'] = qh_fmt

    # 条目号形态抽样（前3）
    tm_fmt = []
    tmidx = [i for i, c in enumerate(seq) if c == 'tiaom']
    for i in tmidx[:3]:
        p = paras[i]
        runs = p.findall(W + 'r')
        info = []
        for r_ in runs[:2]:
            rpr = r_.find(W + 'rPr')
            b = rpr is not None and rpr.find(W + 'b') is not None and rpr.find(W + 'b').get(W + 'val') != '0'
            sh = rpr.find(W + 'shd') if rpr is not None else None
            txt = ''.join(tt.text or '' for tt in r_.findall(W + 't'))[:16]
            info.append({'t': txt, 'b': bool(b), 'shd': (sh.get(W + 'fill') if sh is not None else None)})
        tm_fmt.append({'text': texts[i][:40], 'runs': info})
    out['tiaomu_samples'] = tm_fmt
    out['tiaomu_total'] = len(tmidx)

    # 节标题数（三口径）：pStyle含3/heading3、首run sz=28、段落级ADC2DA
    def is_jie_by_style(p):
        pPr = p.find(W + 'pPr')
        if pPr is None:
            return False
        ps = pPr.find(W + 'pStyle')
        return ps is not None and re.search(r'(?i)(heading3|3$|jie)', ps.get(W + 'val') or '') is not None
    n_style3 = 0; n_sz28 = 0; n_adc = 0
    jie_samples = []
    for i, p in enumerate(paras):
        st = is_jie_by_style(p)
        # 首个含文本run的sz
        szv = None
        for r_ in p.iter(W + 'r'):
            if any((t.text or '') for t in r_.findall(W + 't')):
                rpr = r_.find(W + 'rPr')
                if rpr is not None and rpr.find(W + 'sz') is not None:
                    szv = r_.find(W + 'rPr').find(W + 'sz').get(W + 'val')
                break
        pPr = p.find(W + 'pPr')
        adc = False
        if pPr is not None:
            sh = pPr.find(W + 'shd')
            adc = sh is not None and (sh.get(W + 'fill') or '').upper() == 'ADC2DA'
        if st:
            n_style3 += 1
        if szv == '28':
            n_sz28 += 1
        if adc:
            n_adc += 1
        if adc and len(jie_samples) < 4:
            jie_samples.append(texts[i][:70])
    out['jiebiaoti'] = {'by_style3': n_style3, 'by_sz28': n_sz28, 'by_adc_para': n_adc, 'samples': jie_samples}

    # 答案值清点与现挂法
    ans_lines = 0; ans_with_math = 0; ans_blue_runs = 0; ans_grey_runs = 0
    blue_total = 0; blue_math_total = 0
    for i, c in enumerate(seq):
        if c == 'ansline' and texts[i].startswith('【答案】'):
            ans_lines += 1
            if para_has_omml(paras[i]):
                ans_with_math += 1
            for sh in paras[i].iter(W + 'shd'):
                if (sh.get(W + 'fill') or '').upper() == 'C9C9C9':
                    ans_grey_runs += 1
        if c == 'ansline':
            for co in paras[i].iter(W + 'color'):
                if (co.get(W + 'val') or '').upper() == BLUE:
                    ans_blue_runs += 1
    for co in doc.iter(W + 'color'):
        if (co.get(W + 'val') or '').upper() == BLUE:
            par = co.getparent().getparent()
            if etree.QName(par).localname == 'r':
                blue_total += 1
            else:
                blue_math_total += 1
    out['answer'] = {'ans_label_lines': lab_counts.get('【答案】', 0), 'ans_lines_flow': ans_lines,
                     'ans_lines_with_omml': ans_with_math, 'grey_runs_in_ansline': ans_grey_runs,
                     'blue_runs_in_ansline': ans_blue_runs,
                     'blue_runs_doc_total(w:r)': blue_total, 'blue_runs_math_total(m:r等)': blue_math_total}

    # ---- 章首导航表 ----
    nav = []
    for tbl in body.findall(W + 'tbl'):
        first = ''
        for p in tbl.iter(W + 'p'):
            first = ptext(p)
            break
        alltxt = ''.join(ptext(p) for p in tbl.iter(W + 'p'))[:80]
        if '导航' in alltxt or ('节' in first and ('题量' in alltxt or '简单' in alltxt)):
            szs = {}
            sps = {}
            for p in tbl.iter(W + 'p'):
                k = spacing_of(p)
                sps[k] = sps.get(k, 0) + 1
            for szel in tbl.iter(W + 'sz'):
                v = szel.get(W + 'val')
                szs[v] = szs.get(v, 0) + 1
            # 表头行底纹
            head_shd = []
            for tr in tbl.findall(W + 'tr')[:1]:
                for sh in tr.iter(W + 'shd'):
                    head_shd.append((sh.get(W + 'fill') or '').upper())
            nav.append({'first_row': first[:30], 'sz_dist': szs, 'spacing': sps, 'head_shd': head_shd[:6]})
    out['nav_tables'] = nav

    # ---- 页眉页脚 ----
    hf = {}
    for n in names:
        if re.match(r'word/(header|footer)\d*\.xml', n):
            x = etree.fromstring(z.read(n))
            txts = [t.text or '' for t in x.iter(W + 't')]
            instr = [t.text or '' for t in x.iter(W + 'instrText')]
            fldchar = len([f for f in x.iter(W + 'fldChar')])
            fldsimple = len([f for f in x.iter(W + 'fldSimple')])
            szs = {}
            for szel in x.iter(W + 'sz'):
                v = szel.get(W + 'val')
                szs[v] = szs.get(v, 0) + 1
            sps = {}
            for p in x.iter(W + 'p'):
                k = spacing_of(p)
                sps[k] = sps.get(k, 0) + 1
            hf[n.split('/')[-1]] = {'text': ''.join(txts)[:200], 'instr': instr, 'fldChar': fldchar,
                                   'fldSimple': fldsimple, 'sz': szs, 'spacing': sps}
    out['headerfooter'] = hf
    out['settings_updateFields'] = (settings is not None and settings.find(W + 'updateFields') is not None)
    out['names_hf_parts'] = [n for n in names if re.match(r'word/(header|footer)\d*\.xml', n)]

    # 文内开头标题（首段文本）
    out['first_para'] = texts[0][:80] if texts else ''
    # 全件统计行
    for i, t in enumerate(texts[:8]):
        if '全件' in t and '题' in t:
            out['stat_line'] = t[:80]
            break
    z.close()
    return out

def main():
    res = {}
    for code, fn in FILES.items():
        try:
            res[code] = scan(BASE + '\\' + fn)
            print(f'[ok] {code}')
        except Exception as e:
            res[code] = {'error': repr(e)}
            print(f'[ERR] {code}: {e!r}')
    with io.open(r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\A0勘察\scan_out.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print('saved scan_out.json')

if __name__ == '__main__':
    main()
