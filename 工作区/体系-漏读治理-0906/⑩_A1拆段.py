# -*- coding: utf-8 -*-
# ⑩轮任务A1：规则件超长行拆段（>1000字符）。语义零改动：只插入换行符，不改不删不增任何字符。
# 断点：句界（。；！？后）为主，款界（①-⑳前、**款名**：前）兜底；贪心装包使每段≤1000字符。
# EOL：目标件均为CRLF，插入行断一律 \r\n。基线对照快照⑩_改前快照，禁git。
import pathlib, re, json, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
APPLY = (len(sys.argv) > 1 and sys.argv[1] == 'apply')
LONG = 1000
CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'
SENSE = '。；！？'

# 规格书列明：7件15行（执行时以脚本实测复核）
TARGETS = ['公共规则.md', '附则/多机协作与工具纪律.md', '附则/多脑调用登记.md',
           '附则/跨脑复审计制.md', '附则/页面与页码细则.md', '附则/PDF导出链.md', '高中同步总控.md']

mapping = {}   # file -> {old_lineno: [new_linenos]}
report = []

def break_positions(s):
    prim, sec = [], []
    for i in range(1, len(s)):
        if s[i-1] in SENSE:
            prim.append(i)
    for m in re.finditer(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]', s):
        if m.start() > 0:
            sec.append(m.start())
    for m in re.finditer(r'\*\*[^*\n]{1,30}\*\*：', s):
        if m.start() > 0:
            sec.append(m.start())
    sec = sorted(set(sec))
    return prim, sec

def split_line(s):
    if len(s) <= LONG:
        return [s]
    prim, sec = break_positions(s)
    cuts = []
    pos = 0
    n = len(s)
    while n - pos > LONG:
        cand = [b for b in prim if pos < b <= pos + LONG]
        if not cand:
            cand = [b for b in sec if pos < b <= pos + LONG]
        if not cand:
            return None  # 无合法断点
        b = max(cand)
        cuts.append(b)
        pos = b
    parts, prev = [], 0
    for b in cuts + [n]:
        parts.append(s[prev:b])
        prev = b
    return parts

total_lines = 0
for rel in TARGETS:
    p = ROOT / rel
    raw = p.read_bytes()
    crlf = raw.count(b'\r\n')
    assert crlf == raw.count(b'\n'), f'{rel}: 非纯CRLF，禁止盲拆'
    text = raw.decode('utf-8')
    lines = text.split('\r\n')
    new_lines, fmap = [], {}
    for idx, L in enumerate(lines, 1):
        body = L  # 不含\r\n
        if len(body) > LONG:
            parts = split_line(body)
            if parts is None:
                print(f'!! {rel} L{idx}: 无合法断点仍超{LONG}，停手回票')
                sys.exit(2)
            new_lines.extend(parts)
            fmap[idx] = list(range(len(new_lines) - len(parts) + 1, len(new_lines) + 1))
            report.append(f'{rel} L{idx}（{len(body)}字符）→ {len(parts)}行: ' +
                          ' / '.join(str(x) for x in fmap[idx]) +
                          '  各段长=' + ','.join(str(len(x)) for x in parts))
            total_lines += 1
        else:
            new_lines.append(body)
            fmap[idx] = [len(new_lines)]
    # 守恒自检：剥换行后逐字符全等
    assert ''.join(lines) == ''.join(new_lines), f'{rel}: 拆段守恒失败'
    if APPLY:
        p.write_bytes('\r\n'.join(new_lines).encode('utf-8'))
    mapping[rel] = fmap

out = {'mapping': mapping}
if APPLY:
    (ROOT / '工作区/体系-漏读治理-0906/⑩_拆段映射.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8', newline='')
md = ['# ⑩轮A1拆段映射表（基线=⑩_改前快照；禁改字，仅插入CRLF换行）', '']
for rel in TARGETS:
    md.append(f'## {rel}')
    for old, newl in mapping[rel].items():
        if len(newl) > 1:
            md.append(f'- L{old} → L{newl[0]}–L{newl[-1]}（{len(newl)}行）')
    md.append('')
md.append('## 拆段明细')
md += [f'- {r}' for r in report]
if APPLY:
    (ROOT / '工作区/体系-漏读治理-0906/⑩_拆段映射表.md').write_text(
        '\r\n'.join(md) + '\r\n', encoding='utf-8', newline='')
print(('APPLY' if APPLY else 'DRYRUN'), '拆段行数:', total_lines)
for r in report:
    print(' ', r)
