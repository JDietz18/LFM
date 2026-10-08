"""Ivy generator. Four variations share one leaf and one growth model:

  garland(seed)  - wide drape, hangs from the hero's top-left corner
  climber(seed)  - rises from the footer's bottom-right corner
  sprig(...)     - short flourish for the wordmark (used by build_logos.py)
  ornament       - two mirrored sprigs (build_logos.py composes it)

Every stem is emitted with pathLength="1" and a `--len` duration; every leaf
wrapper carries a `--d` start time, so CSS can draw the stem on and pop the
leaves in order as the tip passes them. Run as a script to write
assets/ivy-garland.svg and assets/ivy-climber.svg.
"""
import math, random
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

GREEN = {"leaf": ("#3E9633", "#52AE3C", "#52AE3C", "#7FCB55"), "vein": "#CFEFA9", "stem": "#3F8A35"}

# five-lobed ivy leaf, base at (0,0), tip at (0,-70); bbox x -38..38, y -70..0
LEAF = ("M0 0 C -8 -4 -22 -2 -30 -12 C -38 -22 -34 -34 -26 -34 C -34 -44 -24 -56 -14 -50 "
        "C -10 -60 0 -70 0 -70 C 0 -70 10 -60 14 -50 C 24 -56 34 -44 26 -34 "
        "C 34 -34 38 -22 30 -12 C 22 -2 8 -4 0 0 Z")
VEINS = "M0 -4 L0 -64 M0 -14 L-20 -46 M0 -14 L20 -46 M0 -8 L-26 -18 M0 -8 L26 -18"


def palette(leaf=None, vein=None, stem=None):
    """Single-ink palette for logo variants, or the green default."""
    if leaf is None:
        return GREEN
    return {"leaf": (leaf,), "vein": vein, "stem": stem or leaf}


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
            u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])


def tangent(p0, p1, p2, p3, t):
    u = 1 - t
    dx = 3*u*u*(p1[0]-p0[0]) + 6*u*t*(p2[0]-p1[0]) + 3*t*t*(p3[0]-p2[0])
    dy = 3*u*u*(p1[1]-p0[1]) + 6*u*t*(p2[1]-p1[1]) + 3*t*t*(p3[1]-p2[1])
    return math.degrees(math.atan2(dy, dx))


def path_d(pts):
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(0, len(pts) - 1, 3):
        p1, p2, p3 = pts[i+1], pts[i+2], pts[i+3]
        d += f" C {p1[0]:.1f} {p1[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} {p3[0]:.1f} {p3[1]:.1f}"
    return d


def leaf_el(x, y, angle, scale, fill, vein, d, extra_cls=""):
    cls = ("lf " + extra_cls).strip()
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({angle:.1f}) scale({scale:.2f})">'
            f'<g class="{cls}" style="--d:{d:.2f}s">'
            f'<path d="{LEAF}" fill="{fill}"/>'
            f'<path d="{VEINS}" fill="none" stroke="{vein}" stroke-width="2" stroke-linecap="round" opacity=".9"/>'
            f'</g></g>')


def stem_el(d, width, color, start, length_s, extra_cls=""):
    cls = ("st " + extra_cls).strip()
    return (f'<path class="{cls}" pathLength="1" style="--d:{start:.2f}s;--len:{length_s:.2f}s" d="{d}" '
            f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')


def curl_el(x, y, color, start, flip=1):
    return (f'<path class="st curl" pathLength="1" style="--d:{start:.2f}s;--len:.35s" '
            f'd="M{x:.1f} {y:.1f} c {6*flip} 8 {-2*flip} 16 {-8*flip} 10 c {-4*flip} -5 {2*flip} -10 {5*flip} -6" '
            f'fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>')


# ---------------------------------------------------------------- vine builder
def vine(main, tendrils, rng, pal, leaf_t=(0.12, 0.34, 0.56, 0.78, 0.95), main_s=1.6,
         leaf_scale=(0.62, 1.0), main_w=4, tendril_w=2.4, t0=0.1):
    """main: list of 3k+1 points (cubic chain). tendrils: list of (tg, (dx1,dy1),(dx2,dy2),(dx3,dy3))
    where tg is the global 0..1 position on the main stem where the tendril attaches and the
    offsets describe its three control points relative to the attach point."""
    segs = (len(main) - 1) // 3
    parts, leaves = [], []
    parts.append(stem_el(path_d(main), main_w, pal["stem"], t0, main_s))

    def at(tg):
        seg = min(int(tg * segs), segs - 1)
        t = tg * segs - seg
        p0, p1, p2, p3 = main[seg*3:seg*3+4]
        return bez(p0, p1, p2, p3, t), tangent(p0, p1, p2, p3, t)

    n = 0
    for seg in range(segs):
        for t in leaf_t:
            tg = (seg + t) / segs
            (x, y), tang = at(tg)
            side = 1 if n % 2 == 0 else -1
            n += 1
            ang = tang + 90 * side + 90 + rng.uniform(-18, 18)
            sc = rng.uniform(*leaf_scale)
            leaves.append((sc, leaf_el(x, y, ang, sc, rng.choice(pal["leaf"]), pal["vein"], t0 + main_s * tg)))

    for tg, o1, o2, o3 in tendrils:
        (x, y), _ = at(tg)
        pts = [(x, y), (x + o1[0], y + o1[1]), (x + o2[0], y + o2[1]), (x + o3[0], y + o3[1])]
        start = t0 + main_s * tg + 0.1
        parts.append(stem_el(path_d(pts), tendril_w, pal["stem"], start, 0.6))
        ex, ey = pts[3]
        parts.append(curl_el(ex, ey, pal["stem"], start + 0.6, flip=rng.choice((-1, 1))))
        for t in (0.3, 0.62, 0.88):
            lx, ly = bez(*pts, t)
            tang = tangent(*pts, t)
            side = rng.choice((-1, 1))
            leaves.append((0.4, leaf_el(lx, ly, tang + 90*side + 90 + rng.uniform(-20, 20),
                                        rng.uniform(0.3, 0.48), rng.choice(pal["leaf"][1:]), pal["vein"],
                                        start + 0.6 * t)))
    leaves.sort(key=lambda s: s[0])          # small leaves first so big ones overlap them
    parts.extend(l for _, l in leaves)
    return "\n".join(parts)


def garland(seed=7, pal=GREEN):
    """Wide drape, 560x310, growing left to right with four hanging tendrils."""
    rng = random.Random(seed)
    main = [(34, 66), (110, 26), (165, 124), (230, 76), (295, 28), (370, 124), (425, 66), (455, 40), (485, 80), (500, 68)]
    tendrils = [(0.34, (-10, 50), (25, 94), (10, 140)),
                (0.60, (5, 66), (-20, 106), (0, 150)),
                (0.85, (30, 50), (10, 100), (40, 152)),
                (0.08, (-20, 44), (10, 78), (-5, 112))]
    return 560, 310, vine(main, tendrils, rng, pal)


def climber(seed=11, pal=GREEN):
    """Rises from the bottom-right corner, 340x330, growing upward."""
    rng = random.Random(seed)
    main = [(318, 326), (300, 260), (330, 200), (280, 150), (230, 100), (250, 50), (190, 30)]
    tendrils = [(0.3, (-40, 10), (-70, -20), (-95, 10)),
                (0.72, (-30, 30), (-10, 70), (-40, 100))]
    return 340, 330, vine(main, tendrils, rng, pal, leaf_t=(0.1, 0.32, 0.55, 0.78, 0.96),
                          main_s=1.4, leaf_scale=(0.55, 0.9), t0=0.05)


def sprig(length=118, flip=False, pal=GREEN, leaf_scale=0.34, seed=3, t0=0.0, total=0.9):
    """Short flourish from (0,0) outward along +x: wavy stem, three leaves, a curl.
    Returns a <g> ready to translate into place. flip mirrors it for the left side.
    Classes match the page's wordmark hooks: vine-stem / vine-leaf."""
    rng = random.Random(seed)
    L = length
    pts = [(0, 0), (L*0.35, -8), (L*0.7, 8), (L, 0)]
    parts = [stem_el(path_d(pts), 2.4, pal["stem"], t0, total * 0.75, extra_cls="vine-stem")]
    parts.append(curl_el(L, 0, pal["stem"], t0 + total * 0.75, flip=1))
    for k, (t, side) in enumerate(((0.22, -1), (0.5, 1), (0.78, -1))):
        x, y = bez(*pts, t)
        tang = tangent(*pts, t)
        ang = tang + 90 * side + 90 + rng.uniform(-10, 10)
        parts.append(leaf_el(x, y, ang, leaf_scale * rng.uniform(0.9, 1.1), pal["leaf"][k % len(pal["leaf"])],
                             pal["vein"], t0 + total * 0.75 * t, extra_cls="vine-leaf"))
    s = -1 if flip else 1
    return f'<g transform="scale({s} 1)">' + "".join(parts) + "</g>"


def wrap(w, h, body, cls="ivy"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'class="{cls}" aria-hidden="true">\n{body}\n</svg>\n')


if __name__ == "__main__":
    for name, fn in (("ivy-garland", garland), ("ivy-climber", climber)):
        w, h, body = fn()
        (ASSETS / f"{name}.svg").write_text(wrap(w, h, body), encoding="utf-8")
        print("wrote", name, w, h, body.count('class="lf'), "leaves")
    old = ASSETS / "ivy.svg"
    if old.exists():
        old.unlink(); print("removed ivy.svg")
