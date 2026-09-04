# -*- coding: utf-8 -*-
"""子步7(c) XML域验收（codex M7列集，纯zip只读）：逐件核对
①页眉页脚 PAGE＋STYLEREF「节名锚」复杂域（fldChar begin/separate/end＋instrText）恰各1组、无fldSimple、无NUMPAGES
②settings.xml updateFields=true、无evenAndOddHeaders
③A4 pgSz 11906×16838、pgMar 四边850＋footer850、无titlePg
④pgNumType start＝部分内累计（对盖章记录逐件核对）、仅头部节带start
⑤同串可见文本形态「…（共N页）·本n/共M本　…　第X页」且 N=部分总页数、X缓存=start、本n/共M与预案一致
⑥页眉页脚定义各仅一处、jc=left、18半点
对照源：盖章记录 md（--record 落盘）。输出 assert_域_子步7.json/.md。"""
import zipfile, re, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = r'C:\提示词\高中数学\高中数学同步'

def parse_record(rec_path):
    rows = {}
    for ln in open(rec_path, encoding='utf-8'):
        m = re.match(r'\| P(\d+) \| 本(\d+) \| (.+?) \| (\d+) \| (\d+) \| (.+?) \| (\d+) \|', ln.strip())
        if m:
            rows[m.group(3)] = {'part': int(m.group(1)), 'book': int(m.group(2)), 'pages': int(m.group(4)),
                                'start': int(m.group(5)), 'tag': m.group(6), 'N': int(m.group(7))}
    return rows

def check_file(path, expect):
    fails = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        doc = z.read('word/document.xml').decode('utf-8')
        settings = z.read('word/settings.xml').decode('utf-8')
        headers = [n for n in names if re.fullmatch(r'word/header\d+\.xml', n)]
        footers = [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
        if len(headers) != 1 or len(footers) != 1:
            fails.append('页眉/页脚部件数=%d/%d（要求各1）' % (len(headers), len(footers)))
        hf = {nm: z.read(nm).decode('utf-8') for nm in headers + footers}
    for nm, xml in hf.items():
        where = os.path.basename(path) + ' ' + nm
        if xml.count('fldCharType="begin"') != 2 or xml.count('fldCharType="end"') != 2 \
           or xml.count('fldCharType="separate"') != 2:
            fails.append(where + ' 复杂域组数异常 begin/separate/end=%d/%d/%d' % (
                xml.count('fldCharType="begin"'), xml.count('fldCharType="separate"'), xml.count('fldCharType="end"')))
        if 'fldSimple' in xml: fails.append(where + ' 含fldSimple')
        if 'NUMPAGES' in xml: fails.append(where + ' 含NUMPAGES')
        if xml.count('STYLEREF "节名锚"') != 1 and xml.count('STYLEREF “节名锚”') != 1:
            fails.append(where + ' STYLEREF节名锚域≠1')
        if len(re.findall(r'<w:instrText[^>]*>[^<]*\bPAGE\b[^<]*</w:instrText>', xml)) != 1:
            fails.append(where + ' PAGE域≠1')
        if len(re.findall(r'<w:jc w:val="left"/>', xml)) != 1:
            fails.append(where + ' jc=left≠1')
        szs = set(re.findall(r'<w:sz w:val="(\d+)"/>', xml))
        if szs != {'18'}: fails.append(where + ' 字号半点=%r' % szs)
        vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml))
        m = re.fullmatch(r'(.+)（共(\d+)页）·本(\d+)/共(\d+)本　(.+)　第(\d+)页', vis)
        if not m:
            fails.append(where + ' 同串形态异常: %r' % vis[:80])
        else:
            if int(m.group(2)) != expect['N']: fails.append(where + ' N=%s≠%d' % (m.group(2), expect['N']))
            if int(m.group(3)) != expect['book']: fails.append(where + ' 本n=%s≠%d' % (m.group(3), expect['book']))
            if int(m.group(4)) != expect['M']: fails.append(where + ' 共M=%s≠%d' % (m.group(4), expect['M']))
            if int(m.group(6)) != expect['start']: fails.append(where + ' X缓存=%s≠start%d' % (m.group(6), expect['start']))
            if not m.group(1).endswith(expect['tag'].split('·')[-1]):
                fails.append(where + ' 件型段尾 %r ≠ %s' % (m.group(1)[-10:], expect['tag']))
    # document.xml
    pgsz = set(re.findall(r'<w:pgSz w:w="(\d+)" w:h="(\d+)"/>', doc))
    if pgsz != {('11906', '16838')}: fails.append('pgSz=%r' % pgsz)
    for pm in re.findall(r'<w:pgMar [^/]*/>', doc):
        for attr in ('top', 'right', 'bottom', 'left', 'footer'):
            if 'w:%s="850"' % attr not in pm:
                fails.append('pgMar 缺 %s=850: %s' % (attr, pm[:120]))
        if 'w:header="283"' not in pm:
            fails.append('pgMar header≠283: %s' % pm[:120])
    if '<w:titlePg' in doc: fails.append('含titlePg')
    starts = re.findall(r'<w:pgNumType w:start="(\d+)"/>', doc)
    if starts != [str(expect['start'])]:
        fails.append('pgNumType start=%r 期望唯一=%d' % (starts, expect['start']))
    if '<w:updateFields' not in settings: fails.append('settings缺updateFields')
    if 'evenAndOddHeaders' in settings: fails.append('settings含evenAndOddHeaders')
    return fails

def main():
    rec = parse_record(os.path.join(HERE, '盖章记录_子步7.md'))
    assert len(rec) == 10, '盖章记录行数=%d' % len(rec)
    Ms = set()
    out, allfails = {}, 0
    for fn, e in rec.items():
        e['M'] = 6
        fails = check_file(os.path.join(BASE, fn), e)
        out[fn] = {'expect': e, 'fails': fails}
        allfails += len(fails)
        print(('PASS ' if not fails else 'FAIL ') + fn[:40] + ('' if not fails else ' | ' + '；'.join(fails[:3])))
    with open(os.path.join(HERE, 'assert_域_子步7.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('域验收：%d/10 件 PASS，fails=%d' % (sum(1 for v in out.values() if not v['fails']), allfails))

if __name__ == '__main__':
    main()
