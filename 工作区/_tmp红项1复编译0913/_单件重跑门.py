# -*- coding: utf-8 -*-
"""红项①复编译后单件重跑门（只读）：承袭 S7 跑门器原判据，仅跑本件，零写盘（不触 json/其它件）。
注：跑门器自带 utf-8 stdout 包装，本壳不再包（双包会让先到的包装器析构时关掉底层 buffer）。"""
import sys, importlib.util
spec = importlib.util.spec_from_file_location(
    "s7", r"C:\提示词\工作区\_tmpS7双断言跑门0913\S7双断言跑门.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
n = m.run_item('导学件/章末-本章总结提升', 'D')
print('\n本件红门数 =', n)
