# -*- coding: utf-8 -*-
r"""⑤_03_样章包.py — 样章 PDF 包（20 代表页＋灰阶梯度条页＋打印叮嘱页）。
页源＝成书交付\全件PDF\（同步盘终态工作区复制件导出）＋扉页.pdf＋阶段④灰阶梯度条页.pdf。
动态页定位：文本检索（焦点弦/重构表/清灰区）＋T7 栏顶几何扫描。逐页 PNG 供目检。
"""
import sys, io, os, re, json, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf
from pypdf import PdfReader, PdfWriter

DELIV = r"C:\提示词\工作区\选必1成书修复-0905\成书交付"
PDFDIR = os.path.join(DELIV, "全件PDF")
HUIJIE = r"C:\提示词\工作区\选必1成书修复-0905\阶段④\灰阶梯度条页.pdf"
DINGZHU = os.path.join(DELIV, "样章", "打印叮嘱页.pdf")
FEIYE = os.path.join(DELIV, "扉页", "扉页.pdf")
OUT_PDF = os.path.join(DELIV, "样章", "人教B版选必1·样章包.pdf")
PNG_DIR = os.path.join(DELIV, "样章", "目检PNG")
LOG = os.path.join(DELIV, "_工作", "⑤_03_样章选页.json")

B = lambda name: os.path.join(PDFDIR, name)


WJ = r"(?:\u2060)?"  # 标签行内 word-joiner（T 系工具插符），检索须容错
MARK = (r"【" + WJ + r"(?:分" + WJ + r"析|详" + WJ + r"解|点" + WJ + r"睛|编" + WJ + r"注)" + WJ + r"】")


def page_of_text(pdf, pattern, start=0, need_image=False):
    """返回首个命中正则的 1-based 页码；need_image 时要求该页含栅格图；未命中 None。"""
    d = pymupdf.open(pdf)
    try:
        rx = re.compile(pattern)
        fallback = None
        for i in range(start, len(d)):
            if rx.search(d[i].get_text()):
                if not need_image or d[i].get_image_info():
                    return i + 1
                fallback = fallback or i + 1
        return fallback
    finally:
        d.close()


def t7_column_top_page(pdf, lo=0):
    """T7 栏顶节首页：某栏首块为节号标题（\\d.\\d 开头）且块顶=该栏最高块顶（≤8pt）。"""
    d = pymupdf.open(pdf)
    try:
        for i in range(lo, len(d)):
            pg = d[i]
            blocks = [b for b in pg.get_text("blocks") if b[6] == 0 and b[4].strip()]
            if not blocks:
                continue
            mid = pg.rect.width / 2
            for col in (lambda b: b[0] < mid, lambda b: b[0] >= mid):
                cb = sorted([b for b in blocks if col(b)], key=lambda b: b[1])
                if not cb:
                    continue
                top = cb[0][1]
                for b in cb:
                    if b[1] - top > 8:
                        break
                    txt = b[4].strip().replace("\n", "")
                    m = re.match(r"^(\d\.\d{1,2})(?!\.\d)\s*\S", txt)
                    if m and len(txt) <= 40:
                        return i + 1, m.group(1), round(b[1] - top, 1)
        return None, None, None
    finally:
        d.close()


def main():
    os.makedirs(PNG_DIR, exist_ok=True)
    pages = []   # (pdf路径, 1based页, 标签)
    log = {"fixed": [], "dynamic": {}, "errors": []}

    def add(pdf, pg, label):
        pages.append((pdf, pg, label))

    # —— 固定页 ——
    add(B("人教B版选必1·封面.pdf"), 1, "封面")
    add(FEIYE, 1, "扉页（CB-13 新配页件）")
    add(B("人教B版选必1·册目录页.pdf"), 1, "册目录页（②-E 重造版）")
    add(B("人教B版选必1·使用说明.pdf"), 1, "使用说明")
    add(B("人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.pdf"), 1,
        "部分封面（第1章·衔接）")
    log["fixed"] = [(os.path.basename(p), q, l) for p, q, l in pages]

    # —— 动态定位 ——
    xj1 = B("人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.pdf")
    pg = page_of_text(xj1, MARK)
    (add(xj1, pg, f"衔接1 p{pg}·解析块清灰区（②C T6c）") if pg else log["errors"].append("衔接1清灰页未命中"))

    xj2 = B("人教B版选必1 第2章 平面解析几何·衔接件（13题）.pdf")
    add(xj2, 3, "衔接2 p3·②F 公式还原点")
    add(xj2, 5, "衔接2 p5·②F 公式还原点")

    q1 = B("人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.pdf")
    add(q1, 11, "清单1 p11·image17 区（③二期 去 rot 注记页）")
    add(q1, 12, "清单1 p12·image18 区")

    q2 = B("人教B版选必1 第2章 平面解析几何·知识清单（完成）.pdf")
    add(q2, 2, "清单2 p2·image3 修复点（③三期）")
    pg = page_of_text(q2, r"焦点弦", need_image=True)
    (add(q2, pg, f"清单2 p{pg}·焦点弦区（含图）") if pg else log["errors"].append("清单2焦点弦未命中"))
    pg = page_of_text(q2, r"图示")
    (add(q2, pg, f"清单2 p{pg}·T8 重构表页（D 转置：位置关系｜图示｜d与𝑅、𝑟关系）") if pg else log["errors"].append("清单2重构表未命中"))

    s61 = B("人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.pdf")
    add(s61, 2, "上61 p2·T8 重构表页（A 拆两表：线性运算＋运算律）")
    add(s61, 3, "上61 p3·讲练件题目页（题号块＋题干底纹＋答案芯片）")

    x79 = B("人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.pdf")
    add(x79, 37, "下79 p37·②F 公式还原点＋T6b 竖条页（题型标题「内切球模型」左竖条）")
    e89 = B("人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.pdf")
    add(e89, 19, "89 p19·②F 公式还原点（同页题型标题左竖条在位）")

    j92 = B("人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.pdf")
    pg, sec, dy = t7_column_top_page(j92, lo=1)
    if pg:
        add(j92, pg, f"92 p{pg}·T7 栏顶节首页（节{sec}，栏顶差{dy}pt）")
        log["dynamic"]["T7"] = {"page": pg, "sec": sec, "delta_pt": dy}
    else:
        log["errors"].append("92 栏顶节首页未命中")
    pg = page_of_text(j92, r"判定方法")
    (add(j92, pg, f"92 p{pg}·T8 重构表页（C 转置并合列）") if pg else log["errors"].append("92重构表未命中"))

    j68 = B("人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.pdf")
    pg = page_of_text(j68, r"2px")
    (add(j68, pg, f"68 p{pg}·T8 重构表页（F/G 抛物线区）") if pg else log["errors"].append("68重构表未命中"))

    # —— 校验 20 页 ——
    assert len(pages) == 20, f"代表页数={len(pages)} ≠ 20"
    assert not log["errors"], f"动态定位未全命中：{log['errors']}"

    # —— 逐页 PNG（目检）＋ 组包 ——
    writer = PdfWriter()
    idx = 0
    for pdf, pg, label in pages:
        src = PdfReader(str(pdf))
        writer.add_page(src.pages[pg - 1])
        writer.add_outline_item(f"{idx+1:02d} {label}", idx)
        d = pymupdf.open(str(pdf))
        pix = d[pg - 1].get_pixmap(dpi=150)
        pix.save(os.path.join(PNG_DIR, f"{idx+1:02d}_{re.sub(r'[\\\\/:*?「」（）·／ ]', '_', label)[:40]}.png"))
        d.close()
        idx += 1
    for pdf, label in ((HUIJIE, "灰阶梯度条页（阶段④产件·CB-10）"),
                       (DINGZHU, "打印叮嘱页（CB-10/11·转交店家）")):
        writer.append(pdf)
        writer.add_outline_item(f"{idx+1:02d} {label}", idx)
        idx += 1
    with open(OUT_PDF, "wb") as f:
        writer.write(f)

    n = len(PdfReader(OUT_PDF).pages)
    log["total_pages"] = n
    log["pages"] = [(os.path.basename(p), q, l) for p, q, l in pages]
    log["generated"] = datetime.datetime.now().isoformat(timespec="seconds")
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    print("样章包", OUT_PDF, "总页数", n, "（20 代表页＋2 校准/叮嘱页）")
    for i, (p, q, l) in enumerate(log["pages"], 1):
        print(f"  {i:02d} {os.path.basename(p)} p{q}  {l}")
    if log["errors"]:
        print("ERRORS:", log["errors"])


if __name__ == "__main__":
    main()
