# -*- coding: utf-8 -*-
r"""表格规范执行器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·T8（工具先建后用）

口径（附则《表格规范》⑥⑦⑧）：
  ⑦ 跨页/跨栏表：首行开重复标题行（w:trPr/w:tblHeader）＋每行禁跨断撕裂（w:trPr/w:cantSplit）；
     跨断判定走 Word COM 实测——起止页不同（Range.Information(3)）或末行 y 小于首行 y
     （跨栏回顶，Information(6)）即为跨断表；不跨断的表不强求（不挂，免布局扰动）。
  ⑧ 单元格段落全部挂 w:keepLines（禁行内断词，西文单词不拆）——全部表格适用。
  ⑥ 首列禁逐字竖排检测：首列单元格字数≥2 且其显示行数（COM ComputeStatistics(1)）≥字数
     → 逐字竖排命中，登记缺陷清单（不自动改——列宽调整属内容感知重构，交主会话）。
     栏内表列数＞3（列数按首行单元格数；栏内表＝表宽≤栏宽现算）→ 登记重构清单
     （不自动转置，清单交主会话）；双栏区落通栏表（表宽＞栏宽）→ 登记缺陷。
  章首导航表（头部单栏区首表）⑥⑧照查、单列登记口径「导航表」。
断言：跨断表两属性覆盖率 100%（exec 后逐表复核；dry-run 出当前覆盖率与拟挂计数）；
      keepLines 幂等（已挂跳过）；零字符增删（仅 trPr/pPr 属性元素）。
模式：默认执行（留 .bak_表格规）；--dry-run 出分布与清单不落盘。
用法:
  python 工具/表格规范执行器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))

TRPR_ORDER = ['cnfStyle', 'divId', 'gridBefore', 'gridAfter', 'wBefore', 'wAfter', 'cantSplit',
              'trHeight', 'tblHeader', 'tblCellSpacing', 'jc', 'hidden', 'ins', 'del', 'trPrChange']


def trpr_of(tr):
    trpr = tr.find(q('trPr'))
    if trpr is None:
        trpr = etree.Element(q('trPr'))
        tr.insert(0, trpr)
    return trpr


def add_trprop(tr, name):
    trpr = trpr_of(tr)
    if trpr.find(q(name)) is not None:
        return False
    el = etree.Element(q(name))
    idx = TRPR_ORDER.index(name)
    for c in trpr:
        cn = tag(c)
        if cn in TRPR_ORDER and TRPR_ORDER.index(cn) > idx:
            c.addprevious(el)
            break
    else:
        trpr.append(el)
    return True


def add_keeplines(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    if ppr.find(q('keepLines')) is not None:
        return False
    kl = etree.Element(q('keepLines'))
    # pPr 序：keepNext 之后 keepLines
    for c in ppr:
        if tag(c) not in ('pStyle', 'keepNext'):
            c.addprevious(kl)
            break
    else:
        ppr.append(kl)
    return True


def com_tables(path):
    """COM 实测每表：起止页/起止y/列数/表宽/栏宽/所在区分栏数/首列逐字竖排行清单。"""
    import win32com.client, pythoncom
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(os.path.abspath(path), ReadOnly=True, AddToRecentFiles=False)
        try:
            d.Repaginate()
            out = []
            for tbl in d.Tables:
                r0 = tbl.Range.Duplicate
                r0.Collapse(1)               # wdCollapseStart
                r1 = tbl.Range.Duplicate
                r1.Collapse(0)               # wdCollapseEnd
                sp, ep = r0.Information(3), r1.Information(3)
                y0, y1 = r0.Information(6), r1.Information(6)
                try:
                    ncol = tbl.Columns.Count
                except Exception:
                    ncol = tbl.Rows(1).Cells.Count
                sec = r0.Sections(1)
                ps = sec.PageSetup
                ncols_sec = ps.TextColumns.Count
                textw = ps.PageWidth - ps.LeftMargin - ps.RightMargin
                colw = (textw - (ncols_sec - 1) * (ps.TextColumns.Spacing if ncols_sec > 1 else 0)) / ncols_sec
                try:
                    tw = sum(c.Width for c in tbl.Rows(1).Cells)
                except Exception:
                    tw = -1
                vert_rows = []
                for ri in range(1, tbl.Rows.Count + 1):
                    try:
                        cell = tbl.Cell(ri, 1)
                    except Exception:
                        continue
                    ctxt = cell.Range.Text.strip('\r\x07\x0b').strip()
                    c = len(ctxt)
                    if c >= 2:
                        ln = cell.Range.ComputeStatistics(1)   # wdStatisticLines
                        if ln >= c:
                            vert_rows.append((ri, ctxt[:12], ln))
                out.append({'sp': sp, 'ep': ep, 'y0': y0, 'y1': y1, 'ncol': ncol,
                            'tblw': tw, 'colw': colw, 'seccols': ncols_sec, 'vert': vert_rows})
            return out
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
    xml_tbls = list(body.iter(q('tbl')))

    infos = com_tables(path) if xml_tbls else []
    if len(infos) != len(xml_tbls):
        raise RuntimeError('COM 表数 %d ≠ XML 表数 %d（嵌套表？人工核查）' % (len(infos), len(xml_tbls)))

    lines = []
    lines.append('## T8 表格规范执行器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    if not xml_tbls:
        lines.append('无表格。\n')
        return '\n'.join(lines)

    n_cross = n_th_pre = n_cs_full_pre = 0
    n_th_add = n_cs_add = n_kl_add = n_kl_keep = 0
    defects = []
    recon = []
    for k, (tbl, inf) in enumerate(zip(xml_tbls, infos)):
        cross = (inf['sp'] != inf['ep']) or (inf['y1'] < inf['y0'] - 2)
        rows = tbl.findall(q('tr'))
        trs = rows if rows and rows[0].tag == q('tr') else list(tbl.iter(q('tr')))
        has_th = False
        if trs:
            trpr = trs[0].find(q('trPr'))
            has_th = trpr is not None and trpr.find(q('tblHeader')) is not None
        all_cs = all((tr.find(q('trPr')) is not None and tr.find(q('trPr')).find(q('cantSplit')) is not None)
                     for tr in trs) if trs else True
        is_nav = (k == 0 and inf['seccols'] == 1)
        wide = inf['tblw'] > 0 and inf['tblw'] > inf['colw'] + 4
        zone = '导航/单栏区' if inf['seccols'] == 1 else ('通栏落双栏区!' if wide else '栏内')
        if cross:
            n_cross += 1
            n_th_pre += has_th
            n_cs_full_pre += all_cs
            if not dry:
                if not has_th:
                    add_trprop(trs[0], 'tblHeader')
                    n_th_add += 1
                for tr in trs:
                    if add_trprop(tr, 'cantSplit'):
                        n_cs_add += 1
            else:
                n_th_add += (0 if has_th else 1)
                n_cs_add += sum(1 for tr in trs
                                if tr.find(q('trPr')) is None or tr.find(q('trPr')).find(q('cantSplit')) is None)
        if inf['vert']:
            defects.append('表%d（%s）首列逐字竖排：%s' % (k, zone, '；'.join('行%d「%s」%d行' % v for v in inf['vert'][:4])))
        if inf['seccols'] >= 2 and not wide and inf['ncol'] > 3:
            recon.append('表%d 栏内表列数 %d＞3 → 转置/重构/转通栏三选一（交主会话）' % (k, inf['ncol']))
        if wide and inf['seccols'] >= 2:
            defects.append('表%d 通栏表落双栏区（宽%.0f＞栏宽%.0f）＝缺陷①' % (k, inf['tblw'], inf['colw']))
        # ⑧ 全部表 keepLines
        for p in tbl.iter(q('p')):
            if dry:
                ppr = p.find(q('pPr'))
                if ppr is None or ppr.find(q('keepLines')) is None:
                    n_kl_add += 1
                else:
                    n_kl_keep += 1
            else:
                if add_keeplines(p):
                    n_kl_add += 1
                else:
                    n_kl_keep += 1

    # 断言：跨断表两属性覆盖率
    if not dry:
        bad = []
        for k, (tbl, inf) in enumerate(zip(xml_tbls, infos)):
            cross = (inf['sp'] != inf['ep']) or (inf['y1'] < inf['y0'] - 2)
            if not cross:
                continue
            trs = [tr for tr in tbl.iter(q('tr'))]
            trpr0 = trs[0].find(q('trPr')) if trs else None
            ok_th = trpr0 is not None and trpr0.find(q('tblHeader')) is not None
            ok_cs = all((tr.find(q('trPr')) is not None and tr.find(q('trPr')).find(q('cantSplit')) is not None)
                        for tr in trs)
            if not (ok_th and ok_cs):
                bad.append(k)
        assert not bad, '跨断表两属性覆盖率未达100%: 表%s' % bad
        cov = '100% PASS（exec复核）'
    else:
        cov = '现状 tblHeader %d/%d、cantSplit 整表 %d/%d' % (n_th_pre, n_cross, n_cs_full_pre, n_cross)
    lines.append('表数 %d｜跨断表 %d（%s）｜拟/已挂 tblHeader %d、cantSplit %d 行｜keepLines 新挂 %d 段（幂等 %d）'
                 % (len(xml_tbls), n_cross, cov, n_th_add, n_cs_add, n_kl_add, n_kl_keep))
    for d_ in defects:
        lines.append('  缺陷: ' + d_)
    for r_ in recon:
        lines.append('  重构: ' + r_)
    lines.append('')

    if not dry and (n_th_add or n_cs_add or n_kl_add):
        import shutil
        bak = path + '.bak_表格规'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.t8tmp'
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
    return '\n'.join(lines)


def main():
    argv = sys.argv[1:]
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    report = None
    if '--report' in argv:
        k = argv.index('--report'); report = argv[k + 1]; del argv[k:k + 2]
    assert argv, '用法: python 工具/表格规范执行器.py <docx...> [--dry-run] [--report r.md]'
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
