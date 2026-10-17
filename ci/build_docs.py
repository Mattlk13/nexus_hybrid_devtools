"""Build the credential-free integration documentation preview (stdlib only)."""
from pathlib import Path
import argparse
import html
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public"
SOURCES = ("CERTIFICATION.md", "FAILURE_MATRIX.md", "ADAPTER_SETUP.md")
CSS = """*{box-sizing:border-box}body{overflow-wrap:anywhere;margin:0;background:#f4f7f8;color:#142a34;font:18px/1.6 system-ui,sans-serif}header,main,footer{max-width:1100px;margin:auto;padding:24px}header{border-bottom:2px solid #b4c6cd}nav{display:flex;flex-wrap:wrap;gap:20px}a{color:#004c78}a:focus-visible{outline:3px solid #004c78;outline-offset:4px}.skip{position:absolute;top:-80px}.skip:focus{top:8px;background:white;padding:8px}h1{font-size:clamp(2rem,6vw,3.5rem);line-height:1.15}h2{margin-top:2.5rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#e6eef1;padding:18px;border-radius:8px}section{border-top:1px solid #b4c6cd;margin-top:30px}.hold{background:#fff0d0;color:#563900;padding:16px;border-left:5px solid #8a5a00}.muted{color:#445c68}p{max-width:85ch}code{overflow-wrap:anywhere}@media(max-width:500px){header,main,footer{padding:16px}}"""
def render_markdown(source):
    # No raw HTML or active Markdown links are accepted from documentation.
    blocks = []
    paragraph = []
    pre = []
    fenced = False
    def flush():
        if paragraph:
            blocks.append("<p>" + html.escape(" ".join(paragraph)) + "</p>")
            paragraph.clear()
    for line in source.splitlines():
        if line.startswith("```"):
            flush()
            if fenced:
                blocks.append("<pre><code>" + html.escape("\n".join(pre)) + "</code></pre>")
                pre.clear()
            fenced = not fenced
        elif fenced:
            pre.append(line)
        elif line.startswith("#"):
            flush()
            level = min(len(line) - len(line.lstrip("#")) + 1, 6)
            blocks.append(f"<h{level}>" + html.escape(line.lstrip("# ").strip()) + f"</h{level}>")
        elif not line.strip():
            flush()
        elif line.startswith("|"):
            flush()
            blocks.append("<pre>" + html.escape(line) + "</pre>")
        else:
            paragraph.append(line)
    flush()
    if pre:
        blocks.append("<pre>" + html.escape("\n".join(pre)) + "</pre>")
    return "\n".join(blocks)

def build():
    docs = [(name, (ROOT / name).read_text(encoding="utf-8")) for name in SOURCES]
    sections = "\n".join(f'<section id="{Path(n).stem.lower()}">' + render_markdown(s) + "</section>" for n,s in docs)
    digest = hashlib.sha256("".join(s for _,s in docs).encode()).hexdigest()
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="NEXUS developer adapter setup, verification evidence and release blockers.">
<title>NEXUS integration documentation</title><link rel="stylesheet" href="styles.css"></head>
<body><a class="skip" href="#main">Skip to documentation</a>
<header><p>NEXUS / Developer integrations</p><h1>Adapters with verifiable outcomes.</h1>
<p>Configuration, test evidence and honest limits for the Sentry and Jenkins integrations.</p>
<nav aria-label="Documentation"><a href="#certification">Certification evidence</a><a href="#failure_matrix">Failure matrix</a><a href="#adapter_setup">Adapter setup</a></nav></header>
<main id="main" tabindex="-1"><p class="hold"><strong>Production HOLD.</strong> This is a development documentation preview. A working preview does not certify the adapters for production.</p>{sections}</main>
<footer><p>Generated from reviewed repository documentation. No credentials, remote scripts or analytics.</p><p class="muted">Source content SHA-256: <code>{digest}</code></p></footer></body></html>
"""
    headers = """/*
  Content-Security-Policy: default-src 'none'; style-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer
  Permissions-Policy: camera=(), microphone=(), geolocation=()
"""
    return {"index.html":page, "styles.css":CSS+"\n", "_headers":headers}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = build()
    if args.check:
        stale = [n for n,s in expected.items() if not (OUT/n).exists() or (OUT/n).read_text(encoding="utf-8") != s]
        if stale: raise SystemExit("Documentation stale: " + ", ".join(stale))
        print("PASS: documentation matches tracked source")
    else:
        OUT.mkdir(exist_ok=True)
        for name,source in expected.items(): (OUT/name).write_text(source, encoding="utf-8", newline="\n")
        print("Built public documentation")
