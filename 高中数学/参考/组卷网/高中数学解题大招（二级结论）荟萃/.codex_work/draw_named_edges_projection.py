from pathlib import Path
import math
import sys

from PIL import Image, ImageDraw, ImageFont


S = 2
W, H = 1600, 1000
ORIGIN = (760, 650)
SCALE = 355


def px(v):
    if isinstance(v, tuple):
        return tuple(int(round(x * S)) for x in v)
    return int(round(v * S))


def get_font(size, bold=False, math_font=False):
    if math_font:
        paths = [r"C:\Windows\Fonts\cambria.ttc", r"C:\Windows\Fonts\times.ttf"]
    elif bold:
        paths = [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"]
    else:
        paths = [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simsun.ttc"]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, px(size))
    return ImageFont.load_default()


def text(draw, xy, value, fnt, fill, anchor="la"):
    draw.text(px(xy), value, font=fnt, fill=fill, anchor=anchor)


def line(draw, points, fill, width=3):
    draw.line([px(p) for p in points], fill=fill, width=px(width), joint="curve")


def arrow(draw, start, end, fill, width=5, head=14):
    line(draw, [start, end], fill, width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - head * math.cos(angle - math.pi / 6), end[1] - head * math.sin(angle - math.pi / 6))
    p2 = (end[0] - head * math.cos(angle + math.pi / 6), end[1] - head * math.sin(angle + math.pi / 6))
    draw.polygon([px(end), px(p1), px(p2)], fill=fill)


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
    draw.rounded_rectangle(px(box), radius=px(radius), fill=fill, outline=outline, width=px(width))


def project(p):
    x, y, z = p
    return (
        ORIGIN[0] + SCALE * (x - 0.65 * y),
        ORIGIN[1] - SCALE * (z + 0.35 * x + 0.25 * y),
    )


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: draw_named_edges_projection.py OUTPUT.png")
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", px((W, H)), "#FFFFFF")
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
    violet = "#7C3AED"
    dashed_color = "#718299"

    f_title = get_font(32, bold=True)
    f_sub = get_font(18)
    f_head = get_font(22, bold=True)
    f_body = get_font(17)
    f_small = get_font(15)
    f_label = get_font(19, bold=True)
    f_math = get_font(19, math_font=True)
    f_formula = get_font(21, math_font=True)

    text(draw, (65, 48), "空间余弦定理｜先看清 OA、OB、OC", f_title, navy)
    text(draw, (65, 96), "沿三条棱各取一个单位点 A、B、C，使 OA = OB = OC = 1。", f_sub, muted)
    text(draw, (1535, 100), "示意图不按比例", f_small, muted, anchor="ra")

    rounded(draw, (55, 140, 1545, 820), panel, border)

    # Unit rays: α=∠BOC, β=∠COA, and the dihedral angle along OC is C.
    alpha = math.radians(65)
    beta = math.radians(55)
    dihedral = math.radians(95)
    O3 = (0.0, 0.0, 0.0)
    C3 = (0.0, 0.0, 1.0)
    A3 = (math.sin(beta), 0.0, math.cos(beta))
    B3 = (math.sin(alpha) * math.cos(dihedral), math.sin(alpha) * math.sin(dihedral), math.cos(alpha))
    Ap3 = (A3[0], A3[1], 0.0)
    Bp3 = (B3[0], B3[1], 0.0)

    O, A, B, C = map(project, [O3, A3, B3, C3])
    Ap, Bp = map(project, [Ap3, Bp3])

    # Plane π through O, perpendicular to OC.
    plane3 = [(-1.05, -1.05, 0), (1.20, -1.05, 0), (1.20, 1.05, 0), (-1.05, 1.05, 0)]
    plane2 = [project(p) for p in plane3]
    draw.polygon([px(p) for p in plane2], fill=plane_fill, outline=plane_edge)
    line(draw, plane2 + [plane2[0]], plane_edge, 2)

    # The actual named face regions O-A-C and O-B-C, extended down to A′ and B′
    # so the relationship with the perpendicular section is immediately visible.
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon([px(p) for p in [O, Bp, B, C]], fill=(7, 138, 118, 55), outline=(7, 138, 118, 185))
    od.polygon([px(p) for p in [O, Ap, A, C]], fill=(37, 99, 235, 55), outline=(37, 99, 235, 185))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Named rays and their projections.
    arrow(draw, O, A, blue, 6)
    arrow(draw, O, B, teal, 6)
    arrow(draw, O, C, navy, 6)
    dashed(draw, A, Ap, dashed_color, 2)
    dashed(draw, B, Bp, dashed_color, 2)
    arrow(draw, O, Ap, blue, 7)
    arrow(draw, O, Bp, teal, 7)

    for p, color in [(O, navy), (A, blue), (B, teal), (C, navy), (Ap, blue), (Bp, teal)]:
        draw.ellipse(px((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5)), fill=color)

    # The section angle representing the dihedral angle at edge OC.
    theta_a = math.degrees(math.atan2(Ap[1] - O[1], Ap[0] - O[0]))
    theta_b = math.degrees(math.atan2(Bp[1] - O[1], Bp[0] - O[0]))
    r = 92
    draw.arc(px((O[0] - r, O[1] - r, O[0] + r, O[1] + r)),
             start=theta_b, end=theta_a, fill=orange, width=px(5))

    # Point and segment labels make the trihedral explicit.
    text(draw, (O[0] - 20, O[1] + 35), "O", f_label, navy)
    text(draw, (A[0] + 14, A[1] - 16), "A", f_label, blue)
    text(draw, (B[0] - 26, B[1] - 18), "B", f_label, teal)
    text(draw, (C[0] + 16, C[1] - 10), "C", f_label, navy)
    text(draw, (Ap[0] + 12, Ap[1] + 18), "A′", f_label, blue)
    text(draw, (Bp[0] - 36, Bp[1] + 15), "B′", f_label, teal)

    text(draw, ((O[0] + A[0]) / 2 + 12, (O[1] + A[1]) / 2 - 8), "OA", f_label, blue)
    text(draw, ((O[0] + B[0]) / 2 - 60, (O[1] + B[1]) / 2 - 8), "OB", f_label, teal)
    text(draw, (C[0] + 28, (O[1] + C[1]) / 2), "OC", f_label, navy)
    text(draw, ((O[0] + Ap[0]) / 2, (O[1] + Ap[1]) / 2 + 34), "OA′", f_label, blue, anchor="mm")
    text(draw, ((O[0] + Bp[0]) / 2 - 12, (O[1] + Bp[1]) / 2 + 28), "OB′", f_label, teal, anchor="mm")

    text(draw, (1035, 300), "平面 AOC", f_label, blue)
    text(draw, (405, 380), "平面 BOC", f_label, teal)
    text(draw, (220, 715), "截面 π 与 OC 垂直", f_label, navy)
    text(draw, (O[0], O[1] - 118), "∠A′OB′ = 二面角 C", f_label, orange, anchor="mm")

    # The exact naming correspondence requested by the proof.
    rounded(draw, (1110, 430, 1500, 745), "#FFFFFF", border, radius=16, width=2)
    text(draw, (1140, 462), "三个面角与一个二面角", f_head, navy)
    text(draw, (1140, 520), "α = ∠BOC", f_math, teal)
    text(draw, (1140, 565), "β = ∠COA", f_math, blue)
    text(draw, (1140, 610), "γ = ∠AOB", f_math, violet)
    text(draw, (1140, 670), "C = ∠A′OB′", f_math, orange)
    text(draw, (1140, 710), "（棱 OC 处的二面角）", f_body, muted)

    rounded(draw, (55, 855, 1545, 950), "#EFF6FF", "#9FC2FA", radius=18, width=2)
    text(draw, (90, 887), "向量对应", f_label, navy)
    text(draw, (225, 887), "a = OA,  b = OB,  c = OC ;  a⊥ = OA′,  b⊥ = OB′", f_math, navy)
    text(draw, (90, 928), "结论", f_label, navy)
    text(draw, (225, 928), "cos C = (cos γ − cos α cos β)/(sin α sin β)", f_formula, navy)

    img = img.resize((W, H), Image.Resampling.LANCZOS)
    img.save(output, quality=95)
    print(output)


if __name__ == "__main__":
    main()
