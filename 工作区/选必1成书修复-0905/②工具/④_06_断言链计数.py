# -*- coding: utf-8 -*-
"""④轮步骤6a：断言链·计数面（三段）。
A：同步盘 12 件字节复制入 副本_④轮_改前（COM 页数「改前面」用——不直开同步盘原件），
   逐件 MD5 与 ④_改前锚定.json 的 sync_md5 全等（同步盘自锚定未漂移证明）。
B：逐件 改前（副本_④轮_改前）/改后（副本_④轮）document.xml 与 word/*.xml 全包的
   C9C9C9/C7C7C7 计数。守恒式（document.xml）：
     C7改后 ＝ C7改前 ＋ C9改前 ＋ ④_04表头行tcPr增量（I2/G/H 各＋3，余 0）
   且 C9改后（document.xml／全包）＝0（TOC 改前即 0）。
C：六类底纹计数.py 跑 12 件改后副本 → 报告/④_六类_<代号>.txt（讲练件族带 --jlp），
   解析「Σ N＝document.xml 原始 N」行与结论行；Σ＝B面原始计数恒等、
   过渡残留签名全包＝0；结论行原文入账（E件 F2F2F2 残留为已登记偏离——只登记不阻断）。
落盘 报告/④_断言链_计数.json。"""
import io, sys, os, re, json, shutil, hashlib, subprocess, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
SYNC = r'C:\提示词\高中数学\高中数学同步'
DST = os.path.join(BASE, '副本_④轮')
DST_PRE = os.path.join(BASE, '副本_④轮_改前')
REP = os.path.join(BASE, '报告')
TOOL = r'C:\提示词\工具\六类底纹计数.py'
FILES = [
    ('I1清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', False, 0),
    ('X1衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', False, 0),
    ('B讲练1上', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', True, 0),
    ('C讲练1下', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', True, 0),
    ('I2清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', False, 3),
    ('X2衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', False, 0),
    ('E讲练92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', True, 0),
    ('F讲练90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', True, 0),
    ('G讲练68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', True, 3),
    ('H讲练89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', True, 3),
    ('SM使用说明', '人教B版选必1·使用说明.docx', False, 0),
    ('TOC册目录页', '人教B版选必1·册目录页.docx', False, 0),
]

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def fill_counts(path):
    """逐 zip 成员的 w:fill="XXXXXX" 计数（document.xml 单列＋全包合计）。"""
    z = zipfile.ZipFile(path)
    doc = z.read('word/document.xml')
    c9_doc = doc.count(b'w:fill="C9C9C9"')
    c7_doc = doc.count(b'w:fill="C7C7C7"')
    c9_all = c7_all = 0
    for n in z.namelist():
        if not (n.startswith('word/') and n.endswith('.xml')):
            continue
        b = z.read(n)
        c9_all += b.count(b'w:fill="C9C9C9"')
        c7_all += b.count(b'w:fill="C7C7C7"')
    z.close()
    return dict(c9_doc=c9_doc, c7_doc=c7_doc, c9_all=c9_all, c7_all=c7_all)

ok_all = True
out = {'A_改前副本MD5': {}, 'B_守恒': {}, 'C_六类': {}}

# —— A：改前副本＋同步盘未漂移锚定 ——
os.makedirs(DST_PRE, exist_ok=True)
anchor = json.load(open(os.path.join(REP, '④_改前锚定.json'), encoding='utf-8'))
for _code, fn, _jlp, _extra in FILES:
    src = os.path.join(SYNC, fn)
    dst = os.path.join(DST_PRE, fn)
    shutil.copyfile(src, dst)
    m = md5(dst)
    ok = (m == anchor[fn]['sync_md5'])
    ok_all = ok_all and ok
    out['A_改前副本MD5'][fn] = {'md5': m, 'match_anchor': ok}
    print('A %-46s %s %s' % (fn[:46], m[:12], 'OK' if ok else '←≠同步盘已漂移'))

# —— B：改前/改后 C9/C7 守恒 ——
for code, fn, _jlp, extra in FILES:
    pre = fill_counts(os.path.join(DST_PRE, fn))
    post = fill_counts(os.path.join(DST, fn))
    exp_doc = pre['c7_doc'] + pre['c9_doc'] + extra
    exp_all = pre['c7_all'] + pre['c9_all'] + extra
    con_doc = (post['c7_doc'] == exp_doc)
    con_all = (post['c7_all'] == exp_all)
    c9_zero = (post['c9_doc'] == 0 and post['c9_all'] == 0)
    ok = con_doc and con_all and c9_zero
    ok_all = ok_all and ok
    out['B_守恒'][code] = {'file': fn, 'pre': pre, 'post': post, 'tcpr_extra': extra,
                           'expect_doc': exp_doc, 'expect_all': exp_all,
                           'conserv_doc': con_doc, 'conserv_all': con_all, 'c9_post_zero': c9_zero,
                           'ok': ok}
    print('B %-10s 改前C9doc %4d C7doc %4d → 改后C7doc %4d（期望 %4d）%s｜C9改后 doc/all %d/%d %s｜%s'
          % (code, pre['c9_doc'], pre['c7_doc'], post['c7_doc'], exp_doc,
             'OK' if con_doc else '←≠', post['c9_doc'], post['c9_all'],
             'OK' if c9_zero else '←残留', 'PASS' if ok else '←FAIL'))

# —— C：六类底纹计数（改后副本）——
for code, fn, jlp, _extra in FILES:
    p = os.path.join(DST, fn)
    rp = os.path.join(REP, '④_六类_%s.txt' % code)
    r = subprocess.run([sys.executable, TOOL, p, rp] + (['--jlp'] if jlp else []),
                       capture_output=True, text=True, encoding='utf-8')
    txt = r.stdout or ''
    # Σ 行形如「…Σ 1234＝document.xml 原始 1234 ✓」
    m = re.search(r'Σ (\d+)＝document\.xml 原始 (\d+)\s*(✓|←≠)', txt)
    sig = re.search(r'过渡残留签名 #C9C9C9[^：]*：document\.xml 挂点 (\d+)｜word/\*\.xml 全包 ([^\n]*)', txt)
    concl = [ln for ln in txt.splitlines() if ln.startswith('结论:')]
    c7_raw = out['B_守恒'][code]['post']['c7_doc']
    if m:
        sigma, raw = int(m.group(1)), int(m.group(2))
        sig_ok = (sigma == raw == c7_raw)
    else:
        sigma = raw = None
        sig_ok = False
    legacy_zero = bool(sig) and sig.group(1) == '0' and sig.group(2).strip() == '0'
    pass_line = bool(concl) and 'PASS' in concl[0]
    ok = (r.returncode == 0) and sig_ok and legacy_zero
    ok_all = ok_all and ok
    out['C_六类'][code] = {'report': os.path.basename(rp), 'sigma': sigma, 'raw': raw,
                           'c7_doc_expect': c7_raw, 'sigma_ok': sig_ok,
                           'legacy_c9': sig.groups() if sig else None, 'legacy_zero': legacy_zero,
                           'conclusion': concl[0] if concl else None, 'pass_line': pass_line,
                           'rc': r.returncode, 'ok': ok}
    print('C %-10s Σ %s＝raw %s（B面 %d）%s｜C9过渡残留 %s｜结论 %s｜%s'
          % (code, sigma, raw, c7_raw, 'OK' if sig_ok else '←≠',
             (sig.group(1) + '/' + sig.group(2).strip()) if sig else '缺行',
             (concl[0][4:34] + '…') if concl else '缺', 'PASS' if ok else '←FAIL'))

with open(os.path.join(REP, '④_断言链_计数.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('④_06 合计 PASS＝%s（A锚定/B守恒/C六类；结论行原文照登——E件F2F2F2残留属已登记偏离）' % ok_all)
sys.exit(0 if ok_all else 1)
