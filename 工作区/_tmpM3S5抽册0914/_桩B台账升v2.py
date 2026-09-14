# -*- coding: utf-8 -*-
"""桩B 台账 v2 升制脚本（器升制·工单 S5-W1 桩B／军师补强④）。
拓展旧制台账（items[].key/值 渲染形）升 v2：补 值tex（照 main.tex ansitem 逐字提取，
非渲染形换算）＋印面号（seat 原串）＋键型/值源/详解锚；v1 字段零动保留（双读过渡，
sunset＝S5-W3 起器面只读 v2）；containment 钉值硬断言随 v2 落地（值tex 腿激活）。
零动断言：升制前后 v1 字段逐字不变。备份已先行（备份-值台账-*-vW2前-0914.json）。
写入域＝成卷/拓展册/<上|下>册/值台账-<册>.json（桩B 授权）。零 git。
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _s5lib import CJ, T  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

V1_FIELDS = ['key', 'seat', 'num', 'form', 'tier', '值', 'nline_detail']
TOP_V1 = ['件', '口径', 'keys', 'vals']  # items 零动由 V1_FIELDS 逐字段断言承管

for pian in ('上册', '下册'):
    pdir = os.path.join(CJ, '拓展册', pian)
    p = os.path.join(pdir, '值台账-%s.json' % pian)
    d = json.load(open(p, encoding='utf-8'))
    before = json.dumps(d, ensure_ascii=False, sort_keys=True)
    piece = T.parse_piece(pdir)
    by_key = {b['key']: b for b in piece['blocks']}
    # 块键集＝台账键集 前置断言（值tex 提取面与台账同源同集）
    assert set(by_key) == set(it['key'] for it in d['items']), \
        '块键集≠台账键集：%s' % pian
    n_add = 0
    for it in d['items']:
        b = by_key[it['key']]
        assert b['seat'] == it['seat'], 'seat 漂：%s' % it['key']
        it['值tex'] = b['val']                    # 照源 ansitem 值串逐字
        it['印面号'] = b['seat']                  # 桩B：印面号＝seat 原串
        it['键型'] = it.get('form', '')
        it['值源'] = 'main.tex %% ans:%s 锚后 \\ansitem 值串（逐字）' % it['key']
        it['详解锚'] = 'main.tex \\ansnote{详解}{…}（键 %s）' % it['key']
        n_add += 1
    d['制式'] = 'v2'
    d['升制记'] = ('S5-W2(2026-09-14) 桩B 升制：补 值tex/印面号/键型/值源/详解锚；'
                   '值tex 照 main.tex ansitem 逐字提取（非渲染形换算，零换算误差）；'
                   'v1 字段（key/seat/num/form/tier/值/nline_detail）零动保留，'
                   '器面 v1/v2 双读过渡，sunset＝S5-W3 起只读 v2（答案抽册器 LEDGER_SUNSET 同文）；'
                   'containment 钉值腿（册值≡值tex 逐字）随本升制转硬断言（§四.6 一并清偿）')
    d['印面连号制'] = ('分节重启制：节前缀＝键内 课时NN 段，节内 seat 单调有序（T1…／01…），'
                       '节间允许重启，(节,seat) 全册恰一；ansitem 首参＝seat 原串逐字')
    after = json.dumps(d, ensure_ascii=False, sort_keys=True)
    # 零动断言：v1 全字段在升制后读数中保持原值
    d2 = json.loads(before)
    for it_old in d2['items']:
        it_new = next(x for x in d['items'] if x['key'] == it_old['key'])
        for f in V1_FIELDS:
            assert it_new.get(f) == it_old.get(f), 'v1 字段漂移：%s.%s' % (it_old['key'], f)
    for k in TOP_V1:
        assert json.dumps(d[k], ensure_ascii=False, sort_keys=True) == \
            json.dumps(d2[k], ensure_ascii=False, sort_keys=True), '顶层 v1 段漂移：%s' % k
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%s：items %d 键升 v2（值tex/印面号/键型/值源/详解锚），v1 零动断言过 → %s'
          % (pian, n_add, p))
print('桩B 升制毕（containment 硬断言＝值tex 腿，器面已激活）')
