# -*- coding: utf-8 -*-
r"""导航表四列化.py — 子步6一次性脚本（总控任务B＋用户拍板2026-09-03删「节内题号」列）。
B/E首卷章首导航表：删第2列「节内题号」→四列固定（节名｜题量｜简单/中档/难｜题型组数，禁增列）；
列宽按附则《表格规范》通栏表款内容感知重排（复用 工具/表格重排工具.py 函数）；
三源恒等（导航表＝节标题行统计段＝全件统计行）与分卷要素断言随跑。
用法:
  python 导航表四列化.py --apply          施工（就地改B/E，写回产出文件夹原位）
  python 导航表四列化.py --verify         三源对照＋分卷要素断言（落盘 verify_子步6.json/.md）
"""
import sys, io, os, re, json, zipfile, shutil, hashlib
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
sys.path.insert(0, r'C:\提示词\工具')
from 表格重排工具 import (q, W, M, measure_table, allocate, apply_table, plan_table,
                        zones_of, is_navtbl, text_stream, TBLPR_ORDER, get_or_make)

SRC = r'C:\提示词\高中数学\高中数学同步'
NAV_FILES = {
 'B': os.path.join(SRC, '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
 'E': os.path.join(SRC, '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
}
CH_VOLUMES = {
 '第1章': ['B', 'C'],
 '第2章': ['E', 'F', 'G', 'H'],
}
VOL_FILES = {
 'C': os.path.join(SRC, '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
 'F': os.path.join(SRC, '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
 'G': os.path.join(SRC, '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
 'H': os.path.join(SRC, '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
}
EXPECT_HEAD = ['节名', '节内题号', '题量', '简单/中档/难', '题型组数']
RE_SECSTAT = re.compile(r'^(\d+(?:\.\d+)+)\s+(.+?)\s*本节(\d+)题')
RE_QH = re.compile(r'^(\d+(?:\.\d+)+)-\d+．（(简单|中档|难)')
RE_TXSTAT = re.compile(r'^(\d+(?:\.\d+){1,3})\s+.+?(\d+)题：题号')
RE_STATS_ROW = re.compile(r'^全件(\d+)题：简单(\d+)｜中档(\d+)｜难(\d+)')
RE_TITLE = re.compile(r'^人教B版选必1 第\d章 .+·讲练件（\d+题）$')
DROP_COL = 1                       # 「节内题号」列下标


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def find_nav(body):
    kids, brk, zp = zones_of(body)
    for i, el in enumerate(kids):
        if etree.QName(el).localname == 'tbl' and is_navtbl(el):
            zone = 'header' if (brk is not None and i <= brk) else 'body'
            return el, i, zone, zp, kids, brk
    return None, None, None, zp, kids, brk


def apply_one(path):
    z = zipfile.ZipFile(path)
    raw = z.read('word/document.xml')
    z.close()
    root = etree.fromstring(raw)
    body = root.find(q('body'))
    ts0 = text_stream(root)
    tbl, idx, zone, zp, kids, brk = find_nav(body)
    assert tbl is not None, '导航表未找到'
    assert zone == 'header', '导航表不在头部单栏区：' + str(zone)
    rows = tbl.findall(q('tr'))
    head = [''.join(t.text or '' for t in tc.iter(q('t'))) for tc in rows[0].findall(q('tc'))]
    assert head == EXPECT_HEAD, '表头不符预期: %s' % head
    removed = []
    for tr in rows:
        tcs = tr.findall(q('tc'))
        assert len(tcs) == 5, '行格数≠5'
        removed.append(''.join(t.text or '' for t in tcs[DROP_COL].iter(q('t'))))
        tr.remove(tcs[DROP_COL])
    grid = tbl.find(q('tblGrid'))
    gcs = grid.findall(q('gridCol'))
    grid.remove(gcs[DROP_COL])
    # 通栏表款重排（头部单栏区 limit＝内容宽）
    plan = plan_table(tbl, 'header', zp)
    assert plan['kind'] == '通栏区表' and plan['alloc'] is not None
    chg = apply_table(tbl, plan)
    # 文字流差异核验＝恰删该列全部文本（多重集差＝删除列文本多重集）
    from collections import Counter
    ts1 = text_stream(root)
    text_ok = (Counter(ts0) - Counter(ts1)) == Counter(t for t in removed)
    new_raw = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    sha_b = hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]
    tmp = path + '.tmp_rewrite'
    zin = zipfile.ZipFile(path, 'r')
    zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'word/document.xml':
            data = new_raw
        zout.writestr(item, data)
    zin.close()
    zout.close()
    shutil.move(tmp, path)
    return {'removed_cells': removed, 'plan_alloc': plan['alloc'], 'limit': plan['limit'],
            'changes': chg, 'text_diff_exact_drop': text_ok,
            'sha_before': sha_b, 'sha_after': hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]}


def read_body(path):
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    return root.find(q('body'))


def longest_sec(token, secs):
    hit = None
    for s in secs:
        if token == s or token.startswith(s + '.'):
            if hit is None or len(s) > len(hit):
                hit = s
    return hit


def verify():
    out = {'nav': {}, 'tri': {}, 'vol_assert': {}}
    nav_data = {}
    for code, path in NAV_FILES.items():
        body = read_body(path)
        tbl, idx, zone, zp, kids, brk = find_nav(body)
        rows = tbl.findall(q('tr'))
        head = [''.join(t.text or '' for t in tc.iter(q('t'))) for tc in rows[0].findall(q('tc'))]
        data = []
        for tr in rows[1:]:
            cells = [''.join(t.text or '' for t in tc.iter(q('t'))) for tc in tr.findall(q('tc'))]
            data.append(cells)
        # 样式核验
        tr0 = rows[0]
        shd_ok = all((tc.find(q('tcPr')).find(q('shd')) is not None
                      and tc.find(q('tcPr')).find(q('shd')).get(q('fill')) == 'C9C9C9')
                     for tc in tr0.findall(q('tc')))
        bold_ok = all(r.find(q('rPr')) is not None and r.find(q('rPr')).find(q('b')) is not None
                      for r in tr0.iter(q('r')))
        sz_ok = True
        spacing_ok = True
        for p in tbl.iter(q('p')):
            ppr = p.find(q('pPr'))
            sp = ppr.find(q('spacing')) if ppr is not None else None
            if sp is None or sp.get(q('line')) != '410' or sp.get(q('lineRule')) != 'atLeast':
                spacing_ok = False
            for r in p.iter(q('r')):
                rpr = r.find(q('rPr'))
                sz = rpr.find(q('sz')) if rpr is not None else None
                if sz is None or sz.get(q('val')) != '24':
                    sz_ok = False
        tw = tbl.find(q('tblPr')).find(q('tblW'))
        nav_data[code] = {'head': head, 'rows': data, 'zone': zone,
                          'style': {'head_shd_C9C9C9': shd_ok, 'head_bold': bold_ok,
                                    'sz_12pt': sz_ok, 'spacing_410': spacing_ok,
                                    'tblW': int(tw.get(q('w'))), 'type': tw.get(q('type'))}}
        out['nav'][code] = nav_data[code]
    # 三源对照
    for ch, vols in CH_VOLUMES.items():
        nav_code = vols[0]
        secs = [r[0].split(' ', 1)[0] for r in nav_data[nav_code]['rows'] if r[0] != '合计']
        sec_names = {r[0].split(' ', 1)[0]: r[0].split(' ', 1)[1] for r in nav_data[nav_code]['rows'] if r[0] != '合计'}
        nav_by_sec = {r[0].split(' ', 1)[0]: r for r in nav_data[nav_code]['rows'] if r[0] != '合计'}
        total_row = [r for r in nav_data[nav_code]['rows'] if r[0] == '合计'][0]
        # 源2：节标题统计段（跨卷）；源3a：题号块档位实测；源3b：题型标题统计段计数
        sec_stat = {}
        diff_count = {}
        grp_count = {}
        stats_row = None
        vol_report = {}
        for v in vols:
            path = NAV_FILES.get(v) or VOL_FILES[v]
            body = read_body(path)
            v_title = v_stats = v_nav = 0
            for el in body:
                ln = etree.QName(el).localname
                if ln == 'p':
                    t = ptext(el).strip()
                    if RE_TITLE.match(t):
                        v_title += 1
                    m = RE_STATS_ROW.match(t)
                    if m:
                        v_stats += 1
                        stats_row = {'题量': int(m.group(1)), '简单': int(m.group(2)),
                                     '中档': int(m.group(3)), '难': int(m.group(4))}
                    m = RE_SECSTAT.match(t)
                    if m:
                        sec_stat[m.group(1)] = {'name': m.group(2), 'n': int(m.group(3))}
                    m = RE_QH.match(t)
                    if m:
                        s = longest_sec(m.group(1), secs)
                        d = diff_count.setdefault(s, {'简单': 0, '中档': 0, '难': 0})
                        d[m.group(2)] += 1
                    m = RE_TXSTAT.match(t)
                    if m and '知识讲解' not in t and '方法讲解' not in t:
                        s = longest_sec(m.group(1), secs)
                        grp_count[s] = grp_count.get(s, 0) + 1
                elif ln == 'tbl' and is_navtbl(el):
                    v_nav += 1
            vol_report[v] = {'文内开头标题': v_title, '全件统计行': v_stats, '导航表': v_nav}
        out['vol_assert'][ch] = vol_report
        # 对照
        tri = []
        for s in secs:
            nav_r = nav_by_sec[s]
            nav_n = int(nav_r[2 - 1])           # 删列后：[节名, 题量, 简单/中档/难, 题型组数]
            nav_diff = nav_r[2]
            nav_grp = int(nav_r[3])
            m = re.match(r'简单(\d+)/中档(\d+)/难(\d+)', nav_diff)
            nav_d = {'简单': int(m.group(1)), '中档': int(m.group(2)), '难': int(m.group(3))}
            ss = sec_stat.get(s)
            dc = diff_count.get(s, {'简单': 0, '中档': 0, '难': 0})
            gc = grp_count.get(s, 0)
            ok = (ss is not None and ss['n'] == nav_n and dc == nav_d and gc == nav_grp)
            tri.append({'sec': s, 'nav题量': nav_n, '节统计段': ss['n'] if ss else None,
                        'nav三档': nav_d, '实测三档': dc, 'nav题型组数': nav_grp, '实测题型组数': gc,
                        '恒等': ok})
        sum_n = sum(int(r[1]) for r in nav_data[nav_code]['rows'] if r[0] != '合计')
        m = re.match(r'简单(\d+)/中档(\d+)/难(\d+)', total_row[2])
        tot_d = {'简单': int(m.group(1)), '中档': int(m.group(2)), '难': int(m.group(3))}
        sum_d = {k: sum(t['实测三档'][k] for t in tri) for k in tot_d}
        total_ok = (int(total_row[1]) == sum_n == (stats_row['题量'] if stats_row else -1)
                    and tot_d == sum_d == {'简单': stats_row['简单'], '中档': stats_row['中档'], '难': stats_row['难']})
        sum_g = sum(int(r[3]) for r in nav_data[nav_code]['rows'] if r[0] != '合计')
        out['tri'][ch] = {'rows': tri, '合计行题量': int(total_row[1]), '节行题量和': sum_n,
                          '全件统计行': stats_row, '合计三档': tot_d, '实测三档和': sum_d,
                          '合计题型组数': int(total_row[3]), '节行题型组数和': sum_g,
                          '合计恒等': total_ok and int(total_row[3]) == sum_g}
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--verify'
    here = os.path.dirname(os.path.abspath(__file__))
    if mode == '--apply':
        res = {}
        for code, path in NAV_FILES.items():
            res[code] = apply_one(path)
            print('[%s] 删列＋重排完成 alloc=%s limit=%d 文字流恰删列=%s sha %s→%s' % (
                code, res[code]['plan_alloc'], res[code]['limit'],
                res[code]['text_diff_exact_drop'], res[code]['sha_before'], res[code]['sha_after']))
        with open(os.path.join(here, 'apply_子步6.json'), 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    else:
        out = verify()
        with open(os.path.join(here, 'verify_子步6.json'), 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        md = ['# 子步6 三源对照＋分卷要素断言', '']
        for code, nv in out['nav'].items():
            md.append('## %s 导航表：落区=%s tblW=%d(%s) 表头行=%s' % (
                code, nv['zone'], nv['style']['tblW'], nv['style']['type'], '/'.join(nv['head'])))
            md.append('- 样式：表头C9C9C9=%s 加粗=%s 表内12pt=%s line410=%s' % (
                nv['style']['head_shd_C9C9C9'], nv['style']['head_bold'],
                nv['style']['sz_12pt'], nv['style']['spacing_410']))
        for ch, tri in out['tri'].items():
            md.append('## %s 三源对照（导航表＝节标题行统计段＝全件统计行）' % ch)
            md.append('| 节 | nav题量 | 节统计段 | nav三档 | 实测三档 | nav题型组数 | 实测组数 | 恒等 |')
            md.append('|---|---|---|---|---|---|---|---|')
            for r in tri['rows']:
                md.append('| %s | %d | %s | %s | %s | %d | %d | %s |' % (
                    r['sec'], r['nav题量'], r['节统计段'], r['nav三档'], r['实测三档'],
                    r['nav题型组数'], r['实测题型组数'], '✓' if r['恒等'] else '✗'))
            md.append('- 合计行：题量%d＝节行和%d＝全件统计行%d；三档合计＝实测和＝统计行 %s；题型组数合计%d＝节行和%d ⇒ 合计恒等＝%s' % (
                tri['合计行题量'], tri['节行题量和'], tri['全件统计行']['题量'],
                tri['合计三档'], tri['合计题型组数'], tri['节行题型组数和'], tri['合计恒等']))
            bad = [r for r in tri['rows'] if not r['恒等']]
            md.append('- 逐节恒等：%d/%d ✓%s' % (len(tri['rows']) - len(bad), len(tri['rows']),
                      ('；不恒等：' + '、'.join(r['sec'] for r in bad)) if bad else ''))
        for ch, vols in out['vol_assert'].items():
            md.append('## %s 分卷要素断言（仅首卷有文内标题/全件统计行/导航表）' % ch)
            for v, r in vols.items():
                expect_first = v == CH_VOLUMES[ch][0]
                ok = (r['文内开头标题'] == (1 if expect_first else 0)
                      and r['全件统计行'] == (1 if expect_first else 0)
                      and r['导航表'] == (1 if expect_first else 0))
                md.append('- %s：文内标题%d 全件统计行%d 导航表%d ⇒ %s' % (
                    v, r['文内开头标题'], r['全件统计行'], r['导航表'], '✓' if ok else '✗'))
        with open(os.path.join(here, 'verify_子步6.md'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(md) + '\n')
        print('落盘 verify_子步6.json/.md')


if __name__ == '__main__':
    main()
