# -*- coding: utf-8 -*-
"""②D_R2_02_T9_exec.py — ②-D 重跑轮 T9 exec（②-F 修复态基态；初跑脚本 ②D_02_T9_exec.py 改版）。
执行基线＝②D_R2_T9_dry_预跑.md（修复态 fresh dry）：
  a) [59,129,476,546,89,52,537,505,387,529]（＝派发基线，硬对平）
  b) 节[10,2,9,1,20,1,10,5,6,1] 讲部[0,0,10,7,0,0,14,12,6,13] 题型[0,5,49,69,0,8,62,61,50,61]（硬对平）
  c) 新挂[59,142,636,481,213,64,606,666,502,852] 幂等[13,0,19,0,54,0,31,7,15,1]（T8 遗留）
     长段[17,4,69,165,51,5,75,92,88,122]（派发基线 17/4/79/187/51/5/86/101/98/153 系②-A前旧态，
     差＝T5 结构重排＋②-F 复原落段，桥梁账随终报；硬断言＝长段零新增挂载）
②-F 血泪坑硬断言：exec 后逐件 m:oMath 元素总数不变（锚 396/882/3251/2876/1156/243/2705/2914/2359/4034，
  树级＋对 .bak_跨行护 前态双重）。不过＝立即停跑。
报告：报告/②D_R2_T9_exec.md、报告/②D_R2_T9_断言.md"""
import sys, io, os, re, time, zipfile, hashlib, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
RPT = os.path.join(HERE, '报告')
T9 = os.path.join(ROOT, '工具', '跨行保护器.py')
NAMES = [
    '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
]
SHORT = ['清单1', '衔接1', '上61', '下79', '清单2', '衔接2', '92', '90', '68', '89']
BASE_A = [59, 129, 476, 546, 89, 52, 537, 505, 387, 529]
BASE_B_SEC = [10, 2, 9, 1, 20, 1, 10, 5, 6, 1]
BASE_B_LECT = [0, 0, 10, 7, 0, 0, 14, 12, 6, 13]
BASE_B_GRP = [0, 5, 49, 69, 0, 8, 62, 61, 50, 61]
BASE_C_NEW = [59, 142, 636, 481, 213, 64, 606, 666, 502, 852]
BASE_C_IDEM = [13, 0, 19, 0, 54, 0, 31, 7, 15, 1]
BASE_C_LONG = [17, 4, 69, 165, 51, 5, 75, 92, 88, 122]
OM_BASE = [396, 882, 3251, 2876, 1156, 243, 2705, 2914, 2359, 4034]

T9_LINE = re.compile(r'a\) 芯片插WJ (\d+) 处（幂等 (\d+)）｜b\) 标题keepLines 新挂 (\d+)（节(\d+)/讲部(\d+)/题型(\d+)，幂等 (\d+)）｜'
                     r'c\) oMath短段keepLines 新挂 (\d+)（幂等 (\d+)；长段 (\d+) 登记不挂）')

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
WJ = '⁠'
CHIP_LOOSE = re.compile(r'【[^】]{1,64}】')
SEC_TTL_RE = re.compile(r'^\d+\.\d+(?:\.\d+)?[\s　]+\S')
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*(?:方法讲解|知识讲解)[｜|]')
GRP_RE = re.compile(r'^\d+(?:\.\d+){2,}[\s　]+\S')
OM_SHORT_LIMIT = 60

def eff_len(s):
    return sum(1.0 if ord(c) > 0x2E7F else 0.5 for c in s)

def load(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    parts = {i.filename: hashlib.md5(z.read(i.filename)).hexdigest() for i in z.infolist()}
    z.close()
    return doc, parts

def om_count(body):
    return sum(len(list(p.iter(qm('oMath')))) for p in body.iter(q('p')))

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None

def has_left_bar(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return False
    pb = ppr.find(q('pBdr'))
    return pb is not None and pb.find(q('left')) is not None

def has_kl(p):
    ppr = p.find(q('pPr'))
    return ppr is not None and ppr.find(q('keepLines')) is not None

def title_kind(p):
    t = ptext(p)
    if pfill(p) == 'ADC2DA' and SEC_TTL_RE.match(t):
        return '节'
    if LECT_RE.match(t):
        return '讲部'
    if GRP_RE.match(t) and (pfill(p) == 'C6D4E3' or has_left_bar(p) or '：' in t[:60]):
        return '题型'
    return None

OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

# ---------- ① exec ----------
say('=== ① T9 exec（逐件，计数对平修复态预跑基线） ===')
exec_rows = []
ok_exec = True
for k, n in enumerate(NAMES):
    fp = os.path.join(DST, n)
    bakp = fp + '.bak_跨行护'
    if os.path.exists(bakp):
        pd_ = subprocess.run(['python', T9, fp, '--dry-run'], capture_output=True,
                             text=True, encoding='utf-8', timeout=120, cwd=ROOT)
        m0 = T9_LINE.search(pd_.stdout or '')
        if pd_.returncode == 0 and m0 and all(int(m0.group(i)) == 0 for i in (1, 3, 8)):
            say('  %s 已 exec 态（dry 全零新挂）→ 幂等重放跳过改写' % SHORT[k])
            exec_rows.append('%-6s 已 exec 态跳过（首轮计数见 ②D_R2_T9_exec_首轮.md 或预跑）' % SHORT[k])
            continue
    p = subprocess.run(['python', T9, fp], capture_output=True,
                       text=True, encoding='utf-8', timeout=300, cwd=ROOT)
    m = T9_LINE.search(p.stdout)
    if p.returncode != 0 or not m:
        ok_exec = False
        say('  !! %s exec 失败 exit=%d %s' % (SHORT[k], p.returncode, p.stderr[-200:]))
        break
    chip, idem_a, nb, sec, lect, grp, idem_b, nc, idem_c, lng = map(int, m.groups())
    hits = (chip == BASE_A[k] and idem_a == 0 and (sec, lect, grp) == (BASE_B_SEC[k], BASE_B_LECT[k], BASE_B_GRP[k])
            and idem_b == 0 and nc == BASE_C_NEW[k] and idem_c == BASE_C_IDEM[k] and lng == BASE_C_LONG[k])
    ok_exec = ok_exec and hits
    exec_rows.append('%-6s a)%3d(幂等%d) b)%3d(节%d/讲部%d/题型%d) c)%3d(幂等%2d)长%3d  %s'
                     % (SHORT[k], chip, idem_a, nb, sec, lect, grp, nc, idem_c, lng,
                        'PASS' if hits else '!!FAIL vs 基线 a=%d b=%d/%d/%d c新=%d幂=%d长=%d'
                        % (BASE_A[k], BASE_B_SEC[k], BASE_B_LECT[k], BASE_B_GRP[k],
                           BASE_C_NEW[k], BASE_C_IDEM[k], BASE_C_LONG[k])))
    say('  ' + exec_rows[-1])
with open(os.path.join(RPT, '②D_R2_T9_exec.md'), 'w', encoding='utf-8') as f:
    f.write('# ②D 重跑轮 T9 exec（a 芯片WJ／b 标题keepLines／c 短公式段keepLines；基态＝②-F 修复态）\n\n```\n'
            + '\n'.join(exec_rows) + '\n```\n- 执行基线＝②D_R2_T9_dry_预跑.md；a/b 与派发基线逐件对平；c 桥梁账（T8幂等＋②-F复原＋T5结构差）随终报。\n')
if not ok_exec:
    say('!! exec 计数未对平——停止后续步骤')
    with open(os.path.join(RPT, '②D_R2_T9_断言.md'), 'w', encoding='utf-8') as f:
        f.write('```text\n' + '\n'.join(OUT) + '\n```\n')
    sys.exit(2)

# ---------- ② oMath 守恒（②-F 血泪坑硬断言） ----------
say('=== ② oMath 元素守恒（exec 态 vs ②-F 锚 vs .bak_跨行护 前态） ===')
ok_om = True
om_rows = []
for k, n in enumerate(NAMES):
    fp = os.path.join(DST, n)
    doc_p, _ = load(fp)
    c_now = om_count(doc_p.find(q('body')))
    bak = fp + '.bak_跨行护'
    c_pre = None
    if os.path.exists(bak):
        doc_b, _ = load(bak)
        c_pre = om_count(doc_b.find(q('body')))
    hit = (c_now == OM_BASE[k]) and (c_pre is None or c_pre == OM_BASE[k])
    ok_om = ok_om and hit
    om_rows.append('%-6s oMath exec后=%5d 锚=%5d 前态=%s  %s' % (SHORT[k], c_now, OM_BASE[k],
                  ('%5d' % c_pre) if c_pre is not None else '  n/a', 'PASS' if hit else '!!FAIL'))
    say('  ' + om_rows[-1])
    if not hit:
        say('  !! oMath 守恒破坏——立即停跑呈报')
        break
with open(os.path.join(RPT, '②D_R2_T9_oMath守恒.md'), 'w', encoding='utf-8') as f:
    f.write('# ②D 重跑轮 oMath 元素守恒（T9 exec 后；锚＝②-F 修复态基线）\n\n```text\n' + '\n'.join(om_rows) + '\n```\n')
if not ok_om:
    with open(os.path.join(RPT, '②D_R2_T9_断言.md'), 'w', encoding='utf-8') as f:
        f.write('```text\n' + '\n'.join(OUT) + '\n```\n')
    sys.exit(2)

# ---------- ③ 幂等二跑 ----------
say('=== ③ T9 dry 幂等二跑（exec 后副本，须全零新挂） ===')
ok_idem = True
idem_lines = []
for run in (1, 2):
    for k, n in enumerate(NAMES):
        p = subprocess.run(['python', T9, os.path.join(DST, n), '--dry-run'], capture_output=True,
                           text=True, encoding='utf-8', timeout=120, cwd=ROOT)
        m = T9_LINE.search(p.stdout)
        if p.returncode != 0 or not m:
            ok_idem = False
            say('  !! run%d %s dry 失败' % (run, SHORT[k]))
            continue
        chip, idem_a, nb, sec, lect, grp, idem_b, nc, idem_c, lng = map(int, m.groups())
        zero = (chip == 0 and nb == 0 and nc == 0)
        ok_idem = ok_idem and zero
        idem_lines.append('run%d %-6s a新%d b新%d c新%d（幂等 a%d b%d c%d，长%d）%s'
                          % (run, SHORT[k], chip, nb, nc, idem_a, idem_b, idem_c, lng,
                             'PASS' if zero else '!!FAIL'))
        if not zero:
            say('  ' + idem_lines[-1])
say('  幂等二跑 20 组全零新挂 = %s' % ok_idem)
with open(os.path.join(RPT, '②D_R2_T9_幂等dry.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(idem_lines) + '\n')

# ---------- ④ 独立 XML 探针 ----------
say('=== ④ 独立 XML 探针（exec 态 vs .bak_跨行护 前态） ===')
ok_probe = True
probe_rows = []
for k, n in enumerate(NAMES):
    fp = os.path.join(DST, n)
    bak = fp + '.bak_跨行护'
    doc_p, parts_p = load(fp)
    doc_b, parts_b = load(bak)
    body_p, body_b = doc_p.find(q('body')), doc_b.find(q('body'))
    paras_p, paras_b = list(body_p.iter(q('p'))), list(body_b.iter(q('p')))
    r = {}
    r['段数守恒'] = len(paras_p) == len(paras_b)
    r['oMath树级守恒'] = om_count(body_p) == om_count(body_b) == OM_BASE[k]
    n_chip = n_chip_nowj = n_chip_bak = n_chip_big = 0
    for t in body_p.iter(q('t')):
        txt = t.text or ''
        if '【' not in txt:
            continue
        for mch in CHIP_LOOSE.finditer(txt):
            inner = len(mch.group(0)[1:-1].replace(WJ, ''))
            if inner > 16:
                n_chip_big += 1
                continue
            n_chip += 1
            if WJ not in mch.group(0):
                n_chip_nowj += 1
    for t in body_b.iter(q('t')):
        txt = t.text or ''
        if '【' in txt:
            for mch in CHIP_LOOSE.findall(txt):
                if len(mch[1:-1]) <= 16:
                    n_chip_bak += 1
    r['芯片全WJ'] = n_chip_nowj == 0
    r['芯片数=基线'] = n_chip == BASE_A[k] == n_chip_bak
    add_total = add_sec = add_lect = add_grp = add_om_short = add_other = add_om_long = 0
    legacy_long_kl = 0
    for pp, pb in zip(paras_p, paras_b):
        if has_kl(pp) and not has_kl(pb):
            add_total += 1
            kd = title_kind(pp)
            if kd == '节':
                add_sec += 1
            elif kd == '讲部':
                add_lect += 1
            elif kd == '题型':
                add_grp += 1
            elif list(pp.iter(qm('oMath'))):
                if eff_len(ptext(pp)) > OM_SHORT_LIMIT:
                    add_om_long += 1
                else:
                    add_om_short += 1
            else:
                add_other += 1
        elif has_kl(pp) and has_kl(pb) and list(pp.iter(qm('oMath'))) and eff_len(ptext(pp)) > OM_SHORT_LIMIT:
            legacy_long_kl += 1
    r['新增挂载=全类分账'] = (add_total == add_sec + add_lect + add_grp + add_om_short)
    r['无意外挂载'] = add_other == 0
    r['新增挂载账'] = (add_sec, add_lect, add_grp, add_om_short) == \
                 (BASE_B_SEC[k], BASE_B_LECT[k], BASE_B_GRP[k], BASE_C_NEW[k])
    r['长段零新增挂载'] = add_om_long == 0

    def texts(body):
        return [''.join((t.text or '').replace(WJ, '') for t in p.iter(q('t'))) for p in body.iter(q('p'))]
    r['文本守恒(去WJ)'] = texts(body_p) == texts(body_b)
    r['部件MD5全等'] = all(v == parts_b.get(k2) for k2, v in parts_p.items() if k2 != 'word/document.xml') \
                  and set(parts_p) - {'word/document.xml'} == set(parts_b) - {'word/document.xml'}
    allok = all(v for kk, v in r.items())
    ok_probe = ok_probe and allok
    probe_rows.append('%-6s 芯片%d(无WJ %d，>16字豁免%d) 新增挂载 节%d/讲部%d/题型%d/短公式%d｜长段新增 %d(T8遗留长段kl %d)｜%s'
                      % (SHORT[k], n_chip, n_chip_nowj, n_chip_big, add_sec, add_lect, add_grp, add_om_short,
                         add_om_long, legacy_long_kl, 'ALL PASS' if allok else
                         'FAIL:' + ','.join(kk for kk, v in r.items() if not v)))
    say('  ' + probe_rows[-1])

say('=== ⑤ 汇总 ===')
ALLOK = ok_exec and ok_om and ok_idem and ok_probe
say('SUMMARY ALLOK=%s (exec=%s oMath=%s idem=%s probe=%s)' % (ALLOK, ok_exec, ok_om, ok_idem, ok_probe))
with open(os.path.join(RPT, '②D_R2_T9_断言.md'), 'w', encoding='utf-8') as f:
    f.write('# ②D 重跑轮 T9 断言（exec 对平＋oMath 守恒＋幂等＋独立 XML 探针；基态＝②-F 修复态）\n\n```text\n' + '\n'.join(OUT) + '\n```\n')
sys.exit(0 if ALLOK else 2)
