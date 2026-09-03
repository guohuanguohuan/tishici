# -*- coding: utf-8 -*-
"""子步3 T0 探测：I1/I2 条目块结构 + 六讲练件节结构（只读）"""
import sys, io, re, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def mtext(p): return ''.join(t.text or '' for t in p.iter(qm('t')))

BASE = r'C:\提示词\高中数学\高中数学同步'
FILES = {
    'I1': BASE + r'\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'I2': BASE + r'\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'B': BASE + r'\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': BASE + r'\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E': BASE + r'\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': BASE + r'\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': BASE + r'\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': BASE + r'\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}

ENT_RE = re.compile(r'^(\d+(?:\.\d+)*)-(\d+)．')   # 条目号「节号-序号．」
SEC_HEAD_RE = re.compile(r'^(\d+(?:\.\d+)+)\s')      # 节标题「N.N(.N) 节名 …」
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*方法讲解[｜|]')
SHUXING_RE = re.compile(r'^(\d+(?:\.\d+)+)\s*本节(\d+)题')  # 节标题行统计段

def load(code):
    z = zipfile.ZipFile(FILES[code])
    xml = z.read('word/document.xml')
    root = etree.fromstring(xml)
    body = root.find(q('body'))
    return z, root, body

def probe_jlp(code):
    """讲练件：列出节标题段/讲部标题/题型标题/题号块首段（含body索引、文本头80字）"""
    z, root, body = load(code)
    out = []
    for i, el in enumerate(body):
        if tag(el) != 'p':
            continue
        t = ptext(el)
        if not t.strip():
            continue
        kind = None
        if LECT_RE.match(t):
            kind = '讲部(方法讲解)'
        elif SEC_HEAD_RE.match(t):
            kind = '节/题型标题?'
        if kind:
            out.append((i, kind, t[:90]))
    return out

def probe_list(code):
    """清单件：列出节标题、条目题名行（body索引+文本头）"""
    z, root, body = load(code)
    secs, ents = [], []
    for i, el in enumerate(body):
        if tag(el) != 'p':
            continue
        t = ptext(el)
        if not t.strip():
            continue
        m = ENT_RE.match(t)
        if m:
            ents.append((i, m.group(1), t[:70]))
        elif SEC_HEAD_RE.match(t) and '本节' not in t[:30]:
            secs.append((i, t[:70]))
    return secs, ents

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if which in ('list', 'all'):
        for code in ('I1', 'I2'):
            secs, ents = probe_list(code)
            print(f'===== {code} 节标题 {len(secs)} 个 =====')
            for i, t in secs:
                print(f'  [{i}] {t}')
            print(f'===== {code} 条目 {len(ents)} 条 =====')
            for i, sec, t in ents[:200]:
                print(f'  [{i}] {sec}: {t}')
    if which in ('jlp', 'all'):
        for code in ('B', 'C', 'E', 'F', 'G', 'H'):
            rows = probe_jlp(code)
            print(f'===== {code} 标题类段落 {len(rows)} 个 =====')
            for i, k, t in rows:
                print(f'  [{i}] {k}: {t}')
