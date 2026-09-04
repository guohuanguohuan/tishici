# -*- coding: utf-8 -*-
r"""部分独立页码盖章（公共规则§7部分独立页码制；2026-09-02 A''成品轮多sectPr＋本n/共M段版）
  A''升级（2026-09-02）：
  · 多sectPr适配——双栏制后每件2节（头部单栏节＋正文双栏节）：pgNumType start 只落首个（头部）节
    sectPr（§7「册级连续页码start落头部节sectPr」），后续节清除 pgNumType（页码连续继承，防重启）；
  · 同串加「本n/共M本」段——「…（共N页）·本n/共M本　节号节名　第X页」；n＝该件所属物理本序（默认＝
    部分序号pi，每部分一物理本——同步线粒度；二次拆分/聚合经配置 book_map 覆盖）、M＝册内物理本总数
    （默认＝部分总数；分层卷派生后随新配置重跑即联动）；两段随N一并写死；
  · 串宽预检——同串可见字符估算宽度超页眉可用宽（10206缇＝510pt）时自动剥「羿郭工作室·」品牌前缀
    （页眉部件；§7允许项），逐件登记；页脚不剥。

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
    "skip_files": ["封面.docx", "使用说明.docx", ...]  // 可选：配页件清单——不属任何部分、不计数、
                                                      // 不盖章，显式列入即可整册装订单式配置直传
  }
  ——「部分」＝同章同类型件的全部文件（公共规则§7）：同部分各卷页码跨卷连续、件标识一致（分卷不加卷次），
    tag 从配置取（如「第1章·衔接／第1章·清单／第1章·讲练」，高中同步总控§5件标识对照）。

前置依赖（2026-09-01起，A'改制轮口径F/G）：每个被盖章件必须先经 工具/页眉面包屑挂载.py 挂载
  「同串＋节名锚」骨架——页眉页脚为同串（「羿郭工作室·册名 第X章 章名·件型（共N页）　节号节名　第X页」，
  含 STYLEREF "节名锚" 复杂域＋PAGE 复杂域）；未挂载件报错退出（不代行挂载——管线序＝先挂载后盖章）。

盖章语义（对 parts 内每个文件，按序）：
  1. COM 只读实测页数（ComputeStatistics(wdStatisticPages)，实测值为源）；
  2. 部分内累计：每部分首件 sectPr <w:pgNumType w:start="1"/>，同部分后件 start＝该件之前同部分
     各件累计页数＋1；N＝该部分总页数（各件页数之和，COM实测）；
  3. 同串盖章（对页眉与页脚两部件同步、外科手术式——不重建骨架、前段与节名域原样保留）：
       · X域缓存：页眉页脚两处 PAGE 复杂域缓存 run 同步刷写为该件 start 实测值
         （PAGE域缓存不随sectPr start自动更新、静态查看器显旧值——flush_page_cache）；
       · N写死：两部件「（共N页）」处占位/旧值替换为部分总页数实测值（禁 NUMPAGES）；
       · 节名段 STYLEREF 域缓存不动（Word/打印/PDF链路必然重算，§7备案口径）；
  4. document.xml：sectPr pgNumType start 写值（部分内级联）＋w:pgMar w:footer 统一850缇＋剔titlePg；
  5. settings.xml 确保 <w:updateFields w:val="true"/>（缺失自动补写）＋剔evenAndOddHeaders。
收敛迭代（2026-08-31 T1实测发现，必须在同一工具内闭环）：footer距边850＝下边距850（零余量），
  页脚行高参与正文区计算——页脚/页眉字号变化后正文区微变、临界件会repaginate，「先测量后盖章」
  一步制会给自己盖出作废数字。故按不动点迭代执行：实测→按当前数字盖章→复测→页数有变则以新页数
  重盖，循环至复测页数与所盖数字一致（实测2轮内收敛；上限5轮不收敛即报错退出）。
幂等（0901幂等重盖章法）：外科手术式替换为确定性操作（无时间戳、无随机序），页数零漂移时重复跑
  输出逐字节不变（zip成员级；容器md5仅重打包时间戳差异——经验定论）。
--record：盖章记录 md 落盘（逐件 页数/start/件标识/N 表），供册目录页/装订单/工具·节页码定位.py
  同源引用（该工具按件名 basename 匹配 start）；记录不含时间戳，「先内容后页码」的先后核对以本文件
  落盘时间（mtime）为准——任何件内容改动后须重跑本工具并刷新记录。
配页件（skip_files 与 parts 之外的一切文件）不传入即不被触碰；传入 skip_files 的只打印跳过行。
沿革：2026-08-26 两级页码制→2026-08-29 成书形态文案→2026-08-30 A–B区间→2026-08-31 N8 部分独立
  页码制（页脚整段重建「件标识（共N页）　第X页」）→2026-09-01 A'改制轮工具债⑥适配同串形态（本版；
  旧整段重建式页脚随口径F退役——本工具不再构造页脚文本，只对挂载骨架做 X缓存双写＋N写死＋start级联）。
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

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
FOOTER_TWIPS = 850   # 页脚距页底1.5厘米＝850缇（§7页面条款）；parts.json 可选 footer_twips{件basename:缇} 按件覆盖（0904选必1 C/H=567缇：页脚零占位实证——页脚整行沉进下边距空白区、不吃正文，页数回本）
INSTR_STYLEREF = 'STYLEREF "节名锚"'
INSTR_PAGE_RE = re.compile(r'<w:instrText[^>]*>[^<]*\bPAGE\b[^<]*</w:instrText>')


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


def locate_page_cache(xml):
    """定位PAGE域缓存run文本（separate后第一个w:t的内部文本）——读回复核用。"""
    ms = INSTR_PAGE_RE.findall(xml)
    assert len(ms) == 1, 'PAGE instrText 数=%d' % len(ms)
    m = INSTR_PAGE_RE.search(xml)
    i_sep = xml.index('w:fldCharType="separate"', m.end())
    j = xml.index('<w:t', i_sep)
    gt = xml.index('>', j)
    k = xml.index('</w:t>', j)
    return xml[gt + 1:k]


def flush_page_cache(xml, start):
    """PAGE复杂域缓存刷写：定位 PAGE instrText → 其后第一个 separate → 其后第一个 w:t 文本置为 start。
    PAGE域缓存不随sectPr start自动更新（静态查看器显旧值）——经验定论；幂等（重复刷写同值）。"""
    ms = INSTR_PAGE_RE.findall(xml)
    assert len(ms) == 1, 'PAGE instrText 数=%d（要求恰1——同串单PAGE域）' % len(ms)
    m = INSTR_PAGE_RE.search(xml)
    i_sep = xml.index('w:fldCharType="separate"', m.end())
    j = xml.index('<w:t', i_sep)
    gt = xml.index('>', j)
    k = xml.index('</w:t>', j)
    i_end = xml.index('w:fldCharType="end"', k)
    assert i_end > k, 'PAGE域separate与end之间缓存run形态异常'
    return xml[:gt + 1] + str(start) + xml[k:]


def set_part_total(xml, n):
    """「（共N页）」处写死部分总页数（占位'N'或旧值→实测值）；恰1处断言。只对页眉/页脚部件调用。"""
    xml2, cnt = re.subn(r'（共(?:N|\d+)页）', '（共%d页）' % n, xml)
    assert cnt == 1, '（共N页）出现%d处（要求恰1处——同串骨架形态异常）' % cnt
    return xml2


BOOKSEG_RE = re.compile(r'（共(?:N|\d+)页）(?:·本\d+/共\d+本)?')


def set_book_seg(xml, n, m):
    """同串「（共N页）」后写死「·本n/共M本」段（A'旧串无段则补插——保留N已写死值；已有则原位改值）。"""
    if not re.search(r'·本\d+/共\d+本', xml):
        mm = re.search(r'（共(N|\d+)页）', xml)
        assert mm, '（共N页）段定位失败（本n/共M补插）'
        xml2 = xml[:mm.start()] + '（共%s页）·本%d/共%d本' % (mm.group(1), n, m) + xml[mm.end():]
        return xml2
    xml2, cnt = re.subn(r'·本\d+/共\d+本', '·本%d/共%d本' % (n, m), xml, count=1)
    assert cnt == 1, '本n/共M段定位失败'
    return xml2


def est_width_pt(vis):
    """同串可见文本估算宽度（pt）：全角≈9pt、半角≈4.5pt（9pt字号档）。"""
    w = 0.0
    for ch in vis:
        w += 9.0 if ord(ch) > 0x2E80 else 4.5
    return w


HEADER_BUDGET_PT = 500.0   # 页眉可用宽（10206缇≈510pt，留裕量）


def strip_brand(xml):
    """页眉同串超宽时剥「羿郭工作室·」品牌前缀（§7允许项；只剥页眉、页脚不剥）。"""
    xml2, cnt = re.subn(r'羿郭工作室·', '', xml, count=1)
    return xml2, cnt


def check_samestring_skeleton(xml, where):
    """同串骨架形态断言（页眉/页脚通用）：恰两组复杂域（STYLEREF＋PAGE）、无fldSimple/NUMPAGES、
    （共N页）在位、jc=left单段、9pt。"""
    assert xml.count('fldCharType="begin"') == 2, '%s fldChar begin数≠2' % where
    assert xml.count('fldCharType="end"') == 2, '%s fldChar end数≠2' % where
    assert 'fldSimple' not in xml, '%s 出现fldSimple（禁用）' % where
    assert 'NUMPAGES' not in xml, '%s 出现NUMPAGES（禁用）' % where
    assert xml.count(INSTR_STYLEREF) == 1, '%s STYLEREF节名锚域缺失' % where
    assert len(INSTR_PAGE_RE.findall(xml)) == 1, '%s PAGE域缺失' % where
    assert len(BOOKSEG_RE.findall(xml)) == 1, '%s（共N页）段缺失' % where
    assert len(re.findall(r'<w:jc w:val="left"/>', xml)) == 1, '%s jc=left单段异常' % where
    szs = set(re.findall(r'<w:sz w:val="(\d+)"/>', xml))
    assert szs == {'18'}, '%s 同串run字号≠18半点: %r' % (where, szs)
    return True


def stamp_document(doc, start, footer_twips=FOOTER_TWIPS):
    """document.xml（A''多sectPr）：首个（头部）sectPr 写 pgNumType start、后续节清除 pgNumType
    （页码连续继承）；pgMar footer 统一850；剔除 titlePg。"""
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
        s = re.sub(r'(<w:pgMar[^>]*?)w:footer="\d+"', r'\1w:footer="%d"' % footer_twips, s)
        if 'w:footer=' not in s and '<w:pgMar ' in s:
            s = re.sub(r'(<w:pgMar )', r'\1w:footer="%d" ' % footer_twips, s, count=1)
        return s

    parts = re.split(r'(<w:sectPr.*?</w:sectPr>)', d, flags=re.S)
    n_sect = 0
    for i in range(1, len(parts), 2):
        if n_sect == 0:
            parts[i] = fix_sect(parts[i])      # 首个（头部）节：写 start
        else:
            parts[i] = re.sub(r'<w:pgNumType[^>]*/>', '', parts[i])   # 后续节：清除（连续继承）
            parts[i] = re.sub(r'(<w:pgMar[^>]*?)w:footer="\d+"', '\\1w:footer="%d"' % footer_twips, parts[i])
        n_sect += 1
    d = ''.join(parts)
    starts = re.findall(r'<w:pgNumType w:start="(\d+)"/>', d)
    assert n_sect >= 1 and len(starts) == 1 and int(starts[0]) == start,         'pgNumType写入失败（期望唯一头部节start=%d）: %r' % (start, starts)
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


def locate_hf(names, path):
    """定位页眉/页脚部件（各恰1个——§7一个页脚定义/同串单页眉）；多定义报错人工拆除。"""
    headers = [n for n in names if re.fullmatch(r'word/header\d+\.xml', n)]
    footers = [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
    assert len(headers) == 1, ('%s 页眉部件%d个（要求恰1个）——多定义件先拆除' % (os.path.basename(path), len(headers)))
    assert len(footers) == 1, ('%s 页脚部件%d个（要求恰1个——§7全文唯一页脚定义）——先拆除首页不同/'
                               '奇偶页脚等多余页脚再盖章' % (os.path.basename(path), len(footers)))
    return headers[0], footers[0]


def preflight(path):
    """盖章前置检查：同串骨架在位（先挂载后盖章）；不代行挂载。"""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        hname, fname = locate_hf(names, path)
        for nm, where in ((hname, '页眉'), (fname, '页脚')):
            xml = z.read(nm).decode('utf-8')
            try:
                check_samestring_skeleton(xml, '%s%s' % (os.path.basename(path), where))
            except AssertionError as e:
                raise AssertionError('同串骨架未在位（%s）——先运行 工具/页眉面包屑挂载.py 挂载：\n  %s'
                                     % (path, e))


def rewrite(path, start, part_total, tag, book_n, total_m, footer_twips=FOOTER_TWIPS):
    """逐件落盘：document.xml（头部节start/footer850/去titlePg）＋页眉页脚两部件同串盖章
    （X域缓存双写start＋N写死＋本n/共M段写死＋页眉超宽剥品牌前缀）＋settings。幂等。"""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        blob = {n: z.read(n) for n in names}
    hname, fname = locate_hf(names, path)

    doc = blob['word/document.xml'].decode('utf-8')
    doc2, n_sect, n_title = stamp_document(doc, start, footer_twips)
    stamped = {}
    stripped_brand = 0
    for nm in (hname, fname):
        xml = blob[nm].decode('utf-8')
        check_samestring_skeleton(xml, '%s %s' % (os.path.basename(path), nm))
        xml = set_part_total(xml, part_total)          # N写死（两部件同步）
        xml = set_book_seg(xml, book_n, total_m)       # 本n/共M段写死（A''）
        xml = flush_page_cache(xml, start)             # X域缓存刷写（两处PAGE域同步＝start实测值）
        # 串宽预检：页眉超预算剥品牌前缀（页脚版心同宽亦剥——页脚与页眉同宽预算）
        vis_probe = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml))
        if est_width_pt(vis_probe) > HEADER_BUDGET_PT and '羿郭工作室·' in vis_probe:
            xml, cnt = strip_brand(xml)
            stripped_brand += cnt
        stamped[nm] = xml
        # 盖章后域形态断言：恰两组复杂域（STYLEREF＋PAGE）、无NUMPAGES、无fldSimple
        assert xml.count('fldCharType="begin"') == 2 and xml.count('fldCharType="end"') == 2, nm + ' 域组数异常'
        assert 'NUMPAGES' not in xml and 'fldSimple' not in xml, nm + ' 域形态残留'
        assert ('（共%d页）' % part_total) in xml, nm + ' N写死缺失'
        vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml))
        m = re.fullmatch(r'(.+)（共(\d+)页）·本(\d+)/共(\d+)本　(.+)　第(\d+)页', vis)
        assert m and int(m.group(2)) == part_total and int(m.group(6)) == start and int(m.group(3)) == book_n and int(m.group(4)) == total_m and m.group(1) and m.group(5), \
            '%s 盖章后可见串形态异常: %r' % (nm, vis)
        assert m.group(1).endswith(tag.split('·')[-1]), \
            '%s 同串前段尾段%r与件型token %r 不符' % (nm, m.group(1)[-8:], tag)
    st2, added = ensure_update_fields(blob['word/settings.xml'].decode('utf-8'))

    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for nm in names:                    # 保持成员原序，幂等
            if nm == 'word/document.xml':
                zo.writestr(nm, doc2)
            elif nm in stamped:
                zo.writestr(nm, stamped[nm])
            elif nm == 'word/settings.xml':
                zo.writestr(nm, st2)
            else:
                zo.writestr(nm, blob[nm])
    os.replace(tmp, path)

    # 落盘后回读复核（同步盘干扰防：读回断言）
    with zipfile.ZipFile(path) as z:
        for nm in (hname, fname):
            f = z.read(nm).decode('utf-8')
            vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', f))
            m = re.fullmatch(r'(.+)（共(\d+)页）·本(\d+)/共(\d+)本　(.+)　第(\d+)页', vis)
            assert m and int(m.group(2)) == part_total and int(m.group(3)) == book_n and int(m.group(4)) == total_m and int(m.group(6)) == start, \
                '回读同串不符 %s: %r' % (nm, vis)
            assert locate_page_cache(f) == str(start), '%s 回读PAGE域缓存≠start' % nm
        d = z.read('word/document.xml').decode('utf-8')
        s = z.read('word/settings.xml').decode('utf-8')
    assert ('<w:pgNumType w:start="%d"/>' % start) in d, '回读start不符'
    assert 'w:footer="%d"' % footer_twips in d, '回读页脚距边不符'
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
    fmcfg = cfg.get('footer_twips')
    footer_map = {os.path.basename(str(k)).strip(): int(v) for k, v in fmcfg.items()} if fmcfg else {}
    bm = cfg.get('book_map')           # 可选：{部分序(int)→本序(int)}——二次拆分/聚合时覆盖默认（部分序=本序、M=部分总数）
    book_map = {int(k): int(v) for k, v in bm.items()} if bm else None
    return book, parts, skips, book_map, footer_map


def apply_stamps(parts, pages, book_map=None, verbose=True, footer_map=None):
    """按当前实测页数逐件盖章（部分内级联；本n默认＝部分序、M默认＝部分总数——book_map可覆盖）。"""
    rec_rows, it, total = [], iter(pages), 0
    total_m = len(parts) if not book_map else max(book_map.values())
    for pi, (tag, files) in enumerate(parts, 1):
        pg = [next(it) for _ in files]
        pn = sum(pg)
        start = 1
        book_n = (book_map or {}).get(pi, pi)
        for f, p in zip(files, pg):
            ft = (footer_map or {}).get(os.path.basename(f), FOOTER_TWIPS)
            n_sect, n_title = rewrite(f, start, pn, tag, book_n, total_m, ft)
            if verbose:
                print('  [P%d·本%d/共%d] %s | %d页 | start=%d | %s（共%d页） | sectPr=%d titlePg剔%d'
                      % (pi, book_n, total_m, os.path.basename(f)[:44], p, start, tag, pn, n_sect, n_title) + (' 页脚%d缇' % ft if ft != FOOTER_TWIPS else ''))
            rec_rows.append('| P%d | 本%d | %s | %d | %d | %s | %d |'
                            % (pi, book_n, os.path.basename(f), p, start, tag, pn))
            start += p
            total += p
    return rec_rows, total


def main():
    ap = argparse.ArgumentParser(description='部分独立页码盖章（§7 N8＋A\'改制轮同串口径：每部分独立从1连续、'
                                             '同部分后件start=前件累计+1；同串「前段（共N页）　节号节名　第X页」'
                                             '——X域缓存页眉页脚双写、N=部分总页数写死；先挂载后盖章）')
    ap.add_argument('--parts', required=True, help='parts.json 配置（book/parts[{tag,files}]/skip_files）')
    ap.add_argument('--record', help='盖章记录md落盘路径（供册目录页/装订单/节页码定位.py 同源引用）')
    args = ap.parse_args()

    book, parts, skips, book_map, footer_map = load_parts(args.parts)
    for _, files in parts:
        for f in files:
            if not os.path.isfile(f):
                print('错误：文件不存在：%s' % f, file=sys.stderr)
                sys.exit(2)
    for f in skips:
        print('  跳过配页件（不属任何部分、不计数、不盖章）: %s' % os.path.basename(f))

    flat = [f for _, files in parts for f in files]
    for f in flat:                        # 前置：同串骨架在位（整批先查后盖，防半批盖章）
        try:
            preflight(f)
        except AssertionError as e:
            print('错误：%s' % e, file=sys.stderr)
            sys.exit(2)
    # 不动点迭代：实测→盖章→复测至页数与所盖数字一致（页眉页脚版式变化可使临界件repaginate，见文件头注）
    pages = measure(flat)
    print('== 部分独立页码盖章（同串版）：%s（%d个部分／%d件）==' % (book, len(parts), len(flat)))
    converged = False
    for rnd in range(1, 6):
        rec_rows, total = apply_stamps(parts, pages, book_map, footer_map=footer_map)
        pages2 = measure(flat)
        if pages2 == pages:
            print('  收敛：第%d轮盖章后复测页数与所盖数字一致（合计%d页）' % (rnd, total))
            converged = True
            break
        print('  复测页数有变（%s→%s），以新页数重盖（第%d轮）'
              % (pages, pages2, rnd + 1))
        pages = pages2
    assert converged, '盖章5轮未收敛（页数仍在漂移）——请人工检查 %s' % flat

    rec = ['# 部分独立页码盖章记录（同串版） — %s' % book,
           '',
           '口径：公共规则§7部分独立页码制（N8）＋A\'改制轮同串口径（2026-09-01）——每部分独立从1连续；',
           '同部分后件start＝该件之前同部分各件累计页数＋1；N＝部分总页数（COM实测，盖章后复测收敛值）；',
           '同串「羿郭工作室·册名 第X章 章名·件型（共N页）　节号节名（STYLEREF节名锚域）　第X页」＝',
           '页眉页脚同内容；X域缓存＝页眉页脚两处PAGE域同步刷写start实测值；N为写死实测值（禁NUMPAGES）。',
           '本记录不含时间戳，「先内容后页码」先后核对以本文件mtime为准',
           '（工具/册级连续页码.py --parts 生成；节页码定位.py按件名匹配start）。',
           '',
           '| 部分 | 本 | 件 | 页数 | start | 件标识 | N（部分总页数） |',
           '|---|---|---|---|---|---|---|'] + rec_rows + [
        '', '恒等式：每部分首件start=1；同部分后件start＝前件start+页数；N＝部分内各件页数之和（COM实测）；'
            '全册合计%d页＝各件页数和（配页件不计页）。' % total]
    if args.record:
        open(args.record, 'w', encoding='utf-8').write('\n'.join(rec) + '\n')
        print('盖章记录 -> %s' % args.record)


if __name__ == '__main__':
    main()
