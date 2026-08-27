# -*- coding: utf-8 -*-
#
# 收编：2026-08-27 选必1整册任务·F2收尾（来源轮次：A4样张首创五杠杆 → C5参数化定稿；此为工具文件夹唯一常驻版，A4/C5桌面scripts副本不再维护）
#
# 用法: 库文件，被「紧凑化五杠杆改版/短行合并候选与决策/短行合并回退」import（from 紧凑化公共库 import *）
# 功能: OOXML命名空间qn()、body加载、段落文本提取、图/公式对象感知(has_object)等共用解析函数

"""common.py — A4紧凑化样张共用解析库（A4样转子代理，桌面自建）"""
import re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def qn(tag):
    p, t = tag.split(':')
    return '{%s}%s' % ({'w': W, 'm': M, 'wp': WP, 'a': A_NS, 'r': R}[p], t)

def load(path):
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find(qn('w:body'))
    return tree, root, body

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(qn('w:t')))

def has_object(p):
    """图/公式感知：含 blip/imagedata/oMath/drawing/pict 的段绝不当空段删"""
    if len(list(p.iter(qn('w:drawing')))) > 0:
        return True
    if len(list(p.iter(qn('w:pict')))) > 0:
        return True
    if len(list(p.iter(qn('m:oMath')))) > 0:
        return True
    if len(list(p.iter(qn('w:object')))) > 0:
        return True
    return False

def eff_len(s):
    """可视宽度折算：CJK=1，半角=0.5"""
    n = 0.0
    for ch in s:
        n += 1.0 if ord(ch) > 0x2E7F else 0.5
    return n

MARKER_RE = re.compile(
    r'^(（\d{1,2}）|\(\d{1,2}\)|[①②③④⑤⑥⑦⑧⑨⑩]|解[:：]|证明[:：]|法[一二三四五六七八九十\d]+|方法[一二三四五六七八九十\d]+|'
    r'证法[一二三四五六七八九十\d]+|情形[一二三四五六七八九十\d]+|思路[一二三四五六七八九十\d]+|第[一二三四五六七八九十\d]+类|'
    r'[（(]?[ⅠⅡⅢⅣ][)）]?|［方法[一二三四五六七八九十\d]+］|\[方法[一二三四五六七八九十\d]+\])')

LABEL_RE = re.compile(r'^【[^】]{1,20}】')

def is_marker_start(s):
    return bool(MARKER_RE.match(s))

def is_label_start(s):
    return bool(LABEL_RE.match(s))
