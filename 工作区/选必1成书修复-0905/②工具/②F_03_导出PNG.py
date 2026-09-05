# -*- coding: utf-8 -*-
"""②F_03_导出PNG.py — ②-F 目检件产出＋自动渲染证。
①前源＝同步盘（②-C 终态，未修复）复制 3 件 → PDF对比/②F前源/；后源＝副本（修复态）。
②COM 导出 前/后 各 3 件（衔接2(13题)/下79/89）→ PDF对比/②F前|②F后/。
③fitz 自动渲染证：逐还原实例取其 m:t 文本指纹片段，定位后 PDF 题号锚页，
  验「片段在后页出现、前页同锚页无」；检出不了者列人工 PNG 判读。
④渲染 PNG（150dpi）→ PDF对比/②F_PNG/②F_PNG_*.png：衔接2 p1–3（任务指定）＋还原锚页；下79 汉堡模型页＋双公式还原页；89 双公式还原页。
落盘 → 报告/②F_03_目检.md"""
import sys, io, os, re, shutil, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\提示词\工具')
import 公式元素还原器 as FX

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SYNC = os.path.join(ROOT, '高中数学', '高中数学同步')
DST = os.path.join(HERE, '副本')
P_PRE_SRC = os.path.join(HERE, 'PDF对比', '②F前源')
P_BEFORE = os.path.join(HERE, 'PDF对比', '②F前')
P_AFTER = os.path.join(HERE, 'PDF对比', '②F后')
P_PNG = os.path.join(HERE, 'PDF对比', '②F_PNG')
for d in (P_PRE_SRC, P_BEFORE, P_AFTER, P_PNG):
    os.makedirs(d, exist_ok=True)

NAMES = [
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', ['2.8.4-7', '2.8.8-13']),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', ['1.2.5.4.4-8', '1.2.5.19.19-50']),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', ['2.8.8-10', '2.8.10-13', '2.8.11-16']),
]
OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)


def copy_sync(n):
    s = os.path.join(SYNC, n)
    d = os.path.join(P_PRE_SRC, n)
    for att in range(8):
        try:
            if os.path.exists(d):
                os.remove(d)
            shutil.copy2(s, d)
            return d
        except PermissionError:
            time.sleep(6)
    raise RuntimeError('同步盘复制持续锁: ' + n)


def norm_ws(s):
    return re.sub(r'\s+', '', s)


def pages_with(pdf, needle, limit=3):
    import fitz
    d = fitz.open(pdf)
    out = []
    for i in range(d.page_count):
        if needle in norm_ws(d[i].get_text()):
            out.append(i + 1)
            if len(out) >= limit:
                break
    d.close()
    return out


def render(pdf, pno, outpng):
    import fitz
    d = fitz.open(pdf)
    d[pno - 1].get_pixmap(dpi=150).save(outpng)
    d.close()
    say('   PNG %s' % os.path.basename(outpng))


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


def word_export(pairs):
    import win32com.client
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    ok = {}
    try:
        for src, dst in pairs:
            done = False
            for att in range(1, 4):
                t0 = time.time()
                try:
                    doc = word.Documents.Open(os.path.abspath(src), ReadOnly=True)
                    doc.ExportAsFixedFormat(os.path.abspath(dst), 17)
                    doc.Close(False)
                    say('   OK %s %.0fs' % (os.path.basename(dst)[:40], time.time() - t0))
                    done = True
                    break
                except Exception as e:
                    say('   att%d fail %s' % (att, str(e)[:120]))
                    kill_newest_winword()
                    time.sleep(20)
                    try:
                        word.Quit()
                    except Exception:
                        pass
                    word = win32com.client.DispatchEx('Word.Application')
                    word.Visible = False
                    word.DisplayAlerts = 0
            ok[src] = done
    finally:
        try:
            word.Quit()
        except Exception:
            pass
    return ok


say('== ① 前源复制（同步盘 ②-C 终态）==')
pre_src = {}
for sh, n, _ in NAMES:
    pre_src[n] = copy_sync(n)
    say('   %s ← 同步盘' % sh)

say('== ② 丢失集重建＋m:t 指纹（donor vs 前源）==')
lost_info = {}
for sh, n, _ in NAMES:
    dtree, _ = FX.load(os.path.join(HERE, '副本_②B留档', n + '.bak_标签行'))
    ptree, _ = FX.load(pre_src[n])
    D, C = FX.instances(dtree), FX.instances(ptree)
    lost = FX.pair_lost(D, C)
    anch = FX.anchors(dtree)
    rows = []
    for (k, nom, el, _dp, dpi, dtxt) in lost:
        mt = ''.join(t.text or '' for t in el.iter(FX.qm('t')))
        rows.append({'k': k, 'anchor': anch[dpi], 'mt': norm_ws(mt)[:16], 'n': nom})
    lost_info[sh] = rows
    say('   %s 还原 %d 实例' % (sh, len(rows)))

say('== ③ COM 导出 前/后 各3件 ==')
pairs = []
for sh, n, _ in NAMES:
    pairs.append((pre_src[n], os.path.join(P_BEFORE, n[:-5] + '.pdf')))
    pairs.append((os.path.join(DST, n), os.path.join(P_AFTER, n[:-5] + '.pdf')))
todo = [(s, d) for (s, d) in pairs if not os.path.exists(d)]
if todo:
    ok = word_export(todo)
    bad = [os.path.basename(s) for s, v in ok.items() if not v]
    if bad:
        say('!! 导出失败：' + repr(bad))
        sys.exit(2)
else:
    say('   6 件 PDF 已在，跳过')

say('== ④ 自动渲染证（m:t 片段 后有前无）==')
ev_all = True
for sh, n, _ in NAMES:
    aft = os.path.join(P_AFTER, n[:-5] + '.pdf')
    bef = os.path.join(P_BEFORE, n[:-5] + '.pdf')
    import fitz
    da, db = fitz.open(aft), fitz.open(bef)
    say('  %s 页数 前=%d 后=%d' % (sh, db.page_count, da.page_count))
    da.close(); db.close()
    hit = miss = 0
    for r in lost_info[sh]:
        if len(r['mt']) < 2:
            continue
        pa = pages_with(aft, r['anchor'][:14], 2)
        pb = pages_with(bef, r['anchor'][:14], 2)
        in_a = any(r['mt'] in norm_ws(fitz.open(aft)[p - 1].get_text()) for p in pa)
        in_b = any(r['mt'] in norm_ws(fitz.open(bef)[p - 1].get_text()) for p in pb)
        okk = in_a and not in_b
        ev_all = ev_all and (in_a or False)
        if okk:
            hit += 1
        else:
            miss += 1
            say('    ! 锚 %s 片段 %r 后页%s 前页%s' % (r['anchor'][:16], r['mt'], pa, pb))
    say('  %s 渲染证：后页检出 %d／未检出 %d' % (sh, hit, miss))
say('渲染证合计（后有）：%s' % ('全检出' if ev_all else '存在未检出项（PDF 字形抽取所限，转人工 PNG 判读）'))

say('== ⑤ 渲染 PNG ==')
for sh, n, anchors in NAMES:
    aft = os.path.join(P_AFTER, n[:-5] + '.pdf')
    bef = os.path.join(P_BEFORE, n[:-5] + '.pdf')
    pgs = []
    if sh == '衔接2':
        pgs += [1, 2, 3]
    for a in anchors:
        pgs += pages_with(aft, a, 1)
    if sh == '下79':
        pgs += pages_with(aft, '汉堡模型', 1)
    pgs = sorted(set(pgs))
    for pno in pgs:
        render(aft, pno, os.path.join(P_PNG, '②F_PNG_%s_后_p%d.png' % (sh, pno)))
        render(bef, pno, os.path.join(P_PNG, '②F_PNG_%s_前_p%d.png' % (sh, pno)))

out = os.path.join(HERE, '报告', '②F_03_目检.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('# ②F 目检 — 前/后 PDF 渲染证与 PNG 清单\n\n```text\n' + '\n'.join(OUT) + '\n```\n')
print('REPORT:', out, flush=True)
