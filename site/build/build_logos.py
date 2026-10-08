"""Build the LittleFoot Munchkins logo set as outlined SVGs.

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
import sys; sys.path.insert(0, str(HERE))
import build_ivy
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
           f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="LittleFoot Munchkins">\n{body}\n</svg>\n')
    (OUT / name).write_text(doc, encoding="utf-8")
    print("wrote", name)


# ---------- shared drawings ----------

def vine(x, y, length, flip=False, stroke="#3A3532", leaf=None, pal=None, leaf_scale=0.34, seed=3):
    """Ivy sprig flourish from (x,y) outward `length` px; flip mirrors it for the left side.
    pal: a build_ivy palette; default is a single-ink sprig in `stroke` with knocked-out veins."""
    if pal is None:
        bg = "#F7F3EC" if stroke != INKS["white"] else INKS["ink"]
        pal = build_ivy.palette(leaf=stroke, vein=bg, stem=stroke)
    return (f'<g transform="translate({x:.1f} {y:.1f})">'
            + build_ivy.sprig(length, flip=flip, pal=pal, leaf_scale=leaf_scale, seed=seed) + "</g>")


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
    """ink in INKS gives a single-colour logo; "ivy" gives ink text with the green ivy flourish."""
    col = INKS["ink"] if ink == "ivy" else INKS[ink]
    pal = build_ivy.GREEN if ink == "ivy" else None
    d, w = script.shape("LittleFoot Munchkins", 96)
    W, H = w + 2 * 150, 170
    x0 = (W - w) / 2
    body = [f'<path class="wm-text" fill="{col}" transform="translate({x0:.1f} 112)" d="{d}"/>',
            f'<g class="vine vine-l">{vine(x0 - 18, 104, 118, flip=True, stroke=col, pal=pal, seed=3)}</g>',
            f'<g class="vine vine-r">{vine(x0 + w + 18, 104, 118, stroke=col, pal=pal, seed=5)}</g>']
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
    top_d, top_w = serif.shape("LITTLEFOOT", 46, tracking=9)
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
    """Heading ornament: two mirrored ivy sprigs meeting at a centre point."""
    W, H = 150, 34
    g = build_ivy.GREEN
    body = [f'<g class="vine vine-l">{vine(W/2 - 3, 20, 52, flip=True, pal=g, leaf_scale=0.2, seed=8)}</g>',
            f'<g class="vine vine-r">{vine(W/2 + 3, 20, 52, pal=g, leaf_scale=0.2, seed=9)}</g>',
            f'<circle cx="{W/2}" cy="20" r="2.2" fill="{g["stem"]}"/>']
    svg(W, H, "\n".join(body), "ornament.svg")


def favicon():
    body = [f'<rect width="64" height="64" rx="14" fill="{INKS["teal"]}"/>', paw(32, 33, 18, INKS["white"])]
    svg(64, 64, "\n".join(body), "favicon.svg")


if __name__ == "__main__":
    for ink in INKS:
        logo_a_wordmark(ink); logo_a_monogram(ink); logo_b_lockup(ink)
    logo_a_wordmark("ivy")
    logo_a_icon(); logo_b_icon(); favicon(); ornament()
