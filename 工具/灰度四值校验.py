# -*- coding: utf-8 -*-
"""灰度四值校验.py（原名 灰度三值校验.py，2026-09-01 A'改制轮工具债⑦升四值更名——
  全库grep无任何可执行引用后安全更名，沿革见 git 历史）— PDF侧四色板底纹灰度四值校验
  （公共规则§7「PDF灰度四值校验」＋§14，A'改制轮口径）。
  四值：#ADC2DA→灰≈190（章/节标题整行底纹）、#C6D4E3→≈209（讲部/题型）、
        #C7C7C7→199（内容标记族；2026-09-06 22%灰真值更正——原 #C9C9C9→201 降为存量过渡签名，
        单列过渡签名计数、新件应＝0、不计离群）、#F2F2F2→242（题干底纹，2026-09-05口径——A''过渡值#E0E0E0/224废止），
  各±容差（默认±8；199/209两带相距10仍互有重叠——分色以矢量层为主、像素带为辅，三重定性沿用
  2026-08-29 全库改色抽验先例：矢量层＋144dpi平台直方图；242带距白底255仅13、带外边界须与离群簇判读合并看；242与199相距43分带更宽）。
  矢量层匹配口径（2026-09-06 随 199/201 分色收紧）：通道精确匹配（±0）——PDF 矢量填充为十六进制
  精确值，199 与 201 相距 2、旧 ±2 通道容差无法分色；像素带照旧 ±容差。
  题干底纹沿革：A''轮曾按#E0E0E0/224，2026-09-05随题干底纹口径回调#F2F2F2/242（十件转值随②轮T6a，现跑存量PDF必报失配属预期）。
  取样两路（兼容矢量PDF与渲染平台）：
    ①矢量层（全部页，快）：page.get_drawings() 逐填充路径取 RGB→BT.601 灰；通道精确匹配四目标色
      （另匹配过渡签名 201，单独计数），四值各自命中矩形数/页码/面积；灰域[150,250]内非四目标
      （且非过渡签名）的填充色＝矢量离群（旧灰A6A6A6=166/
      D9D9D9=217、回调候选F7F7F7=247 等直接现形，比像素簇可靠）；
    ②144dpi渲染平台（抽样页，默认前5页、--pages all 全量/可指定）：灰度直方图四值带像素计数＋峰位；
      灰域[150,250]且不在任一带的连通像素簇（≥min_cluster 且 bbox 填充率≥0.25）＝离群像素簇清单
      （页码＋pt位置＋均值灰度）——供扫描件/位图底纹兜底。
用法: python 灰度四值校验.py <pdf> [--report out.txt] [--dpi 144] [--tol 8]
                            [--pages 1-5|all|3,7] [--min-cluster 400] [--jlp]
输出: 报告文本（stdout＋--report 落盘），供排版自检/§14校验引用；只读 PDF，不改任何文件。
2026-09-04 减法口径改造（选必1⓪复合修复轮子步2，工具债案6——附则《讲练件底纹减法》甲案改文）：
 --jlp＝讲练件族口径：199（#C7C7C7）来源断言改「条目号底纹＋第一子层底纹＋讲部条目需背灰底
 三源合计（＋导航表表头 §6 样式位 tcPr）」——矢量层 199 填充矩形逐个取覆盖文本归因分桶
 （条目号式／第一子层式／导航表表头／讲部需背·待核），非四源清单逐项列出供人工过目；
 190/209/242 三值照旧。190/209/242 测量引擎零改动（冒烟＝同件改造前后读数一致）。"""
import sys, os, re, argparse
import fitz
import numpy as np

TARGETS = [  # (名称, hex, R,G,B, 设计灰)
    ('标题整行#ADC2DA（章/节）', 'ADC2DA', 173, 194, 218, 190),
    ('标题整行#C6D4E3（讲部/题型）', 'C6D4E3', 198, 212, 227, 209),
    ('内容标记族#C7C7C7', 'C7C7C7', 199, 199, 199, 199),
    ('题干底纹#F2F2F2', 'F2F2F2', 242, 242, 242, 242),
]
# 过渡签名（2026-09-06 22%灰真值更正）：存量件 PDF 仍现 #C9C9C9/201，单列计数、新件应＝0、不计离群
TRANSITIONAL = [  # (名称, hex, R,G,B, 设计灰)
    ('内容标记族过渡签名#C9C9C9', 'C9C9C9', 201, 201, 201, 201),
]
GRAY_LO, GRAY_HI = 150.0, 250.0

def rgb_gray(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b

def match_target(rgb, tol_ch=0):
    """通道精确匹配（±0；199/201 相距 2、旧 ±2 无法分色——见 docstring 匹配口径）。
    先查过渡签名（201），再查四目标。命中返回 (名称, hex, 设计灰)，未命中 None。"""
    for name, hx, tr, tg, tb, g0 in TRANSITIONAL:
        if abs(rgb[0] - tr) <= tol_ch and abs(rgb[1] - tg) <= tol_ch and abs(rgb[2] - tb) <= tol_ch:
            return (name, hx, g0)
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
    ap.add_argument('--jlp', action='store_true',
                    help='讲练件族底纹减法口径：199 来源断言＝条目号＋第一子层＋讲部需背（＋导航表表头），'
                         '并对矢量层 199 矩形逐条归因')
    a = ap.parse_args()

    doc = fitz.open(a.pdf)
    pymupdf_ver = (fitz.__doc__ or '').split()[1].rstrip(':') if fitz.__doc__ else '?'
    L = []
    L.append('灰度四值校验（四色板 190/209/199/242；容差±%g；PyMuPDF %s）：%s'
             % (a.tol, pymupdf_ver, os.path.basename(a.pdf)))
    L.append('页数 %d｜渲染 dpi %d｜像素簇门槛 %d px' % (doc.page_count, a.dpi, a.min_cluster))
    if a.jlp:
        L.append('口径：讲练件族底纹减法（附则《讲练件底纹减法》甲案改文）——199灰度值＝条目号底纹＋'
                 '第一子层底纹＋讲部条目需背内容灰底三源合计（＋导航表表头§6样式位），四类废止项贡献＝0；'
                 '190/209/242 照旧')

    # —— ①矢量层（全部页）——
    vec = {hx: {'n': 0, 'area': 0.0, 'pages': []} for _, hx, _, _, _, _ in TARGETS + TRANSITIONAL}
    vec_out = {}   # hex -> [n, pages]
    c9_rects = []  # --jlp：199 矩形收集（页码, rect）供归因（标识符沿用 c9）
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
                if a.jlp and hx == 'C7C7C7':
                    c9_rects.append((pno, d['rect']))
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
    _t = vec['C9C9C9']
    _tpg = sorted(set(_t['pages']))
    L.append('  过渡签名 #C9C9C9＝设计灰 201（存量过渡；新件应＝0，不计离群）：填充矩形 %d 个%s'
             % (_t['n'], ('，页码 %s%s' % (_tpg[:8], '…' if len(_tpg) > 8 else '')) if _tpg else ''))
    if vec_out:
        L.append('  矢量离群填充色（灰域[%g,%g]非四目标且非过渡签名，±0通道）——旧灰/杂色直接现形：'
                 % (GRAY_LO, GRAY_HI))
        for k, (n, pgs) in sorted(vec_out.items(), key=lambda kv: -kv[1][0])[:10]:
            g = rgb_gray(int(k[0:2], 16), int(k[2:4], 16), int(k[4:6], 16))
            L.append('    #%s（灰%.0f）×%d，页 %s' % (k, g, n, sorted(set(pgs))[:8]))
    else:
        L.append('  矢量离群填充色：0（灰域无非四目标色填充）')

    # —— --jlp：199 矢量矩形归因（减法口径三源＋导航表表头 §6 样式位） ——
    if a.jlp:
        RE_ENT = re.compile(r'^\d+(?:\.\d+)+-\d+．')
        RE_SUB = re.compile(r'^（\d+）')
        HDR_WORDS = ('节名', '题量', '题型组数', '简单/中档/难', '节内题号')
        attr = {'条目号式': 0, '第一子层式': 0, '导航表表头': 0}
        todo = []
        for pno, rc in c9_rects:
            page = doc[pno]
            clip = fitz.Rect(rc.x0 - 1, rc.y0 - 1, rc.x1 + 1, rc.y1 + 1)
            txt = re.sub(r'[\s　]+', '', page.get_text('text', clip=clip))
            # PDF 文字层连字号归一（2010/2011/00AD 软连字符 → ASCII）再匹配条目号式
            txt = txt.replace('\u2010', '-').replace('\u2011', '-').replace('\xad', '-')
            if RE_ENT.match(txt):
                attr['条目号式'] += 1
            elif RE_SUB.match(txt):
                attr['第一子层式'] += 1
            elif any(w in txt for w in HDR_WORDS):
                attr['导航表表头'] += 1
            else:
                todo.append((pno + 1, rc, txt[:24]))
        L.append('—— 199 来源归因（--jlp 减法口径：条目号＋第一子层＋讲部条目需背＋导航表表头四源白名单）——')
        L.append('  矢量199矩形 %d 个＝条目号式 %d＋第一子层式 %d＋导航表表头 %d＋待核 %d（讲部需背文字/公式区，'
                 '逐条人工过目）' % (len(c9_rects), attr['条目号式'], attr['第一子层式'],
                                     attr['导航表表头'], len(todo)))
        for pno, rc, txt in todo[:24]:
            L.append('    待核 第%d页 (%.0f,%.0f)-(%.0f,%.0f) %r' % (pno, rc.x0, rc.y0, rc.x1, rc.y1, txt))

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
    L.append('结论: 矢量四值命中 %s｜过渡签名201 %d｜矢量离群 %d 色｜像素簇 %d 个（三重定性：矢量层为主，'
             '像素带/簇为辅；带互有重叠——199/209相距10；242距白底255仅13）'
             % ('/'.join(str(vec[hx]['n']) for _, hx, *_ in TARGETS), vec['C9C9C9']['n'],
                len(vec_out), len(out_clusters)))
    out = '\n'.join(L)
    print(out)
    if a.report:
        d = os.path.dirname(os.path.abspath(a.report))
        if d and not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        open(a.report, 'w', encoding='utf-8').write(out + '\n')

if __name__ == '__main__':
    main()
