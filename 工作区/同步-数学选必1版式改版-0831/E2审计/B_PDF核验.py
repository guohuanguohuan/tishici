# -*- coding: utf-8 -*-
"""E2任务B-核验：六件PDF逐页断言（§14）。
A4/x0≈43/页眉品牌＋STYLEREF逐页断言/页脚整串与start衔接/灰度三值/深蓝/双档字号。"""
import os, re, sys, io, json
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
FILES = {
    'X1': ('人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', '第1章·衔接', 20, 20, 1),
    'I1': ('人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', '第1章·清单', 20, 20, 1),
    'B':  ('人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', '第1章·讲练', 156, 78, 1),
    'X2': ('人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', '第2章·衔接', 4, 4, 1),
    'I2': ('人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', '第2章·清单', 40, 40, 1),
    'E':  ('人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', '第2章·讲练', 197, 47, 1),
}
BRAND = {  # 页眉左侧品牌串（册名 第X章 章名·件型）
    'X1': '羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·衔接',
    'I1': '羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·清单',
    'B':  '羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·讲练',
    'X2': '羿郭工作室·人教B版选必1 第2章 平面解析几何·衔接',
    'I2': '羿郭工作室·人教B版选必1 第2章 平面解析几何·清单',
    'E':  '羿郭工作室·人教B版选必1 第2章 平面解析几何·讲练',
}

def xml_sections(path):
    import zipfile
    with zipfile.ZipFile(path) as z:
        st = etree.fromstring(z.read('word/styles.xml'))
        ids = set()
        for s in st.findall('w:style', NS):
            nm = s.find('w:name', NS)
            if nm is not None and nm.get(f'{{{W}}}val') in ('heading 3', '标题 3'):
                ids.add(s.get(f'{{{W}}}styleId'))
        doc = etree.fromstring(z.read('word/document.xml'))
    secs = []
    for p in doc.findall('.//w:body/w:p', NS):
        ps = p.find('w:pPr/w:pStyle', NS)
        if ps is not None and ps.get(f'{{{W}}}val') in ids:
            t = ''.join(p.itertext()).strip()
            if t:
                secs.append(t)
    return secs

def norm(s):
    return re.sub(r'\s+', '', s)

def luma(c):
    r, g, b = c[:3]
    return 0.299 * r * 255 + 0.587 * g * 255 + 0.114 * b * 255

report = {}
for code, (fn, ident, N, pages_claim, start) in FILES.items():
    pdf = os.path.join(HERE, 'PDF', code + '.pdf')
    doc = fitz.open(pdf)
    r = {'pages': doc.page_count, 'claim': pages_claim}
    # 1 A4 + x0
    sizes = {(round(p.rect.width, 1), round(p.rect.height, 1)) for p in doc}
    r['page_sizes'] = sorted(sizes)
    x0s = []
    for p in doc:
        xs = [b[0] for b in p.get_text('blocks') if b[4].strip()]
        for d in p.get_drawings():
            rr = d['rect']
            if rr.width > 5:
                xs.append(rr.x0)
        if xs:
            x0s.append(round(min(xs), 1))
    r['x0_min'], r['x0_max'] = (min(x0s), max(x0s)) if x0s else (None, None)
    # 2 逐页页眉/页脚
    hdr_vals, foot_bad, hdr_bad = [], [], []
    gray_hits = {190: 0, 209: 0, 201: 0}
    gray_other = {}
    blue_spans = 0
    sz12, sz9 = 0, 0
    brand_ok = 0
    for i, p in enumerate(doc):
        words = p.get_text('words')
        hdr_words = [w for w in words if w[1] < 52]
        ftr_words = [w for w in words if w[1] > 782]
        hdr_line = ''.join(w[4] for w in sorted(hdr_words, key=lambda w: w[0]))
        # STYLEREF 值 = 品牌串之后
        b = norm(BRAND[code])
        hl = norm(hdr_line)
        val = hl.replace(b, '', 1) if hl.startswith(b[:12]) else None
        if hl.startswith(norm(BRAND[code])[:12]) and norm(BRAND[code]) in hl:
            brand_ok += 1
        hdr_vals.append(val if val is not None else ('RAW:' + hdr_line[:40]))
        # 页脚
        ftr = ''.join(w[4] for w in sorted(ftr_words, key=lambda w: w[0]))
        exp_num = start + i
        pat = norm(f'{ident}（共{N}页）第{exp_num}页')
        if norm(ftr) != pat:
            foot_bad.append((i + 1, ftr[:60]))
        # 灰度（drawings填充）
        for d in p.get_drawings():
            f = d.get('fill')
            if f:
                L = luma(f)
                for target in gray_hits:
                    if abs(L - target) <= 8:
                        gray_hits[target] += 1
                        break
                else:
                    k = round(L / 10) * 10
                    gray_other[k] = gray_other.get(k, 0) + 1
        # 深蓝与字号（文本span）
        td = p.get_text('dict')
        for blk in td['blocks']:
            for ln in blk.get('lines', []):
                for sp in ln['spans']:
                    c = sp['color']
                    if abs((c >> 16) & 255 - 31) < 12 and abs(((c >> 8) & 255) - 78) < 14 and abs((c & 255) - 121) < 14:
                        blue_spans += 1
                    if abs(sp['size'] - 12.0) <= 0.35:
                        sz12 += 1
                    elif abs(sp['size'] - 9.0) <= 0.35:
                        sz9 += 1
    r['brand_pages_ok'] = brand_ok
    r['footer_bad'] = foot_bad[:8]
    r['gray'] = gray_hits
    r['gray_other_top'] = dict(sorted(gray_other.items(), key=lambda kv: -kv[1])[:6])
    r['blue_spans'] = blue_spans
    r['sz12_spans'], r['sz9_spans'] = sz12, sz9
    # 3 STYLEREF 逐页断言：值序列 vs XML节序列 + 变更页正文含节标题
    secs = xml_sections(os.path.join(ROOT, fn))
    secs_n = [norm(s) for s in secs]
    uniq_vals = []
    for v in hdr_vals:
        if not uniq_vals or uniq_vals[-1] != v:
            uniq_vals.append(v)
    seq_ok, seq_detail = True, []
    ui = 0
    for v in uniq_vals:
        if not isinstance(v, str) or v.startswith('RAW:'):
            seq_ok = False; seq_detail.append(f'badval:{v}'); continue
        while ui < len(secs_n) and secs_n[ui] != v:
            ui += 1
        if ui >= len(secs_n):
            seq_ok = False; seq_detail.append(f'notinxml:{v[:30]}')
        else:
            ui += 1
    # 变更页断言（抽前10个变更点）
    changes = []
    prev = None
    for i, v in enumerate(hdr_vals):
        if v != prev:
            changes.append((i, v))
            prev = v
    ch_bad = []
    for i, v in changes[:12]:
        if isinstance(v, str) and not v.startswith('RAW:'):
            body = norm(doc[i].get_text())
            if v[:24] not in body:
                ch_bad.append((i + 1, v[:40]))
    r['xml_sections'] = len(secs)
    r['hdr_uniq'] = len(uniq_vals)
    r['hdr_seq_ok'] = seq_ok
    r['hdr_seq_bad'] = seq_detail[:5]
    r['hdr_change_bad'] = ch_bad[:5]
    r['hdr_stats_tail'] = any('本节' in v for v in uniq_vals if isinstance(v, str))
    r['hdr_samples'] = [v[:50] if isinstance(v, str) else v for v in uniq_vals[:6]]
    report[code] = r
    print(f"{code}: pages={r['pages']} A4={r['page_sizes']} x0=[{r['x0_min']},{r['x0_max']}] "
          f"brandOK={brand_ok}/{doc.page_count} footerBad={len(foot_bad)} seqOK={seq_ok} "
          f"gray={gray_hits} blue={blue_spans} 12pt={sz12} 9pt={sz9} statsTail={r['hdr_stats_tail']}")
    doc.close()

with open(os.path.join(HERE, 'B_PDF核验.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print('saved B_PDF核验.json')
