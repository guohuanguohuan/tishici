# -*- coding: utf-8 -*-
# ⑩轮返工：R1-5装机坑三款补标＋R2摘要概括刷新（主会话裁决2026-09-06）。
# 语义零改动纪律不变：R1-5仅插「▽留痕：」；R2仅按裁决刷新概括文字。
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
APPLY = (len(sys.argv) > 1 and sys.argv[1] == 'apply')
MARK = '▽留痕：'

# R1-5：装机坑款①②④补标（③Clash切节点现役不标——主会话2026-09-06实证）
R1_MARKS = [
    ('附则/多脑调用登记.md', '①WinGet同名包遮蔽npm版'),
    ('附则/多脑调用登记.md', '②npm allow-scripts拦postinstall'),
    ('附则/多脑调用登记.md', '④**opencode派发设置'),
]

# R2：摘要概括刷新（按共识门现行文）
R2 = [
    ('公共规则·目录摘要.md',
     '商议体＝qwen一席，双向核实至绝对同意；3轮到线按多数；K1块驻附则《多脑调用登记》',
     '商议体＝kimi-code 子智能体一席，双向核实至绝对同意；3轮到线按多数；K1块驻附则《多脑调用登记》'),
    ('公共规则·目录摘要.md',
     '全量子代理一律qwen（qwen3.8-max·思考max，config.toml force=true钉死；唯一例外＝额度尽降级GLM-5.3-Flash·智谱官方端·思考max〔ZH-6，已回填已切换〕）',
     '全量子代理＝主会话 Agent 工具原生派生之 kimi-code 子智能体（当轮模型＝config.toml [secondary_model] 绑定值、思考档钉死 max；梯队与额度降级照 ZH-1/ZH-6）'),
    ('公共规则·目录摘要.md',
     'qwen明显不足只续议/拆小重派/主脑裁决',
     '子代理明显不足只续议/拆小重派/主脑裁决'),
]

files = sorted(set(f for f, _ in R1_MARKS))
before = {}
for f in files:
    t = (ROOT / f).read_bytes().decode('utf-8')
    assert t.count('\r\n') == t.count('\n'), f'{f} 非纯CRLF'
    before[f] = t
    for _, anchor in R1_MARKS:
        if _ != f:
            continue
        c = t.count(anchor)
        assert c == 1, f'{f}: R1-5锚点非唯一({c}): {anchor[:20]}'
    n = sum(1 for ff, a in R1_MARKS if ff == f)
    t2 = t
    for ff, anchor in R1_MARKS:
        if ff == f:
            t2 = t2.replace(anchor, MARK + anchor)
    # 守恒：双侧剥▽后全等（文件已含此前批次标记）；行长复核
    assert t2.replace(MARK, '') == t.replace(MARK, ''), f'{f}: R1-5守恒失败'
    mx = max(len(x) for x in t2.split('\r\n'))
    print(f'{f}: R1-5补标{n}处 最长行={mx} (≤1000: {mx<=1000})')
    if APPLY:
        (ROOT / f).write_bytes(t2.encode('utf-8'))

# R2 摘要
sp = ROOT / '公共规则·目录摘要.md'
s = sp.read_bytes().decode('utf-8')
assert s.count('\r\n') == s.count('\n'), '摘要非纯CRLF'
for ff, old, new in R2:
    assert ff == '公共规则·目录摘要.md'
    c = s.count(old)
    assert c == 1, f'R2锚点非唯一({c}): {old[:24]}'
    s = s.replace(old, new)
print('摘要: R2概括刷新3处（共识门1＋主脑协审制2）')
if APPLY:
    sp.write_bytes(s.encode('utf-8'))
print('APPLIED' if APPLY else 'DRYRUN')
