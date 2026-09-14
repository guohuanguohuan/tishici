# -*- coding: utf-8 -*-
r"""拓区提取.py — M3 S4 拓展册汇编·拓区 221 题次（本轮实收编 202＋章末 19 缺料）数据提取。
源（全只读）：
  题面库 批A（课时01/02/04/05 拓 10 键）＋批D（课时14~17 拓 115 键）：题面＋形态＋族名＋难度；
  题面库 -答案侧：值（% ans: 锚下「值：」行，逐字）；
  定稿 批A/批D 同课时件：拓块【详解】（印面详解源）；
  定稿 批C（课时10~13）§9.5 拓块：题面／【答案】／【详解】／【题型】（77 席；题面库片未含拓键，
        键名按批D 实排式回填＝2章-拓-课时NN-两位席号，报备键务臂）。
章末 19 席（2章-拓-章末-01~19）：题面库无键、定稿无件（批E-台账仅有池分配账）→ 缺料不收编，登记残余。
输出：工作区/_tmpM3S4拓展册0914/拓区数据.json ＋ 提取报告.txt（写入域内）。
红线：零 git；题面库/定稿只读；本脚本只写 _tmpM3S4拓展册0914/。
"""
import io, json, os, re, sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
TB = ROOT + '/成卷/题面库'
DG = ROOT + '/定稿'
OUT = 'C:/提示词/工作区/_tmpM3S4拓展册0914'

KAOSHI = {  # 课时→(节, 课名, 册)
 '01': ('2.1', '坐标法'), '02': ('2.2', '倾斜角与斜率'), '04': ('2.2', '点斜式与斜截式'),
 '05': ('2.2', '两点式与一般式'), '10': ('2.4', '曲线与方程'), '11': ('2.5.1', '椭圆的标准方程'),
 '12': ('2.5.2', '椭圆的几何性质'), '13': ('2.6.1', '双曲线的标准方程'),
 '14': ('2.6.2', '双曲线的性质'), '15': ('2.7.1', '抛物线方程'), '16': ('2.7.2', '抛物线的性质'),
 '17': ('2.8', '压轴综合一（2.8①）')}
SHANG = ['01', '02', '04', '05', '10', '11', '12', '13']
XIA = ['14', '15', '16', '17']

def rd(p):
    return open(p, encoding='utf-8').read()

rep = []
def log(s):
    rep.append(s)
    print(s)

def seatnat(seat):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', seat)]

# ---------- ① 题面库 片（批A/批D 拓键） ----------
def parse_tiku(fname):
    """返回 [(key, 形态, 族名, 难度raw, 源, body)]；body＝### 与 --- 间文本。"""
    t = rd(os.path.join(TB, fname))
    out = []
    for m in re.finditer(r'^### (2章-[\u4e00-\u9fffA-Za-z0-9\-]+)｜(.+?)$', t, re.M):
        key, head = m.group(1), m.group(2)
        if '-拓-' not in key:
            continue
        parts = [p.strip() for p in head.split('｜')]
        形态, 族名, 难度, 源 = parts[0], parts[1], parts[2], (parts[3] if len(parts) > 3 else '')
        start = m.end()
        nxt = t.find('\n### ', start)
        end = t.find('\n---', start)
        if nxt != -1 and (end == -1 or nxt < end):
            end = nxt
        body = t[start:end if end != -1 else len(t)].strip('\n')
        out.append(dict(key=key, 形态=形态, 族名=族名, 难度raw=难度, 源=源, body=body))
    return out

def parse_dangan(fname):
    """答案侧：% ans:键 → 值行（逐字）。"""
    t = rd(os.path.join(TB, fname))
    vals = {}
    for m in re.finditer(r'^% ans:(\S+)\n值：(.+)$', t, re.M):
        vals[m.group(1)] = m.group(2).strip()
    return vals

# ---------- ② 定稿 拓块详解（批A/批D） ----------
def parse_dg_tuoku(fname, tag):
    """批A:【01-T1｜拓展｜…】；批D:【拓14-01｜课时14·拓展…】→ {席标签: {'答案':…,'详解':[…],'注':…}}"""
    t = rd(os.path.join(DG, fname))
    pat = r'^【(%s-[A-Za-z0-9\-]+)｜([^】]*)】\s*$' % tag
    out = {}
    ms = list(re.finditer(pat, t, re.M))
    for i, m in enumerate(ms):
        seat, head = m.group(1), m.group(2)
        end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
        block = t[m.end():end]
        if '撤' in head and ('不设题' in head or '让位' in head or '撤位' in head or '撤席' in head):
            out[seat] = dict(撤位=True, head=head, 注=block.strip())
            continue
        am = re.search(r'^【答案】(.+)$', block, re.M)
        dm = re.search(r'^【详解】(.+?)(?=^【[^详]|\Z)', block, re.M | re.S)
        if dm is None:
            dm = re.search(r'^【详解】(.+)\Z', block, re.M | re.S)
        lines = []
        if dm:
            for ln in dm.group(1).split('\n'):
                ln = ln.rstrip()
                st = ln.strip()
                if not st:
                    lines.append('')
                    continue
                if st.startswith('#') or st.startswith('**'):
                    break
                if re.match(r'^〔.*〕\s*$', st) or re.match(r'^（源详解照录.*）$', st):
                    continue
                lines.append(st)
            while lines and not lines[-1]:
                lines.pop()
        note = ''
        for patn in (r'^【注】(.+)$', r'^【互斥注记】(.+)$'):
            nm = re.search(patn, block, re.M)
            if nm:
                note = nm.group(1).strip()
        out[seat] = dict(撤位=False, head=head,
                         答案=(am.group(1).strip() if am else ''),
                         详解=lines, 注=note, 全块=block)
    return out

# ---------- ③ 批C §9.5 拓块 ----------
def parse_batchC(fname, nn):
    t = rd(os.path.join(DG, fname))
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
        end = ms[i + 1].start() if i + 1 < len(ms) else len(seg)
        block = seg[m.end():end]
        if '撤' in head:
            out[seat] = dict(撤位=True, head=head, 注=block.strip())
            continue
        am = re.search(r'^【答案】(.+)$', block, re.M)
        dm = re.search(r'^【详解】(.+?)(?=^【[^详]|\Z)', block, re.M | re.S)
        if dm is None:
            dm = re.search(r'^【详解】(.+)\Z', block, re.M | re.S)
        lines = []
        if dm:
            for ln in dm.group(1).split('\n'):
                ln = ln.rstrip()
                st = ln.strip()
                if not st:
                    lines.append('')
                    continue
                if st.startswith('#') or st.startswith('**'):
                    break
                if re.match(r'^〔.*〕\s*$', st) or re.match(r'^（源详解照录.*）$', st):
                    continue
                lines.append(st)
            while lines and not lines[-1]:
                lines.pop()
        meta = ''
        mm = re.search(r'^【题型】(.+)$', block, re.M)
        if mm:
            meta = mm.group(1).strip()
        note = ''
        nm = re.search(r'｜【注】(.+)$', meta)
        if nm:
            note = nm.group(1).strip()
            meta = meta[:nm.start()].strip()
        meta = re.sub(r'｜【亲算】.*$', '', meta).strip()
        答案 = am.group(1).strip() if am else ''
        答案 = re.sub(r'｜【题型】.*$', '', 答案).strip()
        out[seat] = dict(撤位=False, head=head,
                         题面=None, 答案=答案, 详解=lines, 题型=meta, 注=note, 全块=block)
    return out

def block_stem(block):
    """从定稿拓块取题面：首个【答案】前、去头部【答案】/【详解】外的正文。"""
    m = re.search(r'^【答案】', block, re.M)
    body = block[:m.start()] if m else block
    lines = []
    for ln in body.split('\n'):
        s = ln.strip()
        if not s:
            continue
        if re.match(r'^【(注|互斥注记|题型|亲算)', s):
            break
        lines.append(s)
    return lines

# ================= 组装 =================
seats = []
notehu = []  # 让位/撤席注记抄件

def add(seat):
    seats.append(seat)

TIKU_FILES = {
 '01': '课时01-坐标法.md', '02': '课时02-倾斜角与斜率.md', '04': '课时04-点斜式与斜截式.md',
 '05': '课时05-两点式与一般式.md', '14': '课时14-2.6.2双曲线性质.md', '15': '课时15-2.7.1抛物线方程.md',
 '16': '课时16-2.7.2抛物线性质.md', '17': '课时17-2.8①压轴综合一.md'}

DG_TUOKU = {
 '01': ('批A-课时01-坐标法.md', '01'), '02': ('批A-课时02-倾斜角与斜率.md', '02'),
 '04': ('批A-课时04-点斜式与斜截式.md', '04'), '05': ('批A-课时05-两点式与一般式.md', '05'),
 '14': ('批D-课时14-2.6.2双曲线性质.md', '拓14'), '15': ('批D-课时15-2.7.1抛物线方程.md', '拓15'),
 '16': ('批D-课时16-2.7.2抛物线性质.md', '拓16'), '17': ('批D-课时17-2.8①压轴综合一.md', '拓17')}

DGC = {'10': '批C-课时10-2.4曲线与方程.md', '11': '批C-课时11-2.5.1椭圆的标准方程.md',
       '12': '批C-课时12-2.5.2椭圆的几何性质.md', '13': '批C-课时13-2.6.1双曲线的标准方程.md'}

for nn in ['01', '02', '04', '05', '14', '15', '16', '17']:
    blocks = parse_tiku(TIKU_FILES[nn])
    vals = parse_dangan(TIKU_FILES[nn].replace('.md', '-答案侧.md'))
    df, tag = DG_TUOKU[nn]
    dgb = parse_dg_tuoku(df, tag)
    for b in blocks:
        key = b['key']
        seat = key.split('课时%s-' % nn, 1)[1]
        v = vals.get(key)
        if nn in ('01', '02', '04', '05'):
            dkeys = ['%s-%s' % (nn, seat)]
        else:
            dkeys = ['拓%s-%s' % (nn, seat), '拓%s-%s' % (nn, seat.zfill(2))]
        d = None
        for dk in dkeys:
            if dk in dgb:
                d = dgb[dk]
                break
        add(dict(key=key, 批=('批A' if nn in SHANG[:4] else '批D'), 课时=nn, seat=seat,
                 形态=b['形态'], 族名=b['族名'], 难度raw=b['难度raw'], 源=b['源'],
                 题=[l for l in b['body'].split('\n') if l.strip()],
                 值=v, 详解=(d or {}).get('详解'), dg答案=(d or {}).get('答案'),
                 注=(d or {}).get('注', ''), 撤位=False))

for nn in ['10', '11', '12', '13']:
    dgb = parse_batchC(DGC[nn], nn)
    for seat in sorted(dgb, key=seatnat):
        d = dgb[seat]
        if d.get('撤位'):
            notehu.append('%s-%s（撤位登记）：%s' % (nn, seat, (d.get('注') or d.get('head'))[:120]))
            continue
        题 = block_stem(d['全块'])
        # 去题面内【注】行（账面，不入印面）
        题 = [l for l in 题 if not l.startswith('【注】')]
        难raw = d['head'].split('｜')[-1].strip()
        源 = d['head'].split('｜')[2] if d['head'].count('｜') >= 2 else ''
        seat2 = re.sub(r'^%s-拓' % nn, '', seat)
        slot = seat2.zfill(2) if seat2.isdigit() else seat2
        add(dict(key='2章-拓-课时%s-%s' % (nn, slot),
                 批='批C', 课时=nn, seat=slot,
                 形态='', 族名=d.get('题型', ''), 难度raw=难raw, 源=源,
                 题=题, 值=d['答案'], 详解=d['详解'], dg答案=d['答案'],
                 注=d.get('注', ''), 撤位=False))
    # 撤位席注记（拓1/拓2）
    for seat, d in dgb.items():
        if d.get('撤位'):
            pass

log('提取读数：总席 %d' % len(seats))
from collections import Counter
c = Counter(s['课时'] for s in seats)
log('分课时：' + '，'.join('%s:%d' % (k, c[k]) for k in sorted(c)))
log('批A=%d 批C=%d 批D=%d' % (sum(1 for s in seats if s['批'] == '批A'),
                              sum(1 for s in seats if s['批'] == '批C'),
                              sum(1 for s in seats if s['批'] == '批D')))
miss = [s['key'] for s in seats if not s.get('值')]
log('缺值席：%s' % (miss if miss else '无'))
missd = [s['key'] for s in seats if not s.get('详解')]
log('缺详解席：%s' % (missd if missd else '无'))
nogroup = [s['key'] for s in seats if not s.get('族名')]
log('缺族名席：%s' % (nogroup if nogroup else '无'))

json.dump(dict(seats=seats, notehu=notehu), open(os.path.join(OUT, '拓区数据.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
open(os.path.join(OUT, '提取报告.txt'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
log('JSON 已落盘：%s/拓区数据.json' % OUT)
