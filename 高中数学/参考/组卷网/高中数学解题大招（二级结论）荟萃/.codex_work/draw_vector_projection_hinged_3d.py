from pathlib import Path
import math
import sys

from PIL import Image, ImageDraw, ImageFont


S = 2
W, H = 1600, 1000


def q(v):
    if isinstance(v, tuple):
        return tuple(int(round(x * S)) for x in v)
    return int(round(v * S))


def font(size, bold=False, math_font=False):
    if math_font:
        paths = [r"C:\Windows\Fonts\cambria.ttc", r"C:\Windows\Fonts\times.ttf"]
    elif bold:
        paths = [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"]
    else:
        paths = [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simsun.ttc"]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, q(size))
    return ImageFont.load_default()


def text(draw, xy, value, fnt, fill, anchor="la"):
    draw.text(q(xy), value, font=fnt, fill=fill, anchor=anchor)


def line(draw, points, fill, width=3):
    draw.line([q(p) for p in points], fill=fill, width=q(width), joint="curve")


def arrow(draw, start, end, fill, width=5, head=15):
    line(draw, [start, end], fill, width)
    t = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - head * math.cos(t - math.pi / 6), end[1] - head * math.sin(t - math.pi / 6))
    p2 = (end[0] - head * math.cos(t + math.pi / 6), end[1] - head * math.sin(t + math.pi / 6))
    draw.polygon([q(end), q(p1), q(p2)], fill=fill)


def dashed(draw, start, end, fill, width=2, dash=11, gap=8):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    pos = 0
    while pos < length:
        stop = min(length, pos + dash)
        p1 = (start[0] + ux * pos, start[1] + uy * pos)
        p2 = (start[0] + ux * stop, start[1] + uy * stop)
        line(draw, [p1, p2], fill, width)
        pos += dash + gap


def rounded(draw, box, fill, outline, radius=18, width=2):
    draw.rounded_rectangle(q(box), radius=q(radius), fill=fill, outline=outline, width=q(width))


ORIGIN = (790, 625)
SCALE = 330


def project(p):
    """Consistent oblique projection from 3-D coordinates to the page."""
    x, y, z = p
    return (
        ORIGIN[0] + SCALE * (x - 0.65 * y),
        ORIGIN[1] - SCALE * (z + 0.35 * x + 0.25 * y),
    )


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def mul(k, a):
    return tuple(k * x for x in a)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: draw_vector_projection_hinged_3d.py OUTPUT.png")
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", q((W, H)), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    navy = "#203047"
    muted = "#607087"
    border = "#CFDAE8"
    panel = "#F8FAFD"
    plane_fill = "#EDF4FF"
    plane_edge = "#8CB5F4"
    blue = "#2563EB"
    teal = "#078A76"
    orange = "#F59E0B"
    dash_color = "#77889D"

    f_title = font(32, bold=True)
    f_sub = font(18)
    f_head = font(22, bold=True)
    f_body = font(17)
    f_small = font(15)
    f_label = font(18, bold=True)
    f_math = font(20, math_font=True)
    f_formula = font(22, math_font=True)

    text(draw, (65, 48), "向量投影法｜用垂直截面看二面角", f_title, navy)
    text(draw, (65, 96), "两个侧面像合页一样沿棱 OC 张开；截面 π 与 OC 垂直。", f_sub, muted)
    text(draw, (1535, 100), "示意图不按比例", f_small, muted, anchor="ra")

    rounded(draw, (55, 140, 1545, 810), panel, border)

    # Mathematically consistent 3-D vectors.
    alpha = math.radians(65)
    beta = math.radians(55)
    dihedral = math.radians(95)
    c = (0.0, 0.0, 1.0)
    a = (math.sin(beta), 0.0, math.cos(beta))
    b = (math.sin(alpha) * math.cos(dihedral), math.sin(alpha) * math.sin(dihedral), math.cos(alpha))
    a_perp = (a[0], a[1], 0.0)
    b_perp = (b[0], b[1], 0.0)

    O = project((0, 0, 0))
    C = project(mul(1.13, c))
    A = project(a)
    B = project(b)
    Ap = project(a_perp)
    Bp = project(b_perp)

    # Perpendicular cutting plane π.
    plane3 = [(-1.10, -1.10, 0), (1.30, -1.10, 0), (1.30, 1.10, 0), (-1.10, 1.10, 0)]
    plane2 = [project(p) for p in plane3]
    draw.polygon([q(p) for p in plane2], fill=plane_fill, outline=plane_edge)
    line(draw, plane2 + [plane2[0]], plane_edge, 2)

    # Two face planes, rendered as translucent hinged sheets.
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    h = 0.90
    k = 1.18
    face_a3 = [(0, 0, 0), mul(k, a_perp), add(mul(k, a_perp), mul(h, c)), mul(h, c)]
    face_b3 = [(0, 0, 0), mul(k, b_perp), add(mul(k, b_perp), mul(h, c)), mul(h, c)]
    face_a2 = [project(p) for p in face_a3]
    face_b2 = [project(p) for p in face_b3]
    od.polygon([q(p) for p in face_b2], fill=(7, 138, 118, 48), outline=(7, 138, 118, 170))
    od.polygon([q(p) for p in face_a2], fill=(37, 99, 235, 48), outline=(37, 99, 235, 170))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Re-emphasize the hinge and all vector relationships after transparency.
    line(draw, [O, C], navy, 5)
    arrow(draw, O, C, navy, 5)
    arrow(draw, O, A, blue, 5)
    arrow(draw, O, B, teal, 5)
    dashed(draw, A, Ap, dash_color, 2)
    dashed(draw, B, Bp, dash_color, 2)
    arrow(draw, O, Ap, blue, 7)
    arrow(draw, O, Bp, teal, 7)
    draw.ellipse(q((O[0] - 6, O[1] - 6, O[0] + 6, O[1] + 6)), fill=navy)

    # Dihedral angle on the cutting plane.
    theta_a = math.degrees(math.atan2(Ap[1] - O[1], Ap[0] - O[0]))
    theta_b = math.degrees(math.atan2(Bp[1] - O[1], Bp[0] - O[0]))
    arc_box = (O[0] - 93, O[1] - 93, O[0] + 93, O[1] + 93)
    draw.arc(q(arc_box), start=theta_b, end=theta_a, fill=orange, width=q(5))

    # Labels are placed away from intersections.
    text(draw, (O[0] - 18, O[1] + 32), "O", f_label, navy)
    text(draw, (C[0] + 18, C[1] + 12), "OC（方向 c）", f_label, navy)
    text(draw, (A[0] - 35, A[1] + 38), "a", f_math, blue)
    text(draw, (B[0] + 22, B[1] - 5), "b", f_math, teal)
    text(draw, (Ap[0] - 45, Ap[1] + 40), "a⊥", f_math, blue)
    text(draw, (Bp[0] - 60, Bp[1] + 22), "b⊥", f_math, teal)
    text(draw, (O[0] + 5, O[1] - 113), "二面角 C", f_label, orange, anchor="mm")

    text(draw, (1160, 300), "平面 AOC", f_label, blue, anchor="mm")
    text(draw, (430, 365), "平面 BOC", f_label, teal, anchor="mm")
    text(draw, (255, 700), "截面 π", f_label, navy)
    text(draw, (255, 733), "π 与 OC 垂直", f_body, muted)

    # A compact explanation box directly tied to the geometry.
    rounded(draw, (1080, 500, 1495, 735), "#FFFFFF", border, radius=16, width=2)
    text(draw, (1110, 528), "截面上的两条交线", f_head, navy)
    text(draw, (1110, 577), "a⊥：平面 AOC 与 π 的交线方向", f_body, blue)
    text(draw, (1110, 620), "b⊥：平面 BOC 与 π 的交线方向", f_body, teal)
    text(draw, (1110, 676), "所以", f_body, orange)
    text(draw, (1165, 676), "∠(a⊥, b⊥) = C", f_math, orange)

    # Calculation band.
    rounded(draw, (55, 845, 1545, 950), "#EFF6FF", "#9FC2FA", radius=18, width=2)
    text(draw, (90, 878), "投影", f_label, navy)
    text(draw, (180, 878), "a⊥ = a − (a·c)c ;  b⊥ = b − (b·c)c", f_math, navy)
    text(draw, (90, 922), "结论", f_label, navy)
    formula = "cos C = (a⊥·b⊥)/(|a⊥||b⊥|) = (cos γ − cos α cos β)/(sin α sin β)"
    text(draw, (180, 922), formula, f_formula, navy)

    img = img.resize((W, H), Image.Resampling.LANCZOS)
    img.save(output, quality=95)
    print(output)


if __name__ == "__main__":
    main()
