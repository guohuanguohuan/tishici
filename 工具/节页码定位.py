# -*- coding: utf-8 -*-
r"""节页码定位（公共规则§11册目录页件条款明文要求的节级页码生成工具；2026-08-27 按§5回扫纪律先建后用收编入工具文件夹）
功能：定位讲练件内节标题「N.N（第X—Y题）」/「N.N.N（第X—Y题）」所在页，输出该节的全册连续页码（§7两级页码制口径）。

用法（单件模式）：
  python 工具/节页码定位.py <docx路径> <起始偏移N> [--name 件名] [--json]
    —— 起始偏移N＝该件首页的全册页码，即 sectPr <w:pgNumType w:start="N"/> 的值（由 工具/册级连续页码.py 盖章落盘）。
用法（批量模式）：
  python 工具/节页码定位.py @<配置文件> [--json]
    —— 配置文件按扩展名识别：.json＝[{"path":..,"start":..,"name":..}, ...]（或 [[path,start,name], ...]）；
       .tsv/.txt＝每行「路径<TAB>start<TAB>件名」（件名可省，#注释行与空行跳过）。一次输出全册节级页码表。
       配置内相对路径一律相对「配置文件所在目录」解析（开卷前统一转绝对路径）。

输出：TSV行「件名\t节号\t节标题全文\t件内页\t全册页码」打印到stdout（UTF-8）；批量模式先附件级行「件名\t件级起始\t起始偏移」；
  --json 改输出JSON。全册页码＝起始偏移＋件内页−1；件内页码1起算（物理页，Information(3) 不受 pgNumType 调整影响）。

定位规则：Word COM（自建不可见实例，用完Quit，ReadOnly开卷、绝不保存——只读工具，不修改任何docx）遍历段落，
  正则 ^\d+\.\d+(\.\d+)?[空格]+标题（第X[—–-]Y题）$（区间破折号兼容全角—/半角连字符）；同一节号只取首次出现（防重复）；
  跳过表格内段落（Range.Information(wdWithInTable=12) 排除章首导航表的节号行，只认正文结构标题段）。

与盖章流水线的接驳关系（§11册目录页件条款）：节级页码与件级两级页码盖章串成同一条流水线——
  任何成品件内容发生改动 → 重盖两级页码（工具/册级连续页码.py，先内容后页码）→ 强制重跑本工具重测并重写册目录页页码列，
  禁止任何形式的手工维护页码列。0命中时打印前20个标题样式段名辅助诊断并以非零码退出。
"""
import argparse, json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import win32com.client
    import pythoncom
except ImportError:
    print('错误：需要 pywin32（import win32com.client/pythoncom 失败）', file=sys.stderr)
    sys.exit(3)

# 节标题正则：N.N / N.N.N + 标题 + （第X—Y题）收尾；破折号兼容全角—、en dash –、半角-
SEC_RE = re.compile(r'^(\d+\.\d+(?:\.\d+)?)[\s\u3000]+(.+?)（第(\d+)[—–\-](\d+)题）[\s\u3000]*$')
WD_ACTIVE_END_PAGE = 3   # wdActiveEndPageNumber：物理页码（自件首页1起算，忽略pgNumType调整）
WD_WITH_IN_TABLE = 12    # wdWithInTable


def scan_doc(word, path):
    """返回 (hits, page_total)：hits＝[(节号, 节标题全文, 件内页), ...] 按文中出现顺序，同节号只取表外首次出现。"""
    doc = word.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False)
    try:
        doc.Repaginate()
        hits, seen = [], set()
        for para in doc.Paragraphs:
            rng = para.Range
            txt = rng.Text.rstrip('\r\x07\x0b\x0c \u3000')
            m = SEC_RE.match(txt)
            if not m:
                continue
            if rng.Information(WD_WITH_IN_TABLE):   # 表格内段落（章首导航表节号行）跳过
                continue
            if m.group(1) in seen:                  # 同一节号只取首次出现
                continue
            seen.add(m.group(1))
            hits.append((m.group(1), txt, rng.Information(WD_ACTIVE_END_PAGE)))
        return hits, doc.ComputeStatistics(2)
    finally:
        doc.Close(False)   # 不保存：只读工具


def diagnose_styles(word, path, limit=20):
    """0命中时的诊断：打印前20个标题样式段（样式名＋段首文字）。"""
    doc = word.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False)
    try:
        out = []
        for para in doc.Paragraphs:
            if len(out) >= limit:
                break
            try:
                lvl = para.OutlineLevel
                sty = para.Style.NameLocal
            except Exception:
                continue
            if (isinstance(lvl, int) and lvl < 10) or ('标题' in sty or 'Heading' in sty or 'Title' in sty):
                out.append((sty, para.Range.Text.strip()[:36]))
        return out
    finally:
        doc.Close(False)


def load_batch(cfg_path):
    """批量配置→[(name, start, abs_path)]。JSON：对象数组或三元组数组；TSV：路径<TAB>start<TAB>件名。
    相对路径相对配置文件所在目录解析（避免Word按自身CWD误解析）。"""
    base = os.path.dirname(os.path.abspath(cfg_path))

    def norm(p):
        return p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))

    ext = os.path.splitext(cfg_path)[1].lower()
    if ext == '.json':
        with open(cfg_path, encoding='utf-8-sig') as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get('files', [])
        items = []
        for it in data:
            if isinstance(it, dict):
                items.append((it.get('name') or os.path.splitext(os.path.basename(it['path']))[0],
                              int(it['start']), norm(it['path'])))
            else:
                path, start = it[0], int(it[1])
                name = it[2] if len(it) > 2 else os.path.splitext(os.path.basename(path))[0]
                items.append((name, start, norm(path)))
        return items
    items = []
    with open(cfg_path, encoding='utf-8-sig') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            cols = ln.split('\t')
            path, start = norm(cols[0]), int(cols[1])
            name = cols[2].strip() if len(cols) > 2 and cols[2].strip() else os.path.splitext(os.path.basename(path))[0]
            items.append((name, start, path))
    return items


def main():
    ap = argparse.ArgumentParser(description='讲练件节标题「N.N（第X—Y题）」全册页码定位（只读）')
    ap.add_argument('docx', help='docx路径；或 @配置文件（.json/.tsv）批量模式')
    ap.add_argument('start', nargs='?', type=int, help='起始偏移N＝该件首页的全册页码（sectPr pgNumType start值）；批量模式省略')
    ap.add_argument('--name', help='单件模式件名（默认文件名去扩展名）')
    ap.add_argument('--json', action='store_true', help='输出JSON而非TSV')
    args = ap.parse_args()

    if args.docx.startswith('@'):
        if args.start is not None:
            print('错误：批量模式不接start位置参数', file=sys.stderr)
            sys.exit(2)
        cfg = os.path.abspath(args.docx[1:])
        if not os.path.isfile(cfg):
            print(f'错误：配置文件不存在：{cfg}', file=sys.stderr)
            sys.exit(2)
        try:
            items = load_batch(cfg)
        except Exception as e:
            print(f'错误：配置文件解析失败（{cfg}）：{e}', file=sys.stderr)
            sys.exit(2)
        batch = True
    else:
        if args.start is None or args.start < 1:
            print('错误：单件模式需 docx路径 + 起始偏移N（≥1，＝该件首页全册页码/sectPr pgNumType start）', file=sys.stderr)
            sys.exit(2)
        path = os.path.abspath(args.docx)
        name = args.name or os.path.splitext(os.path.basename(path))[0]
        items = [(name, args.start, path)]
        batch = False

    for _, _, p in items:
        if not os.path.isfile(p):
            print(f'错误：文件不存在：{p}', file=sys.stderr)
            sys.exit(2)

    pythoncom.CoInitialize()
    try:
        word = win32com.client.DispatchEx('Word.Application')
    except Exception as e:
        print(f'错误：Word COM启动失败：{e}', file=sys.stderr)
        pythoncom.CoUninitialize()
        sys.exit(3)
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        results = []   # [(name, start, path, hits, pages)]
        for name, start, path in items:
            try:
                hits, pages = scan_doc(word, path)
            except pythoncom.com_error as e:
                print(f'错误：Word COM 开卷/遍历失败（{path}）：{e.excepinfo[2] if e.excepinfo else e}', file=sys.stderr)
                sys.exit(3)
            results.append((name, start, path, hits, pages))
        # 0命中：诊断后以非零码退出
        empties = [r for r in results if not r[3]]
        if empties:
            for name, start, path, _, _ in empties:
                print(f'错误：{os.path.basename(path)} 节标题0命中（正则：{SEC_RE.pattern}）——'
                      f'请核对件型/节标题格式（应为「N.N 标题（第X—Y题）」）', file=sys.stderr)
                try:
                    for sty, head in diagnose_styles(word, path):
                        print(f'  [诊断] 样式「{sty}」：{head}', file=sys.stderr)
                except Exception as e:
                    print(f'  [诊断] 样式扫描失败：{e}', file=sys.stderr)
            sys.exit(1)
        # 输出
        if args.json:
            payload = {'files': [
                {'name': n, 'start': s, 'path': p, 'in_file_pages': pg,
                 'sections': [{'no': no, 'title': t, 'in_page': ip, 'book_page': s + ip - 1} for no, t, ip in h]}
                for n, s, p, h, pg in results]}
            print(json.dumps(payload, ensure_ascii=False, indent=1))
        else:
            if batch:
                print('# 件级（件名\t件级起始\t起始偏移）')
                for n, s, _, _, _ in results:
                    print(f'{n}\t{s}\t{s}')
                print('# 节级（件名\t节号\t节标题全文\t件内页\t全册页码）')
            for n, s, _, h, _ in results:
                for no, t, ip in h:
                    print(f'{n}\t{no}\t{t}\t{ip}\t{s + ip - 1}')
    finally:
        word.Quit()
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    main()
