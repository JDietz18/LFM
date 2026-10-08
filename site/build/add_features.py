"""Patch step 3 (after add_motion.py): polaroid gallery + kitten of the week.
Idempotent: re-running replaces its own markup, CSS and script."""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
html_path = SITE / "index.html"
html = html_path.read_text(encoding="utf-8")

# ---------- 1. polaroid gallery: wrap each tile in a figure with a caption ----------
captions = {
    "kitten-ginger-peonies.jpg": "ginger &amp; white",
    "kitten-blue-point-closeup.jpg": "blue point",
    "kitten-lynx-point-standing.jpg": "lynx point",
    "kitten-seal-point-lounging.jpg": "seal point",
    "kitten-ginger-tail-up.jpg": "ginger",
    "kitten-blue-point-scratcher.jpg": "blue point",
}

def tile(m):
    img = m.group(1)
    name = re.search(r'img/([^"]+)"', img).group(1)
    cap = captions.get(name, "kitten")
    return (f'<li><figure class="polaroid">{img}'
            f'<figcaption><mark class="edit" title="Edit: the kitten\'s name or colour">{cap}</mark></figcaption></figure></li>')

# unwrap a previous run first, then wrap
html = re.sub(r'<li><figure class="polaroid">(<img[^>]+>)<figcaption>.*?</figcaption></figure></li>', r'<li>\1</li>', html, flags=re.S)
html = re.sub(r'<li>(<img src="img/kitten[^>]+>)</li>', tile, html)

# ---------- 2. kitten of the week: the arch photo rotates by ISO week ----------
week = [
    ("kitten-cream-blue-eyes.jpg", "A cream Munchkin kitten with blue eyes sitting in front of peonies"),
    ("kitten-ginger-peonies.jpg", "Ginger and white Munchkin kitten looking up beside a jar of peonies"),
    ("kitten-lynx-point-standing.jpg", "Lynx-point Munchkin kitten standing with tail raised"),
    ("kitten-blue-point-closeup.jpg", "Fluffy blue-point Munchkin kitten with pale blue eyes"),
    ("kitten-seal-point-lounging.jpg", "Seal-point Munchkin kitten lying on a floral quilt"),
    ("kitten-ginger-tail-up.jpg", "Ginger Munchkin kitten with its tail held high"),
    ("kitten-blue-point-scratcher.jpg", "Blue-point Munchkin kitten stretched out on a cardboard scratcher"),
]
pool = ",".join(f'["{f}","{a}"]' for f, a in week)
hero_block = f'''<figure class="arch-figure">
      <div class="arch">
        <img id="kotw" src="img/kitten-cream-blue-eyes.jpg" alt="A cream Munchkin kitten with blue eyes sitting in front of peonies" width="1054" height="1400" fetchpriority="high">
      </div>
      <figcaption class="kotw-caption">Kitten of the week</figcaption>
      <script>
      (function () {{
        // same kitten for everyone all week: index by ISO week number
        var pool = [{pool}];
        var d = new Date(), t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
        t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7));
        var week = Math.ceil(((t - Date.UTC(t.getUTCFullYear(), 0, 1)) / 864e5 + 1) / 7);
        var pick = pool[(t.getUTCFullYear() * 53 + week) % pool.length];
        var img = document.getElementById('kotw');
        img.src = 'img/' + pick[0]; img.alt = pick[1];
      }})();
      </script>
    </figure>'''
html = re.sub(r'<figure class="arch-figure">.*?</figure>', hero_block, html, count=1, flags=re.S)
html = re.sub(r'<div class="arch">\s*<img src="img/kitten-cream-blue-eyes.jpg"[^>]*>\s*</div>', hero_block, html, count=1, flags=re.S)

# ---------- 3. CSS ----------
css = r"""
/* ===== polaroid gallery + kitten of the week ===== */
.arch-figure{margin:0;width:min(100%,500px);margin-inline:auto}
.hero .arch-figure{order:-1}
@media (min-width:860px){.hero .arch-figure{order:0}}
.arch-figure .arch{width:100%}
.kotw-caption{font:italic 500 1.05rem/1.3 var(--serif);color:var(--ink-soft);text-align:center;margin-top:.9rem}
@media (prefers-reduced-motion:no-preference){.kotw-caption{opacity:0;animation:rise .9s cubic-bezier(.34,1.56,.64,1) 1.6s forwards}}
.grid{gap:clamp(18px,3vw,34px)}
.grid li{aspect-ratio:auto;border-radius:0;overflow:visible;background:none;transform:rotate(var(--rest,0deg));transition:transform .5s cubic-bezier(.34,1.56,.64,1)}
.polaroid{transition:box-shadow .5s}
.grid li:nth-child(6n+1){--rest:-2.4deg}
.grid li:nth-child(6n+2){--rest:1.6deg}
.grid li:nth-child(6n+3){--rest:-1.1deg}
.grid li:nth-child(6n+4){--rest:2.1deg}
.grid li:nth-child(6n+5){--rest:-1.7deg}
.grid li:nth-child(6n+6){--rest:1.2deg}
.polaroid{position:relative;margin:0;background:#FFFDF8;padding:12px 12px 14px;
  box-shadow:0 1px 2px rgba(58,53,50,.08),0 10px 24px -10px rgba(58,53,50,.35)}
.polaroid img{aspect-ratio:4/5;width:100%;height:auto;object-fit:cover;display:block;background:var(--linen)}
.polaroid::before{content:"";position:absolute;left:50%;top:-11px;width:84px;height:24px;margin-left:-42px;
  background:rgba(237,229,216,.82);transform:rotate(-3deg);box-shadow:0 1px 2px rgba(58,53,50,.12);
  -webkit-mask:repeating-linear-gradient(90deg,#000 0 7px,rgba(0,0,0,.85) 7px 9px);mask:repeating-linear-gradient(90deg,#000 0 7px,rgba(0,0,0,.85) 7px 9px)}
.polaroid figcaption{font:400 1.55rem/1 var(--script);color:var(--ink);text-align:center;padding:14px 4px 8px;min-height:2.6rem}
.polaroid figcaption mark.edit{border-bottom-width:1px}
@media (prefers-reduced-motion:no-preference){
  .grid.will-animate li:not(.settled){opacity:0;transform:translateY(30px) rotate(calc(var(--rest,0deg) + var(--tilt,2deg)))}
  @keyframes tumble{to{opacity:1;transform:rotate(var(--rest,0deg))}}
  .grid li:hover{transform:rotate(0deg) translateY(-16px) scale(1.06);z-index:1}
  .grid li:hover .polaroid{box-shadow:0 2px 3px rgba(58,53,50,.1),0 28px 40px -16px rgba(58,53,50,.45)}
  .grid li:hover img{transform:none}
}
"""
html = re.sub(r'\n/\* ===== polaroid gallery[^\n]*\n.*?(?=\n/\* =====|\n</style>)', "", html, flags=re.S)
html = html.replace("</style>", css.rstrip("\n") + "\n</style>", 1)

# ---------- 4. paper grain: alpha-only SVG noise laid over the whole page ----------
noise_svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'>"
             "<filter id='g'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/>"
             "<feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0'/></filter>"
             "<rect width='100%' height='100%' filter='url(#g)'/></svg>")
noise_uri = "data:image/svg+xml;utf8," + noise_svg.replace("#", "%23").replace("'", "%27")
grain_css = """
/* ===== paper grain ===== */
body::after{content:"";position:fixed;inset:0;z-index:9999;pointer-events:none;
  background:url("NOISE") repeat;background-size:260px 260px;opacity:.075;mix-blend-mode:multiply}
""".replace("NOISE", noise_uri)
html = re.sub(r'\n/\* ===== paper grain[^\n]*\n.*?(?=\n/\* =====|\n</style>)', "", html, flags=re.S)
html = re.sub(r'body::after\{content:"";position:fixed;inset:0;z-index:9999;[^\n]*\n[^\n]*\n', "", html, count=1)
html = html.replace("</style>", grain_css.rstrip("\n") + "\n</style>", 1)


# ---------- 5. ivy drapes: generated garland (hero) and climber (footer), inlined so they can grow ----------
def _ivy(name, cls, style=""):
    svg = (SITE / f"assets/{name}.svg").read_text(encoding="utf-8").strip()
    svg = re.sub(r'\s(width|height)="[^"]*"', "", svg, count=2)
    return svg.replace('class="ivy"', f'class="{cls}"' + (f' style="{style}"' if style else ""), 1)
html = re.sub(r'\s*<svg[^>]*class="ivy ivy-(top|bottom)[^"]*"[^>]*>.*?</svg>', "", html, flags=re.S)
html = re.sub(r'\s*<img class="ivy ivy-(top|bottom)"[^>]*>', "", html)
html = html.replace('<header class="hero">\n', '<header class="hero">\n  ' + _ivy("ivy-garland", "ivy ivy-top grow", "--base:.4s") + '\n  ' + _ivy("ivy-garland-b", "ivy ivy-top-r grow", "--base:.9s") + '\n', 1)
html = html.replace('<footer>\n', '<footer>\n  ' + _ivy("ivy-climber", "ivy ivy-bottom") + '\n', 1)
ivy_css = """
/* ===== ivy drapes ===== */
.ivy{position:absolute;z-index:0;pointer-events:none;width:clamp(210px,34vw,470px);height:auto;overflow:visible;filter:drop-shadow(0 2px 2px rgba(58,53,50,.12))}
.ivy-top{left:-14px;top:-12px;transform-origin:0 0}
.ivy-top-r{right:-14px;top:-12px;z-index:2;transform:scaleX(-1);transform-origin:50% 0;width:clamp(190px,30vw,430px)}
footer{position:relative;overflow:hidden}
footer > :not(.ivy){position:relative;z-index:1}
.ivy-bottom{right:-10px;bottom:-8px;transform-origin:100% 100%;width:clamp(170px,24vw,320px)}
@media (prefers-reduced-motion:no-preference){
  .ivy-top{animation:ivySwayTop 5s ease-in-out infinite alternate}
  .ivy-top-r{animation:ivySwayTopR 6s ease-in-out -2.5s infinite alternate}
  @keyframes ivySwayTopR{from{transform:scaleX(-1) rotate(-2.2deg) translateX(-3px)}to{transform:scaleX(-1) rotate(2.2deg) translateX(3px)}}
  .ivy-bottom{animation:ivySwayBottom 6s ease-in-out -3s infinite alternate}
  @keyframes ivySwayTop{from{transform:rotate(-2.6deg) translateX(-4px)}to{transform:rotate(2.6deg) translateX(4px)}}
  @keyframes ivySwayBottom{from{transform:rotate(2.4deg)}to{transform:rotate(-2.4deg)}}
}
"""
html = re.sub(r'\n/\* ===== ivy drapes[^\n]*\n.*?(?=\n/\* =====|\n</style>)', "", html, flags=re.S)
html = html.replace("</style>", ivy_css.rstrip("\n") + "\n</style>", 1)

html_path.write_text(html, encoding="utf-8")
print("index.html patched:", len(html), "chars; polaroids:", html.count('class="polaroid"'), "; kotw:", html.count('id="kotw"'))
