from pathlib import Path
import importlib.util

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "04_原始资料" / "模块7立体几何" / "模块7大招5翻折问题之平面化.docx"


def load_helpers():
    path = ROOT / ".codex" / "word_revise_fold.py"
    spec = importlib.util.spec_from_file_location("word_helpers", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prose_paragraph(label: str, text: str, outline=None):
    p = OxmlElement("w:p")
    pPr = OxmlElement("w:pPr")
    p.append(pPr)
    if outline is not None:
        level = OxmlElement("w:outlineLvl")
        level.set(qn("w:val"), str(outline))
        pPr.append(level)

    r1 = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    b = OxmlElement("w:b")
    b.set(qn("w:val"), "1")
    bcs = OxmlElement("w:bCs")
    bcs.set(qn("w:val"), "1")
    rPr.extend([b, bcs])
    r1.append(rPr)
    t1 = OxmlElement("w:t")
    t1.text = label
    r1.append(t1)
    p.append(r1)

    r2 = OxmlElement("w:r")
    t2 = OxmlElement("w:t")
    t2.text = text
    r2.append(t2)
    p.append(r2)
    return p


def main():
    h = load_helpers()
    doc = Document(TARGET)
    body = doc._element.body

    prefixes = ("【符号约定】", "【翻折不变量】", "【平面化】", "【最值模型】")
    old = [p for p in h.body_paragraphs(doc) if h.node_text(p).strip().startswith(prefixes)]
    if len(old) != 4:
        raise RuntimeError(f"预计找到4段符号导语，实际找到{len(old)}段")

    insert_at = body.index(old[0])
    for p in old:
        body.remove(p)

    intro = [
        prose_paragraph(
            "【方法说明】",
            "处理分布在不同平面内的共点线段长度和、截面周长或表面最短路径时，难点在于有关线段不能直接放在同一平面内比较。沿折痕翻折或展开相关平面，使目标线段落到同一平面内，这一过程称为“平面化”。",
            outline=1,
        ),
        prose_paragraph(
            "【翻折方式】",
            "既可以翻折整个平面，也可以只翻折题目所需的线段。实际作图时，应优先选择步骤较少、展开后位置关系较清楚的方式。",
        ),
        prose_paragraph(
            "【不变关系】",
            "翻折会改变点、线、面的空间位置，但不会改变线段长度、角的大小以及图形内部的位置关系；折痕上的点始终保持不动。",
        ),
        prose_paragraph(
            "【解题关键】",
            "先确定折痕，再判断哪些量发生变化、哪些量保持不变。把所求长度或周长转化为同一平面内的折线后，通常利用两点之间线段最短、垂线段最短、三点共线或相切等条件确定最值。",
        ),
        prose_paragraph(
            "【思考顺序】",
            "遇到翻折题，可以依次思考：绕哪条线翻折？哪些长度和角保持不变？目标点能否落到同一平面内？展开后的最值在什么位置取得？",
        ),
    ]
    for offset, p in enumerate(intro):
        body.insert(insert_at + offset, p)

    # OCR result from the user-provided diagram. Place it after the existing
    # visual overview and immediately before the first worked example.
    first_problem = next(
        p for p in h.body_paragraphs(doc) if h.node_text(p).strip().startswith("【题型：翻折周长问题】")
    )
    ocr = [
        prose_paragraph("【知识框架】", "立体几何中的动态翻折问题。", outline=1),
        prose_paragraph(
            "【常见考法】",
            "点的轨迹、位置关系、体积最值、取值范围、外接球、夹角关系、展开图及最短距离。",
        ),
        prose_paragraph(
            "【处理原则】",
            "明确翻折前后不变的位置关系和数量关系，以不变应万变。",
        ),
    ]
    idx = body.index(first_problem)
    for offset, p in enumerate(ocr):
        body.insert(idx + offset, p)

    for p in intro + ocr:
        h.set_paragraph_layout(p)

    doc.save(TARGET)


if __name__ == "__main__":
    main()
