# -*- coding: utf-8 -*-
"""②C_07_T6c_exec.py — T6c 正式执行（衔接件解析块界定清灰 --xj-clear）于 ②工具/副本 十件。
七道关：
  ①exec 剥除数断言：衔接1＝71（基线 71，差 0）；衔接2＝595（基线 649，差 54＝答案行6＋答案值续段42＋知识点行6，
    全部受保护、可解释）；讲练件六件 复核＝0（不剥）；清单件两件 审计登记 0、零改写。
  ②独立分区复算（②C_04 探针机）：剥后解析区 rPr C9C9C9＝0；答案区/知识点区/题干区/条目区 前＝后（零触碰）。
  ③全件 rPr C9C9C9 守恒：前＝后＋剥；pPr/tcPr 级 fill 分布前＝后。
  ④幂等 dry 二跑（--xj-clear）全 0；默认模式 dry 审计回落＝块外保护值（54/0）。
  ⑤文本守恒 strict＋norm＋非 document.xml 部件全等（②C_文本守恒.py）。
  ⑥docxml 指纹：仅衔接件两件被改写，其余八件字节不动。
  ⑦零残留 rPr C9C9C9 于解析区（与②同源双证）。
落 报告/②C_T6c_exec.md"""
import sys, io, os, re, time, subprocess, importlib.util, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
RPT = os.path.join(HERE, '报告', '②C_T6c_exec.md')
TOOL = os.path.join(ROOT, '工具', '底纹批量器.py')

spec = importlib.util.spec_from_file_location('t6guard', os.path.join(HERE, '②C_文本守恒.py'))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)

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
SHORT = ['清单1', '衔接1(29)', '上(61)', '下(79)', '清单2', '衔接2(13)', '92', '90', '68', '89']
KIND = ['清单', '衔接', '讲练', '讲练', '清单', '衔接', '讲练', '讲练', '讲练', '讲练']
BASE = {'衔接1(29)': 71, '衔接2(13)': 649}          # ②-C 登记基线（粘滞审计口径）
EXPECT_STRIP = {'衔接1(29)': 71, '衔接2(13)': 595}   # 块界定实清预期

W = G.q('W') if hasattr(G, 'q') else None
NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (NS, t)
def tag(e): return etree.QName(e).localname

NUM = r'(?:\d+(?:\.\d+)+-\d+|\d+)'
QBLOCK_RE = re.compile(r'^%s．（' % NUM)
ENTRY_RE = re.compile(r'^%s．' % NUM)
TITLE_RE = re.compile(r'^\d+(?:\.\d+)+[\s　]')
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*(?:方法讲解|知识讲解)[｜|]')
KNOWVAL_RE = re.compile(r'^\d+(?:\.\d+)*[\s　]+\S')
ANA_RE = re.compile(r'【(?:分析|详解|点睛|编注)】')
LBL_ANS = re.compile(r'【答案】')
LBL_KNOW = re.compile(r'【知识点】')


def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))


def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None


def has_bar18(p):
    ppr = p.find(q('pPr'))
    if ppr is None: return False
    pb = ppr.find(q('pBdr'))
    if pb is None: return False
    lf = pb.find(q('left'))
    return lf is not None and lf.get(q('sz')) == '18'


def regions(path):
    """独立分区复算（②C_04 探针机）：逐区 rPr C9C9C9 合计＋全件 rPr/pPr/tcPr 级 fill 计数。"""
    z = zipfile.ZipFile(path)
    try:
        doc = etree.fromstring(z.read('word/document.xml'))
    finally:
        z.close()
    agg = {}
    dist = {}
    for shd in doc.iter(q('shd')):
        k = (tag(shd.getparent()), (shd.get(q('fill')) or '').upper())
        dist[k] = dist.get(k, 0) + 1

    def rc9(p):
        n = 0
        for shd in p.iter(q('shd')):
            if tag(shd.getparent()) == 'rPr' and (shd.get(q('fill')) or '').upper() == 'C9C9C9':
                n += 1
        return n

    els = list(doc.find(q('body')))
    region = None; ana_open = False; know_val_pending = False
    for c in els:
        if c.tag != q('p'):
            region = None; ana_open = False; know_val_pending = False
            continue
        t = ptext(c); f = pfill(c)
        is_title = (TITLE_RE.match(t) and (f in ('ADC2DA', 'C6D4E3') or LECT_RE.match(t) or has_bar18(c)))
        if is_title:
            region = '标题'; ana_open = False; know_val_pending = False
        elif QBLOCK_RE.match(t):
            region = '题干区'; ana_open = False; know_val_pending = False
        elif ENTRY_RE.match(t):
            region = '条目区'; ana_open = False; know_val_pending = False
        elif region not in (None, '标题', '条目区'):
            if ANA_RE.search(t):
                region = '解析区'; ana_open = True; know_val_pending = False
            elif LBL_ANS.search(t):
                region = '答案区'; know_val_pending = False
            elif LBL_KNOW.search(t):
                region = '知识点区'; know_val_pending = True
            elif region == '知识点区':
                if know_val_pending and KNOWVAL_RE.match(t):
                    know_val_pending = False
                else:
                    region = '解析区' if ana_open else '知识点区余'
                    know_val_pending = False
        agg[region] = agg.get(region, 0) + rc9(c)
    return agg, dist


def run(args, tries=4, timeout=600):
    for att in range(1, tries + 1):
        try:
            p = subprocess.run(['python', TOOL] + args, capture_output=True, text=True,
                               encoding='utf-8', timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            print('    timeout att%d' % att, flush=True); time.sleep(15); continue
        if p.returncode == 0 and 'Traceback' not in (p.stderr or ''):
            return p.stdout.strip()
        print('    fail att%d rc=%d %s' % (att, p.returncode, (p.stderr or '')[-300:]), flush=True)
        time.sleep(15)
    return None


rows, raws = [], []
allok = True
for i, n in enumerate(NAMES):
    f = os.path.join(DST, n)
    print('=== [%d/10] %s ===' % (i + 1, SHORT[i]), flush=True)
    pre = G.snap(f)
    agg_pre, dist_pre = regions(f)
    out = run([f, '--only', 'c', '--xj-clear'])
    if out is None:
        allok = False; rows.append((SHORT[i], 'RUNFAIL')); continue
    raws.append(out)
    post = G.snap(f)
    agg_post, dist_post = regions(f)
    # 工具输出解析
    m = re.search(r'解析区剥除 (\d+) 处（解析区段 (\d+) 段）｜对平＝粘滞审计 (\d+) − 块外保护 (\d+)（([^）]*)）', out)
    m2 = re.search(r'讲练件题目侧复核＝(\d+) (\w+)', out)
    m3 = re.search(r'审计（非讲练件不剥，附则适用面）：(\d+) 处登记', out)
    if KIND[i] == '衔接':
        strip, anap, sticky, prot, bd = (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                                         int(m.group(4)), m.group(5)) if m else (-1,) * 5
    else:
        strip = anap = sticky = prot = 0
        bd = '-'
    jl_fu = int(m2.group(1)) if m2 else None
    audit = int(m3.group(1)) if m3 else None
    # 断言组
    if KIND[i] == '衔接':
        c_base = (BASE[SHORT[i]] == sticky and EXPECT_STRIP[SHORT[i]] == strip
                  and sticky - strip == prot and prot >= 0)
        c_zero = (agg_post.get('解析区', 0) == 0)
        c_touch = all(agg_post.get(k, 0) == agg_pre.get(k, 0)
                      for k in ('答案区', '知识点区', '题干区', '条目区', '标题'))
        rpr_pre = sum(v for (lv, fl), v in dist_pre.items() if lv == 'rPr' and fl == 'C9C9C9')
        rpr_post = sum(v for (lv, fl), v in dist_post.items() if lv == 'rPr' and fl == 'C9C9C9')
        c_cons = (rpr_pre == rpr_post + strip)
        c_nonrpr = ({k: v for k, v in dist_pre.items() if k[0] != 'rPr'} ==
                    {k: v for k, v in dist_post.items() if k[0] != 'rPr'})
    else:
        if KIND[i] == '讲练':
            c_base = (strip == 0 and jl_fu == 0)
        else:  # 清单
            c_base = (strip == 0 and audit == 0)
        c_zero = True
        c_touch = (agg_pre == agg_post)
        rpr_pre = sum(v for (lv, fl), v in dist_pre.items() if lv == 'rPr' and fl == 'C9C9C9')
        rpr_post = sum(v for (lv, fl), v in dist_post.items() if lv == 'rPr' and fl == 'C9C9C9')
        c_cons = (rpr_pre == rpr_post + strip)
        c_nonrpr = (dist_pre == dist_post)
    # 幂等：--xj-clear dry 二跑（按件类解析剥除数）
    idem = []
    for _ in range(2):
        o = run([f, '--only', 'c', '--xj-clear', '--dry-run'])
        v = -1
        if o:
            if KIND[i] == '衔接':
                mm = re.search(r'解析区剥除 (\d+) 处', o)
                v = int(mm.group(1)) if mm else -1
            elif KIND[i] == '讲练':
                mm = re.search(r'剥除：(\d+) 处', o)
                v = int(mm.group(1)) if mm else -1
            else:
                mm = re.search(r'：(\d+) 处登记', o)
                v = int(mm.group(1)) if mm else -1
        idem.append(v)
    c_idem = all(v == 0 for v in idem)
    # 默认模式 dry（审计回落）
    o_def = run([f, '--only', 'c', '--dry-run'])
    mm3 = re.search(r'审计（非讲练件不剥，附则适用面）：(\d+) 处登记', o_def or '')
    audit_def = int(mm3.group(1)) if mm3 else (0 if (o_def and '复核＝0' in o_def) else -1)
    if KIND[i] == '衔接':
        c_auditfall = (audit_def == prot)
    else:
        c_auditfall = (audit_def == 0)
    # 守恒＋指纹
    cmp = G.compare(pre, post)
    c_txt = cmp['strict'] and cmp['norm']
    c_doc = (cmp['docxml_changed'] == (strip > 0))
    ok = c_base and c_zero and c_touch and c_cons and c_nonrpr and c_idem and c_auditfall and c_txt and c_doc
    allok = allok and ok
    print('  剥%d 对平%d−%d(%s) %s｜解析区残留%d %s｜保护区前=%s 后=%s %s'
          % (strip, sticky, prot, bd, 'PASS' if c_base else '!!FAIL',
             agg_post.get('解析区', 0), 'PASS' if c_zero else '!!FAIL',
             {k: v for k, v in agg_pre.items()}, {k: v for k, v in agg_post.items()},
             'PASS' if c_touch else '!!FAIL'), flush=True)
    print('  rPr C9 %d→%d(剥%d) %s｜非rPr分布同 %s｜幂等dry%s %s｜默认审计回落%d %s｜守恒 %s/%s %s｜docxml改%s %s'
          % (rpr_pre, rpr_post, strip, 'PASS' if c_cons else '!!FAIL',
             'PASS' if c_nonrpr else '!!FAIL', idem, 'PASS' if c_idem else '!!FAIL',
             audit_def, 'PASS' if c_auditfall else '!!FAIL',
             cmp['strict'], cmp['norm'], 'PASS' if c_txt else '!!FAIL',
             cmp['docxml_changed'], 'PASS' if c_doc else '!!FAIL'), flush=True)
    rows.append((SHORT[i], KIND[i], 'PASS' if ok else '!!FAIL', strip, anap, sticky, prot, bd,
                 rpr_pre, rpr_post, idem, audit_def, agg_pre, agg_post, cmp,
                 c_base, c_zero, c_touch, c_cons, c_nonrpr, c_idem, c_auditfall, c_txt, c_doc))

with open(RPT, 'w', encoding='utf-8') as fh:
    fh.write('# ②C T6c 正式执行报告 — 衔接件解析块界定清灰（--xj-clear）\n\n')
    fh.write('- 时点：%s\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
    fh.write('- 工具：`工具\\底纹批量器.py --only c --xj-clear`（本轮新增开关，默认关、仅衔接件生效）\n')
    fh.write('- 对象：`②工具\\副本\\` 十件（T6a/T6b 已执行态；起点＝同步盘 ②-B 回写终态）\n')
    fh.write('- 基线：`②工具对账.md` §二 T6c 行＝衔接件审计登记 71（29题）／649（13题）处、讲练件六件 0；'
             '本轮开关后块界定实清＝衔接1 **71**（与基线差 0）／衔接2 **595**（与基线差 54，见对平账）。\n')
    fh.write('- 口径定案：解析块＝题号块内自首个【分析|详解|点睛|编注】段起（含解析已开后知识点值段之后的'
             '无标签详解公式段），至【答案】/【知识点】行或题块边界止；【答案】行及其值续段、【知识点】行及其'
             '值段、题号块行、题干续段、条目区一律保护。口径侦察三件：`②C_04_解析块分区探针.py`、'
             '`②C_05_口径对平侦察.py`、`②C_06_衔接2差集明细.py`（本轮落盘留档）。\n\n')
    fh.write('## 一、七道关逐件结果\n\n')
    fh.write('| 件 | 类 | 剥除（解析区段数） | 对平（粘滞−保护） | 基线断言 | 解析区残留 | 保护区零触碰 | rPr C9 前→后 | 非rPr分布 | 幂等dry×2 | 默认审计回落 | 文本守恒 | docxml指纹 | 判定 |\n')
    fh.write('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        if r[1] == 'RUNFAIL':
            fh.write('| %s | — | — | — | — | — | — | — | — | — | — | — | — | !!RUNFAIL |\n' % r[0])
            continue
        (sh, kd, st, strip, anap, sticky, prot, bd, rpre, rpost, idem, adef, agp, agq, cmp,
         c1, c2, c3, c4, c5, c6, c7, c8, c9) = r
        if kd == '衔接':
            fh.write('| %s | %s | %d（%d 段） | %d−%d=%d（%s） | %s | %d %s | 前=%s 后=%s %s | %d→%d %s | %s | %s%s %s | %d %s | %s/%s %s | 改=%s %s | %s |\n' % (
                sh, kd, strip, anap, sticky, prot, sticky - prot, bd,
                'PASS' if c1 else '**FAIL**', agq.get('解析区', 0), 'PASS' if c2 else '**FAIL**',
                {k: v for k, v in agp.items() if k in ('答案区', '知识点区', '题干区', '条目区')},
                {k: v for k, v in agq.items() if k in ('答案区', '知识点区', '题干区', '条目区')},
                'PASS' if c3 else '**FAIL**', rpre, rpost, 'PASS' if c4 else '**FAIL**',
                'PASS' if c5 else '**FAIL**', idem[0], idem[1], 'PASS' if c6 else '**FAIL**',
                adef, 'PASS' if c7 else '**FAIL**', cmp['strict'], cmp['norm'],
                'PASS' if c8 else '**FAIL**', cmp['docxml_changed'], 'PASS' if c9 else '**FAIL**', st))
        else:
            fh.write('| %s | %s | 0 | − | %s | − | 前=后 %s | − | %s | %s%s %s | %d %s | %s/%s %s | 改=%s %s | %s |\n' % (
                sh, kd, 'PASS' if c1 else '**FAIL**', 'PASS' if c3 else '**FAIL**',
                'PASS' if c5 else '**FAIL**', idem[0], idem[1], 'PASS' if c6 else '**FAIL**',
                adef, 'PASS' if c7 else '**FAIL**', cmp['strict'], cmp['norm'],
                'PASS' if c8 else '**FAIL**', cmp['docxml_changed'], 'PASS' if c9 else '**FAIL**', st))
    fh.write('\n### 断言口径说明\n\n')
    fh.write('- **基线断言**：衔接件＝登记基线（粘滞审计 71/649）＝粘滞复算，且块界定实清（71/595）＝粘滞−块外保护；'
             '讲练件＝复核剥除 0（题目侧 C9C9C9 已 0，T6c 零触碰）；清单件＝审计登记 0 且零改写。\n')
    fh.write('- **对平账（衔接2 差 54 构成）**：粘滞口径（②-C 登记基线同口径）把题块内首个【分析】之后的全部段落'
             '计入，其中【答案】行 6 段×1 处、【知识点】行 6 段×1 处、答案值续段 9 段×42 处共 54 处，'
             '按硬断言「答案行/题号块零触碰」与块界定（值续段属答案区非解析块）受保护不剥：649−54＝595。'
             '衔接1 差 0（其布局答案/知识点先于解析，粘滞口径与块界定天然重合）。\n')
    fh.write('- **独立分区复算**＝②C_04 探针机（与工具实现互为独立）：剥后解析区 rPr C9C9C9＝0；'
             '答案区/知识点区/题干区/条目区/标题 前＝后。\n')
    fh.write('- **非rPr分布**＝pPr/tcPr 级全部 fill 计数前＝后（T6c 只删 rPr 级 shd）。\n')
    fh.write('- **幂等 dry×2**＝--xj-clear dry 连跑两次均剥 0（不动点）。\n')
    fh.write('- **默认审计回落**＝exec 后默认模式（无开关）dry 的粘滞审计值＝块外保护值（衔接2 54／衔接1 0），'
             '讲练件/清单件＝0——证剥除恰为解析区、块外灰底全部仍在。\n')
    fh.write('- **文本守恒**＝strict＋norm＋非 document.xml 部件 MD5 全等（②C_文本守恒.py）；'
             '**docxml 指纹**＝改动件恰为衔接件两件，其余八件字节不动。\n\n')
    fh.write('## 二、逐件工具原始输出\n\n')
    fh.write('\n'.join(raws) + '\n\n')
    fh.write('## 三、结论\n\n')
    fh.write('%s\n' % ('**十件全绿**：衔接件两件按块界定实清 71/595（对平基线 71/649，差 54 全部受保护可解释），'
                       '讲练件六件复核＝0 零触碰、清单件两件零改写；解析区剥后零残留（独立复算双证）、'
                       '保护区零触碰、非 rPr 级零扰动、幂等 dry 二跑全 0、文本守恒零差异、'
                       '仅衔接件两件 docxml 变动。T6c 通过。'
                       if allok else '**存在未通过项**，见上表 FAIL 标记，T6c 不得放行。'))
print('REPORT ->', RPT, flush=True)
print('SUMMARY allok=%s' % allok, flush=True)
