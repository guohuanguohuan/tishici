# -*- coding: utf-8 -*-
"""阶段7子进程：N11签名单元测试（导入工具模块取SEC_RE，行尾统计段兼容用例）。"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import importlib.util

spec = importlib.util.spec_from_file_location('jdb', r'C:\Users\28120\Desktop\提示词\工具\节页码定位.py')
jdb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jdb)
# 工具模块导入时会替换 sys.stdout 包装——重新接管fd=1，防旧wrapper被GC关闭
sys.stdout = io.TextIOWrapper(os.fdopen(1, 'wb', closefd=False), encoding='utf-8', line_buffering=True)
cases = [
    ('2.4 曲线与方程（第101—119题）', True, '2.4'),
    ('2.4 曲线与方程（第101—119题）　本节19题：简单1｜中档12｜难6', True, '2.4'),
    ('1.1.2 空间向量基本定理（第3—8题） 本节6题：简单2｜中档4', True, '1.1.2'),
    ('2.4 曲线与方程（第101—119题）　本节19题：简单1｜中档12｜难6 ', True, '2.4'),
    ('2.4 曲线与方程（第101—119题）随便其他尾巴', False, None),      # 非统计段尾巴不认
    ('本节19题：简单1（第101—119题）', False, None),                 # 节号缺失
]
allpass = True
for txt, want, no in cases:
    m = jdb.SEC_RE.match(txt)
    got = bool(m) and (m.group(1) == no)
    allpass &= (got == want)
    print('  %s %r -> %s' % ('PASS' if got == want else 'FAIL', txt[:44], m.group(1) if m else '不命中'))
assert allpass, 'N11签名单元测试未全过'
print('阶段7完成：6用例全过（含N11行尾统计段2例正命中＋2负例拒绝）')
