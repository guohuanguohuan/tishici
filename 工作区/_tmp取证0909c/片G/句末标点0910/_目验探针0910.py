# -*- coding: utf-8 -*-
r"""句末标点0910 目验探针：转后「.」形态/字距 vs 既有「.」；题号/序号位「．」在场。
① 数值面＝pymupdf rawdict 逐字符 bbox：目标字符 advance 宽（x1-x0）＋与前后字符墨隙，同页同字号对照；
② 目验面＝按命中片段 bbox 裁片，600dpi 渲染存本目录（ReadMediaFile 目验墨点形态/字距）。
"""
import os
import re
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = r'C:\提示词\工作区\字替对照-0909\variantF\main.pdf'
doc = pymupdf.open(PDF)
print('pages', doc.page_count,
      '| PDF 内 U+FF0E', sum(doc[p].get_text().count('\uff0e') for p in range(doc.page_count)),
      '| U+3002', sum(doc[p].get_text().count('\u3002') for p in range(doc.page_count)))


def chars(pno):
    """页内逐字符流（剔空白，阅读序）：[(char, rect, size, font, line_bbox)]。"""
    out = []
    for b in doc[pno - 1].get_text('rawdict')['blocks']:
        for ln in b.get('lines', []):
            for sp in ln['spans']:
                for c in sp['chars']:
                    if c['c'].strip():
                        out.append((c['c'], pymupdf.Rect(c['bbox']), sp['size'], sp['font'],
                                    pymupdf.Rect(ln['bbox'])))
    return out


def hits_of(cs, pat):
    key = [ch for ch in pat if not ch.isspace()]
    return [i for i in range(len(cs) - len(key) + 1)
            if [c[0] for c in cs[i:i + len(key)]] == key]


def report(tag, pno, pat):
    cs = chars(pno)
    key = [ch for ch in pat if not ch.isspace()]
    hs = hits_of(cs, pat)
    print(f'\n== {tag}｜p{pno}｜{pat!r} 命中 {len(hs)} 处')
    for h in hs:
        seg = cs[h:h + len(key)]
        di = max(i for i, s in enumerate(seg) if s[0] in ('.', '\uff0e'))
        ch, r, size, font, _lb = seg[di]
        p = seg[di - 1]
        n = seg[di + 1] if di + 1 < len(seg) else None
        line = f'  「{ch}」x{r.x0:.2f}-{r.x1:.2f} y{r.y0:.2f} size={size:.2f}pt {font} advance={r.x1 - r.x0:.2f}pt'
        line += f'｜前字={p[0]!r} 左墨隙={r.x0 - p[1].x1:+.2f}pt'
        if n:
            line += f'｜后字={n[0]!r} 右墨隙={n[1].x0 - r.x1:+.2f}pt'
        else:
            line += '｜行末'
        print(line)
    return hs


def crop(tag, pno, pat, dpi=600, pad=2.5):
    cs = chars(pno)
    hs = hits_of(cs, pat)
    if not hs:
        print(f'裁片失败：p{pno} 未命中 {pat!r}')
        return
    key = [ch for ch in pat if not ch.isspace()]
    seg = cs[hs[0]:hs[0] + len(key)]
    x0 = min(s[1].x0 for s in seg) - pad
    x1 = max(s[1].x1 for s in seg) + pad
    y0 = min(s[1].y0 for s in seg) - pad
    y1 = max(s[1].y1 for s in seg) + pad
    pix = doc[pno - 1].get_pixmap(dpi=dpi, clip=pymupdf.Rect(x0, y0, x1, y1))
    out = os.path.join(HERE, tag)
    pix.save(out)
    print(f'裁片 {tag}  {pix.width}x{pix.height}px  clip=({x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f}) @{dpi}dpi')


print('\n########## 一、转后句末「.」（6f 转换位） ##########')
report('6f转·知识点1 定义收口', 1, '叫做空间向量.')
report('6f转·条目(1) 字母表示收口', 1, 'cdots表示.')
report('6f转·判断题干收口', 1, '两个向量相等.')
report('6f转·判断题解析收口', 1, '故.')
report('6f转·答案句收口（选B）', 7, '，选B.')
print('\n########## 二、既有「.」（6e/H3 自撰句已转，对照基准） ##########')
report('6e旧转·编注收口（易错点）', 1, '念题易错点.')
report('6e旧转·编注收口（混淆）', 1, '避免混淆.')
report('6e旧转·小结收口（接）', 1, '衔接.')
print('\n########## 三、题号/序号位「．」未动 ##########')
report('K1 检测题号', 7, '1\uff0e[简单(知识点三)]')
report('K2 选项标号（文字型）', 7, 'A\uff0e充分不必要条件')
report('K2 选项标号（数值网格）', 7, 'B\uff0e2')
print('\n########## 四、裁片（600dpi 目验） ##########')
crop('目验1-转后句末点-p1定义收口.png', 1, '的量叫做空间向量.')
crop('目验2-既有句末点对照-p1编注易错点.png', 1, '是概念题易错点.')
crop('目验3-题号序位未动-p7检测1题号.png', 7, '1\uff0e[简单(知识点三)]')
crop('目验4-选项序位未动-p7选项A.png', 7, 'A\uff0e充分不必要条件')
crop('目验5-转后句末点-p7答案选B.png', 7, '，选B.')
