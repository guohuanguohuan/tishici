# -*- coding: utf-8 -*-
"""②C_08_导出PDF与PNG.py — ②-C 目检件产出（照 ②-B ②B_PNG 做法）。
①Word COM 十件 副本→PDF对比/②C后/*.pdf（页数实测源）；②衔接件两件 作废副本（pre-T6c 态）→②C前/*.pdf（前后对照）。
③fitz 清点 ②C后 十件页数 → 报告/②C_页数_后.txt，并与 报告/②B_页数_后.txt 逐件对照（应零变化）。
④fitz 抽验渲染 → PDF对比/②C_PNG/②C_PNG_*.png：
   衔接1/衔接2 前|后同页对照（解析块清灰区）＋讲练件四件 T6b 左竖条标题页。
每件 COM 300s 超时×3 试、超时杀最新 WINWORD 孤儿（重试甲范式）。"""
import sys, io, os, time, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
DJF = os.path.join(HERE, '副本_②C首轮作废_断言口径误')
P_AFTER = os.path.join(HERE, 'PDF对比', '②C后')
P_BEFORE = os.path.join(HERE, 'PDF对比', '②C前')
P_PNG = os.path.join(HERE, 'PDF对比', '②C_PNG')
RPT_PG = os.path.join(HERE, '报告', '②C_页数_后.txt')
for d in (P_AFTER, P_BEFORE, P_PNG):
    os.makedirs(d, exist_ok=True)

NAMES = [
    '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
]
SHORT = ['清单1', '衔接1(29)', '上61', '下79', '清单2', '衔接2(13)', '92', '90', '68', '89']


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


def export_one(word, src, dstpdf):
    for att in range(1, 4):
        t0 = time.time()
        try:
            doc = word.Documents.Open(os.path.abspath(src), ReadOnly=True)
            doc.ExportAsFixedFormat(os.path.abspath(dstpdf), 17)
            doc.Close(False)
            print('   OK %s %.0fs' % (os.path.basename(dstpdf)[:30], time.time() - t0), flush=True)
            return True
        except Exception as e:
            print('   att%d fail %s' % (att, str(e)[:120]), flush=True)
            kill_newest_winword()
            time.sleep(20)
            try:
                word = None
            except Exception:
                pass
            return False
    return False


def word_export(pairs):
    """pairs: [(src, dstpdf)]；COM 单实例逐件导出。"""
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
                    print('   OK %s %.0fs' % (os.path.basename(dst)[:34], time.time() - t0), flush=True)
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
            ok[src] = done
    finally:
        try:
            word.Quit()
        except Exception:
            pass
    return ok


W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)


def bar_texts(path, want=2):
    """取件内前 want 个左竖条（sz=18）标题段文本（T6b 产物，供 PDF 页定位）。"""
    z = zipfile.ZipFile(path)
    try:
        doc = etree.fromstring(z.read('word/document.xml'))
    finally:
        z.close()
    out = []
    for p in doc.iter(q('p')):
        ppr = p.find(q('pPr'))
        if ppr is None:
            continue
        pb = ppr.find(q('pBdr'))
        if pb is None:
            continue
        lf = pb.find(q('left'))
        if lf is not None and lf.get(q('sz')) == '18':
            t = ''.join(tt.text or '' for tt in p.iter(q('t'))).strip()
            if t:
                out.append(t)
            if len(out) >= want:
                break
    return out


def main():
    import fitz
    # ①② COM 导出（目标 PDF 已齐则跳过——重跑只补缺）
    pairs = [(os.path.join(DST, n), os.path.join(P_AFTER, n[:-5] + '.pdf')) for n in NAMES]
    pairs += [(os.path.join(DJF, n), os.path.join(P_BEFORE, n[:-5] + '.pdf'))
              for n in NAMES if '衔接件' in n]
    todo = [(s, d) for (s, d) in pairs if not os.path.exists(d)]
    if todo:
        print('== COM 导出 %d 件（缺%d）==' % (len(pairs), len(todo)), flush=True)
        ok = word_export(todo)
        bad = [os.path.basename(s) for s, v in ok.items() if not v]
        if bad:
            print('!! 导出失败：', bad, flush=True)
            sys.exit(2)
    else:
        print('== COM 导出跳过（12 件 PDF 已在）==', flush=True)
    # ③ 页数清点＋对照
    print('== 页数清点（fitz，②C后） ==', flush=True)
    lines = []
    allok = True
    for n, sh in zip(NAMES, SHORT):
        d = fitz.open(os.path.join(P_AFTER, n[:-5] + '.pdf'))
        lines.append('%s -> %d pages' % (n, d.page_count))
        d.close()
    with open(RPT_PG, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    b_after = {}
    with open(os.path.join(HERE, '报告', '②B_页数_后.txt'), encoding='utf-8') as f:
        for ln in f:
            m = re.match(r'(.+\.docx) -> (\d+) pages', ln.strip())
            if m:
                b_after[m.group(1)] = int(m.group(2))
    print('页数对照（②C后 vs ②B后）:', flush=True)
    for k, (n, sh) in enumerate(zip(NAMES, SHORT)):
        now = int(re.search(r'-> (\d+)', lines[k]).group(1))
        old = b_after.get(n)
        r = (now == old)
        allok = allok and r
        print('  %-10s %s→%s %s（②B %s）' % (sh, old, now, 'PASS' if r else '!!FAIL', old), flush=True)
    # ④ 抽验 PNG
    print('== 抽验 PNG ==', flush=True)

    def pages_with(pdf, needle, limit):
        d = fitz.open(pdf)
        out = []
        for i in range(d.page_count):
            if needle in d[i].get_text():
                out.append(i + 1)
                if len(out) >= limit:
                    break
        d.close()
        return out

    def render(pdf, pno, outpng):
        d = fitz.open(pdf)
        d[pno - 1].get_pixmap(dpi=150).save(outpng)
        d.close()
        print('   PNG', os.path.basename(outpng), flush=True)

    for n, sh, tag in [(NAMES[1], '衔接1', 'xj1'), (NAMES[5], '衔接2', 'xj2')]:
        aft = os.path.join(P_AFTER, n[:-5] + '.pdf')
        bef = os.path.join(P_BEFORE, n[:-5] + '.pdf')
        lim = 2 if tag == 'xj1' else 3
        pgs = pages_with(aft, '【分析】', lim)
        assert pgs, '%s 找不到解析块页' % sh
        for pno in pgs:
            render(aft, pno, os.path.join(P_PNG, '②C_PNG_%s_后_p%d.png' % (sh, pno)))
            render(bef, pno, os.path.join(P_PNG, '②C_PNG_%s_前_p%d.png' % (sh, pno)))
    for idx, sh in [(2, '上61'), (3, '下79'), (6, '92'), (9, '89')]:
        n = NAMES[idx]
        aft = os.path.join(P_AFTER, n[:-5] + '.pdf')
        bt = bar_texts(os.path.join(DST, n), 1)[0]
        key = bt[:12]
        pgs = pages_with(aft, key, 1)
        assert pgs, '%s 找不到竖条标题页：%s' % (sh, key)
        render(aft, pgs[0], os.path.join(P_PNG, '②C_PNG_%s_竖条_p%d.png' % (sh, pgs[0])))
    print('PAGEDIFF_ALLOK=%s' % allok, flush=True)
    print('DONE', flush=True)


if __name__ == '__main__':
    main()
