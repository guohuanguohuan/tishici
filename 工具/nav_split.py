# -*- coding: utf-8 -*-
"""nav_split.py — 讲练件导航要素回填＋按节界拆卷（通用）
用法: python nav_split.py <工作件.docx> <通式句json> <卷标签逗串（如 上,下 或 2.1—2.3,2.4—2.5,2.6—2.7,2.8）> <文件名前缀>
输出: 各卷 docx（文件名=前缀（卷标）·讲练件（N题）.docx）＋ nav_stats.json"""
import sys, io, zipfile, re, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
sys.path.insert(0, '.')
from repair_lib import W, M, q, mq, tag, ptext

def mkpara(text, bold=False, center=False):
    p = etree.Element(q('p'))
    pPr = etree.SubElement(p, q('pPr'))
    sp = etree.SubElement(pPr, q('spacing'))
    sp.set(q('before'), '0'); sp.set(q('after'), '0'); sp.set(q('line'), '300'); sp.set(q('lineRule'), 'auto')
    jc = etree.SubElement(pPr, q('jc')); jc.set(q('val'), 'center' if center else 'left')
    r = etree.SubElement(p, q('r'))
    rpr = etree.SubElement(r, q('rPr'))
    rf = etree.SubElement(rpr, q('rFonts'))
    rf.set(q('ascii'), 'Times New Roman'); rf.set(q('hAnsi'), 'Times New Roman'); rf.set(q('eastAsia'), '宋体'); rf.set(q('cs'), 'Times New Roman')
    if bold: etree.SubElement(rpr, q('b'))
    sz = etree.SubElement(rpr, q('sz')); sz.set(q('val'), '21')
    szc = etree.SubElement(rpr, q('szCs')); szc.set(q('val'), '21')
    t = etree.SubElement(r, q('t')); t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); t.text = text
    return p

WIDTHS = [3600, 1800, 1000, 2600, 1200]

def mkcell(text, bold=False, center=True):
    tc = etree.Element(q('tc'))
    tcPr = etree.SubElement(tc, q('tcPr'))
    tcW = etree.SubElement(tcPr, q('tcW')); tcW.set(q('w'), '0'); tcW.set(q('type'), 'auto')
    p = mkpara(text, bold=bold, center=center)
    tc.append(p)
    return tc

def mknavtable(rows):
    tbl = etree.Element(q('tbl'))
    tblPr = etree.SubElement(tbl, q('tblPr'))
    tw = etree.SubElement(tblPr, q('tblW')); tw.set(q('w'), '10200'); tw.set(q('type'), 'dxa')
    borders = etree.SubElement(tblPr, q('tblBorders'))
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = etree.SubElement(borders, q(edge))
        e.set(q('val'), 'single'); e.set(q('sz'), '4'); e.set(q('space'), '0'); e.set(q('color'), '000000')
    grid = etree.SubElement(tbl, q('tblGrid'))
    for w_ in WIDTHS:
        gc = etree.SubElement(grid, q('gridCol')); gc.set(q('w'), str(w_))
    for ri, row in enumerate(rows):
        tr = etree.SubElement(tbl, q('tr'))
        for ci, val in enumerate(row):
            tr.append(mkcell(val, bold=(ri == 0)))
    return tbl

def structure(body):
    els = list(body)
    items = []
    for i, el in enumerate(els):
        if el.tag == q('p'):
            t = ptext(el)
            if re.match(r'^\d+(\.\d+)*\s+\S', t):
                kind = 'group' if ('：' in t and re.match(r'^\d+(\.\d+)+\s', t)) else 'section'
            elif re.match(r'^\d+．', t):
                kind = 'qstart'
            else:
                kind = 'para'
            items.append({'kind': kind, 'el': i, 'text': t, 'node': el})
        else:
            items.append({'kind': 'other', 'el': i, 'text': '', 'node': el})
    # 题块：qstart 起到下一 qstart/标题/other-table 前，块内含【难度】
    qs = []
    n = len(items)
    i = 0
    while i < n:
        if items[i]['kind'] == 'qstart':
            j = i + 1
            while j < n and items[j]['kind'] == 'para':
                j += 1
            blk = '\n'.join(items[k]['text'] for k in range(i, j))
            md = re.search(r'【难度】(简单|中档|难)', blk)
            mno = re.match(r'^(\d+)．', items[i]['text'])
            if md and mno:
                qs.append({'no': int(mno.group(1)), 'el': items[i]['el'], 'diff': md.group(1)})
                i = j
                continue
        i += 1
    return items, qs

def main(work, formula_files, vol_labels, prefix):
    formulas = {}
    for f in formula_files:
        formulas.update(json.load(open(f, encoding='utf-8')))
    z = zipfile.ZipFile(work)
    parts = {n: z.read(n) for n in z.namelist()}
    parts0 = parts
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    print('阶段: structure', flush=True)
    items, qs = structure(body)
    els = list(body)
    sections = [x for x in items if x['kind'] == 'section']
    groups = [x for x in items if x['kind'] == 'group']
    # 叶节判定
    def depth(t):
        return t.split(' ')[0].count('.') + 1
    leaf = {}
    for si, s in enumerate(sections):
        d = depth(s['text'])
        nxt = sections[si + 1] if si + 1 < len(sections) else None
        leaf[s['el']] = nxt is None or depth(nxt['text']) <= d
    # 题→当前叶节；组→当前叶节
    q2sec = {}
    g2sec = {}
    cur = None
    curgrp = None
    secels = {s['el'] for s in sections}
    grpels = {g['el'] for g in groups}
    qstarts = {x['el'] for x in qs}
    for it in items:
        if it['el'] in secels:
            cur = it['el']
        elif it['kind'] == 'group':
            curgrp = it['el']
            if cur is not None:
                g2sec[it['el']] = cur
        elif it['el'] in qstarts and cur is not None:
            q2sec[it['el']] = cur
    # 叶节统计
    stats = {}
    for s in sections:
        if leaf[s['el']]:
            stats[s['el']] = {'name': s['text'], 'qs': [], 'groups': 0, 'node': s['node']}
    for g, s in g2sec.items():
        if s in stats:
            stats[s]['groups'] += 1
    for x in qs:
        s = q2sec.get(x['el'])
        if s in stats:
            stats[s]['qs'].append(x)
    order = [s['el'] for s in sections if leaf[s['el']]]
    # 每叶节区间
    for k, s in enumerate(order):
        st = stats[s]
        st['range'] = (st['qs'][0]['no'], st['qs'][-1]['no']) if st['qs'] else None
        st['cnt'] = {'简单': 0, '中档': 0, '难': 0}
        for x in st['qs']:
            st['cnt'][x['diff']] += 1
    total = {'简单': 0, '中档': 0, '难': 0}
    for s in order:
        for k_, v in stats[s]['cnt'].items():
            total[k_] += v
    N = len(qs)
    tot_groups = sum(stats[s]['groups'] for s in order)
    print('叶节 %d | 题 %d（简单%d/中档%d/难%d）| 组 %d' % (len(order), N, total['简单'], total['中档'], total['难'], tot_groups), flush=True)
    # ---------- 插入通式句 ----------
    n_formula = 0
    for g in groups:
        sec = g2sec.get(g['el'])
        sent = formulas.get(g['text'])
        if not sent:
            print('!! 缺通式句:', g['text'][:50]); continue
        g['node'].addnext(mkpara('题型通式：' + sent))
        n_formula += 1
    # ---------- 叶节标题：题号区间 + 节级统计行 ----------
    n_stat = 0
    for s in sections:
        if not leaf[s['el']]:
            continue
        st = stats[s['el']]
        if st['range']:
            rr = etree.SubElement(s['node'], q('r'))
            rpr = etree.SubElement(rr, q('rPr'))
            rf = etree.SubElement(rpr, q('rFonts'))
            rf.set(q('ascii'), 'Times New Roman'); rf.set(q('hAnsi'), 'Times New Roman'); rf.set(q('eastAsia'), '宋体'); rf.set(q('cs'), 'Times New Roman')
            sz = etree.SubElement(rpr, q('sz')); sz.set(q('val'), '21')
            szc = etree.SubElement(rpr, q('szCs')); szc.set(q('val'), '21')
            t = etree.SubElement(rr, q('t')); t.text = '（第%d—%d题）' % st['range']
        d = st['cnt']
        n_ = len(st['qs'])
        if n_:
            s['node'].addnext(mkpara('本节%d题：简单%d｜中档%d｜难%d' % (n_, d['简单'], d['中档'], d['难'])))
            n_stat += 1
    print('通式句插入 %d | 节级统计行 %d' % (n_formula, n_stat), flush=True)
    # ---------- 拆卷（贪心：每卷≤100题，卷数自动）----------
    els2 = list(body)
    print('阶段: els2', len(els2), flush=True)
    # 找各叶节标题段在新列表中的索引
    secnode2idx = {}
    for i2, el in enumerate(els2):
        if el.tag == q('p') and re.match(r'^\d+(\.\d+)*\s+\S', ptext(el)):
            secnode2idx[el] = i2
    K_hint = len(vol_labels)
    sec_counts = [len(stats[s]['qs']) for s in order]
    # 贪心打包：加下一节会超100即切卷
    bounds = []
    acc = 0
    for si in range(len(order)):
        c = sec_counts[si]
        if acc > 0 and acc + c > 100:
            bounds.append(si)
            acc = 0
        acc += c
    vol_secs = []
    prev = 0
    for b in bounds + [len(order)]:
        vol_secs.append(list(range(prev, b)))
        prev = b
    # 超页兜底由外部按实测页数重跑（本脚本可传 K_hint=目标卷数强制等分微调）
    if len(vol_secs) < K_hint:
        # 需要更多卷：在最大卷内按节再二分递归
        while len(vol_secs) < K_hint:
            # 找题数最多的卷
            vi = max(range(len(vol_secs)), key=lambda k: sum(sec_counts[s] for s in vol_secs[k]))
            secidx = vol_secs[vi]
            if len(secidx) < 2:
                break
            tot = sum(sec_counts[s] for s in secidx)
            cum = 0
            cut = None
            best = 10**9
            for pi in range(len(secidx) - 1):
                cum += sec_counts[secidx[pi]]
                if min(cum, tot - cum) > 100 or cum == 0:
                    continue
                if abs(cum - tot / 2) < best:
                    best = abs(cum - tot / 2); cut = pi + 1
            if cut is None:
                break
            vol_secs = vol_secs[:vi] + [secidx[:cut], secidx[cut:]] + vol_secs[vi + 1:]
    if len(vol_secs) <= 3:
        auto_labels = ['上', '中', '下'][:len(vol_secs)] if len(vol_secs) == 3 else (['上', '下'] if len(vol_secs) == 2 else ['全'])
    else:
        auto_labels = []
        for secidx in vol_secs:
            a = stats[order[secidx[0]]]['name'].split(' ')[0]
            b = stats[order[secidx[-1]]]['name'].split(' ')[0]
            auto_labels.append(a if a == b else '%s—%s' % (a, b))
    vol_labels = auto_labels
    print('卷划分:', [(vol_labels[k], sum(sec_counts[s] for s in vol_secs[k])) for k in range(len(vol_secs))], flush=True)
    out_meta = []
    title_el = els2[0]  # 文内标题
    # 各卷起点：叶节标题向前上溯连续的父节标题段
    def vol_start_idx(secidx0):
        fi = els2.index(stats[order[secidx0]]['node'])
        while fi - 1 >= 1:
            prev = els2[fi - 1]
            if prev.tag == q('p') and re.match(r'^\d+(\.\d+)*\s+\S', ptext(prev)) and '：' not in ptext(prev)[:ptext(prev).find('（') if '（' in ptext(prev) else len(ptext(prev))]:
                # 标题段（非题型）：判断是否父节（depth 更小）
                dprev = ptext(prev).split(' ')[0].count('.') + 1
                dleaf = stats[order[secidx0]]['name'].split(' ')[0].count('.') + 1
                if dprev < dleaf:
                    fi -= 1
                    continue
            break
        return fi
    starts = [vol_start_idx(si[0]) for si in vol_secs]
    for vi, secidx in enumerate(vol_secs):
        first_i = starts[vi]
        last_sec_el = stats[order[secidx[-1]]]['node']
        # 卷内最后元素 = 下一卷首节标题前（或文尾 sectPr 前）
        if vi + 1 < len(vol_secs):
            last_i = starts[vi + 1]
        else:
            last_i = len(els2)
            # 排除末尾 body 级 sectPr
            while last_i > first_i and els2[last_i - 1].tag == q('sectPr'):
                last_i -= 1
        vol_q = [x for s in secidx for x in stats[order[s]]['qs']]
        vd = {'简单': 0, '中档': 0, '难': 0}
        for x in vol_q:
            vd[x['diff']] += 1
        n_v = len(vol_q)
        rng = (vol_q[0]['no'], vol_q[-1]['no']) if vol_q else (0, 0)
        vol_label = vol_labels[vi]
        out_meta.append({'label': vol_label, 'n': n_v, 'diff': vd, 'range': rng, 'first': first_i, 'last': last_i})
        print('卷%s: %d题 简单%d/中档%d/难%d 第%d—%d题' % (vol_label, n_v, vd['简单'], vd['中档'], vd['难'], rng[0], rng[1]))
    json.dump({ 'order': [stats[s]['name'] for s in order],
                'secstats': [{'name': stats[s]['name'], 'range': stats[s]['range'], 'n': len(stats[s]['qs']), 'cnt': stats[s]['cnt'], 'groups': stats[s]['groups']} for s in order],
                'total': {'n': N, 'cnt': total, 'groups': tot_groups},
                'vols': out_meta}, open('nav_stats.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # ---------- 生成各卷包（字符串拼装，避免整树deepcopy）----------
    import copy as _copy
    docstr = etree.tostring(doc, encoding='unicode')
    open_tag_end = docstr.index('>') + 1
    open_tag = docstr[:open_tag_end]
    close_tag = '</%s>' % etree.QName(doc).localname if False else None
    # 找根元素关闭标签（文档级根的localname带前缀）
    mclose = re.search(r'</([\w:]*document)\s*>\s*$', docstr)
    close_tag = '</%s>' % mclose.group(1)
    body_open = '<%sbody>' % ('w:')
    # 段序列化缓存
    seg_cache = {}
    def seg(el):
        k = id(el)
        if k not in seg_cache:
            seg_cache[k] = etree.tostring(el, encoding='unicode')
        return seg_cache[k]
    sectPr = None
    for el in reversed(els2):
        if el.tag == q('sectPr'):
            sectPr = el; break
    for vi, vm in enumerate(out_meta):
        vol_label = vm['label']
        fname = '%s（%s）·讲练件（%d题）.docx' % (prefix, vol_label, vm['n'])
        title = '%s（%s）·讲练件（%d题）' % (prefix, vol_label, vm['n'])
        parts_xml = [etree.tostring(mkpara(title, bold=True), encoding='unicode'),
                     etree.tostring(mkpara('本卷%d题：简单%d｜中档%d｜难%d（第%d—%d题）' % (vm['n'], vm['diff']['简单'], vm['diff']['中档'], vm['diff']['难'], vm['range'][0], vm['range'][1])), encoding='unicode')]
        if vi == 0:
            rows = [('节名', '题号区间', '题量', '简单/中档/难', '题型组数')]
            for s in order:
                st = stats[s]
                rows.append((st['name'], '第%d—%d题' % st['range'] if st['range'] else '—', str(len(st['qs'])), '简单%d/中档%d/难%d' % (st['cnt']['简单'], st['cnt']['中档'], st['cnt']['难']), str(st['groups'])))
            rows.append(('合计', '第1—%d题' % N, str(N), '简单%d/中档%d/难%d' % (total['简单'], total['中档'], total['难']), str(tot_groups)))
            parts_xml.append(etree.tostring(mknavtable(rows), encoding='unicode'))
        for el in els2[vm['first']:vm['last']]:
            if el is title_el:
                continue
            parts_xml.append(seg(el))
        if sectPr is not None:
            parts_xml.append(seg(sectPr))
        body_inner = ''.join(parts_xml)
        full_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + chr(10) + open_tag + body_open + body_inner + '</w:body>' + close_tag)
        # core title
        core = parts0.get('docProps/core.xml', b'')
        core_s = core.decode('utf-8') if core else None
        title2 = None
        if core_s:
            title2 = re.sub(r'<dc:title>[^<]*</dc:title>', '<dc:title>%s</dc:title>' % title, core_s)
            if '<dc:title>' not in title2:
                title2 = title2.replace('</cp:coreProperties>', '<dc:title>%s</dc:title></cp:coreProperties>' % title)
        zo = zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED)
        for n_ in z.namelist():
            if n_ == 'word/document.xml':
                zo.writestr(n_, full_xml.encode('utf-8'))
            elif n_ == 'docProps/core.xml' and title2:
                zo.writestr(n_, title2.encode('utf-8'))
            else:
                zo.writestr(n_, z.read(n_))
        zo.close()
        print('写出', fname, flush=True)

if __name__ == '__main__':
    work = sys.argv[1]
    formulas = sys.argv[2].split(',')
    vol_labels = sys.argv[3].split(',')
    prefix = sys.argv[4]  # 如 人教B版选必1 第1章 空间向量与立体几何
    prefix_chapter = prefix  # 文内标题用
    main(work, formulas, vol_labels, prefix)
