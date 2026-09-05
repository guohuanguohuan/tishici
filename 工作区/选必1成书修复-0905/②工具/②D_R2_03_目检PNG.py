# -*- coding: utf-8 -*-
"""②D_R2_03_目检PNG.py — ②-D 重跑轮 T9 目检件（照 ②D_03 做法，前缀 ②D_PNG）。
0) 清空初跑作废态 ②D后/*.pdf 与 ②D_PNG/*.png（shutil，不动副本目录）。
1) COM 导出 post-T9 四件（衔接1/上61/89/衔接2）→ PDF对比/②D后/。
2) fitz 渲染 → PDF对比/②D_PNG/：
   芯片区＝衔接1 芯片页 前(②C后)|后 对照＋300dpi 放大裁片（后态）；
   标题区＝上61 讲部标题页＋题型标题页（后态）；
   公式密集段＝89 讲部起始 2 页 后态＋前态(②F后) 对照；
   ②-F 还原点复查＝衔接2「2.8.4-7」页 前(②F后)|后(②D后) 对照＋150dpi 像素差。
每件 COM 300s 超时×3 试、超时杀最新 WINWORD 孤儿（重试甲范式）。
"""
import sys, io, os, time, re, zipfile, glob, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
P_AFTER = os.path.join(HERE, 'PDF对比', '②D后')
P_BEFORE_C = os.path.join(HERE, 'PDF对比', '②C后')
P_BEFORE_F = os.path.join(HERE, 'PDF对比', '②F后')
P_PNG = os.path.join(HERE, 'PDF对比', '②D_PNG')

FILES = {
    '衔接1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '上61': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '89': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
    '衔接2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
}
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WJ = '⁠'
def q(t): return '{%s}%s' % (W, t)


def kill_newest_winword():
    try:
        import psutil
        ws = [p for p in psutil.process_iter(['name', 'create_time'])
              if (p.info['name'] or '').upper() == 'WINWORD.EXE']
        ws.sort(key=lambda x: x.info['create_time'], reverse=True)
        if ws:
            ws[0].kill()
            print('   killed orphan WINWORD', ws[0].pid, flush=True)
    except Exception as e:
        print('   kill fail', e, flush=True)


say = print
say('== 0) 清初跑作废态（②D后/②D_PNG）==', flush=True)
for d in (P_AFTER, P_PNG):
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, '*')):
        os.remove(f)
        say('   removed %s' % os.path.basename(f))

say('== 1) COM 导出 post-T9 四件 ==', flush=True)
import win32com.client
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for sh, n in FILES.items():
        src = os.path.join(DST, n)
        dst = os.path.join(P_AFTER, n[:-5] + '.pdf')
        done = False
        for att in range(1, 4):
            t0 = time.time()
            try:
                doc = word.Documents.Open(os.path.abspath(src), ReadOnly=True)
                doc.ExportAsFixedFormat(os.path.abspath(dst), 17)
                doc.Close(False)
                say('   OK %s %.0fs' % (sh, time.time() - t0), flush=True)
                done = True
                break
            except Exception as e:
                say('   att%d fail %s' % (att, str(e)[:120]), flush=True)
                kill_newest_winword()
                time.sleep(20)
                try:
                    word.Quit()
                except Exception:
                    pass
                word = win32com.client.DispatchEx('Word.Application')
                word.Visible = False
                word.DisplayAlerts = 0
        if not done:
            say('!! 导出失败 %s' % sh, flush=True)
            sys.exit(2)
finally:
    try:
        word.Quit()
    except Exception:
        pass

import fitz


def pages_with(pdf, needle, limit=2):
    d = fitz.open(pdf)
    out = []
    for i in range(d.page_count):
        txt = d[i].get_text().replace(WJ, '')
        if needle in txt:
            out.append(i + 1)
            if len(out) >= limit:
                break
    d.close()
    return out


def render(pdf, pno, outpng, dpi=150, clip=None):
    d = fitz.open(pdf)
    pm = d[pno - 1].get_pixmap(dpi=dpi, clip=clip)
    pm.save(outpng)
    d.close()
    say('   PNG %s' % os.path.basename(outpng), flush=True)


def pixdiff(pdf1, pdf2, pno, dpi=150):
    d1, d2 = fitz.open(pdf1), fitz.open(pdf2)
    pm1 = d1[pno - 1].get_pixmap(dpi=dpi)
    pm2 = d2[pno - 1].get_pixmap(dpi=dpi)
    if (pm1.width, pm1.height) != (pm2.width, pm2.height):
        d1.close(); d2.close()
        return None
    s1, s2 = pm1.samples, pm2.samples
    n = len(s1)
    diff = sum(1 for i in range(0, n, 3) if s1[i:i + 3] != s2[i:i + 3])
    d1.close(); d2.close()
    return diff, (pm1.width * pm1.height)


def first_title(path, kind):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    LECT = re.compile(r'^\d+(?:\.\d+)*\s*(?:方法讲解|知识讲解)[｜|]')
    GRP = re.compile(r'^\d+(?:\.\d+){2,}[\s　]+\S')

    def pfill(p):
        ppr = p.find(q('pPr'))
        if ppr is None:
            return None
        sh = ppr.find(q('shd'))
        return sh.get(q('fill')) if sh is not None else None

    def has_bar(p):
        ppr = p.find(q('pPr'))
        if ppr is None:
            return False
        pb = ppr.find(q('pBdr'))
        return pb is not None and pb.find(q('left')) is not None

    for p in doc.find(q('body')).iter(q('p')):
        t = ''.join(tt.text or '' for tt in p.iter(q('t'))).replace(WJ, '')
        if kind == '讲部' and LECT.match(t):
            return t[:20]
        if kind == '题型' and GRP.match(t) and (pfill(p) == 'C6D4E3' or has_bar(p) or '：' in t[:60]):
            return t[:20]
    return None


say('== 2) 芯片区（衔接1 前=②C后 | 后=②D后）==', flush=True)
n1 = FILES['衔接1']
aft1 = os.path.join(P_AFTER, n1[:-5] + '.pdf')
bef1 = os.path.join(P_BEFORE_C, n1[:-5] + '.pdf')
needles = ['【' + WJ + '答' + WJ + '案' + WJ + '】', '【答案】']
pgs = []
for nd in needles:
    pgs = pages_with(aft1, nd, 2)
    if pgs:
        break
assert pgs, '衔接1 找不到答案芯片页'
for pno in pgs:
    render(aft1, pno, os.path.join(P_PNG, '②D_PNG_芯片_衔接1_后_p%d.png' % pno))
    render(bef1, pno, os.path.join(P_PNG, '②D_PNG_芯片_衔接1_前_p%d.png' % pno))
    df = pixdiff(bef1, aft1, pno)
    say('   p%d 像素差 前(②C后)vs后 = %s' % (pno, ('%d（%.3f%%）' % (df[0], 100.0 * df[0] / df[1])) if df else '尺寸不同'))
d = fitz.open(aft1)
rect = None
for nd in needles:
    rl = d[pgs[0] - 1].search_for(nd)
    if rl:
        rect = rl[0]
        break
if rect is not None:
    x0, y0 = max(rect.x0 - 30, 0), max(rect.y0 - 20, 0)
    clip = fitz.Rect(x0, y0, min(rect.x1 + 220, d[pgs[0] - 1].rect.x1), min(rect.y1 + 60, d[pgs[0] - 1].rect.y1))
    render(aft1, pgs[0], os.path.join(P_PNG, '②D_PNG_芯片放大_衔接1_后_p%d.png' % pgs[0]), dpi=300, clip=clip)
d.close()

say('== 3) 标题区（上61 讲部/题型，后态）==', flush=True)
n2 = FILES['上61']
aft2 = os.path.join(P_AFTER, n2[:-5] + '.pdf')
for kind in ('讲部', '题型'):
    t = first_title(os.path.join(DST, n2), kind)
    assert t, '上61 找不到%s标题' % kind
    pgs2 = pages_with(aft2, t[:12], 1)
    assert pgs2, '上61 %s 标题页定位失败：%s' % (kind, t)
    render(aft2, pgs2[0], os.path.join(P_PNG, '②D_PNG_标题%s_上61_后_p%d.png' % (kind, pgs2[0])))

say('== 4) 公式密集段（89 讲部起始 2 页，前=②F后 | 后=②D后）==', flush=True)
n3 = FILES['89']
aft3 = os.path.join(P_AFTER, n3[:-5] + '.pdf')
bef3 = os.path.join(P_BEFORE_F, n3[:-5] + '.pdf')
t3 = first_title(os.path.join(DST, n3), '讲部')
pgs3 = pages_with(aft3, t3[:12], 2) if t3 else [2, 3]
for pno in pgs3:
    render(aft3, pno, os.path.join(P_PNG, '②D_PNG_公式_89_后_p%d.png' % pno))
    render(bef3, pno, os.path.join(P_PNG, '②D_PNG_公式_89_前(②F后)_p%d.png' % pno))
    df = pixdiff(bef3, aft3, pno)
    say('   p%d 像素差 前(②F后)vs后 = %s' % (pno, ('%d（%.3f%%）' % (df[0], 100.0 * df[0] / df[1])) if df else '尺寸不同'))

say('== 5) ②-F 还原点复查（衔接2「2.8.4-7」，前=②F后 | 后=②D后）==', flush=True)
n4 = FILES['衔接2']
aft4 = os.path.join(P_AFTER, n4[:-5] + '.pdf')
bef4 = os.path.join(P_BEFORE_F, n4[:-5] + '.pdf')
pgs4 = pages_with(aft4, '2.8.4-7', 1)
assert pgs4, '衔接2 2.8.4-7 页定位失败'
p4 = pgs4[0]
render(aft4, p4, os.path.join(P_PNG, '②D_PNG_还原点_衔接2_后_p%d.png' % p4))
render(bef4, p4, os.path.join(P_PNG, '②D_PNG_还原点_衔接2_前(②F后)_p%d.png' % p4))
df = pixdiff(bef4, aft4, p4)
say('   p%d 像素差 前(②F后)vs后 = %s' % (p4, ('%d（%.3f%%）' % (df[0], 100.0 * df[0] / df[1])) if df else '尺寸不同'))
d = fitz.open(aft4)
print('   2.8.4-7 所在页文本抽取（去WJ）首 300 字：', flush=True)
print('   ' + d[p4 - 1].get_text().replace(WJ, '')[:300].replace('\n', ' ⏎ '), flush=True)
d.close()
for sh, n in FILES.items():
    dd = fitz.open(os.path.join(P_AFTER, n[:-5] + '.pdf'))
    say('   fitz 页数 %s = %d' % (sh, dd.page_count), flush=True)
    dd.close()
say('DONE', flush=True)
