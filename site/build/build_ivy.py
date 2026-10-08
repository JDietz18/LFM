"""Draw an ivy garland as SVG (assets/ivy.svg), in the spirit of the owner's reference:
five-lobed leaves with pale veins, a wavy main stem running left to right, and a few
hanging tendrils with small leaves and curled tips. Deterministic (seeded)."""
import math, random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "ivy.svg"
W, H = 560, 310
rng = random.Random(7)

DARK, MID, LIGHT, VEIN, STEM = "#3E9633", "#52AE3C", "#7FCB55", "#CFEFA9", "#3F8A35"

# ivy leaf, base at (0,0), tip at (0,-70)
LEAF = ("M0 0 C -8 -4 -22 -2 -30 -12 C -38 -22 -34 -34 -26 -34 C -34 -44 -24 -56 -14 -50 "
        "C -10 -60 0 -70 0 -70 C 0 -70 10 -60 14 -50 C 24 -56 34 -44 26 -34 "
        "C 34 -34 38 -22 30 -12 C 22 -2 8 -4 0 0 Z")
VEINS = ("M0 -4 L0 -64 M0 -14 L-20 -46 M0 -14 L20 -46 M0 -8 L-26 -18 M0 -8 L26 -18")


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
            u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])


def bez_tangent(p0, p1, p2, p3, t):
    u = 1 - t
    dx = 3*u*u*(p1[0]-p0[0]) + 6*u*t*(p2[0]-p1[0]) + 3*t*t*(p3[0]-p2[0])
    dy = 3*u*u*(p1[1]-p0[1]) + 6*u*t*(p2[1]-p1[1]) + 3*t*t*(p3[1]-p2[1])
    return math.degrees(math.atan2(dy, dx))


def leaf(x, y, angle, scale, shade):
    """A leaf whose base sits at (x,y), pointing along `angle` (deg, 0 = up)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({angle:.1f}) scale({scale:.2f})">'
            f'<path d="{LEAF}" fill="{shade}"/>'
            f'<path d="{VEINS}" fill="none" stroke="{VEIN}" stroke-width="2" stroke-linecap="round" opacity=".9"/>'
            f'</g>')


def stem_path(pts):
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(0, len(pts) - 1, 3):
        p1, p2, p3 = pts[i+1], pts[i+2], pts[i+3]
        d += f" C {p1[0]:.1f} {p1[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} {p3[0]:.1f} {p3[1]:.1f}"
    return d


parts = []

# ---- main stem: three cubic segments, left to right, gently waving
main = [(34, 66), (110, 26), (165, 124), (230, 76), (295, 28), (370, 124), (425, 66), (455, 40), (485, 80), (500, 68)]
parts.append(f'<path d="{stem_path(main)}" fill="none" stroke="{STEM}" stroke-width="4" stroke-linecap="round"/>')

# ---- leaves along the main stem, alternating sides
leaves = []
for seg in range(3):
    p0, p1, p2, p3 = main[seg*3:seg*3+4]
    for k, t in enumerate((0.12, 0.34, 0.56, 0.78, 0.95)):
        x, y = bez(p0, p1, p2, p3, t)
        tang = bez_tangent(p0, p1, p2, p3, t)
        side = 1 if (seg*5 + k) % 2 == 0 else -1
        ang = tang + 90 * side + rng.uniform(-18, 18) + 90   # +90: leaf path points "up" at 0
        sc = rng.uniform(0.62, 1.0)
        shade = rng.choice((DARK, MID, MID, LIGHT))
        leaves.append((sc, leaf(x, y, ang, sc, shade)))

# ---- hanging tendrils with small leaves and a curl at the tip
tendrils = [((165, 122), (155, 172), (190, 216), (175, 262)),
            ((300, 46), (305, 112), (280, 152), (300, 196)),
            ((430, 62), (460, 112), (440, 162), (470, 214)),
            ((80, 50), (60, 94), (90, 128), (75, 162))]
for p0, p1, p2, p3 in tendrils:
    parts.append(f'<path d="{stem_path([p0, p1, p2, p3])}" fill="none" stroke="{STEM}" stroke-width="2.4" stroke-linecap="round"/>')
    ex, ey = p3
    tang = bez_tangent(p0, p1, p2, p3, 1.0)
    curl = (f'<path d="M{ex:.1f} {ey:.1f} c 6 8 -2 16 -8 10 c -4 -5 2 -10 5 -6" fill="none" stroke="{STEM}" stroke-width="1.8" stroke-linecap="round"/>')
    parts.append(curl)
    for t in (0.3, 0.62, 0.88):
        x, y = bez(p0, p1, p2, p3, t)
        tang = bez_tangent(p0, p1, p2, p3, t)
        side = rng.choice((-1, 1))
        leaves.append((0.4, leaf(x, y, tang + 90*side + 90 + rng.uniform(-20, 20), rng.uniform(0.3, 0.48), rng.choice((MID, LIGHT)))))

# small leaves first so big ones overlap them
leaves.sort(key=lambda s: s[0])
parts.extend(l for _, l in leaves)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true">\n'
       + "\n".join(parts) + "\n</svg>\n")
OUT.write_text(svg, encoding="utf-8")
print("wrote", OUT, len(svg), "bytes,", len(leaves), "leaves")
