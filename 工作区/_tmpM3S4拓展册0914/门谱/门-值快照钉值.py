# -*- coding: utf-8 -*-
r"""门-值快照钉值.py — M3 S4 拓展册·值快照逐字＋钉值零漂＋manifest 逐键哈希。

断言面（202 席＝批A10＋批C77＋批D115）：
  A 值快照逐字：main.tex 各键 \ansitem 第二参（花括号平衡取参）≡ convert(台账值) —— 双册 202 键逐字全等
      （台账值＝题面库答案侧「值：」行（批A/D）／定稿批C【答案】行（截「｜【题型】」尾），源文本口径）。
  B 钉值零漂·批A/批D（125 键）：台账值 ≡ 题面库答案侧值行（逐字）；manifest 逐键哈希复算零漂——
      题面哈希 sha256(题面块正文行集) ＋ 答案哈希 sha256(值+'\n'+详解锚行)，配方照抄 题面库/对号门.py。
  C 钉值零漂·批C（77 键）：按 拓区提取.py 同配方复提 定稿 批C-课时10~13 §9.5 拓块【答案】行
      （截「｜【题型】」尾）≡ 台账值 逐字（定稿盘上态 vs 台账 零漂）。
  D 点检：17-01 值含 CJK 括注「C（弦长 8/5）」（源文本比）；两册键集=202 且与守恒门台账同源。
用法: python 门-值快照钉值.py
退出码: 0＝全过；1＝有红。红线：题面库/定稿/工具只读；唯一写件＝门谱/值快照-读数.json（本目录）。
"""
import hashlib
import importlib.util as ilu
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
BASE = ROOT + '/成卷/拓展册'
TB = ROOT + '/成卷/题面库'
DG = ROOT + '/定稿'
HERE = os.path.dirname(os.path.abspath(__file__))

VOLS = {'上册': 87, '下册': 115}
TIKU_FILES = {
 '01': '课时01-坐标法.md', '02': '课时02-倾斜角与斜率.md', '04': '课时04-点斜式与斜截式.md',
 '05': '课时05-两点式与一般式.md', '14': '课时14-2.6.2双曲线性质.md', '15': '课时15-2.7.1抛物线方程.md',
 '16': '课时16-2.7.2抛物线性质.md', '17': '课时17-2.8①压轴综合一.md'}
DGC = {'10': '批C-课时10-2.4曲线与方程.md', '11': '批C-课时11-2.5.1椭圆的标准方程.md',
       '12': '批C-课时12-2.5.2椭圆的几何性质.md', '13': '批C-课时13-2.6.1双曲线的标准方程.md'}

# convert（与生成器同源）
_spec = ilu.spec_from_file_location('gen', 'C:/提示词/工作区/_tmpM3S4拓展册0914/生成册tex.py')
_gen = ilu.module_from_spec(_spec)
_spec.loader.exec_module(_gen)
convert = _gen.convert

reds = []
def check(name, ok, detail=''):
    tag = '绿' if ok else '红'
    print(f'  [{tag}] {name}' + (f'｜{detail}' if detail else ''))
    if not ok:
        reds.append(name)

def braces(s, i):
    """s[i]=='{' → 平衡花括号体与闭位（\\(\\) 等转义不参配平）。"""
    d, j = 0, i
    while j < len(s):
        if s[j] == '\\' and j + 1 < len(s):
            j += 2
            continue
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[i + 1:j], j
        j += 1
    raise ValueError('花括号不配平')

def sha_text(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()

def parse_questions(path):
    """题面侧 → {键: 题面正文行集('\\n' 连)}——照抄 题面库/对号门.py 配方。"""
    text = open(path, encoding='utf-8', newline='').read()
    out, cur = [], None
    for ln in text.splitlines():
        if ln.startswith('### '):
            if cur:
                out.append(cur)
            head = ln[4:]
            key = head.split('｜')[0].strip()
            cur = [key, []]
        elif cur is not None:
            if ln.strip() == '---':
                out.append(cur)
                cur = None
            elif ln.startswith('【注】') or not ln.strip():
                continue
            else:
                cur[1].append(ln)
    if cur:
        out.append(cur)
    return {k: '\n'.join(b) for k, b in out}

def parse_answers(path):
    """答案侧 → {键: (值, 详解锚)}——照抄 题面库/对号门.py 配方。"""
    text = open(path, encoding='utf-8', newline='').read()
    out, cur = [], None
    for ln in text.splitlines():
        m = re.match(r'^% ans:(\S+)\s*$', ln)
        if m:
            if cur:
                out.append(cur)
            cur = [m.group(1), '', '']
        elif cur is not None:
            if ln.startswith('值：'):
                cur[1] = ln[2:].strip()
            elif ln.startswith('详解：'):
                cur[2] = ln[3:].strip()
    if cur:
        out.append(cur)
    return {k: (v, d) for k, v, d in out}

def parse_batchC_vals(fname, nn):
    """定稿批C §9.5 拓块 → {key: 答案行(截「｜【题型】」尾)}——照抄 拓区提取.py 配方。"""
    t = open(os.path.join(DG, fname), encoding='utf-8').read()
    m95 = re.search(r'^### [^\n]*拓展册[^\n]*$', t, re.M)
    if not m95:
        return {}
    nxt = t.find('\n### ', m95.end())
    seg = t[m95.start():nxt if nxt != -1 else len(t)]
    pat = r'^\*{0,2}【(%s-拓[0-9]+)｜([^】]*)】\*{0,2}\s*$' % nn
    out = {}
    ms = list(re.finditer(pat, seg, re.M))
    for i, m in enumerate(ms):
        seat, head = m.group(1), m.group(2)
        if '撤' in head:
            continue
        end = ms[i + 1].start() if i + 1 < len(ms) else len(seg)
        block = seg[m.end():end]
        am = re.search(r'^【答案】(.+)$', block, re.M)
        ans = am.group(1).strip() if am else ''
        ans = re.sub(r'｜【题型】.*$', '', ans).strip()
        seat2 = re.sub(r'^%s-拓' % nn, '', seat)
        slot = seat2.zfill(2) if seat2.isdigit() else seat2
        out['2章-拓-课时%s-%s' % (nn, slot)] = ans
    return out

snapshot = {}
for vol, nseat in VOLS.items():
    print(f'======== {vol}（{nseat} 席）========')
    d = os.path.join(BASE, vol)
    src = open(os.path.join(d, 'main.tex'), encoding='utf-8').read()
    led = json.load(open(os.path.join(d, f'值台账-{vol}.json'), encoding='utf-8'))
    keys, vals = led['keys'], {it['key']: it['值'] for it in led['items']}
    check(f'{vol} 台账 keys≡items 键序', [it['key'] for it in led['items']] == keys, '')

    # ---- A 值快照逐字（tex ansitem ≡ convert(台账值)）----
    tex_vals, order, cur = {}, [], None
    for ln in src.split('\n'):
        mb = re.match(r'\\begin\{ansblock\}\[([^\]]+)\]', ln.strip())
        if mb:
            cur = mb.group(1)
            order.append(cur)
            continue
        ma = re.search(r'\\ansitem\{([^}]+)\}\{', ln)
        if ma and cur:
            body, _ = braces(ln, ma.end() - 1)
            tex_vals[cur] = body
    badA = []
    for k in keys:
        conv, unk = convert(vals[k])
        tv = tex_vals.get(k)
        if tv != conv:
            badA.append(k)
    check(f'A 值快照逐字 {nseat}/{nseat}（\\ansitem≡convert(源值)）', not badA,
          f'漂移{len(badA)}：{badA[:3]}')
    snapshot[vol] = {k: {'源值': vals[k], 'tex值': tex_vals.get(k)} for k in keys}

    # ---- B 钉值零漂（批A/批D 课时：manifest 哈希＋答案侧值行）----
    lessons = ['01', '02', '04', '05'] if vol == '上册' else ['14', '15', '16', '17']
    badB, nb = [], 0
    for les in lessons:
        tf = TIKU_FILES[les]
        mani = json.load(open(os.path.join(TB, 'manifest', f'课时{les}.manifest.json'),
                              encoding='utf-8'))
        qtext = parse_questions(os.path.join(TB, tf))
        aside = parse_answers(os.path.join(TB, tf.replace('.md', '-答案侧.md')))
        ltk = [k for k in keys if f'-课时{les}-' in k]
        for k in ltk:
            h = mani['逐键哈希'].get(k)
            av, ad = aside.get(k, ('', ''))
            if not h or av != vals[k] or sha_text(qtext.get(k, '')) != h['题面'] \
                    or sha_text(av + '\n' + ad) != h['答案']:
                badB.append(k)
            else:
                nb += 1
    check('B 钉值零漂·manifest 逐键哈希＋答案侧值行（批A/批D）', not badB,
          f'{nb} 键零漂｜漂移{len(badB)}：{badB[:3]}')

    # ---- C 批C 复提零漂 ----
    lessonsC = ['10', '11', '12', '13'] if vol == '上册' else []
    if lessonsC:
        badC, nc = [], 0
        for les in lessonsC:
            re_vals = parse_batchC_vals(DGC[les], les)
            ltk = [k for k in keys if f'-课时{les}-' in k]
            for k in ltk:
                if re_vals.get(k) != vals[k]:
                    badC.append(k)
                else:
                    nc += 1
        check('C 批C 定稿复提【答案】行（截题型尾）零漂', not badC,
              f'{nc} 键零漂｜漂移{len(badC)}：{badC[:3]}')

k17 = '2章-拓-课时17-01'
allv = {k: v for vol in VOLS for k, v in snapshot[vol].items()}
print('======== 汇总点检 ========')
check('两册快照合计=202', len(allv) == 202, f'{len(allv)}')
check("D 点检 17-01 源值含 CJK 括注「C（弦长 8/5）」", 'C（弦长 8/5）' in allv[k17]['源值'],
      repr(allv[k17]['源值'])[:80])
check("D 点检 17-01 tex 值存「弦长」括注且括注未被数学化截断", '弦长' in allv[k17]['tex值'],
      repr(allv[k17]['tex值'])[:80])
json.dump(snapshot, open(os.path.join(HERE, '值快照-读数.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('值快照 →', os.path.join(HERE, '值快照-读数.json'))
print()
print('值快照钉值门：', '全绿' if not reds else f'红 {len(reds)} 项：{reds}')
sys.exit(0 if not reds else 1)
