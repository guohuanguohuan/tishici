# -*- coding: utf-8 -*-
r"""节页码定位（公共规则§11册目录页件条款明文要求的节级页码生成工具；2026-08-27 按§5回扫纪律先建后用收编入工具文件夹）
功能：定位讲练件内节标题所在页，输出该节的部分内页码
  （公共规则§7部分独立页码制·2026-08-31 N8：部分内页码＝件内页＋该件start−1；
  2026-08-27~30旧「全册连续页码」口径废止；start＝该件 sectPr <w:pgNumType w:start> 值，
  由 工具/册级连续页码.py 盖章落盘——从盖章记录（--record）或批量配置读）。
签名兼容（2026-08-31 N11）：节标题行已与节级统计行合并为一行——「2.4 曲线与方程（第101—119题）　本节19题：
  简单1｜中档12｜难6」，行尾带统计段照常命中（统计段形态＝全角空格＋「本节N题…」）。
层级制节标题签名（2026-09-01 A'改制轮·工具债③·T3）：题号层级制后节标题行区间括注改题量括注
  （规格书§1口径C授权差异②）——「2.4 曲线与方程　本节19题：简单1｜中档12｜难6」（无「（第X—Y题）」）；
  本工具双签名兼容：区间括注（旧式）与纯统计段（层级制新式）任一在位即命中，题型标题（无统计段）不误命中。
批量0命中逐件独立报告（2026-09-01 工具债③·T3 强化）：批量模式任一件0命中不再「告警后丢弃该件」，
  而是0命中件照常进输出（件级行＋空节表＋「0命中」注记行），退出码0——衔接件/知识清单无节标题不属错误；
  --strict 恢复防呆口径（任一件0命中即非零退出，用于纯讲练件配置）。

用法（单件模式）：
  python 工具/节页码定位.py <docx路径> <start> [--name 件名] [--json]
    —— start＝该件首页的部分内页码，即 sectPr pgNumType start（≥1）。
用法（批量模式）：
  python 工具/节页码定位.py @<配置文件> [--record <盖章记录.md>] [--json] [--strict]
    —— 配置文件按扩展名识别：
       .json＝[{"path":..,"start":..,"name":..,"tag":..}, ...]（或 [[path,start,name], ...]）；
              也直接接受 工具/册级连续页码.py 的 parts.json（{"book":..,"parts":[{"tag":..,"files":[..]}]}，
              start 自动从 --record 记录按件名补齐）；
       .tsv/.txt＝每行「路径<TAB>start<TAB>件名」（start 可留空或写 - ，由 --record 补；
              #注释行与空行跳过）。
    —— --record＝册级连续页码.py --record 落盘的盖章记录md（按件名basename匹配 start/件标识/N；
       配置内未给 start 的件必须能从记录补齐，否则该件报错跳过）。

输出：TSV行「件名\t节号\t节标题全文\t件内页\t部分内页码」打印到stdout（UTF-8）；批量模式先附件级行
  「件名\t件级起始start\t件标识」＋0命中件的「件名\t!0命中\t—\t—\t—」注记行；--json 改输出JSON
  （part_page＝部分内页码＝start+件内页−1；0命中件 sections=[] 且 zero_hit=true）。
  件内页码1起算（物理页，Information(3) 不受 pgNumType 调整影响）。

定位规则：Word COM（自建不可见实例，用完Quit，ReadOnly开卷、绝不保存——只读工具，不修改任何docx）遍历段落，
  节标题正则＝节号（N.N / N.N.N）＋空格＋标题＋【旧式（第X[—–-]Y题）区间括注 或 新式「　本节N题…」统计段】
  （区间破折号兼容全角—/半角连字符；两形态任一在位即命中、都缺即不认——防题型标题误命中）；
  同一节号只取首次出现（防重复）；跳过表格内段落（wdWithInTable 排除章首导航表的节号行，只认正文结构标题段）。

与盖章流水线的接驳关系（§11册目录页件条款）：节级页码与部分内页码盖章串成同一条流水线——
  任何成品件内容发生改动 → 重盖部分内页码（工具/册级连续页码.py，先内容后页码）→ 强制重跑本工具重测
  并重写册目录页页码列，禁止任何形式的手工维护页码列。单件模式0命中时打印前20个标题样式段名辅助诊断
  并以非零码退出（单件模式语义＝确有节可测，0命中即异常）。
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

# 节标题正则（双签名）：节号 N.N/N.N.N + 标题 + 【（第X—Y题）区间括注｜纯统计段】任一在位；
# 破折号兼容全角—、en dash –、半角-；层级制新式＝无区间括注、统计段「　本节N题：…」必在
SEC_RE = re.compile(r'^(\d+\.\d+(?:\.\d+)?)[\s\u3000]+(.+?)'
                    r'(?:（第(\d+)[—–\-](\d+)题）)?(?:[\s\u3000]+本节\d+题[：:].*)?[\s\u3000]*$')
STATS_RE = re.compile(r'[\s\u3000]本节\d+题')   # 统计段在位判定（与区间括注二选一）
WD_ACTIVE_END_PAGE = 3   # wdActiveEndPageNumber：物理页码（自件首页1起算，忽略pgNumType调整）
WD_WITH_IN_TABLE = 12    # wdWithInTable
REC_ROW = re.compile(r'^\|\s*(P\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*$')


def scan_doc(word, path):
    """返回 (hits, page_total)：hits＝[(节号, 节标题全文, 件内页), ...] 按文中出现顺序，同节号只取表外首次出现。
    双签名：区间括注（旧式）或统计段（层级制新式）任一在位才认节标题——防题型标题误命中。"""
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
            if not (m.group(3) or STATS_RE.search(txt)):   # 双签名都在缺 → 不是节标题（题型标题防误命中）
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


def load_record(rec_path):
    """盖章记录md → {basename: (start, tag, N)}（工具/册级连续页码.py --record 表格行）。"""
    if not rec_path:
        return {}
    if not os.path.isfile(rec_path):
        print(f'错误：盖章记录不存在：{rec_path}', file=sys.stderr)
        sys.exit(2)
    table = {}
    with open(rec_path, encoding='utf-8-sig') as f:
        for ln in f:
            m = REC_ROW.match(ln.rstrip('\n'))
            if not m:
                continue
            _part, fname, _pages, start, tag, n = m.groups()
            table.setdefault(os.path.basename(fname.strip()), (int(start), tag.strip(), int(n)))
    if not table:
        print(f'错误：盖章记录内未解析到任何件行（{rec_path}）——应为册级连续页码.py记录表格', file=sys.stderr)
        sys.exit(2)
    return table


def load_batch(cfg_path, record):
    """批量配置→[(name, start|None, abs_path, tag|None)]。start None＝待record补齐。
    JSON：对象数组/三元组数组/parts.json（册级连续页码.py配置直传）；TSV：路径<TAB>start<TAB>件名。
    相对路径相对配置文件所在目录解析（避免Word按自身CWD误解析）。"""
    base = os.path.dirname(os.path.abspath(cfg_path))

    def norm(p):
        return p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))

    ext = os.path.splitext(cfg_path)[1].lower()
    if ext == '.json':
        with open(cfg_path, encoding='utf-8-sig') as f:
            data = json.load(f)
        items = []
        if isinstance(data, dict):                      # parts.json 直传（册级连续页码.py配置）
            for it in data.get('parts', []):
                for p in it.get('files', []):
                    items.append({'path': norm(p), 'start': None, 'name': None, 'tag': it.get('tag')})
        else:
            for it in data:
                if isinstance(it, dict):
                    items.append({'path': norm(it['path']),
                                  'start': int(it['start']) if it.get('start') is not None else None,
                                  'name': it.get('name'), 'tag': it.get('tag')})
                else:
                    path, start = norm(it[0]), (int(it[1]) if len(it) > 1 and it[1] not in (None, '', '-') else None)
                    name = it[2] if len(it) > 2 else None
                    items.append({'path': path, 'start': start, 'name': name, 'tag': None})
        out = []
        for it in items:
            start, tag = it['start'], it.get('tag')
            if start is None:
                hit = record.get(os.path.basename(it['path']))
                if hit is None:
                    print(f'错误：{os.path.basename(it["path"])} 无start且盖章记录未命中（须先跑 册级连续页码.py）',
                          file=sys.stderr)
                    sys.exit(2)
                start, tag, _n = hit
            out.append((it.get('name') or os.path.splitext(os.path.basename(it['path']))[0], start, it['path'], tag))
        return out
    items = []
    with open(cfg_path, encoding='utf-8-sig') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            cols = ln.split('\t')
            path = norm(cols[0])
            start = int(cols[1]) if len(cols) > 1 and cols[1].strip() not in ('', '-') else None
            tag = None
            if start is None:
                hit = record.get(os.path.basename(path))
                if hit is None:
                    print(f'错误：{os.path.basename(path)} 无start且盖章记录未命中（须先跑 册级连续页码.py）',
                          file=sys.stderr)
                    sys.exit(2)
                start, tag, _n = hit
            name = cols[2].strip() if len(cols) > 2 and cols[2].strip() else os.path.splitext(os.path.basename(path))[0]
            items.append((name, start, path, tag))
    return items


def main():
    ap = argparse.ArgumentParser(description='讲练件节标题部分内页码定位（只读；双签名兼容：旧式「N.N 标题'
                                             '（第X—Y题）」与层级制「N.N 标题　本节N题：…」；'
                                             '批量0命中逐件独立报告不阻断）')
    ap.add_argument('docx', help='docx路径；或 @配置文件（.json/.tsv）批量模式')
    ap.add_argument('start', nargs='?', type=int,
                    help='单件模式：该件首页的部分内页码（sectPr pgNumType start值）；批量模式省略')
    ap.add_argument('--name', help='单件模式件名（默认文件名去扩展名）')
    ap.add_argument('--record', help='盖章记录md（册级连续页码.py --record 产物）：批量配置缺start的件按件名补齐')
    ap.add_argument('--json', action='store_true', help='输出JSON而非TSV')
    ap.add_argument('--strict', action='store_true', help='批量模式恢复旧口径：任一件0命中即非零退出（纯讲练配置防呆）')
    args = ap.parse_args()

    record = load_record(args.record)

    if args.docx.startswith('@'):
        if args.start is not None:
            print('错误：批量模式不接start位置参数', file=sys.stderr)
            sys.exit(2)
        cfg = os.path.abspath(args.docx[1:])
        if not os.path.isfile(cfg):
            print(f'错误：配置文件不存在：{cfg}', file=sys.stderr)
            sys.exit(2)
        try:
            items = load_batch(cfg, record)
        except Exception as e:
            print(f'错误：配置文件解析失败（{cfg}）：{e}', file=sys.stderr)
            sys.exit(2)
        batch = True
    else:
        if args.start is None or args.start < 1:
            print('错误：单件模式需 docx路径 + start（≥1，＝该件首页部分内页码/sectPr pgNumType start）',
                  file=sys.stderr)
            sys.exit(2)
        path = os.path.abspath(args.docx)
        name = args.name or os.path.splitext(os.path.basename(path))[0]
        items = [(name, args.start, path, None)]
        batch = False

    for _, _, p, _ in items:
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
        results = []   # [(name, start, path, tag, hits, pages)]
        fatal = False
        for name, start, path, tag in items:
            try:
                hits, pages = scan_doc(word, path)
            except pythoncom.com_error as e:
                print(f'错误：Word COM 开卷/遍历失败（{path}）：{e.excepinfo[2] if e.excepinfo else e}',
                      file=sys.stderr)
                fatal = True
                continue
            if not hits and not batch:
                # 单件模式：确有节可测，0命中即异常——诊断后非零退出
                print(f'错误：{os.path.basename(path)} 节标题0命中（正则：{SEC_RE.pattern}）——'
                      f'请核对件型/节标题格式（应为「N.N 标题（第X—Y题）」或层级制「N.N 标题　本节N题：…」）',
                      file=sys.stderr)
                try:
                    for sty, head in diagnose_styles(word, path):
                        print(f'  [诊断] 样式「{sty}」：{head}', file=sys.stderr)
                except Exception as e:
                    print(f'  [诊断] 样式扫描失败：{e}', file=sys.stderr)
                fatal = True
                continue
            if not hits and batch:
                # 批量模式0命中：逐件独立报告（不丢弃、不阻断）——衔接件/知识清单无节标题不属错误
                print(f'注记：{os.path.basename(path)} 节标题0命中——已按独立空结果报告（衔接件/知识清单'
                      f'无节级标题不属错误；若该件确为讲练件请核对节标题格式）', file=sys.stderr)
                results.append((name, start, path, tag, [], pages))
                if args.strict:
                    fatal = True
                continue
            results.append((name, start, path, tag, hits, pages))
        if fatal:
            sys.exit(1)
        # 输出（0命中件照常逐件报告：件级行＋「!0命中」注记行）
        if args.json:
            payload = {'files': [
                {'name': n, 'start': s, 'tag': t, 'path': p, 'in_file_pages': pg,
                 'zero_hit': not h,
                 'sections': [{'no': no, 'title': tt, 'in_page': ip, 'part_page': s + ip - 1}
                              for no, tt, ip in h]}
                for n, s, p, t, h, pg in results]}
            print(json.dumps(payload, ensure_ascii=False, indent=1))
        else:
            if batch:
                print('# 件级（件名\t件级起始start\t件标识）')
                for n, s, _, t, h, _ in results:
                    print(f'{n}\t{s}\t{t or ""}')
                print('# 节级（件名\t节号\t节标题全文\t件内页\t部分内页码）')
                for n, _s, _p, _t, h, _pg in results:
                    if not h:
                        print(f'{n}\t!0命中\t—\t—\t—')
            for n, s, _, _, h, _ in results:
                for no, tt, ip in h:
                    print(f'{n}\t{no}\t{tt}\t{ip}\t{s + ip - 1}')
    finally:
        word.Quit()
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    main()
