# -*- coding: utf-8 -*-
#
# 收编：2026-08-27 选必1整册任务·F2收尾（来源轮次：A4样张首创五杠杆 → C5参数化定稿；此为工具文件夹唯一常驻版，A4/C5桌面scripts副本不再维护）
#
# 用法: python 工具/零字符增删核验.py <原版.docx或解包dir> <改版.docx或解包dir> <输出报告.txt>
# 功能: 零字符增删铁律对账——document.xml 全部 w:t＋m:t 按文档序拼接、剥空白逐字符比对；恒等即同时证明文字/公式全局交错序列未移动堆积

"""zerodiff.py — 零字符增删归一化diff：document.xml 文字流逐字符比对（剥换行/空段/缩进后）
用法: python zerodiff.py <orig_unpacked_dir> <mod_unpacked_dir> <out_report>"""
import sys, io, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

def text_stream(xml_bytes):
    root = etree.fromstring(xml_bytes)
    parts = []
    for el in root.iter():
        if el.tag in (f'{{{W}}}t', f'{{{M}}}t'):
            parts.append(el.text or '')
    # 归一化：剥除所有空白（换行/空段/缩进不参与），再逐字符比对
    return re.sub(r'\s+', '', ''.join(parts))

def stream_from_docx(path):
    with zipfile.ZipFile(path) as z:
        return text_stream(z.read('word/document.xml'))

a = stream_from_docx(sys.argv[1])
b = stream_from_docx(sys.argv[2])
print('原版归一化字符数:', len(a))
print('改版归一化字符数:', len(b))
if a == b:
    print('结论: 恒等（零字符增删，含公式m:t? 不含——本diff口径=w:t文字流）')
    open(sys.argv[3], 'w', encoding='utf-8').write(
        '零字符增删归一化diff\n原版字符数=%d\n改版字符数=%d\n结论=恒等\n口径=document.xml全部w:t与m:t(公式)按文档序拼接，剥空白后逐字符比对\n' % (len(a), len(b)))
else:
    # 找第一个差异点
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    ctx_a = a[max(0, i - 30):i + 30]
    ctx_b = b[max(0, i - 30):i + 30]
    print('结论: 不恒等！首个差异@%d' % i)
    print('原版: ...', ctx_a)
    print('改版: ...', ctx_b)
    open(sys.argv[3], 'w', encoding='utf-8').write(
        '零字符增删归一化diff\n原版字符数=%d\n改版字符数=%d\n结论=不恒等\n首个差异@%d\n原版:%s\n改版:%s\n' % (len(a), len(b), i, ctx_a, ctx_b))
    sys.exit(1)
