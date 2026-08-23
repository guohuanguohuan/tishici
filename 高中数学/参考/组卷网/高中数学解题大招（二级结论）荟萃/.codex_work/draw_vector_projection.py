from pathlib import Path
import math
import sys

from PIL import Image, ImageDraw, ImageFont


SCALE = 2
W, H = 1600, 980


def sc(v):
    if isinstance(v, tuple):
        return tuple(int(round(x * SCALE)) for x in v)
    return int(round(v * SCALE))


def font(size, bold=False, math_font=False):
    if math_font:
        candidates = [
            r"C:\Windows\Fonts\cambria.ttc",
            r"C:\Windows\Fonts\times.ttf",
        ]
    elif bold:
        candidates = [
            r"C:\Windows\Fonts\msyhbd.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
        ]
    else:
        candidates = [
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\simsun.ttc",
        ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, sc(size))
    return ImageFont.load_default()


def line(draw, points, fill, width=3, joint="curve"):
    draw.line([sc(p) for p in points], fill=fill, width=sc(width), joint=joint)


def arrow(draw, start, end, fill, width=4, head=13):
    line(draw, [start, end], fill, width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    left = (
        end[0] - head * math.cos(angle - math.pi / 6),
        end[1] - head * math.sin(angle - math.pi / 6),
    )
    right = (
        end[0] - head * math.cos(angle + math.pi / 6),
        end[1] - head * math.sin(angle + math.pi / 6),
    )
    draw.polygon([sc(end), sc(left), sc(right)], fill=fill)


def dashed(draw, start, end, fill, width=2, dash=10, gap=8):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    pos = 0.0
    while pos < length:
        stop = min(length, pos + dash)
        p1 = (start[0] + ux * pos, start[1] + uy * pos)
        p2 = (start[0] + ux * stop, start[1] + uy * stop)
        line(draw, [p1, p2], fill, width)
        pos += dash + gap


def text(draw, xy, value, fnt, fill, anchor="la"):
    draw.text(sc(xy), value, font=fnt, fill=fill, anchor=anchor)


def arc_between(draw, origin, r, theta1, theta2, fill, width=3):
    box = (origin[0] - r, origin[1] - r, origin[0] + r, origin[1] + r)
    draw.arc(sc(box), start=theta1, end=theta2, fill=fill, width=sc(width))


def rounded_box(draw, box, fill, outline, radius=18, width=2):
    draw.rounded_rectangle(sc(box), radius=sc(radius), fill=fill, outline=outline, width=sc(width))


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: draw_vector_projection.py OUTPUT.png")
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", sc((W, H)), "#FFFFFF")
    draw = ImageDraw.Draw(image)

    navy = "#203047"
    muted = "#607087"
    border = "#CFD9E7"
    panel = "#F8FAFD"
    plane_fill = "#EAF2FF"
    plane_edge = "#8CB5F4"
    blue = "#2563EB"
    teal = "#078A76"
    orange = "#F59E0B"
    dashed_color = "#7A8AA2"

    f_title = font(32, bold=True)
    f_subtitle = font(18)
    f_panel = font(23, bold=True)
    f_body = font(17)
    f_small = font(15)
    f_math = font(20, math_font=True)
    f_math_small = font(17, math_font=True)
    f_label = font(18, bold=True)

    text(draw, (70, 50), "证明一｜向量投影法", f_title, navy)
    text(draw, (70, 96), "a、b、c 均为单位向量；把 a、b 沿 c 的分量去掉，在垂直于 c 的截面内计算夹角。", f_subtitle, muted)
    text(draw, (1530, 101), "示意图：角度与长度不按比例", f_small, muted, anchor="ra")

    rounded_box(draw, (55, 145, 895, 770), panel, border)
    rounded_box(draw, (925, 145, 1545, 770), panel, border)
    text(draw, (85, 175), "① 空间中的正交分解", f_panel, navy)
    text(draw, (955, 175), "② 截面 π 中的夹角", f_panel, navy)

    # Left panel: three unit directions and their orthogonal projections onto π.
    O = (430, 620)
    C = (430, 255)
    Aperp = (735, 640)
    Bperp = (255, 470)
    A = (735, 355)
    B = (255, 285)
    plane = [(155, 685), (675, 735), (790, 545), (270, 490)]
    draw.polygon([sc(p) for p in plane], fill=plane_fill, outline=plane_edge)
    line(draw, plane + [plane[0]], plane_edge, 2)
    text(draw, (178, 662), "截面 π 与 c 垂直", f_body, muted)

    arrow(draw, O, C, navy, 4)
    arrow(draw, O, A, blue, 4)
    arrow(draw, O, B, teal, 4)
    arrow(draw, O, Aperp, blue, 4)
    arrow(draw, O, Bperp, teal, 4)
    dashed(draw, A, Aperp, dashed_color, 2)
    dashed(draw, B, Bperp, dashed_color, 2)

    draw.ellipse(sc((O[0] - 5, O[1] - 5, O[0] + 5, O[1] + 5)), fill=navy)
    text(draw, (414, 646), "O", f_label, navy)
    text(draw, (448, 270), "c", f_label, navy)
    text(draw, (650, 390), "a", f_label, blue)
    text(draw, (300, 330), "b", f_label, teal)
    text(draw, (620, 690), "a⊥", f_math, blue)
    text(draw, (300, 520), "b⊥", f_math, teal)
    text(draw, (765, 493), "沿 c 正交投影", f_small, muted, anchor="mm")

    # Angle labels between the original directions and c.
    arc_between(draw, O, 57, 270, 312, orange, 3)
    text(draw, (475, 553), "β", f_math, orange)
    arc_between(draw, O, 74, 248, 270, orange, 3)
    text(draw, (397, 532), "α", f_math, orange)

    text(draw, (84, 722), "a⊥ = a − (a·c)c", f_math_small, blue)
    text(draw, (470, 722), "b⊥ = b − (b·c)c", f_math_small, teal)

    # Right panel: the two projected vectors lie in one plane.
    O2 = (1150, 520)
    A2 = (1450, 410)
    B2 = (1010, 280)
    arrow(draw, O2, A2, blue, 5)
    arrow(draw, O2, B2, teal, 5)
    draw.ellipse(sc((O2[0] - 5, O2[1] - 5, O2[0] + 5, O2[1] + 5)), fill=navy)
    text(draw, (1135, 548), "O", f_label, navy)
    text(draw, (1436, 382), "a⊥", f_math, blue)
    text(draw, (972, 272), "b⊥", f_math, teal)
    text(draw, (1325, 486), "|a⊥| = sin β", f_math_small, blue, anchor="mm")
    text(draw, (1047, 390), "|b⊥| = sin α", f_math_small, teal, anchor="mm")

    angle_a = math.degrees(math.atan2(A2[1] - O2[1], A2[0] - O2[0]))
    angle_b = math.degrees(math.atan2(B2[1] - O2[1], B2[0] - O2[0]))
    arc_between(draw, O2, 82, angle_b, angle_a, orange, 4)
    text(draw, (1160, 426), "C", f_math, orange, anchor="mm")

    rounded_box(draw, (970, 590, 1500, 728), "#FFFFFF", border, radius=14, width=2)
    text(draw, (995, 616), "a⊥·b⊥ = a·b − (a·c)(b·c)", f_math_small, navy)
    text(draw, (995, 657), "= cos γ − cos α cos β", f_math_small, navy)
    text(draw, (995, 698), "∠(a⊥, b⊥) = C", f_math_small, orange)

    # Final calculation band.
    rounded_box(draw, (55, 805, 1545, 930), "#EFF6FF", "#A9C7F7", radius=18, width=2)
    text(draw, (95, 839), "因此", f_label, navy)
    formula = "cos C = (a⊥·b⊥)/(|a⊥||b⊥|) = (cos γ − cos α cos β)/(sin α sin β)"
    text(draw, (215, 858), formula, f_math, navy, anchor="lm")
    text(draw, (215, 900), "投影后的夹角就是棱 OC 处的二面角。", f_body, muted, anchor="lm")

    image = image.resize((W, H), Image.Resampling.LANCZOS)
    image.save(output, quality=95)
    print(output)


if __name__ == "__main__":
    main()
