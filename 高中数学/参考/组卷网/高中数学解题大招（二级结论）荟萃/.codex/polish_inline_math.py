from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def append_text(parent, text: str) -> None:
    run = OxmlElement("w:r")
    node = OxmlElement("w:t")
    if text.startswith(" ") or text.endswith(" "):
        node.set(qn("xml:space"), "preserve")
    node.text = text
    run.append(node)
    parent.append(run)


def append_math(parent, text: str) -> None:
    math = OxmlElement("m:oMath")
    run = OxmlElement("m:r")
    node = OxmlElement("m:t")
    node.text = text
    run.append(node)
    math.append(run)
    parent.append(math)


def set_mixed(paragraph, segments: list[tuple[str, str]]) -> None:
    p = paragraph._p
    for child in list(p):
        if child.tag != qn("w:pPr"):
            p.remove(child)
    for kind, value in segments:
        (append_math if kind == "math" else append_text)(p, value)


def replace_text_outside_math(paragraph, old: str, new: str) -> None:
    for child in paragraph._p:
        if child.tag in {qn("m:oMath"), qn("m:oMathPara")}:
            continue
        for node in child.iter(qn("w:t")):
            if node.text and old in node.text:
                node.text = node.text.replace(old, new)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    target = Path(sys.argv[1]).resolve()
    doc = Document(target)
    p = doc.paragraphs

    replace_text_outside_math(p[4], "=______", "的值为多少")

    set_mixed(p[49], [
        ("text", "因为向量 "), ("math", "BF=(0,2,1)"),
        ("text", "，向量 "), ("math", "DE=(1−a,1,−2)"),
        ("text", "，且 "), ("math", "BF·DE=0×(1−a)+2×1+1×(−2)=0"),
        ("text", "，所以直线 BF 垂直于直线 DE。"),
    ])
    set_mixed(p[51], [
        ("text", "取 BC 的中点 G。三角形 B₁GF 是三角形 DEF 在侧面 BB₁C₁C 上的投影。设二面角的平面角为 "),
        ("math", "θ"), ("text", "，则 "),
        ("math", "cosθ=S_(△B₁GF)/S_(△DEF)"),
        ("text", "。要使二面角正弦值最小，只需使这个余弦值最大。"),
    ])
    set_mixed(p[52], [
        ("text", "三角形 DEF 在侧面 BB₁C₁C 上的投影是固定三角形 B₁GF，其面积为 "),
        ("math", "3/2"),
        ("text", "；线段 EF 的长度也固定。因此问题转化为求三角形 DEF 的最小面积，进一步转化为求点 D 到定直线 EF 的最小距离。"),
    ])
    set_mixed(p[54], [
        ("math", "d=√(DF^2−(DF·EF/|EF|)^2)=√((a^2+5)−(a+1)^2/3)=√6/3·√(a^2−a+7)"),
        ("text", "。"),
    ])
    set_mixed(p[55], [
        ("text", "当 "), ("math", "a=1/2"), ("text", " 时，"),
        ("math", "d_min=3√2/2"), ("text", "，此时 "),
        ("math", "(S_(△DEF))_min=1/2·EF·d_min=1/2×√3×3√2/2=3√6/4"),
        ("text", "。"),
    ])
    set_mixed(p[56], [
        ("text", "因此 "),
        ("math", "(cosθ)_max=S_(△B₁GF)/(S_(△DEF))_min=(3/2)/(3√6/4)=√6/3"),
        ("text", "。"),
    ])
    set_mixed(p[57], [
        ("math", "(sinθ)_min=√(1−(√6/3)^2)=√3/3"),
        ("text", "，此时 "), ("math", "B₁D=1/2"), ("text", "。"),
    ])
    set_mixed(p[58], [
        ("text", "所以当 "), ("math", "B₁D=1/2"),
        ("text", " 时，平面 BB₁C₁C 与平面 DFE 所成二面角的正弦值最小。"),
    ])
    set_mixed(p[61], [
        ("text", "因为向量 "), ("math", "EF=(−1,1,1)"),
        ("text", "，向量 "), ("math", "DE=(1−a,1,−2)"),
        ("text", "，所以 "),
        ("math", "{█(m·EF=0@m·DE=0)┤"),
        ("text", "，即 "),
        ("math", "{█(−x+y+z=0@(1−a)x+y−2z=0)┤"), ("text", "。"),
    ])
    set_mixed(p[63], [
        ("text", "记所求二面角的平面角为 "), ("math", "θ"),
        ("text", "。侧面 BB₁C₁C 的一个法向量为 "), ("math", "BA=(2,0,0)"),
        ("text", "，所以 "),
        ("math", "|cosθ|=|m·BA|/(|m||BA|)=6/(2√(2a^2−2a+14))=3/√(2a^2−2a+14)"),
        ("text", "。"),
    ])
    set_mixed(p[64], [
        ("text", "当 "), ("math", "a=1/2"), ("text", " 时，"),
        ("math", "2a^2−2a+14"), ("text", " 取得最小值 "),
        ("math", "27/2"), ("text", "，从而 "),
        ("math", "|cosθ|_max=√6/3"), ("text", "。"),
    ])
    set_mixed(p[65], [
        ("math", "(sinθ)_min=√(1−(√6/3)^2)=√3/3"),
        ("text", "，此时 "), ("math", "B₁D=1/2"), ("text", "。"),
    ])
    set_mixed(p[66], [
        ("text", "所以当 "), ("math", "B₁D=1/2"),
        ("text", " 时，平面 BB₁C₁C 与平面 DFE 所成二面角的正弦值最小。"),
    ])

    set_mixed(p[150], [
        ("text", "则 "), ("math", "C(0,0,0)"), ("text", "，"),
        ("math", "C′(0,0,2√3)"), ("text", "。设 "),
        ("math", "P(0,a,0)"), ("text", "，"), ("math", "Q(b,0,0)"),
        ("text", "，其中 "), ("math", "0<a≤4"), ("text", "，"), ("math", "0<b≤3"),
        ("text", "。于是 "), ("math", "PC′=(0,−a,2√3)"), ("text", "，"),
        ("math", "QC′=(−b,0,2√3)"), ("text", "，"),
        ("math", "CC′=(0,0,2√3)"), ("text", "。"),
    ])
    set_mixed(p[151], [
        ("text", "设平面 PQC′ 的一个法向量为 "), ("math", "n=(x,y,z)"),
        ("text", "，则 "),
        ("math", "{█(n·PC′=0@n·QC′=0)┤"),
        ("text", "，即 "),
        ("math", "{█(−ay+2√3z=0@−bx+2√3z=0)┤"),
        ("text", "。令 "), ("math", "z=1"), ("text", "，得 "),
        ("math", "n=(2√3/b,2√3/a,1)"), ("text", "。"),
    ])
    set_mixed(p[152], [
        ("text", "由线面角条件，"),
        ("math", "cos(n,CC′)=1/√(12/b^2+12/a^2+1)=1/2"),
        ("text", "，所以 "),
        ("math", "12/a^2+12/b^2=3"),
        ("text", "，即 "), ("math", "a^2b^2=4(a^2+b^2)"),
        ("text", "。又因为 "), ("math", "a^2+b^2≥2ab"),
        ("text", "，所以 "), ("math", "ab≥8"), ("text", "。"),
    ])
    set_mixed(p[154], [
        ("text", "直线 CC′ 与动平面 PQC′ 所成的角固定为 "), ("math", "30°"),
        ("text", "，所以点 C 到平面 PQC′ 的距离保持为 "),
        ("math", "d=CC′·sin30°=2√3×1/2=√3"), ("text", "。"),
    ])
    set_mixed(p[155], [
        ("text", "同一四面体换底计算，体积不变，即 "),
        ("math", "V_(C′−PQC)=V_(C−PQC′)"), ("text", "。因此 "),
        ("math", "1/3×4×2√3=1/3×S_(△PQC′)×√3"),
        ("text", "，解得 "), ("math", "S_(△PQC′)=8"), ("text", "。"),
    ])

    # “知识点”内容已删除，相应的空栏目横幅也一并去掉，只保留例题栏目。
    empty_knowledge_banner = p[2]._element
    empty_knowledge_banner.getparent().remove(empty_knowledge_banner)

    doc.save(target)
    print(f"saved={target}")


if __name__ == "__main__":
    main()
