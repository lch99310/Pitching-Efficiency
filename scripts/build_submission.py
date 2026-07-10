"""
build_submission.py -- render README.md into paste-ready HTML for the FanGraphs
Community Blog (WordPress "Text" editor): images become external raw-GitHub URLs
pinned to the current commit, the LaTeX formula becomes plain HTML, and relative
repo links are absolutized. Output: ../submission/fangraphs_submission.html

    python3 scripts/build_submission.py
"""
import os, re, subprocess, markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
REPO = "https://github.com/lch99310/Pitching-Efficiency"
SITE = "https://chunghaolee.com/portfolio/outs_per_effort/"
SHA = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
IMG_BASE = f"https://raw.githubusercontent.com/lch99310/Pitching-Efficiency/{SHA}/charts"
FILE_BASE = f"{REPO}/tree/{SHA}"

md = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
md = md.split("---", 1)[1].lstrip("\n")                       # drop title + byline block
md = re.sub(r"\$\$.*?\$\$",
            '<p style="text-align:center;font-size:1.5em;margin:1em 0;">'
            '<strong>OPE = (100 &times; outs) &divide; (pitches + 4 &times; TB)</strong></p>',
            md, flags=re.S)
md = re.sub(r"\]\(charts/", f"]({IMG_BASE}/", md)             # images -> raw URLs

def absify(m):
    tgt = m.group(1)
    if tgt.startswith("http") or tgt.startswith("#"):
        return m.group(0)
    return f"]({FILE_BASE}/{tgt.rstrip('/')})"
md = re.sub(r"\]\(([^)]+)\)", absify, md)

dek = (
    '<p><em>Data: MLB Stats API, 2023&ndash;2025 (~1,000 pitcher-seasons, IP &ge; 50). '
    f'A version of this article first appeared at <a href="{SITE}">chunghaolee.com</a>; '
    f'the full data and code are on <a href="{REPO}">GitHub</a>.</em></p>\n'
)
body = markdown.markdown(md, extensions=["tables", "attr_list", "sane_lists"])
body = body.replace("<img ", '<img style="max-width:100%;height:auto;" ')

out = os.path.join(ROOT, "submission", "fangraphs_submission.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(dek + body)
print(f"SHA {SHA}\nwrote {out}\nimages {body.count('<img')}  tables {body.count('<table')}")
