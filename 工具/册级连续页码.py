# -*- coding: utf-8 -*-
"""册级连续页码盖章（公共规则§7两级页码制：全册连续＋部分内独立，2026-08-26 拍板）
用法：python 册级连续页码.py <册名> <件1> <件2> | <件3> <件4> | <件5> ...
  —— 同一个「部分」的件相邻放置，部分之间用独立参数 '|' 分隔（如：讲练上、讲练下同属一章讲练部分）。
按装订顺序逐件：COM只读实测页数→累计偏移→sectPr写pgNumType start（全册级偏移）→页脚两级落盘：
  ①（共→（全册共、NUMPAGES复杂域替换为写死的册总页数（重盖时更新既有写死值）；
  ②页尾追加写死「·本部位于第A–B页（共N页）」＝该件在其部分内的起止页/部分总页数（部分内跨件衔接：
    首件A=1、末件B=N、后件A=前件B+1；重盖时先清旧本部段再写新值，幂等可重跑）。
  【2026-08-29 页脚文案直白化升级（2026-08-28 拍板）：本部段文案「·本部第A–B页」→「·本部位于第A–B页」，
    区间语义不变；清旧段逻辑同步升级为「run边界回溯＋跨run整段摘除」，兼容旧版单run形态与Word重存后的
    跨多run分裂形态（选必1衔接件实测5-run分裂，旧单run正则会漏清致双段），幂等口径不变。】
2026-08-29 增（D2工具升级，E3-F3/E1-S1六件PAGE域旧缓存治理）：盖章时把复杂域缓存结果run
  （fldChar separate 与 end 之间的数字run）刷写为该件首页实测页码＝sectPr start 值——非刷新查看器
  （静态预览类）不再显示旧布局残留页码；Word/WPS/PDF 渲染路径本就按页刷新，不受影响。
盖章记录（各件页数/全册偏移/本部区间/部分数）打印供过程对账收录。
封面/册目录页/使用说明页等配页件不传入即不计页、不被改写（只处理显式传入的件）。任何件内容改动后须对所在册
重跑本工具（先内容后页码，页码最后盖）。
"""
import zipfile, re, os, sys
import win32com.client

RPR = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
       'w:eastAsia="宋体" w:cs="Times New Roman"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>')

RUN_OPEN = re.compile(r'<w:r(?:\s[^>]*)?>')

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

def _run_text(run_xml):
    return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', run_xml))

def strip_benbu(ftr):
    """幂等清旧本部段：从含「本部」的run起、到其后首个「页）」run止整段摘除；
    若紧邻前一run恰为独立「·」run（或其文字以「·」收尾）一并处置。兼容单run与跨run分裂两种旧形态。"""
    i = ftr.find('本部')
    if i < 0:
        return ftr, 0
    opens = [m for m in RUN_OPEN.finditer(ftr) if m.start() < i]
    assert opens, '本部段前找不到run开标签'
    rs = opens[-1].start()
    # 前一run若恰为独立「·」run，段起点前移含之
    prevs = [m for m in RUN_OPEN.finditer(ftr[:rs])]
    if prevs:
        m = prevs[-1]
        prev_run = ftr[m.start():rs]
        if _run_text(prev_run) == '·':
            rs = m.start()
        elif _run_text(prev_run).endswith('·'):
            # 「·」粘在前一run尾部：仅摘除该「·」字符（取其最后一个<w:t>内删一处）
            last_t = prev_run.rfind('<w:t')
            tclose = prev_run.find('>', last_t) + 1
            prev_run_new = prev_run[:tclose] + prev_run[tclose:].replace('·', '', 1)
            ftr = ftr[:m.start()] + prev_run_new + ftr[rs:]
            opens2 = [mm for mm in RUN_OPEN.finditer(ftr) if mm.start() < i]
            rs = opens2[-1].start()
    k = ftr.find('页）', i)
    assert k > 0, '本部段内找不到收尾「页）」'
    e = ftr.find('</w:r>', k)
    assert e > 0
    e += len('</w:r>')
    return ftr[:rs] + ftr[e:], 1

def update_total(ftr, total):
    """定位「页（全册共」后首个纯数字run，整run替换为写死总页数run。兼容NUMPAGES复杂域残留（旧首盖形态先拆域）。"""
    # 首盖形态：NUMPAGES复杂域整体替换
    pat = re.compile(
        r'<w:r>(?:(?!</w:r>).)*?<w:fldChar w:fldCharType="begin"/>(?:(?!</w:r>).)*?</w:r>'
        r'<w:r>(?:(?!</w:r>).)*?NUMPAGES(?:(?!</w:r>).)*?</w:r>'
        r'(?:(?!<w:fldChar w:fldCharType="end").)*?<w:fldChar w:fldCharType="end"/></w:r>', re.S)
    lit = f'<w:r>{RPR}<w:t>{total}</w:t></w:r>'
    ftr, n = pat.subn(lit, ftr)
    if n:
        assert n == 1, f'NUMPAGES域替换数={n}'
        assert 'NUMPAGES' not in ftr
        return ftr
    # 重盖形态：既有写死值run更新
    p = ftr.find('页（全册共')
    if p < 0:  # 兼容未升级前缀的旧件：先补「全册」
        ftr2 = ftr.replace('页（共', '页（全册共')
        assert ftr2 != ftr, '页脚找不到「页（共/页（全册共」总页数锚'
        ftr = ftr2
        p = ftr.find('页（全册共')
    seg = ftr[p:]
    m = RUN_OPEN.search(seg)
    assert m, '总页数锚后无run'
    run = seg[m.start():seg.find('</w:r>', m.start()) + len('</w:r>')]
    assert re.fullmatch(r'\d+', _run_text(run)), f'总页数run非纯数字：{_run_text(run)!r}'
    return ftr[:p] + seg[:m.start()] + lit + seg[seg.find('</w:r>', m.start()) + len('</w:r>'):]

def flush_page_cache(ftr, start):
    """PAGE复杂域缓存结果run刷写为start（2026-08-29增，E3-F3/E1-S1治理；幂等：值同亦无副作用）。"""
    pat = re.compile(r'(<w:fldChar w:fldCharType="separate"/></w:r><w:r>(?:(?!</w:r>).)*?<w:t[^>]*>)(\d+)(</w:t>)', re.S)
    ftr2, n = pat.subn(lambda m: m.group(1) + str(start) + m.group(3), ftr)
    assert n == 1, f'PAGE域缓存run数={n}（预期1）'
    return ftr2

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
    # footer：幂等清旧本部段（含跨run分裂形态）→前缀→全册共→总页数写死→追加「本部位于」新段
    ftr = blob['word/footer1.xml'].decode('utf-8')
    ftr, nstrip = strip_benbu(ftr)
    assert '本部' not in ftr, f'旧本部段清除后仍有残留 {path}'
    assert nstrip <= 1, f'旧本部段清除数={nstrip} {path}'
    ftr = ftr.replace('页（共', '页（全册共')
    ftr = update_total(ftr, total)
    ftr = flush_page_cache(ftr, start)
    assert 'NUMPAGES' not in ftr and 'fldSimple' not in ftr, f'域形态残留 {path}'
    bun = f'<w:r>{RPR}<w:t>·本部位于第{pa}–{pb}页（共{pn}页）</w:t></w:r>'
    ends = [m for m in re.finditer(r'<w:t[^>]*>页）</w:t></w:r>', ftr)]
    assert len(ends) == 1, f'「页）」收尾run数={len(ends)} {path}'
    ftr = ftr[:ends[0].end()] + bun + ftr[ends[0].end():]
    assert ftr.count(f'·本部位于第{pa}–{pb}页（共{pn}页）') == 1, f'本部段写入失败 {path}'
    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for nm in names:
            if nm == 'word/document.xml':
                zo.writestr(nm, doc2)
            elif nm == 'word/footer1.xml':
                zo.writestr(nm, ftr)
            else:
                zo.writestr(nm, blob[nm])
    os.replace(tmp, path)

def main():
    book = sys.argv[1]
    args = sys.argv[2:]
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
    off = 1
    pit = iter(pages)
    for gi, grp in enumerate(parts, 1):
        gp = [next(pit) for _ in grp]
        pn = sum(gp)
        poff = 1
        for p, pg in zip(grp, gp):
            rewrite(p, off, total, poff, poff + pg - 1, pn)
            print(f'  [部{gi}] {os.path.basename(p)[:44]} | {pg}页 | 全册起始页码={off} | 本部位于第{poff}–{poff+pg-1}页（共{pn}页）')
            off += pg; poff += pg

if __name__ == '__main__':
    main()
