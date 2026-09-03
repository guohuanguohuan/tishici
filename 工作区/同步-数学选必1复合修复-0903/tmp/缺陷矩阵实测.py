# -*- coding: utf-8 -*-
r"""缺陷矩阵实测.py — 子步0一次性脚本（T4十件缺陷矩阵实测门·XML侧）。
逐件实测：四类废止fill计数（题号难度块run/题目侧答案值灰底run+oMath挂点/块标签芯片run/并行解法标记run）、
保留项fill计数（#ADC2DA段/#C6D4E3段/#E0E0E0段/条目号C9C9C9 run/第一子层C9C9C9 run）、
全表清单（tblW/落区/栏宽上限现算）、图基线（图数/最大宽高/超8.6cm计数/anchor数）、
讲部现状（讲部标题数/讲部条目数）。
用法: python 缺陷矩阵实测.py 代号=docx路径 ...  → 输出 缺陷矩阵.json 到本目录
"""
import sys, io, os, re, json, zipfile
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)
def wq(t): return '{%s}%s' % (WP, t)

C9 = 'C9C9C9'
RE_TQH = re.compile(r'^\d+(?:\.\d+){3,}-\d+．')
RE_TMH = re.compile(r'^\d+\.\d+(?:\.\d+)?-\d+．')
RE_CHIP = re.compile(r'^【[^】]+】')
RE_PARA = re.compile(r'^(方法一|方法二|解法一|解法二|另解)')
RE_LECT = re.compile(r'^\d+(?:\.\d+)*[ 　]*(?:方法讲解|知识讲解)[｜|]')
RE_SUB1 = re.compile(r'^（\d+）')

COL_W_CM = 8.6
EMU_PER_CM = 360000


def rtext(r):
    return ''.join(t.text or '' for t in r.iter(q('t')))


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def run_fill(r):
    rpr = r.find(q('rPr'))
    if rpr is None:
        return None
    shd = rpr.find(q('shd'))
    return shd.get(q('fill')) if shd is not None else None


def para_direct_fill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    shd = ppr.find(q('shd'))
    return shd.get(q('fill')) if shd is not None else None


def style_fill_map(styles_root):
    """styleId → 底纹fill（直挂于样式pPr）。"""
    m = {}
    if styles_root is None:
        return m
    for st in styles_root.findall(q('style')):
        sid = st.get(q('styleId'))
        ppr = st.find(q('pPr'))
        if ppr is not None:
            shd = ppr.find(q('shd'))
            if shd is not None:
                m[sid] = shd.get(q('fill'))
    return m


def measure(path):
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    try:
        styles = etree.fromstring(z.read('word/styles.xml'))
    except KeyError:
        styles = None
    z.close()
    stfill = style_fill_map(styles)
    body = root.find(q('body'))
    kids = list(body)

    def eff_fill(p):
        f = para_direct_fill(p)
        if f:
            return f
        ppr = p.find(q('pPr'))
        if ppr is not None:
            ps = ppr.find(q('pStyle'))
            if ps is not None:
                return stfill.get(ps.get(q('val')))
        return None

    # 分节符落点（头部单栏区边界）
    brk = None
    for i, el in enumerate(kids):
        if etree.QName(el).localname == 'p':
            ppr = el.find(q('pPr'))
            if ppr is not None and ppr.find(q('sectPr')) is not None:
                brk = i
                break
    # 页面参数（body级sectPr）
    sects = body.findall(q('sectPr'))
    sect = sects[-1]
    pgSz, pgMar = sect.find(q('pgSz')), sect.find(q('pgMar'))
    pw, ml, mr = int(pgSz.get(q('w'))), int(pgMar.get(q('left'))), int(pgMar.get(q('right')))
    cols = sect.find(q('cols'))
    colspace = int(cols.get(q('space'))) if cols is not None else 425
    body_w = pw - ml - mr
    col_w = (body_w - colspace) // 2

    # 四类废止fill计数（C9C9C9 run级分桶）＋OMML挂点
    c = {'题号难度块run': 0, '块标签芯片run': 0, '并行解法标记run': 0, '答案值灰底run': 0,
         '答案值OMML挂点': 0, '条目号run': 0, '第一子层run': 0,
         'ADC2DA段': 0, 'C6D4E3段': 0, 'E0E0E0段': 0}
    lect_method = 0   # 方法讲解｜类讲部标题（大招讲解，现存）
    lect_know = 0     # 知识讲解｜类讲部标题（清单复制块，待补挂）
    entry_nums = 0
    RE_NUMTOK = re.compile(r'^\d+(?:\.\d+)+-\d+．')
    RE_QK = re.compile(r'^（(?:简单|中档|难|衔接必会)')
    for p in body.iter(q('p')):
        f = eff_fill(p)
        if f == 'ADC2DA':
            c['ADC2DA段'] += 1
        elif f == 'C6D4E3':
            c['C6D4E3段'] += 1
        elif f == 'E0E0E0':
            c['E0E0E0段'] += 1
        t = ptext(p).strip()
        if RE_LECT.match(t) and f == 'C6D4E3':
            if '知识讲解' in t[:30]:
                lect_know += 1
            else:
                lect_method += 1
        # 段级定性：题号块（号＋档位/衔接括注）／条目号（号＋题名）；题号与条目号同形时以号后括注签名判别
        m_tok = RE_NUMTOK.match(t)
        para_kind = None
        tok_len = 0
        if m_tok:
            tok_len = len(m_tok.group(0))
            if RE_QK.match(t[tok_len:]):
                para_kind = '题号难度块'
            else:
                para_kind = '条目号'
                entry_nums += 1
        pos = 0
        for r in p.iter(q('r')):
            rt = rtext(r)
            start = pos
            pos += len(rt)
            if run_fill(r) != C9 or not rt.strip():
                continue
            if para_kind and start < tok_len:
                c[para_kind + 'run'] += 1
            elif RE_CHIP.match(rt.strip()):
                c['块标签芯片run'] += 1
            elif RE_PARA.match(rt.strip()):
                c['并行解法标记run'] += 1
            elif start == 0 and RE_SUB1.match(rt.strip()):
                c['第一子层run'] += 1
            else:
                c['答案值灰底run'] += 1
    # OMML挂灰（m:r 与 ctrlPr 的 w:shd C9C9C9）
    om = 0
    for mrel in root.iter(mq('r')):
        rpr = mrel.find(mq('rPr'))
        wrpr = mrel.find(q('rPr'))
        for rr in (rpr, wrpr):
            if rr is not None:
                shd = rr.find(q('shd'))
                if shd is not None and shd.get(q('fill')) == C9:
                    om += 1
                    break
    for cp in root.iter(mq('ctrlPr')):
        rpr = cp.find(q('rPr'))
        if rpr is not None:
            shd = rpr.find(q('shd'))
            if shd is not None and shd.get(q('fill')) == C9:
                om += 1
    c['答案值OMML挂点'] = om

    # 全表清单
    tables = []
    ti = 0
    for i, el in enumerate(kids):
        if etree.QName(el).localname != 'tbl':
            continue
        ti += 1
        tblpr = el.find(q('tblPr'))
        w_el = tblpr.find(q('tblW')) if tblpr is not None else None
        ind_el = tblpr.find(q('tblInd')) if tblpr is not None else None
        cm_el = tblpr.find(q('tblCellMar')) if tblpr is not None else None
        cm_l = cm_r = 0
        if cm_el is not None:
            for side in ('left', 'right'):
                e = cm_el.find(q(side))
                if e is not None:
                    v = int(e.get(q('w')))
                    if side == 'left':
                        cm_l = v
                    else:
                        cm_r = v
        tblw = int(w_el.get(q('w'))) if w_el is not None else 0
        zone = '头部单栏区' if (brk is not None and i <= brk) else '双栏正文区'
        limit = body_w if zone == '头部单栏区' else col_w - cm_l - cm_r
        tables.append({'idx': ti, 'tblW': tblw, 'tblInd': int(ind_el.get(q('w'))) if ind_el is not None else 0,
                       'zone': zone, 'cellMar': [cm_l, cm_r], '上限缇': limit,
                       '超限': tblw > limit})

    # 图基线
    imgs = {'count': 0, 'anchor': 0, 'maxWcm': 0.0, 'maxHcm': 0.0, 'over86': 0}
    for dr in root.iter(wq('inline')):
        imgs['count'] += 1
        ext = dr.find(wq('extent'))
        if ext is not None:
            wcm = int(ext.get('cx')) / EMU_PER_CM
            hcm = int(ext.get('cy')) / EMU_PER_CM
            imgs['maxWcm'] = max(imgs['maxWcm'], round(wcm, 2))
            imgs['maxHcm'] = max(imgs['maxHcm'], round(hcm, 2))
            if wcm > COL_W_CM + 0.01:
                imgs['over86'] += 1
    for dr in root.iter(wq('anchor')):
        imgs['anchor'] += 1
        imgs['count'] += 1
    return {'fill': c, 'tables': tables, 'images': imgs,
            '讲部标题数_方法讲解': lect_method, '讲部标题数_知识讲解': lect_know,
            '条目号段落数': entry_nums,
            'page': {'w': pw, 'ml': ml, 'mr': mr, 'body_w': body_w, 'col_w': col_w}}


def main():
    out = {}
    for a in sys.argv[1:]:
        if '=' not in a:
            continue
        code, path = a.split('=', 1)
        out[code] = measure(path)
        print('[%s] fill=%s 表=%d 图=%s 讲部(方法/知识)=%d/%d 条目=%d'
              % (code, out[code]['fill'], len(out[code]['tables']), out[code]['images'],
                 out[code]['讲部标题数_方法讲解'], out[code]['讲部标题数_知识讲解'], out[code]['条目号段落数']))
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), '缺陷矩阵.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('写出', dst)


if __name__ == '__main__':
    main()
