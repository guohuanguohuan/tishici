# -*- coding: utf-8 -*-
"""印前自检.py——付印前六项体检（2026-09-11 拍板，看板五十六号）。

用法：
    python 工具/印前自检.py <pdf1> [<pdf2> …] [--本 名称:起-止 …] [--报告目录 DIR]

六项检查（逐项落数字，按级别挂档）：
  ① 字体全嵌入    P0  逐页 get_fonts(full=True)；本版 PyMuPDF 无显式 emb 位，
                      以 ext 代之：ext=='n/a'/'' 即未嵌入（已抽 font 文件验证，
                      ext='ttf'/'cid'/… 均为真嵌入）。未嵌入列「字体名×页」。
  ② 图片有效 dpi  P1  逐图 get_image_info(xrefs=True)；有效dpi＝像素宽÷显示宽(英寸)，
                      按拍板口径以宽向dpi挂档（高向dpi另列参考）。<150dpi挂P1，
                      <96dpi挂P0；宽高均<200px 的图标类小图豁免挂档，单列豁免登记。
  ③ 页数          P2  总页数奇偶（奇数仅提示，胶装不强制）；--本 名称:起-止
                      （可多次）按「本」报分段页数，未传只报总数。
  ④ 尺寸一致性    P1  逐页 w×h（pt，0.1pt 精度归组）；同尺寸PASS，异尺寸逐页列出。
  ⑤ 出血/贴边扫描 P2  逐页取文字块∪矢量绘图∪图片的墨迹联合外接框，量四边最小距离；
                      <3mm 的页列「疑似出血页」清单，仅供人工目检，脚本不判生死。
  ⑥ 空白页        P1  600dpi 灰度整页渲染，非白(<245)像素<16 视为空白；
                      末页空白、连续≥2页空白特别标注。

退出码：有 P0＝1；仅 P1＝2；全过＝0。参数错/文件打不开等硬错误＝9。
只读：仅 open 检查，不保存不改写 PDF，可重复跑。--报告目录 写入
「印前自检-<父目录>-<文件名>.md/.json」两份报告（同名自动加后缀）。
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pymupdf

DPI_P1 = 150      # 有效dpi低于此挂P1
DPI_P0 = 96       # 有效dpi低于此挂P0（高于P1优先）
ICON_PX = 200     # 宽高均低于此＝图标类小图，豁免挂档
BLEED_MM = 3.0    # 墨迹距边低于此＝疑似出血页
BLANK_DPI = 600   # 空白判定渲染精度
BLANK_MAX_PX = 16 # 非白像素低于此＝空白页（「若干像素」取16）
NONWHITE_LT = 245 # 灰度值低于此计为非白

MM = 25.4 / 72.0  # pt→mm


def 级别排序(级别: str) -> int:
    return {"P0": 0, "P1": 1, "P2": 2}.get(级别, 3)


class 文件检查结果:
    def __init__(self, 路径: Path):
        self.路径 = 路径
        self.发现: list[dict] = []   # {项, 级别, 结论, 摘要}
        self.数据: dict = {}          # 六项原始读数（供 JSON）

    def 记(self, 项: str, 级别: str, 结论: str, 摘要: str):
        self.发现.append({"项": 项, "级别": 级别, "结论": 结论, "摘要": 摘要})

    @property
    def 最高级别(self) -> str | None:
        有 = [f["级别"] for f in self.发现 if f["级别"] in ("P0", "P1", "P2")]
        return min(有, key=级别排序) if 有 else None


def 检查一_字体(doc: pymupdf.Document, r: 文件检查结果):
    未嵌入: dict[str, set[int]] = {}
    底册: dict[str, set[int]] = {}
    for 页号, 页 in enumerate(doc, 1):
        for xref, ext, 类型, 字体名, _别名, _编码, _引用 in 页.get_fonts(full=True):
            页集 = 底册.setdefault(字体名, set())
            页集.add(页号)
            if ext in ("n/a", ""):
                未嵌入.setdefault(字体名, set()).add(页号)
    总处数 = sum(len(p) for p in 底册.values())
    r.数据["字体"] = {
        "字体名×页": {k: sorted(v) for k, v in sorted(底册.items())},
        "未嵌入字体×页": {k: sorted(v) for k, v in sorted(未嵌入.items())},
    }
    if 未嵌入:
        明细 = "；".join(f"{k}×{sorted(v)}" for k, v in sorted(未嵌入.items()))
        r.记("①字体全嵌入", "P0", "FAIL", f"未嵌入 {len(未嵌入)} 种：{明细}")
    else:
        r.记("①字体全嵌入", "P0", "PASS", f"全部嵌入（{len(底册)}种字体/{总处数}处）")


def 检查二_图片dpi(doc: pymupdf.Document, r: 文件检查结果):
    逐图 = []
    for 页号, 页 in enumerate(doc, 1):
        for im in 页.get_image_info(xrefs=True):
            宽px, 高px = im["width"], im["height"]
            x0, y0, x1, y1 = im["bbox"]
            宽in, 高in = (x1 - x0) / 72.0, (y1 - y0) / 72.0
            dpi宽 = 宽px / 宽in if 宽in > 1e-6 else float("inf")
            dpi高 = 高px / 高in if 高in > 1e-6 else float("inf")
            豁免 = 宽px < ICON_PX and 高px < ICON_PX
            if 豁免:
                级, 档 = "豁免", "图标类小图豁免登记"
            elif dpi宽 < DPI_P0:
                级, 档 = "P0", f"{dpi宽:.1f}dpi<{DPI_P0}"
            elif dpi宽 < DPI_P1:
                级, 档 = "P1", f"{dpi宽:.1f}dpi<{DPI_P1}"
            else:
                级, 档 = "PASS", f"{dpi宽:.1f}dpi"
            逐图.append({"页": 页号, "xref": im["xref"], "像素": [宽px, 高px],
                         "显示pt": [round(x1 - x0, 1), round(y1 - y0, 1)],
                         "dpi宽": round(dpi宽, 1), "dpi高": round(dpi高, 1),
                         "级别": 级, "判定": 档})
    r.数据["图片dpi"] = {"逐图": 逐图, "dpi门限": [DPI_P1, DPI_P0]}
    正图 = [g for g in 逐图 if g["级别"] != "豁免"]
    最低5 = sorted(正图, key=lambda g: g["dpi宽"])[:5]
    r.数据["最低5图"] = 最低5
    r.数据["豁免登记"] = [g for g in 逐图 if g["级别"] == "豁免"]
    if not 逐图:
        r.记("②图片有效dpi", "—", "PASS", "全卷无位图")
        return
    最低值 = min((g["dpi宽"] for g in 正图), default=float("inf"))
    最低显 = f"{最低值:.1f}dpi" if 正图 else "—（正图0张，全部豁免）"
    摘 = (f"图{len(逐图)}张（正图{len(正图)} 豁免{len(逐图) - len(正图)}）"
          f" 最低{最低显}")
    if any(g["级别"] == "P0" for g in 逐图):
        r.记("②图片有效dpi", "P0", "FAIL", 摘 + "｜存在<96dpi图")
    elif any(g["级别"] == "P1" for g in 逐图):
        r.记("②图片有效dpi", "P1", "FAIL", 摘 + f"｜存在<{DPI_P1}dpi图")
    else:
        r.记("②图片有效dpi", "P1", "PASS", 摘)


def 检查三_页数(doc: pymupdf.Document, r: 文件检查结果, 分本: list[tuple[str, int, int]]):
    总页 = len(doc)
    r.数据["页数"] = {"总页": 总页, "奇偶": "奇" if 总页 % 2 else "偶"}
    for 名称, 起, 止 in 分本:
        r.数据["页数"].setdefault("按本", []).append(
            {"本": 名称, "起": 起, "止": 止, "页数": 止 - 起 + 1,
             "奇偶": "奇" if (止 - 起 + 1) % 2 else "偶"})
    if 总页 % 2:
        结论 = "提示"
    else:
        结论 = "PASS"
    摘 = f"{总页}页（{'奇数，胶装不强制' if 总页 % 2 else '偶'}）"
    for 本 in r.数据["页数"].get("按本", []):
        摘 += f"｜本「{本['本']}」{本['起']}-{本['止']}＝{本['页数']}页（{本['奇偶']}）"
    r.记("③页数", "P2" if 总页 % 2 else "—", 结论, 摘)


def 检查四_尺寸(doc: pymupdf.Document, r: 文件检查结果):
    逐页 = []
    for 页号, 页 in enumerate(doc, 1):
        逐页.append({"页": 页号,
                     "宽pt": round(页.rect.width, 1), "高pt": round(页.rect.height, 1),
                     "宽mm": round(页.rect.width * MM, 1), "高mm": round(页.rect.height * MM, 1)})
    组: dict[tuple[float, float], list[int]] = {}
    for g in 逐页:
        组.setdefault((g["宽pt"], g["高pt"]), []).append(g["页"])
    r.数据["尺寸"] = {"逐页": 逐页, "归组": {f"{w}x{h}pt": v for (w, h), v in 组.items()}}
    if len(组) == 1:
        (w, h), 页们 = next(iter(组.items()))
        r.记("④尺寸一致性", "P1", "PASS", f"{w}×{h}pt（{w*MM:.1f}×{h*MM:.1f}mm）×{len(页们)}页")
    else:
        明细 = "；".join(f"{w}×{h}pt→{v}" for (w, h), v in 组.items())
        r.记("④尺寸一致性", "P1", "FAIL", f"{len(组)}种尺寸：{明细}")


def 检查五_出血(doc: pymupdf.Document, r: 文件检查结果):
    逐页 = []
    疑似 = []
    for 页号, 页 in enumerate(doc, 1):
        框s = [b[:4] for b in 页.get_text("blocks")]
        框s += [d["rect"] for d in 页.get_drawings()]
        框s += [im["bbox"] for im in 页.get_image_info()]
        if not 框s:
            逐页.append({"页": 页号, "最小mm": None})
            continue
        墨 = pymupdf.Rect(框s[0])
        for b in 框s[1:]:
            墨 |= pymupdf.Rect(b)
        墨.intersect(页.rect)
        四边 = {"左": 墨.x0, "上": 墨.y0,
               "右": 页.rect.x1 - 墨.x1, "下": 页.rect.y1 - 墨.y1}
        最小边 = min(四边, key=四边.get)
        最小mm = 四边[最小边] * MM
        逐页.append({"页": 页号, "最小边": 最小边, "最小mm": round(最小mm, 2)})
        if 最小mm < BLEED_MM:
            疑似.append(页号)
    r.数据["出血扫描"] = {"逐页": 逐页, "疑似出血页": 疑似, "门限mm": BLEED_MM}
    if 疑似:
        最小值 = min(g["最小mm"] for g in 逐页 if g["最小mm"] is not None)
        r.记("⑤出血/贴边扫描", "P2", "提示",
             f"疑似出血页{疑似}（全卷最小{最小值:.2f}mm<{BLEED_MM}mm，供人工目检）")
    else:
        r.记("⑤出血/贴边扫描", "P2", "PASS", f"无<3mm贴边页（供人工目检参考）")


def 检查六_空白(doc: pymupdf.Document, r: 文件检查结果):
    逐页 = []
    空白页 = []
    表 = bytes(1 if i < NONWHITE_LT else 0 for i in range(256))
    for 页号, 页 in enumerate(doc, 1):
        pix = 页.get_pixmap(dpi=BLANK_DPI, colorspace=pymupdf.csGRAY, annots=False)
        非白 = pix.samples.translate(表).count(1)
        空白 = 非白 < BLANK_MAX_PX
        if 空白:
            空白页.append(页号)
        逐页.append({"页": 页号, "非白像素": 非白, "空白": 空白})
    备注 = []
    if 空白页 and 空白页[-1] == len(doc):
        备注.append(f"末页第{len(doc)}页空白")
    连续 = [p for p in 空白页 if p + 1 in 空白页]
    if 连续:
        备注.append(f"连续空白{连续}")
    r.数据["空白页"] = {"逐页非白像素": 逐页, "空白页": 空白页,
                       "门限": f"600dpi非白(<{NONWHITE_LT})<{BLANK_MAX_PX}px", "备注": 备注}
    if 空白页:
        r.记("⑥空白页", "P1", "FAIL", f"空白页{空白页}（{'；'.join(备注) if 备注 else '卷中空白'}）")
    else:
        r.记("⑥空白页", "P1", "PASS", f"无空白页（逐页非白像素≥{min(g['非白像素'] for g in 逐页)}）")


def 解析分本(specs: list[str]) -> list[tuple[str, int, int]]:
    分本 = []
    for s in specs or []:
        try:
            名称, 范围 = s.rsplit(":", 1)
            起, 止 = (int(x) for x in 范围.split("-", 1))
            assert 1 <= 起 <= 止
        except Exception:
            print(f"[错误] --本 格式应为 名称:起-止（1起）,得到：{s}")
            raise SystemExit(9)
        分本.append((名称, 起, 止))
    return 分本


def 检本范围(分本, 总页, 路径):
    for n, a, b in 分本:
        if not (1 <= a <= b <= 总页):
            print(f"[错误] {路径}: --本 {n}:{a}-{b} 超出页数1-{总页}")
            raise SystemExit(9)
    return 分本


def 报告md(r: 文件检查结果) -> str:
    d = r.数据
    行s = [f"# 印前自检报告——{r.路径.as_posix()}",
           f"- 生成：{datetime.now():%Y-%m-%d %H:%M:%S}｜工具：工具/印前自检.py"
           f"｜PyMuPDF {pymupdf.__version__}｜只读检查，未改写PDF"]
    行s += ["", "## 判定一览", "", "| 项 | 级别 | 结论 | 摘要 |", "|---|---|---|---|"]
    行s += [f"| {f['项']} | {f['级别']} | {f['结论']} | {f['摘要']} |" for f in r.发现]

    行s += ["", "## ① 字体全嵌入"]
    行s += [f"- {名}：{len(页)}页 {页 if len(页) < 8 else f'{页[:6]}…共{len(页)}页'}"
            for 名, 页 in d["字体"]["字体名×页"].items()]
    if d["字体"]["未嵌入字体×页"]:
        行s += ["- **未嵌入（P0）**："] + \
               [f"  - {名}×{页}" for 名, 页 in d["字体"]["未嵌入字体×页"].items()]
    else:
        行s += ["- 未嵌入字体：无（PASS）"]

    行s += ["", "## ② 图片有效dpi（拍板口径：像素宽÷显示宽英寸；高向仅参考）"]
    if d["图片dpi"]["逐图"]:
        行s += ["", "| 页 | xref | 像素 | 显示pt | dpi宽 | dpi高 | 级别 | 判定 |", "|---|---|---|---|---|---|---|---|"]
        行s += [f"| p{g['页']} | {g['xref']} | {g['像素'][0]}×{g['像素'][1]} "
                f"| {g['显示pt'][0]}×{g['显示pt'][1]} | {g['dpi宽']} | {g['dpi高']} "
                f"| {g['级别']} | {g['判定']} |" for g in d["图片dpi"]["逐图"]]
        行s += ["", "**最低5张（正图，按dpi宽）**："] + \
               [f"- p{g['页']} xref{g['xref']}：{g['dpi宽']}dpi（像素{g['像素'][0]}×{g['像素'][1]}）"
                for g in d["最低5图"]]
        if d["豁免登记"]:
            行s += ["", "**图标类小图豁免登记（<200×200px，不挂档）**："] + \
                   [f"- p{g['页']} xref{g['xref']}：像素{g['像素'][0]}×{g['像素'][1]}，"
                    f"dpi宽{g['dpi宽']}" for g in d["豁免登记"]]
        else:
            行s += ["", "图标类小图豁免登记：无"]
    else:
        行s += ["- 全卷无位图"]

    行s += ["", "## ③ 页数"]
    p = d["页数"]
    行s += [f"- 总页数：{p['总页']}（{p['奇偶']}）"]
    for 本 in p.get("按本", []):
        行s.append(f"- 本「{本['本']}」p{本['起']}-{本['止']}：{本['页数']}页（{本['奇偶']}）")
    if "按本" not in p:
        行s.append("- 按「本」分段：未提供（--本 名称:起-止）")

    行s += ["", "## ④ 页面尺寸一致性", "", "| 页 | 宽×高 pt | 宽×高 mm |", "|---|---|---|"]
    行s += [f"| p{g['页']} | {g['宽pt']}×{g['高pt']} | {g['宽mm']}×{g['高mm']} |"
            for g in d["尺寸"]["逐页"]]

    行s += ["", "## ⑤ 出血/贴边扫描（内容墨含图，距四边最小距离；<3mm＝疑似出血页）", "",
            "| 页 | 最近边 | 最小距离 mm |", "|---|---|---|"]
    行s += [f"| p{g['页']} | {g.get('最小边', '—')} | "
            f"{'—（无墨，见⑥）' if g['最小mm'] is None else g['最小mm']} |"
            for g in d["出血扫描"]["逐页"]]
    行s += ["", f"疑似出血页清单（供人工目检，脚本不判生死）：{d['出血扫描']['疑似出血页'] or '无'}"]

    行s += ["", f"## ⑥ 空白页（{d['空白页']['门限']}）", "",
            "| 页 | 非白像素 | 空白 |", "|---|---|---|"]
    行s += [f"| p{g['页']} | {g['非白像素']} | {'是' if g['空白'] else ''} |"
            for g in d["空白页"]["逐页非白像素"]]
    if d["空白页"]["备注"]:
        行s += ["- **注意**：" + "；".join(d["空白页"]["备注"])]

    退出码 = 计退出码([r])
    行s += ["", f"退出码：{退出码}（0全过／1有P0／2仅P1）"]
    return "\n".join(行s) + "\n"


def 计退出码(结果s: list[文件检查结果]) -> int:
    级s = {f["级别"] for r in 结果s for f in r.发现
           if f["结论"] == "FAIL"}  # PASS行与P2提示不计档
    if "P0" in 级s:
        return 1
    if "P1" in 级s:
        return 2
    return 0


def 报告路径(目录: Path, 路径: Path, 已用: set[str]) -> Path:
    基名 = f"印前自检-{路径.parent.name}-{路径.stem}"
    名, 序 = 基名, 1
    while f"{名}.md" in 已用:
        序 += 1
        名 = f"{基名}-{序}"
    已用.add(f"{名}.md")
    return 目录 / 名


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="印前自检：六项体检，只读，不判出血生死")
    ap.add_argument("pdfs", nargs="+", help="PDF 路径（可多个）")
    ap.add_argument("--本", action="append", default=[], metavar="名称:起-止",
                    help="按本分段统计页数，可多次；未传只报总页数")
    ap.add_argument("--报告目录", default=None, help="写入 .md/.json 报告的目录")
    a = ap.parse_args(argv[1:])
    分本 = 解析分本(a.本)

    结果s = []
    已用报告名: set[str] = set()
    for p in a.pdfs:
        路径 = Path(p)
        if 路径.suffix.lower() != ".pdf":
            print(f"[错误] 非 .pdf 输入：{路径}")
            return 9
        if not 路径.is_file():
            print(f"[错误] 找不到 PDF：{路径}")
            return 9
        r = 文件检查结果(路径)
        try:
            doc = pymupdf.open(路径)
        except Exception as e:
            print(f"[错误] 打不开 PDF：{路径}（{e}）")
            return 9
        try:
            检本范围(分本, len(doc), 路径)
            检查一_字体(doc, r)
            检查二_图片dpi(doc, r)
            检查三_页数(doc, r, 分本)
            检查四_尺寸(doc, r)
            检查五_出血(doc, r)
            检查六_空白(doc, r)
        finally:
            doc.close()
        结果s.append(r)

        print(f"== 印前自检：{路径.as_posix()} ==")
        for f in r.发现:
            print(f"{f['项']}\t{f['级别']}\t{f['结论']}\t{f['摘要']}")
        if a.报告目录:
            目录 = Path(a.报告目录)
            目录.mkdir(parents=True, exist_ok=True)
            基 = 报告路径(目录, 路径, 已用报告名)
            (目录 / f"{基.name}.md").write_text(报告md(r), encoding="utf-8")
            (目录 / f"{基.name}.json").write_text(
                json.dumps({"路径": 路径.as_posix(),
                            "生成": datetime.now().isoformat(timespec="seconds"),
                            "判定": r.发现, "读数": r.数据,
                            "退出码": 计退出码([r])},
                           ensure_ascii=False, indent=1),
                encoding="utf-8")
            print(f"报告→ {目录/(基.name+'.md')} ＋ .json")

    码 = 计退出码(结果s)
    print(f"[退出码 {码}] {'有P0' if 码 == 1 else ('仅P1' if 码 == 2 else '全过')}"
          f"（{'、'.join(str(r.路径) for r in 结果s)}）")
    return 码


if __name__ == "__main__":
    sys.exit(main(sys.argv))
