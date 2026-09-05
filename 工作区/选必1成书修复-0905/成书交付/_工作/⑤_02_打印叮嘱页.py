# -*- coding: utf-8 -*-
r"""⑤_02_打印叮嘱页.py — 打印叮嘱一页（CB-10/11 口径＋装订单§四＋CB-1/3/4/6/12），PyMuPDF 直产 A4。"""
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

OUT = r"C:\提示词\工作区\选必1成书修复-0905\成书交付\样章\打印叮嘱页.pdf"
FONT = r"C:\Windows\Fonts\simsun.ttc"

TITLE = "打印叮嘱（随样章包交付·转交打印店）"
SECTIONS = [
    ("一、打印设置（CB-11）", [
        "1. 按 100% 原大打印，禁止「适应页面／缩放打印／适合纸张」等任何缩放。",
        "2. 双面打印选「长边翻转」。",
        "3. 每件从新纸起始：合册 PDF 已在各件之间自动补白页凑偶数页，店端无需也",
        "    不应再作调整；件尾背面空白页属正常分节，不是缺页。",
    ]),
    ("二、纸张与灰度（CB-3／CB-4／CB-10）", [
        "1. 纸张：建议 70g 高不透明度纸＋激光打印（浅底灰阶保真）；样章同批以",
        "    「70g 复印纸」与「70g 米黄道林纸」各打一份，供两纸实物比对定纸。",
        "2. 灰度：全册底纹最深 22% 灰封顶；样章含《灰阶梯度条》页（5%~25% 逐格、",
        "    逐格标注色值），请以实物核定最浅可还原灰度与 22% 上限实测表现并回填。",
    ]),
    ("三、装订（装订单§四／CB-7）", [
        "1. 页码为各部分独立页码、多套页码原样并存拼接，非全册连续页码，属正常。",
        "2. 装订组合：方案A 整册装订（按装订单取件序）或 方案B 按件型抽订（全部",
        "    衔接／全部清单／全部讲练各订一套），详见《人教B版选必1·装订单》。",
        "3. 各件页脚含「（共N页）·本n/共6本」同串，可作分本归属核对。",
    ]),
    ("四、下单注意（CB-1／CB-6／CB-12）", [
        "1. 定位＝网上打印店数码快印成书（教辅内部资料），封面不置书号／定价／条码。",
        "2. 封面＋封底＋书脊为连体展开稿单印（幅面 446×303mm 含 3mm 出血；默认书脊",
        "    20mm 为预估值，正式下印前须以店家实测纸厚回填重出展开稿）。",
        "3. PDF 内书签仅作翻阅与核页用，不需打印输出。",
        "4. 流程：先以样章包打样核定（灰阶＋两纸），通过后再放整册／分本量产。",
    ]),
]
FOOT = "人教B版选必1·成书交付⑤轮（样章PDF包）　2026-09-06"


def put(page, x, y, text, size, color=(0, 0, 0)):
    page.insert_text((x, y), text, fontname="F0", fontfile=FONT, fontsize=size, color=color)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = pymupdf.open()
    page = doc.new_page(width=595.28, height=841.89)  # A4
    y = 72.0
    put(page, 60, y, TITLE, 16)
    y += 14
    page.draw_line(pymupdf.Point(60, y), pymupdf.Point(535, y), width=1.2)
    y += 26
    for head, items in SECTIONS:
        put(page, 60, y, head, 12.5)
        y += 21
        for it in items:
            put(page, 72, y, it, 10.5)
            y += 17
        y += 9
    put(page, 60, 790, FOOT, 9, color=(0.35, 0.35, 0.35))
    doc.save(OUT)
    print("产出", OUT, "页数", len(doc))


if __name__ == "__main__":
    main()
