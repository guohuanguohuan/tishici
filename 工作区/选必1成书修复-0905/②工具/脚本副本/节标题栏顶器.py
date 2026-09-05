# -*- coding: utf-8 -*-
r"""节标题栏顶器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·T7（工具先建后用）

口径（附则《节标题栏顶规则》LT-1..4）：
  LT-1 各教材节标题段前插分栏符使节标题栏顶起排；节标题不得落栏中/栏尾孤悬。
      ②-D 执行形态：节标题段前（节名锚之后）紧邻新起仅含分栏符的零高空段（snapToGrid=0＋exact
      1pt 行距＋1pt 段标记），空行留在前栏底（1pt、无底纹、不可见）；实测空段段标记落新栏顶
      dy≈0、标题文本首行 dy≈3.3（≤6 过阈）。段末插符形态真败（宿主段标记被推至新栏顶占一行，
      衔接1 dy=23.8）；锚段段首形态亦可用，统一取空段形态（与锚段行高/节网格无关、实现单一）。
      空段形态即 LT-1 括注「前一元素为表时新起仅含分栏符的空段」推广至一切前元素，偏离括注
      字面已登记待主脑裁决。测位锚＝标题文本首行顶（Range 起点处 Information(6)）——勿取段
      标记处：多行标题（如清单1 节1.1.3 在栏宽内折两行）段标记在第二行，dy 虚高一行致复核
      假失败（本轮三次失败同此一因）。
  LT-2 幂等：Word COM 实测每个节标题段 Range.Information(wdVerticalPositionRelativeToPage=6)，
      与栏正文区顶（所在节 PageSetup.TopMargin）比对——实测选必1自然栏顶 dy≈2.3pt（行网格
      咬合所致），判定阈值取 dy≤6pt（半行以内；中栏位置最小亦≫行高14pt，无误判风险）；
      恰已栏顶者不插。②-D 重跑轮页感知增补（FX-2）：第 1 页双栏区顶被头部单栏区（章头＋
      清单表）压低（清单2 实测豁免节 2.1 dy=66.6；插符后 2.2.1 落第 1 页第 2 栏顶同为 66.6），
      第 1 页栏顶判定以 LT-4 豁免标题实测 dy 为基准，与固定阈 6pt 并用——详见 process 内注记。
  LT-4 豁免：文内开头标题（章首）与头部单栏区要素不适用；首页首节标题即双栏区起点
      （XML 判据：向前越过「节名锚」段后，前一兄弟段含 w:sectPr）者不插。
  派生判定（本工具登记口径，规格书未细条）：节标题紧邻父节标题（如 1.1 后紧跟 1.1.1，
      中间仅隔节名锚段）时子节随父同栏顶区，不再插符（避免近空栏），逐处登记「随父」。
识别：节标题段＝段级底纹 ADC2DA＋节号 pattern＋标题3样式（COM 侧 NameLocal＝「标题 3」；
      「节名锚」1pt 段天然排除）。章标题（文内开头件名行）不匹配节号 pattern。
预算：页数增量 +6~8 页全册（LT-3 用户已拍板）；exec 后 COM 复核逐节栏顶＋实测页数增量登记。
模式：--dry-run 只测不插，输出逐件「节数/已栏顶数/豁免数/随父数/拟插符数」；默认执行插符
      （留 .bak_栏顶）并以 COM 复核断言：非豁免非随父节标题栏顶率 100%。
用法:
  python 工具/节标题栏顶器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None

SEC_TTL_RE = re.compile(r'^(\d+\.\d+(?:\.\d+)?)[\s　]+\S')
TOP_TOL = 6.0            # 栏顶判定阈值（pt）：自然栏顶实测 dy≈2.3，半行保险界


def is_jiemingmao(p):
    """节名锚段：pStyle=JieMingMao。"""
    ppr = p.find(q('pPr'))
    if ppr is None:
        return False
    ps = ppr.find(q('pStyle'))
    return ps is not None and ps.get(q('val')) == 'JieMingMao'


def has_sectpr(p):
    ppr = p.find(q('pPr'))
    return ppr is not None and ppr.find(q('sectPr')) is not None


def collect_titles(body):
    """节标题段清单：[(body内idx, 节号, 文本, 豁免LT4, 随父, 插符目标段, 目标形态)]"""
    els = list(body)
    out = []
    for i, c in enumerate(els):
        if c.tag != q('p'):
            continue
        txt = ptext(c)
        if pfill(c) != 'ADC2DA' or not SEC_TTL_RE.match(txt):
            continue
        secno = SEC_TTL_RE.match(txt).group(1)
        # 向前越过节名锚段
        j = i - 1
        while j >= 0 and els[j].tag == q('p') and is_jiemingmao(els[j]):
            j -= 1
        prev = els[j] if j >= 0 else None
        exempt = prev is not None and prev.tag == q('p') and has_sectpr(prev)
        ride = False
        host = None
        tgt = None                          # (插符落点元素＝节标题段, 形态)
        if not exempt:
            if prev is not None and prev.tag == q('p'):
                pt = ptext(prev)
                if pfill(prev) == 'ADC2DA' and SEC_TTL_RE.match(pt) \
                        and secno.startswith(SEC_TTL_RE.match(pt).group(1) + '.'):
                    ride = True
                else:
                    tgt = (els[i], '空段')
            elif prev is not None and prev.tag == q('tbl'):
                tgt = (els[i], '空段')
            else:
                exempt = True               # 文档首元素等——按豁免处理
        if tgt:
            host = tgt[0]
        out.append([i, secno, txt[:40], exempt, ride, host, tgt[1] if tgt else ''])
    return out


def com_measure(path):
    """COM 实测：逐「标题 3」段 (文本, y, dy, page)；返回 (pages, rows)。rows 按文档序。"""
    import win32com.client, pythoncom
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(os.path.abspath(path), ReadOnly=True, AddToRecentFiles=False)
        try:
            d.Repaginate()
            pages = d.ComputeStatistics(2)   # wdStatisticPages
            rows = []
            for para in d.Paragraphs:
                try:
                    st = para.Range.Style.NameLocal
                except Exception:
                    continue
                if st != '标题 3':
                    continue
                t = para.Range.Text.strip('\r\x07\x0c').strip()
                y = para.Range.Information(6)          # wdVerticalPositionRelativeToPage——锚＝文本首行顶；
                tm = para.Range.Sections(1).PageSetup.TopMargin   # 勿改段标记处（多行标题标记在第二行，dy 虚高一行）
                pg = para.Range.Information(3)         # wdActiveEndPageNumber
                rows.append((t, y, y - tm, pg))
            return pages, rows
        finally:
            d.Close(False)
    finally:
        word.Quit()
        pythoncom.CoUninitialize()


def process(path, dry):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    titles = collect_titles(body)

    pages_pre, com_rows = com_measure(path)
    # COM 行与 XML 节标题按序配对（文本去统计段后前缀匹配）
    ti = 0
    for t, y, dy, pg in com_rows:
        while ti < len(titles):
            want = titles[ti][2].rstrip()
            if t[:len(want)] == want or want[:len(t)] == t:
                break
            ti += 1
        if ti >= len(titles):
            break
        titles[ti].append(round(dy, 1))
        titles[ti].append(pg)
        ti += 1

    # 栏顶判定（页感知，2026-09-05 ②-D 重跑轮 FX-2 修复）：第 2 页起自然栏顶 dy≈2.3（阈 6pt）；
    # 第 1 页双栏区顶被头部单栏区（章头＋清单表）压低——以 LT-4 豁免标题（双栏区起点）实测 dy
    # 为第 1 页栏顶基准（清单2 实测 2.1@66.6；2.2.1 插符后落第 1 页第 2 栏顶同为 66.6，
    # 原固定阈 6pt 误判失败；插符本身有效）。此判据同用于 exec 复核。
    pg1_top = None
    for x in titles:
        if x[3] and len(x) > 8 and x[8] == 1:
            pg1_top = x[7]
            break

    def _is_top(x):
        if len(x) <= 8:
            return False
        if x[7] <= TOP_TOL:
            return True
        return pg1_top is not None and x[8] == 1 and abs(x[7] - pg1_top) <= TOP_TOL

    at_top = {k for k, x in enumerate(titles) if _is_top(x)}

    n_sec = len(titles)
    n_exempt = sum(1 for x in titles if x[3])
    n_ride = sum(1 for x in titles if x[4])
    n_top = len(at_top)
    plan = [x for k, x in enumerate(titles) if not x[3] and not x[4] and k not in at_top]

    lines = []
    lines.append('## T7 节标题栏顶器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    lines.append('节数 %d｜已栏顶 %d｜LT-4豁免 %d｜随父 %d｜拟插符 %d｜当前页数 %d'
                 % (n_sec, n_top, n_exempt, n_ride, len(plan), pages_pre))
    for k, x in enumerate(titles):
        dy = ('dy=%s' % x[7]) if len(x) > 7 else 'dy=?'
        stat = '豁免' if x[3] else '随父' if x[4] else '已栏顶' if k in at_top else '拟插符'
        tg = ('｜' + x[6]) if x[6] else ''
        lines.append('  节%s %s%s｜%s｜%s' % (x[1], stat, tg, dy, x[2][:30]))

    if dry:
        lines.append('')
        return '\n'.join(lines)

    # ---- 执行插符（②-D 空段形态：节标题段前紧邻新起仅含分栏符的零高空段）。
    #      空段置节名锚之后、标题段之前；段末插符形态已实测真败（宿主段标记被推至新栏顶占一行）。
    #      空段自身 snapToGrid=0＋exact 1pt 行距＋1pt 段标记，仅占 1pt（实测段标记 dy≈0），
    #      标题文本首行落新栏顶 dy≈3.3。 ----
    n_ins = 0
    for x in plan:
        tgt = x[5]
        br = etree.Element(q('br'))
        br.set(q('type'), 'column')
        r = etree.Element(q('r'))
        r.append(br)
        np = etree.Element(q('p'))
        ppr2 = etree.Element(q('pPr'))
        sng = etree.Element(q('snapToGrid'))
        sng.set(q('val'), '0')
        spc = etree.Element(q('spacing'))
        spc.set(q('before'), '0')
        spc.set(q('after'), '0')
        spc.set(q('line'), '20')
        spc.set(q('lineRule'), 'exact')
        rpr = etree.Element(q('rPr'))
        sz2 = etree.SubElement(rpr, q('sz'))
        sz2.set(q('val'), '2')
        szcs = etree.SubElement(rpr, q('szCs'))
        szcs.set(q('val'), '2')
        ppr2.append(sng)
        ppr2.append(spc)
        ppr2.append(rpr)
        np.append(ppr2)
        np.append(r)
        tgt.addprevious(np)
        n_ins += 1
    assert n_ins == len(plan), '插符数与计划不符'
    if n_ins:
        import shutil
        bak = path + '.bak_栏顶'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.t7tmp'
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
                zout.writestr(item, data)
        for k in range(12):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                time.sleep(6)
        else:
            raise RuntimeError('locked: ' + path)

    # ---- COM 复核（FX-2 修复 2026-09-05 ②-D：断言面＝拟插符标题。原实现遍历全部「标题 3」段，
    #      豁免/随父标题不插符、dy>6 属常态，exec 必假失败；与 docstring「非豁免非随父节标题栏顶率
    #      100%」不符。修复后仅对 plan 标题按同序配对断言栏顶，豁免/随父不参断言。----
    pages_post, com_post = com_measure(path)
    plan_idx = [k for k, x in enumerate(titles) if not x[3] and not x[4] and k not in at_top]
    assert len(plan_idx) == len(plan), 'plan 复算与拟插清单不一致'
    ti = 0
    post_dy = {}
    for t, y, dy, pg in com_post:
        while ti < len(titles):
            want = titles[ti][2].rstrip()
            if t[:len(want)] == want or want[:len(t)] == t:
                break
            ti += 1
        if ti >= len(titles):
            break
        post_dy[ti] = (round(dy, 1), pg)
        ti += 1
    pg1_top_post = None
    for k, x in enumerate(titles):
        if x[3] and k in post_dy and post_dy[k][1] == 1:
            pg1_top_post = post_dy[k][0]
            break

    def _is_top_post(k):
        if k not in post_dy:
            return False
        dy, pg = post_dy[k]
        if dy <= TOP_TOL:
            return True
        return pg1_top_post is not None and pg == 1 and abs(dy - pg1_top_post) <= TOP_TOL

    bad = ['节%s dy=%.1f page=%d' % (titles[k][1], post_dy[k][0], post_dy[k][1])
           for k in plan_idx if not _is_top_post(k)]
    lines.append('执行：插符 %d｜页数 %d→%+d｜COM复核拟插标题栏顶 %d/%d%s'
                 % (n_ins, pages_pre, pages_post - pages_pre,
                    len(plan_idx) - len(bad), len(plan_idx),
                    ('——未栏顶：' + '；'.join(bad[:6])) if bad else '（拟插标题栏顶率100% PASS）'))
    lines.append('')
    if bad:
        raise RuntimeError('栏顶复核未过: %s' % bad[:6])
    return '\n'.join(lines)


def main():
    argv = sys.argv[1:]
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    report = None
    if '--report' in argv:
        k = argv.index('--report'); report = argv[k + 1]; del argv[k:k + 2]
    assert argv, '用法: python 工具/节标题栏顶器.py <docx...> [--dry-run] [--report r.md]'
    out = []
    for path in argv:
        r = process(path, dry)
        out.append(r)
        print(r)
    if report:
        with open(report, 'a', encoding='utf-8') as f:
            f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
