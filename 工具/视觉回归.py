# -*- coding: utf-8 -*-
"""视觉回归.py — 版式视觉回归基线工具（PyMuPDF 渲页 PNG 逐像素比对）

用途：对 PDF 建「渲染基线」，后续版本逐页逐像素回归比对（改版式/换字/调参后防意外改动）。
渲染：PyMuPDF 全部页 → PNG，固定 dpi（默认 150）；同一 PDF 同 dpi 渲染确定性可复现。

用法:
  python 工具/视觉回归.py 建基线 <pdf> <基线目录> [--dpi N] [--force]
  python 工具/视觉回归.py 比对   <pdf> <基线目录> [--tol N]

建基线：渲染全部页存 <基线目录>/pageNN.png ＋ <基线目录>/manifest.json（dpi/页数/源 pdf md5）；
     --force 重建并清理旧基线遗留的陈旧 pageNN.png（比对 diff/ 不动）。
比对：逐页与基线逐像素 diff，输出每页「差异像素占比 / 最大通道差 / 差异 bbox」；
     差异页裁热区图（左＝基线 右＝当前，差异像素红色高亮）存 <基线目录>/diff/pageNN_diff.png。
     容差 --tol N（默认 0＝逐像素严格）：单像素任一通道差 > N 才算差异像素。
退出码：0＝全页无差异；1＝有差异（打印摘要表）；2＝用法/基线缺失等错误。
页数不一致：报「页数变化 N→M」，按较少页数逐页比对，余页标注（新增/缺失），判定有差异。
"""
import sys
import os
import io
import json
import time
import hashlib
import re

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import pymupdf
except ImportError:  # 旧版 PyMuPDF 兼容
    import fitz as pymupdf
from PIL import Image, ImageChops, ImageDraw

DEFAULT_DPI = 150
USAGE = """用法:
  python 工具/视觉回归.py 建基线 <pdf> <基线目录> [--dpi N] [--force]
  python 工具/视觉回归.py 比对   <pdf> <基线目录> [--tol N]"""


# ---------- 基础 ----------

def md5_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def page_name(i, total):
    """1-based 页码 → pageNN.png（0 填充宽度 = max(2, 总页数位数)）"""
    return 'page%0*d.png' % (max(2, len(str(total))), i)


def wlen(s):
    from unicodedata import east_asian_width
    return sum(2 if east_asian_width(c) in 'WF' else 1 for c in s)


def wpad(s, width):
    return s + ' ' * max(0, width - wlen(s))


def render_pages(pdf_path, dpi):
    """全页渲 RGB PIL Image 列表（alpha=False），返回 (imgs, 页数)"""
    doc = pymupdf.open(pdf_path)
    try:
        imgs = []
        for pg in doc:
            pix = pg.get_pixmap(dpi=dpi, alpha=False)
            imgs.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
        return imgs, doc.page_count
    finally:
        doc.close()


def fail(msg):
    print('错误：' + msg)
    sys.exit(2)


def expand_box(box, w, h, margin=10, minsize=56):
    """差异 bbox 外扩 margin、至少 minsize 见方，再夹回页内"""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    if x1 - x0 < minsize:
        x0, x1 = cx - minsize / 2.0, cx + minsize / 2.0
    if y1 - y0 < minsize:
        y0, y1 = cy - minsize / 2.0, cy + minsize / 2.0
    x0, y0 = max(0, int(x0 - margin)), max(0, int(y0 - margin))
    x1, y1 = min(w, int(x1 + margin) + 1), min(h, int(y1 + margin) + 1)
    return (x0, y0, x1, y1)


# ---------- 建基线 ----------

def cmd_build(args):
    if not args:
        print('用法错误：缺 <pdf> <基线目录>')
        print(USAGE)
        sys.exit(2)
    pdf, base = args[0], (args[1] if len(args) > 1 else None)
    if base is None:
        print('用法错误：缺 <基线目录>')
        print(USAGE)
        sys.exit(2)
    dpi, force = DEFAULT_DPI, False
    rest = args[2:]
    i = 0
    while i < len(rest):
        if rest[i] == '--dpi' and i + 1 < len(rest):
            try:
                dpi = int(rest[i + 1])
            except ValueError:
                fail('--dpi 需为整数：%r' % rest[i + 1])
            i += 2
        elif rest[i] == '--force':
            force = True
            i += 1
        else:
            print('用法错误：未知参数 %r' % rest[i])
            print(USAGE)
            sys.exit(2)
    if dpi <= 0:
        fail('--dpi 需为正整数')

    if not os.path.isfile(pdf):
        fail('PDF 不存在：%s' % pdf)
    manifest_path = os.path.join(base, 'manifest.json')
    if os.path.isfile(manifest_path) and not force:
        fail('基线已存在：%s（如需重建加 --force）' % manifest_path)

    try:
        imgs, n = render_pages(pdf, dpi)
    except Exception as e:
        fail('无法打开/渲染 PDF：%s（%s）' % (pdf, e))
    if n == 0:
        fail('PDF 无页面：%s' % pdf)

    os.makedirs(base, exist_ok=True)
    for i, im in enumerate(imgs, 1):
        im.save(os.path.join(base, page_name(i, n)))
    if force:  # 重建时清理旧基线的陈旧 pageNN.png（页数/命名宽度变化留下的余件）
        new_names = {page_name(i, n) for i in range(1, n + 1)}
        for f in os.listdir(base):
            if f not in new_names and re.fullmatch(r'page\d+\.png', f):
                os.remove(os.path.join(base, f))
    manifest = {
        'tool': '工具/视觉回归.py',
        'dpi': dpi,
        'pages': n,
        'pdf': os.path.basename(pdf),
        'pdf_md5': md5_file(pdf),
        'created': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    print('渲染：%s（%d 页 @%ddpi）' % (pdf, n, dpi))
    print('  已写入 %s … %s（%d 文件）' % (page_name(1, n), page_name(n, n), n))
    print('  manifest.json：dpi=%d 页数=%d 源pdf md5=%s' % (dpi, n, manifest['pdf_md5']))
    print('基线目录：%s' % os.path.abspath(base))
    print('完成：0')
    sys.exit(0)


# ---------- 比对 ----------

def cmd_compare(args):
    if not args:
        print('用法错误：缺 <pdf> <基线目录>')
        print(USAGE)
        sys.exit(2)
    pdf, base = args[0], (args[1] if len(args) > 1 else None)
    if base is None:
        print('用法错误：缺 <基线目录>')
        print(USAGE)
        sys.exit(2)
    tol, dpi_opt = 0, None
    rest = args[2:]
    i = 0
    while i < len(rest):
        if rest[i] == '--tol' and i + 1 < len(rest):
            try:
                tol = int(rest[i + 1])
            except ValueError:
                fail('--tol 需为整数：%r' % rest[i + 1])
            i += 2
        elif rest[i] == '--dpi' and i + 1 < len(rest):
            try:
                dpi_opt = int(rest[i + 1])
            except ValueError:
                fail('--dpi 需为整数：%r' % rest[i + 1])
            i += 2
        else:
            print('用法错误：未知参数 %r' % rest[i])
            print(USAGE)
            sys.exit(2)
    if tol < 0:
        fail('--tol 需为非负整数')

    if not os.path.isfile(pdf):
        fail('PDF 不存在：%s' % pdf)
    manifest_path = os.path.join(base, 'manifest.json')
    if not os.path.isfile(manifest_path):
        fail('基线缺失：%s 不存在（先用「建基线」生成）' % manifest_path)
    try:
        with open(manifest_path, encoding='utf-8') as f:
            manifest = json.load(f)
        m_dpi, m_pages, m_md5 = int(manifest['dpi']), int(manifest['pages']), manifest['pdf_md5']
    except Exception as e:
        fail('manifest.json 读取失败：%s（%s）' % (manifest_path, e))
    if dpi_opt is not None and dpi_opt != m_dpi:
        print('提示：比对按基线 dpi=%d 渲染（--dpi %d 忽略）' % (m_dpi, dpi_opt))

    try:
        imgs, n = render_pages(pdf, m_dpi)
    except Exception as e:
        fail('无法打开/渲染 PDF：%s（%s）' % (pdf, e))

    cur_md5 = md5_file(pdf)
    print('基线：%s（dpi=%d 页数=%d 源md5=%s）' % (os.path.abspath(base), m_dpi, m_pages, m_md5))
    print('当前：%s（%d 页 @%ddpi 源md5=%s%s）' % (
        pdf, n, m_dpi, cur_md5, '＝基线' if cur_md5 == m_md5 else '≠基线'))
    print('容差：tol=%d（单像素任一通道差 >%d 计差异像素）' % (tol, tol))

    count_changed = (n != m_pages)
    if count_changed:
        print('页数变化 %d→%d（基线→当前）' % (m_pages, n))
    else:
        print('页数一致（%d）' % n)

    minn = min(n, m_pages)
    diff_pages, rows = 0, []
    diff_dir = None
    for i in range(1, minn + 1):
        bp = os.path.join(base, page_name(i, m_pages))
        if not os.path.isfile(bp):
            fail('基线缺失：%s 不存在' % bp)
        base_im = Image.open(bp).convert('RGB')
        cur_im = imgs[i - 1]
        note, dim_flag = '', False
        if base_im.size != cur_im.size:
            dim_flag = True
            ow = min(base_im.width, cur_im.width)
            oh = min(base_im.height, cur_im.height)
            note = '尺寸变化 %dx%d→%dx%d' % (base_im.width, base_im.height,
                                            cur_im.width, cur_im.height)
            base_im, cur_im = base_im.crop((0, 0, ow, oh)), cur_im.crop((0, 0, ow, oh))
        diff = ImageChops.difference(base_im, cur_im)
        extrema = diff.getextrema()
        maxdiff = max(e[1] for e in extrema) if isinstance(extrema[0], tuple) else extrema[1]
        r, g, b = diff.split()
        m = ImageChops.lighter(ImageChops.lighter(r, g), b)
        hist = m.histogram()
        cnt = sum(hist[tol + 1:])
        total = base_im.width * base_im.height
        ratio = cnt / total if total else 0.0
        if cnt > 0:
            mb = m.point(lambda v: 255 if v > tol else 0)
            bbox = mb.getbbox()
        else:
            mb, bbox = m, None
        if cnt > 0 or dim_flag:
            diff_pages += 1
            if diff_dir is None:
                diff_dir = os.path.join(base, 'diff')
                os.makedirs(diff_dir, exist_ok=True)
            out = os.path.join(diff_dir, page_name(i, m_pages).replace('.png', '_diff.png'))
            if bbox is None:
                region = (0, 0, base_im.width, base_im.height)
            else:
                region = expand_box(bbox, base_im.width, base_im.height)
            bc = base_im.crop(region)
            cc = cur_im.crop(region)
            mc = mb.crop(region)
            red = Image.new('RGB', cc.size, (255, 60, 60))
            cc = cc.copy()
            cc.paste(red, (0, 0), mc)
            gap, band = 8, 15
            canvas = Image.new('RGB', (bc.width + gap + cc.width, band + bc.height), (255, 255, 255))
            canvas.paste(bc, (0, band))
            canvas.paste(cc, (bc.width + gap, band))
            dr = ImageDraw.Draw(canvas)
            dr.text((2, 2), 'BASE', fill=(0, 0, 160))
            dr.text((bc.width + gap + 2, 2), 'CUR (diff red)', fill=(200, 0, 0))
            canvas.save(out)
            note = (note + ' ' if note else '') + '热区图 diff/%s' % os.path.basename(out)
            bbox_s = '(%d,%d,%d,%d)' % bbox
        else:
            bbox_s = '—'
        rows.append((page_name(i, m_pages), '%.4f%%' % (ratio * 100.0), str(maxdiff), bbox_s, note))

    width = 12
    print('')
    print(wpad('页码', width) + wpad('差异像素占比', 14) + wpad('最大通道差', 12) + wpad('差异bbox', 21) + '备注')
    for r in rows:
        print(wpad(r[0], width) + wpad(r[1], 14) + wpad(r[2], 12) + wpad(r[3], 21) + r[4])
    if count_changed:
        if n > m_pages:
            extra = '、'.join(page_name(i, n) for i in range(m_pages + 1, n + 1))
            print(wpad('新增页', width) + wpad('100%', 14) + wpad('—', 12) + wpad('—', 21)
                  + '当前多出 %s（无基线可对）' % extra)
        else:
            extra = '、'.join(page_name(i, m_pages) for i in range(n + 1, m_pages + 1))
            print(wpad('缺失页', width) + wpad('—', 14) + wpad('—', 12) + wpad('—', 21)
                  + '基线有 %s（当前无）' % extra)

    if diff_pages == 0 and not count_changed:
        print('汇总：%d/%d 页无差异；判定：无差异' % (minn, minn))
        sys.exit(0)
    print('汇总：共比对 %d 页，有差异 %d 页%s；判定：有差异' % (
        minn, diff_pages, '；页数变化 %d→%d' % (m_pages, n) if count_changed else ''))
    sys.exit(1)


def main(argv):
    if len(argv) < 3 or argv[0] not in ('建基线', '比对'):
        print(USAGE)
        sys.exit(2)
    if argv[0] == '建基线':
        cmd_build(argv[1:])
    else:
        cmd_compare(argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
