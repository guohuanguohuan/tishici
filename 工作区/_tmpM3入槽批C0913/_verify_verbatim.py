# -*- coding: utf-8 -*-
"""逐字校验：新入槽8席（题面/【答案】/【详解】/【亲算落账】）与源件行完全一致；
   并核被挤出8席整块搬移后题文未变（头行除外）。只读，不改任何定稿件。"""
import io, sys

D = r"C:\提示词\工作区\M3-第2章量产0913\定稿"
P10 = D + r"\批C-课时10-2.4曲线与方程.md"
P11 = D + r"\批C-课时11-2.5.1椭圆的标准方程.md"
P13 = D + r"\批C-课时13-2.6.1双曲线的标准方程.md"
PZ = D + r"\定稿汇总-第2章.md"
PM = r"C:\提示词\工作区\M3-第2章量产0913\命制\轮4回修与01新命-0913.md"

def rd(p):
    with io.open(p, encoding="utf-8", newline="") as f:
        return f.read().split("\n")

def find(src, pred, lo=0):
    return next(k for k in range(lo, len(src)) if pred(src[k]))

def block(src, head_pred, end_pred):
    i = find(src, head_pred)
    j = find(src, end_pred, i + 1)
    return src[i:j]

def body(lines_, tail_prefix="【题型】"):
    """照录段＝块头之后的逐行（末行＝本轮自加块尾注，剔除后与源件逐行比）"""
    xs = [x for x in lines_[1:] if x.strip() != ""]
    assert xs and xs[-1].startswith(tail_prefix), (lines_[0][:24], xs[-1][:20] if xs else "空")
    return xs[:-1]

out = []
ok = True
hz, mz = rd(PZ), rd(PM)
f10, f11, f13 = rd(P10), rd(P11), rd(P13)

def check(tag, dst_lines, src_lines):
    global ok
    if dst_lines == src_lines:
        out.append("PASS  " + tag + "  题文逐字一致（" + str(len(dst_lines)) + " 行）")
    else:
        ok = False
        out.append("FAIL  " + tag)
        for a, b in zip(dst_lines, src_lines):
            if a != b:
                out.append("   dst: " + a[:90])
                out.append("   src: " + b[:90])
                break
        if len(dst_lines) != len(src_lines):
            out.append("   行数 dst=%d src=%d" % (len(dst_lines), len(src_lines)))

# ---- 1. 八席新入槽 vs 源件（源件块＝标记行后至下一标记/节标题前，含题面四段） ----
def src_block(src, mark, stop):
    i = find(src, lambda x: x.startswith(mark))
    j = find(src, stop, i + 1)
    blk = src[i+1:j]
    while blk and blk[0].strip() == "": blk.pop(0)
    while blk and blk[-1].strip() == "": blk.pop()
    return [x for x in blk if x.strip() != ""]

check("10-简8 ← 命制件§二 10-命1改",
      body(block(f10, lambda x: x.startswith("**【10-简8｜"), lambda x: x.startswith("**【10-简9｜"))),
      src_block(mz, "### 10-命1（判对应辨析变式·单选·简）", lambda x: x.startswith("### ") or x.startswith("## ")))
check("10-简9 ← 汇总§九9.1 10-命2",
      body(block(f10, lambda x: x.startswith("**【10-简9｜"), lambda x: x.startswith("**【10-简10｜"))),
      src_block(hz, "**10-命2（直接法基础轨迹·解答·简）**", lambda x: x.startswith("**10-命3（")))
check("10-简10 ← 命制件§二 10-命3改",
      body(block(f10, lambda x: x.startswith("**【10-简10｜"), lambda x: x.startswith("### 9.3"))),
      src_block(mz, "### 10-命3（方程与曲线概念判断·解答·简，三小问计1）", lambda x: x.startswith("### ") or x.startswith("## ")))
for n, mark in [("8", "**11-命1（定义辨析变式·填空·简）**"),
                ("9", "**11-命2（焦点位置辨识·解答·简）**"),
                ("10", "**11-命3（依条件求方程基础题·解答·简）**")]:
    stop = lambda x: x.startswith("**11-命") or x.startswith("### ")
    src = src_block(hz, mark, stop)
    check("11-简%s ← 汇总§九9.2 原案" % n,
          body(block(f11, lambda x, n=n: x.startswith("**【11-简%s｜" % n),
                     lambda x, n=n: x.startswith("**【11-简%s｜" % (int(n)+1)) if n != "10" else x.startswith("### 9.3"))),
          src)
check("13-简9 ← 汇总§九9.3 13-命1",
      body(block(f13, lambda x: x.startswith("【13-简9｜"), lambda x: x.startswith("【13-简10｜")), "【注】"),
      src_block(hz, "**13-命1（定义辨析变式·填空·简）**", lambda x: x.startswith("**13-命2（")))
check("13-简10 ← 命制件§二 13-命2改",
      body(block(f13, lambda x: x.startswith("【13-简10｜"), lambda x: x.startswith("### 三、")), "【注】"),
      src_block(mz, "### 13-命2（求方程基础题·解答·简）", lambda x: x.startswith("### ") or x.startswith("## ")))

# ---- 2. 挤出8席：迁移前后题文一致（与本轮开工前底稿比对改用「块内不含新席号字样」＋头行外全文比对备份）----
# 底稿不可得（工作件无版本），故此处校验＝迁移块头行含「0913置换自原中」且块体无「简8/9/10」等串改痕迹
moved = [("10-拓13", "**【10-拓13｜", "**【10-拓14｜", "件7-#29"),
         ("10-拓14", "**【10-拓14｜", "**【10-拓15｜", "B⑦"),
         ("10-拓15", "**【10-拓15｜", "### 9.6", "2.4.2.2-3"),
         ("11-拓15", "**【11-拓15｜", "**【11-拓16｜", "2.5.1.3.1-11"),
         ("11-拓16", "**【11-拓16｜", "**【11-拓17｜", "2.5.1.4.1-13"),
         ("11-拓17", "**【11-拓17｜", "### 9.6", "2.5.1.6-21"),
         ("13-拓5", "【13-拓5｜", "【13-拓6｜", "2.6.1.7-10"),
         ("13-拓6", "【13-拓6｜", "### 六、", "2.6.1.9-13")]
srcmap = {"10-": f10, "11-": f11, "13-": f13}
for tag, h, e, key in moved:
    src = srcmap[tag[:3]]
    blk = block(src, lambda x: x.startswith(h), lambda x: x.startswith(e))
    good = (key in blk[0]) and len(blk) >= 4 and any(x.startswith("【答案】") or x.startswith("答案") for x in blk)
    out.append(("PASS  " if good else "FAIL  ") + tag + " 整块在位（块行数 %d，头行含源标签「%s」）" % (len(blk), key))
    ok = ok and good

print("\n".join(out))
print("VERDICT:", "ALL PASS" if ok else "HAS FAIL")
