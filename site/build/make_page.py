"""Assemble site/index.html from build/template.html and the generated assets.
Run after build_logos.py and build_ivy.py:   python -P make_page.py
Replaces the old add_motion.py / add_features.py patch steps."""
import re
from pathlib import Path

B = Path(__file__).resolve().parent
SITE = B.parent
A = SITE / "assets"

def svg_inline(name, cls, style=""):
    s = (A / f"{name}.svg").read_text(encoding="utf-8").strip()
    s = re.sub(r'\s(width|height)="[^"]*"', "", s, count=2)
    s = s.replace(' role="img" aria-label="LittleFoot Munchkins"', "")
    if 'class="' in s.split(">", 1)[0]:
        s = re.sub(r'class="[^"]*"', f'class="{cls}"', s, count=1)
    else:
        s = s.replace("<svg ", f'<svg class="{cls}" aria-hidden="true" ', 1)
    if style:
        s = s.replace("<svg ", f'<svg style="{style}" ', 1)
    return s

# ---- paw symbol (from the circle-free icon) ----
paw = (A / "paw-only.svg").read_text(encoding="utf-8")
paw_body = re.sub(r'\sfill="[^"]*"', "", paw[paw.index(">") + 1: paw.rindex("</svg>")]).strip()
PAW_SYMBOL = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
              f'<symbol id="paw" viewBox="0 0 128 128">{paw_body}</symbol></svg>')
PAW_TRAIL = "".join('<svg><use href="#paw"/></svg>' for _ in range(6))

# ---- kittens: the sample board (owner replaces names, dates, statuses) ----
KITTENS = [
    ("kitten-ginger-peonies.jpg", "Ginger and white Munchkin kitten looking up beside a jar of peonies", "Name", "ginger &amp; white, female", "Born MM/DD", "available"),
    ("kitten-blue-point-closeup.jpg", "Fluffy blue-point Munchkin kitten with pale blue eyes", "Name", "blue point, male", "Born MM/DD", "reserved"),
    ("kitten-lynx-point-standing.jpg", "Lynx-point Munchkin kitten standing with tail raised", "Name", "lynx point, female", "Born MM/DD", "available"),
    ("kitten-seal-point-lounging.jpg", "Seal-point Munchkin kitten lying on a floral quilt", "Name", "seal point, male", "Born MM/DD", "home"),
    ("kitten-ginger-tail-up.jpg", "Ginger Munchkin kitten with its tail held high", "Name", "ginger, male", "Born MM/DD", "reserved"),
    ("kitten-blue-point-scratcher.jpg", "Blue-point Munchkin kitten stretched out on a cardboard scratcher", "Name", "blue point, female", "Born MM/DD", "home"),
]
LABEL = {"available": "Available", "reserved": "Reserved", "home": "Gone home"}
cards = []
for f, alt, name, colour, born, status in KITTENS:
    cards.append(
        f'<li data-status="{status}"><figure class="polaroid">'
        f'<img src="img/{f}" alt="{alt}" loading="lazy" width="1100" height="1400">'
        f'<span class="ribbon">{LABEL[status]}</span>'
        f'<figcaption><div class="name"><mark class="edit" title="Edit: the kitten\'s name">{name}</mark></div>'
        f'<div class="meta"><mark class="edit" title="Edit: colour and sex">{colour}</mark> &middot; <mark class="edit" title="Edit: birth date">{born}</mark></div></figcaption>'
        f'</figure></li>')
KITTEN_CARDS = "\n      ".join(cards)

KOTW = [
    ("kitten-cream-blue-eyes.jpg", "A cream Munchkin kitten with blue eyes sitting in front of peonies"),
    ("kitten-ginger-peonies.jpg", "Ginger and white Munchkin kitten looking up beside a jar of peonies"),
    ("kitten-lynx-point-standing.jpg", "Lynx-point Munchkin kitten standing with tail raised"),
    ("kitten-blue-point-closeup.jpg", "Fluffy blue-point Munchkin kitten with pale blue eyes"),
    ("kitten-seal-point-lounging.jpg", "Seal-point Munchkin kitten lying on a floral quilt"),
    ("kitten-ginger-tail-up.jpg", "Ginger Munchkin kitten with its tail held high"),
    ("kitten-blue-point-scratcher.jpg", "Blue-point Munchkin kitten stretched out on a cardboard scratcher"),
]
KOTW_POOL = "[" + ",".join(f'["{f}","{a}"]' for f, a in KOTW) + "]"

# ---- grain tile ----
noise_svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'>"
             "<filter id='g'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/>"
             "<feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0'/></filter>"
             "<rect width='100%' height='100%' filter='url(#g)'/></svg>")
GRAIN_URI = "data:image/svg+xml;utf8," + noise_svg.replace("#", "%23").replace("'", "%27")

# ---- small icons (inline, currentColor / teal) ----
ICON_FB = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.8c0-.9.3-1.6 1.6-1.6h1.7V4.4c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.3H7.4V14h2.8v8h3.3z"/></svg>'
ICON_IG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 7.3a4.7 4.7 0 1 0 0 9.4 4.7 4.7 0 0 0 0-9.4zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm5-8.9a1.1 1.1 0 1 1-2.2 0 1.1 1.1 0 0 1 2.2 0zM12 3.4c2.8 0 3.1 0 4.2.1 2.9.1 4.2 1.5 4.3 4.3.1 1.1.1 1.4.1 4.2s0 3.1-.1 4.2c-.1 2.8-1.4 4.2-4.3 4.3-1.1.1-1.4.1-4.2.1s-3.1 0-4.2-.1c-2.9-.1-4.2-1.5-4.3-4.3C3.4 15.1 3.4 14.8 3.4 12s0-3.1.1-4.2C3.6 5 4.9 3.6 7.8 3.5c1.1-.1 1.4-.1 4.2-.1zM12 1.6c-2.8 0-3.2 0-4.3.1C3.8 1.9 1.9 3.8 1.7 7.7 1.6 8.8 1.6 9.2 1.6 12s0 3.2.1 4.3c.2 3.9 2.1 5.8 6 6 1.1.1 1.5.1 4.3.1s3.2 0 4.3-.1c3.9-.2 5.8-2.1 6-6 .1-1.1.1-1.5.1-4.3s0-3.2-.1-4.3c-.2-3.9-2.1-5.8-6-6C15.2 1.6 14.8 1.6 12 1.6z"/></svg>'
ICON_TT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.6 2h-3.3v13.6a2.9 2.9 0 1 1-2.9-2.9c.3 0 .6 0 .9.1V9.5a6.2 6.2 0 1 0 5.3 6.1V8.9a7.2 7.2 0 0 0 4.4 1.5V7.1A4.4 4.4 0 0 1 16.6 2z"/></svg>'
T = 'fill="none" stroke="#2E8B8B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
ICO_HOME = f'<svg viewBox="0 0 48 48" aria-hidden="true" {T}><path d="M8 22 24 9l16 13"/><path d="M12 20v18h24V20"/><path d="M20 38V27h8v11"/></svg>'
ICO_HEART = f'<svg viewBox="0 0 48 48" aria-hidden="true" {T}><path d="M24 40s-15-9.5-15-20a8 8 0 0 1 15-4 8 8 0 0 1 15 4c0 10.5-15 20-15 20z"/></svg>'
ICO_LEAF = f'<svg viewBox="0 0 48 48" aria-hidden="true" {T}><path d="M10 38C10 22 20 10 38 10c0 18-12 28-28 28z"/><path d="M12 36c6-8 12-14 20-20"/></svg>'
ICO_CHAT = f'<svg viewBox="0 0 48 48" aria-hidden="true" {T}><path d="M8 12h32v20H20l-8 7v-7H8z"/><path d="M16 20h16M16 26h10"/></svg>'
ICO_EYES = f'<svg viewBox="0 0 48 48" aria-hidden="true" {T}><path d="M4 24s8-12 20-12 20 12 20 12-8 12-20 12S4 24 4 24z"/><circle cx="24" cy="24" r="6"/></svg>'
ICO_PAW = '<svg viewBox="0 0 128 128" aria-hidden="true"><use href="#paw"/></svg>'

html = (B / "template.html").read_text(encoding="utf-8")
subs = {
    "{{PAW_SYMBOL}}": PAW_SYMBOL, "{{PAW_TRAIL}}": PAW_TRAIL, "{{KITTEN_CARDS}}": KITTEN_CARDS, "{{KOTW_POOL}}": KOTW_POOL,
    "{{GRAIN_URI}}": GRAIN_URI,
    "{{WORDMARK}}": svg_inline("logo-a-wordmark-ivy", "wordmark grow", "--base:2.6s"),
    "{{ORNAMENT}}": svg_inline("ornament", "ornament"),
    "{{IVY_GARLAND}}": svg_inline("ivy-garland", "ivy ivy-top grow", "--base:.6s"),
    "{{IVY_GARLAND_B}}": svg_inline("ivy-garland-b", "ivy ivy-top-r grow", "--base:1.1s"),
    "{{IVY_CLIMBER}}": svg_inline("ivy-climber", "ivy ivy-bottom"),
    "{{ICON_FB}}": ICON_FB, "{{ICON_IG}}": ICON_IG, "{{ICON_TT}}": ICON_TT,
    "{{ICO_HOME}}": ICO_HOME, "{{ICO_HEART}}": ICO_HEART, "{{ICO_LEAF}}": ICO_LEAF,
    "{{ICO_CHAT}}": ICO_CHAT, "{{ICO_EYES}}": ICO_EYES, "{{ICO_PAW}}": ICO_PAW,
}
for k, v in subs.items():
    html = html.replace(k, v)
left = re.findall(r"\{\{[A-Z_]+\}\}", html)
if left:
    raise SystemExit("unfilled tokens: " + ", ".join(sorted(set(left))))
(SITE / "index.html").write_text(html, encoding="utf-8")
print("wrote index.html", len(html), "chars")
