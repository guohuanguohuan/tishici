# -*- coding: utf-8 -*-
"""B代理·配页件10件XML断言：无页眉页脚部件/不计页/A4/pgMar850/全左对齐（册目录页缩进例外）/1页结构判定。
只读审计，不修改任何被审文件。输出stdout（UTF-8）。"""
import io, re, sys, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SYNC = r'C:\提示词\高中数学\高中数学同步'
PEIJI = [
    '人教B版选必1·封面.docx',
    '人教B版选必1·使用说明.docx',
    '人教B版选必1·册目录页.docx',
    '人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx',
    '人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx',
    '人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx',
    '人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx',
    '人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx',
    '人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx',
]

def para_text(p_xml):
    """拼接段落文字（含w:t，不含域指令）。"""
    return ''.join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', p_xml))

for fn in PEIJI:
    path = SYNC + '\\' + fn
    z = zipfile.ZipFile(path)
    names = z.namelist()
    doc = z.read('word/document.xml').decode('utf-8')
    print('=' * 100)
    print(f'【{fn}】 zip成员数={len(names)} document.xml={len(doc)}B')
    # ① 无页眉页脚部件
    hf_parts = [n for n in names if re.search(r'word/(header|footer)\d*\.xml$', n)]
    hf_ref = len(re.findall(r'<w:(?:header|footer)Reference\b', doc))
    print(f'  ①页眉页脚部件={len(hf_parts)}（{hf_parts if hf_parts else "无"}） document.xml内header/footerReference={hf_ref} | {"PASS" if not hf_parts and hf_ref==0 else "红旗"}')
    # settings.xml 检查（evenAndOddHeaders/titlePg等）
    settings = z.read('word/settings.xml').decode('utf-8') if 'word/settings.xml' in names else ''
    odd = 'w:evenAndOddHeaders' in settings
    upd = 'w:updateFields' in settings
    print(f'  settings.xml：evenAndOddHeaders={"在" if odd else "无"} updateFields={"在" if upd else "无"}（配页件无页码域，updateFields无需在位）')
    # ② 不计页：sectPr无pgNumType；无PAGE域
    sects = re.findall(r'<w:sectPr[^>]*>.*?</w:sectPr>', doc, re.S)
    pgnum = re.findall(r'<w:pgNumType\b[^>]*/?>', doc)
    page_field = ('PAGE' in ''.join(re.findall(r'<w:instrText[^>]*>([^<]*)</w:instrText>', doc))
                  or 'fldSimple' in doc or 'NUMPAGES' in doc)
    print(f'  ②不计页：sectPr数={len(sects)} pgNumType={len(pgnum)} PAGE/fldSimple/NUMPAGES域={"有(红旗)" if page_field else "无"} | {"PASS" if len(pgnum)==0 and not page_field else "红旗"}')
    # ③ A4 + ④ pgMar
    for i, s in enumerate(sects, 1):
        sz = re.search(r'<w:pgSz([^>]*)/>', s)
        mar = re.search(r'<w:pgMar([^>]*)/>', s)
        szs = sz.group(1) if sz else '(缺pgSz)'
        mars = mar.group(1) if mar else '(缺pgMar)'
        print(f'  ③sect#{i} pgSz{szs.strip()}')
        print(f'  ④sect#{i} pgMar{mars.strip()}')
        m = dict(re.findall(r'w:(\w+)="(-?\d+)"', mars))
        four = [m.get(k) for k in ('top', 'left', 'bottom', 'right')]
        ok4 = all(v == '850' for v in four)
        print(f'     四边850：{"PASS" if ok4 else "红旗："+str(four)}（header={m.get("header")},footer={m.get("footer")}）')
    # ⑤ 全左对齐：jc仅left或无（册目录页右对齐制表位不经jc）
    jcs = re.findall(r'<w:jc w:val="([^"]+)"', doc)
    from collections import Counter
    jc_c = Counter(jcs)
    bad_jc = {k: v for k, v in jc_c.items() if k not in ('left',)}
    print(f'  ⑤对齐：jc分布={dict(jc_c) if jc_c else "全部无jc(默认左)"} 非left={bad_jc if bad_jc else 0} | {"PASS" if not bad_jc else "红旗"}')
    # w:ind（册目录页例外=层级缩进；其余件应为0或仅制表位类）
    inds = re.findall(r'<w:ind\b[^>]*/>', doc)
    ind_left = [i for i in inds if 'w:left' in i and 'w:left="0"' not in i]
    print(f'  ⑤b缩进：w:ind总数={len(inds)} 非零left={len(ind_left)}（册目录页层级缩进例外；其他件应=0）')
    # ⑥ 1页结构判定：无手动分页/无lastRenderedPageBreak分页信号/单节
    br_page = len(re.findall(r'<w:br w:type="page"\s*/>', doc))
    br_any = len(re.findall(r'<w:br\b', doc))
    lrpb = doc.count('lastRenderedPageBreak')
    paras = re.findall(r'<w:p\b[^>]*>.*?</w:p>|<w:p\b[^>]*/>', doc, re.S)
    print(f'  ⑥页数结构：段落数={len(paras)} 手动分页符={br_page} 全部w:br={br_any} lastRenderedPageBreak={lrpb} sectPr={len(sects)} → 结构上{"1页" if br_page==0 and len(sects)<=1 else "多页/需COM复核"}')
    # ⑦ docDefaults登记（观察项）
    styles = z.read('word/styles.xml').decode('utf-8') if 'word/styles.xml' in names else ''
    dd = re.search(r'<w:docDefaults>.*?</w:docDefaults>', styles, re.S)
    if dd:
        d = dd.group(0)
        rpr = re.search(r'<w:rPrDefault>(.*?)</w:rPrDefault>', d, re.S)
        ppr = re.search(r'<w:pPrDefault>(.*?)</w:pPrDefault>', d, re.S)
        rprs = (rpr.group(1).strip() if rpr else '(无)')
        pprs = (ppr.group(1).strip() if ppr else '(无)')
        print(f'  ⑦docDefaults：rPrDefault={rprs[:180]}')
        print(f'     pPrDefault={pprs[:180]}')
    # ⑧ 媒体与图（inline/anchor）
    media = [n for n in names if n.startswith('word/media/')]
    inline = doc.count('<wp:inline')
    anchor = doc.count('<wp:anchor')
    print(f'  ⑧图：media={len(media)} wp:inline={inline} wp:anchor={anchor}{"（红旗：配页件应零锚定）" if anchor else "（零锚定PASS）"}')
    z.close()
print('=' * 100)
print('完成：配页件10件断言（封面/使用说明/册目录页/部分封面×6）。')
