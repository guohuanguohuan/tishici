# -*- coding: utf-8 -*-
"""批5a 互斥机制级扫描：章末件＋学史件 vs 八件 9.x main.tex＋学史样张＋两件互比。
口径照批1 §六：main.tex 去注释后 CJK/数字字符窗扫描，12 字起报（最长公共段合并）。"""
import re
import hashlib
from difflib import SequenceMatcher

BASE = r'C:/提示词/工作区/P1-必修3第9章量产0912/成卷'
NEW = {
    '章末': BASE + '/章末-本章易错过关/main.tex',
    '学史': BASE + '/学史切片/第9章静电学史/main.tex',
}
EIGHT = {
    '9.1导学': BASE + '/导学件/9.1电荷/main.tex',
    '9.2导学': BASE + '/导学件/9.2库仑定律/main.tex',
    '9.3导学': BASE + '/导学件/9.3电场电场强度/main.tex',
    '9.4导学': BASE + '/导学件/9.4静电的防止与利用/main.tex',
    '9.1练习': BASE + '/练习件/9.1电荷/main.tex',
    '9.2练习': BASE + '/练习件/9.2库仑定律/main.tex',
    '9.3练习': BASE + '/练习件/9.3电场电场强度/main.tex',
    '9.4练习': BASE + '/练习件/9.4静电的防止与利用/main.tex',
}
YANGZHANG = {'学史样张': r'C:/提示词/工作区/物理样张0911/学史切片/main.tex'}

MINLEN = 12
CJK_DIGIT = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff0-9]')


def strip_comments(text):
    # 去 % 至行尾注释（\% 不算注释）
    return re.sub(r'(?<!\\)%.*', '', text)


def fingerprint(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    text = strip_comments(text)
    return ''.join(ch for ch in text if CJK_DIGIT.match(ch))


def common_runs(a, b):
    sm = SequenceMatcher(None, a, b, autojunk=False)
    return [(blk.size, a[blk.a:blk.a + blk.size])
            for blk in sm.get_matching_blocks() if blk.size >= MINLEN]


def md5_of(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


pools = {}
for name, path in {**NEW, **EIGHT, **YANGZHANG}.items():
    pools[name] = fingerprint(path)
    print(f'[fp] {name}: {len(pools[name])} CJK/数字字符  md5={md5_of(path)}')

print('\n===== A组：章末件 vs 八件＋学史件＋学史样张 =====')
for name in list(EIGHT) + ['学史', '学史样张']:
    hits = common_runs(pools['章末'], pools[name])
    print(f'--- 章末 vs {name}: {len(hits)} 窗')
    for size, run in hits:
        print(f'    [{size}字] {run}')

print('\n===== B组：学史件 vs 八件（学史件 vs 样张另列 C组） =====')
for name in EIGHT:
    hits = common_runs(pools['学史'], pools[name])
    print(f'--- 学史 vs {name}: {len(hits)} 窗')
    for size, run in hits:
        print(f'    [{size}字] {run}')

print('\n===== C组：学史件 vs 学史样张（骨架继承参考，非互斥对象） =====')
hits = common_runs(pools['学史'], pools['学史样张'])
print(f'--- 学史 vs 学史样张: {len(hits)} 窗')
for size, run in hits:
    print(f'    [{size}字] {run}')

print('\n===== 终态 =====')
print('扫描口径：去注释（\\%保留）→ CJK/数字窗 ≥12 起报（SequenceMatcher 最长公共段）')
