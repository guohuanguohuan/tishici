# -*- coding: utf-8 -*-
"""子步3 T0 页数增量预算：I1/I2 逐节条目块 → 高度估算 → 各卷页数增量（只读源件）
模型：正文行高 line=410 atLeast = 20.5pt；栏宽 4890缇 = 244.5pt；
     CJK字符宽=字号(12pt/表内10.5pt)，西文半角=0.5×；图高=wp:extent cy(EMU→pt)；
     页版心高 = 842−2×42.52 = 757pt。校准：对 I1/I2 全件估算 vs 实测页数（13/27）。
"""
import sys, io, re, zipfile, json, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def qwp(t): return '{%s}%s' % (WP, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def mtext(p): return ''.join(t.text or '' for t in p.iter(qm('t')))

BASE = r'C:\提示词\高中数学\高中数学同步'
FILES = {
    'I1': BASE + r'\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'I2': BASE + r'\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
}
LINE_PT = 20.5
COL_PT = 244.5
PAGE_PT = 757.0

ENT_RE = re.compile(r'^(\d+(?:\.\d+)*)-(\d+)．')
SEC_TITLE_FILL = 'ADC2DA'

def cjk_width(s, font_pt):
    w = 0.0
    for ch in s:
        w += font_pt if ord(ch) >= 0x2E80 else font_pt * 0.5
    return w

def para_shd_fill(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return None
    shd = ppr.find(q('shd'))
    return shd.get(q('fill')) if shd is not None else None

def para_style(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return None
    st = ppr.find(q('pStyle'))
    return st.get(q('val')) if st is not None else None

def est_para_height(p, font_pt=12.0):
    """段落估算高度：文字折行 + 内嵌图高（取大者叠加：图段文字≈0）"""
    txt = ptext(p) + mtext(p)
    wpt = cjk_width(txt, font_pt)
    lines = max(1, math.ceil(wpt / COL_PT)) if txt.strip() else 1
    h = lines * LINE_PT
    for ext in p.iter(qwp('extent')):
        try:
            cy = int(ext.get('cy', '0')) / 12700.0
        except (TypeError, ValueError):
            cy = 0
        if cy > 0:
            h += cy + LINE_PT  # 图段上下余量
    return h

def est_tbl_height(tbl):
    """表格估算：逐行 = 各格估算行数最大值 × 20.5pt（表内字号下限10.5pt，栏宽按格数均分）"""
    rows = tbl.findall(q('tr'))
    total = 0.0
    for tr in rows:
        cells = tr.findall(q('tc'))
        n = max(1, len(cells))
        cell_w = COL_PT / n
        mx = 1
        for tc in cells:
            txt = ''.join(t.text or '' for t in tc.iter(q('t'))) + ''.join(t.text or '' for t in tc.iter(qm('t')))
            wpt = cjk_width(txt, 10.5)
            lines = max(1, math.ceil(wpt / max(60.0, cell_w))) if txt.strip() else 1
            img_h = 0.0
            for ext in tc.iter(qwp('extent')):
                try: img_h += int(ext.get('cy', '0')) / 12700.0
                except (TypeError, ValueError): pass
            mx = max(mx, lines + (math.ceil(img_h / LINE_PT) if img_h else 0))
        total += mx * LINE_PT
    return total

def extract_entries(code):
    """返回 {节号: [ {start,end,paras,tables,chars,imgs,img_h,est_h}, ...]} + 全件估算总高"""
    z = zipfile.ZipFile(FILES[code])
    root = etree.fromstring(z.read('word/document.xml'))
    body = root.find(q('body'))
    children = list(body)
    # 边界判定：条目题名行 / 节名锚段(JieMingMao) / 节标题段(段级ADC2DA)
    bounds = []
    for i, el in enumerate(children):
        if tag(el) != 'p': continue
        t = ptext(el)
        if not t.strip(): continue
        if ENT_RE.match(t):
            bounds.append((i, 'ent', ENT_RE.match(t).group(1)))
        elif para_style(el) == 'JieMingMao' or para_shd_fill(el) == SEC_TITLE_FILL:
            bounds.append((i, 'sec', None))
    entries = {}
    ent_marks = [(i, sec) for i, k, sec in bounds if k == 'ent']
    for idx, (i, sec) in enumerate(ent_marks):
        # 块结束 = 下一个边界（条目或节标题/锚）
        j = len(children)
        for bi, bk, _ in bounds:
            if bi > i:
                j = bi
                break
        block = children[i:j]
        paras = sum(1 for el in block if tag(el) == 'p')
        tables = sum(1 for el in block if tag(el) == 'tbl')
        chars = 0
        imgs = 0
        img_h = 0.0
        est = 0.0
        for el in block:
            if tag(el) == 'p':
                chars += len(ptext(el)) + len(mtext(el))
                n_img = len(list(el.iter(qwp('extent'))))
                imgs += n_img
                for ext in el.iter(qwp('extent')):
                    try: img_h += int(ext.get('cy', '0')) / 12700.0
                    except (TypeError, ValueError): pass
                est += est_para_height(el)
            elif tag(el) == 'tbl':
                est += est_tbl_height(el)
                chars += len(''.join(t.text or '' for t in el.iter(q('t'))))
                for ext in el.iter(qwp('extent')):
                    try:
                        img_h += int(ext.get('cy', '0')) / 12700.0; imgs += 1
                    except (TypeError, ValueError): pass
        entries.setdefault(sec, []).append({
            'start': i, 'end': j, 'paras': paras, 'tables': tables,
            'chars': chars, 'imgs': imgs, 'img_h_pt': round(img_h, 1),
            'est_h_pt': round(est, 1),
        })
    # 全件估算（校准用）：全部 body 子元素
    total_est = 0.0
    for el in children:
        if tag(el) == 'p':
            total_est += est_para_height(el)
        elif tag(el) == 'tbl':
            total_est += est_tbl_height(el)
    return entries, total_est

# 各卷节归属（任务书T2：B+C逐节之和=I1、E+F+G+H之和=I2）
VOL_SECS = {
    'B': ['1.1.1', '1.1.2', '1.1.3', '1.2.1', '1.2.2', '1.2.3', '1.2.4'],
    'C': ['1.2.5'],
    'E': ['2.1', '2.2.1', '2.2.2', '2.2.3', '2.2.4', '2.3.1', '2.3.2', '2.3.3'],
    'F': ['2.3.4', '2.4', '2.5.1', '2.5.2'],
    'G': ['2.6.1', '2.6.2', '2.7.1', '2.7.2'],
    'H': ['2.8'],
}
CUR_PAGES = {'B': 52, 'C': 60, 'E': 48, 'F': 52, 'G': 37, 'H': 63}  # 子步2后 PDF=COM 实测
LIST_PAGES = {'I1': 13, 'I2': 27}

if __name__ == '__main__':
    out = {'model': {'line_pt': LINE_PT, 'col_pt': COL_PT, 'page_pt': PAGE_PT}}
    all_entries = {}
    for code in ('I1', 'I2'):
        entries, total_est = extract_entries(code)
        all_entries[code] = entries
        actual_h = LIST_PAGES[code] * PAGE_PT
        calib = actual_h / total_est if total_est else 0
        out[code] = {
            '条目数': sum(len(v) for v in entries.values()),
            '全件估算高pt': round(total_est, 1),
            '实测页数': LIST_PAGES[code],
            '实测等效高pt': actual_h,
            '校准系数(实测/估算)': round(calib, 3),
            '逐节': {sec: {'条目数': len(v), '字符': sum(e['chars'] for e in v),
                        '图数': sum(e['imgs'] for e in v),
                        '图高pt': round(sum(e['img_h_pt'] for e in v), 1),
                        '估算高pt': round(sum(e['est_h_pt'] for e in v), 1)}
                   for sec, v in sorted(entries.items())},
        }
    # 用两清单各自的校准系数分别应用于对应章（I1→B/C，I2→E/F/G/H）
    calib = {'I1': out['I1']['校准系数(实测/估算)'], 'I2': out['I2']['校准系数(实测/估算)']}
    src = {'B': 'I1', 'C': 'I1', 'E': 'I2', 'F': 'I2', 'G': 'I2', 'H': 'I2'}
    vols = {}
    for vol, secs in VOL_SECS.items():
        lst = src[vol]
        est_h = 0.0
        n_ent = 0
        detail = {}
        for sec in secs:
            v = all_entries[lst].get(sec, [])
            h = sum(e['est_h_pt'] for e in v)
            detail[sec] = {'条目数': len(v), '估算高pt': round(h, 1)}
            est_h += h
            n_ent += len(v)
        # +每节一个讲部标题行（20.5pt，按一行计）
        est_h += len(secs) * LINE_PT
        inc_pages_raw = est_h * calib[lst] / PAGE_PT
        inc_pages = math.ceil(inc_pages_raw)
        vols[vol] = {
            '源清单': lst, '条目数': n_ent, '节数': len(secs),
            '估算增量高pt(校准后)': round(est_h * calib[lst], 1),
            '增量页(原估)': round(inc_pages_raw, 2), '增量页(进整)': inc_pages,
            '现页数': CUR_PAGES[vol], '预估页数': CUR_PAGES[vol] + inc_pages,
            '超80页': CUR_PAGES[vol] + inc_pages > 80,
            '逐节': detail,
        }
    out['各卷预算'] = vols
    with open('T0_预算实测.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out['各卷预算'], ensure_ascii=False, indent=1))
    print('校准系数:', calib)
    for code in ('I1', 'I2'):
        print(code, '逐节:', json.dumps(out[code]['逐节'], ensure_ascii=False))
