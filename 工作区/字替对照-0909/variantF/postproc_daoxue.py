# -*- coding: utf-8 -*-
r"""v4.2 导学件后处理器：sec.tex（pandoc 原始输出）→ chapterhead.tex + body.tex + postproc_daoxue_log.txt。
v4.2 对齐全品轮（22 条改版指令，逐条登记交付报告§九；口径＝与全品原书完全一致）：
A 类：撤页眉（翻拍板8②回归原旨）、四级标题仿粗黑 \heibf、栏间竖线恢复（翻拍板28，black!25＝拍板39 派生档）、
页脚小字黑粗、课时名内容式（第1课时 空间向量的概念及线性运算）、题干图 minipage 并排（图 30mm 档提档至≈34mm）
＋详解图 40mm、花形微调、编注/解析 8pt 黑、题侧 8pt；C 类：条目（1）（2）各自成段、素养小结①②③各自成段、
【诊断分析】单行化、表格列宽内容驱动、选项 4 项/行扩域；D 类：变式/检测补【解析】简析 ×15（逐题亲算）；
E 类：撤★精选标（翻拍板25 导学件部分）；F 类：\kongda 印答盒 \kern0.15em 防粘连；G 类：条目号/检测题号加粗。
v4.3 改版轮（2026-09-08 拍板落槌，逐条登记交付报告§十）：图档 sub3_B_4 45→60mm／image5 40→34mm（居中档 32.5–35.8）、
题干 minipage \raggedright 松排、居中图上下间距 2.8/2.2mm；表格组（外框 0.8pt＞内线 0.4pt＋线色灰122＋首列居中
＋行高＝单行 7.26mm 档＋表顶前距 2.8mm）；检测题号 11.4pt \heihao；题侧→题干 1.3mm；选项行距分档（例区19pt／评价·检测21pt）；
素养小结②③包 \kaishu；【诊断分析】说明紧缩文案（10.5pt 单行）；条目首子项（1）连排机制断言（第8步）。
v4.4 导学件改版执行轮（2026-09-08，规格书＝派工规格书-v44执行轮.md；逐条登记交付报告§十）：
表顶负胶撤除改正胶（0908 标定回填 1.1mm）＋表内行距 13.9pt＋表尾 \addvspace（0908 二次标定回填 2.8mm，旧 -0.8 系带底假口径误调）；
第 6 步 \allowbreak 注入撤除；
新增转换 pass（全角（）→半角／(~~~~)→(\kongwei)／CJK 邻空格清除／【分析】【详解】【点睛】→[ ]，
均计数＋清后 0 断言）；题侧→\tieside 10.5pt 黑半角[]；题号数字 \textbf 加重（检测题号/例N/变式N）；
\tjdnr 改 5 参发射（◆探究点N＋空两字＋名；RENAME 压字探六/探七去括注后缀）；探五例1 多选 \duoxuan；
image5 居中→题侧并排（探九图归位，side×5）；side 行 raisebox 顶对齐 2.6mm＋\hspace{1.2mm}；
居中图尾距 -1.7→-1.0mm（0908 二次标定：首轮 -0.3 实测图底→下块 3.22 出窗 0.4–2.6）；
检测提示词 \zhuzhu→\zhushi（\zhuzhu 的 [注意] 前缀不再占用提示词位）。
F 片A 图文形态轮（2026-09-09）：image1 剪垫（839×1345→691×1159，墨幅冻结 27.2×45.67mm）＋
探二/探九图归位【详解】区（挂详解首块文字旁）＋探三/六/八题干图留位；五组并排几何档 3c 重写
（文字栏宽逐图标定／图盒按墨宽折算／盒间胶与 raisebox 高由图墨右缘距栏右 2.6mm 与图墨顶 −0.25mm 反解）。
v4.1 用户过目轮（依据＝用户以全品原书 p04/p05/p06 提出的 11 条改版指令，逐条登记交付报告§八）：
知识点区挖空印答（\kongda，原词下划线印出，仅例题/变式/检测题干保留 \kongbai）、判断题加第 4 参【解析】＋
全品式（1）（2）序号、花形行栏内化（撤 multicols 切分，单一 multicols，花形为栏内首元素，菱形标＋栏宽灰线）、
条目号按知识点重起（知识点一 1～3／二 1～2／三 1～4，投影向量入号）、章名「第一章」。
结构：章首通栏（章22 左对齐/节18/小节15/课时14＋章首错位灰方块）→【学习目标】×3（楷体化压缩，通栏区）
→ \begin{multicols}{2} → 花形行「课前预习」（栏内首元素）→ ◆知识点×3（条目挖空印答＋编注段末并排＋三列挖空表；每知识点后紧跟【诊断分析】判断块×2 题）
→ 花形行「课中探究」（栏内）→ ◆探究点×9（恒式＝例1＋变式1＋素养小结；◆标题与例1 同段内联）
→ 花形行「课堂评价」（栏内）→ 检测×5（3 单选＋2 填空带提示词）→ \end{multicols}。一切题题后紧跟答案（拍板12）。
题侧＝〔难度（知识点N）〕（拍板15/18，撤〔源〕括注）。
题源分配（拍板16 源题优先）：例1×9＝各组第 1 题（题1～7、9、10）；变式1：探究点七＝源题8（池尽前优先池配），
其余 8 点按变式六策命制（逐题亲算，策名逐条登记）；源题 10 题全在场（题量守恒）。
命制登记：v4 轮新命制 14（变式8＋检测4＋诊断2）≤上限 15；沿用 v3 已亲算 5（检测1＋诊断4），逐条登记；
v4.1 轮新增＝判断解析 6 句（逐题亲算复核）＋挖空答案印出（原词来自源/条目文意，逐个核对）；
v4.2 轮新增＝变式解析 9＋检测解析 5（逐题亲算文字转写，D 类16/17）。
模板 8 条坑（v3 交付报告§七）全程规避：\kongbai{} 空组隔离／hangafter 数字后留界／raw 反斜杠纪律／
\underline 只包值／图块段 hangindent 残留靠首行不缩进规避＋控制字符扫描兜底／reflow 输出流分离／渲染前清 png。"""
import re

# F 0909：BASE 本地化到 variantF（原指向 样张v4\导学件——只读区，曾致误写，见交付报告F 事故登记；
# sec.tex 已随 variantF 目录分发，与只读区逐字节一致）
BASE = r"C:\提示词\工作区\字替对照-0909\variantF"
LOG = []
log = LOG.append

tex = open(BASE + r"\sec.tex", encoding='utf-8').read()
n_sec_fh = tex.count('；')

# ---- 1. 源清洗（同 v2/v3）：U+2060、箭头归一化、长下划线挖空 ----
tex = tex.replace('\u2060', '')
tex = tex.replace(r'\overset{⃑}{', r'\overrightarrow{')
n_kong = len(re.findall(r'(?:\\_){4,}', tex))
tex = re.sub(r'(?:\\_){4,}', r'\\kongbai{}', tex)
log(f'1. 源清洗：去 U+2060、\\overset{{⃑}}{{}}→\\overrightarrow{{}}（同 v2/v3）；长下划线→\\kongbai ×{n_kong}（题干挖空留白线，'
    f'仅例题/变式/检测；课前预习知识点区挖空经 #4 段改 \\kongda 印答）；源节分号计数（清洗后）＝{n_sec_fh}')

blocks = [b.strip() for b in re.split(r'\n\s*\n', tex) if b.strip()]

# ---- 2. 解析：讲部条目 ＋ 题部组/题 ----
RE_ENTRY = re.compile(r'^1\.1\.1-(\d)．〔基〕')
RE_GRP = re.compile(r'^\\textbf\{(1\.1\.1\.(\d+) [^}]*)\}$')
RE_TI = re.compile(r'^\\textbf\{(1\.1\.1\.(\d+)-(\d+)．（(简单|中档|难)）)\}(.*)$', re.S)

entries, tis, grp_order = {}, {}, []
cur_entry = cur_grp = cur_ti = None
for b in blocks:
    m = RE_GRP.match(b)
    if m:
        cur_grp = m.group(1)
        cur_ti = None
        if m.group(2) != '1':
            grp_order.append(cur_grp)
        continue
    m = RE_ENTRY.match(b)
    if m:
        cur_entry = int(m.group(1))
        entries[cur_entry] = {'title': b, 'note': None, 'blocks': [], 'tables': 0}
        continue
    m = RE_TI.match(b)
    if m:
        key = (int(m.group(2)), int(m.group(3)))
        cur_ti = key
        tis[key] = {'num': f'1.1.1.{key[0]}-{key[1]}', 'nanidu': m.group(4),
                    'stem': [m.group(5).replace('\n', ' ').strip()] if m.group(5).strip() else [],
                    'ans': '', 'zsd': '', 'fenxi': [], 'xiangjie': [], 'dj': []}
        continue
    if cur_entry is not None and not tis:
        if b.startswith('【编注】') and entries[cur_entry]['note'] is None:
            entries[cur_entry]['note'] = b[len('【编注】'):].strip()
        elif b.startswith('【微提醒】'):
            entries[cur_entry]['blocks'].append(b)
        elif '\\begin{tabular}' in b or '\\begin{longtable}' in b:
            entries[cur_entry]['tables'] += 1
        else:
            entries[cur_entry]['blocks'].append(b)
        continue
    if cur_ti:
        d = tis[cur_ti]
        if b.startswith('【答案】'):
            d['ans'] = b[len('【答案】'):].strip() or 'NEXT'
        elif b.startswith('【知识点】'):
            d['zsd'] = b[len('【知识点】'):].strip() or 'NEXT'
        elif b.startswith('【分析】'):
            d['fenxi'] = [b] if len(b) > len('【分析】') else []
        elif b.startswith('【详解】'):
            d['xiangjie'] = [b]
        elif b.startswith('【点睛】'):
            d['dj'] = [b]
        elif d['ans'] == 'NEXT':
            d['ans'] = b.replace('\n', ' ')
        elif d['zsd'] == 'NEXT':
            d['zsd'] = b.replace('\n', ' ')
        elif d['fenxi'] and not d['xiangjie']:
            d['fenxi'].append(b)
        elif d['xiangjie']:
            d['xiangjie'].append(b)
        else:
            d['stem'].append(b.replace('\n', ' '))
for k, d in tis.items():
    assert d['ans'] and d['ans'] != 'NEXT', f'{d["num"]} 答案缺失'
log(f'2. 解析：讲部条目 {len(entries)} 个（编注 {sum(1 for e in entries.values() if e["note"])} 条、'
    f'讲部表 {sum(e["tables"] for e in entries.values())} 张，longtable 环境不排印）；题部组 {len(grp_order)} 组、题 {len(tis)} 道：'
    + '；'.join(f'{d["num"]}({d["nanidu"]})' for d in tis.values()))
log('2b. 组数核对：题部组 9 组（1.1.1.2～1.1.1.10，其中 1.1.1.8 含 2 题）＋讲部组 1 组（1.1.1.1）；'
    '【知识点】标签不排印（登记），题侧改挂（知识点N）（见 5g 映射台账）')

# ---- 3. 图分档＋处置（v4.2-A6 重写；F 片A 0909 改图位与几何）：
#      side=文字左 minipage＋图右 minipage 并排（几何档见 3c，全品截图实证）；
#      center=详解内图维持居中独立行（40mm 提档）；三联图 45mm 居中不动。逐图定性登记见 reflow/emit 处 log。
FIG = {'sub3_B_4.png': ('center', '60mm'),   # 条目3 投影三联图：居中独立行（v4.3 图区组 45→60mm 提档）
       'image1.png': ('side', ''),           # 探究点二例1（题2）图：F 片A 0909 归位【详解】区（挂「连接CA₁」旁，源实证段168）
       'image2.png': ('side', ''),           # 探究点三例1（题3）题干图：minipage 并排（留题干）
       'image3.png': ('side', ''),           # 探究点六例1（题6）题干图：minipage 并排（留题干）
       'image4.png': ('side', ''),           # 探究点八例1（题9）题干图：minipage 并排（留题干）
       'image5.png': ('side', '')}           # 探究点九例1（题10）图：F 片A 0909 归位【详解】区（挂「过点B，D分别向AC作垂线」旁）
FIGRE = re.compile(r'\\includegraphics\[(width=[\d.]+in,height=[\d.]+in)(,alt=\{[^}]*\})?\]\{([^}]+)\}')
figs_seen = []

# ---- 3c. F 片A 并排几何档（0909 全品截图实证）：文字左 \raggedright／图右侧／
#      图墨右缘距栏右 2.6±1mm／图文墨缝 6.7±1.5mm／图墨顶比首行墨顶高 0.25mm（窗 ±1）。
#      剪垫后按墨宽排印（勿因剪垫放大墨幅）：图盒宽＝墨宽目标折算，G 由墨右缘位置反解。 ----
COLW_MM = 82.8            # 栏宽（qp-layout 版心 174.85mm − columnsep 9.25mm 折半）
SIDE_BOX_W_MM = 33.12     # 旧置入盒宽 0.40\linewidth（ink_w=None 时按此盒折算维持现行墨宽）
SIDE_TEXT_W_MM = 46.368   # 文字 minipage 默认宽（0.56 栏）
SIDE_C0 = 2.96            # 首行墨顶相对基线（D 组实测反推 2.95–3.04；topdiff = c0 − H + pad_t）
SIDE_TOP_SHIFT = 0.25     # 图墨顶目标＝首行墨顶 −0.25mm（全品截图 0.25mm 档）→ H = c0 + pad_t + 0.25
SIDE_DEF = {
    # ink_w：打印墨宽目标 mm（None＝维持现行置入墨宽）；r_edge：图墨右缘距栏右 mm；
    # text_w：左栏文字宽 mm；c0：首行墨顶标定（缺省 SIDE_C0）——片A 0909 探针标定值
    'image1.png': dict(ink_w=27.200, r_edge=1.70, text_w=49.000, c0=3.04),  # 剪垫后冻结墨幅 27.2×45.67mm（勿放大）；T=49 令详解式首段成行（48.68 档）
    'image2.png': dict(ink_w=None, r_edge=2.0, text_w=46.368),
    'image3.png': dict(ink_w=None, r_edge=1.70, text_w=46.368),
    'image4.png': dict(ink_w=None, r_edge=2.6, text_w=44.000),   # T=44 避空位右挂件压图（挂件右缘 T−1.6 档）
    'image5.png': dict(ink_w=30.000, r_edge=2.6, text_w=46.368),   # 墨宽 33.12→30.0（−9.4%，配 T 标准档令缝落 6.6mm；近全品截图 29.6 档）
}

from PIL import Image as _PILImage

def _ink_geom(name):
    """PNG 墨 bbox（alpha 合成白底，阈值 245——与取证 C 同口径）。返回 (w_px, h_px, (l,t,r,b))。"""
    im = _PILImage.open(BASE + r'\media\media\\' + name).convert('RGBA')
    w, h = im.size
    bg = _PILImage.new('RGB', (w, h), (255, 255, 255))
    bg.paste(im, (0, 0), im)
    bb = bg.convert('L').point(lambda v: 255 if v < 245 else 0).getbbox()
    assert bb, f'{name} 无墨（阈值 245）'
    return w, h, bb

def side_row(text, tok, tag):
    r"""F 片A 并排几何（全品截图档）。结构＝左 \begin{minipage}[t]{T mm}\raggedright 文字
    ＋ \hspace{G} ＋ 右 \begin{minipage}[t]{PRINTW mm} 图盒。G 由图墨右缘距栏右 r_edge 反解：
    G = 栏宽 − r_edge + 图盒右留白 − 文字栏宽 T − 图盒宽；图盒宽＝墨宽目标折算
    （剪垫不放大墨幅）。竖直：\raisebox 声明盒 [height=H][depth=\height−H]，H = c0 + pad_t + 0.25——
    图墨顶＝基线−H+pad_t、首行墨顶＝基线−c0，差落 [−1,+1]mm（目标 −0.25）。
    盒深参与行距＝后续文字推到图底之下（F 0909 R3 修复保留）。空位括号右挂（探八）保留。"""
    figs_seen.append(('side', tok, tag))
    hang = ''
    for tail in ('(~~~~)', '（）', '()'):
        if text.endswith(tail):
            text = text[:-len(tail)]
            hang = r'\nobreak\mbox{}\nobreak\hfill(\kongwei)\hspace{0.56mm}'
            log(f'3b-F. 并排题干空位右挂 ×1（{tag}）：题干尾空位 {tail} 改 \\hfill 末行右挂＋尾胶 0.56mm'
                f'（全品 p07 题1-3 形；孤括号行缺陷位消解，右挂件直发 \\kongwei 终形）')
            break
    name = re.search(r'\{([^{}]+)\}$', tok).group(1).split('/')[-1]
    w_px, h_px, (l, t, r, b) = _ink_geom(name)
    cfg = SIDE_DEF[name]
    ink_px_w = r - l
    ink_w = cfg['ink_w'] or SIDE_BOX_W_MM * ink_px_w / w_px
    scale = ink_w / ink_px_w                      # mm/px——按墨宽排印
    print_w = w_px * scale                        # 图盒宽（含 1px 级留白）
    pad_r, pad_t = (w_px - r) * scale, t * scale
    text_w = cfg.get('text_w', SIDE_TEXT_W_MM)
    glue = COLW_MM - cfg['r_edge'] + pad_r - text_w - print_w
    H = cfg.get('c0', SIDE_C0) + pad_t + SIDE_TOP_SHIFT
    assert glue > 0 and text_w + glue + print_w <= COLW_MM + 0.02, \
        f'{name} 并排几何出栏：glue={glue:.2f} total={text_w + glue + print_w:.2f}/{COLW_MM}'
    assert H > 0
    tok2 = re.sub(r'width=[^,\]]+', 'width=%.3fmm' % print_w, tok)
    log(f'3c-A. 并排几何（{tag}／{name}）：墨宽 {ink_w:.2f}×{(b - t) * scale:.2f}mm，盒宽 {print_w:.2f}mm，'
        f'盒右/上留白 {pad_r:.2f}/{pad_t:.2f}mm，文字宽 {text_w:.2f}mm，墨右缘距栏右 {cfg["r_edge"]:.2f}mm，'
        f'盒间胶 {glue:.2f}mm，raisebox 高 {H:.2f}mm（图墨顶目标 −0.25mm 档）')
    return (r'\noindent\begin{minipage}[t]{%.3fmm}\raggedright ' % text_w + text + hang +
            r'\end{minipage}\hspace{%.3fmm}' % glue +
            r'\begin{minipage}[t]{%.3fmm}\centering' % print_w +
            r'\raisebox{\dimexpr-\height+%.3fmm\relax}[\dimexpr%.3fmm\relax][\dimexpr\height-%.3fmm\relax]{' % (H, H, H)
            + tok2 + r'}\end{minipage}\par')

def reflow(blocks_in, tag):
    out = []
    for b in blocks_in:
        if '\\begin{tabular}' in b or not FIGRE.search(b):
            out.append(b)
            continue
        last = 0
        for mm in FIGRE.finditer(b):
            if b[last:mm.start()].strip():
                out.append(b[last:mm.start()].strip())
            name = mm.group(3).split('/')[-1]
            kind, w = FIG.get(name, ('center', '30mm'))
            assert w, f'{tag}: {name} 未分档'
            tok = mm.group(0).replace(mm.group(1), 'width=' + w)
            if kind == 'side':
                # side 图独立成块抵达此处（不应发生）：与块内已有文字并排，无文字则退化为居中
                out.append(side_row(b[last:mm.start()].strip() or r'\hfill', tok, tag))
            else:
                figs_seen.append((name, w, tag))
                # v4.3 图区组（总账F）：居中图上下间距目标＝全品墨口径 2.8/2.2mm。
                # 块首必须 \par：图块被 \bindp（\noindent）接入前段时 \vspace 陷水平模式（\vadjust）失效，
                # 0908 校准实测前距塌 0.84≈旧 0.8（ink 口径）；\par 后 \vspace 才是栏内真胶。
                # 胶值回填（0908 渲染实测，ink 口径）：\par 结构下胶 2.8/2.2 出墨 3.73-3.56/5.76-6.43，
                # 结构垫高（baselineskip 系）前 +0.85／后 +3.9，回填 1.9/-1.7 → 实测 2.8/2.2±0.3 落窗。
                # v4.4⑫：图尾 -1.7→-0.3mm——下邻块距改走「图底→下块顶 0.4–2.6mm」新窗（断言⑥），
                # 0908 二次标定：-0.3 实测 3.22 出窗，回填 -1.0mm（目标中值 1.5，成因登记）。
                out.append(r'\par\vspace{1.9mm}\penalty10000\noindent\makebox[\linewidth][c]{' + tok + r'}\par\vspace{-1.0mm}\penalty10000')
            last = mm.end()
        if b[last:].strip():
            out.append(b[last:].strip())
    return out

def consume_side(stem_list, tag):
    """v4.2-A6：题干块列内首个 side 图——抽出图 token，返回（题干余块、图 token）。无 side 图返回 (原列, None)。"""
    for i, b in enumerate(stem_list):
        for mm in FIGRE.finditer(b):
            name = mm.group(3).split('/')[-1]
            if FIG.get(name, ('', ''))[0] == 'side':
                tok = mm.group(0).replace(mm.group(1), 'width=\\linewidth')
                rest = stem_list[:i] + [b[:mm.start()] + b[mm.end():]] + stem_list[i+1:]
                rest = [x for x in rest if x.strip()]
                return rest, tok
    return stem_list, None

def extract_fig(blocks, figname):
    """v4.2-返修2：从块列中抽出指定图 token（width=\\linewidth）——图在题干后续块（详解流内）时配题干用；
    块内剩余文字保留（空块删除）。找不到即 assert（图源漂移防漏改）。"""
    for i, b in enumerate(blocks):
        for mm in FIGRE.finditer(b):
            if mm.group(3).split('/')[-1] == figname:
                tok = mm.group(0).replace(mm.group(1), 'width=\\linewidth')
                rest = blocks[:i] + [b[:mm.start()] + b[mm.end():]] + blocks[i+1:]
                rest = [x for x in rest if x.strip()]
                return rest, tok
    assert False, f'返修2：{figname} 在块列中未找到（图源漂移，人工复核）'

# ---- 3b. 选项网格（拍板21：极短 4 项/行、短 2 项/行、长 1 行/项；分号字符全保留） ----
COMPOSED = []   # 命制/演示文字流（分号守恒对账用）

# v4.3 拍板9：选项行距分档——例题区 19pt／评价·检测区 21pt（emit_blocks/grid_lines 按当前档外包
# \fontsize；OPTLH[0] 由组装段切换：课中探究前置 '19'，课堂评价段前置 '21'）
OPTLH = ['19']

def opt_wrap(s):
    # 行距档组内收段（\par 必须在 \fontsize 组内，段参数才取本档 baselineskip——
    # 0908 实测组外 \par 时选项 pitch 恒 18pt，19/21 档失效）
    return r'{\fontsize{10.5pt}{' + OPTLH[0] + r'pt}\selectfont ' + s + r'\par}'

def opt_len(s):
    """v4.2-C15 修复：原把 \( \) 括号计入宽度致检测2/检测4 短数学项被判 1 项/行——
    剥控制词（\frac 等）、非字母控制符（\( \) \{ \}）、括号（）()[] 与花括号后再估宽。"""
    t = re.sub(r'\\[a-zA-Z]+', '', s)
    t = re.sub(r'\\[^a-zA-Z]', '', t)
    t = re.sub(r'[\\{}$&%()\[\]（）]', '', t)
    return sum(1.0 if ord(ch) > 0x2E7F else 0.55 for ch in t)

def grid_lines(s):
    """A．…；B．…；C．…；D．… → 槽位网格行；分号原样保留（拆分后逐一回填）。
    v4.2-C15：剥括号后短数学项估宽大降，4 项/行阈值 2.8→4.8（4 槽容量 0.25×栏宽−0.5em≈55.9pt≈5.3 字档，
    阈值 4.8＝内容 ≤3.3 字档≈34.7pt 留余量；检测3 长选项仍 >6.5 判 1 项/行）。"""
    parts = re.split(r'；(?=\s*[A-D]．)', s)
    if len(parts) == 1:
        return [r'\bindopt ' + opt_wrap(s)]
    opts = [p.strip() for p in parts if p.strip()]
    for i in range(len(opts) - 1):
        if not opts[i].endswith('；'):
            opts[i] += '；'
    # v4.2-C15：项尾「；」为分隔符非选项内容，估宽前剥除（回填原文不动）
    lens = [opt_len(o.rstrip('；')) + 1.5 for o in opts]
    mx, n = max(lens), len(opts)
    per = 4 if (n == 4 and mx <= 4.8) else (2 if mx <= 6.5 else 1)
    rows = []
    for i in range(0, len(opts), per):
        row = opts[i:i + per]
        if len(row) == 1:
            rows.append(r'\bindopt ' + opt_wrap(row[0]))
        else:
            slot = r'0.25\linewidth-0.5em' if per == 4 else r'0.5\linewidth-1em'
            rows.append(r'\bindopt ' + opt_wrap(''.join(
                r'\makebox[\dimexpr' + slot + r'\relax][l]{' + o + '}' for o in row)))
    log(f'3b. 选项网格：{n} 项 {per} 项/行（最长估 {mx:.1f} 字档，v4.2 剥括号估宽；行距 {OPTLH[0]}pt 档）')
    return rows

def emit_blocks(bs):
    """续块分类：A．起且含分号→选项网格；A．/①起→2em 缩进绑定；其余段前绑定。
    v4.3：选项行（A．起）一律按当前 OPTLH 档外包行距（①链不属选项，不外包）。"""
    for s in bs:
        if re.match(r'^A．', s) and '；' in s:
            body.extend(grid_lines(s))
        elif s.startswith(('A．', 'B．', 'C．', 'D．')):
            body.append(r'\bindopt ' + opt_wrap(s))
        elif s.startswith('①'):
            body.append(r'\bindopt ' + s)
        else:
            body.append(r'\bindp ' + s)

# ---- 4. 挖空印答（原词登记，v4.1 指令1：知识点区 \kongbai→\kongda 印出下划线答案） ----
n_kb = [0]
def kb(word):
    n_kb[0] += 1
    log(f'4. 挖空印答 #{n_kb[0]}：原词「{word}」→ \\kongda{{{word}}}（下划线印出，最小宽 15mm 自适应）')
    return r'\kongda{' + word + '}'

TABW = ('17', '37', '25')   # v4.2-C14 起按表配宽（kbtable 第 5 参显式传入），此默认仅存档
# F 片B 0909 #30（意见31 甲案标定回填）：extrarowheight 0.4→1.7mm（qp-layout:76，甲案 2.6 实测出窗）＋
# 行尾胶按行折数自动分档（\tabrowglue：1/2/≥3 折 → 0.85/4.65/7.60mm，qp-layout 定义）；
# 表头行胶单独回拨维持行高≈9.0mm（全品 9.03，实测 9.18）。
TABHEAD_G = '0.45mm'
# v4.4①（BG-04 表顶前距 2.77mm 档）：负胶 -3.8mm 撤除改正胶——上一块段尾 \addvspace{1mm} 与
# 行盒深构成自然缝≈0.4mm；0908 标定：2.4mm 实测 3.95/4.12 出窗（窗 2.2–3.4，断言⑦表顶），
# 回填 1.1mm（成因登记：正胶叠加段间垫胶同向垫高，与表尾 -0.8 同因）
# F 片B 0909 #36 连带复标：\tiaomu 尾距 1.8→0.35mm（-1.45）——表顶前距＝尾距＋TABTOP 叠加，
# TABTOP 1.1→2.55mm 全额回填（三表前距 4.29/3.44/3.44 维持）
TABTOP = r'\vspace{2.55mm}'
n_tab = [0]
def kbtable(h1, h2, h3, rows, widths, tcsep=3):
    r"""v4.2-C14：列宽内容驱动（对照全品 p04 表三列宽比 19%:41%:40%）——
    可用宽＝栏宽 86.2mm−框线 4×0.4pt−tabcolsep 6×tcsep；三列和 ≤可用宽；逐表编译目检微调。
    v4.2-表1 翻修：tcsep 2pt 档（组内局部 \setlength，不影响全局 3pt）——配合 (16,35,29) 使
    定义列 35mm（省 2 折行行、表1 装进 p1 左栏）且名称列保 16mm（4 字名不折行）。
    v4.3 总账D：表线深灰 122（\arrayrulecolor{gray122}，表组内不泄漏）；外框 0.8pt（!{\vline width 0.8pt}
    左右框＋组内 \\arrayrulewidth 加档 \\hline 顶底线）＞内线 0.4pt；首列居中（\\centering 替 \\raggedright）；
    行高留白＝全品单行 7.26mm 档（arraystretch 1.05＋extrarowheight，qp-layout 全局）；表顶前距 TABTOP（0908 标定 1.1mm 正胶）。
    v4.5-F（P-E 0909，实测＝_calib/pe_measure.py 读全品 p04 表1 裁片）：表头三格居中（定义/表示 padL=padR
    13.55/13.12mm）；列1/2 撤 \raggedright 改两端对齐（全品非末行右缘齐平 R1.69–2.12mm、末行左起）；
    三列 p→m 格内竖直居中（全品多行格 padT=(行高−块高)/2 反推吻合 3.53/3.81/4.16mm）。"""
    n_tab[0] += 1
    usable = 86.2 - 1.6 * 25.4 / 72 - 6 * tcsep * 25.4 / 72   # 框线 4×0.4pt＋tabcolsep 6×tcsep，折 mm
    # v4.5-F：表头三格全居中——\makebox[\linewidth] 盒内居中（首版 \centering…\par 实测表头行增高
    # 1.39mm→8.75mm：\par 空段副作用，撤；全品 p04 实测表头 padL=padR 13.55/13.12mm）
    head = ' & '.join(r'\makebox[\linewidth]{\textbf{' + c + '}}' for c in (h1, h2, h3))
    # v4.4②（BG-02/03 表内行距）：列前导 \fontsize{10.5pt}{13.9pt}\selectfont——表内行距 13.9pt
    # （单元格行高 7.26mm 档的内行距落点），三列 >{} 前导统一注入（ braces 由 array >{} 隐式组承担，
    # 前导内不得再手写裸 {——0908 首轮编译 19 错即 此因，登记）；表尾 \addvspace{2.8mm}
    # ＝表底→下块顶 3.91mm 档（断言⑦表底缝）。0908 二次标定：-0.8mm 时物理缝（线墨底→下块墨带顶）
    # 实测仅 0.28mm（p1 表→【诊断分析】探针）——旧 +2.7/-0.8 两轮读数 6.96/7.81/11.37 全系断言
    # 「取下带底」假口径（多含一整行行高 ≈3.7mm），断言已改取带顶；按 Δ线性回填 2.8mm（0.28+3.6=3.88）
    fs_lead = r'\fontsize{10.5pt}{13.9pt}\selectfont'
    lines = ['{\\setlength{\\tabcolsep}{' + str(tcsep) + 'pt}\\arrayrulecolor{gray122}',
             TABTOP,
             r'\noindent\begin{tabular}{!{\vline width 0.8pt}>{' + fs_lead + r'\centering\arraybackslash}m{' + widths[0] +
             r'mm}!{\vline width 0.4pt}>{' + fs_lead + r'}m{' + widths[1] +
             r'mm}!{\vline width 0.4pt}>{' + fs_lead + r'}m{' + widths[2] + r'mm}!{\vline width 0.8pt}}',
             r'\thickhline', head + r' \\[' + TABHEAD_G + r']', r'\hline']
    for j, r in enumerate(rows):
        # F 片B 0909 #30：数据格首格 \rowreset、格末 \marklines（TeX 自测折数），行尾胶 \tabrowglue 自动分档
        cells = list(r)
        cells[0] = r'\rowreset ' + cells[0] + r'\marklines'
        for k in range(1, len(cells)):
            cells[k] = cells[k] + r'\marklines'
        lines.append(' & '.join(cells) + (r' \\[\tabrowglue] \hline' if j < len(rows) - 1
                                         else r' \\[\tabrowglue]'))
    lines.append(r'\thickhline')
    lines.append(r'\end{tabular}\par\addvspace{2.8mm}')
    lines.append('}')
    body.append('\n'.join(lines))
    log(f'4b. 三列挖空表 #{n_tab[0]}：白底黑体表头＋外框 0.8pt＞内线 0.4pt＋线色灰122（总账D）＋表头三格/首列居中＋'
        f'列1/2 两端对齐＋三列 m 竖直居中（v4.5-F 实测全品 p04 落档）＋行高＝多行格净空档（arraystretch 1.05＋extrarowheight 1.7mm＋行尾胶按折数分档 0.85/4.65/7.60mm，F 片B 0909 #30 标定回填；表头/单行档单独回拨）＋表内行距 13.9pt（v4.4② 列前导），列宽内容驱动 {"/".join(widths)}mm＋'
        f'tabcolsep {tcsep}pt（三列和 {sum(float(x) for x in widths):.1f}mm≤{usable:.1f}mm 门），'
        f'{len(rows)} 行（cells 选编自源讲部表，挖空印答见 #4 登记），表顶前距 TABTOP 2.55mm 正胶（F 片B 0909 #36 连带回填——\\tiaomu 尾距 -1.45 全额补偿，表顶墨隙实测 4.29/3.44/3.44 维持）、'
        f'表尾 \\addvspace{{2.8mm}}（v4.4② 0908 二次标定回填，表底→下块 3.91 档，旧负胶系假口径误调）')

# ---- 5. 组装正文 ----
body = []
em = body.append
# F 片C 0909 #29（数学符号间距刚性化）：\emergencystretch 8em→2em——8em 曾把 \thickmuskip 的
# plus 分量拉伸到自然值 2.2 倍（正文 =/∥ 两侧实测 1.2–2.35mm）；刚性化已由 qp-layout
# \thickmuskip=5mu 承担（关系胶不再受 emergencystretch 影响）。本值只决定行内空格胶弹性：
# 实测 0pt 出 17 处 overfull、2em 落 0（基线 8em 亦 0）——按任务书「0pt 劣于基线则回试 1–2em」取 2em。
LAN_OPEN = ('\\vspace{1.7mm}%  v4.3 花形前距（0908 实测回填）：课前预习花形为 multicols 栏首元素，'
            '行首胶被 TeX 弃置，前距须在栏区外给——设计 4.5 实出墨距 2.82，+1.7 → 4.5±0.8 窗\n'
            '\\begin{multicols}{2}\n\\emergencystretch=2em')
LAN_CLOSE = '\\end{multicols}'

def huaxing(chars, xiao):
    em(r'\huaxing{' + '}{'.join(chars) + '}{' + xiao + '}')
    COMPOSED.append(chars + xiao)

# 学习目标（楷体化压缩，通栏区——见 chapterhead 组装段 7）
log('5a. 【学习目标】3 条＝演示编写（v3 文案压缩：条目压至 ≤1 行/条，三条要点全保留），楷体排印（拍板28），移入章首通栏区（防 multicols 短栏平衡），登记')

em(LAN_OPEN)
huaxing('课前预习', '知识导学\\quad 素养初识')
log('5b. 花形行×3（v4.3 拍板1＋总账A 复刻）：四枚圆角菱形（组 23.5×6.7mm、内字 11pt \\huabf＝方正黑体＋FakeSlant0.18'
    '＋FakeBold2.0 斜体特粗）＋右词灰122 黑体常规 6.5pt 不加粗坐线（字底贴线 0.43mm）＋底线 1.2pt 灰77（0x4D）'
    '两端缩进（起点 版心左+2.77mm／终点 距栏线 4mm）、花形前距 4.5mm、整行总高≈7.4mm（全品 7.1mm 档）；'
    '文案对齐全品（v4.2-21 新实证修订）：课前预习＝知识导学　素养初识（p04）、'
    '课中探究＝考点探究　素养小结（p05，v4.1 误作「素养提升」已正）、课堂评价＝知识评价　素养形成（p07；'
    '全品第三花形名＝「课堂评价」非「课堂检测」，v4.1「限时训练　当堂达标」撤）；'
    '单一 multicols，课前预习花形为栏内首元素')

# —— ◆知识点一（诊断块①）——
em(r'\zsd{一}{空间向量的概念}')
em(r'\tiaomu{1}{定义：在空间，我们把具有' + kb('大小') + '和' + kb('方向') + r'的量叫做空间向量．'
   r'\zhuzhu{' + entries[1]['note'] + '}}')
# v4.2-C11：条目内（1）（2）并列子项各自成段——条目 2 拆为条目号段（（1）字母表示法）＋ \bindp（2）几何表示法段（序号保留）
# F 片B 0909 #28：拆段首段改零尾距变体 \tiaomuz（1.8mm 尾距曾落 (1)→(2) 中缝 8.21mm/墨 4.53）；
# 条目尾距由 \tiaomutail 挂到条目末段（#36 条目缝统一，0.35mm 档）
em(r'\tiaomuz{2}{（1）字母表示法：用字母 \(\overrightarrow{a},\overrightarrow{b},\overrightarrow{c},\cdots\) 表示．}')
em(r'\bindp （2）几何表示法：用有向线段表示，其' + kb('长度') + r'表示空间向量的模．即若向量 \(\overrightarrow{a}\) 的起点是 \(A\)、终点是 \(B\)，'
   r'则向量 \(\overrightarrow{a}\) 也可记作 \(\overrightarrow{AB}\)，其模记为 \(\left| \overrightarrow{AB} \right|\)．'
   r'\zhuzhu{' + entries[2]['note'] + r'}\tiaomutail')
em(r'\tiaomu{3}{几类特殊向量（见下表）；规定：' + kb('零') + r'向量与任意向量平行．即对任意向量 \(\overrightarrow{a}\)，'
   r'都有 \(\overrightarrow{0}\parallel\overrightarrow{a}\)．\zhuzhu{' + entries[3]['note'] + '}}')
kbtable('名称', '定义', '表示', [
    [r'零向量', r'长度为' + kb('0') + r'的向量叫做零向量', r'记作' + kb('0')],
    [r'单位向量', r'模等于' + kb('1') + r'的向量', r'用 \(e\) 表示，\(|e|=1\)'],
    [r'相反向量', r'与 \(\overrightarrow{a}\) 长度相同而方向' + kb('相反') + r'的向量', r'记作 \(-\overrightarrow{a}\)'],
    [r'共线向量或平行向量', r'表示若干空间向量的有向线段所在的直线' + kb('互相平行') + r'或' + kb('重合'), r'记作 \(\overrightarrow{a}\parallel\overrightarrow{b}\)'],
    [r'相等向量', r'方向相同且' + kb('模相等') + r'的向量', r'记作 \(\overrightarrow{a}=\overrightarrow{b}\)'],
], ('16', '35', '26.7'), tcsep=2)   # F：E 手改②上移——表1 末列 29→26.7mm（E 定稿值）
log('5c-表1. 列宽翻修（16,33,30）→（16,35,29）＋tabcolsep 3→2pt（本表局部组内）：拍板22 版心底 20mm 让位页脚后 '
    'p1 左栏余 81.1mm，(16,33,30) 档表1 实测 85.0mm 装不下（arraystretch 1.15→1.05 仅省 1.2mm——表高主体是折行内容非 strut，'
    '预估 5.8mm 落空）；定义列 33→35mm 使「模等于□1的向量」与「共线向量或平行向量」行各省 1 折行行，表1 → 78.7mm 归位左栏底'
    '（余 2.4mm），p1 左栏利用率 69%→99%；曾试（14,35,30）同装下但名称列 4 字名全折行，目检不过，改 tabcolsep 让宽保名称列')
log('5c. 知识点一：条目 1～3 选编＋挖空印答（v4.1 指令1）；编注以 \\zhuzhu 并入条目段末同段接排（独立段数 0，字符总量不变，对照§四-7）；'
    '三列挖空表 cells 选编自源讲部「特殊向量」表；'
    'v4.2-C11：条目 2（1）（2）并列子项各自成段（全件扫描：条目体内（N）并列且同段连排仅此 1 处——'
    '条目 3 投影向量源文已分段、其余条目无（N）并列，登记），条目号段（（1）字母表示法）＋\\bindp（2）段，序号保留；'
    'F 片B 0909 #28：拆段首段零尾距变体 \\tiaomuz（1.8mm 尾距曾落 (1)→(2) 中缝致 8.21mm/墨 4.53，'
    '修后 6.41/墨 2.75＝普通行距档）；#36：条目尾距 \\tiaomutail 挂条目末段（0.35mm，条目→条目缝统一）')
em(r'\zhenhead{判断正误(正确的打√,错误的打×)}')
PANDUAN = {
    1: [(r'两个空间向量的模相等，则这两个向量相等．', '×',
         r'模相等方向未必相同，还可能相反或斜交，两向量未必相等，故×．'),
        (r'相等向量一定是共线向量．', '√',
         r'相等向量方向相同，所在直线平行或重合，符合共线向量（平行向量）定义，故√．')],
    2: [(r'若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，\(\overrightarrow{b}\parallel\overrightarrow{c}\)，则 \(\overrightarrow{a}\parallel\overrightarrow{c}\)．', '×',
         r'平行传递需 \(\overrightarrow{b}\neq\overrightarrow{0}\)；\(\overrightarrow{b}=\overrightarrow{0}\) 时零向量与任意向量平行，传递性失效，故×．'),
        (r'若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则存在唯一实数 \(\lambda\)，使 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)．', '×',
         r'缺 \(\overrightarrow{b}\neq\overrightarrow{0}\) 前提；且 \(\overrightarrow{a}=\overrightarrow{0}\) 时 \(\lambda\) 不唯一，故×．')],
    3: [(r'若 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)（\(\overrightarrow{a}\)，\(\overrightarrow{b}\) 不共线），则 \(\overrightarrow{p}\)，\(\overrightarrow{a}\)，\(\overrightarrow{b}\) 共面．', '√',
         r'\(\overrightarrow{p}\) 是 \(\overrightarrow{a}\)、\(\overrightarrow{b}\) 的线性组合，由共面向量定理知三向量共面，故√．'),
        (r'两个非零空间向量的数量积大于 \(0\)，则这两个向量的夹角为锐角．', '×',
         r'数量积大于 0 仅保证 \(\cos\theta>0\)，夹角 \(\theta\in[0^\circ,90^\circ)\)；\(\theta=0^\circ\)（同向）时数量积也为正而非锐角，故×．')],
}
def panduan_block(bh):
    for i, (t, a, jx) in enumerate(PANDUAN[bh], 1):
        em(r'\zhenti{（' + str(i) + '）}{' + t + '}{' + a + '}{' + jx + '}')
        COMPOSED.append(t)
    COMPOSED.extend(jx for _, _, jx in PANDUAN[bh])
panduan_block(1)
log('5c′. 【诊断分析】块①（知识点一后紧跟，拍板35⑤）＝2 道：沿用 v3 已亲算 2 道（模相等⇒相等×；相等⇒共线√）；'
    'v4.1 指令2：序号（一）（二）→全品式（1）（2），逐题加一句话【解析】（6.5pt 灰顶格，数学正确性逐题复核），登记')

# —— ◆知识点二（诊断块②）——
em(r'\zsd{二}{空间向量的线性运算}')
em(r'\tiaomu{1}{加法可按' + kb('三角形') + r'法则或' + kb('平行四边形') + r'法则作出；减法 \(\overrightarrow{a}-\overrightarrow{b}\) '
   r'为减向量终点指向被减向量终点；数乘 \(\lambda\overrightarrow{a}\)：当 \(\lambda>0\) 时与 \(\overrightarrow{a}\) 方向' + kb('相同') +
   r'，当 \(\lambda<0\) 时方向' + kb('相反') + r'，当 \(\lambda=0\) 时 \(\lambda\overrightarrow{a}=\overrightarrow{0}\)．'
   r'\zhuzhu{' + entries[4]['note'] + '}}')
em(r'\tiaomu{2}{共线的充要条件：对任意两个空间向量 \(\overrightarrow{a},\overrightarrow{b}\)（\(\overrightarrow{b}\neq\overrightarrow{0}\)），'
   r'\(\overrightarrow{a}\parallel\overrightarrow{b}\) 的充要条件是存在' + kb('实数') +
   r' \(\lambda\)，使 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)．\zhuzhu{' + entries[5]['note'] + '}}')
kbtable('运算', '法则要点', '运算律举例', [
    [r'加法', r'三角形法则／平行四边形法则（与平面向量一致）', r'\(\overrightarrow{a}+\overrightarrow{b}=\overrightarrow{b}+\overrightarrow{a}\)'],
    [r'减法', r'减向量终点指向被减向量终点', r'\((\overrightarrow{a}+\overrightarrow{b})+\overrightarrow{c}=\overrightarrow{a}+(\overrightarrow{b}+\overrightarrow{c})\)'],
    [r'数乘', r'实数 \(\lambda\) 与向量 \(\overrightarrow{a}\) 的乘积仍为向量', r'\((\lambda+\mu)\overrightarrow{a}=\lambda\overrightarrow{a}+\mu\overrightarrow{a}\)'],
    [r'共线', r'\(\overrightarrow{a}\parallel\overrightarrow{b}\)（\(\overrightarrow{b}\neq\overrightarrow{0}\)）', r'\(\overrightarrow{a}=\lambda\overrightarrow{b}\)'],
], ('10', '37', '28.6'))   # F：E 手改②上移——表2 末列 32→28.6mm
log('5d. 知识点二：条目 1～2（原 4～5 重编号，v4.1 指令8 按知识点重起）＋挖空印答＋编注并段；三列挖空表 cells 选编自源讲部「加法／运算律」表')
em(r'\zhenhead{判断正误(正确的打√,错误的打×)}')
panduan_block(2)
log('5d′. 【诊断分析】块②＝2 道：第 1 道沿用 v3 已亲算（平行传递×，b=0 反例）；'
    r'第 2 道 v4 轮新命制（亲算：\(\overrightarrow{b}=\overrightarrow{0}\) 时前提失效、\(\overrightarrow{a}=\overrightarrow{0}\) 时 λ 不唯一，故×），共线充要条件前提辨析；'
    'v4.1 指令2：全品式序号＋逐题加【解析】，登记')

# —— ◆知识点三（诊断块③）——
em(r'\zsd{三}{空间向量的夹角、数量积与共面}')
em(r'\tiaomu{1}{夹角：已知两个非零向量 \(\overrightarrow{a},\overrightarrow{b}\)，在空间中任取一点 \(O\)，'
   r'作 \(\overrightarrow{OA}=\overrightarrow{a},\overrightarrow{OB}=\overrightarrow{b}\)，则大小在' + kb('[0°,180°]') +
   r'内的 \(\angle AOB\) 称为 \(\overrightarrow{a}\) 与 \(\overrightarrow{b}\) 的夹角，记作 \(\langle\overrightarrow{a},\overrightarrow{b}\rangle\)；'
   r'当 \(\langle\overrightarrow{a},\overrightarrow{b}\rangle=\frac{\pi}{2}\) 时，称 \(\overrightarrow{a}\) 与 \(\overrightarrow{b}\)' +
   kb('互相垂直') + r'，记作 \(\overrightarrow{a}\perp\overrightarrow{b}\)．\zhuzhu{' + entries[6]['note'] + '}}')
weiti = next((s for s in entries[7]['blocks'] if s.startswith('【微提醒】')), '')
# v4.4（拍板1）：剥【微提醒】前缀——\zhuzhu 宏自带 [注意] 内联前缀（半角[]），原【微提醒】字面不再排印
if weiti.startswith('【微提醒】'):
    weiti = weiti[len('【微提醒】'):].strip()
em(r'\tiaomu{2}{数量积：定义 \(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)；'
   '规定' + kb('零向量') + r'与任意向量的数量积为 0．'
   r'性质：\(\overrightarrow{a}\perp\overrightarrow{b}\Leftrightarrow\overrightarrow{a}\cdot\overrightarrow{b}=0\)；'
   r'\(\overrightarrow{a}\cdot\overrightarrow{a}={{\overrightarrow{a}}^{2}}={\left| \overrightarrow{a} \right|}^{2}\)；'
   r'\(\left| \overrightarrow{a}\cdot\overrightarrow{b} \right|\leq\left| \overrightarrow{a} \right|\left| \overrightarrow{b} \right|\)．'
   + (r'\zhuzhu{' + weiti + '}' if weiti else '') +
   r'\zhuzhu{' + entries[7]['note'] + '}}')
blk8 = list(entries[8]['blocks'])
blk8[0] = blk8[0] + r'\zhuzhu{' + entries[8]['note'] + '}'   # 条目8 编注并入首段段末（v3 漏排，v4 补排）
# F 片B 0909 #28/#36：条目 3 同为拆段条目——首段零尾距变体，条目尾距挂到末段（\tiaomutail）
em(r'\tiaomuz{3}{投影向量：' + blk8[0] + '}')
_n_emit0 = len(body)
emit_blocks(reflow(blk8[1:], '知识点三'))
assert body[_n_emit0].startswith(r'\bindp'), '条目3 首续段应为 \\bindp'
assert body[-1].startswith(r'\bindp'), '条目3 末段应为 \\bindp（尾距挂载点）'
body[-1] += r'\tiaomutail'
log('5e. 知识点三：条目 1～2（原 6～7 重编号）选编＋挖空印答＋编注并段（微提醒同段并排）；'
    '条目 3（原条目 8「投影向量」，v4.1 指令8 入号，题名「投影向量」取自源条目名）整段源文排印（含投影三联图 45mm 独立居中，编注并入首段段末——v3 漏排，v4 补排登记）；'
    'F 片B 0909 #28/#36：条目 3 同为拆段条目——首段 \\tiaomuz 零尾距（1.8mm 尾距曾落 (1)→如图① 中缝），'
    '条目尾距 \\tiaomutail 移至末段（如图③段末），条目 3→4 缝落普通行距档；'
    '条目 2 源（2）块内容已由条目 2 自编性质句全量覆盖（选编授权，源块不另排）')
em(r'\tiaomu{4}{共面的充要条件：向量 \(\overrightarrow{p}\) 与不共线向量 \(\overrightarrow{a},\overrightarrow{b}\) 共面的充要条件是存在' +
   kb('有序实数对') + r' \((x,y)\)，使 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)．\zhuzhu{' + entries[9]['note'] + '}}')
kbtable('概念', '要点', '记号／范围', [
    [r'夹角', r'\(\angle AOB\)（\(\overrightarrow{OA}=\overrightarrow{a},\overrightarrow{OB}=\overrightarrow{b}\)）',
     r'\(0^\circ\leq\langle\overrightarrow{a},\overrightarrow{b}\rangle\leq180^\circ\)'],
    [r'数量积', r'\(\overrightarrow{a}\) 的模与 \(\overrightarrow{b}\) 在 \(\overrightarrow{a}\) 上投影的数量之积',
     r'\(\overrightarrow{a}\allowbreak\cdot\allowbreak\overrightarrow{b}\allowbreak=\allowbreak|\overrightarrow{a}|\allowbreak|\overrightarrow{b}|\allowbreak\cos\allowbreak\langle\overrightarrow{a},\overrightarrow{b}\rangle\)'],
    [r'投影向量', r'与 \(\overrightarrow{b}\) 同向（\(\cos\allowbreak\langle\overrightarrow{a},\overrightarrow{b}\rangle\allowbreak>0\) 时）',
     r'模为 \(|\overrightarrow{a}|\allowbreak\cos\allowbreak\langle\overrightarrow{a},\overrightarrow{b}\rangle\)'],
    [r'共面', r'存在 \((x,y)\) 使 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)（\(\overrightarrow{a},\overrightarrow{b}\) 不共线）',
     r'\(\overrightarrow{p},\overrightarrow{a},\overrightarrow{b}\) 共面'],
], ('9.5', '36.5', '29.6'))   # F：E 手改②上移——表3 末列 33→29.6mm
# F 片C 0909 #29：首列 10→9.5／次列 36→36.5——relpenalty=10000 后「∠AOB(OA=a,OB=b)」单元
#   不可断行，36mm 出 0.99pt overfull（总宽 75.6mm 不变；首列内容均折行，9.5mm 折法同前）。
em(r'\zhenhead{判断正误(正确的打√,错误的打×)}')
panduan_block(3)
log('5e′. 【诊断分析】块③＝2 道：第 1 道沿用 v3 已亲算（共面表示√）；'
    r'第 2 道 v4 轮新命制（亲算：取 \(\overrightarrow{a}=2\overrightarrow{b}\) 同向得数量积 \(>0\) 而夹角 \(0^\circ\) 非锐角，故×），夹角范围辨析；'
    'v4.1 指令2：全品式序号＋逐题加【解析】，登记')

# —— 课中探究（探究点×9 恒式；花形行栏内化，无 multicols 切分）——
# v4.2-21：右侧文案对齐全品 p05 实证＝「考点探究　素养小结」（v4.1 误作「素养提升」，正）
huaxing('课中探究', '考点探究\\quad 素养小结')

SANJU = {
    2: r'①识别：题干围绕模、方向、零向量、单位向量、相等向量与相反向量罗列说法要求辨误时，判归本题型。'
       r'②操作：对照定义逐条核验，存疑条目用反例否定。③收束：排除错误项定答案，忌凭直觉误选。',
    3: r'①识别：在几何体中给出若干已知向量、要求表示指定向量时，判归本题型。'
       r'②操作：为目标向量选一条首尾相接的路径写出加减链，再把链中各段用相等或共线的已知向量替换，最后合并化简得表达式。'
       r'③收束：复查每段方向与起讫点，防抄错向量。',
    4: r'①识别：指定三个不共面的向量作基底、要求把目标向量写成基底向量的线性组合并求系数时，判归本题型。'
       r'②操作：先把目标向量沿几何路径分解为基底向量的和，再把各段按比例关系代入基底。'
       r'③收束：比较等式两边系数求出待定值，防漏写中间段。',
    5: r'①识别：题干给出 p=xa+yb 或 MP=xMA+yMB 一类线性表示与“共面”结论的互推说法判断时，判归本题型。'
       r'②操作：核对充要条件的前提（两向量不共线或三点不共线）是否齐备，再对缺前提的说法举共线反例排除。'
       r'③收束：最后汇总正确序号定选项。',
    6: r'①识别：题干列出数量积相关的若干等式（平方、商式、乘积展开）要求判断正误时，判归本题型。'
       r'②操作：按定义 a·b=|a||b|cosθ 逐式展开核验，展开后移项验算。'
       r'③收束：警惕向量无除法、数量积无结合律等误用。',
    7: r'①识别：题干在几何体中求两向量的夹角、模长或投影而不建坐标系时，判归本题型。'
       r'②操作：先平移向量使起点共点或选不共面的三个向量作基底，再把相关向量用基底表示并算出数量积与模长。'
       r'③收束：最后代入夹角公式并按向量夹角范围 [0,π] 取角。',
    8: r'①识别：题干给出两向量的模与夹角、并以夹角为锐角/钝角或两向量垂直为条件求参数时，判归本题型。'
       r'②操作：第一步用数量积把条件翻译成不等式或方程（锐角 cos>0、钝角 cos<0、垂直 cos=0）。'
       r'③收束：再求解并剔除使两向量共线的参数，最后写出参数值或取值范围。',
    9: r'①识别：题干在含二面角的拼接图形中求两点距离时，判归本题型。'
       r'②操作：第一步把待求线段对应的向量写成已知棱向量的首尾相接和链，再对模长平方作数量积展开，'
       r'逐项代入模长与夹角（端点处两条垂线段的夹角由二面角决定，注意取 45° 还是 135°）。③收束：最后开方得距离。',
    10: r'①识别：题干为平面图形沿一条直线折起且折后两面垂直、求两点间距离时，判归本题型。'
        r'②操作：第一步在折后图形中过两点对折痕作垂线定出垂足，再把目标向量写成两段垂线与折痕段的和链并平方展开。'
        r'③收束：最后利用面面垂直带来的向量垂直逐项化简、开方得距离。',
}
# v4.2-E18 撤★精选标（翻拍板25 导学件部分：全品导学案无★，★属练习册体系）——原 STAR 字典
# （探究点一/七/九典型性理由）整体撤除，\tjdnr 形参 #4 一并撤（宏签名 4 参），COMPOSED 不再收入理由文字
log('5f-0. ★精选标撤除（v4.2-E18，翻拍板25 导学件部分）：原 v4 拍板25 ★×3（探究点一概念母题/七求参母题/九折叠距离方法母题'
    '＋典型性理由题侧 6.5pt 灰）整体撤——全品导学案无★精选标（★属练习册体系，p04-p07 实证）；'
    '\\tjdnr 宏签名 5 参→4 参（撤 #4 ★块位），COMPOSED 同步不再收入理由文字，断言⑥ ★=0')
CN = '一二三四五六七八九'
KN = {2: '一', 3: '二', 4: '二', 5: '三', 6: '三', 7: '三', 8: '三', 9: '三', 10: '三'}   # 组号→知识点块序

# 变式六策命制（探究点一～六、八、九；亲算核验逐条登记）
BIAN_COMPOSED = {
    1: {'ce': '逆向化＋概念辨析化（选正确→选错误）', 'nd': '简单',
        'stem': r'下列说法错误的是（~~~~）',
        'opts': r'A．零向量与任意向量都平行；B．若 \(|\overrightarrow{a}|=0\)，则 \(\overrightarrow{a}=\overrightarrow{0}\)；'
                r'C．若 \(\overrightarrow{a}=\overrightarrow{b}\)，则 \(|\overrightarrow{a}|=|\overrightarrow{b}|\)；'
                r'D．若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则 \(|\overrightarrow{a}|=|\overrightarrow{b}|\)',
        'ans': r'\ansul{D}',
        'jc': r'亲算：A 规定成立；B 模为 0 即零向量；C 相等必等模；D 平行不需等模（反例 \(\overrightarrow{a}=2\overrightarrow{b}\)），故选 D．'},
    2: {'ce': '换载体（直三棱柱→平行六面体）＋换设问', 'nd': '简单',
        'stem': r'在平行六面体 \(ABCD-A_1B_1C_1D_1\) 中，\(\overrightarrow{AB}=\overrightarrow{a}\)，\(\overrightarrow{AD}=\overrightarrow{b}\)，'
                r'\(\overrightarrow{AA_1}=\overrightarrow{c}\)，则 \(\overrightarrow{D_1B}=\)\kongbai{}．（用 \(\overrightarrow{a}\)，\(\overrightarrow{b}\)，\(\overrightarrow{c}\) 表示）',
        'ans': r'\ansul{\(\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)}',
        'jc': r'亲算：\(\overrightarrow{D_1B}=\overrightarrow{D_1A_1}+\overrightarrow{A_1A}+\overrightarrow{AB}=-\overrightarrow{b}-\overrightarrow{c}+\overrightarrow{a}\)．'},
    3: {'ce': '换载体＋换数值（正方体 1/4→平行六面体 1/2）', 'nd': '简单',
        'stem': r'在平行六面体 \(ABCD-A_1B_1C_1D_1\) 中，点 \(E\) 在 \(A_1C_1\) 上，且 \(\overrightarrow{A_1E}=\frac{1}{2}\overrightarrow{A_1C_1}\)，'
                r'若 \(\overrightarrow{AE}=x\overrightarrow{AA_1}+y(\overrightarrow{AB}+\overrightarrow{AD})\)，则 \(x=\)\kongbai{}，\(y=\)\kongbai{}．',
        'ans': r'\ansul{\(x=1\)}，\ansul{\(y=\frac{1}{2}\)}',
        'jc': r'亲算：\(\overrightarrow{AE}=\overrightarrow{AA_1}+\overrightarrow{A_1E}=\overrightarrow{AA_1}+\frac{1}{2}(\overrightarrow{AB}+\overrightarrow{AD})\)，故 x=1，y=1/2．'},
    4: {'ce': '换设问（互推选择→判定说明）', 'nd': '简单',
        'stem': r'已知 \(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)，判断 \(P\)，\(M\)，\(A\)，\(B\) 四点是否共面，并说明理由．',
        'ans': r'\ansul{共面}（\(\overrightarrow{MP}\) 可由 \(\overrightarrow{MA}\)，\(\overrightarrow{MB}\) 线性表示，故 \(\overrightarrow{MP}\)，\(\overrightarrow{MA}\)，\(\overrightarrow{MB}\) 共面，即 \(P\) 在平面 \(MAB\) 内）',
        'jc': r'亲算：MP=3MA−2MB 为 MA、MB 的线性组合 ⇒ 三向量共面 ⇒ P∈平面 MAB．'},
    5: {'ce': '换设问（辨析→展开计算）', 'nd': '简单',
        'stem': r'已知 \(|\overrightarrow{a}|=2\)，\(|\overrightarrow{b}|=3\)，\(\langle\overrightarrow{a},\overrightarrow{b}\rangle=60^\circ\)，'
                r'则 \((\overrightarrow{a}+2\overrightarrow{b})\cdot(\overrightarrow{a}-\overrightarrow{b})=\)\kongbai{}．',
        'ans': r'\ansul{\(-11\)}',
        'jc': r'亲算：a·b=2×3×cos60°=3；原式=a²+a·b−2b²=4+3−18=−11．'},
    6: {'ce': '换载体（正方体→长方体）＋换设问（求角→求余弦值）', 'nd': '中档',
        'stem': r'在长方体 \(ABCD-A_1B_1C_1D_1\) 中，\(AB=2\)，\(AD=2\)，\(AA_1=1\)，则向量 \(\overrightarrow{AB_1}\) 与 \(\overrightarrow{AC}\) 夹角的余弦值为\kongbai{}．',
        'ans': r'\ansul{\(\frac{\sqrt{10}}{5}\)}',
        'jc': r'亲算：\(\overrightarrow{AB_1}\cdot\overrightarrow{AC}=(\overrightarrow{AB}+\overrightarrow{BB_1})\cdot(\overrightarrow{AB}+\overrightarrow{BC})=|\overrightarrow{AB}|^2=4\)；'
              r'\(|\overrightarrow{AB_1}|=\sqrt5\)，\(|\overrightarrow{AC}|=2\sqrt2\)；cos=4/(√5·2√2)=√10/5．'},
    8: {'ce': '换数值（二面角 45°→60°）', 'nd': '简单',
        'stem': r'在大小为 \(60^\circ\) 的二面角 \(A-EF-D\) 中，四边形 \(ABFE\)，\(CDEF\) 都是边长为 \(1\) 的正方形，'
                r'则 \(B\)，\(D\) 两点间的距离为\kongbai{}．',
        'ans': r'\ansul{\(\sqrt{2}\)}',
        'jc': r'亲算：\(|\overrightarrow{BD}|^2=1+1+1+2\overrightarrow{BF}\cdot\overrightarrow{ED}=3+2\cos120^\circ=2\)，故 √2．'},
    9: {'ce': '换条件（折起 90°→60° 二面角）', 'nd': '中档',
        'stem': r'已知矩形 \(ABCD\) 中，\(AB=1\)，\(BC=\sqrt{3}\)，将矩形 \(ABCD\) 沿对角线 \(AC\) 折起，使二面角 \(B-AC-D\) 的大小为 \(60^\circ\)，'
                r'则 \(|\overrightarrow{BD}|=\)\kongbai{}．',
        'ans': r'\ansul{\(\frac{\sqrt{13}}{2}\)}',
        'jc': r'亲算：BM=DN=√3/2，MN=1，两垂线向量夹角随二面角 60° 得 \(\overrightarrow{BM}\cdot\overrightarrow{ND}=\frac{3}{4}\cos60^\circ=\frac{3}{8}\)；'
              r'\(|\overrightarrow{BD}|^2=\frac{3}{4}+1+\frac{3}{4}+2\cdot\frac{3}{8}=\frac{13}{4}\)，故 √13/2．'},
}
for g, d in BIAN_COMPOSED.items():
    COMPOSED.append(d['stem'])
    if 'opts' in d:
        COMPOSED.append(d['opts'])
    COMPOSED.append(d['ans'])

# v4.2-D16：变式1×9 补【解析】简析行（8pt 黑，排【答案】行下一行）——亲算文字即 BIAN_COMPOSED 各 jc 字段转写；
# 探究点七变式1（源题8）简析由题干答案自明，自拟一句亲算句（m·n=0 展开，λ=−3/2）
BIAN_JX = {
    1: r'A 规定成立；B 模为 0 即零向量；C 相等必等模；D 平行不需等模（反例 \(\overrightarrow{a}=2\overrightarrow{b}\)），故选 D．',
    2: r'\(\overrightarrow{D_1B}=\overrightarrow{D_1A_1}+\overrightarrow{A_1A}+\overrightarrow{AB}=-\overrightarrow{b}-\overrightarrow{c}+\overrightarrow{a}\)．',
    3: r'\(\overrightarrow{AE}=\overrightarrow{AA_1}+\overrightarrow{A_1E}=\overrightarrow{AA_1}+\frac{1}{2}(\overrightarrow{AB}+\overrightarrow{AD})\)，故 \(x=1\)，\(y=\frac{1}{2}\)．',
    4: r'\(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\) 为 \(\overrightarrow{MA}\)、\(\overrightarrow{MB}\) 的线性组合，故三向量共面，\(P\) 在平面 \(MAB\) 内．',
    5: r'\(\overrightarrow{a}\cdot\overrightarrow{b}=2\times3\times\cos60^\circ=3\)；原式 \(=\overrightarrow{a}^2+\overrightarrow{a}\cdot\overrightarrow{b}-2\overrightarrow{b}^2=4+3-18=-11\)．',
    6: r'\(\overrightarrow{AB_1}\cdot\overrightarrow{AC}=(\overrightarrow{AB}+\overrightarrow{BB_1})\cdot(\overrightarrow{AB}+\overrightarrow{BC})=|\overrightarrow{AB}|^2=4\)，\(|\overrightarrow{AB_1}|=\sqrt{5}\)，\(|\overrightarrow{AC}|=2\sqrt{2}\)，故 \(\cos\langle\overrightarrow{AB_1},\overrightarrow{AC}\rangle=\frac{4}{\sqrt{5}\times2\sqrt{2}}=\frac{\sqrt{10}}{5}\)．',
    7: r'\(\overrightarrow{m}\cdot\overrightarrow{n}=(\overrightarrow{a}+\overrightarrow{b})\cdot(\overrightarrow{a}+\lambda\overrightarrow{b})=|\overrightarrow{a}|^2+\lambda|\overrightarrow{b}|^2+(1+\lambda)\overrightarrow{a}\cdot\overrightarrow{b}=18+16\lambda-12(1+\lambda)=6+4\lambda=0\)，故 \(\lambda=-\frac{3}{2}\)．',
    8: r'\(|\overrightarrow{BD}|^2=1+1+1+2\overrightarrow{BF}\cdot\overrightarrow{ED}=3+2\cos120^\circ=2\)，故 \(|\overrightarrow{BD}|=\sqrt{2}\)．',
    9: r'\(BM=DN=\frac{\sqrt{3}}{2}\)，\(MN=1\)；两垂线向量夹角随二面角为 \(60^\circ\)，\(\overrightarrow{BM}\cdot\overrightarrow{ND}=\frac{3}{4}\cos60^\circ=\frac{3}{8}\)；'
       r'\(|\overrightarrow{BD}|^2=\frac{3}{4}+1+\frac{3}{4}+2\times\frac{3}{8}=\frac{13}{4}\)，故 \(|\overrightarrow{BD}|=\frac{\sqrt{13}}{2}\)．',
}
for g, jx in BIAN_JX.items():
    COMPOSED.append(jx)

GRP_KS = {}
for (gn, k) in tis:
    GRP_KS.setdefault(gn, []).append(k)
for gn in GRP_KS:
    GRP_KS[gn].sort()

def sanju_rows(s):
    """v4.2-C12：素养小结三句式按①②③拆行——首段（①识别）随【素养小结】标签，②③各自 \\bindp 顶格独立段。"""
    i2, i3 = s.find('②'), s.find('③')
    assert 0 < i2 < i3, f'素养小结三句式拆分异常：{s[:24]}'
    return s[:i2], s[i2:i3], s[i3:]

for gi, gname in enumerate(grp_order, 1):
    gnum = int(re.match(r'1\.1\.1\.(\d+)', gname).group(1))
    kn = KN[gnum]
    d = tis[(gnum, GRP_KS[gnum][0])]   # 各组第 1 题＝X-1（组2→题1…组8→题7；组8 双题后组9→题9、组10→题10）
    # v4.4⑨（压字清单）：探究点名 RENAME——探六（源「数量积求夹角与投影（非坐标法）」）、
    # 探七（源「数量积条件求参（夹角与垂直）」）去括注后缀（◆探究点N＋名 单行≤82mm，断言⑫）；
    # 探八/探九（源「数量积求距离（展开法）／（折叠矩形）」）12 字后缀保留合规，不压字
    RENAME = {6: '数量积求夹角与投影', 7: '数量积条件求参'}
    dotname = RENAME.get(gi, gname.split(' ', 1)[1])
    # v4.4⑦（拍板2）：例1 数字 \textbf 加重；⑧（TJ-04）：探五例1（题5 答案 AD）挂多选标记 \duoxuan
    label = r'例\textbf{1}' + (r'\duoxuan' if gi == 5 else '')
    tjd_args = CN[gi-1] + '}{' + dotname + '}{' + label + '}{' + d['nanidu'] + '（知识点' + kn + '）'
    stem_rest, side_tok = consume_side(d['stem'][1:], f'例{gi}')
    detail_tok = None
    if side_tok is None and gi in (2, 9):
        # F 片A 0909：图归位【详解】区（源实证：探二图＝【详解】段后独立段「段168」、探九图与【详解】同段）——
        # 抽图后挂详解首块文字旁（探二「连接CA₁」／探九「过点B，D分别向AC作垂线」），不再与题干并排
        figname = 'image1.png' if gi == 2 else 'image5.png'
        d['xiangjie'], detail_tok = extract_fig(d['xiangjie'], figname)
        log(f'3-图. 探究点{CN[gi-1]}例1 图 {figname} 归位【详解】区：挂详解首块文字旁'
            f'（{"连接CA₁" if gi == 2 else "过点B，D分别向AC作垂线"}），几何档 3c（全品并排实证）')
    if side_tok is not None:
        # 探三/六/八：题干图 minipage 并排（题干留位，几何档 3c）——◆标签行题干位传空，题干文字入图行左栏
        em(r'\tjdnr{' + tjd_args + '}{}')
        em(side_row(d['stem'][0], side_tok, f'例{gi}'))
        log(f'3-图. 探究点{CN[gi-1]}例1 题干图→minipage 并排（文字左 0.56\\linewidth／图右按墨宽，'
            f'几何档 3c：墨右缘距栏右 2.6±1mm／墨缝 6.7±1.5mm／图墨顶 −0.25mm 档）')
    else:
        em(r'\tjdnr{' + tjd_args + '}{' + d['stem'][0] + '}')
    emit_blocks(reflow(stem_rest, f'例{gi}'))
    emit_blocks(reflow(d['fenxi'], f'例{gi}'))
    if detail_tok is not None:
        # 详解首块与图并排（探二/探九）：图挂首块文字旁，其余详解块照常续排
        assert d['xiangjie'] and d['xiangjie'][0].startswith('【详解】'), \
            f'例{gi} 详解首块异常：{(d["xiangjie"] or [""])[0][:24]}'
        em(side_row(d['xiangjie'][0], detail_tok, f'例{gi}详解'))
        emit_blocks(reflow(d['xiangjie'][1:], f'例{gi}'))
    else:
        emit_blocks(reflow(d['xiangjie'], f'例{gi}'))
    if d['dj']:
        emit_blocks(reflow(d['dj'], f'例{gi}'))
    if gi in BIAN_COMPOSED:
        v = BIAN_COMPOSED[gi]
        # F 0909：变式标签改 \liB（例N 标签维持 \li w600）；F 片D 0909c：\liB 拆双字重（变 FY-w700＋式N FY-w450）
        em(r'\liB{变式\textbf{1}}{' + v['nd'] + '（知识点' + kn + '）}{}{' + v['stem'] + '}')
        if 'opts' in v:
            emit_blocks([v['opts']])
        em(r'\ansline{' + v['ans'] + '}')
        em(r'\jiexi{' + BIAN_JX[gi] + '}')
        log(f'5g. 探究点{CN[gi-1]}：例1＝{d["num"]}（{d["nanidu"]}，源题原样，【分析】【详解】紧跟'
            + ('＋【点睛】' if d['dj'] else '') + '）；变式1＝新命制（' + v['ce'] + '，' + v['nd'] + '）；' + v['jc']
            + '；v4.2-D16 补【解析】简析行（8pt 黑，答案行下一行，jc 转写）')
    else:
        d8 = tis[(gnum, GRP_KS[gnum][1])]   # 组8 第 2 题＝题8（组内第 2 题按节内全局编号）
        em(r'\liB{变式\textbf{1}}{' + d8['nanidu'] + '（知识点' + kn + '）}{}{' + d8['stem'][0] + '}')
        emit_blocks(reflow(d8['stem'][1:], f'变式{gi}'))
        em(r'\ansline{\ansul{' + d8['ans'] + '}}')
        em(r'\jiexi{' + BIAN_JX[gi] + '}')
        log(f'5g. 探究点{CN[gi-1]}：例1＝{d["num"]}（{d["nanidu"]}，源题原样）；'
            f'变式1＝{d8["num"]}（{d8["nanidu"]}，源题池配——拍板16 源题优先，池尽方命制），答案行紧跟；'
            'v4.2-D16 补【解析】简析行（简析由题干答案自明，自拟一句亲算句：m·n=0 展开得 λ=−3/2）')
    p1_, p2_, p3_ = sanju_rows(SANJU[gnum])
    em(r'\xiaojie{' + p1_ + '}')
    em(r'\bindp {\kaishu ' + p2_ + '}')
    em(r'\bindp {\kaishu ' + p3_ + '}')
log('5g-台账. 题源映射（拍板18 撤〔源〕括注，映射留台账）：探究点一↔题1；二↔题2；三↔题3；四↔题4；五↔题5；'
    '六↔题6；七↔题7（变式1＝题8）；八↔题9；九↔题10——源题 10 题全在场（题量守恒），知识点N 侧挂见各题〔〕')
log('5g-台账. 知识点N 映射：题1→知识点一；题2、3→知识点二；题4～10→知识点三（按三列挖空表三块内容域归类）')
log('5g-补. 【点睛】：源题9、题10 含【点睛】，v3 漏排，v4 补排（内容零增删口径，登记）')

# —— 课堂检测（恒 5 题：3 单选＋2 填空带提示词，拍板35④；花形行栏内化，无 multicols 切分）——
# v4.2-21：第三花形名对齐全品 p07 实证＝「课堂评价」（非「课堂检测」），右侧＝「知识评价　素养形成」
# v4.2-⑦：花形行＋检测 5 题整体装 \vbox（box 不可切列）——末页 multicol 平衡断点原恰落花形线后，
# 标线悬空左栏底、题目全数右栏（实测 p6：标线 y=192.7mm 栏末无下级）；整节 vbox 后归位右栏顶，
# 花形线→检测1 缝回 ≤8mm 断言域。左栏末页留白参差收尾＝拍板23，⑤b 实测登记
OPTLH[0] = '21'   # v4.3 拍板9：评价·检测区选项行距 21pt（例区 19pt 档维持默认）
em(r'\vbox{')
huaxing('课堂评价', '知识评价\\quad 素养形成')

def cebiao(nd, kn):
    # v4.4⑤（TJ-03＋#3）：题侧〔〕→ \tieside 半角[]内联——宏自带 [] 与 10.5pt 黑宋体（拍板2 与正文完全同号），
    # 此处只给隙距：标签→[ ] 2.7mm、]→题干 2.2mm（args 不带括号）
    return (r'\hspace{2.7mm}\tieside{' + nd + '（知识点' + kn + '）}' + r'\hspace{2.2mm}')

# v4.2-D17：课堂检测 5 题各补【解析】简析行（8pt 黑，【答案】行下一行）——亲算文字逐题转写
DET_JX = {
    1: r'\(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos60^\circ=2\times3\times0.5=3\)．',
    2: r'\(\overrightarrow{b}=\lambda\overrightarrow{a}\Rightarrow4=2\lambda\Rightarrow\lambda=2\)，\(k=2\)，选 B．',
    3: r'非零向量 \(\overrightarrow{a}\cdot\overrightarrow{b}=0\Leftrightarrow\overrightarrow{a}\perp\overrightarrow{b}\)，充要条件，选 C．',
    4: r'取 \(AC\) 中点 \(G\)，\(\overrightarrow{EF}=\overrightarrow{EG}+\overrightarrow{GF}=\frac{1}{2}\overrightarrow{BC}+\frac{1}{2}\overrightarrow{AD}\)，选 D．',
    5: r'\(\overrightarrow{a}\cdot\overrightarrow{b}=4\times3\times\cos120^\circ=-6\)，\(|\overrightarrow{a}+\overrightarrow{b}|^2=16+9-12=13\)，故 \(\sqrt{13}\)．',
}
for g, jx in DET_JX.items():
    COMPOSED.append(jx)

# v4.2-G20：检测题号加粗（全品实证检测题号 1. 2. 3. 粗黑）＝postproc 输出 {\heiti N．}
#   F 0909：数字改走 \numboldjian（NSC-w700 拉丁族，Height/Depth 裁齐——绕开 xeCJK 数字路由），
#   全角「．」随 \heihao BoldFont（同步升 w700）；E 轮 body 手改形上移回 postproc 源头
em(r'\jiancestem{{\fontsize{11.4pt}{14pt}\selectfont\heihao {\numboldjian 1}．}' + cebiao('简单', '三')
   + r'已知 \(|\overrightarrow{a}|=2\)，\(|\overrightarrow{b}|=3\)，\(\langle\overrightarrow{a},\overrightarrow{b}\rangle=60^\circ\)，'
     r'则 \(\overrightarrow{a}\cdot\overrightarrow{b}=\)\kongbai{}．'
     r'{\zhushi{（提示：\(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)）}}}')
em(r'\ansline{\ansul{3}}')
em(r'\jiexi{' + DET_JX[1] + '}')
COMPOSED.append(r'（提示：\(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\)）')
log('5h. 检测1＝沿用 v3 已亲算（数量积定义求值，答案 3），本轮按 35④ 追加提示词（演示性增补，登记）；v4.2-D17 补【解析】简析行')

jc2_stem = (r'设 \(\overrightarrow{e_1}\)，\(\overrightarrow{e_2}\) 不共线，\(\overrightarrow{a}=2\overrightarrow{e_1}+\overrightarrow{e_2}\)，'
            r'\(\overrightarrow{b}=4\overrightarrow{e_1}+k\overrightarrow{e_2}\)，若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则 \(k=\)（~~~~）')
jc2_opts = r'A．\(\frac{1}{2}\)；B．\(2\)；C．\(-\frac{1}{2}\)；D．\(3\)'
em(r'\jiancestem{{\fontsize{11.4pt}{14pt}\selectfont\heihao {\numboldjian 2}．}' + cebiao('简单', '二') + jc2_stem + '}')
emit_blocks([jc2_opts])
em(r'\ansline{\ansul{B}}')
em(r'\jiexi{' + DET_JX[2] + '}')
COMPOSED.append(jc2_stem); COMPOSED.append(jc2_opts)
log('5h. 检测2（单选）＝本轮新命制（亲算：b=λa ⇒ 4=2λ ⇒ λ=2，k=2×1=2，选 B）；共线定理定量应用；v4.2-D17 补【解析】简析行')

jc3_stem = (r'设 \(\overrightarrow{a}\)，\(\overrightarrow{b}\) 均为非零空间向量，则“\(\overrightarrow{a}\cdot\overrightarrow{b}=0\)”'
            r'是“\(\overrightarrow{a}\perp\overrightarrow{b}\)”的（~~~~）')
jc3_opts = r'A．充分不必要条件；B．必要不充分条件；C．充要条件；D．既不充分也不必要条件'
em(r'\jiancestem{{\fontsize{11.4pt}{14pt}\selectfont\heihao {\numboldjian 3}．}' + cebiao('简单', '三') + jc3_stem + '}')
emit_blocks([jc3_opts])
em(r'\ansline{\ansul{C}}')
em(r'\jiexi{' + DET_JX[3] + '}')
COMPOSED.append(jc3_stem); COMPOSED.append(jc3_opts)
log('5h. 检测3（单选）＝本轮新命制（亲算：两向量均非零时 a·b=0 ⇔ a⊥b，充要，选 C）；数量积与垂直（充要条件为必修前序知识，不超纲）；v4.2-D17 补【解析】简析行')

jc4_stem = (r'在空间四边形 \(ABCD\) 中，\(E\)，\(F\) 分别为 \(AB\)，\(CD\) 的中点，'
            r'则 \(\frac{1}{2}(\overrightarrow{AD}+\overrightarrow{BC})=\)（~~~~）')
jc4_opts = r'A．\(2\overrightarrow{EF}\)；B．\(-\overrightarrow{EF}\)；C．\(\overrightarrow{FE}\)；D．\(\overrightarrow{EF}\)'
em(r'\jiancestem{{\fontsize{11.4pt}{14pt}\selectfont\heihao {\numboldjian 4}．}' + cebiao('简单', '二') + jc4_stem + '}')
emit_blocks([jc4_opts])
em(r'\ansline{\ansul{D}}')
em(r'\jiexi{' + DET_JX[4] + '}')
COMPOSED.append(jc4_stem); COMPOSED.append(jc4_opts)
log(r'5h. 检测4（单选）＝本轮新命制（亲算：\(\overrightarrow{EF}=\frac{1}{2}(\overrightarrow{AD}+\overrightarrow{BC})\)，选 D）；中点向量恒等式（线性运算）；v4.2-D17 补【解析】简析行')

jc5_stem = (r'已知 \(|\overrightarrow{a}|=4\)，\(|\overrightarrow{b}|=3\)，\(\langle\overrightarrow{a},\overrightarrow{b}\rangle=120^\circ\)，'
            r'则 \(|\overrightarrow{a}+\overrightarrow{b}|=\)\kongbai{}．'
            r'{\zhushi{（提示：先算 \(\overrightarrow{a}\cdot\overrightarrow{b}\)，再对 \(|\overrightarrow{a}+\overrightarrow{b}|^2=(\overrightarrow{a}+\overrightarrow{b})^2\) 展开）}}')
em(r'\jiance{' + r'{\fontsize{11.4pt}{14pt}\selectfont\heihao {\numboldjian 5}．}' + cebiao('简单', '三') + jc5_stem + '}' + r'{\ansul{\(\sqrt{13}\)}}')
em(r'\jiexi{' + DET_JX[5] + '}')
# F 0909：E 手改③上移——课堂评价 vbox 尾胶收缩（C 轮标定：自然高超出栏高 9.58pt，盒尾负胶收回，
# 不动任何字号/行距/表距）。注释走 @@VBOXGLUE@@ 占位（6 步 pass 会剥注释内 CJK 邻空格），6d 步回填原字面；
# 注释行与收盒 } 同块发射（块间 \n\n 会在两者间垫空行，与 E 定稿结构不符）
em(r'\vspace{-9.7pt}%@@VBOXGLUE@@' + '\n}')
COMPOSED.append(jc5_stem)
log('5h. 检测5（填空带提示词）＝本轮新命制（亲算：a·b=12×cos120°=−6；|a+b|²=16−12+9=13，故 √13）；模长平方展开；v4.2-D17 补【解析】简析行')
log('5h-小结. 课堂检测恒 5 题＝3 单选（检测2/3/4）＋2 填空带提示词（检测1/5），难度均 简单 ≤例题（拍板35④）；'
    '题侧均挂 [难度(知识点N)]（v4.4⑤ \\tieside 半角[]内联），题答紧跟（拍板12）；'
    'v4.2-⑦：花形行＋检测 5 题整体 \\vbox 装栏（防「课堂评价」标线悬空栏底——multicol 平衡断点切列无视段间 penalty，实测登记）')

em(LAN_CLOSE)

# ---- 6. 巨型公式断点撤除（v4.4③）＋转换 pass（v4.4④）＋分号守恒＋控制字符扫描＋输出 ----
# v4.4③：第 6 步两处 \allowbreak 注入（顶层 = 与 · 后）撤除——拍板3 半角窄式＋PunctStyle=plain 下
# 断行纪律由 xeCJK 接管，注入式断点随旧「巨型公式整行」形态一并废弃；表格 cell 内显式 \allowbreak
# （kbtable 数量积 cell 窄栏断行用）维持不动。6b 对账 _norm 已随本轮扩展规范化（见该函数注）。
body_text = '\n\n'.join(body)

# ---- 6a. v4.4④ 转换 pass（顺序固定：全角括号→空位括注→CJK 邻空格→【】标签；body 域）----
# a) 全角（）→半角（拍板3 半角窄式；断言② 全角（）零残留）；chapterhead head 行同域转换在 7 步
n_paren = body_text.count('（') + body_text.count('）')
body_text = body_text.replace('（', '(').replace('）', ')')
# b) 空位括注 (~~~~)→(\kongwei)（#17 定宽 6.8mm 空档；源 4 处＋命制 4 处＝8）
n_kw = body_text.count('(~~~~)')
assert n_kw == 8, f'空位括注 (~~~~) 计数异常：{n_kw}/8（源漂移，人工复核）'
body_text = body_text.replace('(~~~~)', r'(\kongwei)')
# c) CJK 邻空格清除：邻 CJK 汉字/全角标点/引号 的半角空格——控制字词尾空格保护（\quad 素养小结 类
#    为控制字名终止符，TeX 解析不产空格，保留形制）；断言⑨ 清后 0
_CJK = '\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u2018\u2019\u201c\u201d'
_n_sp = [0]
def _cvt_sp(m):
    s = m.group(0)
    if s.startswith('\\'):   # 控制字＋其后空格：整体保留（空格系控制字名终止符）
        return s
    _n_sp[0] += 1
    return ''
body_text = re.sub(r'\\[a-zA-Z]+ +| +(?=[' + _CJK + r'])|(?<=[' + _CJK + r']) +', _cvt_sp, body_text)
_sp_resid = [m.group(0) for m in re.finditer(r'\\[a-zA-Z]+ +| +(?=[' + _CJK + r'])|(?<=[' + _CJK + r']) +', body_text)
             if not m.group(0).startswith('\\')]
assert not _sp_resid, f'CJK 邻空格清除残留：{_sp_resid[:5]}'
# d) 标签转换：【分析】【详解】【点睛】→[分析][详解][点睛]（[ ] 半角标签；【】仅留三件套＝\biaoqian）
n_fx, n_xj2, n_dj2 = (body_text.count('【分析】'), body_text.count('【详解】'), body_text.count('【点睛】'))
assert (n_fx, n_xj2, n_dj2) == (9, 9, 2), f'【】标签计数异常：分析{n_fx}/详解{n_xj2}/点睛{n_dj2}（应 9/9/2）'
body_text = (body_text.replace('【分析】', '[分析]').replace('【详解】', '[详解]').replace('【点睛】', '[点睛]'))
log(f'6a. v4.4④ 转换 pass：全角（）→半角 ×{n_paren}（断言② 零残留）；(~~~~)→(\\kongwei) ×{n_kw}；'
    f'CJK 邻空格清除 ×{_n_sp[0]}（控制字词尾空格保护，清后 0 断言）；'
    f'【分析】【详解】【点睛】→[ ] ×{n_fx + n_xj2 + n_dj2}（9/9/2）；'
    'chapterhead head 行括号同域转换见 7 步')

# ---- 6a-F. F 0909 终审 pass 组（定界符／全角数学符／√× 仿宋路由／公式接合／断行绑定；逐 pass 精确计数断言）----
# R1：pandoc \left…\right 定界符→普通字符（全品同位均普通括号/竖线；自动伸缩非全品形态）。
# 豁免留痕：探七两处 cases（\left\{ 双行 array）→固定 \Bigg\{ …\Bigg.（\right.\ 控制空格一并收回）
n_lp = body_text.count(r'\left(')
n_rp = body_text.count(r'\right)')
n_lv = body_text.count(r'\left|')
n_rv = body_text.count(r'\right|')
n_la = body_text.count(r'\left\langle')
n_ra = body_text.count(r'\right\rangle')
n_lc = body_text.count(r'\left\{')
n_rcs = body_text.count(r'\right.\ ')
assert (n_lp, n_rp, n_lv, n_rv, n_la, n_ra, n_lc, n_rcs) == (19, 19, 39, 39, 14, 14, 2, 2), \
    f'R1 定界符计数异常：({n_lp},{n_rp},{n_lv},{n_rv},{n_la},{n_ra},{n_lc},{n_rcs})≠(19,19,39,39,14,14,2,2)（源漂移，人工复核）'
body_text = (body_text
             .replace(r'\left\langle', r'\langle').replace(r'\right\rangle', r'\rangle')
             .replace(r'\left\{', r'\Bigg\{').replace(r'\right.\ ', r'\Bigg.')
             .replace(r'\left(', '(').replace(r'\right)', ')')
             .replace(r'\left|', '|').replace(r'\right|', '|'))
assert r'\left' not in body_text and r'\right' not in body_text, 'R1 清后残留 \\left/\\right'
# R4①：~~ 连排 nbsp 残留清除（探九详解 ~~过点，pandoc 件源）
n_tilde = body_text.count('~~')
assert n_tilde == 1, f'R4① ~~ 计数异常：{n_tilde}/1'
body_text = body_text.replace('~~', '')
# R4③：跨段断式接合（探二详解 …CC₁ =\⏎\(b−a−c…)——删 \)⏎\( 对使公式连续；同行 \) \( 形 0 处（普查留痕）
n_join = body_text.count('\\)\n\\(')
assert n_join == 1, f'R4③ 接合位计数异常：{n_join}/1'
body_text = body_text.replace('\\)\n\\(', '')
# F 片C 0909 #29：数学组接缝 \\)\( 加 \allowbreak（不添空、不改式面）——\relpenalty=10000 下
#   纯公式段（探九详解 46.368mm minipage）唯一可用断点；不给则 line 333 出 24.4pt overfull。
#   关系号紧邻的接缝（前字 =／<／>／≤／≥／≠／∥／⊥）不加——否则等于在关系号后开断点，
#   反而造「c=」悬行尾（p2 投影向量式首轮实证）。3 处加、1 处跳过（= 紧邻）。
n_join2 = len(re.findall(r'(?<![=<>≤≥≠∥⊥])\\\)\\\(', body_text))
assert n_join2 == 3, f'数学组接缝计数异常：{n_join2}/3（源漂移，人工复核）'
body_text = re.sub(r'(?<![=<>≤≥≠∥⊥])\\\)\\\(', r'\\)\\allowbreak\\(', body_text)
# R5：全角数学符→半角（＝×4／＋×2／－×1，探三题干与探七变式 λ＝；断言清后 0）
n_dj3, n_pl3, n_mn3 = body_text.count('＝'), body_text.count('＋'), body_text.count('－')
assert (n_dj3, n_pl3, n_mn3) == (4, 2, 1), f'R5 全角数学符计数异常：＝{n_dj3}/4 ＋{n_pl3}/2 －{n_mn3}/1'
body_text = body_text.replace('＝', '=').replace('＋', '+').replace('－', '-')
assert ('＝' not in body_text) and ('＋' not in body_text) and ('－' not in body_text)
# P-D：判断题 √ 路由仿宋（FZFSK cmap 含 U+221A，fontTools 实证）——\zhenhead 说明行、
# 判断答案位、条目/小结同位文字统一转宏 \gou{}。×（U+00D7）同转 \cha{}，但 F 片C 0909 #34 后
# \cha 已是 TikZ 自绘（方正全系 × 仅 ~0.48em 小×，换族无效；qp-fonts.tex \AtBeginDocument），
# 不再走仿宋字形——计数与转宏照旧（字形由宏侧接管）。
n_gou, n_cha = body_text.count('√'), body_text.count('×')
assert (n_gou, n_cha) == (7, 11), f'P-D √× 计数异常：√{n_gou}/7 ×{n_cha}/11'
body_text = body_text.replace('√', r'\gou{}').replace('×', r'\cha{}')
# R2 绑定（防孤字断行）：①则＋行内公式 21 处禁断（则不落行尾）；②「是(\kongwei)」3 处禁断；
# ③探三题干 \emph{x}/\emph{y} 与 =空槽 绑定（y 孤字缺陷位）；④探八题干裸 ()→(\kongwei)（空位补齐）
n_ze = body_text.count('则\\(')
assert n_ze == 23, f'R2 则\\( 计数异常：{n_ze}/23（21 行，两行各 2 处）'
body_text = body_text.replace('则\\(', '则\\nobreak\\(')
n_shi = body_text.count('是(\\kongwei)')
assert n_shi == 3, f'R2 是(\\kongwei) 计数异常：{n_shi}/3'
body_text = body_text.replace('是(\\kongwei)', '是\\nobreak(\\kongwei)')
n_ex = body_text.count(r'\emph{x}=\kongbai{}')
n_wy = body_text.count(r'\emph{y}=\kongbai{}')
assert (n_ex, n_wy) == (1, 1), f'R2 emph 绑定位计数异常：x{n_ex}/1 y{n_wy}/1'
body_text = body_text.replace(r'\emph{x}=\kongbai{}', r'\emph{x}\nobreak=\kongbai{}')
body_text = body_text.replace(r'\emph{y}=\kongbai{}', r'\emph{y}\nobreak=\kongbai{}')
n_kw8 = body_text.count('()')
assert n_kw8 == 0, f'R2 裸() 计数异常：{n_kw8}/0（探八例1 裸() 已由 side_row 空位右挂消费，余量应 0）'
assert ('()' not in body_text) and ('(~~~~)' not in body_text), '空位杂形残留'
# R2⑤（F 收尾轮 V7d）：并排题干空位末行右挂（side_row 发射，探八例1 孤括号行消解；全品 p07 题1-3 右挂纪律）
n_hang = body_text.count('\\nobreak\\hfill(\\kongwei)')
assert n_hang == 1, f'R2⑤ 并排题干空位右挂计数异常：{n_hang}/1'
log(f'6a-F. F 终审 pass：R1 定界符 \\left(/\\right)/\\left|/\\right|→普通 {n_lp}/{n_rp}/{n_lv}/{n_rv}、'
    f'\\left\\langle/\\right\\rangle→\\langle/\\rangle {n_la}/{n_ra}（清后 0 断言）；cases 豁免 \\left\\{{→\\Bigg\\{{ ×{n_lc}＋'
    f'\\right.\\ →\\Bigg. ×{n_rcs}（探七两处，堆叠定径留痕）；R4① ~~×{n_tilde}；R4③ 跨段断式接合 ×{n_join}（探二详解）；'
    f'R5 全角数学符 ＝{n_dj3}／＋{n_pl3}／－{n_mn3}（清后 0）；P-D √→\\gou{{}} ×{n_gou}（仿宋 FZFSK 路由）、×→\\cha{{}} ×{n_cha}（F 片C 0909 #34 后 TikZ 自绘）；'
    f'R2 绑定 则\\nobreak\\( ×{n_ze}（21 行 23 处）、是\\nobreak(\\kongwei) ×{n_shi}、emph x/y\\nobreak= ×2、探八裸() 由 side_row 右挂消费 ×{n_kw8}、'
    f'并排题干空位右挂 \\nobreak\\hfill(\\kongwei) ×{n_hang}（探八例1，孤括号行消解）；'
    'kongwei 总数 8→9（§8 断言同步）')

# ---- 6b. 分号守恒对账（拍板21；片段级，剥 \allowbreak 注入与空白差） ----
# v4.4④：_norm 随转换 pass 同步规范化——全角（）→半角、(~~~~)→(\kongwei)、【分析】【详解】【点睛】→[ ]，
# 两侧（源片段/body）同一映射，转换不产生伪「未排印」
def _norm(s):
    s = re.sub(r'\s+', '', s).replace(r'\allowbreak', '')
    s = s.replace('（', '(').replace('）', ')')
    s = s.replace('(~~~~)', r'(\kongwei)')
    s = (s.replace('【分析】', '[分析]').replace('【详解】', '[详解]').replace('【点睛】', '[点睛]'))
    # F 0909：6a-F pass 后 body 侧与源片段侧同映射归一（转换不生伪「未排印」）；\s+ 已剥空格，
    # 故 cases 闭端用无空格形态 \right.\) 匹配源侧
    s = (s.replace(r'\left\langle', r'\langle').replace(r'\right\rangle', r'\rangle')
          .replace(r'\left\{', r'\Bigg\{').replace(r'\right.\)', r'\Bigg.)')
          .replace(r'\left(', '(').replace(r'\right)', ')')
          .replace(r'\left|', '|').replace(r'\right|', '|')
          .replace('＝', '=').replace('＋', '+').replace('－', '-')
          .replace('√', r'\gou{}').replace('×', r'\cha{}')
          .replace('~~', '').replace('()', r'(\kongwei)')
          .replace(r'\)\(', '')
          # F 0909 收尾轮：side_row 空位右挂件（\nobreak\mbox{}\nobreak\hfill(\kongwei)\hspace{0.56mm}）
          # 与源侧裸 ()（→(\kongwei)）同映射归一
          .replace(r'\nobreak\mbox{}\nobreak\hfill', '').replace(r'\hspace{0.56mm}', '')
          .replace(r'\nobreak', ''))
    return s
body_n = _norm(body_text)
fh_tongshi = fh_unprint = fh_verbatim = 0
fh_miss = []
for b in blocks:
    n = b.count('；')
    if n == 0:
        continue
    if b.startswith('【编注】') and '题型通式' in b:
        fh_tongshi += n          # 授权转换：通式编注→素养小结三句式（v3 登记沿用）
        continue
    frag = _norm(b[len('【编注】'):]) if b.startswith('【编注】') else _norm(b)
    if frag.startswith('A．') and '；' in frag:
        pieces = [_norm(p) for p in re.split(r'；(?=[A-D]．)', b) if _norm(p)]
        if all(p in body_n for p in pieces):
            fh_verbatim += n
        else:
            fh_miss.append((n, b[:40]))
        continue
    if frag in body_n:
        fh_verbatim += n
    else:
        fh_miss.append((n, b[:40]))
fh_unprint = sum(n for n, _ in fh_miss)   # 未排印块（讲部表×2＋条目7（2）选编，登记）
n_comp_fh = sum(s.count('；') for s in COMPOSED)
n_body_fh = body_text.count('；')
log(f'6b. 分号守恒对账（拍板21，片段级）：源节 {n_sec_fh} ＝ 逐字在场 {fh_verbatim}（选项网格拆分回填含内）'
    f'＋通式编注→三句式授权转换 {fh_tongshi}（v3 登记沿用）＋未排印块 {fh_unprint}（讲部表×2＋条目7（2）选编，其内容由条目7 自编性质句覆盖）；'
    f'成件 body 共 {n_body_fh} ＝ 源逐字 {fh_verbatim}＋命制/演示自编 {n_body_fh - fh_verbatim}（对账 COMPOSED 计 {n_comp_fh}，余为条目/学习目标自编句）')
assert fh_unprint <= 3, f'分号对账异常：{fh_miss}'
ctrl = re.findall(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', body_text)
assert not ctrl, f'控制字符污染：{ctrl[:5]}'
log('6c. 控制字符扫描兜底（v3 交付报告§七-4）：0 处')
# F 0909：vbox 尾胶注释占位回填（E 手改③）——注释若经 6 步转换 pass（CJK 邻空格剥除／全角（）→半角）
# 会被改字面，故发射点只放 @@VBOXGLUE@@ 占位，此处（全 pass 后）回填 E 原注释精确字节
VBOXGLUE = (r' 字替对照 C：课堂评价 vbox 在 10.09/18.25 密度下自然高超出栏高 9.58pt，'
            r'于盒尾胶内收缩（不动任何字号/行距/表距）')
n_vbg = body_text.count('@@VBOXGLUE@@')
body_text = body_text.replace('@@VBOXGLUE@@', VBOXGLUE)
assert n_vbg == 1, f'vbox 尾胶占位异常：{n_vbg}'
log(f'6d. 课堂评价 vbox 尾胶上移（E 手改③）：\\vspace{{-9.7pt}}＋C 轮标定注释占位回填 {n_vbg}/1（R9 复核不压页脚）')
open(BASE + r'\body.tex', 'w', encoding='utf-8').write(body_text + '\n')
head = [
    r'\zhangtitle{第一章\quad 空间向量与立体几何}',
    r'\jietitle{1.1 空间向量及其运算}',
    r'\xiaojietitle{1.1.1 空间向量及其运算}',
    r'\keshi{第1课时\quad 空间向量的概念及线性运算}',
    r'\mubiaoline',
    r'\mubiaomu{1}{理解空间向量及其相关概念（模、零向量、单位向量、相等与相反、共线与共面），会用有向线段表示空间向量；}',
    r'\mubiaomu{2}{掌握线性运算（加减、数乘）的法则与运算律，理解共线、共面的充要条件；}',
    r'\mubiaomu{3}{掌握数量积的概念与运算律，会求夹角、投影向量，并能用数量积求距离．}',
]
COMPOSED.extend(h[1:].rstrip('；') for h in head[4:])
# v4.4④：head 行全角（）→半角（mubiaomu 括注同域转换；CJK 邻空格规则对 \quad 保护同 6a）
n_paren_hd = sum(h.count('（') + h.count('）') for h in head)
head = [h.replace('（', '(').replace('）', ')') for h in head]
open(BASE + r'\chapterhead.tex', 'w', encoding='utf-8').write('\n'.join(head) + '\n')
log('7. 章首通栏：章20.67（v4.4 字号梯子，全品 22pt 墨高折算；v4.1 指令7 全品式左对齐＝两枚 6.9mm 等大对角相触方块＋右下 2.3mm 小块（v4.3 总账B 复刻放大），'
    '章名黑体左排，「第1章」改「第一章」；节/小节/课时维持居中）/节16.88（行高22，\\heiti 常规——v4.3 节标题撤仿粗，附则§三）'
    '/小节15.1/课时13（\\heijie 3.3×；级间距 6.9/5.5/5.9/5.8mm 全品档放开，拍板7）；'
    'v4.2-5：课时名内容式对齐全品 p04 实证＝「第1课时　空间向量的概念及线性运算」（原「空间向量及其运算」撤）；'
    'v4.3：四级标题字体＝方正黑体分档 FakeBold 字重阶梯（章4.0/小节·课时3.3，字库见 qp-fonts）；'
    '【学习目标】3 条楷体＋顶格例外（拍板6：序号半角加粗＋首行缩进2字＋悬挂8.3mm＋行距17pt）；'
    f'v4.4④：head 行全角（）→半角 ×{n_paren_hd}（转换 pass 同域）；'
    '讲练件的统计行与 T0 导航表不排入导学件（件型差异，登记）')

# ---- 8. 逻辑断言自检（复测波脚本手工版的数据面） ----
n_tj = body_text.count(r'\tjdnr{')
n_li1 = body_text.count(r'{例\textbf{1}}') + body_text.count(r'{例\textbf{1}\duoxuan}')
n_bs = body_text.count(r'{变式\textbf{1}}')
n_ans = body_text.count(r'\ansline{') + body_text.count(r'\jiance{')
n_star = body_text.count('典型性理由：')
n_kd = body_text.count(r'\kongda{')
n_kb_stem = body_text.count(r'\kongbai{}')
n_zt = body_text.count(r'\zhenti{')
n_jx = body_text.count(r'\jiexi{')
n_mini = body_text.count(r'\begin{minipage}')
n_hao_bold = len(re.findall(r'\{\\fontsize\{11\.4pt\}\{14pt\}\\selectfont\\heihao \{\\numboldjian \d\}．\}', body_text))
n_hao_old = len(re.findall(r'\\heihao \\textbf\{\d\}．', body_text))   # F 前 emission 残留应为 0
n_side = len(re.findall(r'\\begin\{minipage\}\[t\]\{[\d.]+mm\}\\raggedright', body_text))  # F 片A：文字栏宽逐图标定（mm）
n_duox = body_text.count(r'\duoxuan')
n_kw2 = body_text.count(r'\kongwei')
n_tie = body_text.count(r'\tieside{')
n_lib = body_text.count(r'\liB{变式')
n_li_old = body_text.count(r'\li{变式')   # F 前变式标签 emission 残留应为 0
# F 片C 0909 #27：悬空引用禁则升级——旧模式 衔接\d 对「衔接条目5」漏检（数字前有「条目」二字），
# 且不覆盖「条目9」「支撑条目16、17、34」等旧连号引用；本片 5 处编注已改指名式（sec.tex），
# 禁则改为「条目＋阿拉伯数字」0 命中（与 _测v4断言.py N11 同式）。
xuankong = [w for w in ('见例', '如下例') if w in body_text] + \
    ([m.group(0) for m in re.finditer(r'条目\s*\d', body_text)] if re.search(r'条目\s*\d', body_text) else [])
cg_hits = [w for w in ('基本定理', '空间直角') if w in body_text]
cg_zuobiao = [m.group(0) for m in re.finditer(r'.{6}坐标.{6}', body_text)
              if '不建坐标系' not in m.group(0) and '非坐标' not in m.group(0)]   # 否定式表述非坐标法使用
# v4.3 条4机制补漏（拍板3）：\tiaomu 内「文字+（N）」连排命中即报＋（2）起未各自成段扫描——
# 首子项（1）连排条目头＝全品式合法形态（全品 p05 实证）；（2）起并列子项必须各自成段（顶格）。
# 命中仅报告供人工复核，不阻断（合法形态在同一扫描域内无法机判，逐条登记）。
lianpai_hits = [m.group(0)[:30] for m in re.finditer(r'\\tiaomu\{\d\}\{[^\n]*?[^\s{（]（\d）', body_text)]
sub2_inline = [m.group(0)[:30] for m in re.finditer(r'[^\s{（]（[2-9]）', body_text)]
log(f'8. 逻辑断言自检（数据面）：◆探究点 {n_tj}/9；例1 {n_li1}/9（数字 \\textbf 加重，探五带 \\duoxuan）；变式1 {n_bs}/9；【答案】行 {n_ans}/14；'
    f'★典型性理由 {n_star}/0（v4.2-E18 撤★）；【解析】简析 \\jiexi {n_jx}/14（变式9＋检测5，D 类16/17）；'
    f'图文并排 minipage {n_mini}（{n_side} 组并排，左 0.56\\linewidth 文字／右按墨宽盒，F 片A side×5＝探二三六八九）；'
    f'多选标记 \\duoxuan {n_duox}/1（探五例1，题5 答案 AD）；空位 (\\kongwei) {n_kw2}/9（v4.4④ 转换 pass 8＋F 探八裸括号补 1）；'
    f'题侧 \\tieside {n_tie}/5（检测题侧直排；例1 题侧在 \\tjdnr 第 4 参由宏排印）；'
    f'变式标签 \\liB {{n_lib}}/9（F 片D 0909c：\\liB 拆双字重——变 FY-w700／式N FY-w450；旧形 \\li 残留 {n_li_old}/0）；'
    f'挖空印答 \\kongda {n_kd}/20（课前预习知识点区全部空，答案逐个核对条目语义）；'
    f'题干留白 \\kongbai {n_kb_stem}（例题/变式/课堂检测，答案由【答案】/【详解】紧跟）；'
    f'判断题 \\zhenti {n_zt}/6（第 4 参【解析】由宏排印，字面在 qp-blocks）；'
    f'检测题号 {{\\fontsize{{11.4pt}}{{14pt}}\\selectfont\\heihao {{\\numboldjian{{N}}．}} {n_hao_bold}/5（G20＋F 0909 升重：数字 \\numboldjian NSC-w700、「．」随 heihao BoldFont w700，E 手改上移）；旧形 \\textbf 残留 {n_hao_old}/0；'
    f'条目内「文字+(N)」连排命中 {lianpai_hits or "无"}（拍板3 机制断言：首子项连排合法，命中即报人工复核）；'
    f'（2）起未各自成段嫌疑 {sub2_inline or "无"}（应全为 \\bindp 段首，命中即报）；'
    f'悬空引用 {xuankong or "无"}；'
    f'超纲禁词（基本定理/空间直角）{cg_hits or "无"}；'
    f'「坐标」非否定式命中 {cg_zuobiao or "无"}（命制/演示文字超纲复查＝0）')
assert n_kd == 20 and n_zt == 6, f'v4.1 印答/解析计数异常：kongda={n_kd} zhenti={n_zt}'
assert n_star == 0 and n_jx == 14 and n_side == 5 and n_hao_bold == 5 and n_hao_old == 0 \
        and n_lib == 9 and n_li_old == 0 and n_duox == 1 and n_kw2 == 9, \
    f'v4.2-v4.4 计数异常：star={n_star} jiexi={n_jx} side={n_side}（⑩ side×5）haobold={n_hao_bold}(旧形{n_hao_old}) ' \
    f'liB={n_lib}(旧形{n_li_old}) duoxuan={n_duox} kongwei={n_kw2}/9（F 探八补 1）'
log('8a. R8 题源答案普查（sec.tex 十题，F 0909 补登记）：B/式/C/1¼/AD/60°/区间/−3/2/D/A——'
    '唯题5＝AD 多答（\\duoxuan 已挂，n_duox=1 断言维持）；普查结论＝源题答案全部在场，与【答案】行/【详解】逐一相符')
log('8b. 命制对账：本轮新命制 14（变式 8＋检测 4＋诊断 2）≤上限 15，逐题亲算（见 5g/5h 各条）；'
    '沿用 v3 已亲算 5（检测1＋诊断块①2 道＋块②③第 1 道），逐条登记；'
    '变式六策覆盖：逆向化/概念辨析化/换载体/换设问/换数值/换条件')
log('8c. F 片A 图定性处置台账（全件 6 图）：sub3_B_4＝条目3 投影三联图 60mm 居中（图区组，条5；'
    '居中前距 1.9mm/尾距 -1.0mm（0908 标定回填），v4.4⑫ 下距窗 0.4–2.6）；'
    'image1（探究点二例1）＝【详解】区并排（F 片A 归位：挂「连接CA₁」详解首块旁，源实证图在【详解】段后独立段）；'
    'image5（探究点九例1）＝【详解】区并排（F 片A 归位：挂「过点B，D分别向AC作垂线」详解首块旁，源实证图与【详解】同段）；'
    'image2（探究点三例1 题干图）／image3（探究点六例1 题干图）／image4（探究点八例1 题干图）＝题干并排（留题干）；'
    '五组同几何档（3c，全品截图实证）：文字左 0.56\\linewidth\\raggedright／图右盒宽按墨宽折算（image1 剪垫后冻结 27.2mm 不放大），'
    '图墨右缘距栏右 2.6±1mm／图文墨缝 6.7±1.5mm／图墨顶比首行墨顶高 0.25mm（窗 ±1）；'
    'raisebox 声明盒 [height=H][depth=\\height−H] 逐图反解（盒深参与行距，R3 零重叠修复保留）')
log('9. F 片B 0909（竖向间距与表格净空四意见；仅登记，改动明细见 5c/5e/4b/TABTOP 注释）：'
    '#28 条目2 (1)→(2)：拆段首段 \\tiaomuz 零尾距（8.21→6.41mm/墨 4.53→2.75）；'
    '#36 条目→条目缝：\\tiaomu 尾距 1.8→0.35mm＋拆段条目尾距移末段（\\tiaomutail）——全对 pitch 6.76mm、'
    '墨隙 3.05–3.39（目标 3.06±0.2；两端点系字形墨深）；TABTOP 1.1→2.55mm 回填表顶前距；'
    '#31 相邻判断题缝：\\zhenti 尾 7pt→0（8.88→6.41mm/墨 5.38→2.62–3.05）＋\\huaxing 宏胶 0.9→3.37mm'
    '回填考点探究前距（\\jiexi 7pt 语境不同维持）；'
    '#30 表格多行格净空：extrarowheight 0.4→1.7mm＋\\tabrowglue 按折数分档（1/2/≥3 折 0.85/4.65/7.60mm，'
    '\\rowreset/\\marklines 用 \\prevgraf 自测折数）——多行格每侧 顶 3.1–3.5/底 3.0–4.0（基线 0.9–2.2），'
    '表头行高 9.18（全品 9.03）、格内行距 13.9pt 不动；表高增致表3 移 p3 左栏首（登记）；'
    '文书修正（#38）：4b 段 extrarowheight 旧值描述（0.6mm，实际早已 0.4）一并改正')
open(BASE + r'\postproc_daoxue_log.txt', 'w', encoding='utf-8').write('\n'.join(LOG))
print('\n'.join(LOG))
