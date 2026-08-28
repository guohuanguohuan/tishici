from pathlib import Path
import math
import sys

from PIL import Image, ImageDraw, ImageFont


S = 2
W, H = 1600, 1000


def pt(value):
    if isinstance(value, tuple):
        return tuple(int(round(v * S)) for v in value)
    return int(round(value * S))


def get_font(size, bold=False, math_font=False):
    if math_font:
        paths = [r"C:\Windows\Fonts\cambria.ttc", r"C:\Windows\Fonts\times.ttf"]
    elif bold:
        paths = [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"]
    else:
        paths = [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simsun.ttc"]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, pt(size))
    return ImageFont.load_default()


def txt(draw, xy, value, font, fill, anchor="la"):
    draw.text(pt(xy), value, font=font, fill=fill, anchor=anchor)


def line(draw, points, fill, width=3):
    draw.line([pt(p) for p in points], fill=fill, width=pt(width), joint="curve")


def arrow(draw, start, end, fill, width=5, head=15):
    line(draw, [start, end], fill, width)
    theta = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - head * math.cos(theta - math.pi / 6), end[1] - head * math.sin(theta - math.pi / 6))
    p2 = (end[0] - head * math.cos(theta + math.pi / 6), end[1] - head * math.sin(theta + math.pi / 6))
    draw.polygon([pt(end), pt(p1), pt(p2)], fill=fill)


def dashed(draw, start, end, fill, width=2, dash=11, gap=8):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    pos = 0.0
    while pos < length:
        stop = min(length, pos + dash)
        line(draw, [(start[0] + ux * pos, start[1] + uy * pos),
                    (start[0] + ux * stop, start[1] + uy * stop)], fill, width)
        pos += dash + gap


def rounded(draw, box, fill, outline, radius=18, width=2):
    draw.rounded_rectangle(pt(box), radius=pt(radius), fill=fill, outline=outline, width=pt(width))


def angle_arc(draw, origin, radius, start_deg, end_deg, fill, width=5):
    box = (origin[0] - radius, origin[1] - radius, origin[0] + radius, origin[1] + radius)
    draw.arc(pt(box), start=start_deg, end=end_deg, fill=fill, width=pt(width))


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: draw_vector_projection_intuitive.py OUTPUT.png")
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", pt((W, H)), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    navy = "#203047"
    muted = "#63748A"
    border = "#D0DBE8"
    panel = "#F8FAFD"
    plane = "#E9F2FF"
    plane_edge = "#88B3F6"
    blue = "#2563EB"
    blue_soft = "#8EB6FF"
    teal = "#078A76"
    teal_soft = "#72C8B9"
    orange = "#F59E0B"
    dashed_color = "#75859A"

    f_title = get_font(32, bold=True)
    f_sub = get_font(18)
    f_panel = get_font(23, bold=True)
    f_body = get_font(17)
    f_small = get_font(15)
    f_label = get_font(18, bold=True)
    f_math = get_font(20, math_font=True)
    f_formula = get_font(22, math_font=True)

    txt(draw, (65, 48), "向量投影法｜把向量的“影子”落到截面上", f_title, navy)
    txt(draw, (65, 96), "a、b、c 均为单位向量。截面 π 与 c 垂直；虚线表示沿 c 方向的正交投影。", f_sub, muted)
    txt(draw, (1535, 100), "示意图不按比例", f_small, muted, anchor="ra")

    rounded(draw, (55, 140, 1000, 785), panel, border)
    rounded(draw, (1040, 140, 1545, 785), panel, border)
    txt(draw, (85, 172), "第一眼只看这一件事：a、b 在截面上的影子", f_panel, navy)
    txt(draw, (1070, 172), "沿 c 方向俯视", f_panel, navy)

    # Main spatial view: a and b cast shadows onto the screen π along c.
    O = (480, 640)
    c_end = (480, 255)
    a_end = (805, 340)
    b_end = (245, 295)
    a_foot = (805, 650)
    b_foot = (245, 555)
    plane_poly = [(145, 700), (720, 765), (925, 575), (350, 510)]
    draw.polygon([pt(p) for p in plane_poly], fill=plane, outline=plane_edge)
    line(draw, plane_poly + [plane_poly[0]], plane_edge, 2)

    txt(draw, (165, 675), "“屏幕”π", f_label, muted)
    txt(draw, (165, 710), "π 与 c 垂直", f_small, muted)

    arrow(draw, O, c_end, navy, 4)
    arrow(draw, O, a_end, blue, 5)
    arrow(draw, O, b_end, teal, 5)
    dashed(draw, a_end, a_foot, dashed_color, 2)
    dashed(draw, b_end, b_foot, dashed_color, 2)

    # Shadows are emphasized more strongly than auxiliary geometry.
    line(draw, [O, a_foot], blue_soft, 12)
    arrow(draw, O, a_foot, blue, 5)
    line(draw, [O, b_foot], teal_soft, 12)
    arrow(draw, O, b_foot, teal, 5)

    draw.ellipse(pt((O[0] - 6, O[1] - 6, O[0] + 6, O[1] + 6)), fill=navy)
    txt(draw, (463, 669), "O", f_label, navy)
    txt(draw, (495, 270), "c", f_label, navy)
    txt(draw, (720, 392), "a", f_label, blue)
    txt(draw, (280, 348), "b", f_label, teal)
    txt(draw, (650, 682), "a 的影子：a⊥", f_body, blue, anchor="mm")
    txt(draw, (315, 605), "b 的影子：b⊥", f_body, teal, anchor="mm")
    txt(draw, (830, 495), "沿 c 投下去", f_small, muted, anchor="mm")
    txt(draw, (215, 430), "沿 c 投下去", f_small, muted, anchor="mm")

    # Eye + direction cue between spatial and top views.
    arrow(draw, (930, 360), (1030, 360), orange, 4, 13)
    draw.ellipse(pt((952, 315, 1008, 345)), outline=orange, width=pt(3))
    draw.ellipse(pt((975, 323, 985, 333)), fill=orange)
    txt(draw, (980, 385), "视线 ∥ c", f_small, orange, anchor="ma")

    # Top view: the dihedral angle is now plainly the angle between shadows.
    O2 = (1275, 500)
    a2 = (1480, 425)
    b2 = (1120, 300)
    draw.ellipse(pt((1090, 260, 1510, 665)), fill="#FFFFFF", outline=plane_edge, width=pt(2))
    txt(draw, (1298, 690), "俯视截面 π", f_body, muted, anchor="mm")
    arrow(draw, O2, a2, blue, 6)
    arrow(draw, O2, b2, teal, 6)
    draw.ellipse(pt((O2[0] - 6, O2[1] - 6, O2[0] + 6, O2[1] + 6)), fill=navy)
    txt(draw, (1260, 531), "O", f_label, navy)
    txt(draw, (1440, 390), "a⊥", f_math, blue)
    txt(draw, (1085, 284), "b⊥", f_math, teal)

    theta_a = math.degrees(math.atan2(a2[1] - O2[1], a2[0] - O2[0]))
    theta_b = math.degrees(math.atan2(b2[1] - O2[1], b2[0] - O2[0]))
    angle_arc(draw, O2, 90, theta_b, theta_a, orange, 5)
    txt(draw, (1288, 393), "C", f_math, orange, anchor="mm")
    txt(draw, (1295, 735), "影子的夹角就是二面角 C", f_label, orange, anchor="mm")

    # Compact calculation band: explanation follows the picture, not vice versa.
    rounded(draw, (55, 820, 1545, 950), "#EFF6FF", "#9FC2FA", radius=18, width=2)
    txt(draw, (90, 850), "投影长度", f_label, navy)
    txt(draw, (225, 850), "β = ∠(a,c)  ⇒  |a⊥| = sin β", f_math, blue)
    txt(draw, (720, 850), "α = ∠(b,c)  ⇒  |b⊥| = sin α", f_math, teal)
    txt(draw, (90, 905), "点积计算", f_label, navy)
    formula = "cos C = (a⊥·b⊥)/(|a⊥||b⊥|) = (cos γ − cos α cos β)/(sin α sin β)"
    txt(draw, (225, 906), formula, f_formula, navy)

    img = img.resize((W, H), Image.Resampling.LANCZOS)
    img.save(output, quality=95)
    print(output)


if __name__ == "__main__":
    main()
