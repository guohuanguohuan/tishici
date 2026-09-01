# -*- coding: utf-8 -*-
"""灰度四值校验.py（原名 灰度三值校验.py，2026-09-01 A'改制轮工具债⑦升四值更名——
  全库grep无任何可执行引用后安全更名，沿革见 git 历史）— PDF侧四色板底纹灰度四值校验
  （公共规则§7「PDF灰度四值校验」＋§14，A'改制轮口径）。
  四值：#ADC2DA→灰≈190（章/节标题整行底纹）、#C6D4E3→≈209（讲部/题型）、
        #C9C9C9→201（内容标记族）、#F2F2F2→242（解析块段落浅底），
  各±容差（默认±8；201/209两带相距8互有重叠——分色以矢量层为主、像素带为辅，三重定性沿用
  2026-08-29 全库改色抽验先例：矢量层＋144dpi平台直方图；242带与白底255距离13、带外不误吞）。
  取样两路（兼容矢量PDF与渲染平台）：
    ①矢量层（全部页，快）：page.get_drawings() 逐填充路径取 RGB→BT.601 灰；通道级±2 匹配四目标色，
      四值各自命中矩形数/页码/面积；灰域[150,250]内非四目标色的填充色＝矢量离群（旧灰A6A6A6=166/
      D9D9D9=217、回调候选F7F7F7=247 等直接现形，比像素簇可靠）；
    ②144dpi渲染平台（抽样页，默认前5页、--pages all 全量/可指定）：灰度直方图四值带像素计数＋峰位；
      灰域[150,250]且不在任一带的连通像素簇（≥min_cluster 且 bbox 填充率≥0.25）＝离群像素簇清单
      （页码＋pt位置＋均值灰度）——供扫描件/位图底纹兜底。
用法: python 灰度四值校验.py <pdf> [--report out.txt] [--dpi 144] [--tol 8]
                            [--pages 1-5|all|3,7] [--min-cluster 400]
输出: 报告文本（stdout＋--report 落盘），供排版自检/§14校验引用；只读 PDF，不改任何文件。"""
import sys, os, re, argparse
import fitz
import numpy as np

TARGETS = [  # (名称, hex, R,G,B, 设计灰)
    ('标题整行#ADC2DA（章/节）', 'ADC2DA', 173, 194, 218, 190),
    ('标题整行#C6D4E3（讲部/题型）', 'C6D4E3', 198, 212, 227, 209),
    ('内容标记族#C9C9C9', 'C9C9C9', 201, 201, 201, 201),
    ('解析块浅底#F2F2F2', 'F2F2F2', 242, 242, 242, 242),
]
GRAY_LO, GRAY_HI = 150.0, 250.0

def rgb_gray(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b

def match_target(rgb, tol_ch=2):
    for name, hx, tr, tg, tb, g0 in TARGETS:
        if abs(rgb[0] - tr) <= tol_ch and abs(rgb[1] - tg) <= tol_ch and abs(rgb[2] - tb) <= tol_ch:
            return (name, hx, g0)
    return None

def parse_pages(spec, n):
    if spec == 'all':
        return list(range(n))
    m = re.fullmatch(r'(\d+)-(\d+)', spec)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return [p for p in range(a - 1, min(b, n))]
    return [int(x) - 1 for x in spec.split(',') if x.strip()]

def clusters(mask, gray, scale, min_cluster, min_fill=0.25):
    """mask(bool, h×w) 连通域（4邻接 BFS）；返回 [(y0,x0,y1,x1,px,mean_gray_pt)]。"""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    idx = np.argwhere(mask)
    for y0, x0 in idx:
        if seen[y0, x0]:
            continue
        stack = [(y0, x0)]
        seen[y0, x0] = True
        pix = []
        y_min = y_max = y0; x_min = x_max = x0
        while stack:
            y, x = stack.pop()
            pix.append((y, x))
            if y < y_min: y_min = y
            if y > y_max: y_max = y
            if x < x_min: x_min = x
            if x > x_max: x_max = x
            for ny, nx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(pix) < min_cluster:
            continue
        bh, bw = y_max - y_min + 1, x_max - x_min + 1
        if len(pix) / (bh * bw) < min_fill:
            continue                      # 细碎边缘/纹理，非整片底纹
        gvals = [gray[y, x] for y, x in pix[:: max(1, len(pix) // 4000)]]
        out.append((y_min, x_min, y_max, x_max, len(pix), float(np.mean(gvals))))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--report')
    ap.add_argument('--dpi', type=int, default=144)
    ap.add_argument('--tol', type=float, default=8)
    ap.add_argument('--pages', default='1-5')
    ap.add_argument('--min-cluster', type=int, default=400)
    a = ap.parse_args()

    doc = fitz.open(a.pdf)
    pymupdf_ver = (fitz.__doc__ or '').split()[1].rstrip(':') if fitz.__doc__ else '?'
    L = []
    L.append('灰度四值校验（四色板 190/209/201/242；容差±%g；PyMuPDF %s）：%s'
             % (a.tol, pymupdf_ver, os.path.basename(a.pdf)))
    L.append('页数 %d｜渲染 dpi %d｜像素簇门槛 %d px' % (doc.page_count, a.dpi, a.min_cluster))

    # —— ①矢量层（全部页）——
    vec = {hx: {'n': 0, 'area': 0.0, 'pages': []} for _, hx, _, _, _, _ in TARGETS}
    vec_out = {}   # hex -> [n, pages]
    for pno in range(doc.page_count):
        page = doc[pno]
        for d in page.get_drawings():
            f = d.get('fill')
            if not f:
                continue
            rgb = (round(f[0] * 255), round(f[1] * 255), round(f[2] * 255))
            mt = match_target(rgb)
            if mt:
                hx = mt[1]
                vec[hx]['n'] += 1
                vec[hx]['area'] += abs(d['rect'])
                vec[hx]['pages'].append(pno + 1)
            else:
                g = rgb_gray(*rgb)
                if GRAY_LO <= g <= GRAY_HI:
                    k = '%02X%02X%02X' % rgb
                    vo = vec_out.setdefault(k, [0, []])
                    vo[0] += 1
                    vo[1].append(pno + 1)
    L.append('—— 矢量层（全 %d 页）四值命中 ——' % doc.page_count)
    for name, hx, tr, tg, tb, g0 in TARGETS:
        v = vec[hx]
        pg = sorted(set(v['pages']))
        L.append('  %s＝设计灰 %d：填充矩形 %d 个，面积 %.0f pt²，页码 %s'
                 % (hx, g0, v['n'], v['area'],
                    ('%s%s' % (pg[:8], '…' if len(pg) > 8 else '')) if pg else '（未检出）'))
    if vec_out:
        L.append('  矢量离群填充色（灰域[%g,%g]非四目标，±2通道）——旧灰/杂色直接现形：'
                 % (GRAY_LO, GRAY_HI))
        for k, (n, pgs) in sorted(vec_out.items(), key=lambda kv: -kv[1][0])[:10]:
            g = rgb_gray(int(k[0:2], 16), int(k[2:4], 16), int(k[4:6], 16))
            L.append('    #%s（灰%.0f）×%d，页 %s' % (k, g, n, sorted(set(pgs))[:8]))
    else:
        L.append('  矢量离群填充色：0（灰域无非四目标色填充）')

    # —— ②144dpi 渲染平台（抽样页）——
    rpages = parse_pages(a.pages, doc.page_count)
    L.append('—— 渲染平台（dpi %d，抽样 %d 页：%s）——' % (a.dpi, len(rpages), a.pages))
    band_px = {hx: 0 for _, hx, _, _, _, _ in TARGETS}
    out_clusters = []
    peaks_all = {}
    for pno in rpages:
        pix = doc[pno].get_pixmap(dpi=a.dpi)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        gray = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2])
        inband = np.zeros_like(gray, dtype=bool)
        row = []
        for name, hx, tr, tg, tb, g0 in TARGETS:
            m = np.abs(gray - g0) <= a.tol
            band_px[hx] += int(m.sum())
            inband |= m
        # 直方图峰（灰域内、计数≥0.05%页像素）
        hist, edges = np.histogram(gray[(gray >= 140) & (gray <= 250)], bins=110, range=(140, 250))
        thr = max(200, int(0.0005 * gray.size))
        for i in np.argsort(hist)[::-1][:6]:
            if hist[i] < thr:
                break
            c = int((edges[i] + edges[i + 1]) / 2)
            peaks_all.setdefault(c, 0)
            peaks_all[c] += int(hist[i])
        # 离群像素簇
        mask = (gray >= GRAY_LO) & (gray <= GRAY_HI) & (~inband)
        scale = 72.0 / a.dpi
        for (y0, x0, y1, x1, npx, mg) in clusters(mask, gray, scale, a.min_cluster):
            out_clusters.append((pno + 1, x0 * scale, y0 * scale, x1 * scale, y1 * scale, npx, mg))
    for name, hx, tr, tg, tb, g0 in TARGETS:
        L.append('  %s＝灰%d±%g：像素 %d' % (hx, g0, a.tol, band_px[hx]))
    if peaks_all:
        pk = sorted(peaks_all.items(), key=lambda kv: -kv[1])[:8]
        L.append('  平台直方图峰（灰值:像素）：' + '；'.join('%d:%d' % kv for kv in pk))
    if out_clusters:
        out_clusters.sort(key=lambda c: -c[5])
        L.append('  离群像素簇 %d 个（灰域[%g,%g]且不在任一四值带；页码＋pt位置＋px＋均值灰）：'
                 % (len(out_clusters), GRAY_LO, GRAY_HI))
        for c in out_clusters[:12]:
            L.append('    第%d页 (%.0f,%.0f)-(%.0f,%.0f) %d px 均灰%.0f' % c)
    else:
        L.append('  离群像素簇：0（抽样页无带外整片底纹簇）')
    L.append('结论: 矢量四值命中 %s｜矢量离群 %d 色｜像素簇 %d 个（三重定性：矢量层为主，'
             '像素带/簇为辅；带互有重叠——201/209相距8；242距白底255为13）'
             % ('/'.join(str(vec[hx]['n']) for _, hx, *_ in TARGETS), len(vec_out), len(out_clusters)))
    out = '\n'.join(L)
    print(out)
    if a.report:
        d = os.path.dirname(os.path.abspath(a.report))
        if d and not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        open(a.report, 'w', encoding='utf-8').write(out + '\n')

if __name__ == '__main__':
    main()
