# -*- coding: utf-8 -*-
"""④轮步骤7c：灰度四值校验 12 件（④轮新导出 PDF）＋改前基线（PDF对比/②E终）对照。
判据（2026-09-06 ④轮口径，经 H/I2/G 表头渲染定位修订——见 ④_10b 证据）：
  ①过渡签名201 矢量命中＝0（12 件——C9 已改 C7，CB-4 新件口径）；
  ②矢量离群：I2/G/H＝0（8 处规范化后无带外灰——改前含 F2F5F9/F2F5F8/CCCCCC/FAFAFA/FAFBFC）；
    其余件 vout 色（hex,计数）与改前逐色全等（SM 的 E0E0E0×1 系预存⑦段级题干底纹，只登记）；
  ③矢量199：9 件非④_04件逐页 199(改后)＝201(改前) 全等；I2/G/H 逐页 Δ≥0、
    Δ≠0 页 ⊆ 固定表格所在页（I2{18,19}/G{11}/H{13,14,15}——banner 表头行整行改色所致，
    视觉＝表格规范⑤：近白 banner→C7C7C7＋黑细线边框，已 PNG 目检 ④_10b）；
  ④像素簇数 改后＝改前（SM 2＝2 等）。
落盘 报告/④_灰度对照.json。"""
import io, sys, os, re, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
PDFO = os.path.join(BASE, 'PDF对比', '④轮PDF')
PDFB = os.path.join(BASE, 'PDF对比', '②E终')
REP = os.path.join(BASE, '报告')
TOOL = r'C:\提示词\工具\灰度四值校验.py'
DELTA_PAGES = {'I2清单2': {18, 19}, 'G讲练68': {11}, 'H讲练89': {13, 14, 15}}
FILES = [
    ('I1清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）', False),
    ('X1衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）', False),
    ('B讲练1上', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）', True),
    ('C讲练1下', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', True),
    ('I2清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）', False),
    ('X2衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）', False),
    ('E讲练92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）', True),
    ('F讲练90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）', True),
    ('G讲练68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）', True),
    ('H讲练89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）', True),
    ('SM使用说明', '人教B版选必1·使用说明', False),
    ('TOC册目录页', '人教B版选必1·册目录页', False),
]

def run_tool(pdf, rpt, jlp):
    r = subprocess.run([sys.executable, TOOL, pdf, '--report', rpt] + (['--jlp'] if jlp else []),
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    assert r.returncode == 0, '%s rc=%d\n%s' % (pdf, r.returncode, (r.stderr or '')[:400])
    return open(rpt, encoding='utf-8').read()

def parse(txt):
    m = re.search(r'结论: 矢量四值命中 (\d+)/(\d+)/(\d+)/(\d+)｜过渡签名201 (\d+)｜矢量离群 (\d+) 色｜像素簇 (\d+) 个', txt)
    outs = re.findall(r'#([0-9A-F]{6})（灰\d+）×(\d+)', txt)
    return {'vec': [int(m.group(i)) for i in (1, 2, 3, 4)], 'sig': int(m.group(5)),
            'vout': int(m.group(6)), 'pout': int(m.group(7)), 'vout_hex': dict(outs)}

def per_page(path):
    import pymupdf
    d = pymupdf.open(path)
    per = {}
    for i in range(len(d)):
        c7 = c9 = 0
        for dr in d[i].get_drawings():
            f = dr.get('fill')
            if f is None:
                continue
            r, g, b = [round(x * 255) for x in f]
            if (r, g, b) == (199, 199, 199):
                c7 += 1
            elif (r, g, b) == (201, 201, 201):
                c9 += 1
        if c7 or c9:
            per[i + 1] = (c7, c9)
    d.close()
    return per

ok_all = True
out = {}
for code, stem, jlp in FILES:
    t_new = run_tool(os.path.join(PDFO, stem + '.pdf'),
                     os.path.join(REP, '④_灰度_%s.txt' % code), jlp)
    t_old = run_tool(os.path.join(PDFB, stem + '.pdf'),
                     os.path.join(REP, '④_灰度改前_%s.txt' % code), jlp)
    pn, po = parse(t_new), parse(t_old)
    sig0 = (pn['sig'] == 0)
    if code in DELTA_PAGES:
        vout_ok = (pn['vout'] == 0)
    else:
        vout_ok = (pn['vout_hex'] == po['vout_hex'])
    pages = per_page(os.path.join(PDFO, stem + '.pdf'))
    pages_o = per_page(os.path.join(PDFB, stem + '.pdf'))
    allp = sorted(set(pages) | set(pages_o))
    deltas = {}
    loc_ok = True
    for p in allp:
        a = pages.get(p, (0, 0))[0]
        b = pages_o.get(p, (0, 0))[1]
        if a != b:
            deltas[p] = a - b
            if code not in DELTA_PAGES:
                loc_ok = False
            elif not (a - b >= 0 and p in DELTA_PAGES[code]):
                loc_ok = False
    pout_ok = (pn['pout'] == po['pout'])
    ok = sig0 and vout_ok and loc_ok and pout_ok
    ok_all = ok_all and ok
    out[code] = {'new': pn, 'old': po, 'delta_pages': deltas,
                 'sig_zero': sig0, 'vout_ok': vout_ok, 'loc_ok': loc_ok,
                 'pout_ok': pout_ok, 'delta_allow': sorted(DELTA_PAGES.get(code, [])),
                 'ok': ok}
    print('%s %-10s 201签名 %d→%d %s｜矢量离群 %s→%s %s｜像素簇 %d→%d %s｜199Δ页 %s %s' % (
        ' ' if ok else 'B←', code, po['sig'], pn['sig'], 'OK' if sig0 else '←残留',
        po['vout_hex'] or '{}', pn['vout_hex'] or '{}', 'OK' if vout_ok else '←≠',
        po['pout'], pn['pout'], 'OK' if pout_ok else '←≠',
        deltas if deltas else '无', 'OK' if loc_ok else '←非预期位移'))
with open(os.path.join(REP, '④_灰度对照.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('④_10 合计 PASS＝%s' % ok_all)
sys.exit(0 if ok_all else 1)
