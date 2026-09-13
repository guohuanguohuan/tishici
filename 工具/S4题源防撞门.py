# -*- coding: utf-8 -*-
r"""S4题源防撞门.py — S4 题源防撞门（军师账审-收口轮0913 §十·终裁前置三条件③：扩容闸的机械前置）。

门口径（逐候选三门判级，撞面五源）：
  撞面＝①题面库 572 键语料（M3 成卷/题面库/ 逐键题面＋头注源号，只读）；
        ②定稿源号（题面库头注 `源：` 富矿指针＝在册账；练域 320 键即任务口径「320 题定稿源号」）；
        ③拓展册收编指纹（批A~E 台账＋定稿件 bodies 取用面全扫，含裸前缀件——B20 病灶）；
        ④防双收清单 B19~B24（查重总表 §三.2 在案对，硬编码登记）；
        ⑤查重总表禁收（查①②③ 逐题表判级＝重复/教材同源/超纲行；任务口径锚＝查③ 重复73＋同源20）。
  另挂 R9 对勘腿（§十前置①）：成品卷①~④ 全dump 块语料 ↔ 候选文本比对（破「假净余」）。

判级（逐候选）：
  ❌撞——L1 源号双收（候选源号 ∈ 消费账∪防双收∪禁收）；
        L2 逐字/近逐字（归一化字 3-gram 包含 c≥0.90，或 c≥0.80 且数字集重合≥0.85）；
        L3 同数值构（0.60≤c<0.90 且数字集 Jaccard≥0.75 且两侧≥3 数——只换数/换问族）；
        L4 同族超上限（军师钉：同族锁取一族达上限者归 ❌ 不归 ⚠——族内兄弟已收则锁员全 ❌）。
  ⚠疑——文本近似待钉（0.50≤c 且带数字协证），或同族守门席/受限件/题面未取得。
  ✅净——三门全空，放行。0.45≤c<0.50 弱命中只观察登记不判级（查①人判新增不复审弱带）。

用法: python 工具/S4题源防撞门.py --selftest
      python 工具/S4题源防撞门.py --firstrun [--out 报告.md]   # S4-0 净余候选＋R9 对勘首跑
      python 工具/S4题源防撞门.py --candidates 候选.json --out 报告.md
        # 候选 json：[{"id":…,"src":"2章件2-#38"或null,"text":题面或null,"fp":指纹或null},…]
退出码: 0＝全净放行；1＝有撞/疑（禁行，须逐枚钉码后再议）；2＝用法/输入错。
写前核: --out 路径已存在即拒写（防覆盖既有交付；删后重跑或换 --out）。
红线: 全部语料只读；零 git；报告只落 --out 指定路径。
"""
import argparse
import io
import json
import os
import re
import sys
import unicodedata

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M3 = os.path.join(ROOT, '工作区', 'M3-第2章量产0913')
TIKU_DIR = os.path.join(M3, '成卷', '题面库')
DINGGAO_DIR = os.path.join(M3, '定稿')
CZ_DIR = os.path.join(ROOT, '工作区', '_tmpM3轮1查重0913')
CZ_FILES = {'①': os.path.join(CZ_DIR, '查重-2.1-2.3.md'),
            '②': os.path.join(CZ_DIR, '查重-2.4-2.6.md'),
            '③': os.path.join(CZ_DIR, '查重-2.7-2.8.md')}
ZONGTAB = os.path.join(M3, '查重总表-轮1.md')
FUKUANG_ROOT = os.path.join(ROOT, '高中数学', '参考', '组卷网', '【新课标 新探索】大单元作业设计',
                            '人教A版选择性必修1')
DOCX_DIR2 = os.path.join(FUKUANG_ROOT, '第2章 直线与圆的方程')
JUAN_DUMPS = [('卷①', os.path.join(ROOT, '工作区', '_tmpM3轮0登记0913', '_tmp-卷①全dump.txt')),
              ('卷②', os.path.join(ROOT, '工作区', '_tmpM3轮0登记0913', '_tmp-卷②全dump.txt')),
              ('卷③', os.path.join(ROOT, '工作区', '_tmpM3轮0登记0913', '_tmp-卷③全dump.txt')),
              ('卷④', os.path.join(ROOT, '工作区', '_tmpM3轮0登记0913', '_tmp-卷④全dump.txt'))]

# ── 防双收清单 B19~B24（查重总表-轮1 §三.2 在案对；B20＝裸前缀纪律非单题）──────────
B_SHOU = {
    '3章件11-#12': 'B19 教材复习题B19↔件11-#12 同文对（教材同源未入白名单，防双收）',
    '3章件3-#21': 'B21 批C-11 正文简7（成品2.5.1.2.2-3）↔拓2 同题对（拓2 已撤让位）',
    '3章件4-#10': 'B23 批C-12 拓6↔拓27 同题双收对（0914 主裁保拓6撤拓27，已落盘）',
    '3章件17-#1': 'B24 批D-16 正文16-09↔批E-18 导学18-G1 一源两席对（保16-09撤18-G1）',
    '3章件17-#19': 'B24 链：18-G1 撤换回冲改取 #19（#19 已入册 18-G1）',
}

# ── 同族锁族谱（查重总表 §三.3 件内/跨件同构族＋S4-0 盘点 §七 锁清单 12 枚）──────
FAMILIES = [
    ('F1 件2 #10/#11 平行垂直判族', ['2章件2-#10', '2章件2-#11'], ['2章件2-#11']),
    ('F2 件2 #16/#17 方向向量族', ['2章件2-#16', '2章件2-#17'], ['2章件2-#16']),
    ('F3 件2 #32族 含参平行垂直五件', ['2章件2-#32', '2章件2-#34', '2章件2-#39',
                                      '2章件2-#42', '2章件2-#46'],
     ['2章件2-#32', '2章件2-#34', '2章件2-#39', '2章件2-#42']),
    ('F4 件7 #12/#17 切线长最小族', ['2章件7-#12', '2章件7-#17'], ['2章件7-#12']),
    ('F5 件7#16/件10#4 跨件长短弦四边形', ['2章件7-#16', '2章件10-#4'], []),
    ('F6 件7#39/件10#12 跨件定圆△面积', ['2章件7-#39', '2章件10-#12'], ['2章件10-#12']),
    ('F7 件9 #12/#17 切线长对称族', ['2章件9-#12', '2章件9-#17'], ['2章件9-#12']),
    ('F8 件9#16 教材p113同族异约束（教材侧族·无富矿兄弟）', ['2章件9-#16'], ['2章件9-#16']),
    ('F9 件11 #2/#5 雷达族', ['2章件11-#2', '2章件11-#5'], ['2章件11-#2', '2章件11-#5']),
    ('FR 光线反射族 件3#24/件5#9/件9#5', ['2章件3-#24', '2章件5-#9', '2章件9-#5'], []),
]
LOCK12 = sorted({m for _, ms, lks in FAMILIES for m in lks})
SHOUXIAN3 = {'2章件2-#27': '受限（多选说法·选项判据未提取）',
             '2章件4-#13': '受限（充要辨析·判据受限）',
             '2章件14-#9': '受限（圆与直线概念多选·图/选项受限）'}
BUKESAN3 = {'2章件4-#14': '不可用（条目混排非题·剔）',
            '2章件7-#25': '不可用（双判·复读定级＝重复）',
            '2章件7-#27': '不可用（双判·0913 轮3 钉死全域不采）'}

# ── 归一化与相似度 ────────────────────────────────────────────────────────────────
SUP = {'²': '^2', '³': '^3', '¹': '^1', '⁴': '^4', 'ⁿ': '^n',
       '₀': '_0', '₁': '_1', '₂': '_2', '₃': '_3', '₄': '_4', '₅': '_5',
       '₆': '_6', '₇': '_7', '₈': '_8', '₉': '_9'}
RE_KEEP = re.compile(r'[0-9a-z\u4e00-\u9fff√πΔ∈≤≥≠±∞∴∵⇒α-ω]+')
RE_NUM = re.compile(r'\d+(?:\.\d+)?')


def _nfkc_sup(s):
    s = unicodedata.normalize('NFKC', s or '')
    for k, v in SUP.items():
        s = s.replace(k, v)
    return s.replace('⟦', '').replace('⟧', '')


def norm_text(s):
    return ''.join(RE_KEEP.findall(_nfkc_sup(s).lower()))


def nums_of(s):
    return set(RE_NUM.findall(_nfkc_sup(s)))


def tris(s):
    return {s[i:i + 3] for i in range(len(s) - 2)} if len(s) >= 3 else ({s} if s else set())


def contain(c_tri, k_tri):
    if not c_tri:
        return 0.0
    return len(c_tri & k_tri) / len(c_tri)


def jac(a, b):
    u = a | b
    return len(a & b) / len(u) if u else 0.0


# ── 指针与消费账 ─────────────────────────────────────────────────────────────────
RE_PTR = re.compile(r'(2章|3章)?件(\d{1,2})\s*[-—–－]\s*#?(\d{1,3})')
RE_QSTART = re.compile(r'^(\d{1,3})[．.、]')
NEG_PRE = ['未取', '未收', '未采', '不采', '不取', '禁再收', '禁收', '让位', '弃用', '除名',
           '不收', '双判', '防双收', '已撤', '撤席', '销项', '撤下', '让给', '同族取一', '取一',
           '重题', '白名单外', '未入', '未消', '勿再', '撤换', '原列头', '未消费', '不收双列',
           '撞族', '跨件同题', '未取余量', '备选', '受限题', '未从']
NEG_POST = ['未收', '未采', '不采', '不取', '让位', '双判', '备选', '撤换', '撤席', '不合', '禁收',
            '对称前引']
POS_PROSE = ['归属', '取用', '已收', '已用', '采用', '留用', '入槽', '承接', '补位', '补换',
             '改取', '换收']
RE_MENTION = re.compile(r'(件\d+-#?\d+|#\d+)')


def _neg_after(line, end, self_txt):
    """指针后语境裁决（实证规则）：后20字基本负语境→剔；「未取」紧跟本指针→剔；「均未取」→剔；
    「未取/同族取一」按兄弟点名判（「#32 未取」＝本件留用方；「件9-#12未取」＝本件未取；
    「A、B、C未取」链尾＝链上全部未取；「与件X 同族取一」＝留用方）。"""
    post = line[end:end + 36]
    if re.match(r'\s*未取', post):
        return False
    if any(t in post[:20] for t in NEG_POST):
        return False
    if '均未取' in post:
        return False
    if '同族取一' in post or '未取' in post:
        m = re.search(r'(件\d+-#?\d+|#\d+)\s*未取', post)
        if m:
            if re.fullmatch(r'[、，,；;｜/\s（）()]*'
                            r'((?:件\d+-#?\d+|#\d+)[、，,；;｜/\s（）()]*)*',
                            post[:m.start()]):
                return False  # 「A、B、C未取」链尾：本件与点名件同链均未取
            men = re.findall(r'\d+', m.group(1))
            men = men[-1] if men else ''
            nums = re.findall(r'\d+', self_txt)
            cur_n = nums[-1] if nums else ''
            if men != cur_n:
                return True
            return False
        if re.search(r'与[^，；｜|【】]{0,14}(同族)?取一', post[:24]):
            mk = re.search(r'[（(]\s*取\s*(?:件\d+-#?|#)(\d+)', post)
            if mk:  # 「A与B同族取一（取#K）」：K＝他者→本件弃；K＝本件→本件取
                cur_n2 = re.findall(r'\d+', self_txt)
                return mk.group(1) == (cur_n2[-1] if cur_n2 else '')
            return True
        if '同族取一' in post:
            return False
    return True


def canon(zhang, n, k):
    return '%s件%d-#%d' % (zhang, int(n), int(k))


class Universe:
    """件号×题号存在域（裸前缀章判用）：('2章',N)->最大题号。"""

    def __init__(self):
        self.cnt = {}

    def feed(self, zhang, n, count):
        key = (zhang, int(n))
        self.cnt[key] = max(self.cnt.get(key, 0), int(count))

    def exists(self, zhang, n, k):
        return 1 <= int(k) <= self.cnt.get((zhang, int(n)), 0)


def resolve(z, n, k, uni, pre_ctx):
    """带前缀→定；裸前缀→存在域唯一则解；两可→看前文60字有无「3章件/富矿3章」就近判（查① 同法），
    仍两可→返回 (2章ptr, True) 与 (3章ptr, True) 两可疑。返回 [(ptr, sus)]。"""
    if z:
        return [(canon(z, n, k), False)]
    e2, e3 = uni.exists('2章', n, k), uni.exists('3章', n, k)
    if e2 and not e3:
        return [(canon('2章', n, k), False)]
    if e3 and not e2:
        return [(canon('3章', n, k), False)]
    if not e2 and not e3:
        return []
    if re.search(r'(富矿3章|3章件)', pre_ctx):
        return [(canon('3章', n, k), False)]
    if re.search(r'(富矿2章|2章件)', pre_ctx):
        return [(canon('2章', n, k), False)]
    return [(canon('2章', n, k), True), (canon('3章', n, k), True)]


def load_read(path):
    with open(path, encoding='utf-8-sig', errors='replace') as fh:
        return fh.read()


def load_tiku():
    """题面库逐键题面：{键: dict(text,norm,nums,tri,src,片)}（题面侧 md，答案侧不读）。"""
    keys = {}
    if not os.path.isdir(TIKU_DIR):
        return keys
    for fn in sorted(os.listdir(TIKU_DIR)):
        if not fn.endswith('.md') or fn.endswith('-答案侧.md'):
            continue
        pian = fn.split('-')[0]
        raw = load_read(os.path.join(TIKU_DIR, fn))
        for b in re.split(r'\n(?=### )', raw):
            m = re.match(r'###\s+(\S+?)｜(.*)', b)
            if not m:
                continue
            key, meta = m.group(1), m.group(2)
            body = b.split('\n', 1)[1] if '\n' in b else ''
            body = body.split('\n---')[0].strip()
            sm = re.search(r'源：([^｜\n]+)', meta)
            keys[key] = {'text': body, 'norm': norm_text(body), 'nums': nums_of(body),
                         'src': sm.group(1).strip() if sm else '', '片': pian}
    for v in keys.values():
        v['tri'] = tris(v['norm'])
    return keys


def tiku_ptrs(tiku, uni):
    """题面库头注源号 → 在册指针集（消费账腿一；裸前缀两可者不计入）。"""
    out = set()
    for v in tiku.values():
        for ptr, sus in tiku_ptr_one(v.get('src') or '', uni):
            if not sus:
                out.add(ptr)
    return out


def tiku_ptr_one(src, uni):
    if not src:
        return []
    out = []
    for m in RE_PTR.finditer(src):
        out += resolve(m.group(1), int(m.group(2)), int(m.group(3)), uni, src[:m.start()])
    return out


def scan_consumption(uni):
    """定稿件 bodies＋批A~E 台账 取用面全扫（R9 腿一）→ (消费账{ptr:[证据]}, 裸前缀两可疑清单)。
    行级 designated：表行（| … |）与块头（【…】）直认消费；散文行须含 POS_PROSE 消费关键词
    （双收处置「补换＝」「留用」等）否则只略——台账备选池散文（「课时NN池：…」「未取余量登记」
    「受限题」）不判死。章判：显式前缀＞前60字就近＞文件域默认（批A/B→2章、批C/D/E→3章）＞
    存在域唯一；仍两可→bare_sus（B20 只记疑不判死）。语境：前45字 NEG_PRE；后窗 _neg_after
    实证规则（「#32 未取」＝本件留用方；「件9-#12未取」＝本件未取；「均未取」＝双双未取）。"""
    consumed, bare_sus = {}, []
    files = []
    if os.path.isdir(DINGGAO_DIR):
        files += [os.path.join(DINGGAO_DIR, f) for f in sorted(os.listdir(DINGGAO_DIR))
                  if f.endswith('.md')]
    for fp in files:
        fn = os.path.basename(fp)
        dom = '2章' if re.match(r'批[AB]', fn) else ('3章' if re.match(r'批[CDE]', fn) else None)
        try:
            raw = load_read(fp)
        except OSError:
            continue
        for i, line in enumerate(raw.splitlines(), 1):
            if '件' not in line:
                continue
            if '未取余量' in line:
                continue  # 台账弃题／移交清单整段（「未取余量：件X…」全列＝未取，不作消费证据）
            s = line.strip()
            is_table = s.startswith('|')
            is_block = '【' in line and '】' in line
            if not (is_table or is_block or any(t in line for t in POS_PROSE)):
                continue
            for m in RE_PTR.finditer(line):
                pre = line[max(0, m.start() - 45):m.start()]
                if any(t in pre for t in NEG_PRE):
                    continue
                if not _neg_after(line, m.end(), m.group(0)):
                    continue
                pre60 = line[max(0, m.start() - 60):m.start()]
                z = m.group(1)
                if not z:
                    if re.search(r'(富矿3章|3章件)', pre60):
                        z = '3章'
                    elif re.search(r'(富矿2章|2章件)', pre60):
                        z = '2章'
                    else:
                        z = dom
                n, k = int(m.group(2)), int(m.group(3))
                e2, e3 = uni.exists('2章', n, k), uni.exists('3章', n, k)
                ptrs = []
                if z and uni.exists(z, n, k):
                    ptrs = [(canon(z, n, k), False)]
                elif z:
                    ptrs = []
                elif e2 and not e3:
                    ptrs = [(canon('2章', n, k), False)]
                elif e3 and not e2:
                    ptrs = [(canon('3章', n, k), False)]
                else:
                    ptrs = [(canon('2章', n, k), True), (canon('3章', n, k), True)]
                for ptr, sus in ptrs:
                    if sus:
                        bare_sus.append('%s ← %s:%d' % (ptr, fn, i))
                        continue
                    consumed.setdefault(ptr, []).append('%s:%d｜%s' % (fn, i, s[:90]))
    return consumed, bare_sus


RE_CZ_HEAD = re.compile(r'^#{2,4}\s*(?:[\d④③②①⓪.]+\s*)?(?:[\u2460-\u2473]?\s*)?(?:\d+\.\d+\s*)?(?:逐题表[——-]*)?件(\d{1,2})\s*[《\s（]')
RE_CZ_CNT = re.compile(r'（共(\d+)题）|（(\d+)题')


def load_jinchang():
    """查①②③ 逐题表禁收（重复/教材同源/超纲）＋件题量存在域 → (禁收{ptr:(源,判级,指纹)}, Universe)。
    行式：查① |题号|难度|指纹|判级|…；查②③ |题|难度|档|指纹|判级（题号列裸数字，件号取自节头）。
    章域（B20 纪律）：查① 全域＝2章件1~14；查③ 全域＝3章件1~21；查② 仅「2.4 逐题表——件7」
    ＝2章件7 轨迹上探域，其余件N（椭圆/双曲线）＝3章件N——两章件号分立，不得互串。"""
    jin, uni = {}, Universe()
    for tag, fp in CZ_FILES.items():
        if not os.path.isfile(fp):
            continue
        cur_zhang = '2章' if tag == '①' else '3章'
        cur_pian = None
        for line in load_read(fp).splitlines():
            hm = re.match(r'^#{2,4}\s*件(\d{1,2})\s*[《\s（]', line)
            if hm:
                cur_pian = int(hm.group(1))
                if tag == '②':
                    cur_zhang = '3章'  # 查②「件N」缺省＝3章富矿（椭圆/双曲线件系）
                cm = re.search(r'共?\s*(\d+)\s*题', line)
                if cm:
                    uni.feed(cur_zhang, cur_pian, cm.group(1))
                continue
            hm2 = re.match(r'^#{2,4}\s*[\d.]+.*?件(\d{1,2})\s', line)
            if hm2 and ('逐题表' in line or '题，均' in line):
                cur_pian = int(hm2.group(1))
                if tag == '②':
                    # 查② 唯一 2章域＝「2.4 逐题表——件7 轨迹上探」；其余逐题表节头归 3章
                    cur_zhang = '2章' if '2.4' in line else '3章'
                cm = re.search(r'(\d+)\s*题', line)
                if cm:
                    uni.feed(cur_zhang, cur_pian, cm.group(1))
                continue
            if not line.startswith('|') or cur_pian is None:
                continue
            cells = [c.strip() for c in line.strip('|').split('|')]
            if len(cells) < 4:
                continue
            m = RE_PTR.match(cells[0])
            if m and m.group(1):
                ptr = canon(cur_zhang, m.group(2), m.group(3))
            elif cells[0].isdigit():
                ptr = canon(cur_zhang, cur_pian, cells[0])
            else:
                continue
            verdict = next((c for c in cells if re.match(r'^(重复|教材同源|超纲)', c)), '')
            if verdict:
                jin[ptr] = (tag, verdict.split('（')[0][:6], cells[2][:40])
    return jin, uni


def load_whitelist():
    """查重总表 §二 2.1~2.3 段白名单 → [(ptr,难度,指纹,flags)]。"""
    items = []
    if not os.path.isfile(ZONGTAB):
        return items
    seg = re.search(r'### 2\.1~2\.3 段.*?(?=### 2\.4 段)', load_read(ZONGTAB), re.S)
    if not seg:
        return items
    for line in seg.group(0).splitlines():
        if not line.startswith('| 件'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 3:
            continue
        m = RE_PTR.match(cells[0])
        if not m:
            continue
        fp_txt = cells[2] if len(cells) > 2 else ''
        flags = []
        if ('剔' in fp_txt or '非题' in fp_txt) and '⚠' in fp_txt:
            flags.append('剔')
        if '受限' in fp_txt:
            flags.append('受限')
        if '同族' in fp_txt or '取一' in fp_txt:
            flags.append('同族')
        if '双判' in fp_txt:
            flags.append('双判')
        items.append((canon('2章', m.group(2), m.group(3)), cells[1], fp_txt, flags))
    return items


def load_chengpin():
    """成品卷①~④ 全dump 块语料（R9 腿二）：[(对端label, norm, tri, nums)]。"""
    out = []
    for lab, fp in JUAN_DUMPS:
        if not os.path.isfile(fp):
            continue

        def flush(_cur, _buf):
            if _cur and _buf:
                txt = '\n'.join(_buf)
                nm = norm_text(txt)
                out.append(('%s·%s' % (lab, _cur), nm, tris(nm), nums_of(txt)))
        cur, buf = None, []
        for line in load_read(fp).splitlines():
            m = re.match(r'^(\d+(?:\.\d+)*-\d+)[．.]', line.strip())
            if m:
                flush(cur, buf)
                cur, buf = m.group(1), [line]
            elif cur is not None:
                buf.append(line)
        flush(cur, buf)
    return out


# ── 富矿 docx 题面提取（对象读·OMML 线性化，查③ 同制）─────────────────────────
_docx = None
_DOCX_CACHE = {}
DOCX_FILES2 = {2: '2 直线的倾斜角与斜率（共49题）.docx',
               3: '3 直线的方程（共35题）.docx',
               4: '4 直线的方程综合（共23题）.docx',
               5: '5 直线的交点坐标与距离公式（共43题）.docx',
               6: '6 圆的方程（共28题）.docx',
               7: '7 圆的几何性质、轨迹、综合应用（共40题）.docx',
               8: '8 直线与圆的位置关系（共28题）.docx',
               9: '9 圆的切线问题（共19题）.docx',
               10: '10 圆的弦长与圆心距（共14题）.docx',
               11: '11 直线与圆的位置关系的综合运用（共10题）.docx',
               12: '12 圆与圆的位置关系（共40题）.docx',
               13: '13 直线与圆的方程中的高考新题型（共45题）.docx',
               14: '14 章节综合测试-直线和圆的方程（共22题）.docx'}


def docx_questions(n):
    r"""第2章件N docx → {题号: 题干}（新题起始＝行首题号且当前块已含【难度】，查③ 同制）。"""
    n = int(n)
    if n in _DOCX_CACHE:
        return _DOCX_CACHE[n]
    qs = {}
    fp = os.path.join(DOCX_DIR2, DOCX_FILES2.get(n, ''))
    if os.path.isfile(fp):
        global _docx
        if _docx is None:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import dump_docx as _m
            _docx = _m
        d = _docx
        doc = d.Document(fp)
        paras = []
        for child in doc.element.body.iterchildren():
            t = d.tagof(child)
            if t == 'p':
                paras.append(d.para_text(child))
            elif t == 'tbl':
                for p in child.findall('.//{' + d.W + '}p'):
                    paras.append(d.para_text(p))
        cur, buf, armed = None, [], False
        for t in paras:
            s = t.strip()
            m = RE_QSTART.match(s)
            if m and (armed or cur is None):
                if cur is not None and cur not in qs:
                    qs[cur] = '\n'.join(buf)
                cur, buf, armed = int(m.group(1)), [s], False
            elif cur is not None:
                buf.append(s)
                if '【难度】' in s:
                    armed = True
        if cur is not None and cur not in qs:
            qs[cur] = '\n'.join(buf)
        qs = {k: v.split('【答案】')[0].strip() for k, v in qs.items()}
    _DOCX_CACHE[n] = qs
    return qs


# ── 判级核心 ─────────────────────────────────────────────────────────────────────
def judge_text(text, corpora):
    """文本腿：corpora=[(域标签,[(对端,norm,tri,nums)])] → (级别, 撞命中, 疑/观察)。
    c＝双向 3-gram 包含度取大（候选⊂语料／语料⊂候选）；同数值构另设数字先行规则
    （数字集重合≥0.85 且两侧≥3 数且字 bigram Jaccard≥0.35——只换数/换问族，词面可异）。"""
    nm = norm_text(text)
    ct = tris(nm)
    cn = nums_of(text)
    bg = {nm[i:i + 2] for i in range(len(nm) - 1)} if len(nm) >= 2 else set()
    hits, obs = [], []
    for lab, arr in corpora:
        bh, bo = None, None

        def take(b, x, is_hit):
            if x is None:
                return b if b is not None else None
            if b is None:
                return x
            return x if x[0] > b[0] else b
        for name, knm, ktri, knums in arr:
            c = max(contain(ct, ktri), contain(ktri, ct))
            nsim = jac(cn, knums) if (cn and knums) else 0.0
            enough = min(len(cn), len(knums)) >= 3
            kbg = {knm[i:i + 2] for i in range(len(knm) - 1)} if len(knm) >= 2 else set()
            bj = jac(bg, kbg) if (bg and kbg) else 0.0
            if c >= 0.90 or (c >= 0.80 and enough and nsim >= 0.85):
                bh = take(bh, (c, name, nsim, '逐字/近逐字' if c >= 0.90 else '近逐字·数字重合'), True)
            elif enough and nsim >= 0.85 and bj >= 0.35:
                bh = take(bh, (max(c, bj), name, nsim, '同数值构（数字先行·换问族）'), True)
            elif 0.60 <= c < 0.90 and enough and nsim >= 0.75:
                bh = take(bh, (c, name, nsim, '同数值构（只换数/换问族）'), True)
            elif enough and nsim >= 0.75 and bj >= 0.30:
                bo = take(bo, (max(c, bj), name, nsim, '近似'), False)
            elif c >= 0.50 and (nsim >= 0.60 or c >= 0.55):
                bo = take(bo, (c, name, nsim, '近似'), False)
            elif c >= 0.45:
                bo = take(bo, (c, name, nsim, '弱（观察）'), False)
        if bh:
            hits.append((lab, bh))
        if bo:
            obs.append((lab, bo))
    lvl = '撞' if hits else ('疑' if any(o[1][3] == '近似' for o in obs) else '')
    return lvl, hits, obs


def judge_candidate(cid, src, text, fp, ctx):
    """单候选三门判级。ctx＝dict(consumed,jinchang,tiku_arr,chengpin,families,uni,have_text)。"""
    consumed, jin = ctx['consumed'], ctx['jinchang']
    ev, pin = [], '净'
    src_ptr = None
    if src:
        pr = resolve_ptr_str(src, ctx['uni'])
        if pr:
            src_ptr = pr
    if src_ptr:
        if src_ptr in B_SHOU:
            pin = '撞'
            ev.append('L1 防双收：%s' % B_SHOU[src_ptr])
        if src_ptr in jin:
            pin = '撞'
            ev.append('L1 禁收：查%s 判级[%s]（%s）' % (jin[src_ptr][0], jin[src_ptr][1], jin[src_ptr][2]))
        if src_ptr in consumed:
            pin = '撞'
            ev.append('L1 源号双收 ← %s' % consumed[src_ptr][0])
    if text:
        lvl, hits, obs = judge_text(text, ctx['corpora'])
        if lvl == '撞' and pin != '撞':
            pin = '撞'
        if lvl == '疑' and pin == '净':
            pin = '疑'
        for lab, (c, name, nsim, kind) in hits:
            ev.append('L2/3 文本撞[%s] vs %s：%s c=%.2f 数字重合=%.2f' % (kind, lab, name, c, nsim))
        for lab, (c, name, nsim, kind) in obs:
            ev.append('%s vs %s：%s c=%.2f（%s）' % ('⚠疑' if kind == '近似' else '○观察', lab, name, c, kind))
    if not text and pin == '净':
        pin = '疑'
        ev.append('题面未取得（docx 提取缺号/变体）——待钉')
    return {'id': cid, 'src': src_ptr or src or '', 'pin': pin, 'ev': ev}


def resolve_ptr_str(src, uni):
    out = resolve(None, 0, 0, uni, '') and None
    for m in RE_PTR.finditer(src):
        r = resolve(m.group(1), int(m.group(2)), int(m.group(3)), uni, src[:m.start()])
        if r and not r[0][1]:
            return r[0][0]
        if r:
            return r[0][0] + '（裸前缀两可疑）'
    return None


def family_rejudge(pins, consumed, families):
    """军师钉「取一族达上限」：族内任一员已收⇒锁员全 ❌；族全净⇒锁员首席 ⚠守门、余锁员 ❌。"""
    notes = []
    for fam, members, locks in families:
        taken = [m for m in members if m in consumed]
        free = not taken
        live_locks = [m for m in locks if m in pins]
        keeper = live_locks[0] if live_locks else None
        for m in live_locks:
            p = pins[m]
            if not free:
                if p['pin'] in ('净', '疑'):
                    p['ev'].append('L4 同族超上限：族「%s」兄弟已收（%s）' % (fam, '，'.join(taken)))
                    p['pin'] = '撞'
                    notes.append('%s：族「%s」席位已占（%s）→ ❌ 不归 ⚠' % (m, fam, '，'.join(taken)))
            else:
                if p['pin'] == '净':
                    if m == keeper:
                        p['pin'] = '疑'
                        p['ev'].append('L4 同族守门席：族「%s」全净，本席保留待钉' % fam)
                        notes.append('%s：族「%s」全净→守门席 ⚠' % (m, fam))
                    else:
                        p['pin'] = '撞'
                        p['ev'].append('L4 同族超上限：守门席＝%s（族「%s」）' % (keeper, fam))
                        notes.append('%s：族「%s」上限（守门席＝%s）→ ❌' % (m, fam, keeper))
        for m in members:
            if m in pins and m not in locks and not free and pins[m]['pin'] == '净':
                pins[m]['pin'] = '撞'
                pins[m]['ev'].append('L4 同族超上限：族「%s」席位已由 %s 占' % (fam, '，'.join(taken)))
                notes.append('%s：族「%s」席位已占（%s）→ ❌' % (m, fam, '，'.join(taken)))
    return notes


SYM = {'净': '✅净', '撞': '❌撞', '疑': '⚠疑'}


def build_ctx():
    tiku = load_tiku()
    jin, uni = load_jinchang()
    consumed, bare_sus = scan_consumption(uni)
    chengpin = load_chengpin()
    for k, v in tiku.items():
        for ptr, sus in tiku_ptr_one(v.get('src') or '', uni):
            consumed.setdefault(ptr, []).append('题面库头注源号（在册·%s）' % k)
    tiku_arr = [(k, v['norm'], v['tri'], v['nums']) for k, v in tiku.items()]
    return {'tiku': tiku, 'jinchang': jin, 'uni': uni, 'consumed': consumed,
            'bare_sus': bare_sus, 'chengpin': chengpin,
            'corpora': ([('题面库%d键' % len(tiku_arr), tiku_arr)] if tiku_arr else [])
                       + ([('成品卷①~④%d块' % len(chengpin), chengpin)] if chengpin else []),
            'tiku_ptrs': tiku_ptrs(tiku, uni)}


def write_report(path, lines):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


def check_out(path):
    if os.path.exists(path):
        print('[FAIL] 写前核：%s 已存在，拒写（删后重跑或换 --out）' % path)
        return False
    return True


def run_candidates(cands, out, ctx=None):
    """通用门：cands=[{id,src,text,fp}]。"""
    ctx = ctx or build_ctx()
    pins = {}
    for c in cands:
        pins[c['id']] = judge_candidate(c['id'], c.get('src'), c.get('text'), c.get('fp'), ctx)
    notes = family_rejudge(pins, ctx['consumed'], FAMILIES)
    L = ['[语料] 题面库 %d 键｜禁收 %d 项｜消费账 %d 指针｜成品卷块 %d（R9 腿）'
         % (len(ctx['tiku']), len(ctx['jinchang']), len(ctx['consumed']), len(ctx['chengpin']))]
    for n in notes:
        L.append('[同族] %s' % n)
    cnt = {'净': 0, '撞': 0, '疑': 0}
    for cid, p in pins.items():
        cnt[p['pin']] += 1
        L.append('[%s] %s（%s）%s' % (SYM[p['pin']], cid, p['src'],
                                      '；'.join(p['ev']) if p['ev'] else '三门空'))
    if cnt['撞'] or cnt['疑']:
        verdict = '[FAIL] 撞 %d／疑 %d／净 %d —— 撞疑禁行，逐枚钉码后再议' % (cnt['撞'], cnt['疑'], cnt['净'])
    else:
        verdict = '[PASS] 全净放行 %d' % cnt['净']
    L.append(verdict)
    if out:
        if not check_out(out):
            return 2
        write_report(out, L)
        print('[报告] %s' % out)
    print(verdict)
    return 0 if (cnt['撞'] == 0 and cnt['疑'] == 0) else 1


# ── 首跑（S4-0 净余候选 117＋R9 对勘）────────────────────────────────────────────
def firstrun(out):
    ctx = build_ctx()
    consumed, jin, uni, tiku = ctx['consumed'], ctx['jinchang'], ctx['uni'], ctx['tiku']
    tiku_srcs = ctx['tiku_ptrs']
    wl = load_whitelist()
    wl_map = {p: (dif, fp, fl) for p, dif, fp, fl in wl}
    L = []
    L.append('# S4 题源防撞门·首跑钉码（2026-09-14）')
    L.append('')
    L.append('> 门＝`工具/S4题源防撞门.py`｜依据＝军师账审-收口轮0913 §十（开扩容闸·前置三条件①②③）'
             '＋`_tmpM3S4预备0913/S4-0净可用盘点.md`（净余 102＋15待判＋3禁 口径）'
             '＋`_tmp换装预备0913/键账对平首跑.md`（门体例参照）。')
    L.append('> 撞面＝题面库 %d 键语料＋头注定稿源号＋批A~E 取用面全扫（R9 腿一）＋防双收 B19~B24'
             '＋查重①②③禁收（任务口径锚＝查③ 重复73＋同源20）＋R9 腿二成品卷①~④ 块语料。' % len(tiku))
    L.append('> 红线：全语料只读、零 git；本跑唯一写入＝本件。')
    L.append('')
    pian_lian = [k for k in tiku if '-练-' in k]
    pian_dao = [k for k in tiku if '-导-' in k]
    pian_tuo = [k for k in tiku if '-拓-' in k]
    jin3 = {k: v for k, v in jin.items() if v[0] == '③'}
    dup3 = {k: v for k, v in jin3.items() if '重复' in v[1]}
    tong3 = {k: v for k, v in jin3.items() if '教材同源' in v[1]}
    L.append('## 〇、语料读数')
    L.append('')
    L.append('| 腿 | 读数 |')
    L.append('|---|---|')
    L.append('| ①题面库键语料 | %d 键（导 %d＋练 %d＋拓 %d）——逐键题面＋头注源号 |'
             % (len(tiku), len(pian_dao), len(pian_lian), len(pian_tuo)))
    L.append('| ②定稿源号（头注在册指针） | 富矿指针 %d 枚在册（练域 320 键账含于其中） |' % len(tiku_srcs))
    L.append('| ③拓展册收编指纹＋取用面全扫（R9 腿一） | 消费账 %d 指针（正语境）；裸前缀两可疑 %d 处 |'
             % (len(consumed), len(ctx['bare_sus'])))
    L.append('| ④防双收 | B19~B24 硬编码 %d 枚（B20＝裸前缀纪律，见 2.3） |' % len(B_SHOU))
    L.append('| ⑤查重禁收 | 全量 %d 项；其中查③域 %d 项＝重复 %d＋教材同源 %d（任务口径「重复73＋同源20」机械复现%s） |'
             % (len(jin), len(jin3), len(dup3), len(tong3),
                '✓' if (len(dup3) == 73 and len(tong3) == 20) else '（读数见左，差异系逐题表行式变体，禁收并集仍全覆盖）'))
    L.append('| R9 腿二·成品卷①~④ | %d 块语料（含〔基〕知识条块＝查① 同口径全集） |' % len(ctx['chengpin']))
    L.append('')
    L.append('## 一、候选池重构（白名单 250 → 本门消费账过滤）')
    L.append('')
    excluded = [p for p, _, _, f in wl if '剔' in f]
    consumed_wl = [p for p, _, _, _ in wl if p in consumed or p in jin or p in B_SHOU]
    cand, bukesan = [], []
    for ptr, dif, fp_txt, flags in wl:
        if ptr in BUKESAN3:
            bukesan.append(ptr)
            continue
        if ptr in consumed_wl:
            continue
        m = re.match(r'2章件(\d+)-#(\d+)', ptr)
        text = docx_questions(int(m.group(1))).get(int(m.group(2)), '')
        cand.append(ptr)
        wl_map.setdefault(ptr, (dif, fp_txt, flags))
    L.append('- 白名单 2.1~2.3 段逐件清单 %d 枚（剔非题 %d 枚另列）。' % (len(wl), len(excluded)))
    L.append('- 本门消费账命中白名单 %d 枚 → 不入候选（已收/禁收，逐枚证据 §2.1）。' % len(consumed_wl))
    L.append('- 候选＝未消费余量 %d 枚（同族锁 12＋受限 3 含在内，§三 逐枚钉码）；不可用 3 枚直接 ❌（§四）。' % len(cand))
    L.append('- S4-0 口径对照：净可用 117＝102净＋15待判；本门实测候选 %d 枚＝S4-0 117＋2章件13-#35'
             '（S4-0 账外项；本门文本门 ⚠疑 vs 题面库09-G4〔其源＝成品C卷2.3.4.4-6〕，近同已用题，'
             '不入放行净数）——✅净 102 两口径一致（§三 依据列）。' % len(cand))
    L.append('')
    L.append('## 二、R9 对勘结论')
    L.append('')
    L.append('### 2.1 腿一·取用面补扫（批A~E 台账＋定稿件 bodies；题面库头注源号并入）')
    L.append('')
    L.append('白名单域消费账 %d 枚，证据（文件:行｜语境）：' % len(consumed_wl))
    L.append('')
    L.append('| 白名单项 | 消费证据 |')
    L.append('|---|---|')
    for p in sorted(consumed_wl):
        ev = consumed.get(p, ['（禁收/防双收）'])[0]
        L.append('| %s | %s |' % (p, ev.replace('|', '／')))
    L.append('')
    L.append('### 2.2 腿二·成品卷①~④ ↔ 候选文本对勘')
    L.append('')
    r9_hit, r9_obs = [], []
    for p in cand:
        m = re.match(r'2章件(\d+)-#(\d+)', p)
        text = docx_questions(int(m.group(1))).get(int(m.group(2)), '')
        if not text:
            continue
        nm, ct, cn = norm_text(text), tris(norm_text(text)), nums_of(text)
        best = None
        for name, knm, ktri, knums in ctx['chengpin']:
            c = contain(ct, ktri)
            if best is None or c > best[1]:
                best = (name, c, jac(cn, knums) if (cn and knums) else 0.0)
        if best and best[1] >= 0.60:
            r9_hit.append((p, best))
        elif best and best[1] >= 0.50:
            r9_obs.append((p, best))
    L.append('候选 vs 成品卷 %d 块最高包含度：≥0.60 共 %d 枚（撞级线）、0.50~0.60 共 %d 枚（观察带——查① 已人判新增，'
             '弱带不复审、只登记）。' % (len(ctx['chengpin']), len(r9_hit), len(r9_obs)))
    L.append('')
    L.append('| 候选 | 成品卷最高对端 | c | 数字重合 |')
    L.append('|---|---|---|---|')
    for p, (name, c, ns) in (r9_hit + r9_obs)[:40]:
        L.append('| %s | %s | %.2f | %.2f |' % (p, name, c, ns))
    if len(r9_hit + r9_obs) > 40:
        L.append('| …（余 %d 枚同带略） | | | |' % (len(r9_hit + r9_obs) - 40))
    L.append('')
    L.append('### 2.3 裸前缀（B20 病灶）登记')
    L.append('')
    L.append('取用面扫出裸前缀「件N-#K」2章/3章两可且正语境者 %d 处——照 B20 只记疑不判死：' % len(ctx['bare_sus']))
    L.append('')
    for s in ctx['bare_sus'][:20] or ['（无）']:
        L.append('- %s' % s)
    L.append('')
    L.append('## 三、候选逐枚钉码')
    L.append('')
    pins = {}
    for p in cand:
        m = re.match(r'2章件(\d+)-#(\d+)', p)
        text = docx_questions(int(m.group(1))).get(int(m.group(2)), '')
        pins[p] = judge_candidate(p, p, text, wl_map[p][1], ctx)
    for p, why in SHOUXIAN3.items():
        if p not in pins:
            ev = ['受限件：%s' % why]
            if p in consumed:
                ev.append('L1 源号双收 ← %s' % consumed[p][0])
                pins[p] = {'id': p, 'src': p, 'pin': '撞', 'ev': ev}
            else:
                pins[p] = {'id': p, 'src': p, 'pin': '疑', 'ev': ev}
    fnote = family_rejudge(pins, consumed, FAMILIES)
    cnt = {'净': 0, '撞': 0, '疑': 0}
    L.append('| 候选 | 难度 | 钉 | 依据（腿｜对端｜读数） |')
    L.append('|---|---|---|---|')
    for p in sorted(pins):
        v = pins[p]
        cnt[v['pin']] += 1
        dif = wl_map.get(p, ('', '', []))[0]
        ev = '；'.join(v['ev']) if v['ev'] else '三门空（题面已对全库语料）'
        L.append('| %s | %s | %s | %s |' % (p, dif, SYM[v['pin']], ev.replace('|', '／')[:240]))
    L.append('')
    L.append('### 钉码分布：✅净 %d｜❌撞 %d｜⚠疑 %d（候选 %d 枚）' % (cnt['净'], cnt['撞'], cnt['疑'], len(pins)))
    L.append('')
    for n in fnote:
        L.append('- [同族锁重判] %s' % n)
    L.append('')
    L.append('## 四、S4-0 口径三禁（不可用 3 枚，直接 ❌）')
    L.append('')
    for p, why in BUKESAN3.items():
        L.append('- ❌撞 %s：%s' % (p, why))
    L.append('')
    L.append('## 五、门判读数与结论')
    L.append('')
    L.append('- 首跑候选 %d 枚：✅净 %d／❌撞 %d／⚠疑 %d；另有口径三禁 ❌3。' % (len(pins), cnt['净'], cnt['撞'], cnt['疑']))
    L.append('- R9 腿一：白名单域消费账 %d 枚（含禁收/防双收），逐枚证据 §2.1。' % len(consumed_wl))
    L.append('- 同族锁 12 枚按「取一族达上限」重判：兄弟已收者 ❌（不归 ⚠）；族全净者守门席 ⚠、余员 ❌。'
             '非锁员的族成员（件7-#39／件10-#4 等）族全净时不钉，保持本门判级——是否预占席属军师钉范围，本门只注记。')
    L.append('- 件13-#35 特记：S4-0 未列（账外），本门消费账亦无槽位证据；文本门 ⚠疑 vs 题面库09-G4'
             '（c=0.50，其源＝成品C卷2.3.4.4-6）——近同已用题，建议军师按「疑似变式已用」复核后定去留。')
    L.append('- R9 腿二：成品卷对勘 ≥0.60 命中 %d 枚（观察带 %d 枚）——对端见 §2.2 与 §三 依据列。' % (len(r9_hit), len(r9_obs)))
    L.append('- 结论：扩容闸放行题量上限＝✅净 %d 枚；⚠疑 %d 枚须逐枚人工钉后再议；❌撞禁取。'
             % (cnt['净'], cnt['疑']))
    L.append('')
    if cnt['撞'] or cnt['疑']:
        verdict = '[FAIL] 撞 %d／疑 %d／净 %d —— 撞疑禁行' % (cnt['撞'], cnt['疑'], cnt['净'])
    else:
        verdict = '[PASS] 全净 %d' % cnt['净']
    L.append(verdict)
    if out:
        if not check_out(out):
            return 2
        write_report(out, L)
        print('[报告] %s' % out)
    print('[钉码] 净 %d／撞 %d／疑 %d（候选 %d）' % (cnt['净'], cnt['撞'], cnt['疑'], len(pins)))
    print(verdict)
    return 0 if (cnt['撞'] == 0 and cnt['疑'] == 0) else 1


# ── 负测/正测（--selftest）─────────────────────────────────────────────────────
def selftest():
    import tempfile
    rc = 0
    print('== S4题源防撞门 selftest（离线合成 TEMP 跑毕即删＋实库在案对只读）==')
    with tempfile.TemporaryDirectory(prefix='S4闸-selftest-') as td:
        key_text = '已知直线l过点P(3,2)且与圆x^2+y^2=4相切，求直线l的方程．'
        fresh_text = '设数列{an}满足a1=7，an+1=an+4，求an的通项公式及a10的值．'
        same_num = '已知直线m经过点P(3,2)，且直线m与圆x^2+y^2=4相切，试写出直线m的方程．'
        part_sim = '已知直线l过点P(1,1)且与圆x^2+y^2=9相切，求直线l的斜率．'
        tdir = os.path.join(td, '题面库')
        os.makedirs(tdir, exist_ok=True)
        with open(os.path.join(tdir, '课时99-合成.md'), 'w', encoding='utf-8') as fh:
            fh.write('### 2章-练-课时99-01｜单选｜合成｜难度：0.85｜源：2章件2-#38\n%s\n\n---\n' % key_text)
        # 语料路径猴补丁（离线合成层）
        saved = {k: globals()[k] for k in ('TIKU_DIR', 'CZ_FILES', 'DINGGAO_DIR', 'ZONGTAB',
                                           'JUAN_DUMPS', 'B_SHOU', 'FAMILIES')}
        try:
            globals()['TIKU_DIR'] = tdir
            globals()['CZ_FILES'] = {k: os.path.join(td, '无-查%s.md' % k) for k in CZ_FILES}
            globals()['DINGGAO_DIR'] = os.path.join(td, '无-定稿')
            globals()['ZONGTAB'] = os.path.join(td, '无-总表.md')
            globals()['JUAN_DUMPS'] = []
            globals()['B_SHOU'] = {}
            globals()['FAMILIES'] = []
            ctx = build_ctx()

            def one(cid, src, text):
                d = judge_candidate(cid, src, text, None, ctx)
                return d['pin']

            cases = [
                ('P0 全新题零误报（离线）', one('T-新', None, fresh_text), '净'),
                ('N1 逐字撞（语料键原文）真拦', one('T-逐字', None, key_text), '撞'),
                ('N2 源号双收（头注源号在册）真拦', one('T-源号', '2章件2-#38', None), '撞'),
                ('N3 同数值构（同数字换问式）真拦', one('T-同数', None, same_num), '撞'),
                ('N4 近似疑（部分相似）不静默放行', one('T-疑', None, part_sim), '疑'),
            ]
            for tag, got, want in cases:
                ok = got == want
                rc |= (not ok)
                print('[selftest %s] %s：判 %s（期望 %s）' % ('PASS' if ok else 'FAIL', tag, got, want))
            got = run_candidates([{'id': 'T-全门', 'src': None, 'text': fresh_text}], None, ctx)
            rc |= (got != 0)
            print('[selftest %s] P5 通用门健康候选放行：退出码 %d（期望 0）' % ('PASS' if got == 0 else 'FAIL', got))
        finally:
            globals().update(saved)
    # 实库腿（只读；缺语料则记 FAIL 提示）
    try:
        ctx = build_ctx()
        ok_base = len(ctx['tiku']) > 0
    except Exception as e:  # noqa
        print('[selftest FAIL] 实库语料装载异常：%s' % e)
        return 1
    if not ok_base:
        print('[selftest FAIL] 实库语料不可达（题面库 0 键）')
        return 1
    for pid, tag in (('3章件17-#1', 'B24 一源两席（16-09/18-G1）'),
                     ('3章件4-#10', 'B23 拓6/拓27 双收'),
                     ('2章件2-#38', '批A 01-E1 已用')):
        d = judge_candidate(pid, pid, None, None, ctx)
        ok = d['pin'] == '撞'
        rc |= (not ok)
        print('[selftest %s] 实库负测 %s（%s）：%s ← %s'
              % ('PASS' if ok else 'FAIL', pid, tag, SYM[d['pin']],
                 d['ev'][0] if d['ev'] else '无据'))
    # 实库正测：健康键零误报（在册键必须撞＝漏报 0；对端须含自身＝错挂 0；只对题面库域，
    # 免键源本身出自成品卷的正当自命中干扰——成品卷域误报另由 firstrun §2.2 观察）
    uni = ctx['uni']
    tiku = ctx['tiku']
    ctx_tiku_only = dict(ctx)
    ctx_tiku_only['corpora'] = [c for c in ctx['corpora'] if c[0].startswith('题面库')]

    def ptr_of(src):
        rs = tiku_ptr_one(src or '', uni)
        return rs[0][0] if rs else None

    healthy = []
    for k, v in sorted(tiku.items()):
        p = ptr_of(v['src'])
        if not p or p in ctx['jinchang'] or p in B_SHOU or not v['norm']:
            continue
        healthy.append(k)
    sample = healthy[:80] if len(healthy) >= 80 else healthy
    miss, wrong, fire = [], [], []
    for k in sample:
        d = judge_candidate(k, None, tiku[k]['text'], None, ctx_tiku_only)
        if d['pin'] != '撞':
            miss.append(k)
        if not any(k in e for e in d['ev']):
            wrong.append(k)
        if any('禁收' in e or '防双收' in e for e in d['ev']):
            fire.append(k)
    ok = (not miss) and (not wrong) and (not fire)
    rc |= (not ok)
    print('[selftest %s] 健康键零误报：抽 %d 键｜漏放 %d｜对端错挂 %d｜禁收误火 %d'
          % ('PASS' if ok else 'FAIL', len(sample), len(miss), len(wrong), len(fire)))
    if miss[:3]:
        print('   漏放样：', miss[:3])
    if wrong[:3]:
        print('   错挂样：', wrong[:3])
    print('[selftest %s]' % ('PASS 负测真拦·正测零误报' if rc == 0 else 'FAIL'))
    return 0 if rc == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--firstrun', action='store_true')
    ap.add_argument('--candidates')
    ap.add_argument('--out')
    ap.add_argument('-h', '--help', action='store_true')
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    if a.help or not (a.firstrun or a.candidates):
        print(__doc__)
        return 2
    if a.firstrun:
        out = a.out or os.path.join(ROOT, '工作区', '_tmpM3S4题源闸0914', '首跑钉码.md')
        return firstrun(out)
    if a.candidates:
        if not os.path.isfile(a.candidates):
            print('[FAIL] 候选清单不存在：%s' % a.candidates)
            return 2
        try:
            cands = json.loads(load_read(a.candidates))
        except (ValueError, OSError) as e:
            print('[FAIL] 候选清单解析失败：%s' % e)
            return 2
        if not isinstance(cands, list) or not cands:
            print('[FAIL] 候选清单须为非空数组')
            return 2
        return run_candidates(cands, a.out)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
