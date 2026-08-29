# -*- coding: utf-8 -*-
"""四类底纹计数.py — 兼容入口（2026-08-29 成书形态拍板由四类扩为六类，已更名
六类底纹计数.py——公共规则§7「六类底纹分开计数」条款：内容标记/题号难度块/结构序号〔节·讲部·题型〕/
块标签〔含行内小标签〕/条目号/条目第一子层）。本文件保留旧名调用入口（其他会话既有命令行不变），
执行同一六类计数与恒等式断言；六类口径与实现见 工具/六类底纹计数.py。
用法: python 四类底纹计数.py <docx> <报告txt>   （＝六类底纹计数.py 同 CLI）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 六类底纹计数 import count

if __name__ == '__main__':
    count(sys.argv[1], sys.argv[2])
