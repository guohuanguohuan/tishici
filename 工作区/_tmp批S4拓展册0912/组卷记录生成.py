# -*- coding: utf-8 -*-
"""S4 拓展册：由 总底表.ROWS ＋ tex 标记 生成 上册.md／下册.md 组装记录 与 值台账.md 初稿。
组装记录每题一行：拓号｜域｜组｜难度｜源号｜图位（文件×宽／占位／无图）｜注记（转写/并置/占位/救回/答案册侧义务）。
值台账：拓号→qisuan_dump.ans 截要；缺者标「答案册轮提取」。"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 总底表 import ROWS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r'C:/提示词/工作区/M2-第1章量产0911/成卷/拓展册'

# ── tex 图位标记抽取 ──
def tex_marks(vol):
    p = os.path.join(OUT, vol, 'main.tex')
    txt = open(p, encoding='utf-8').read()
    marks = []  # (拓号, kind, payload) 顺序流
    cur = None
    for m in re.finditer(r'\\tihao\{(\d+)\}|\\tu\{([^}]+)\}\{([^}]+)\}|\\tuzhan\{([^}]+)\}|\\bingzhi\{([^}]+)\}', txt):
        if m.group(1):
            cur = int(m.group(1))
        elif m.group(2):
            marks.append((cur, 'tu', '%s×%s' % (m.group(2), m.group(3))))
        elif m.group(4):
            marks.append((cur, 'tuzhan', m.group(4)))
        elif m.group(5):
            marks.append((cur, 'bingzhi', m.group(5)))
    return marks

# ── 解析段救回登记（抽图.py manifest 核实）──
RESCUE = {40: '单元5·e231', 59: '讲上·e1080', 67: '讲上·e1361',
          70: '讲上·e1468+e1469（双图）', 98: '讲下·e784', 118: '讲下·e653'}

# ── 题面转写登记（tex 头注同款）──
ZXW = {59: '题面两处【图】补全「直三棱柱ABC−A₁B₁C₁」「A₁C」（定稿C§3.4）',
       71: 'DABE→△ABE／DA₁BE→△A₁BE（希腊→拉丁已落）',
       107: 'PA/PB/PC 补全＋选项D＝√3/3π（定稿C§3.4 目验值）',
       116: '原图数据文字化（直径3、母线3、棱长a；选项A=1/B=√2/C=√3/D=2），不须原图',
       136: '问句脱文补「则该圆锥的体积为」（对照源件；清稿§二-2）',
       41: '平面MBD⊥平面PCD 文字化（两小图目验确读）；面／点位名称脱字待裁（清稿注）'}

# 底表注记与转写重文时以转写为准，此处裁剪底表注
NOTE_OVERRIDE = {59: None, 71: '双图（图1 图2）', 41: None}

def build(vol, lo, hi):
    marks = tex_marks(vol)
    by_t = {}
    for t, k, v in marks:
        by_t.setdefault(t, []).append((k, v))
    L = []
    L.append('# 拓展册·%s 组装记录（拓-%03d～%03d）' % (vol, lo, hi))
    L.append('')
    L.append('- 成品：`成卷/拓展册/%s/`（main.tex＋qp-*.tex 六宏＋figs/＋main.pdf＋png/＋render.py）' % vol)
    L.append('- 题面冻结源：`成卷/题面库/拓展册.md`；难度/域/组照 `工作区/_tmp批S4拓展册0912/总底表.py`')
    L.append('- 本表兼「成品号↔源号」映射表（排产单 §2.2 规则6）；组名为候选名，待立组轮正名')
    L.append('- 版式：练习线局部层；新宏 \\zu（组行＋候选名灰注）、\\tu、\\tuzhan、\\bingzhi、\\nao（臑字 SimSun 回退）')
    L.append('')
    L.append('拓号｜域｜组｜难度｜源号｜图位｜注记')
    L.append('|---|---|---|---|---|---|---|')
    for r in ROWS:
        t, dom, grp, dif, src, tsrc, note = r
        if not (lo <= t <= hi):
            continue
        cells = ['%03d' % t, dom, grp, dif, src]
        # 图位
        mk = by_t.get(t, [])
        fus = [v for k, v in mk if k == 'tu']
        zh = [v for k, v in mk if k == 'tuzhan']
        if fus:
            figs = '；'.join(fus)
        elif zh:
            figs = '占位：' + zh[0]
        else:
            figs = '无图'
        cells.append(figs)
        # 注记
        notes = []
        if t in ZXW:
            notes.append('转写：' + ZXW[t])
        note_eff = NOTE_OVERRIDE.get(t, note) if note else note
        has_bz = bool(note_eff and '并置' in note_eff)
        for k, v in mk:
            if k == 'bingzhi':
                if has_bz:
                    note_eff = re.sub(r'(并置：主件[^；）]*)）', r'\1；答案册同页排放）', note_eff)
                else:
                    notes.append('并置件，主件' + v + '（答案册同页排放）')
        if t in RESCUE:
            notes.append('解析段救回图：' + RESCUE[t])
        if note_eff:
            notes.append(note_eff)
        cells.append('；'.join(notes) if notes else '—')
        L.append('| ' + ' | '.join(cells) + ' |')
    L.append('')
    return '\n'.join(L)

# ── 值台账 ──
# 亲算档指针键无 ans 的 13 题：由亲算 md 原档段落手工提取（组卷记录生成时逐段核对）
ANS_OVERRIDE = {
    1: ('C（①③⑤真；②④假）', '亲算-1.1.1-b.md§一F7·4'),
    8: ('D（θ=arccos(1/4)≈75.5°，非特殊角）', '亲算-1.1.1-b.md§一F2·23'),
    11: ('C（系数和 11−6−4=1 ⟹ M∈平面 BA₁D₁）', '亲算-1.1.2.md§P11'),
    12: ('(1)(2)(3) 证毕；(3) OM=(1/4)(OA+OB+OC+OD)', '亲算-1.1.2.md§P12'),
    15: ('A（AM·MN=−4/3）', '亲算-1.1.2.md§P14'),
    18: ('八点坐标：F(0,0,0)／A(0,4,0)／B(−3,0,0)／C(3,0,0)／A₁(0,4,5)／B₁(−3,0,5)／C₁(3,0,5)／E(3,0,5/2)', '亲算-1.1.3-a.md§E3'),
    21: ('A（P=(1,1,−1)，|OP|=√3）', '亲算-1.1.3-a.md§T6'),
    22: ('D（2√14；A′=(3,3,−1)）', '亲算-1.1.3-b.md§E13'),
    25: ('λ=3（双根 −2 由 λ>0 舍）', '亲算-1.1.3-a.md§E9'),
    27: ('B（λ=−√6/6）', '亲算-1.1.3-a.md§T5'),
    28: ('(1) 证毕；(2) √30/15；(3) √22/3', '亲算-1.1.3-a.md§E1'),
    30: ('B（x=1/2，y=−4）', '亲算-1.1.3-b.md§E15'),
    34: ('A（[√6/2, √2]）', '亲算-1.1.3-a.md§T10'),
}
# 钉值门 5 题亲算复核（本卷排版轮独立重算，对照台账值）
DINGZHI = (
    (34, '正方体 A₁P⊥AC₁ ⟹ P 在底面对角线 AC 上；|A₁P|²=2(x−½)²+3/2 ⟹ [√6/2,√2]，选A', '台账一致 ✓'),
    (72, '直二面角折叠：AD∩BC=60°（A✗）；AC⊥BD（B✓）；BC∩面ACD 正弦 = √6/3（C✗，坐标＋等体积两法）；面ABC∩面BCD tan=√2（D✓）⟹ BD', '台账一致 ✓（C 支值 √6/3 两法复核）'),
    (78, 'V=(√3/6)AD²=2√3/3 ⟹ AD=2；建系 PMB∩SAD 锐二面角：3t²+2t−1=0 ⟹ t=1/3，M 存在且 AM=⅓AS', '台账一致 ✓'),
    (96, '菱形 ∠A=60°，a=4√3 ⟹ OB=2√3、OP=OC=6、∠POC=120°；球心 (0,2,2√3)，R²=28（P/B/C 三点等距验）⟹ 112π，选D', '台账一致 ✓'),
    (136, '展开 2√13=√(40−24cosα) ⟹ α=2π/3；r=lα/2π=2，h=4√2 ⟹ V=16√2π/3，选C', '台账一致 ✓'),
)

def key_for(src, dom, D, m125):
    """源号→亲算档键；返回 (键, 备注疑义)；无键返回 (None, 原因)。"""
    m = re.match(r'^池-(\d+)$', src)
    if m:
        n = m.group(1)
        if dom == '1.2.5' and n in m125:
            return m125[n], ''
        bare = [k for k in D if re.match(r'^%s\.[\d.]+-%s$' % (dom, n), k)]
        if bare:
            return bare[0], '' if len(bare) == 1 else '多候选取首'
        ann = [k for k in D if re.match(r'^%s\.[\d.]+-%s（' % (dom, n), k)]
        if ann:
            return ann[0], '键带注记'
        return None, '亲算档无此池键'
    m = re.match(r'^池(1\.\d[\d.]*\d)-(\d+)$', src)
    if m:
        cands = [k for k in D if re.match(r'^%s-%s$' % (m.group(1), m.group(2)), k)]
        return (cands[0], '') if cands else (None, '亲算档无此池键')
    m = re.match(r'^池T(\d+)$', src)
    if m:
        cands = [k for k in D if k.startswith('T%s｜' % m.group(1))]
        return (cands[0], '') if cands else (None, '亲算档无此池键')
    m = re.match(r'^(F\d+·\d+)$', src)
    if m:
        cands = [k for k in D if re.match(r'^%s(（|$)' % re.escape(src), k)]
        if cands:
            note = '' if len(cands) == 1 else '双键取并'
            return cands[-1], note
        cands = [k for k in D if re.search(r'外源\s*%s\b' % re.escape(src), k)]
        return (cands[0], '经外源键') if cands else (None, '亲算档无此 F 键')
    return None, '教材题/导p36，答案册轮提取'

def ledger():
    D = json.load(open(os.path.join(HERE, 'qisuan_dump.json'), encoding='utf-8'))
    m125 = json.load(open(os.path.join(HERE, 'map125.json'), encoding='utf-8'))
    L = []
    L.append('# 拓展册·值台账（160 题）')
    L.append('')
    L.append('- 答案值源：`工作区/_tmp批S4拓展册0912/qisuan_dump.json`（亲算档挖掘）')
    L.append('- 键配规则：池-N（1.2.4/1.2.5）按 `域.槽-池题号` 全串锚定（1.2.5 以 map125.json 权威映射）；池域题（1.2.1～1.2.3）按源号自带前缀锚定；池T# 按「T#｜池题」键；F 系列按「F#·#」直配，缺者经 P#/E# 外源键回配')
    L.append('- 钉值门抽 5 题亲算复核：拓-034／072／078／096／136（跨域抽样，见文末）')
    L.append('- 亲算档指针键无 ans 的 13 题（拓-001/008/011/012/015/018/021/022/025/027/028/030/034）由亲算 md 原档段落手工提取，出处见行尾')
    L.append('- 教材题（复习题／习题／节练习）与 导-P2／p36⑩⑫ 亲算档未挖掘，标「答案册轮提取」（答案册排版轮履行）')
    L.append('')
    L.append('拓号｜域｜源号｜答案值（截要）｜备')
    L.append('|---|---|---|---|---|')
    miss = []
    for r in ROWS:
        t, dom, grp, dif, src, tsrc, note = r
        if t in ANS_OVERRIDE:
            a1, prov = ANS_OVERRIDE[t]
            a1 = a1.replace('|', '｜')
            L.append('| %03d | %s | %s | %s | 亲算档 `%s` 段落提取' % (t, dom, src, a1, prov))
            continue
        k, flag = key_for(src, dom, D, m125)
        if k:
            a = re.sub(r'\s+', ' ', D[k].get('ans', '')).strip()
            if not a:
                L.append('| %03d | %s | %s | （答案册轮提取） | 键 `%s` 无 ans 值' % (t, dom, src, k))
                miss.append(t)
                continue
            a1 = a[:80] + ('…' if len(a) > 80 else '')
            a1 = a1.replace('|', '｜')
            tail = ('（键 `%s`%s）' % (k, '；' + flag if flag else '')) if len(k) <= 46 else ('（键 `%s…`%s）' % (k[:44], '；' + flag if flag else ''))
            L.append('| %03d | %s | %s | %s | %s' % (t, dom, src, a1, tail))
        else:
            L.append('| %03d | %s | %s | （答案册轮提取） | %s' % (t, dom, src, flag))
            miss.append(t)
    L.append('')
    L.append('## 钉值门·亲算复核 5 题（拓-034／072／078／096／136，本卷排版轮独立重算）')
    L.append('')
    for t, calc, verdict in DINGZHI:
        row = [x for x in ROWS if x[0] == t][0]
        L.append('- **拓-%03d**（%s，%s）：%s —— %s' % (t, row[1], row[4], calc, verdict))
    L.append('')
    L.append('## 缺值清单（%d 题，答案册轮提取）' % len(miss))
    L.append('')
    L.append('、'.join('%03d' % t for t in miss))
    L.append('')
    return '\n'.join(L)

if __name__ == '__main__':
    open(os.path.join(OUT, '上册.md'), 'w', encoding='utf-8').write(build('上册', 1, 58))
    open(os.path.join(OUT, '下册.md'), 'w', encoding='utf-8').write(build('下册', 59, 160))
    open(os.path.join(OUT, '值台账.md'), 'w', encoding='utf-8').write(ledger())
    print('上册.md / 下册.md / 值台账.md 已写出')
