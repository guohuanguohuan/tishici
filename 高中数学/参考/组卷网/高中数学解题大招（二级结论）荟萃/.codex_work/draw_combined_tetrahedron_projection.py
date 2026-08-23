from pathlib import Path
import math
import sys

from PIL import Image, ImageDraw, ImageFont


S = 2
W, H = 1600, 960


def z(v):
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
            return ImageFont.truetype(path, z(size))
    return ImageFont.load_default()


def text(draw, xy, value, fnt, fill, anchor="la"):
    draw.text(z(xy), value, font=fnt, fill=fill, anchor=anchor)


def line(draw, points, fill, width=3):
    draw.line([z(p) for p in points], fill=fill, width=z(width), joint="curve")


def arrow(draw, start, end, fill, width=5, head=14):
    line(draw, [start, end], fill, width)
    t = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - head * math.cos(t - math.pi / 6), end[1] - head * math.sin(t - math.pi / 6))
    p2 = (end[0] - head * math.cos(t + math.pi / 6), end[1] - head * math.sin(t + math.pi / 6))
    draw.polygon([z(end), z(p1), z(p2)], fill=fill)


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
    draw.rounded_rectangle(z(box), radius=z(radius), fill=fill, outline=outline, width=z(width))


def right_angle_marker(draw, origin, ray1_end, ray2_end, fill, size=30, width=3):
    """Draw a perspective right-angle corner between two rays from origin."""
    def unit(end):
        dx, dy = end[0] - origin[0], end[1] - origin[1]
        length = math.hypot(dx, dy)
        return dx / length, dy / length

    u1 = unit(ray1_end)
    u2 = unit(ray2_end)
    p1 = (origin[0] + size * u1[0], origin[1] + size * u1[1])
    p2 = (p1[0] + size * u2[0], p1[1] + size * u2[1])
    p3 = (origin[0] + size * u2[0], origin[1] + size * u2[1])
    line(draw, [p1, p2, p3], fill, width)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: draw_combined_tetrahedron_projection.py OUTPUT.png")
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", z((W, H)), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    navy = "#203047"
    muted = "#607087"
    border = "#CFDAE8"
    panel = "#F8FAFD"
    blue = "#2563EB"
    teal = "#078A76"
    orange = "#F59E0B"
    violet = "#7C3AED"
    edge = "#64748B"
    plane_fill = "#EDF4FF"
    plane_edge = "#8CB5F4"

    f_title = font(32, bold=True)
    f_sub = font(18)
    f_head = font(22, bold=True)
    f_body = font(17)
    f_small = font(15)
    f_label = font(19, bold=True)
    f_math = font(19, math_font=True)

    text(draw, (65, 45), "三棱锥 O-ABC 与垂直截面（合并图）", f_title, navy)
    text(draw, (65, 92), "先看完整三棱锥，再在同一图中读取投影 A′、B′ 与棱 OC 处的二面角。", f_sub, muted)
    text(draw, (1535, 96), "示意图不按比例", f_small, muted, anchor="ra")

    rounded(draw, (55, 135, 1545, 800), panel, border)

    # One common spatial model.
    O = (770, 665)
    C = (770, 220)
    A = (1165, 345)
    B = (405, 340)
    Ap = (1165, 585)
    Bp = (405, 510)
    plane = [(245, 555), (930, 420), (1395, 615), (710, 805)]

    # Draw the perpendicular screen first, behind the tetrahedron.
    draw.polygon([z(p) for p in plane], fill=plane_fill, outline=plane_edge)
    line(draw, plane + [plane[0]], plane_edge, 2)

    # Actual tetrahedron faces. These are visually stronger than the screen.
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon([z(p) for p in [O, A, C]], fill=(37, 99, 235, 45))
    od.polygon([z(p) for p in [O, B, C]], fill=(7, 138, 118, 45))
    od.polygon([z(p) for p in [O, A, B]], fill=(124, 58, 237, 22))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # All six tetrahedron edges: AB is the hidden edge.
    line(draw, [A, C], edge, 3)
    line(draw, [B, C], edge, 3)
    dashed(draw, A, B, edge, 2)
    arrow(draw, O, A, blue, 6)
    arrow(draw, O, B, teal, 6)
    arrow(draw, O, C, navy, 6)

    # Projection construction, subordinate but still readable.
    dashed(draw, A, Ap, edge, 2)
    dashed(draw, B, Bp, edge, 2)
    arrow(draw, O, Ap, blue, 7)
    arrow(draw, O, Bp, teal, 7)

    for p, color in [(O, navy), (A, blue), (B, teal), (C, navy), (Ap, blue), (Bp, teal)]:
        draw.ellipse(z((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5)), fill=color)

    # Plane angle corresponding to the dihedral angle.
    theta_a = math.degrees(math.atan2(Ap[1] - O[1], Ap[0] - O[0]))
    theta_b = math.degrees(math.atan2(Bp[1] - O[1], Bp[0] - O[0]))
    r = 105
    draw.arc(z((O[0] - r, O[1] - r, O[0] + r, O[1] + r)),
             start=theta_b, end=theta_a, fill=orange, width=z(5))
    right_angle_marker(draw, O, C, Ap, blue, size=31, width=3)
    right_angle_marker(draw, O, C, Bp, teal, size=43, width=3)

    # Named points and rays.
    text(draw, (O[0] - 20, O[1] + 34), "O", f_label, navy)
    text(draw, (A[0] + 14, A[1] - 12), "A", f_label, blue)
    text(draw, (B[0] - 26, B[1] - 12), "B", f_label, teal)
    text(draw, (C[0] + 14, C[1] - 10), "C", f_label, navy)
    text(draw, (Ap[0] + 14, Ap[1] + 15), "A′", f_label, blue)
    text(draw, (Bp[0] - 38, Bp[1] + 15), "B′", f_label, teal)
    text(draw, (980, 520), "OA", f_label, blue)
    text(draw, (535, 520), "OB", f_label, teal)
    text(draw, (790, 425), "OC", f_label, navy)
    text(draw, (1000, 640), "OA′ ⊥ OC", f_math, blue)
    text(draw, (500, 600), "OB′ ⊥ OC", f_math, teal)
    text(draw, (1115, 470), "AA′ ∥ OC", f_small, muted)
    text(draw, (325, 445), "BB′ ∥ OC", f_small, muted)
    text(draw, (275, 690), "截面 π 与 OC 垂直", f_label, navy)
    text(draw, (275, 730), "OA′、OB′ 在 π 内，所以都垂直于 OC", f_body, muted)
    text(draw, (770, 535), "∠A′OB′ = 二面角 C", f_label, orange, anchor="mm")

    # Compact reading key; the drawing remains one single spatial object.
    rounded(draw, (1215, 235, 1500, 520), "#FFFFFF", border, radius=16, width=2)
    text(draw, (1245, 268), "角的对应关系", f_head, navy)
    text(draw, (1245, 323), "α = ∠BOC", f_math, teal)
    text(draw, (1245, 365), "β = ∠COA", f_math, blue)
    text(draw, (1245, 407), "γ = ∠AOB", f_math, violet)
    text(draw, (1245, 465), "C = ∠A′OB′", f_math, orange)

    rounded(draw, (950, 690, 1500, 770), "#FFFFFF", border, radius=14, width=2)
    text(draw, (975, 717), "A′、B′ 是 A、B 在 π 内的正投影", f_body, navy)
    text(draw, (975, 750), "OA′、OB′ 是两个侧面与 π 的交线方向", f_body, muted)

    rounded(draw, (55, 835, 1545, 925), "#EFF6FF", "#9FC2FA", radius=18, width=2)
    text(draw, (90, 867), "读图主线", f_label, navy)
    text(draw, (225, 867), "三棱锥 O-ABC", f_label, navy)
    arrow(draw, (410, 878), (520, 878), orange, 4, 12)
    text(draw, (555, 867), "棱 OC 的两个侧面", f_label, navy)
    arrow(draw, (790, 878), (900, 878), orange, 4, 12)
    text(draw, (935, 867), "垂直截面中的 ∠A′OB′ 就是二面角 C", f_label, navy)
    text(draw, (225, 907), "所有对象都保留在同一幅空间图中。", f_body, muted)

    img = img.resize((W, H), Image.Resampling.LANCZOS)
    img.save(output, quality=95)
    print(output)


if __name__ == "__main__":
    main()
