"""Build index.html from page.html: inlines the traced Key Did Dat logo path (assets/logo.svg) wherever
{{LOGO_D}} / {{LOGO_VB}} appear, then writes the Content-Security-Policy into {{CSP}} with a sha256 hash
of every inline <script> (so editing a script is safe: the hash is redone each build).
Rerun after editing page.html:  python3 build.py"""
import re, pathlib, hashlib, base64
HERE = pathlib.Path(__file__).parent
svg = (HERE / "assets/logo.svg").read_text()
d = re.search(r' d="([^"]+)"', svg).group(1)
vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
page = (HERE / "page.html").read_text()
assert "{{LOGO_D}}" in page and "{{CSP}}" in page
out = page.replace("{{LOGO_D}}", d).replace("{{LOGO_VB}}", vb)
inline = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", out, re.S)
hashes = " ".join("'sha256-%s'" % base64.b64encode(hashlib.sha256(s.encode()).digest()).decode() for s in inline)
csp = "; ".join([
    "default-src 'self'",
    f"script-src 'self' https://cdn.jsdelivr.net {hashes}",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src https://fonts.gstatic.com",
    "img-src 'self' data: blob:",
    "media-src 'self'",
    "connect-src 'self' https://cdn.jsdelivr.net",
    "frame-src https://www.instagram.com https://www.google.com",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'none'",
    "upgrade-insecure-requests",
])
out = out.replace("{{CSP}}", csp)
(HERE / "index.html").write_text(out)
print("index.html", len(out) // 1024, "KB,", len(inline), "inline scripts hashed")
