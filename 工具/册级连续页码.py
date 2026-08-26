# -*- coding: utf-8 -*-
"""册级连续页码盖章（公共规则§7两级页码制：全册连续＋部分内独立，2026-08-26 拍板）
用法：python 册级连续页码.py <册名> <件1> <件2> | <件3> <件4> | <件5> ...
  —— 同一个「部分」的件相邻放置，部分之间用独立参数 '|' 分隔（如：讲练上、讲练下同属一章讲练部分）。
按装订顺序逐件：COM只读实测页数→累计偏移→sectPr写pgNumType start（全册级偏移）→页脚两级落盘：
  ①（共→（全册共、NUMPAGES复杂域替换为写死的册总页数（重盖时更新既有写死值）；
  ②页尾追加写死「·本部第A–B页（共N页）」＝该件在其部分内的起止页/部分总页数（部分内跨件衔接：
    首件A=1、末件B=N、后件A=前件B+1；重盖时先清旧本部段再写新值，幂等可重跑）。
盖章记录（各件页数/全册偏移/本部区间/部分数）打印供过程对账收录。
封面/册目录页不传入、不计页。任何件内容改动后须对所在册重跑本工具（先内容后页码，页码最后盖）。
"""
import zipfile, re, os, sys
import win32com.client

RPR = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
       'w:eastAsia="宋体" w:cs="Times New Roman"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>')

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
    # footer：幂等清旧本部段（必须在前缀替换前——本部段文本内也含「页（共」子串，先替换会破坏清段匹配）；
    # 清段模式兼容「页（共/页（全册共」两种形态；随后前缀→全册共、总页数写死（首盖替换NUMPAGES域／重盖更新既有值）
    ftr = blob['word/footer1.xml'].decode('utf-8')
    ftr, nstrip = re.subn(
        r'<w:r>(?:(?!</w:r>).)*?<w:t>·本部第\d+[–-]\d+页（(?:全册)?共\d+页）</w:t></w:r>', '', ftr, flags=re.S)
    assert nstrip <= 1, f'旧本部段清除数={nstrip} {path}'
    ftr = ftr.replace('页（共', '页（全册共')
    pat = re.compile(
        r'<w:r>(?:(?!</w:r>).)*?<w:fldChar w:fldCharType="begin"/>(?:(?!</w:r>).)*?</w:r>'
        r'<w:r>(?:(?!</w:r>).)*?NUMPAGES(?:(?!</w:r>).)*?</w:r>'
        r'(?:(?!<w:fldChar w:fldCharType="end").)*?<w:fldChar w:fldCharType="end"/></w:r>', re.S)
    lit = f'<w:r>{RPR}<w:t>{total}</w:t></w:r>'
    ftr, n = pat.subn(lit, ftr)
    if n == 0:  # 重盖：更新既有写死总页数
        upd = re.compile(r'(<w:t>页（全册共</w:t></w:r>)<w:r>(?:(?!</w:r>).)*?<w:t>\d+</w:t></w:r>', re.S)
        ftr, n2 = upd.subn(r'\g<1>' + lit, ftr)
        assert n2 == 1, f'总页数写死run定位失败 {path}'
    else:
        assert n == 1, f'NUMPAGES域替换数={n} {path}'
    assert 'NUMPAGES' not in ftr
    assert ftr.count('<w:t>页）</w:t>') == 1, f'「页）」run数异常 {path}'
    bun = f'<w:r>{RPR}<w:t>·本部第{pa}–{pb}页（共{pn}页）</w:t></w:r>'
    ftr = ftr.replace('<w:t>页）</w:t></w:r>', '<w:t>页）</w:t></w:r>' + bun, 1)
    assert ftr.count(f'·本部第{pa}–{pb}页（共{pn}页）') == 1, f'本部段写入失败 {path}'
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
            print(f'  [部{gi}] {os.path.basename(p)[:44]} | {pg}页 | 全册起始页码={off} | 本部第{poff}–{poff+pg-1}页（共{pn}页）')
            off += pg; poff += pg

if __name__ == '__main__':
    main()
