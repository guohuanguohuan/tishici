# -*- coding: utf-8 -*-
"""排版病0911：_测v4断言.py round3 补丁机械导出 v2（difflib 块·块间不相交·count==1 fail-fast）。
块切片用 keepends 行列表直接拼接——替换即文本级精确，无线程分隔符残差。
链：A_roundtrip.py（＝round2 终态＝本轮 .bak_排版病0911 之 LF 形）→ patch_v8断言_round3.py → A_roundtrip3.py
验证：A_roundtrip3.py 与现网 _测v4断言.py（CRLF→LF 归一）逐字节相等。"""
import io, difflib, os

RT = r"C:\提示词\工作区\_tmp取证0909c\片G\全品对齐0911\rt"
SRC = os.path.join(RT, "A_roundtrip.py")
CUR = r"C:\提示词\工作区\字替对照-0909\variantF\_测v4断言.py"
OUT_PATCH = r"C:\提示词\工作区\_tmp取证0909c\片G\全品对齐0911\patch_v8断言_round3.py"
OUT_NEW = os.path.join(RT, "A_roundtrip3.py")

src = io.open(SRC, encoding="utf-8").read()
cur = io.open(CUR, encoding="utf-8", newline="").read().replace("\r\n", "\n")

a, b = src.splitlines(keepends=True), cur.splitlines(keepends=True)
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
pairs = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    old = "".join(a[i1:i2])
    new = "".join(b[j1:j2])
    while src.count(old) != 1 and i1 > 0:
        i1 -= 1; j1 -= 1
        old = "".join(a[i1:i2])
        new = "".join(b[j1:j2])
    if src.count(old) != 1:
        raise SystemExit("块无法消歧 count=%d: %r" % (src.count(old), old[:80]))
    pairs.append((old, new))

hdr = (
    "# -*- coding: utf-8 -*-\n"
    '"""patch_v8断言_round3.py —— _测v4断言.py 排版病0911 门同步（difflib 机械导出·块间不相交·count==1 fail-fast）。\n'
    "前置＝patch_v8断言.py＋patch_v8断言_round2.py（链终态 A_roundtrip.py，2313 行）；本补丁钉到 v9 态（2312 行）。\n"
    "内容＝④ zhentib_form_ok 锁串换新宏形（1000fil＋rightskip 双锁）＋④ reg 补排版病0911 句＋\n"
    "拉伸门白名单删除（p1y488.9 在|的|直|线 3 对豁免块撤除，门回净 ==0）＋拉伸 reg 尾注旧→新（修形登记）。\n"
    '"""\n'
    "import io, sys\n\n"
    'P = r"C:\\提示词\\工作区\\_tmp取证0909c\\片G\\全品对齐0911\\rt\\A_roundtrip.py"\n'
    "src = io.open(P, encoding=\"utf-8\").read()\n\n"
    "def rep(old, new):\n"
    "    global src\n"
    "    c = src.count(old)\n"
    "    if c != 1:\n"
    '        print("块失配 count=%d: %r..." % (c, old[:60])); sys.exit(1)\n'
    "    src = src.replace(old, new, 1)\n\n"
)
body = "".join("rep(%s,\n    %s)\n\n" % (repr(o), repr(n)) for o, n in pairs)
tail = (
    "OUT = r\"C:\\提示词\\工作区\\_tmp取证0909c\\片G\\全品对齐0911\\rt\\A_roundtrip3.py\"\n"
    "io.open(OUT, \"w\", encoding=\"utf-8\", newline=\"\").write(src)\n"
    'print("round3 落盘", OUT, "行数", src.count("\\n") + 1)\n'
)
io.open(OUT_PATCH, "w", encoding="utf-8", newline="").write(hdr + body + tail)
print("补丁写出:", OUT_PATCH, "块数", len(pairs))

exec(compile(hdr + body + tail, OUT_PATCH, "exec"))
new_txt = io.open(OUT_NEW, encoding="utf-8").read()
print("回环验证 A_roundtrip3 == 现网(CRLF归一):", new_txt == cur)
