# -*- coding: utf-8 -*-
"""
SW任务3：B/E章首导航表「题号区间」列改节内口径（看板「导航表节内口径」联动项）
依据：E3知会B卷导航表「题号区间」列仍全局旧号；层级制改制（口径C）后全件已无全局题号，
该列为唯一残留全局区间引用。属改制授权差异「统计段区间括注改写」同族，逐笔登记。
改法（择简，与节标题行统计段/册目录页题量括注口径一致）：
  - 表头「题号区间」→「节内题号」；
  - 每节行「第X—Y题」→「1—N」（N=该节题量；N=1时径写「1」——节号已在节名列、不重复冠「节号：」前缀）；
  - 合计行区间值→「—」（层级制无全件连续区间；合计题量/难度/题型组数各列恒等不动）。
断言（逐件）：
  C1 表头结构＝节名｜题号区间｜题量｜简单/中档/难｜题型组数（改前）；
  C2 改前各行全局区间 span＝该行题量、逐行起点=前行终点+1、合计＝各节题量之和；
  C3 改后每节行区间终点＝该行题量（N=1行为「1」）；其余各列单元格文本逐格与改前相等；
  C4 全件统计行文本改前后恒等；节标题行统计段（本节N题）逐节N与导航表题量恒等、改前后恒等；
  C5 除word/document.xml外zip成员逐字节不变。
用法: python 导航表节内口径.py [--dry-run]
"""
import io
import os
import re
import sys
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from lxml import etree

WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def W(t):
    return '{%s}%s' % (WNS, t)


WORK = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\S盖章\SW工作'
EVID = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\S盖章\SW脚本'
FILES = {
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
}
RANGE_RE = re.compile(r'^第(\d+)—(\d+)题$')
SEC_RE = re.compile(r'^(\d+(?:\.\d+)+)\s')
SECSTAT_RE = re.compile(r'本节(\d+)题')
FULLSTAT_RE = re.compile(r'^全件\d+题')
DASH = '—'


def cell_text(tc):
    return ' '.join(''.join(t.text or '' for t in p.iter() if t.tag == W('t')).strip()
                    for p in tc.findall(W('p'))).strip()


def set_cell_text(tc, new_text):
    """单段单run形态（勘察已证）：置该段首个非空run的w:t文本，其余run文本清空。"""
    done = False
    for p in tc.findall(W('p')):
        for r in p.findall(W('r')):
            ts = r.findall(W('t'))
            if not ts:
                continue
            for t in ts:
                if not done and (t.text or '').strip():
                    t.text = new_text
                    done = True
                else:
                    t.text = ''
    return done


def section_stat_map(body):
    """节标题行（pPr整行底纹ADC2DA）统计段：节号→(本节N题, 整行文本)。"""
    out = {}
    for p in body.findall(W('p')):
        pPr = p.find(W('pPr'))
        if pPr is None:
            continue
        shd = pPr.find(W('shd'))
        if shd is None or (shd.get(W('fill')) or '').upper() != 'ADC2DA':
            continue
        txt = ''.join(t.text or '' for t in p.iter() if t.tag == W('t')).strip()
        m = SEC_RE.match(txt)
        n = SECSTAT_RE.search(txt)
        if m and n:
            out[m.group(1)] = (int(n.group(1)), txt)
    return out


def process(code, fname, dry_run):
    path = os.path.join(WORK, fname)
    with zipfile.ZipFile(path) as z:
        members = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    blob = dict(members)
    root = etree.fromstring(blob['word/document.xml'])
    body = root.find(W('body'))

    tbl = next((t for t in body if t.tag == W('tbl')), None)
    if tbl is None:
        return None, ['%s: 无表格' % code]
    rows = tbl.findall(W('tr'))
    grid = [[cell_text(tc) for tc in tr.findall(W('tc'))] for tr in rows]
    fails, reg = [], []

    # C1 表头结构
    if grid[0] != ['节名', '题号区间', '题量', '简单/中档/难', '题型组数']:
        fails.append('C1失败：表头结构不符：%r' % grid[0])
    if grid[-1][0] != '合计':
        fails.append('C1失败：末行非合计行：%r' % grid[-1][0])

    # C2 改前恒等：区间span=题量、逐行衔接、合计=各节和
    sec_rows = grid[1:-1]
    prev_end = 0
    sec_info = []
    for gi, g in enumerate(sec_rows, start=2):
        m = RANGE_RE.match(g[1])
        if not m:
            fails.append('C2失败：行%d区间值形态不符：%r' % (gi, g[1]))
            continue
        s, e = int(m.group(1)), int(m.group(2))
        qty = int(g[2])
        if e - s + 1 != qty:
            fails.append('C2失败：行%d span(%d)≠题量(%d)' % (gi, e - s + 1, qty))
        if s != prev_end + 1:
            fails.append('C2失败：行%d起点%d≠前行终点+1(%d)' % (gi, s, prev_end + 1))
        prev_end = e
        sec_no = SEC_RE.match(g[0])
        if not sec_no:
            fails.append('C2失败：行%d节名无节号前缀：%r' % (gi, g[0]))
        sec_info.append((gi, sec_no.group(1) if sec_no else '?', s, e, qty))
    mt = RANGE_RE.match(grid[-1][1])
    if not mt or int(mt.group(1)) != 1 or int(mt.group(2)) != prev_end:
        fails.append('C2失败：合计区间非第1—%d题：%r' % (prev_end, grid[-1][1]))
    if int(grid[-1][2]) != sum(q for *_, q in sec_info):
        fails.append('C2失败：合计题量%r≠各节和%d' % (grid[-1][2], sum(q for *_, q in sec_info)))

    # C4前置：全件统计行＋节标题行统计段快照与交叉恒等
    # （导航表＝全章口径，本卷未含的节（B之1.2.5在C卷、E之2.3.4起在F/G/H卷）在本件无节标题行——
    #   交叉恒等按「本卷在场的节」双向核验：在场节逐一对照＋本件全部节标题行均有对应导航行）
    full_before = [''.join(t.text or '' for t in p.iter() if t.tag == W('t')).strip()
                   for p in body.findall(W('p')) if FULLSTAT_RE.match(
                       ''.join(t.text or '' for t in p.iter() if t.tag == W('t')).strip())]
    if not full_before:
        fails.append('C4失败：全件统计行未找到')
    secstat = section_stat_map(body)
    nav_map = {sec_no: qty for _gi, sec_no, _s, _e, qty in sec_info}
    for gi, sec_no, _s, _e, qty in sec_info:
        if sec_no in secstat and secstat[sec_no][0] != qty:
            fails.append('C4失败：节%s统计段题量%d≠导航表%d（本卷在场节）' % (sec_no, secstat[sec_no][0], qty))
    for sec_no, (n, _txt) in secstat.items():
        if sec_no not in nav_map:
            fails.append('C4失败：节标题行%s在导航表无对应行' % sec_no)
        elif nav_map[sec_no] != n:
            fails.append('C4失败：节标题行%s题量%d≠导航表%d' % (sec_no, n, nav_map[sec_no]))
    secstat_before = {k: v[1] for k, v in secstat.items()}

    if fails:
        return None, fails

    # ---- 手术 ----
    n_cells = 0
    trs = rows
    tcs_head = trs[0].findall(W('tc'))
    reg.append(('表头·列2', '题号区间', '节内题号'))
    if not dry_run:
        set_cell_text(tcs_head[1], '节内题号')
    n_cells += 1
    for (gi, sec_no, _s, _e, qty), tr in zip(sec_info, trs[1:-1]):
        new = '1' if qty == 1 else '1%s%d' % (DASH, qty)
        old = grid[gi - 1][1]
        reg.append(('行%d·%s·列2' % (gi, sec_no), old, new))
        if not dry_run:
            set_cell_text(tr.findall(W('tc'))[1], new)
        n_cells += 1
    reg.append(('合计行·列2', grid[-1][1], DASH))
    if not dry_run:
        set_cell_text(trs[-1].findall(W('tc'))[1], DASH)
    n_cells += 1

    # ---- 落盘 ----
    if not dry_run:
        out = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.tmp'
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
            for name, data in members:
                zo.writestr(name, out if name == 'word/document.xml' else data)
        os.replace(tmp, path)

    # ---- C3/C4/C5 复验（重开） ----
    with zipfile.ZipFile(path) as z:
        post_blob = {i.filename: z.read(i.filename) for i in z.infolist()}
    proot = etree.fromstring(post_blob['word/document.xml'])
    pbody = proot.find(W('body'))
    ptbl = next(t for t in pbody if t.tag == W('tbl'))
    pgrid = [[cell_text(tc) for tc in tr.findall(W('tc'))] for tr in ptbl.findall(W('tr'))]
    if pgrid[0][1] != '节内题号':
        fails.append('C3失败：表头改写未生效：%r' % pgrid[0][1])
    for ri in range(1, len(pgrid) - 1):
        qty = int(pgrid[ri][2])
        expect = '1' if qty == 1 else '1%s%d' % (DASH, qty)
        if pgrid[ri][1] != expect:
            fails.append('C3失败：行%d区间值%r≠期望%r' % (ri + 1, pgrid[ri][1], expect))
    if pgrid[-1][1] != DASH:
        fails.append('C3失败：合计行区间值%r≠%r' % (pgrid[-1][1], DASH))
    # 其余各列逐格恒等
    for ri, (g0, g1) in enumerate(zip(grid, pgrid)):
        for ci in (0, 2, 3, 4):
            if g0[ci] != g1[ci]:
                fails.append('C3失败：行%d列%d被意外改动：%r→%r' % (ri + 1, ci + 1, g0[ci], g1[ci]))
    pfull = [''.join(t.text or '' for t in p.iter() if t.tag == W('t')).strip()
             for p in pbody.findall(W('p')) if FULLSTAT_RE.match(
                 ''.join(t.text or '' for t in p.iter() if t.tag == W('t')).strip())]
    if pfull != full_before:
        fails.append('C4失败：全件统计行被改动：%r→%r' % (full_before, pfull))
    psecstat = section_stat_map(pbody)
    if {k: v[1] for k, v in psecstat.items()} != secstat_before:
        fails.append('C4失败：节标题行统计段被改动')
    # C5 其余成员逐字节
    for name, data in members:
        if name != 'word/document.xml' and post_blob.get(name) != data:
            fails.append('C5失败：成员被改动：%s' % name)

    return {'code': code, 'file': fname, 'n_rows': len(rows), 'n_sec': len(sec_info),
            'n_cells': n_cells, 'reg': reg, 'fails': fails,
            'grand': int(pgrid[-1][2]) if not fails else int(grid[-1][2])}, fails


def main():
    dry_run = '--dry-run' in sys.argv
    evid_lines = ['# SW任务3证据：B/E导航表题号区间列改节内口径（逐笔授权差异登记）', '',
                  '依据：层级制改制后全件已无全局题号；导航表区间列为唯一残留全局引用。改法择简：表头「题号区间」→「节内题号」；每节行「第X—Y题」→「1—N」（N=题量，N=1写「1」）；合计行→「—」（层级制无全件连续区间）。', '']
    for code, fname in FILES.items():
        res, fails = process(code, fname, dry_run)
        if res is None:
            print('[%s] 失败：%s' % (code, '; '.join(fails)))
            continue
        print('[%s] 行%d（表头1+节%d+合计1）｜改写单元格%d笔｜合计题量%d｜断言%s'
              % (code, res['n_rows'], res['n_sec'], res['n_cells'], res['grand'],
                 '全过（C1表头/C2改前恒等/C3改后恒等+C4统计恒等/C5部件恒等）' if not fails
                 else '失败:' + ';'.join(fails)))
        evid_lines.append('## %s（%s）——%d笔' % (code, fname, res['n_cells']))
        evid_lines.append('')
        evid_lines.append('| 位置 | 改前 | 改后 |')
        evid_lines.append('|---|---|---|')
        for pos, old, new in res['reg']:
            evid_lines.append('| %s | %s | %s |' % (pos, old, new))
        evid_lines.append('')
    if not dry_run:
        with open(os.path.join(EVID, 'SW任务3_导航表授权差异.md'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(evid_lines))
        print('授权差异登记落盘：SW任务3_导航表授权差异.md')


if __name__ == '__main__':
    main()
