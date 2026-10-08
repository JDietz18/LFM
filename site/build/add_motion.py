"""One-shot patch: inline the wordmark SVG into index.html and add the motion layer.
Idempotent: re-running replaces the previous motion block and inline SVG."""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
html_path = SITE / "index.html"
html = html_path.read_text(encoding="utf-8")

# ---------- 1. inline the wordmark SVG (so its parts can be animated) ----------
svg = (SITE / "assets/logo-a-wordmark-ink.svg").read_text(encoding="utf-8").strip()
svg = re.sub(r'\s(width|height)="[^"]*"', "", svg, count=2)           # keep viewBox only
svg = svg.replace('<svg ', '<svg class="wordmark" ', 1)
html = re.sub(r'<img class="wordmark"[^>]*>', svg, html, count=1)
html = re.sub(r'<svg class="wordmark".*?</svg>', svg, html, count=1, flags=re.S)  # replace if already inline

# ---------- 2. a reusable paw symbol + the trail markup ----------
paw = (SITE / "assets/paw-only.svg").read_text(encoding="utf-8")
paw_body = re.sub(r'\sfill="[^"]*"', "", paw[paw.index(">") + 1: paw.rindex("</svg>")]).strip()
symbol = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
          f'<symbol id="paw" viewBox="0 0 128 128">{paw_body}</symbol></svg>')
html = re.sub(r'<svg width="0" height="0" style="position:absolute" aria-hidden="true">.*?</svg>\n', "", html, count=1, flags=re.S)
html = html.replace("<body>\n", "<body>\n" + symbol + "\n", 1)

trail = ('<div class="paw-trail" aria-hidden="true">'
         + "".join('<svg><use href="#paw"/></svg>' for _ in range(6)) + "</div>\n    ")
html = re.sub(r'<div class="paw-trail".*?</div>\n\s*', "", html, count=1, flags=re.S)
html = html.replace('<h2>Recent kittens</h2>', trail + '<h2>Recent kittens</h2>', 1)

# ---------- 2b. vine ornament under each section heading ----------
orn = (SITE / "assets/ornament.svg").read_text(encoding="utf-8").strip()
orn = re.sub(r'\s(width|height)="[^"]*"', "", orn, count=2)
orn = orn.replace('<svg ', '<svg class="ornament" aria-hidden="true" ', 1).replace(' role="img" aria-label="Little Foot Munchkins"', "")
html = re.sub(r'\n\s*<svg class="ornament".*?</svg>', "", html, flags=re.S)
html = re.sub(r'(<h2>[^<]*</h2>)', lambda m: m.group(1) + "\n    " + orn, html)

# ---------- 3. CSS ----------
css = r"""
/* ===== texture + ornament ===== */
.about,.follow{
  --plank:176px;
  background-color:var(--linen);
  background-image:repeating-linear-gradient(to bottom,
      transparent 0, transparent calc(var(--plank) - 3px),
      rgba(120,100,78,.11) calc(var(--plank) - 3px), rgba(120,100,78,.11) calc(var(--plank) - 1px),
      rgba(255,255,255,.6) calc(var(--plank) - 1px), rgba(255,255,255,.6) var(--plank));
  background-position:0 56px;
}
.ornament{display:block;width:150px;max-width:60%;height:auto;margin:-.15em 0 1.1em}
.gallery .ornament,.contact .ornament{margin-inline:auto}
/* ===== motion (everything below is skipped when the viewer prefers reduced motion) ===== */
.wordmark{display:block;height:auto}
.hero{position:relative;overflow:hidden}
.hero .wrap{position:relative;z-index:1}
.paw-trail{display:flex;justify-content:center;gap:clamp(10px,3vw,30px);height:44px;margin:0 auto 14px}
.paw-trail svg{width:26px;height:26px;fill:var(--teal);opacity:.5}
.paw-trail svg:nth-child(odd){transform:translateY(-7px) rotate(-16deg) scaleX(-1)}
.paw-trail svg:nth-child(even){transform:translateY(7px) rotate(16deg)}
.paw-ghost{position:absolute;z-index:2;width:26px;height:26px;fill:var(--teal);pointer-events:none;opacity:0;
  transform:translate(-50%,-50%) rotate(var(--rot,0deg)) scale(.6)}
.social{transition:background-color .15s,color .15s,transform .35s cubic-bezier(.34,1.56,.64,1)}
.grid img{transition:transform .7s cubic-bezier(.2,.7,.2,1)}
@media (prefers-reduced-motion:no-preference){
  /* hero: pen draws the vines, the script writes itself on, then copy and buttons rise */
  .wm-text{clip-path:inset(-12% 100% -12% -2%);animation:writeOn 1.6s cubic-bezier(.45,0,.25,1) .3s forwards}
  @keyframes writeOn{to{clip-path:inset(-12% -2% -12% -2%)}}
  .vine-stem{stroke-dasharray:1;stroke-dashoffset:1;animation:draw .9s ease-out 1.7s forwards}
  @keyframes draw{to{stroke-dashoffset:0}}
  .vine-leaf{transform-box:fill-box;transform-origin:0% 50%;transform:scale(0);
    animation:leafPop .55s cubic-bezier(.34,1.56,.64,1) forwards,sway 5.5s ease-in-out 3.4s infinite alternate}
  .vine > g:nth-child(2) .vine-leaf{animation-delay:2.0s,3.4s}
  .vine > g:nth-child(3) .vine-leaf{animation-delay:2.2s,3.9s}
  .vine > g:nth-child(4) .vine-leaf{animation-delay:2.4s,4.5s}
  .ornament .vine-leaf{transform:none;animation:sway 6.5s ease-in-out infinite alternate}
  .ornament .vine > g:nth-child(2) .vine-leaf{animation-delay:-1s}
  .ornament .vine > g:nth-child(3) .vine-leaf{animation-delay:-3s}
  .ornament .vine > g:nth-child(4) .vine-leaf{animation-delay:-5s}
  @keyframes leafPop{to{transform:scale(1)}}
  @keyframes sway{from{transform:rotate(-4deg)}to{transform:rotate(4deg)}}
  .tagline,.socials li{opacity:0;animation:rise .7s cubic-bezier(.2,.7,.2,1) forwards}
  .tagline{animation-delay:1.4s}
  .socials li:nth-child(1){animation-delay:1.9s}
  .socials li:nth-child(2){animation-delay:2.05s}
  .socials li:nth-child(3){animation-delay:2.2s}
  @keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
  .hero .arch{animation:fadeIn .9s ease-out both}
  .hero .arch img{transform:scale(1.08);animation:settle 2.2s cubic-bezier(.2,.7,.2,1) .1s forwards}
  @keyframes fadeIn{from{opacity:0}to{opacity:1}}
  @keyframes settle{to{transform:scale(1)}}
  /* buttons answer the pointer */
  .social:hover{transform:translateY(-3px)}
  .social:hover svg{animation:wiggle .5s ease-in-out}
  @keyframes wiggle{25%{transform:rotate(-14deg)}75%{transform:rotate(12deg)}}
  /* gallery: paw prints walk in, then the tiles tumble into place */
  .paw-trail.will-animate svg{opacity:0;transform:scale(.4)}
  .paw-trail.is-in svg{animation:pawIn .45s cubic-bezier(.34,1.56,.64,1) calc(var(--i,0) * .16s) forwards}
  .paw-trail.is-in svg:nth-child(odd){animation-name:pawInL}
  @keyframes pawIn{to{opacity:.5;transform:translateY(7px) rotate(16deg) scale(1)}}
  @keyframes pawInL{to{opacity:.5;transform:translateY(-7px) rotate(-16deg) scaleX(-1) scale(1)}}
  .grid.will-animate li{opacity:0;transform:translateY(30px) rotate(var(--tilt,2deg))}
  .grid li:nth-child(even){--tilt:-2deg}
  .grid.is-in li{animation:tumble .85s cubic-bezier(.2,.8,.2,1) calc(.5s + var(--i,0) * .11s) forwards}
  @keyframes tumble{to{opacity:1;transform:none}}
  .grid li:hover img{transform:scale(1.045)}
  /* cursor paw prints across the hero */
  .paw-ghost{animation:pawGhost 1.7s ease-out forwards}
  @keyframes pawGhost{12%{opacity:.42;transform:translate(-50%,-50%) rotate(var(--rot,0deg)) scale(1)}
    100%{opacity:0;transform:translate(-50%,-50%) rotate(var(--rot,0deg)) scale(1)}}
}
"""
html = re.sub(r'\n/\* ===== motion.*?\n\}\n', "\n", html, count=1, flags=re.S)
html = html.replace("</style>", css.rstrip("\n") + "\n</style>", 1)

# ---------- 4. JS ----------
js = r"""
<script>
(function () {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  // scroll-triggered: paw trail + gallery tumble, once each
  var grid = document.querySelector('.grid'), trail = document.querySelector('.paw-trail');
  [grid, trail].forEach(function (el) {
    if (!el) return;
    el.classList.add('will-animate');
    Array.prototype.forEach.call(el.children, function (c, i) { c.style.setProperty('--i', i); });
  });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { threshold: 0.2 });
    [grid, trail].forEach(function (el) { if (el) io.observe(el); });
  } else {
    [grid, trail].forEach(function (el) { if (el) el.classList.add('is-in'); });
  }
  // cursor paw prints across the hero (mouse only)
  if (!matchMedia('(pointer: fine)').matches) return;
  var hero = document.querySelector('.hero'), last = null, side = 1, live = 0;
  hero.addEventListener('mousemove', function (e) {
    var r = hero.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
    if (last) {
      var dx = x - last.x, dy = y - last.y;
      if (dx * dx + dy * dy < 85 * 85) return;
      var ang = Math.atan2(dy, dx) * 180 / Math.PI + 90;
      side = -side;
      var s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      s.setAttribute('class', 'paw-ghost');
      s.innerHTML = '<use href="#paw"/>';
      s.style.left = (x + side * 11) + 'px';
      s.style.top = y + 'px';
      s.style.setProperty('--rot', (ang + side * 16) + 'deg');
      if (side < 0) s.style.setProperty('--rot', (ang + side * 16) + 'deg');
      hero.appendChild(s); live++;
      if (live > 40) { var first = hero.querySelector('.paw-ghost'); if (first) { first.remove(); live--; } }
      s.addEventListener('animationend', function () { s.remove(); live--; });
    }
    last = { x: x, y: y };
  });
  hero.addEventListener('mouseleave', function () { last = null; });
})();
</script>
"""
html = re.sub(r'\n<script>\n\(function \(\) \{\n  if \(matchMedia.*?</script>\n', "\n", html, count=1, flags=re.S)
html = html.replace("</body>", js.strip("\n") + "\n</body>", 1)

html_path.write_text(html, encoding="utf-8")
print("index.html patched:", len(html), "chars")
