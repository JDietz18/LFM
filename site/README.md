# LittleFoot Munchkins site

Static landing page plus logo set. No build step is needed to host it: upload the
whole `site/` folder (minus `build/`) to any web host.

- `index.html` — the landing page, ASSEMBLED from `build/template.html` by `build/make_page.py`.
  Edit the template, not index.html. Placeholders are wrapped in `<mark class="edit">`; search for
  `class="edit"`, replace each one, then delete the `<mark>` tags. Kitten cards (name, colour, birth
  date, status) are the `KITTENS` list in `build/make_page.py`; `data-status` drives the ribbon and
  the filter chips. Social links: the hero buttons, the nav button, and the evening band.
- `logos.html` — side-by-side sheet of the two logo directions with downloads.
  **Direction A (script wordmark + L.F.M monogram + paw icon) is the chosen logo, 2026-10-08.**
  Direction B is kept as the alternative.
- `assets/` — outlined SVG logos (no fonts required), icon, favicon, heading ornament, and the three
  ivy pieces (two garlands, one climber).
- `exports/` — PNG avatars for Facebook and Instagram: `avatar-paw` (paw on teal, full bleed)
  and `avatar-monogram` (L.F.M on whitewash), each at 1024 and 400 px. Re-render with
  `build/avatars.html` (`?v=paw` or `?v=mono`) at a 1024x1024 viewport.
- `img/` — the seven unwatermarked photos, resized to 1400 px for the web, plus `social-card.jpg`
  (1200x630, the Facebook / Twitter share image; re-render `build/socialcard.html` at 1200x630).
- `favicon.ico` — multi-size icon from the paw avatar, for browsers that ignore the SVG favicon.
- `build/` — run from inside `build/`, in this order, after any change:

  ```
  python -P build_logos.py     # logo SVGs + ornament (imports build_ivy for the sprigs)
  python -P build_ivy.py       # assets/ivy-garland.svg, ivy-garland-b.svg, ivy-climber.svg
  python -P make_page.py       # template.html + assets -> ../index.html
  python -P make_artifact.py   # ../index.html -> build/artifact.html (claude.ai preview)
  ```

  Needs `fonttools` and `uharfbuzz` (`pip install fonttools uharfbuzz`). The fonts in
  `build/fonts/` are from the Google Fonts repo (SIL Open Font License).

Palette: whitewash #F7F3EC, linen #EDE5D8, ink #3A3532, teal #2E8B8B, blush #F0CFC0,
sage #9DAE98. Type: Great Vibes (script), Cormorant Garamond (headings), Nunito (body).
