from pathlib import Path
import math
import sys

from PIL import Image, ImageDraw, ImageFont


S = 2
W, H = 1600, 960


def u(v):
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
            return ImageFont.truetype(path, u(size))
    return ImageFont.load_default()


def text(draw, xy, value, fnt, fill, anchor="la"):
    draw.text(u(xy), value, font=fnt, fill=fill, anchor=anchor)


def line(draw, points, fill, width=3):
    draw.line([u(p) for p in points], fill=fill, width=u(width), joint="curve")


def arrow(draw, start, end, fill, width=5, head=14):
    line(draw, [start, end], fill, width)
    t = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - head * math.cos(t - math.pi / 6), end[1] - head * math.sin(t - math.pi / 6))
    p2 = (end[0] - head * math.cos(t + math.pi / 6), end[1] - head * math.sin(t + math.pi / 6))
    draw.polygon([u(end), u(p1), u(p2)], fill=fill)


def dashed(draw, start, end, fill, width=2, dash=10, gap=8):
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
    draw.rounded_rectangle(u(box), radius=u(radius), fill=fill, outline=outline, width=u(width))


def arc(draw, origin, radius, start, end, fill, width=4):
    box = (origin[0] - radius, origin[1] - radius, origin[0] + radius, origin[1] + radius)
    draw.arc(u(box), start=start, end=end, fill=fill, width=u(width))


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: draw_tetrahedron_then_section.py OUTPUT.png")
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", u((W, H)), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    navy = "#203047"
    muted = "#607087"
    border = "#CFDAE8"
    panel = "#F8FAFD"
    blue = "#2563EB"
    teal = "#078A76"
    orange = "#F59E0B"
    violet = "#7C3AED"
    gray_edge = "#607087"
    plane_fill = "#EDF4FF"
    plane_edge = "#8CB5F4"

    f_title = font(32, bold=True)
    f_sub = font(18)
    f_panel = font(23, bold=True)
    f_body = font(17)
    f_small = font(15)
    f_label = font(19, bold=True)
    f_math = font(19, math_font=True)

    text(draw, (65, 45), "先认三棱锥，再看垂直截面", f_title, navy)
    text(draw, (65, 92), "第一步只认清 O-ABC 和三条棱；第二步再聚焦棱 OC 处的二面角。", f_sub, muted)
    text(draw, (1535, 96), "示意图不按比例", f_small, muted, anchor="ra")

    rounded(draw, (55, 135, 745, 800), panel, border)
    rounded(draw, (855, 135, 1545, 800), panel, border)
    text(draw, (85, 170), "① 三棱锥 O-ABC", f_panel, navy)
    text(draw, (885, 170), "② 聚焦棱 OC，作垂直截面", f_panel, navy)

    # Step 1: the complete tetrahedron, before any projection is introduced.
    O = (365, 650)
    C = (365, 245)
    A = (650, 420)
    B = (125, 405)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon([u(p) for p in [O, A, C]], fill=(37, 99, 235, 35))
    od.polygon([u(p) for p in [O, B, C]], fill=(7, 138, 118, 35))
    od.polygon([u(p) for p in [O, A, B]], fill=(124, 58, 237, 22))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    line(draw, [A, C], gray_edge, 3)
    line(draw, [B, C], gray_edge, 3)
    dashed(draw, A, B, gray_edge, 2)
    arrow(draw, O, A, blue, 6)
    arrow(draw, O, B, teal, 6)
    arrow(draw, O, C, navy, 6)

    for p, color in [(O, navy), (A, blue), (B, teal), (C, navy)]:
        draw.ellipse(u((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5)), fill=color)
    text(draw, (O[0] - 18, O[1] + 25), "O", f_label, navy)
    text(draw, (A[0] + 14, A[1] - 12), "A", f_label, blue)
    text(draw, (B[0] - 25, B[1] - 12), "B", f_label, teal)
    text(draw, (C[0] + 14, C[1] - 10), "C", f_label, navy)
    text(draw, (520, 545), "OA", f_label, blue)
    text(draw, (210, 535), "OB", f_label, teal)
    text(draw, (386, 445), "OC", f_label, navy)

    # Three face angles at vertex O; the outer arc is γ, the two inner ones are α,β.
    theta_a = math.degrees(math.atan2(A[1] - O[1], A[0] - O[0]))
    theta_b = math.degrees(math.atan2(B[1] - O[1], B[0] - O[0]))
    theta_c = math.degrees(math.atan2(C[1] - O[1], C[0] - O[0]))
    arc(draw, O, 52, theta_b, theta_c, teal, 4)
    arc(draw, O, 66, theta_c, theta_a, blue, 4)
    arc(draw, O, 103, theta_b, theta_a, violet, 3)
    text(draw, (326, 560), "α", f_math, teal, anchor="mm")
    text(draw, (410, 555), "β", f_math, blue, anchor="mm")
    text(draw, (365, 520), "γ", f_math, violet, anchor="mm")

    rounded(draw, (100, 705, 700, 775), "#FFFFFF", border, radius=14, width=2)
    text(draw, (125, 731), "α = ∠BOC", f_math, teal)
    text(draw, (300, 731), "β = ∠COA", f_math, blue)
    text(draw, (485, 731), "γ = ∠AOB", f_math, violet)

    # Transition: now and only now introduce the perpendicular section.
    arrow(draw, (760, 430), (840, 430), orange, 5, 14)
    text(draw, (800, 392), "只看棱 OC", f_small, orange, anchor="mm")

    # Step 2: same named rays, with the perpendicular section and projections.
    O2 = (1240, 655)
    C2 = (1240, 230)
    A2 = (1430, 315)
    B2 = (1050, 320)
    Ap = (1430, 535)
    Bp = (1050, 510)
    plane = [(940, 540), (1320, 450), (1515, 585), (1135, 750)]
    draw.polygon([u(p) for p in plane], fill=plane_fill, outline=plane_edge)
    line(draw, plane + [plane[0]], plane_edge, 2)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon([u(p) for p in [O2, Bp, B2, C2]], fill=(7, 138, 118, 48), outline=(7, 138, 118, 165))
    od.polygon([u(p) for p in [O2, Ap, A2, C2]], fill=(37, 99, 235, 48), outline=(37, 99, 235, 165))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    arrow(draw, O2, A2, blue, 5)
    arrow(draw, O2, B2, teal, 5)
    arrow(draw, O2, C2, navy, 6)
    dashed(draw, A2, Ap, gray_edge, 2)
    dashed(draw, B2, Bp, gray_edge, 2)
    arrow(draw, O2, Ap, blue, 7)
    arrow(draw, O2, Bp, teal, 7)

    for p, color in [(O2, navy), (A2, blue), (B2, teal), (C2, navy), (Ap, blue), (Bp, teal)]:
        draw.ellipse(u((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5)), fill=color)
    text(draw, (O2[0] - 18, O2[1] + 24), "O", f_label, navy)
    text(draw, (A2[0] + 12, A2[1] - 12), "A", f_label, blue)
    text(draw, (B2[0] - 26, B2[1] - 12), "B", f_label, teal)
    text(draw, (C2[0] + 14, C2[1] - 10), "C", f_label, navy)
    text(draw, (Ap[0] + 12, Ap[1] + 15), "A′", f_label, blue)
    text(draw, (Bp[0] - 35, Bp[1] + 15), "B′", f_label, teal)
    text(draw, (1270, 425), "OC", f_label, navy)
    text(draw, (1370, 620), "OA′", f_label, blue)
    text(draw, (1080, 600), "OB′", f_label, teal)
    text(draw, (875, 690), "截面 π", f_body, muted)

    ta = math.degrees(math.atan2(Ap[1] - O2[1], Ap[0] - O2[0]))
    tb = math.degrees(math.atan2(Bp[1] - O2[1], Bp[0] - O2[0]))
    arc(draw, O2, 88, tb, ta, orange, 5)
    text(draw, (1240, 540), "C", f_math, orange, anchor="mm")

    rounded(draw, (905, 705, 1500, 775), "#FFFFFF", border, radius=14, width=2)
    text(draw, (930, 730), "A′、B′ 分别是 A、B 在 π 内的正投影", f_body, navy)
    text(draw, (930, 760), "∠A′OB′ = 棱 OC 处的二面角 C", f_body, orange)

    rounded(draw, (55, 835, 1545, 925), "#EFF6FF", "#9FC2FA", radius=18, width=2)
    text(draw, (90, 865), "观察顺序", f_label, navy)
    text(draw, (225, 865), "三棱锥 O-ABC", f_label, navy)
    arrow(draw, (405, 875), (515, 875), orange, 4, 12)
    text(draw, (550, 865), "聚焦棱 OC 的两个侧面", f_label, navy)
    arrow(draw, (835, 875), (945, 875), orange, 4, 12)
    text(draw, (980, 865), "垂直截面中得到 ∠A′OB′ = C", f_label, navy)
    text(draw, (225, 905), "先建立空间对象，再引入投影；不要反过来。", f_body, muted)

    img = img.resize((W, H), Image.Resampling.LANCZOS)
    img.save(output, quality=95)
    print(output)


if __name__ == "__main__":
    main()
