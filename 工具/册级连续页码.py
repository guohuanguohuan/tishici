# -*- coding: utf-8 -*-
r"""部分独立页码盖章（公共规则§7部分独立页码制·2026-08-31 N8改版；旧「全册连续＋A–B区间」两级制全部废止）

用法：
  python 工具/册级连续页码.py --parts <parts.json> [--record <盖章记录.md>]

配置文件 parts.json（UTF-8，相对路径一律相对配置文件所在目录解析）：
  {
    "book":  "人教B版选必1",                      // 册名（仅用于记录/打印标题）
    "parts": [                                     // 按装订顺序列出全部「部分」（P1..Pn）
      {"tag": "第1章·衔接", "files": ["衔接件.docx"]},
      {"tag": "第1章·清单", "files": ["知识清单.docx"]},
      {"tag": "第1章·讲练", "files": ["讲上.docx", "讲下.docx"]}   // 同部分多卷依序排列
    ],
    "skip_files": ["封面.docx", "使用说明.docx", ...]  // 可选：配页件清单（封面/册目录页/使用说明页/
                                                      // 错题记录/部分封面）——不属任何部分、不计数、
                                                      // 不盖章，显式列入即可整册装订单式配置直传，本工具跳过
  }
  ——「部分」＝同章同类型件的全部文件（公共规则§7）：同部分各卷页码跨卷连续、件标识一致（分卷不加卷次），
    tag 从配置取（如「第1章·衔接／第1章·清单／第1章·讲练」，高中同步总控§5件标识对照）。

盖章语义（对 parts 内每个文件，按序）：
  1. COM 只读实测页数（ComputeStatistics(wdStatisticPages)，实测值为源）；
  2. 部分内累计：每部分首件 sectPr <w:pgNumType w:start="1"/>，同部分后件 start＝该件之前同部分
     各件累计页数＋1；N＝该部分总页数（各件页数之和，COM实测）；
  3. 页脚整段重建（全文唯一一个页脚定义、左对齐）：
       「件标识（共N页）＋全角空格＋第X页」，例「第1章·讲练（共155页）　第5页」
     —— X＝PAGE 复杂域（fldChar begin/separate/end＋w:instrText，禁 fldSimple），域缓存结果 run
       刷写为按 start 推算的首页实测值（＝start）；N＝写死文本（禁 NUMPAGES，检测到即随整段重建拆除）；
     —— 页码 9pt（w:sz=18半点）：中文宋体、西文/数字 Times New Roman；
  4. w:pgMar w:footer 统一 850 缇（页脚距页底1.5厘米）；剔除 w:titlePg（不勾「首页不同」）；
  5. settings.xml 确保 <w:updateFields w:val="true"/>（缺失自动补写）。
收敛迭代（2026-08-31 T1实测发现，必须在同一工具内闭环）：footer距边850＝下边距850（零余量），
  页脚行高参与正文区计算——旧件页脚字号改9pt（18半点）后正文区微增、临界件会repaginate
  （实测讲上79→78页），「先测量后盖章」一步制会给自己盖出作废数字。故按不动点迭代执行：
  实测→按当前数字盖章→复测→页数有变则以新页数重盖，循环至复测页数与所盖数字一致（实测2轮内收敛；
  上限5轮不收敛即报错退出）。

幂等：全重建为确定性构造（无时间戳、无随机序），重复跑输出逐字节不变（zip成员级）。
--record：盖章记录 md 落盘（逐件 页数/start/件标识/N 表），供册目录页/装订单/工具·节页码定位.py 同源
  引用（该工具按件名 basename 匹配 start）；记录不含时间戳，「先内容后页码」的先后核对以本文件
  落盘时间（mtime）为准——任何件内容改动后须重跑本工具并刷新记录。
配页件（skip_files 与 parts 之外的一切文件）不传入即不被触碰；传入 skip_files 的只打印跳过行。
沿革：2026-08-26 两级页码制→2026-08-29 成书形态文案→2026-08-30 A–B区间→
  2026-08-31 N8 部分独立页码制（本版；旧「全册第X/Y页　件标识（位于A–B页·共N页）」文案随本版废止，
  整段重建天然清旧串，兼容任意旧版/新版起态）。
"""
import argparse
import json
import os
import re
import sys
import io
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import win32com.client
except ImportError:
    print('错误：需要 pywin32（import win32com.client 失败）', file=sys.stderr)
    sys.exit(3)

RPR = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
       'w:eastAsia="宋体" w:cs="Times New Roman"/>'
       '<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>')   # 页码9pt＝18半点（N8/§7）
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
FOOTER_TWIPS = 850   # 页脚距页底1.5厘米＝850缇（§7页面条款）


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def measure(paths):
    """COM 只读开卷逐件实测页数（wdStatisticPages=2）；自建实例用完 Quit。"""
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    pages = []
    try:
        for p in paths:
            doc = word.Documents.Open(os.path.abspath(p), ReadOnly=True, AddToRecentFiles=False)
            try:
                pages.append(doc.ComputeStatistics(2))
            finally:
                doc.Close(False)
    finally:
        word.Quit()
    return pages


def _run(text):
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (RPR, esc(text))


def page_field(cache):
    """PAGE 复杂域（fldChar begin/separate/end＋instrText；缓存结果run＝cache）。禁 fldSimple（§7）。"""
    return ('<w:r>%s<w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r>%s<w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
            '<w:r>%s<w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r>%s<w:t xml:space="preserve">%d</w:t></w:r>'
            '<w:r>%s<w:fldChar w:fldCharType="end"/></w:r>') % (RPR, RPR, RPR, RPR, cache, RPR)


def rebuild_footer(ftr, start, part_total, tag):
    """页脚整段重建为「件标识（共N页）　第X页」。全文唯一页脚定义＝单段（多段落归一，页脚除件标识
    与页码外不得有其他内容——§7）；旧串（含 NUMPAGES/fldSimple 等任何旧域形态）随整段重建一并拆除，
    X 改挂新建 PAGE 复杂域（缓存=start）。确定性构造、幂等。"""
    expect = '%s（共%d页）　第%d页' % (tag, part_total, start)
    body = (_run('%s（共%d页）' % (tag, part_total)) + _run('　')
            + _run('第') + page_field(start) + _run('页'))
    para = '<w:p xmlns:w="%s"><w:pPr><w:jc w:val="left"/></w:pPr>%s</w:p>' % (W_NS, body)
    n_para = len(re.findall(r'<w:p\b.*?</w:p>', ftr, re.S))
    assert n_para >= 1, '页脚段落未找到'
    ftr2 = re.sub(r'<w:p\b.*?</w:p>', '', ftr, flags=re.S)          # 删全部旧段（多段归一）
    assert '</w:ftr>' in ftr2, '页脚根元素 </w:ftr> 未找到'
    ftr2 = ftr2.replace('</w:ftr>', para + '</w:ftr>')
    vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', ftr2))
    assert vis == expect, '页脚可见文本异常: %r（预期 %r）' % (vis, expect)
    return ftr2


def stamp_document(doc, start):
    """document.xml：每个 sectPr 写 pgNumType start；pgMar footer 统一850；剔除 titlePg。"""
    d = doc
    n_title = d.count('<w:titlePg')
    d = d.replace('<w:titlePg/>', '').replace('<w:titlePg>', '')
    d = re.sub(r'<w:titlePg[^>]*/>', '', d)

    def fix_sect(s):
        s = re.sub(r'<w:pgNumType[^>]*/>', '', s)                       # 清旧值（含旧start任意属性形态）
        if '<w:pgMar ' in s:
            s = re.sub(r'(<w:pgMar [^/]*/>)', r'\1<w:pgNumType w:start="%d"/>' % start, s, count=1)
        else:
            s = s.replace('</w:sectPr>', '<w:pgNumType w:start="%d"/></w:sectPr>' % start)
        s = re.sub(r'(<w:pgMar[^>]*?)w:footer="\d+"', r'\1w:footer="%d"' % FOOTER_TWIPS, s)
        if 'w:footer=' not in s and '<w:pgMar ' in s:
            s = re.sub(r'(<w:pgMar )', r'\1w:footer="%d" ' % FOOTER_TWIPS, s, count=1)
        return s

    parts = re.split(r'(<w:sectPr.*?</w:sectPr>)', d, flags=re.S)
    n_sect = 0
    for i in range(1, len(parts), 2):
        parts[i] = fix_sect(parts[i])
        n_sect += 1
    d = ''.join(parts)
    starts = re.findall(r'<w:pgNumType w:start="(\d+)"/>', d)
    assert n_sect >= 1 and all(int(x) == start for x in starts), 'pgNumType写入失败: %r' % starts
    return d, n_sect, n_title


def ensure_update_fields(settings_xml):
    """settings.xml 确保 updateFields（缺失补写）；剔除 evenAndOddHeaders（§7不勾「奇偶页不同」）。"""
    s = re.sub(r'<w:evenAndOddHeaders[^>]*/>', '', settings_xml)
    added = False
    if '<w:updateFields' not in s:
        ins = '<w:updateFields w:val="true"/>'
        if '<w:compat' in s:
            s = s.replace('<w:compat', ins + '<w:compat', 1)
        else:
            s = s.replace('</w:settings>', ins + '</w:settings>')
        added = True
    return s, added


def rewrite(path, start, part_total, tag):
    """逐件落盘：document.xml（start/footer850/去titlePg）＋唯一页脚部件（整段重建）＋settings。"""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        blob = {n: z.read(n) for n in names}
    footers = [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
    assert len(footers) == 1, ('全文必须唯一一个页脚定义（§7），%s 现有 %d 个页脚部件 %s——'
                               '请先拆除首页不同/奇偶页脚等多余页脚再盖章' % (os.path.basename(path), len(footers), footers))
    ftr_name = footers[0]

    doc = blob['word/document.xml'].decode('utf-8')
    doc2, n_sect, n_title = stamp_document(doc, start)
    ftr2 = rebuild_footer(blob[ftr_name].decode('utf-8'), start, part_total, tag)
    # 域形态断言：唯一复杂域＝PAGE；无 NUMPAGES、无 fldSimple
    assert ftr2.count('fldCharType="begin"') == 1, 'fldChar begin 数异常'
    assert ftr2.count('fldCharType="end"') == 1, 'fldChar end 数异常'
    assert 'NUMPAGES' not in ftr2 and 'fldSimple' not in ftr2, '域形态残留（NUMPAGES/fldSimple）'
    assert ' PAGE ' in ftr2, 'PAGE instrText 缺失'
    st2, added = ensure_update_fields(blob['word/settings.xml'].decode('utf-8'))

    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for nm in names:                    # 保持成员原序，幂等
            if nm == 'word/document.xml':
                zo.writestr(nm, doc2)
            elif nm == ftr_name:
                zo.writestr(nm, ftr2)
            elif nm == 'word/settings.xml':
                zo.writestr(nm, st2)
            else:
                zo.writestr(nm, blob[nm])
    os.replace(tmp, path)

    # 落盘后回读复核（同步盘干扰防：读回断言）
    with zipfile.ZipFile(path) as z:
        f = z.read(ftr_name).decode('utf-8')
        d = z.read('word/document.xml').decode('utf-8')
        s = z.read('word/settings.xml').decode('utf-8')
    vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', f))
    assert vis == '%s（共%d页）　第%d页' % (tag, part_total, start), '回读页脚不符: %r' % vis
    assert ('<w:pgNumType w:start="%d"/>' % start) in d, '回读start不符'
    assert 'w:footer="%d"' % FOOTER_TWIPS in d, '回读页脚距边不符'
    assert '<w:updateFields' in s, '回读updateFields缺失'
    return n_sect, n_title


def load_parts(cfg_path):
    """parts.json → (book, [(tag, [abs路径])], [跳过件abs路径])；相对路径相对配置文件目录。"""
    base = os.path.dirname(os.path.abspath(cfg_path))

    def norm(p):
        return p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))

    cfg = json.load(open(cfg_path, encoding='utf-8-sig'))
    book = cfg.get('book', os.path.splitext(os.path.basename(cfg_path))[0])
    parts = []
    for it in cfg.get('parts', []):
        tag = it['tag'].strip()
        files = [norm(f) for f in it['files']]
        assert tag and files, 'parts 条目缺 tag/files: %r' % it
        parts.append((tag, files))
    assert parts, 'parts 为空（无可盖章件）'
    skips = [norm(f) for f in cfg.get('skip_files', [])]
    return book, parts, skips


def apply_stamps(parts, pages, verbose=True):
    """按当前实测页数逐件盖章（部分内级联）；返回（记录行, 合计页数）。"""
    rec_rows, it, total = [], iter(pages), 0
    for pi, (tag, files) in enumerate(parts, 1):
        pg = [next(it) for _ in files]
        pn = sum(pg)
        start = 1
        for f, p in zip(files, pg):
            n_sect, n_title = rewrite(f, start, pn, tag)
            if verbose:
                print('  [P%d] %s | %d页 | start=%d | %s（共%d页） | sectPr=%d titlePg剔%d'
                      % (pi, os.path.basename(f)[:44], p, start, tag, pn, n_sect, n_title))
            rec_rows.append('| P%d | %s | %d | %d | %s | %d |'
                            % (pi, os.path.basename(f), p, start, tag, pn))
            start += p
            total += p
    return rec_rows, total


def main():
    ap = argparse.ArgumentParser(description='部分独立页码盖章（公共规则§7 N8：每部分独立从1连续、'
                                             '同部分后件start=前件累计+1、页脚「件标识（共N页）　第X页」）')
    ap.add_argument('--parts', required=True, help='parts.json 配置（book/parts[{tag,files}]/skip_files）')
    ap.add_argument('--record', help='盖章记录md落盘路径（供册目录页/装订单/节页码定位.py 同源引用）')
    args = ap.parse_args()

    book, parts, skips = load_parts(args.parts)
    for _, files in parts:
        for f in files:
            if not os.path.isfile(f):
                print('错误：文件不存在：%s' % f, file=sys.stderr)
                sys.exit(2)
    for f in skips:
        print('  跳过配页件（不属任何部分、不计数、不盖章）: %s' % os.path.basename(f))

    flat = [f for _, files in parts for f in files]
    # 不动点迭代：实测→盖章→复测至页数与所盖数字一致（页脚9pt化可使临界件repaginate，见文件头注）
    pages = measure(flat)
    print('== 部分独立页码盖章：%s（%d个部分／%d件）==' % (book, len(parts), len(flat)))
    converged = False
    for rnd in range(1, 6):
        rec_rows, total = apply_stamps(parts, pages)
        pages2 = measure(flat)
        if pages2 == pages:
            print('  收敛：第%d轮盖章后复测页数与所盖数字一致（合计%d页）' % (rnd, total))
            converged = True
            break
        print('  复测页数有变（%s→%s），以新页数重盖（第%d轮）'
              % (pages, pages2, rnd + 1))
        pages = pages2
    assert converged, '盖章5轮未收敛（页数仍在漂移）——请人工检查 %s' % flat

    rec = ['# 部分独立页码盖章记录 — %s' % book,
           '',
           '口径：公共规则§7部分独立页码制（2026-08-31 N8）——每部分独立从1连续；同部分后件start＝该件之前',
           '同部分各件累计页数＋1；N＝部分总页数（COM实测，盖章后复测收敛值）；页脚「件标识（共N页）　第X页」。',
           '本记录不含时间戳，「先内容后页码」先后核对以本文件mtime为准',
           '（工具/册级连续页码.py --parts 生成；节页码定位.py按件名匹配start）。',
           '',
           '| 部分 | 件 | 页数 | start | 件标识 | N（部分总页数） |',
           '|---|---|---|---|---|---|'] + rec_rows + [
        '', '恒等式：每部分首件start=1；同部分后件start＝前件start+页数；N＝部分内各件页数之和（COM实测）；'
            '全册合计%d页＝各件页数和（配页件不计页）。' % total]
    if args.record:
        open(args.record, 'w', encoding='utf-8').write('\n'.join(rec) + '\n')
        print('盖章记录 -> %s' % args.record)


if __name__ == '__main__':
    main()
