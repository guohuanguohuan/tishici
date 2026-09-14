# -*- coding: utf-8 -*-
"""S6 销案·回冲：导学件 6 片件manifest 件指纹刷新＋销案变更注记（照 S4 导学件制）。
写入域＝六片 件manifest.json。零 git。
"""
import hashlib, io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
CJ = r"C:/提示词/工作区/M3-第2章量产0913/成卷/导学件"

NOTES = {
    "课时02": ("S6 印前销案（0914，承军师三案）：S2-A1 组头宏 \\xjkeshi→\\jietitle（1 处，衔接节用例未动）；"
               "S2-A2 补【学习目标】位 \\mubiaoline＋\\mubiaomu×3（照母版 01 行36-39 制式；文案来源 "
               "zsd 分册一倾斜角→条1／分册二斜率的定义与两点斜率公式→条2／分册三倾斜角与斜率的关系→条3）；"
               "页数实测 true 5→6（增行预期漂移，装配 A1 基线回填）、false 3 零漂；复编三零，门谱复跑全绿（_tmpM3S6预备0914/门谱S6/）。"),
    "课时03": ("S6 印前销案（0914）：S2-A1 组头宏 \\xjkeshi→\\jietitle（1 处）；S2-A2 补目标位 "
               "\\mubiaoline＋\\mubiaomu×3（来源 zsd 分册一直线的方向向量→条1／分册二直线的法向量→条2／"
               "条3 军师定夺走综合应用贯通两分册）；页数 5/2 零漂；复编三零，门谱复跑全绿。"),
    "课时10": ("S6 印前销案（0914）：S2-A5 残键 10-G2 插桩销案（图资源/10-G2.png md5 93f091ba9a5b…，"
               "\\ansfig 36mm 插题面「如图」处；题面〔图注：折叠示意图，照录自源〕收短注〔照录自源〕）；"
               "页数 6/3 零漂；复编三零，门谱复跑全绿。"),
    "课时14": ("S6 印前销案（0914）：S2-A5 残七键全数插桩销案——14-拓04 36mm／14-拓11 40mm／14-拓18 38mm／"
               "14-拓33-12 情境图 24mm（主图含解设标注防纯题档泄答不插、留存图资源）／14-拓33-13 主图 40mm"
               "（答案侧带建系轴变体不插）／14-拓34-2 40mm／14-拓34-6 36mm，图源 md5 对 图资源/清单.txt 钉值全符；"
               "页数实测 18/8→19/9（大档插图预期漂移，装配 A1 基线回填）；复编三零，门谱复跑全绿。"),
    "课时16": ("S6 印前销案（0914）：S2-A5 残键 16-拓10 插桩销案（32mm 图、题面行后；实测下调 30mm 消末页 "
               "Overfull\\vbox 0.74pt——p12 课堂评价区文句化增行所致，三零复守）；S2-A6 承军师案一文句化销案："
               "\\ding{51}×23＋\\ding{55}×1 改「成立/相符/不合」文语、⇒×32/⟺×6 改「得/即/故/等价于」文语，"
               "印面与注释头 raw 符号双清零（词汇照 18/19 片先例）；页数 12/5 零漂；复编三零，门谱复跑全绿。"),
    "课时17": ("S6 印前销案（0914）：S2-A6 承军师案一文句化销案：\\ding{51}×56 改「成立/相符/回验相符」文语、"
               "⇒×8/⟺×26 改「得/即/故/等价于/推出」文语，印面与注释头 raw 符号双清零；"
               "页数 14/4 零漂；复编三零，门谱复跑全绿。"),
}

md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()


def pdir(pid):
    for d in os.listdir(CJ):
        if d == pid or d.startswith(pid + "-"):
            return os.path.join(CJ, d)
    raise SystemExit(pid)


for pid, note in NOTES.items():
    d = pdir(pid)
    fp = os.path.join(d, "件manifest.json")
    j = json.load(open(fp, encoding="utf-8"))
    fz = j.get("件指纹", {})
    for k in list(fz):
        if k.endswith(".md5"):
            name = k[:-4]
            p = os.path.join(d, name)
            if os.path.exists(p):
                fz[k] = md5(p)
    j["件指纹"] = fz
    j["变更注记"] = note
    json.dump(j, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("回冲", pid, "件manifest 指纹重钉＋变更注记落账")
print("done")
