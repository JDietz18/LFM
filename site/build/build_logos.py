"""Build the Little Foot Munchkins logo set as outlined SVGs.

Run from LFM/site/build:   python -I build_logos.py
Inputs : fonts/GreatVibes-Regular.ttf, fonts/CormorantGaramond.ttf (OFL, Google Fonts repo)
Outputs: ../assets/*.svg  (two directions x three inks, plus icons + favicon)

Text is shaped with HarfBuzz so the script's contextual connectors apply,
then each glyph is traced to a path, so the SVGs need no font installed.
"""
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
OUT = HERE.parent / "assets"
OUT.mkdir(exist_ok=True)

INKS = {"ink": "#3A3532", "teal": "#2E8B8B", "white": "#FBF8F3"}
BLUSH, SAGE = "#F0CFC0", "#9DAE98"


class Face:
    def __init__(self, path, wght=None):
        self.tt = TTFont(path)
        if wght is not None and "fvar" in self.tt:
            self.tt = instantiateVariableFont(self.tt, {"wght": wght})
        self.upm = self.tt["head"].unitsPerEm
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        blob = hb.Blob.from_file_path(str(path)) if wght is None else None
        if blob is None:
            import io
            buf = io.BytesIO(); self.tt.save(buf); blob = hb.Blob(buf.getvalue())
        self.hbfont = hb.Font(hb.Face(blob))

    def shape(self, text, size, features=None, tracking=0):
        """Return (path_d, width) for text at `size` px, baseline at y=0, x from 0."""
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, features or {})
        scale = size / self.upm
        pen = SVGPathPen(self.glyphset, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        x = 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = self.order[info.codepoint]
            tp = TransformPen(pen, (scale, 0, 0, -scale, (x + pos.x_offset) * scale, -pos.y_offset * scale))
            self.glyphset[name].draw(tp)
            x += pos.x_advance + tracking * self.upm / size
        return pen.getCommands(), x * scale


script = Face(FONTS / "GreatVibes-Regular.ttf")
serif = Face(FONTS / "CormorantGaramond.ttf", wght=600)


def svg(w, h, body, name):
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
           f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="Little Foot Munchkins">\n{body}\n</svg>\n')
    (OUT / name).write_text(doc, encoding="utf-8")
    print("wrote", name)


# ---------- shared drawings ----------

def vine(x, y, length, flip=False, stroke="#3A3532", leaf=SAGE):
    """A thin stem with three leaves, running from (x,y) outward `length` px.
    flip mirrors it for the left side. Leaves are filled, stem is stroked."""
    s = -1 if flip else 1
    g = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s} 1)" fill="none" stroke="{stroke}" stroke-width="2.4" stroke-linecap="round">']
    # stem with a gentle wave, ending in a small curl; pathLength lets CSS draw it on
    g.append(f'<path class="vine-stem" pathLength="1" d="M0 0 C {length*0.35:.1f} -8 {length*0.7:.1f} 8 {length:.1f} 0 '
             f'C {length+8:.1f} -4 {length+10:.1f} -10 {length+4:.1f} -11"/>')
    g.append('</g>')
    leaves = []
    for t, side in ((0.22, -1), (0.5, 1), (0.78, -1)):
        lx = x + s * t * length
        # y on the cubic with control points 0, -8, 8, 0
        ly = y + 3 * (1 - t) ** 2 * t * -8 + 3 * (1 - t) * t ** 2 * 8
        ang = (-40 if side < 0 else 40) * s
        leaves.append(
            f'<g transform="translate({lx:.1f} {ly:.1f}) rotate({ang}) scale({s} 1)"><g class="vine-leaf">'
            f'<path fill="{leaf}" d="M0 0 C 6 -12 16 -14 24 -7 C 16 2 6 3 0 0 Z"/>'
            f'<path fill="none" stroke="{stroke}" stroke-width="1" d="M1 -0.5 C 8 -4 14 -6 22 -7"/></g></g>')
    return "\n".join(g + leaves)


def paw(cx, cy, r, fill):
    """Paw print: one pad plus four toes, built from ellipses so it scales cleanly."""
    pad = f'<ellipse cx="{cx}" cy="{cy + r*0.25:.1f}" rx="{r*0.62:.1f}" ry="{r*0.5:.1f}" fill="{fill}"/>'
    toes = []
    for dx, dy, rx, ry, rot in ((-0.72, -0.35, 0.22, 0.3, -25), (-0.26, -0.68, 0.22, 0.3, -8),
                                (0.26, -0.68, 0.22, 0.3, 8), (0.72, -0.35, 0.22, 0.3, 25)):
        toes.append(f'<ellipse cx="{cx + dx*r:.1f}" cy="{cy + dy*r:.1f}" rx="{rx*r:.1f}" ry="{ry*r:.1f}" '
                    f'transform="rotate({rot} {cx + dx*r:.1f} {cy + dy*r:.1f})" fill="{fill}"/>')
    return pad + "\n" + "\n".join(toes)


# Munchkin silhouette, side view facing left, built from clean primitives so it
# stays crisp at favicon size: round head, two ears, long low body, four short
# legs, and a thick plume tail. Box is 240x150 with feet on y=144.
def munchkin(col):
    return (f'<g fill="{col}" stroke="{col}" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M 196 96 C 214 90 226 72 226 52 C 226 40 222 30 216 24" fill="none" stroke-width="22"/>'
            '<path d="M 216 24 C 212 20 206 20 204 26" fill="none" stroke-width="13"/>'
            '<rect x="36" y="104" width="18" height="40" rx="8"/><rect x="62" y="104" width="18" height="40" rx="8"/>'
            '<rect x="150" y="104" width="18" height="40" rx="8"/><rect x="176" y="104" width="18" height="40" rx="8"/>'
            '<ellipse cx="118" cy="98" rx="86" ry="30"/><circle cx="54" cy="86" r="26"/><circle cx="46" cy="58" r="27"/>'
            '<path d="M 28 40 L 22 14 C 32 20 40 26 44 32 Z"/><path d="M 62 36 L 70 10 C 62 18 54 24 50 32 Z"/>'
            '</g>')


# ---------- Direction A: refined script wordmark ----------

def logo_a_wordmark(ink):
    col = INKS[ink]
    leaf = SAGE if ink != "white" else "#CBD7C6"
    d, w = script.shape("Little Foot Munchkins", 96)
    W, H = w + 2 * 150, 170
    x0 = (W - w) / 2
    body = [f'<path class="wm-text" fill="{col}" transform="translate({x0:.1f} 112)" d="{d}"/>',
            f'<g class="vine vine-l">{vine(x0 - 18, 104, 118, flip=True, stroke=col, leaf=leaf)}</g>',
            f'<g class="vine vine-r">{vine(x0 + w + 18, 104, 118, stroke=col, leaf=leaf)}</g>']
    svg(W, H, "\n".join(body), f"logo-a-wordmark-{ink}.svg")


def logo_a_monogram(ink):
    col = INKS[ink]
    d, w = script.shape("L.F.M", 140)
    W, H = w + 60, 190
    svg(W, H, f'<path fill="{col}" transform="translate(30 140)" d="{d}"/>', f"logo-a-monogram-{ink}.svg")


def logo_a_icon():
    body = [f'<circle cx="64" cy="64" r="62" fill="{INKS["teal"]}"/>', paw(64, 66, 36, INKS["white"])]
    svg(128, 128, "\n".join(body), "logo-a-icon.svg")


# ---------- Direction B: Munchkin mark + two-tier lockup ----------

def logo_b_lockup(ink):
    col = INKS[ink]
    top_d, top_w = serif.shape("LITTLE FOOT", 46, tracking=9)
    bot_d, bot_w = script.shape("Munchkins", 92)
    W = max(top_w, bot_w, 240) + 80
    H = 330
    cx = W / 2
    body = [f'<g transform="translate({cx-114:.1f} 14) scale(0.95)">{munchkin(col)}</g>',
            f'<path fill="{col}" transform="translate({cx - top_w/2:.1f} 210)" d="{top_d}"/>',
            f'<path fill="{col}" transform="translate({cx - bot_w/2:.1f} 300)" d="{bot_d}"/>']
    svg(W, H, "\n".join(body), f"logo-b-lockup-{ink}.svg")


def logo_b_icon():
    body = [f'<circle cx="64" cy="64" r="62" fill="{INKS["teal"]}"/>',
            f'<g transform="translate(14 30) scale(0.42)">{munchkin(INKS["white"])}</g>']
    svg(128, 128, "\n".join(body), "logo-b-icon.svg")


def ornament():
    """Heading ornament: two short vines meeting at a centre point, same leaves as the logo."""
    W, H = 150, 32
    body = [f'<g class="vine vine-l">{vine(W/2 - 3, 18, 52, flip=True, stroke=INKS["ink"], leaf=SAGE)}</g>',
            f'<g class="vine vine-r">{vine(W/2 + 3, 18, 52, stroke=INKS["ink"], leaf=SAGE)}</g>',
            f'<circle cx="{W/2}" cy="18" r="2.2" fill="{INKS["ink"]}"/>']
    svg(W, H, "\n".join(body), "ornament.svg")


def favicon():
    body = [f'<rect width="64" height="64" rx="14" fill="{INKS["teal"]}"/>', paw(32, 33, 18, INKS["white"])]
    svg(64, 64, "\n".join(body), "favicon.svg")


if __name__ == "__main__":
    for ink in INKS:
        logo_a_wordmark(ink); logo_a_monogram(ink); logo_b_lockup(ink)
    logo_a_icon(); logo_b_icon(); favicon(); ornament()
