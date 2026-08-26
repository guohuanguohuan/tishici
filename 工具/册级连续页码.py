# -*- coding: utf-8 -*-
"""册级连续页码盖章（公共规则§7页脚条款，2026-08-26启用）
用法：python 册级连续页码.py <册名> <件1.docx> <件2.docx> ...
按装订顺序逐件：COM只读实测页数→累计偏移→sectPr写pgNumType start→页脚（共→（全册共、
NUMPAGES复杂域替换为写死的册总页数→落盘。盖章记录（各件页数/偏移/册总页数）打印供过程对账收录。
封面/册目录页不传入、不计页。任何件内容改动后须对所在册重跑本工具（先内容后页码）。
"""
import zipfile, re, os, sys, tempfile, shutil
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

def rewrite(path, start, total):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        blob = {n: z.read(n) for n in names}
    # document.xml: pgNumType
    doc = blob['word/document.xml'].decode('utf-8')
    cur = re.search(r'<w:pgNumType w:start="(\d+)"/>', doc)
    if cur and int(cur.group(1)) == start:
        doc2 = doc  # 已是目标值，无需改写
    elif '<w:pgNumType' in doc:
        doc2 = re.sub(r'<w:pgNumType[^/]*/>', f'<w:pgNumType w:start="{start}"/>', doc)
    else:
        doc2 = re.sub(r'(<w:pgMar [^/]*/>)', r'\1<w:pgNumType w:start="%d"/>' % start, doc, count=1)
        assert doc2 != doc, f'pgNumType写入失败 {path}'
    # footer: （共→（全册共；NUMPAGES域→写死总页数
    ftr = blob['word/footer1.xml'].decode('utf-8')
    ftr2 = ftr.replace('页（共', '页（全册共')
    pat = re.compile(
        r'<w:r>(?:(?!</w:r>).)*?<w:fldChar w:fldCharType="begin"/>(?:(?!</w:r>).)*?</w:r>'
        r'<w:r>(?:(?!</w:r>).)*?NUMPAGES(?:(?!</w:r>).)*?</w:r>'
        r'(?:(?!<w:fldChar w:fldCharType="end").)*?<w:fldChar w:fldCharType="end"/></w:r>', re.S)
    lit = f'<w:r>{RPR}<w:t>{total}</w:t></w:r>'
    ftr2, n = pat.subn(lit, ftr2)
    assert n == 1, f'NUMPAGES域替换数={n} {path}'
    assert 'NUMPAGES' not in ftr2
    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for nm in names:
            if nm == 'word/document.xml':
                zo.writestr(nm, doc2)
            elif nm == 'word/footer1.xml':
                zo.writestr(nm, ftr2)
            else:
                zo.writestr(nm, blob[nm])
    os.replace(tmp, path)

def main():
    book = sys.argv[1]
    paths = sys.argv[2:]
    pages = measure(paths)
    total = sum(pages)
    print(f'== 册级连续页码盖章：{book}（全册共{total}页）==')
    off = 1
    for p, pg in zip(paths, pages):
        rewrite(p, off, total)
        print(f'  {os.path.basename(p)[:44]} | {pg}页 | 起始页码={off}')
        off += pg

if __name__ == '__main__':
    main()
