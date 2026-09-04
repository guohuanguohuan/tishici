# -*- coding: utf-8 -*-
r"""逐页巡检管线.py — 2026-09-03 选必1版式复合修复轮·子步0新建（公共规则§14主路径＋逐页视觉巡检条款）。

输入docx清单→逐件经PDFCreator主路径出全件PDF（§14：本地副本打开→spool快照→PrintOut(Background=False)
→轮询新.pdf→取走→用完删自己的.pdf/.inf/.PS）→PyMuPDF逐页转PNG（120dpi）→产分批清单（每批≤10页、
批间分片标签）。幂等：PDF已存在跳过导出（--reexport强制重导）；PNG已存在跳过该页。
超时（§14超时处置fail-closed）：单件单次导出>600s中止→换本地副本重试一次→仍超时记「该件未过视觉门」，
不停轮、其余件继续，超时件在总结与 导出记录.json 单列。
主路径兜底（链路定义「spool .PS→本机任一可用Ghostscript渲染，GS来源不限」）：轮询期满.pdf未现而.PS在案
→以用户级gswin64c（剥离GS_LIB环境）渲染该.PS为PDF，日志记「PS拦截渲染」。

用法:
  python 逐页巡检管线.py --out <工作区根> 代号=docx路径 [代号=docx路径 ...] [--reexport] [--dpi 120]
产物:
  <out>/pdf/<代号>.pdf            全件PDF（子步0管线产物，供断言⑤与巡检）
  <out>/pdf/导出记录.json        逐件耗时/模式/状态
  <out>/pages/<代号>/pNNN.png    逐页PNG（120dpi）
  <out>/pages/分批清单.md        批次标签｜件｜页范围｜页数
"""
import sys, io, os, re, time, glob, json, shutil, subprocess
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

SPOOL = os.path.expandvars(r'%LOCALAPPDATA%\Temp\PDFCreator\Spool')
GS_USER = r'C:\Users\28120\AppData\Local\Programs\Ghostscript\bin\gswin64c.exe'
TIMEOUT = 600          # 单件单次导出上限（§14 十分钟）
POLL = 2


def clean_env():
    env = dict(os.environ)
    env.pop('GS_LIB', None)   # GS_LIB串扰（10051≠10071根因）——渲染一律剥离
    return env


def render_ps(ps_path, out_pdf):
    """主路径链路定义的GS渲染环节：spool .PS → 用户级GS → pdf（GS来源不限）。"""
    cmd = [GS_USER, '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=pdfwrite',
           '-dPDFSETTINGS=/prepress', '-sOutputFile=' + os.path.abspath(out_pdf),
           os.path.abspath(ps_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, env=clean_env(), timeout=300)
    return os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 0, (r.stdout or '') + (r.stderr or '')


def wait_stable(path, rounds=3):
    s0 = -1
    for _ in range(rounds * 3):
        if not os.path.exists(path):
            return False
        s1 = os.path.getsize(path)
        if s1 == s0 and s1 > 0:
            return True
        s0 = s1
        time.sleep(1)
    return True


def export_one(src, out_pdf, pages_from=None, pages_to=None, log=print):
    """单件PDFCreator主路径导出。返回 (status, mode, seconds)；status∈{OK,TIMEOUT,ERROR}。"""
    src = os.path.abspath(src)
    out_pdf = os.path.abspath(out_pdf)
    t0 = time.time()
    for attempt in (1, 2):   # 超时/失败重试一次（§14）
        before = set(os.listdir(SPOOL)) if os.path.isdir(SPOOL) else set()
        pythoncom.CoInitialize()
        word = win32com.client.DispatchEx('Word.Application')
        word.Visible = False
        word.DisplayAlerts = 0
        newps = None
        try:
            d = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
            word.ActivePrinter = 'PDFCreator'
            if pages_from is None:
                d.PrintOut(Background=False)
            else:
                d.PrintOut(Background=False, Range=3, From=str(pages_from), To=str(pages_to))
            d.Close(False)
            deadline = time.time() + TIMEOUT
            newpdf = None
            while time.time() < deadline:
                time.sleep(POLL)
                cur = set(os.listdir(SPOOL)) if os.path.isdir(SPOOL) else set()
                new = sorted(f for f in cur - before if f.lower().endswith('.pdf'))
                if new:
                    cand = os.path.join(SPOOL, new[0])
                    if wait_stable(cand):
                        newpdf = cand
                        break
                ps = sorted(f for f in cur - before if f.lower().endswith('.ps'))
                if ps:
                    newps = os.path.join(SPOOL, ps[0])
            if newpdf is None and newps is not None:
                # 兜底：GS渲染spool .PS（链路定义环节）
                log('  [PS拦截渲染] 轮询期满无.pdf，.PS在案→用户级GS渲染')
                ok, gslog = render_ps(newps, out_pdf)
                if ok:
                    _cleanup_spool(before, keep_pdf=False)
                    return 'OK', 'PS拦截渲染(尝试%d)' % attempt, time.time() - t0
                log('  [PS拦截渲染失败] ' + gslog[-200:])
            if newpdf is not None:
                for mvtry in range(8):
                    try:
                        shutil.move(newpdf, out_pdf)
                        break
                    except PermissionError:
                        time.sleep(5)
                        if mvtry == 4:
                            subprocess.run(['taskkill', '/f', '/im', 'PDFCreator.exe'],
                                           capture_output=True)   # §4⑨：结束本任务拉起的隐藏引擎
                else:
                    log('  [ERROR] spool 文件持续占用')
                    return 'ERROR', '占用', time.time() - t0
                _cleanup_spool(before, keep_pdf=False)
                return 'OK', '自动出件(尝试%d)' % attempt, time.time() - t0
            log('  [超时] 第%d次导出 %ds 无产物' % (attempt, TIMEOUT))
        except Exception as e:
            log('  [异常] 第%d次: %r' % (attempt, e))
        finally:
            try:
                word.Quit()
            except Exception:
                pass
            pythoncom.CoUninitialize()
            _cleanup_spool(before, keep_pdf=False)
        time.sleep(30)   # 重试间隔
    return 'TIMEOUT', '两次超时', time.time() - t0


def export_direct(src, out_pdf, log=print):
    """Word直导（ExportAsFixedFormat，wdExportFormatPDF=17）——无打印队列、无PDFCreator/GS依赖。
    异常重试一次（换新实例）；同步COM调用不可轮询中断，挂死风险由外层帽与幂等续跑兜底。"""
    src = os.path.abspath(src)
    out_pdf = os.path.abspath(out_pdf)
    t0 = time.time()
    for attempt in (1, 2):
        pythoncom.CoInitialize()
        word = win32com.client.DispatchEx('Word.Application')
        word.Visible = False
        word.DisplayAlerts = 0
        try:
            d = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
            d.ExportAsFixedFormat(out_pdf, 17)
            d.Close(False)
            if os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 0:
                return 'OK', 'Word直导(尝试%d)' % attempt, time.time() - t0
            log('  [直导无产物] 第%d次' % attempt)
        except Exception as e:
            log('  [直导异常] 第%d次: %r' % (attempt, e))
        finally:
            try:
                word.Quit()
            except Exception:
                pass
            pythoncom.CoUninitialize()
        time.sleep(10)
    return 'TIMEOUT', '直导两次失败', time.time() - t0


def _cleanup_spool(before, keep_pdf=False):
    """§4⑨残留清查：删本任务新增 spool 件（.pdf/.inf/.PS与临时目录），不动他人文件。"""
    if not os.path.isdir(SPOOL):
        return
    for f in set(os.listdir(SPOOL)) - before:
        p = os.path.join(SPOOL, f)
        try:
            if os.path.isfile(p):
                os.remove(p)
            elif os.path.isdir(p) and (f.startswith('intermediate_') or f.startswith('temp_')):
                shutil.rmtree(p, ignore_errors=True)
        except OSError:
            pass


def to_png(pdf_path, pages_dir, dpi, log=print):
    """逐页转PNG，幂等跳过已存在页。返回 (总页数, 新增页数)。"""
    import pymupdf
    os.makedirs(pages_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    n = doc.page_count
    made = 0
    for i in range(n):
        out = os.path.join(pages_dir, 'p%03d.png' % (i + 1))
        if os.path.exists(out):
            continue
        pix = doc[i].get_pixmap(dpi=dpi)
        pix.save(out)
        made += 1
    doc.close()
    return n, made


def main():
    # 解析：--key value 与 --key=value 两形皆收；其余位置参数为 代号=docx路径
    args, opts, i = [], {}, 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a.startswith('--'):
            if '=' in a:
                k, v = a.split('=', 1)
                opts[k] = v
            elif i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--') and '=' not in sys.argv[i + 1] and a in ('--out', '--dpi'):
                opts[a] = sys.argv[i + 1]
                i += 1
            else:
                opts[a] = True
        else:
            args.append(a)
        i += 1
    out = os.path.abspath(str(opts.get('--out', '.')))
    reexport = '--reexport' in opts
    direct = '--direct' in opts   # Word直导主路径（无PDFCreator/GS依赖）；默认仍走打印链备胎
    dpi = int(opts.get('--dpi', 120))
    pdf_dir = os.path.join(out, 'pdf')
    pages_root = os.path.join(out, 'pages')
    copy_dir = os.path.join(out, 'tmp', 'copies')
    for d in (pdf_dir, pages_root, copy_dir):
        os.makedirs(d, exist_ok=True)
    records = {}
    for pair in args:
        if '=' not in pair:
            continue
        code, src = pair.split('=', 1)
        if not os.path.exists(src):
            print('[%s] 源缺失: %s' % (code, src))
            records[code] = {'status': 'ERROR', 'mode': '源缺失', 'seconds': 0, 'pages': 0}
            continue
        out_pdf = os.path.join(pdf_dir, code + '.pdf')
        if os.path.exists(out_pdf) and not reexport:
            print('[%s] PDF已存在，跳过导出（幂等）' % code)
            status, mode, secs = 'OK', '幂等跳过', 0.0
        else:
            local = os.path.join(copy_dir, code + '.docx')   # §14 本地副本
            shutil.copy2(src, local)
            print('[%s] 导出 %s ...' % (code, os.path.basename(src)))
            if direct:
                status, mode, secs = export_direct(local, out_pdf)
            else:
                status, mode, secs = export_one(local, out_pdf)
            print('[%s] %s %s %.1fs' % (code, status, mode, secs))
        pages = 0
        made = 0
        if status == 'OK' and os.path.exists(out_pdf):
            pages, made = to_png(out_pdf, os.path.join(pages_root, code), dpi)
            print('[%s] PNG 页数=%d 新增=%d' % (code, pages, made))
        if status != 'OK':
            print('[%s] 该件未过视觉门（fail-closed，其余件继续）' % code)
        records[code] = {'status': status, 'mode': mode, 'seconds': round(secs, 1),
                         'pages': pages, 'png_new': made}
    # 分批清单（每批≤10页）
    lines = ['# 分批清单（逐页巡检·每批≤10页）', '',
             '| 批次标签 | 件 | 页范围 | 页数 |', '|---|---|---|---|']
    for pair in args:
        if '=' not in pair:
            continue
        code = pair.split('=', 1)[0]
        n = records.get(code, {}).get('pages', 0)
        if not n:
            d0 = os.path.join(pages_root, code)
            n = len(glob.glob(os.path.join(d0, 'p*.png'))) if os.path.isdir(d0) else 0
        for k in range(0, max(n, 1), 10):
            a, b = k + 1, min(k + 10, n)
            lines.append('| %s-批%02d | %s | p%03d–p%03d | %d |' % (code, k // 10 + 1, code, a, b, b - a + 1))
    with open(os.path.join(pages_root, '分批清单.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(pdf_dir, '导出记录.json'), 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    bad = [c for c, r in records.items() if r['status'] != 'OK']
    print('=== 汇总: %d件 OK, %d件未过视觉门 %s ===' % (len(records) - len(bad), len(bad), bad))


if __name__ == '__main__':
    main()
