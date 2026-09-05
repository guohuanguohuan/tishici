# -*- coding: utf-8 -*-
"""②E_07_断言批.py — ②-E 逐页巡检回归断言批（PDF/PNG/XML 面，零 COM）。
①逐页 PNG 完整性＋空白页扫描（巡检_②E/pages，120dpi）；②灰度四值校验 242 口径（十件，矢量层全页）；
③首页断言集（--gen-mapping/--make-p1/--run，十件）；④图定尺寸断言 --assert（十件）；⑤oMath 元素守恒（副本_②E 十件对锚）。
证据：报告/②E_07_断言批.md、②E_242_<代号>.txt、巡检_②E/首页断言报告.md、报告/②E_图定尺寸.*"""
import sys, io, os, re, json, subprocess, zipfile, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RPT = os.path.join(HERE, '报告')
DST = os.path.join(HERE, '副本_②E')
XJ = os.path.join(HERE, '巡检_②E')
PDF = os.path.join(XJ, 'pdf')
PNG = os.path.join(XJ, 'pages')

TEN = [
    ('清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）', 15, 396),
    ('衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）', 15, 882),
    ('上61', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）', 65, 3251),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）', 62, 2876),
    ('清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）', 32, 1156),
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）', 5, 243),
    ('92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）', 58, 2705),
    ('90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）', 58, 2914),
    ('68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）', 47, 2359),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）', 73, 4034),
]
EXP_PAGES = {sh: p for sh, _, p, _ in TEN}
OM_BASE = {sh: om for sh, _, _, om in TEN}
LIST_FILES = {'清单1', '清单2'}
JLP = {'上61', '下79', '92', '90', '68', '89'}

OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

alloks = {}

# —— ① 逐页 PNG 完整性＋空白页扫描 ——
say('== ① 逐页 PNG 完整性＋空白页扫描 ==')
import fitz
png_ok = True
blank_all = []
for sh, fn, pg_exp, _ in TEN:
    d = os.path.join(PNG, sh)
    pngs = sorted(glob.glob(os.path.join(d, 'p*.png')))
    if len(pngs) != pg_exp:
        png_ok = False
        say('  !! %s PNG %d 页 ≠ 预期 %d' % (sh, len(pngs), pg_exp))
        continue
    blanks = []
    for p in pngs:
        pix = fitz.Pixmap(p)
        arr = bytearray(pix.samples)
        s0 = arr[:2000]
        uniform = all(b == s0[0] for b in s0) and len(set(arr[::4097])) == 1
        if uniform:
            blanks.append(os.path.basename(p))
        pix = None
    if blanks:
        blank_all.append((sh, blanks))
    say('  %s：%d 页 PNG 齐，均匀空白页=%s' % (sh, len(pngs), blanks or '0'))
alloks['png'] = png_ok
say('  逐页完整性 = %s；空白页清单=%s（空白页须人工目检定责）' % ('PASS' if png_ok else 'FAIL', blank_all or '无'))

# —— ② 灰度四值校验（242 口径；矢量层全页，平台抽样前5页） ——
say('== ② 灰度四值校验（十件；讲练件 --jlp） ==')
res242 = {}
ok242 = True
for sh, fn, _p, _o in TEN:
    pdf = os.path.join(PDF, sh + '.pdf')
    rep = os.path.join(RPT, '②E_242_%s.txt' % sh)
    cmd = [sys.executable, os.path.join(ROOT, '工具', '灰度四值校验.py'), pdf, '--report', rep]
    if sh in JLP:
        cmd.append('--jlp')
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                       timeout=900, cwd=ROOT)
    txt = open(rep, encoding='utf-8').read() if os.path.exists(rep) else (r.stdout or '')
    m = re.search(r'结论: 矢量四值命中 (\d+)/(\d+)/(\d+)/(\d+)｜矢量离群 (\d+) 色｜像素簇 (\d+) 个', txt)
    if not m:
        ok242 = False
        say('  !! %s 校验输出不可解析' % sh)
        continue
    b190, b209, b201, b242, vout, pclu = map(int, m.groups())
    exp242 = sh not in LIST_FILES      # 清单件无题干底纹（T6a=0）——242 未检出不判FAIL，照实登记
    band_ok = (b190 > 0) and ((b242 > 0) if exp242 else True) and ((b201 > 0) if sh in JLP else True)
    ok = (vout == 0) and band_ok
    ok242 = ok242 and ok
    res242[sh] = (b190, b209, b201, b242, vout, pclu)
    say('  %-6s 矢量命中190/209/201/242=%d/%d/%d/%d 离群色=%d 像素簇=%d %s'
        % (sh, b190, b209, b201, b242, vout, pclu, 'PASS' if ok else '!!FAIL'))
alloks['g242'] = ok242
say('  242 口径校验 = %s' % ('PASS' if ok242 else 'FAIL'))

# —— ③ 首页断言集（十件） ——
say('== ③ 首页断言集（gen-mapping → make-p1 → run） ==')
pairs = ['%s=%s' % (sh, os.path.join(DST, fn + '.docx')) for sh, fn, _p, _o in TEN]
r1 = subprocess.run([sys.executable, os.path.join(ROOT, '工具', '首页断言集执行器.py'),
                     '--gen-mapping', '--out', XJ] + pairs,
                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600, cwd=ROOT)
say('  gen-mapping exit=%d\n%s' % (r1.returncode, (r1.stdout or '')[-600:]))
r2 = subprocess.run([sys.executable, os.path.join(ROOT, '工具', '首页断言集执行器.py'),
                     '--make-p1', '--out', XJ] + pairs,
                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600, cwd=ROOT)
say('  make-p1 exit=%d' % r2.returncode)
r3 = subprocess.run([sys.executable, os.path.join(ROOT, '工具', '首页断言集执行器.py'),
                     '--run', '--out', XJ] + pairs,
                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900, cwd=ROOT)
say('  run exit=%d\n%s' % (r3.returncode, (r3.stdout or '')[-600:]))
hj = json.load(open(os.path.join(XJ, '首页断言结果.json'), encoding='utf-8'))
a1_fail = [c for c, r in hj.items() if c != '阴性对照' and r.get('a1', ('', ''))[0] != 'PASS']
a2_fail = [c for c, r in hj.items() if c != '阴性对照'
           and any(row[1] == 'FAIL' for row in r.get('a2', []))]
a5_fail = [c for c, r in hj.items() if c != '阴性对照' and r.get('a5', ('', ''))[0] != 'PASS']
blocked = [c for c, r in hj.items() if r.get('blocked')]
neg = hj.get('阴性对照', {})
if neg:
    neg_ok = (neg.get('expect') == 'FAIL' and neg.get('ok') is True)
else:
    neg_ok = True   # 本轮无缺陷态样本，阴性对照未执行——不作硬断言（登记）
home_ok = (not a1_fail and not a2_fail and not a5_fail and not blocked and neg_ok)
alloks['home'] = home_ok
say('  断言①FAIL=%s 断言②FAIL=%s 断言⑤FAIL=%s blocked=%s 阴性对照=%s → %s'
    % (a1_fail, a2_fail, a5_fail, blocked, ('ok' if neg_ok else 'FAIL') if neg else '未执行(无缺陷态样本)', 'PASS' if home_ok else 'FAIL'))

# —— ④ 图定尺寸断言 --assert（十件）＋页尾空白登记（--page-tail） ——
say('== ④ 图定尺寸断言 --assert（十件） ==')
r4 = subprocess.run([sys.executable, os.path.join(ROOT, '工具', '图定尺寸断言器.py'),
                     '--assert', '--out', os.path.join(RPT, '②E_图定尺寸')] + pairs,
                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900, cwd=ROOT)
say('  assert exit=%d\n%s' % (r4.returncode, (r4.stdout or '')[-800:]))
md4 = open(os.path.join(RPT, '②E_图定尺寸.md'), encoding='utf-8').read()
act_rows = [ln for ln in md4.splitlines() if re.search(r'\| (带域断言族|登记豁免族)', ln) and re.search(r'缩|超|放大', ln)]
say('  图尺寸待处置行=%d（应为0——历轮已 apply 定尺寸，assert 应全「不动」）' % len(act_rows))
for ln in act_rows[:10]:
    say('    ' + ln[:150])
alloks['fig'] = (len(act_rows) == 0) and r4.returncode == 0
say('  图定尺寸断言 = %s' % ('PASS' if alloks['fig'] else 'FAIL'))

# —— ⑤ oMath 元素守恒（副本十件 post-盖章，对 ②-F 锚） ——
say('== ⑤ oMath 元素守恒（十件，XML 元素级） ==')
from lxml import etree
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ok_om = True
for sh, fn, _p, om_exp in TEN:
    z = zipfile.ZipFile(os.path.join(DST, fn + '.docx'))
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    c = sum(len(list(p.iter('{%s}oMath' % M))) for p in doc.iter('{%s}p' % W))
    hit = (c == om_exp)
    ok_om = ok_om and hit
    say('  %-6s oMath=%5d 锚=%5d %s' % (sh, c, om_exp, 'PASS' if hit else '!!FAIL'))
alloks['omath'] = ok_om
say('  oMath 守恒 = %s' % ('PASS' if ok_om else 'FAIL'))

say('== 汇总 ==')
ALLOK = all(alloks.values())
say('SUMMARY_07 ALLOK=%s %s' % (ALLOK, alloks))
with open(os.path.join(RPT, '②E_07_断言批.md'), 'w', encoding='utf-8') as f:
    f.write('# ②-E 断言批（PDF/PNG/XML 面）\n\n```text\n' + '\n'.join(OUT) + '\n```\n\n'
            + '## 242 四值命中表\n\n| 件 | 190 | 209 | 201 | 242 | 矢量离群 | 像素簇 |\n|---|---|---|---|---|---|---|\n'
            + '\n'.join('| %s | %d | %d | %d | %d | %d | %d |' % (k, *v) for k, v in res242.items()) + '\n')
sys.exit(0 if ALLOK else 2)
