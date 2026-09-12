# 批5 结构断言——课时09／课时10（pymupdf 文本计数，照批2/批3 口径）
import pymupdf, re, sys

def count(pdf):
    doc = pymupdf.open(pdf)
    text = "".join(p.get_text() for p in doc)
    t = re.sub(r"\s+", "", text)
    rows = [
        ("页数", len(doc)),
        ("课前预习", t.count("课前预习")),
        ("课中探究", t.count("课中探究")),
        ("课堂评价", t.count("课堂评价")),
        ("探究点◆", t.count("◆探究点")),
        ("例1", t.count("例1[")),
        ("变式1", t.count("变式1[")),
        ("素养小结", t.count("素养小结")),
        ("判断正误组", t.count("判断正误")),
        ("提示词", t.count("(提示：")),
        ("书写区", t.count("解答书写区")),
        ("此处书写", t.count("此处书写")),
    ]
    return rows

for name, pdf in [("课时09", "C:/提示词/工作区/M2-第1章量产0911/成卷/导学件/课时09/main.pdf"),
                  ("课时10", "C:/提示词/工作区/M2-第1章量产0911/成卷/导学件/课时10/main.pdf")]:
    print(f"== {name} ==")
    for k, v in count(pdf):
        print(f"  {k}: {v}")
