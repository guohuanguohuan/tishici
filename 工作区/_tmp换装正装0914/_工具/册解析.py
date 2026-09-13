# -*- coding: utf-8 -*-
"""册解析.py — M2 答案册 body.tex 导学区组解析＋件内迁移公共件（M2 换装正装波1·副本树内作业）。

依据：工作区/_tmp换装预备0913/换装方案草案.md §1（锚点迁移法＋成组 \\ansline 键级拆分＋拆分不确定禁猜）、
     副本树/试迁报告.md（课时01 试迁规约 R1/R2/R3）、副本树-测评本/试迁报告-测评本.md（\\ov 随值迁入件内）。
红线：答案册 body.tex／值快照.json 与 M2 成卷正件只读（本模块仅 open('r')）。
组结构（导学区）：连续 `% pair:键` 行＝一组键；组体＝首条 `\\ansline{标签}{值}`（主值行），
     其后同组 `\\ansline{解析}{…}` 等附行随组迁入（attach 规则见 split_group）；章末段为
     `\\dansitem{标签}{值}` 单键行。成组拆分：判组 (N) 序／评组 N．序／探组
     「例1 X；变式1 Y[；变式2 Z]」分隔符拆；拆不出→共键整组迁组首键（禁猜）＋登记。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

BODY = r"C:/提示词/工作区/M2-第1章量产0911/成卷/答案册/body.tex"
SNAP = r"C:/提示词/工作区/M2-第1章量产0911/成卷/答案册/值快照.json"
ANS_STY_DIR = r"C:/提示词/工作区/_tmpM3toolchain0913"          # qp-m3 钉后版（md5 7c393036…）
QP_M3_MD5 = "7c3930362be8a0a2bdf21bbf8ac16573"

RE_PAIR = re.compile(r'^% pair:(\S+)$')
RE_ANSLINE = re.compile(r'^\\ansline\{(.+?)\}\{(.+)\}$')
RE_DANSITEM = re.compile(r'^\\dansitem\{(.+?)\}\{(.+)\}$')


def read(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return f.read()


def parse_book():
    """答案册导学区（【甲】段）→ 有序组表。每组：keys/label/value/extra[(标签,值)]/n_lines。"""
    body = read(BODY)
    lines = body.split('\n')
    i0 = next(i for i, l in enumerate(lines) if l.startswith('% 【甲】'))
    i1 = next(i for i, l in enumerate(lines) if l.startswith('% 【乙】'))
    groups, cur = [], None

    def flush():
        nonlocal cur
        if cur and cur['keys']:
            if cur['label'] is None:
                raise AssertionError('组无主值行：%s' % cur['keys'])
            groups.append(cur)
        cur = None

    for ln in lines[i0 + 1:i1]:
        s = ln.strip()
        m = RE_PAIR.match(s)
        if m:
            if cur is not None and cur['label'] is not None:
                flush()
            if cur is None:
                cur = {'keys': [], 'label': None, 'value': None, 'extra': []}
            cur['keys'].append(m.group(1))
            continue
        if cur is None:
            continue
        m2 = RE_ANSLINE.match(s) or RE_DANSITEM.match(s)
        if m2:
            if cur['label'] is None:
                cur['label'], cur['value'] = m2.group(1), m2.group(2)
            else:
                cur['extra'].append((m2.group(1), m2.group(2)))
        elif s.startswith(('\\qufen', '\\jietitle')):
            flush()
    flush()
    kmap = {}
    for g in groups:
        for k in g['keys']:
            assert k not in kmap, '重键 %s' % k
            kmap[k] = g
    return groups, kmap


def split_group(g, piece):
    """组→{键: 值}（键级拆分·重组恒等断言）；拆不出→共键整组迁组首键（返回并登记 uncertain）。"""
    keys, val = g['keys'], g['value']
    if len(keys) == 1:
        return {keys[0]: val}, None
    # 判组：(N) 序拆（首项可无 (1) 前缀归一）
    if all(re.match(r'^%s-判\d+$' % re.escape(piece), k) for k in keys):
        parts = re.split(r'\\quad\s*(?=\(\d+\))', ' ' + val.strip())
        seq = []
        for p in parts:
            m = re.match(r'\s*(?:\((\d+)\))?\s*(.*)$', p, re.S)
            seq.append((m.group(1), m.group(2).strip()))
        nums = [n for n, _ in seq if n]
        vals = [v for _, v in seq]
        if len(vals) == len(keys) + 1 and len(nums) == len(keys) + 1:
            # 尾键双值（课时02 判组 6 答 5 键——快照判5＝'×\quad (6)√' 双值口径）：
            # 首键起 1:1，末键合并末两值，印面＝末题后 \\ansitem{(5)}{v5}＋\\anssub{(6)}{v6}
            joined_last = '%s\\quad (%s)%s' % (vals[-2], nums[-1], vals[-1])
            out = dict(zip(keys[:-1], vals[:-2]))
            out[keys[-1]] = joined_last
            out['__双值__'] = {'key': keys[-1], 'labels': ['(%s)' % nums[-2], '(%s)' % nums[-1]],
                               'vals': [vals[-2], vals[-1]]}
            return out, None
        if len(vals) == len(keys) and all(vals):
            reasm = '(%s)%s' % (nums[0], vals[0])
            for n, v in zip(nums[1:], vals[1:]):
                reasm += '\\quad (%s)%s' % (n, v)
            assert reasm == val.strip(), '判组重组不等原值：%s' % keys
            return dict(zip(keys, vals)), None
    # 评组：N．序拆
    if all(re.match(r'^%s-评\d+$' % re.escape(piece), k) for k in keys):
        parts = re.split(r'；(?=\d+．)', val)
        if len(parts) == len(keys) and all(parts):
            vals = []
            for p, k in zip(parts, keys):
                m = re.match(r'^(\d+)．\s*(.*)$', p, re.S)
                assert m and m.group(1) == k.rsplit('-', 1)[-1][len('评'):], '评组序不符：%s' % k
                vals.append(m.group(2).strip())
            return dict(zip(keys, vals)), None
    # 探组：例1 X；变式1 Y[；变式2 Z] 分隔符拆（前瞻不耗分隔符→重组＝原串）
    if all(re.match(r'^%s-探\d+-(例1|变式\d)$' % re.escape(piece), k) for k in keys):
        tags = [k.rsplit('-', 1)[-1] for k in keys]
        pat = '；(?=' + '|'.join(re.escape(t) + ' ' for t in tags[1:]) + ')'
        parts = re.split(pat, val)
        if len(parts) == len(keys) and all(p.startswith(t + ' ') for p, t in zip(parts, tags)):
            return {k: p[len(t) + 1:].strip() for k, p, t in zip(keys, parts, tags)}, None
    return None, {'group': keys, 'value': val, '处置': '整组迁组首键 %s，余键 \\anskey 发射同值（禁猜）' % keys[0]}
