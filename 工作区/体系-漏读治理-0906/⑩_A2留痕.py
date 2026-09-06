# -*- coding: utf-8 -*-
# ⑩轮任务A2：规则件留痕标记。词集命中且语义=「该物已停用/被取代、仅存档备查」的分句，句首加「▽留痕：」。
# 只插入「▽留痕：」5字符，语义零改动；句首已有▽者跳过（幂等）；加前缀后超1000字符按A1同法再拆。
# 歧义句不标，列清单回主会话（见⑩_终报A.md）。
import pathlib, re, json, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
APPLY = (len(sys.argv) > 1 and sys.argv[1] == 'apply')
LONG = 1000
SENSE = '。；！？'
MARK = '▽留痕：'

# (file, anchor) —— 在 anchor 紧前插入 MARK；anchor 必须在全文件唯一
MARKS = [
    ('公共规则.md', 'qwen CLI/codex CLI/opencode 全体出脑、软件与凭证历史保留'),
    ('公共规则.md', '2026-09-06 用户令：外部 CLI 形态全体退役'),
    ('公共规则.md', 'posOffset/allowOverlap 等锚定机制废止'),
    ('公共规则.md', '讲练件四类底纹废止——附则《讲练件底纹减法》'),
    ('公共规则.md', '深蓝字（#1F4E79）废止、全体系不再使用'),
    ('公共规则.md', '**落选题清单已废止**'),
    ('公共规则.md', '原「与执行者恒异族」前提废止（外移文本已落注）'),
    ('附则/主脑协审制.md', '商议体一席原 CLI 形态 2026-09-06 用户令退役'),
    ('附则/多脑调用登记.md', '**外部 CLI 全体退役（2026-09-06 用户令）**'),
    ('附则/多脑调用登记.md', 'qwen CLI（含下文商议体调用块全式与臂执行类'),
    ('附则/多脑调用登记.md', '**任务执行子代理＝平台继承的普通子智能体（2026-09-04用户令废除'),
    ('附则/多脑调用登记.md', '沿革注记：k3→k3-256k'),
    ('附则/多脑调用登记.md', '**商议qwen单脑制（2026-09-04用户令Ⅵ'),
    ('附则/多脑调用登记.md', '「升档 max」之议作废'),
    ('附则/多脑调用登记.md', '公共规则 L180「与执行者恒异族」前提同拍板废止'),
    ('附则/多脑调用登记.md', '**dsh召集禁令（2026-09-03用户拍板dsh彻底出脑）**'),
    ('附则/多脑调用登记.md', '**商议体调用块**：qwen商议体成员态全式'),
    ('附则/多脑调用登记.md', '**臂执行类调用形态（2026-09-04实证，资格门故障修复登记'),
    ('附则/多脑调用登记.md', '**opencode多通道席（2026-09-04用户令；'),
    ('附则/多脑调用登记.md', '**凭证核验（逐轮硬要求）**'),
    ('附则/多脑调用登记.md', '**跨脑复审计轮值指针（2026-09-03立；'),
    ('附则/讲练件底纹减法.md', '原「仅余条目族（现值0处）」句系补挂前态、废止'),
    ('附则/跨脑复审计制.md', '「与执行者恒异族」前提废止）'),
    ('附则/跨脑复审计制.md', '2026-09-06 用户拍板废止「恒异族」前提'),
    ('附则/跨脑复审计制.md', 'qwen CLI/codex/opencode 臂全体退役留痕、族别判读枚举转历史'),
    ('附则/跨脑复审计制.md', '指针制随单脑废止'),
    ('高中同步总控.md', '该文件类型已废止，公共规则第9节'),
    ('00总纲.md', '已退役并删除：新的数学物理单元同步提示词.md'),
]

files = sorted(set(f for f, _ in MARKS))

def split_line(s):
    if len(s) <= LONG:
        return [s]
    prim = [i for i in range(1, len(s)) if s[i-1] in SENSE]
    sec = sorted(set([m.start() for m in re.finditer(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]', s) if m.start() > 0]
                     + [m.start() for m in re.finditer(r'\*\*[^*\n]{1,30}\*\*：', s) if m.start() > 0]))
    cuts, pos = [], 0
    while len(s) - pos > LONG:
        cand = [b for b in prim if pos < b <= pos + LONG] or [b for b in sec if pos < b <= pos + LONG]
        if not cand:
            return None
        b = max(cand); cuts.append(b); pos = b
    parts, prev = [], 0
    for b in cuts + [len(s)]:
        parts.append(s[prev:b]); prev = b
    return parts

before_all, after_all, lines_all = {}, {}, {}
for f in files:
    raw = (ROOT / f).read_bytes()
    assert raw.count(b'\r\n') == raw.count(b'\n') or raw.count(b'\r') == 0, f'{f}: 混合EOL'
    t = raw.decode('utf-8')
    assert MARK not in t, f'{f}: 已存在{MARK}，幂等防护触发'
    before_all[f] = t
    n_marks = 0
    for ff, anchor in MARKS:
        if ff != f:
            continue
        c = t.count(anchor)
        assert c == 1, f'{f}: 锚点非唯一（{c}次）: {anchor[:30]}'
        t = t.replace(anchor, MARK + anchor)
        n_marks += 1
    after_all[f] = t
    # 加前缀后超1000的行按A1同法再拆
    lines = t.split('\r\n') if '\r\n' in t else t.split('\n')
    new_lines, resplit = [], 0
    for L in lines:
        parts = split_line(L)
        if parts is None:
            print(f'!! {f}: 加前缀后无合法断点仍超{LONG}: {L[:40]}'); sys.exit(2)
        if len(parts) > 1:
            resplit += 1
        new_lines.extend(parts)
    lines_all[f] = new_lines
    print(f'{f}: 标记{n_marks}处 再拆{resplit}行 守恒(剥▽前缀+换行)={after_all[f].replace(MARK,"").replace(chr(13),"").replace(chr(10),"") == before_all[f].replace(chr(13),"").replace(chr(10),"")}')

if APPLY:
    for f in files:
        eol = '\r\n' if '\r\n' in after_all[f] or (ROOT / f).read_bytes().count(b'\r\n') > 0 else '\n'
        (ROOT / f).write_bytes(eol.join(lines_all[f]).encode('utf-8'))
    print('APPLIED')
else:
    print('DRYRUN')
