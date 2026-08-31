# -*- coding: utf-8 -*-
"""E2任务A：十件内容件同册横向一致性diff（公共规则§13）。
只读产出文件夹原件，逐件提取页脚域形态/docDefaults/标签体系/docGrid/pgSz/pgMar/sectPr，
落盘 JSON + 横向对比表。不修改任何文件。"""
import zipfile, re, json, sys, io, os
from lxml import etree

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
ROOT = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
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

def txt(el):
    return ''.join(el.itertext()) if el is not None else ''

def parse_footer(z):
    """解析全部footer*.xml：域形态/字号/对齐/文本。"""
    out = []
    names = [n for n in z.namelist() if re.match(r'word/footer\d*\.xml$', n)]
    for n in names:
        root = etree.fromstring(z.read(n))
        # 域形态
        instr = [t.text or '' for t in root.iter(f'{{{W}}}instrText')]
        fldchars = [c.get(f'{{{W}}}fldCharType') for c in root.iter(f'{{{W}}}fldChar')]
        fldsimple = root.findall(f'.//w:fldSimple', NS)
        runs = root.findall(f'.//w:r', NS)
        szs = sorted({r.find(f'w:rPr/w:sz', NS).get(f'{{{W}}}val') for r in runs
                      if r.find(f'w:rPr/w:sz', NS) is not None})
        jcs = [p.find(f'w:pPr/w:jc', NS).get(f'{{{W}}}val') for p in root.findall(f'.//w:p', NS)
               if p.find(f'w:pPr/w:jc', NS) is not None]
        full = txt(root)
        out.append({'part': n, 'instr': instr, 'fldchars': fldchars,
                    'fldSimple': len(fldsimple),
                    'NUMPAGES': sum('NUMPAGES' in i.upper() for i in instr),
                    'PAGE_fields': sum('PAGE' in i.upper() and 'NUMPAGES' not in i.upper() for i in instr),
                    'run_szs': szs, 'jcs': jcs, 'text': full[:120],
                    'shd': len(root.findall(f'.//w:shd', NS))})
    return out

def parse_doc(z, name):
    doc = etree.fromstring(z.read('word/document.xml'))
    res = {}
    sects = doc.findall('.//w:sectPr', NS)
    sec_out = []
    for s in sects:
        pg = s.find(f'w:pgSz', NS); mar = s.find(f'w:pgMar', NS)
        num = s.find(f'w:pgNumType', NS); grid = s.find(f'w:docGrid', NS)
        hr = s.findall(f'w:headerReference', NS); fr = s.findall(f'w:footerReference', NS)
        sec_out.append({
            'pgSz': (pg.get(f'{{{W}}}w'), pg.get(f'{{{W}}}h')) if pg is not None else None,
            'pgMar': ({k.split('}')[1]: v for k, v in mar.attrib.items()} if mar is not None else None),
            'pgNumType_start': num.get(f'{{{W}}}start') if num is not None else None,
            'docGrid': ({k.split('}')[1]: v for k, v in grid.attrib.items()} if grid is not None else None),
            'headerRefs': len(hr), 'footerRefs': len(fr),
            'titlePg': s.find(f'w:titlePg', NS) is not None,
        })
    res['sectPrs'] = sec_out
    # 标签体系（document.xml全文计数）
    body_txt = ''.join(doc.itertext())
    tags = ['【答案】', '【知识点】', '【分析】', '【详解】', '【点睛】', '【编注】', '【大招指引】',
            '【题后反思】', '【温馨提醒】', '【定义】', '【结论】', '【注】', '【定理】', '【拓展】']
    res['tag_counts'] = {t: body_txt.count(t) for t in tags if body_txt.count(t) > 0}
    # 题号块形态（文本层）
    res['qnum_3seg'] = len(re.findall(r'（(?:简单·保60%|中档·保80%|难·冲100%)·卡壳看答案）', body_txt))
    res['qnum_2seg'] = len(re.findall(r'（衔接必会·卡壳看答案）', body_txt))
    res['qnum_bare'] = len(re.findall(r'（卡壳看答案）', body_txt))  # 不应出现裸两词
    # 底纹三色用法
    res['shd_ADC2DA'] = len(re.findall(r'w:fill="ADC2DA"', etree.tostring(doc, encoding='unicode')))
    res['shd_C6D4E3'] = len(re.findall(r'w:fill="C6D4E3"', etree.tostring(doc, encoding='unicode')))
    res['shd_C9C9C9'] = len(re.findall(r'w:fill="C9C9C9"', etree.tostring(doc, encoding='unicode')))
    res['color_1F4E79'] = len(re.findall(r'w:val="1F4E79"', etree.tostring(doc, encoding='unicode')))
    # 行内残留违规形态
    res['w_ind_nonzero'] = sum(1 for i in doc.iter(f'{{{W}}}ind')
                               if (i.get(f'{{{W}}}left') not in (None, '0')
                                   or i.get(f'{{{W}}}firstLine') not in (None, '0')
                                   or i.get(f'{{{W}}}hanging') not in (None, '0')))
    res['w_br'] = len(doc.findall('.//w:br', NS))
    res['anchor'] = len(re.findall(r'<wp:anchor', etree.tostring(doc, encoding='unicode')))
    res['inline'] = len(re.findall(r'<wp:inline', etree.tostring(doc, encoding='unicode')))
    return res

def parse_styles(z):
    st = etree.fromstring(z.read('word/styles.xml'))
    rpr = st.find(f'w:docDefaults/w:rPrDefault/w:rPr', NS)
    ppr = st.find(f'w:docDefaults/w:pPrDefault/w:pPr', NS)
    def rpr_map(r):
        if r is None: return None
        o = {}
        sz = r.find(f'w:sz', NS); rf = r.find(f'w:rFonts', NS); b = r.find(f'w:b', NS)
        if sz is not None: o['sz'] = sz.get(f'{{{W}}}val')
        if rf is not None:
            o['rFonts'] = {k.split('}')[1]: v for k, v in rf.attrib.items()}
        o['b'] = b is not None
        return o
    def ppr_map(p):
        if p is None: return None
        o = {}
        sp = p.find(f'w:spacing', NS); jc = p.find(f'w:jc', NS)
        if sp is not None: o['spacing'] = {k.split('}')[1]: v for k, v in sp.attrib.items()}
        if jc is not None: o['jc'] = jc.get(f'{{{W}}}val')
        return o
    # Normal样式
    normals = []
    for s in st.findall(f'w:style', NS):
        if s.get(f'{{{W}}}default') == '1' and s.get(f'{{{W}}}type') == 'paragraph':
            normals.append(s.get(f'{{{W}}}styleId'))
    # 标题3样式
    h3 = None
    for s in st.findall(f'w:style', NS):
        nm = s.find(f'w:name', NS)
        if nm is not None and nm.get(f'{{{W}}}val') in ('heading 3', '标题 3'):
            r = s.find(f'w:rPr', NS); p = s.find(f'w:pPr', NS)
            h3 = {'styleId': s.get(f'{{{W}}}styleId'), 'name': nm.get(f'{{{W}}}val'),
                  'rPr': rpr_map(r), 'pPr': ppr_map(p)}
    return {'rPrDefault': rpr_map(rpr), 'pPrDefault': ppr_map(ppr),
            'default_para_styleId': normals, 'heading3': h3}

def main():
    out = {}
    for code, fn in FILES.items():
        p = os.path.join(ROOT, fn)
        with zipfile.ZipFile(p) as z:
            d = parse_doc(z, fn)
            d['footers'] = parse_footer(z)
            d['styles'] = parse_styles(z)
            settings = etree.fromstring(z.read('word/settings.xml'))
            d['updateFields'] = settings.find(f'w:updateFields', NS) is not None
            d['zip_members_media'] = sum(1 for n in z.namelist() if n.startswith('word/media/'))
        out[code] = d
        print(f'{code}: footers={len(d["footers"])} sect={len(d["sectPrs"])} '
              f'sz24doc={d["styles"]["rPrDefault"]} ppr={d["styles"]["pPrDefault"]}')
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'A_横向一致性.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('saved A_横向一致性.json')

if __name__ == '__main__':
    main()
