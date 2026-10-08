"""Derive build/artifact.html (for the claude.ai preview) from index.html:
drop the document skeleton the publisher adds, keep title/meta/style/body,
and add a footer link to the logo sheet."""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
s = (SITE / "index.html").read_text(encoding="utf-8")
head = s[s.index("<title>"): s.index("</style>") + len("</style>")]
head = re.sub(r'<link rel="icon"[^>]*>\n', "", head)
body = s[s.index("<body>") + 6: s.index("</body>")]
body = body.replace("<div>&copy; 2026 Little Foot Munchkins</div>",
                    '<div>&copy; 2026 Little Foot Munchkins &nbsp;&middot;&nbsp; <a href="logos.html">Logo options</a></div>')
out = SITE / "build/artifact.html"
out.write_text(head + "\n" + body, encoding="utf-8")
print("wrote", out, len(head + body), "chars")
