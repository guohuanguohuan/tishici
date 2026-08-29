# -*- coding: utf-8 -*-
"""册级连续页码盖章（公共规则§7两级页码制：全册连续＋部分内独立）
用法：python 册级连续页码.py <册名> <件1> <件2> | <件3> <件4> | <件5> ... [--record 盖章记录md]
  —— 同一个「部分」的件相邻放置，部分之间用独立参数 '|' 分隔（如：讲练上、讲练下同属一章讲练部分）；
  --record 可选：盖章记录（逐件页数/starts/Y/A–B/N）落盘 md（不传则仅 stdout 打印）；
  单册/单件测试＝只传一个件（一册一部分一件），全册配置接口不变。
按装订顺序逐件：COM只读实测页数→累计偏移→sectPr写pgNumType start（全册级偏移）→页脚整段落重建：
  【2026-08-29 成书形态拍板文案改版（规格§3.1）】新文案串＝
    「全册第{PAGE}/{Y}页　{件标识}（位于{A}–{B}页·共{N}页）」
    例「全册第258/357页　第2章·讲练（位于106–141页·共206页）」——
    X＝PAGE 复杂域唯一自动数（fldChar begin/separate/end＋instrText，缓存结果run刷写为该件首页
    实测页码＝sectPr start 值）；Y/A–B/N 写死实测值（Y＝册总页数＝各件页数和；A–B＝该件在其部分内
    起止页；N＝部分总页数；部分内跨件衔接：首件A=1、末件B=N、后件A=前件B+1）；「页」与件标识间
    全角空格；A–B 用 EN DASH（–，U+2013）；件标识沿用既有页脚文本自动提取（旧串「第X章·件型」）。
  旧文案「件标识　第X页（全册共Y页）·本部位于第a–b页（共c页）」废止——整段重建天然清旧串，
    兼容旧版/新版两种起态，幂等可重跑（重盖时 Y/A–B/N 随新实测值整体重写）。
  机制保留：pgNumType start、settings.xml updateFields（缺失自动补写）、单 PAGE 复杂域、
    无 NUMPAGES/fldSimple 断言、页脚 run 五号宋体/Times New Roman、左对齐段。
封面/册目录页/使用说明页等配页件不传入即不计页、不被改写（只处理显式传入的件）。任何件内容改动后
须对所在册重跑本工具（先内容后页码，页码最后盖）。
沿革：2026-08-26 两级页码制拍板→2026-08-28 文案直白化→2026-08-29 成书形态拍板本文案（旧串废止）。
"""
import zipfile, re, os, sys
import win32com.client

RPR = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
       'w:eastAsia="宋体" w:cs="Times New Roman"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>')
ENDASH = '\u2013'   # – EN DASH（A–B 区间连接号）

def measure(paths):
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False; word.DisplayAlerts = 0
    pages = []
    try:
        for p in paths:
            doc = word.Documents.Open(os.path.abspath(p), ReadOnly=True, AddToRecentFiles=False)
            pages.append(doc.ComputeStatistics(2))
            doc.Close(False)
    finally:
        word.Quit()
    return pages

def _visible(ftr):
    return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', ftr))

def extract_tag(ftr):
    """从页脚可见文本提取件标识。兼容旧串（{件标识}　第X页（全册共…）与
    新串（全册第X/Y页　{件标识}（位于…）两种起态。"""
    vis = _visible(ftr)
    if vis.startswith('全册第'):
        i = vis.find('　'); j = vis.find('（位于')
        assert i > 0 and j > i, '新串页脚件标识锚未找到: %r' % vis[:40]
        tag = vis[i + 1:j]
    else:
        i = vis.find('　')
        assert i > 0, '旧串页脚件标识锚（首个全角空格）未找到: %r' % vis[:40]
        tag = vis[:i]
    assert tag.strip(), '件标识为空'
    return tag

def extract_page_field(ftr):
    """提取 PAGE 复杂域整段 run 序列（begin→end，含缓存结果 run）。断言全 footer 唯一域、无 NUMPAGES。"""
    assert 'NUMPAGES' not in ftr and 'fldSimple' not in ftr, '域形态残留（NUMPAGES/fldSimple）'
    n_begin = ftr.count('fldCharType="begin"')
    assert n_begin == 1, 'fldChar begin 数=%d（预期1）' % n_begin
    ib = ftr.find('<w:fldChar w:fldCharType="begin"/>')
    ie = ftr.find('<w:fldChar w:fldCharType="end"/>')
    assert 0 <= ib < ie, 'PAGE 域 begin/end 定位失败'
    rs = ftr.rfind('<w:r>', 0, ib)
    re_ = ftr.find('</w:r>', ie)
    assert rs >= 0 and re_ > 0
    field = ftr[rs:re_ + len('</w:r>')]
    assert field.count('PAGE') >= 1, 'PAGE instrText 不在提取域内'
    return field

def flush_cache(field, start):
    """域内缓存结果 run（separate 与 end 之间）刷写为 start。"""
    pat = re.compile(r'(<w:fldChar w:fldCharType="separate"/></w:r><w:r>(?:(?!</w:r>).)*?<w:t[^>]*>)(\d+)(</w:t>)', re.S)
    field2, n = pat.subn(lambda m: m.group(1) + str(start) + m.group(3), field)
    assert n == 1, 'PAGE 域缓存run数=%d（预期1）' % n
    return field2

def _run(text):
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (RPR, text)

def rebuild_footer(ftr, start, total, tag, pa, pb, pn):
    """页脚段整段重建为新文案串（保留 pPr 与 PAGE 复杂域本体；缓存刷写为 start）。幂等。"""
    field = flush_cache(extract_page_field(ftr), start)
    static = (_run('全册第') + field + _run('/%d页' % total) + _run('　') + _run(tag)
              + _run('（位于%d%s%d页·共%d页）' % (pa, ENDASH, pb, pn)))
    m = re.search(r'<w:p\b[^>]*>.*?</w:p>', ftr, re.S)
    assert m, '页脚段 <w:p> 未找到'
    para = m.group(0)
    mp = re.search(r'<w:pPr>.*?</w:pPr>', para, re.S)
    ppr = mp.group(0) if mp else '<w:pPr><w:jc w:val="left"/></w:pPr>'
    new_para = '<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">%s%s</w:p>' % (ppr, static)
    return ftr[:m.start()] + new_para + ftr[m.end():]

def ensure_update_fields(settings_xml):
    """settings.xml 含 <w:updateFields w:val="true"/>（缺失自动补写；渲染器开卷即刷新域缓存）。"""
    if '<w:updateFields' in settings_xml:
        return settings_xml, False
    ins = '<w:updateFields w:val="true"/>'
    if '<w:compat' in settings_xml:
        return settings_xml.replace('<w:compat', ins + '<w:compat', 1), True
    return settings_xml.replace('</w:settings>', ins + '</w:settings>'), True

def rewrite(path, start, total, pa, pb, pn):
    """start=全册起始页码；total=册总页数；pa/pb=该件在部分内的起/止页；pn=部分总页数。"""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        blob = {n: z.read(n) for n in names}
    # document.xml: pgNumType（全册级偏移）
    doc = blob['word/document.xml'].decode('utf-8')
    cur = re.search(r'<w:pgNumType w:start="(\d+)"/>', doc)
    if cur and int(cur.group(1)) == start:
        doc2 = doc  # 已是目标值，无需改写
    elif '<w:pgNumType' in doc:
        doc2 = re.sub(r'<w:pgNumType[^/]*/>', f'<w:pgNumType w:start="{start}"/>', doc)
    else:
        doc2 = re.sub(r'(<w:pgMar [^/]*/>)', r'\1<w:pgNumType w:start="%d"/>' % start, doc, count=1)
        assert doc2 != doc, f'pgNumType写入失败 {path}'
    # footer1.xml：件标识提取＋整段重建（新文案串）
    ftr = blob['word/footer1.xml'].decode('utf-8')
    tag = extract_tag(ftr)
    ftr2 = rebuild_footer(ftr, start, total, tag, pa, pb, pn)
    vis = _visible(ftr2)
    expect_head = '全册第'
    assert vis.startswith(expect_head), '页脚重建后前缀异常: %r' % vis[:20]
    assert ('（位于%d%s%d页·共%d页）' % (pa, ENDASH, pb, pn)) in vis, '本部区间串缺失'
    assert '　' + tag + '（位于' in vis, '件标识段形态异常'
    assert 'NUMPAGES' not in ftr2 and 'fldSimple' not in ftr2, '域形态残留 %s' % path
    # settings.xml：updateFields 保障
    st = blob['word/settings.xml'].decode('utf-8')
    st2, added = ensure_update_fields(st)
    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for nm in names:
            if nm == 'word/document.xml':
                zo.writestr(nm, doc2)
            elif nm == 'word/footer1.xml':
                zo.writestr(nm, ftr2)
            elif nm == 'word/settings.xml':
                zo.writestr(nm, st2)
            else:
                zo.writestr(nm, blob[nm])
    os.replace(tmp, path)
    return tag

def main():
    argv = sys.argv[1:]
    record_md = None
    if '--record' in argv:
        i = argv.index('--record')
        record_md = argv[i + 1]
        del argv[i:i + 2]
    book = argv[0]
    args = argv[1:]
    parts, cur = [], []
    for a in args:
        if a == '|':
            assert cur, '部分边界"|"位置异常：连续两个边界或以边界开头'
            parts.append(cur); cur = []
        else:
            cur.append(a)
    assert cur, '件列表为空'
    parts.append(cur)
    flat = [p for grp in parts for p in grp]
    pages = measure(flat)
    total = sum(pages)
    print(f'== 两级页码盖章：{book}（全册共{total}页，{len(parts)}个部分）==')
    rec = [f'# 两级页码盖章记录 — {book}',
           '',
           f'盖章时间标记：基线实测（全册共{total}页，{len(parts)}个部分；Y={total}）',
           '',
           '| 部分 | 件 | 页数 | start（全册起始页码） | 件标识 | A–B（部分内） | N（部分页数） |',
           '|---|---|---|---|---|---|---|']
    off = 1
    pit = iter(pages)
    for gi, grp in enumerate(parts, 1):
        gp = [next(pit) for _ in grp]
        pn = sum(gp)
        poff = 1
        for p, pg in zip(grp, gp):
            tag = rewrite(p, off, total, poff, poff + pg - 1, pn)
            print(f'  [部{gi}] {os.path.basename(p)[:44]} | {pg}页 | 全册起始页码={off} | {tag}（位于{poff}{ENDASH}{poff+pg-1}页·共{pn}页）')
            rec.append('| %d | %s | %d | %d | %s | %d%s%d | %d |'
                       % (gi, os.path.basename(p), pg, off, tag, poff, ENDASH, poff + pg - 1, pn))
            off += pg; poff += pg
    rec.append('')
    rec.append('恒等式：首件 start=1；后件 start=前件（start+页数）；各部分首件 A=1、末件 B=N、后件 A=前件B+1；Y=%d=各件页数和。' % total)
    if record_md:
        open(record_md, 'w', encoding='utf-8').write('\n'.join(rec) + '\n')
        print('盖章记录 -> %s' % record_md)

if __name__ == '__main__':
    main()
