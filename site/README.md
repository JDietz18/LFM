# LittleFoot Munchkins site

Static landing page plus logo set. No build step is needed to host it: upload the
whole `site/` folder (minus `build/`) to any web host.

- `index.html` — the landing page. Placeholders are wrapped in `<mark class="edit">`;
  search for `class="edit"`, replace each one, and remove the `<mark>` tags.
  The three social buttons in the hero and the three links under "Follow along"
  need the real Facebook, Instagram and TikTok URLs.
- `logos.html` — side-by-side sheet of the two logo directions with downloads.
  **Direction A (script wordmark + L.F.M monogram + paw icon) is the chosen logo, 2026-10-08.**
  Direction B is kept as the alternative.
- `assets/` — outlined SVG logos (no fonts required), icon and favicon.
- `exports/` — PNG avatars for Facebook and Instagram: `avatar-paw` (paw on teal, full bleed)
  and `avatar-monogram` (L.F.M on whitewash), each at 1024 and 400 px. Re-render with
  `build/avatars.html` (`?v=paw` or `?v=mono`) at a 1024x1024 viewport.
- `img/` — the seven unwatermarked photos, resized to 1400 px for the web.
- `build/` — `build_logos.py` regenerates `assets/` from the two Google Fonts files
  in `build/fonts/` (SIL Open Font License). Run from inside `build/`:

  ```
  python -P build_logos.py
  ```

  Needs `fonttools` and `uharfbuzz` (`pip install fonttools uharfbuzz`).

  The page is then assembled by two idempotent patch steps (run both, in order, from
  `build/`, after any logo rebuild): `python -P add_motion.py` (inlines the wordmark, adds
  motion, shiplap and ornaments) and `python -P add_features.py` (polaroid gallery, kitten
  of the week). `python -P make_artifact.py` derives the claude.ai preview page.

Palette: whitewash #F7F3EC, linen #EDE5D8, ink #3A3532, teal #2E8B8B, blush #F0CFC0,
sage #9DAE98. Type: Great Vibes (script), Cormorant Garamond (headings), Nunito (body).
