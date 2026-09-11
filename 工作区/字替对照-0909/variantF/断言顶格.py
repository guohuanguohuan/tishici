# -*- coding: utf-8 -*-
r"""顶格断言（v4.1 指令5 口径，替代断言题号列.py；v4.2 随结构变化复查适配）：
v4.1 撤全部悬挂缩进（\parindent=0pt、hangindent 全撤、题号列恒空制废除），正文一切行、表、图从栏左起。
v4.2 结构变化三点复查：①【旧史（图源回退后不适用）】题干图 minipage 并排行（左 0.56\linewidth
题干／右 0.40\linewidth 图）已退场——「题干行非签名行不进 (c)」判据本身不受影响；②选项网格 4 槽行
（0.25\linewidth）与 2 槽行同机制，
B．/C．/D．以「同视觉行左侧存在更靠前文本」排除；③【解析】简析行（\jiexi）与②③小结拆行均为顶格
签名行，进 (c) 正常判。检查面：
  (a) body.tex 结构 grep：无 \hangindent / \hspace*{7mm} / \hspace*{2em}（顶格化残留扫描；\kern0.15em
      为 \kongda 印答盒间距 kern，非行首缩进语义，不在禁区）；
  (b) qp-blocks.tex 无 \hspace*{2em}（选项/①链 2em 前缀已撤；\hspace{-2mm} 花形连排、\hspace{0.5em}
      \zhuzhu 前距为非 * 版本且非行首缩进语义，不在禁区；v4.2-C13 \zhenhead 标签后距已撤）；
  (c) pdf 签名行顶格：以〔N．／【答案】／【解析】／【诊断分析】／【素养小结】／【学习目标】／
      A．~D．／①~⑨／◆／（N）〕起行的行首墨迹 ∈ 栏左±3.5pt。坑规（沿 v2/旧脚本登记）：行首
      全角标点【（ 经 xeCJK 半宽压缩，line bbox x0=origin 比墨迹左偏 ~5.2pt——凡 bbox x0<栏左
      的签名行一律 300dpi 墨迹左缘复核。行中元素（选项网格槽位项 B．/C．/D．被 pymupdf 按
      定位跳转拆成独立 line）以「同视觉行左侧存在更靠前文本」排除。
  (d) 竖直表线（宽≤2pt 高≥4pt）全部落在某栏带内（x0≥栏左−1 且 x1≤栏右+1），且每张表的
      左框线在场（页上存在 x0==栏左±1 的表线）＝表盒子顶格；表内部竖线（列分隔/右框）位置
      随内容驱动列宽（表1 16/33/30、表2 10/37/32、表3 起调 10/36/33，v4.2-C14）任意，不判 x0==栏左。
      豁免 multicol 栏线（x0≈栏中缝，v4.2-A3 恢复）、花形行 tcbox 左竖边（高 8~30pt 且距栏左 ≤3pt）。
  (e) 位图×6：PDF 内 raster 图对象恰 6（\includegraphics 引原图位图），全部在栏带内
      （x0≥栏左−1 且 x1≤栏右+1）、且图矩形与正文行 bbox 零压字（相交行数＝0）。
  片E 0909c（#40 绕图回流）：「图旁前缀仍为 minipage 并排」系旧史（图源回退后不适用——题干图并排
  已退场；并排恢复0910 g1/g2 文左图右另是一形，见 (e)）；图底以下余段改通栏
  独立段（探八题干第 4 行起、探九详解第 5 行起）——余段行以栏左起、达栏右，签名行口径不受影响。
登记豁免：p1 学习目标块（multicols 外通栏区）\mubiaomu 楷体条目悬挂保留——v4.3 拍板6 顶格例外，
hangindent=8.3mm（qp-titles:46 定义，不在 body——(a) grep 不误报；N5 断言窗 23.3±0.6mm 另行实测）
（章首块不属正文顶格口径，登记）——条目行不以签名起，不进 (c)；花形右侧灰小字不以签名起；
页眉已撤（v4.2-A1）；页脚块 fill 宽 >2pt 不进 (d)；页码数字不匹配签名。
v4.3 签名覆盖注：知识点条目号改半角「N.」（总账E），不以全角「．」入 SIG——顶格性由 \tiaomu
行首 \noindent 机制保证；全角「N．」仅存检测题号（postproc \heihao），照常入 (c)。
v4.4 签名适配（执行轮）：【答案】/【解析】→半角 [答案]/[解析] 入 SIG（拍板2 半角[]标签制）；
子项号（N）转半角 (N) 后以 \(N 入 SIG（判断题全品式序号）；【答案】行 14 维持（n_ans 计 [答案]）。
（「图构成＝5 并排 side 0.56＋1 居中 60mm」系旧史——图源回退后不适用，现形制见下「回退轮 0910」段
位图六张。）
预期（答案制0911 更正口径）：图 4（位图——g1-prism/g5-fold 随 [详解] 出册另排 导学件答案册-v1）、
[答案] 行 0（答案落册——(c) 改反向锁 n_ans==0，正文渗回即红；册侧值在场见 _测v4断言.py ㉑b/㉑c）。
（旧档·残留清理 0911 口径：图 6、[答案] 行 14。）表线总数随分页漂移，不硬编码。
回退轮 0910 (e) 换回位图口径：六图（五例1 图＋条目3 投影三联）由片G 的 TikZ 矢量重绘回退为原图
位图（body.tex 六行 \includegraphics[width=…mm]{media/media/*.png}，图下置居中·反解宽档），
PDF 内 image 对象 0→6——(e) 改以 page.get_image_info(xrefs=True) 逐页归集位图矩形并按原生像素
尺寸认领 g1~g6：门＝位图 n_fig==6 且全部落在栏带内（n_viol_e==0）且与正文行零压字
（n_press==0）；ok 式相应改 n_fig==6。矢量墨聚簇内核 _vec_clusters 自此不再参与 (e)；残留清理
0911 已将其折叠删除（位图时代 0 簇＝死码，(d) 计数不变，见件内折叠注）。
答案制0911 适配：(e) 位图 6→4（g1/g5 出册，余 g6/g2/g3/g4——(e) 判定式 n_fig==4）；n_ans 14→0（反向锁）；
  页码块/签名口径不涉答案域，其余判据逐字不动；n_sig<40 异常阈值维持（实测见运行行）。
全品对齐0911 复跑注：判断简析 6 行随 6h 出册→正文 [解析] 签名行退场，n_sig 基线 97→实测 91（恰 −6）；
  判断行尾「（　）」系 fil 后独立片段行，（＋U+3000 不成「（\d」不匹配 SIG——天然不进 (c)，实测 0 违规；
  (a)(b) 禁区 grep 不受 \zhentib/\kongbai 新宏影响（无 hangindent、无 \hspace*{2em}）。"""
import os
import re
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
PT = 72 / 25.4
# F 0909 收尾轮（V7b 断言适配）：MARGIN/COLSEP 按 F 版 qp-layout 新参数（版心 174.85mm＝margin 17.575、
# columnsep 9.25mm、栏宽 82.8mm）——旧 15/7.5 系 C 版值，致 (d) 表左框线全部匹配不到栏左（0<6 误失败）
# H1 片 0909c 适配（E7 版面基准）：margin 17.575→17.2mm、columnsep 9.25→7.6mm（栏宽 84.0mm）；顶距
# 19.6mm 只影响纵向（本脚本 (a)-(e) 均为横向/顶格判据，不涉足）——(d) 表线/表左框线基准随之复位。
MARGIN = 17.2 * PT                             # 48.76pt 版心左＝左栏左
BOT = 20 * PT                                  # 56.7pt 版心底＝20mm（v4.2 拍板22 正文区让位页脚带）
COLSEP = 7.6 * PT
COLW = (595.276 - 2 * MARGIN - COLSEP) / 2     # 238.11pt＝84.0mm（全品栏宽实测档）
MID = MARGIN + COLW + COLSEP / 2               # 297.62pt 栏中缝
COLL = (MARGIN, MARGIN + COLW + COLSEP)        # 左/右栏左 48.76 / 308.36
TOL = 3.5                                      # 行首墨迹容差 pt

fail = []

# ---- (a)(b) 结构 grep ----
body = open(os.path.join(BASE, 'body.tex'), encoding='utf-8').read()
blk = open(os.path.join(BASE, 'qp-blocks.tex'), encoding='utf-8').read()
bad_body = re.findall(r'\\hangindent|\\hspace\*\{7mm\}|\\hspace\*\{2em\}', body)
bad_blk = re.findall(r'\\hspace\*\{2em\}', blk)
print(f'(a) body.tex 顶格残留 {bad_body or "无"}　(b) qp-blocks.tex 2em 前缀 {bad_blk or "无"}')
if bad_body or bad_blk:
    fail.append('(a/b)结构残留')

# ---- (c)(d)(e) pdf ----
SIG = re.compile(
    r'^(\d+．|\[答案\]|\[解析\]|【诊断分析】|【素养小结】|【学习目标】|[A-D]．|[①②③④⑤⑥⑦⑧⑨]|◆|（\d+|\(\d+)')

def ink_left(page, y0, y1, cl, dpi=300):
    """竖带 [cl−3, cl+7] × [y0−0.5, y1+0.5] 内最左墨迹像素 x（pt），无墨返回 1e9。"""
    clip = pymupdf.Rect(cl - 3, y0 - 0.5, cl + 7, y1 + 0.5)
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    w, h, n, s = pix.width, pix.height, pix.n, pix.samples
    for x in range(w):
        for y in range(h):
            off = (y * w + x) * n
            if (s[off] + s[off + 1] + s[off + 2]) / 3 < 128:
                return clip.x0 + x / (dpi / 72.0)
    return 1e9

doc = pymupdf.open(BASE + r'\main.pdf')
n_sig = n_viol_c = n_ans = n_rules = n_leftedge = n_viol_d = n_fig = n_viol_e = n_exempt = 0
n_press = n_named = 0
# (e) 位图身份认领：原生像素尺寸 → 图号（回退轮 0910 六图源文件，见 素材 media/media/*.png）；
#     仅供打印定位与「恰 6」佐证，不参与判定。像素尺寸为钉死值——换图源（重采样/换档）须同步本表。
FIG_PX = {(1408, 374): 'g6-triple', (691, 1159): 'g1-prism', (764, 764): 'g2-cubeE',
          (521, 496): 'g3-cube6', (788, 424): 'g4-dihedral', (1798, 1350): 'g5-fold'}


# ---- 矢量墨聚簇内核（_diag_items/_vec_clusters，片G 0910 建、回退轮0910 起只服务 (d)）已随
#      残留清理0911 折叠删除：六图回位图后实测 0 簇＝死码，(d) in_fig 恒不触发、表线计数逐字节
#      不变；删前 grep 证无调用。原文见 断言顶格.py.bak_残留清理0911；qp-blocks.tex 的 \huadia
#      素材宏不在此件、未动。

for pno, page in enumerate(doc, 1):
    H = page.rect.height
    def coll(x0):
        return MARGIN if x0 < MID else MARGIN + COLW + COLSEP
    lines = []
    for blk_ in page.get_text('dict')['blocks']:
        for ln in blk_.get('lines', []):
            t = ''.join(sp['text'] for sp in ln['spans']).strip()
            if t:
                lines.append((t, pymupdf.Rect(ln['bbox']), ln['spans'][0]['origin'][1]))

    # (c) 签名行行首墨迹（版心 y 带内）
    for t, r, base in lines:
        if not SIG.match(t):
            continue
        if base < MARGIN - 1 or base > H - BOT + 1:      # 页眉/页脚带豁免（v4.2 版心底＝BOT）——
            continue                                      # 返修3 轮改基线判定：栏首数学行（探四变式1【答案】）行内
                                                          # \overrightarrow 箭头字形 bbox 撑高 y0 至版心顶上方，
                                                          # bbox 判定误豁免致【答案】14→13（基线仍在版心内，非版面缺陷）
        cl0 = coll(r.x0)
        if any(o is not r and abs(o[2] - base) < 2.0          # 基线差 <2pt＝同视觉行
               and o[1].x0 >= cl0 - 1.0                        # 同栏起点（排跨栏同 y 行）
               and o[1].x1 <= r.x0 + 1.0 for o in lines):     # 左侧有文本＝行中元素
            continue
        n_sig += 1
        if t.startswith('[答案]'):
            n_ans += 1
        cl = cl0
        ref = r.x0 if cl - 0.5 <= r.x0 else None
        ink = ink_left(page, r.y0, r.y1, cl) if ref is None else cl
        if not (cl - TOL <= ink <= cl + TOL):
            n_viol_c += 1
            print(f'   (c)违规签名行 x0={r.x0:.2f} 墨迹={ink:.2f} 栏左={cl:.2f} p{pno} y={r.y0:.1f} {t[:14]}')

    # (d) 竖直表线
    for d in page.get_drawings():
        r = d['rect']
        if not (r.width <= 2.0 and r.height >= 4.0):
            continue
        if abs(r.x0 - MID) < 1.0:
            continue   # multicol 栏线
        if 8.0 <= r.height <= 30.0 and any(0.5 <= r.x0 - c <= 3.0 for c in COLL):
            n_exempt += 1   # 花形行 tcbox 左竖边
            continue
        n_rules += 1
        cl = coll(r.x0)
        if r.x0 < cl - 1.0 or r.x1 > cl + COLW + 1.0:
            n_viol_d += 1
            print(f'   (d)表线出栏带 x0={r.x0:.2f} x1={r.x1:.2f} 栏带=[{cl:.2f},{cl + COLW:.2f}] p{pno} y={r.y0:.1f}~{r.y1:.1f}')
        if any(abs(r.x0 - c) <= 1.0 for c in COLL):
            n_leftedge += 1   # 表左框线在场（== 栏左）

    # (e) 图——回退轮 0910 位图口径：\includegraphics 引入的原图位图（media/media/*.png），
    #     逐页归集 PDF 内 raster 图对象；违规＝越栏 ∨ 压字（图矩形与任一正文行 bbox 相交），零容忍。
    for info in page.get_image_info(xrefs=True):
        r = pymupdf.Rect(info['bbox'])
        n_fig += 1
        tag = FIG_PX.get((info['width'], info['height']))
        if tag:
            n_named += 1
        else:
            tag = '未认领(%dx%d)' % (info['width'], info['height'])
        cl = coll(r.x0)
        if not (r.x0 >= cl - 1.0 and r.x1 <= cl + COLW + 1.0):
            n_viol_e += 1
            print(f'   (e)越栏图 {tag} x0={r.x0:.2f} x1={r.x1:.2f} 栏带=[{cl:.2f},{cl + COLW:.2f}] p{pno} y={r.y0:.1f}')
        hit = [t for t, rr, _b in lines if rr.intersects(r)]
        if hit:
            n_press += 1
            print(f'   (e)压字图 {tag} 矩形=[{r.x0:.2f},{r.y0:.2f},{r.x1:.2f},{r.y1:.2f}]'
                  f' 相交正文行 {len(hit)} 首行={hit[0][:14]} p{pno}')

print(f'—— 签名行 {n_sig}（其中[答案]{n_ans}；违规 {n_viol_c}）｜表线 {n_rules}（左框线 {n_leftedge}；'
      f'违规 {n_viol_d}，花形豁免 {n_exempt}）｜位图×{n_fig}（尺寸认领 {n_named}/{n_fig}；'
      f'越栏 {n_viol_e}，压字 {n_press}）')
viol = n_viol_c + n_viol_d + n_viol_e + n_press
ok = viol == 0 and not fail and n_fig == 4 and n_ans == 0 and n_leftedge >= 6   # 答案制0911：n_fig 6→4、n_ans 14→0
if n_sig < 40:
    ok = False
    print(f'!! 签名行计数异常：{n_sig} < 40（签名口径失效嫌疑，人工复核）')
print('断言结果：', '通过' if ok else '未通过')
raise SystemExit(0 if ok else 1)
