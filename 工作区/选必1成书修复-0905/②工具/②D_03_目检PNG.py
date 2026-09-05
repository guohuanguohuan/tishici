# -*- coding: utf-8 -*-
"""②D_03_目检PNG.py — ②-D T9 目检件产出（照 ②-C ②C_PNG 做法，前缀 ②D_PNG）。
①COM 导出 post-T9 三件代表（衔接1/上61/89）→ PDF对比/②D后/*.pdf；
②fitz 渲染 → PDF对比/②D_PNG/：
  芯片区＝衔接1【答案】密集页 前|后 对照＋300dpi 芯片放大裁片（后态）；
  标题区＝上61 讲部标题页＋题型标题页（XML 提取标题文本定位，后态）；
  公式密集段＝89 讲部起始页 2 张（后态）。
前态 PDF 源＝②工具/PDF对比/②C后/（②-C 终态导出，pre-T9）。
每件 COM 300s 超时×3 试、超时杀最新 WINWORD 孤儿（重试甲范式）。"""
import sys, io, os, time, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
P_AFTER = os.path.join(HERE, 'PDF对比', '②D后')
P_BEFORE = os.path.join(HERE, 'PDF对比', '②C后')
P_PNG = os.path.join(HERE, 'PDF对比', '②D_PNG')
for d in (P_AFTER, P_PNG):
    os.makedirs(d, exist_ok=True)

FILES = {
    '衔接1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '上61': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '89': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
WJ = '⁠'


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


def export_three():
    import win32com.client
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        for sh, n in FILES.items():
            src = os.path.join(DST, n)
            dst = os.path.join(P_AFTER, n[:-5] + '.pdf')
            if os.path.exists(dst):
                print('   跳过（已在）%s' % sh, flush=True)
                continue
            done = False
            for att in range(1, 4):
                t0 = time.time()
                try:
                    doc = word.Documents.Open(os.path.abspath(src), ReadOnly=True)
                    doc.ExportAsFixedFormat(os.path.abspath(dst), 17)
                    doc.Close(False)
                    print('   OK %s %.0fs' % (sh, time.time() - t0), flush=True)
                    done = True
                    break
                except Exception as e:
                    print('   att%d fail %s' % (att, str(e)[:120]), flush=True)
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
                print('!! 导出失败 %s' % sh, flush=True)
                sys.exit(2)
    finally:
        try:
            word.Quit()
        except Exception:
            pass


def pages_with(pdf, needle, limit=2):
    d = fitz.open(pdf)
    out = []
    for i in range(d.page_count):
        if needle in d[i].get_text():
            out.append(i + 1)
            if len(out) >= limit:
                break
    d.close()
    return out


def render(pdf, pno, outpng, dpi=150, clip=None):
    d = fitz.open(pdf)
    pg = d[pno - 1]
    pm = pg.get_pixmap(dpi=dpi, clip=clip)
    pm.save(outpng)
    d.close()
    print('   PNG', os.path.basename(outpng), flush=True)


def first_title(path, kind):
    """从 post-T9 docx 取首个讲部/题型标题文本（去WJ）。题型识别与 T9 工具同口径
    （C6D4E3 底纹 或 左竖条 pBdr 或 全角冒号）。"""
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


import fitz
print('== ① COM 导出 post-T9 三件 ==', flush=True)
export_three()
print('== ② 芯片区（衔接1 前|后）==', flush=True)
n1 = FILES['衔接1']
aft1 = os.path.join(P_AFTER, n1[:-5] + '.pdf')
bef1 = os.path.join(P_BEFORE, n1[:-5] + '.pdf')
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
# 300dpi 芯片放大裁片（后态，首个命中矩形外扩）
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
print('== ③ 标题区（上61 讲部/题型）==', flush=True)
n2 = FILES['上61']
aft2 = os.path.join(P_AFTER, n2[:-5] + '.pdf')
for kind in ('讲部', '题型'):
    t = first_title(os.path.join(DST, n2), kind)
    assert t, '上61 找不到%s标题' % kind
    pgs2 = pages_with(aft2, t[:12], 1)
    assert pgs2, '上61 %s 标题页定位失败：%s' % (kind, t)
    render(aft2, pgs2[0], os.path.join(P_PNG, '②D_PNG_标题%s_上61_后_p%d.png' % (kind, pgs2[0])))
print('== ④ 公式密集段（89 讲部起始 2 页）==', flush=True)
n3 = FILES['89']
aft3 = os.path.join(P_AFTER, n3[:-5] + '.pdf')
t3 = first_title(os.path.join(DST, n3), '讲部')
pgs3 = pages_with(aft3, t3[:12], 2) if t3 else [2, 3]
for pno in pgs3:
    render(aft3, pno, os.path.join(P_PNG, '②D_PNG_公式_89_后_p%d.png' % pno))
print('DONE', flush=True)
