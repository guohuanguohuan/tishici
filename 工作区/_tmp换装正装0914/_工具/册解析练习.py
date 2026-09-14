# -*- coding: utf-8 -*-
"""册解析练习.py — M2 答案册 body.tex 【乙】练/【丙】拓 区解析（正装波2·练习本 12 件批插公共件）。

依据：换装方案草案 §1（锚点迁移法）；试迁报告-练习本 §一（练区键级一对一、\ansitem 形、
     解析 6 处随迁、\\anshang 双位档）；义务总表 §一.2（练习本 319 键＝练 160＋拓上 57＋拓下 102）。
红线：body.tex／值快照.json 与 M2 成卷正件只读（本模块仅 open('r')）。
区结构（与导学区册解析.py 分工，不改动波1 文件）：
  【乙】练区：`% pair:练-课时NN-N` ＋ `\ansitem{N}{值}` 主值行＋其后同键 `\ansline{解析}{…}` 附行；
  【丙】拓区：`% pair:拓-NNN` ＋ `\ansitem{NNN}{值}`（057 撤下＝159 键，无附行）。
"""
import io
import re

BODY = r"C:/提示词/工作区/M2-第1章量产0911/成卷/答案册/body.tex"
SNAP = r"C:/提示词/工作区/M2-第1章量产0911/成卷/答案册/值快照.json"
QP_M3_SRC = r"C:/提示词/工作区/_tmpM3toolchain0913/qp-m3.sty"
QP_M3_MD5 = "7c3930362be8a0a2bdf21bbf8ac16573"

RE_PAIR = re.compile(r'^% pair:(\S+)$')
RE_ANSITEM = re.compile(r'^\\ansitem\{(.+?)\}\{(.+)\}$')
RE_ANSLINE = re.compile(r'^\\ansline\{(.+?)\}\{(.+)\}$')


def read(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return f.read()


def _parse_area(lines, area):
    """区行 → 组表：每 `% pair:键` 开新组；主值＝首条 \ansitem；\ansline 附行随组。"""
    groups, cur = [], None
    for ln in lines:
        s = ln.strip()
        m = RE_PAIR.match(s)
        if m:
            assert cur is None or cur['value'] is not None, '%s 组 %s 无主值行即遇下组' % (area, cur)
            if cur:
                groups.append(cur)
            cur = {'keys': [m.group(1)], 'label': None, 'value': None, 'extra': []}
            continue
        if cur is None:
            continue
        m2 = RE_ANSITEM.match(s)
        if m2:
            assert cur['value'] is None, '%s 组 %s 多主值行（键级一对一判据破·停）' % (area, cur['keys'])
            cur['label'], cur['value'] = m2.group(1), m2.group(2)
            continue
        m3 = RE_ANSLINE.match(s)
        if m3:
            assert cur['value'] is not None, '%s 组 %s 附行先于主值行' % (area, cur['keys'])
            cur['extra'].append((m3.group(1), m3.group(2)))
    assert cur is None or cur['value'] is not None, '%s 尾组 %s 无主值行' % (area, cur)
    if cur:
        groups.append(cur)
    return groups


def parse_book_lt():
    """【乙】练＋【丙】拓 → (练组表, 拓组表, kmap)。断言：练 160（10 课时×16）＋拓 159（057 撤下）。"""
    body = read(BODY)
    lines = body.split('\n')
    i_yi = next(i for i, l in enumerate(lines) if l.startswith('% 【乙】'))
    i_bing = next(i for i, l in enumerate(lines) if l.startswith('% 【丙】'))
    i_ding = next(i for i, l in enumerate(lines) if l.startswith('% 【丁】'))
    g_lian = _parse_area(lines[i_yi + 1:i_bing], '练')
    g_tuo = _parse_area(lines[i_bing + 1:i_ding], '拓')
    kmap = {}
    for g in g_lian + g_tuo:
        for k in g['keys']:
            assert k not in kmap, '重键 %s' % k
            kmap[k] = g
    assert len(g_lian) == 160, '练区组数 %d ≠ 160' % len(g_lian)
    assert len(g_tuo) == 159, '拓区组数 %d ≠ 159（057 撤下）' % len(g_tuo)
    for i in range(1, 11):
        ks = [k for k in kmap if re.match(r'^练-课时%02d-\d+$' % i, k)]
        assert len(ks) == 16 and sorted(int(k.rsplit('-', 1)[-1]) for k in ks) == list(range(1, 17)), \
            '练-课时%02d 键账 ≠ 1..16' % i
    assert '拓-057' not in kmap and '拓-001' in kmap and '拓-160' in kmap, '拓域 057 撤下哨位异常'
    return g_lian, g_tuo, kmap


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    gl, gt, km = parse_book_lt()
    nex = sum(len(g['extra']) for g in gl)
    print('练 160 组（附行 解析 %d）｜拓 159 组（附行 %d）｜kmap %d 键'
          % (nex, sum(len(g['extra']) for g in gt), len(km)))
