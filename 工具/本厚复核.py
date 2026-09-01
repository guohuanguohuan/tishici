# -*- coding: utf-8 -*-
"""本厚复核.py——装订单「本划分」逐本页数合计复核（公共规则§11册厚控制分本制＋配页前检查⑤）。

用法：python 本厚复核.py <装订单.md路径>
解析「本划分」节（节头兼容「## 本划分」与「## 三、本划分」等序号形态）内形如 `- **本1**＝…：内容页合计 **16** 页。` 的行，
逐本取页数合计，断言每本≤400页（分本制第二顺位二次拆分触发线）。
只读；断言不过退出码1。输出逐本页数＋全册合计＋判定结论（供配页前检查⑤落数字）。
"""
import re
import sys

LIMIT = 400
LINE = re.compile(r"-\s*\*\*(本\d+)\*\*＝.*?内容页合计\s*\*\*(\d+)\*\*\s*页")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("用法：python 本厚复核.py <装订单.md路径>")
        return 2
    path = argv[1]
    text = open(path, encoding="utf-8").read()
    m = re.search(r"##\s*(?:[一二三四五六七八九十]+、)?\s*本划分.*?(?=\n##\s|\Z)", text, re.S)
    if not m:
        print(f"[FAIL] 未找到「本划分」节：{path}")
        return 1
    rows = LINE.findall(m.group(0))
    if not rows:
        print("[FAIL] 本划分节内未解析出任何「内容页合计」行")
        return 1
    ok = True
    total = 0
    for name, pages in rows:
        p = int(pages)
        total += p
        flag = "OK" if p <= LIMIT else "超限→第二顺位二次拆分"
        if p > LIMIT:
            ok = False
        print(f"{name}\t{p}页\t≤{LIMIT}:{flag}")
    print(f"合计\t{total}页\t本数={len(rows)}")
    print("[PASS] 逐本均≤400页，本厚复核通过" if ok else "[FAIL] 存在超限本，须二次拆分后复跑")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
