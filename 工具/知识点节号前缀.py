# -*- coding: utf-8 -*-
"""知识点节号前缀.py — 高中同步总控任务B「【知识点】值＝教材节号＋规范知识点名」（内容改动，Pass1）：
逐题块取其前方最近教材节标题的节号，在【知识点】值前补「节号＋半角空格」
（形如「2.5.1 椭圆的标准方程」；已带节号前缀的跳过并计数）。仅讲练件/衔接件适用。
节号取最近的上级节标题（二级节与三级节均可；题在三级节下取三级节号）。
用法: python 知识点节号前缀.py <docx> <登记表md>"""
import sys, io, zipfile, re, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'

SEC_RE = re.compile(r'^(\d+\.\d+(?:\.\d+)?)\s+\S')
PREFIXED_RE = re.compile(r'^\d+\.\d+(\.\d+)?\s')

def wtext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def prefix(path, regmd):
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(q('body'))
    els = list(body)
    reg, skipped, errors = [], 0, []
    cur_sec = None   # 最近节号（二级/三级节标题皆更新）
    cur_q = None     # 最近题号（登记用）
    for el in els:
        if tag(el) != 'p':
            continue
        t = wtext(el)
        ms = SEC_RE.match(t)
        if ms and '：' not in t:
            # 教材节标题（题型标题带「：」不更新节号）
            cur_sec = ms.group(1)
            continue
        mq_ = re.match(r'^(\d+)．', t)
        if mq_:
            cur_q = mq_.group(1)
        if '【知识点】' not in t:
            continue
        i = t.find('【知识点】') + len('【知识点】')
        val = t[i:]
        if PREFIXED_RE.match(val.strip()):
            skipped += 1
            continue
        if cur_sec is None:
            errors.append('题%s 前方无节标题，未补前缀' % cur_q)
            continue
        # 在【知识点】后的 w:t 处插入「节号 」
        off = 0
        done = False
        for tt in el.iter(q('t')):
            txt = tt.text or ''
            a, b = off, off + len(txt)
            off = b
            if a <= i <= b:
                tt.text = txt[:i - a] + cur_sec + ' ' + txt[i - a:]
                tt.set(XMLSPACE, 'preserve')
                done = True
                break
        if done:
            reg.append((cur_q, cur_sec))
        else:
            errors.append('题%s 插入失败' % cur_q)
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.kp'
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name, b in parts.items():
        zo.writestr(name, b)
    zo.close()
    for k in range(12):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            time.sleep(6)
    else:
        raise RuntimeError('locked: ' + path)
    with open(regmd, 'w', encoding='utf-8') as f:
        f.write('# 知识点节号前缀登记：%s\n\n' % os.path.basename(path))
        f.write('| 题号 | 补入节号 |\n|---|---|\n')
        for no, sec in reg:
            f.write('| %s | %s |\n' % (no, sec))
        f.write('\n补前缀 %d 处；已带前缀跳过 %d；异常 %d 起。\n' % (len(reg), skipped, len(errors)))
        for e in errors:
            f.write('- ' + e + '\n')
    print('补前缀 %d | 跳过 %d | 异常 %d -> %s' % (len(reg), skipped, len(errors), regmd))
    for e in errors:
        print('  !', e)

if __name__ == '__main__':
    prefix(sys.argv[1], sys.argv[2])
