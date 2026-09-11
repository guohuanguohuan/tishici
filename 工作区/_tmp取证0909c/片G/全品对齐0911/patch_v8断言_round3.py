# -*- coding: utf-8 -*-
"""patch_v8断言_round3.py —— _测v4断言.py 排版病0911 门同步（difflib 机械导出·块间不相交·count==1 fail-fast）。
前置＝patch_v8断言.py＋patch_v8断言_round2.py（链终态 A_roundtrip.py，2313 行）；本补丁钉到 v9 态（2312 行）。
内容＝④ zhentib_form_ok 锁串换新宏形（1000fil＋rightskip 双锁）＋④ reg 补排版病0911 句＋
拉伸门白名单删除（p1y488.9 在|的|直|线 3 对豁免块撤除，门回净 ==0）＋拉伸 reg 尾注旧→新（修形登记）。
"""
import io, sys

P = r"C:\提示词\工作区\_tmp取证0909c\片G\全品对齐0911\rt\A_roundtrip.py"
src = io.open(P, encoding="utf-8").read()

def rep(old, new):
    global src
    c = src.count(old)
    if c != 1:
        print("块失配 count=%d: %r..." % (c, old[:60])); sys.exit(1)
    src = src.replace(old, new, 1)

rep("zhentib_form_ok = (r'\\noindent#1\\kern2.1pt#2\\nobreak\\hspace{0pt plus 1fil}\\nobreak（\u3000）\\hspace{0.56mm}\\par' in blkfile)\n",
    "zhentib_form_ok = (r'\\noindent#1\\kern2.1pt#2\\nobreak\\hspace{0pt plus 1000fil}\\nobreak（\u3000）\\hspace{0.56mm}\\par' in blkfile\n                   and r'{\\rightskip=0pt plus 1fil\\parfillskip=0pt' in blkfile)\n")

rep("reg('④ 判断括号换形（全品对齐0911）', '\\\\zhentib 尾段＝\\\\nobreak\\\\hspace{0pt plus 1fil}\\\\nobreak（\u3000）\\\\hspace{0.56mm}——'\n",
    "reg('④ 判断括号换形（全品对齐0911；排版病0911 拉伸空洞修）', '\\\\zhentib 尾段＝\\\\nobreak\\\\hspace{0pt plus 1000fil}\\\\nobreak（\u3000）\\\\hspace{0.56mm}——'\n")

rep("    '右挂机制（fil 双 nobreak 直连＋\\\\kern2.1pt 序号隙）承 \\\\zhenti 逐字不动，槽内容改空、括号改全角（照全品 p04 实拍）；'\n",
    "    '右挂机制（fil 双 nobreak 直连＋\\\\kern2.1pt 序号隙）承 \\\\zhenti 逐字不动，槽内容改空、括号改全角（照全品 p04 实拍）；'\n    '排版病0911：组内加 \\\\rightskip=0pt plus 1fil（题干超一行时首行改右参差，拉宽不再集中于「，」后胶→空洞）'\n    '＋内部胶 1fil→1000fil（末行拉伸 99.9% 归内部胶，（\u3000）右挂残差实测 0.1–0.2pt，在窗内）；'\n")

rep("            if (_pno == 0 and abs(_gy - 488.9) < 0.6\n                    and (_a[2], _b2[2]) in (('在', '的'), ('的', '直'), ('直', '线'))):\n                continue   # 全品对齐0911 豁免登记（见 reg）：6h kongbai 定宽使知识点表格\n                           #   「…线段所在/的直线＋两空」行断移位，残行「在的直线」被两端对齐均拉 3×5.51pt\n",
    '')

rep("    '全品对齐0911：豁免 1 行 3 对——p1y488.9「在|的|直|线」3×5.51pt（0.53em）均拉，成因＝6h kongda 自适盒→'\n    'kongbai 15mm 定宽，知识点表格「…所在的直线＿或＿」格行断移位、残行两端对齐拉 CJKglue（目验轻、非 #41 级过拉）；'\n    '修形需格内换行/换宽重排全表分页，本轮不取，冻 L1 后处理——豁免判据按（页,y,字对）三元组白名单，位移即红')\n",
    "    '全品对齐0911 曾豁免 1 行 3 对（p1y488.9「在|的|直|线」3×5.51pt 均拉），排版病0911 已修：'\n    'postproc 表1 共线行·定义列格文首个 \\\\kongbai 前插 \\\\hspace{0pt plus 1fill}——断行空隙全进 fill、文字零拉伸；'\n    '格内换行 7/7/4/1→8/8/2/1（四行 y 坐标与两空线盒位与旧版逐字节同、prevgraf 仍 4、行高档不变），'\n    '行1-2 均拉 4.61→2.46pt（格内两端对齐设计档内），行3「直线」1.04pt 自然缝；白名单删除，门回净 ==0')\n")

OUT = r"C:\提示词\工作区\_tmp取证0909c\片G\全品对齐0911\rt\A_roundtrip3.py"
io.open(OUT, "w", encoding="utf-8", newline="").write(src)
print("round3 落盘", OUT, "行数", src.count("\n") + 1)
