"""Check the site's internal links, and that every bootcamp week is linked everywhere it should be.

Run before every push (exit code 1 if anything is missing):
    python -I tools/check_links.py

1. Every relative href / src in every page points at a file that exists
   (a folder link needs its index.html). External links are not fetched.
2. For each week in WEEKS (tools/bootcamp_nav.py):
   - AWS-Bootcamp/index.html links the week page,
   - the home page (index.html) names the week on the bootcamp tile,
   - the week page links every lesson in that week,
   - the previous week's page links forward to it,
   - every lesson page exists and carries the generated nav (<!-- awsq:top -->).
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from bootcamp_nav import V2, WEEKS  # noqa: E402

# Source code and downloads are not pages; their own links are not ours to check.
SKIP = ("zips/", ".git/", ".claude/", "data-dump/")
LINK = re.compile(r'\b(?:href|src)\s*=\s*"([^"]*)"', re.I)


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT).as_posix()
        if not rel.startswith(SKIP):
            yield p, rel


def broken_links():
    errors = []
    for p, rel in pages():
        s = p.read_text(encoding="utf-8", errors="replace")
        # links inside <script> are built at run time, so leave them out
        s = re.sub(r"<script\b.*?</script>", "", s, flags=re.S | re.I)
        for url in LINK.findall(s):
            url = html.unescape(url).strip()
            if not url or re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#|\$\{)", url, re.I):
                continue
            path = url.split("#", 1)[0].split("?", 1)[0]
            if not path:
                continue
            target = (ROOT / path.lstrip("/")) if path.startswith("/") else (p.parent / path)
            target = target.resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{rel}: broken link -> {url}")
    return errors


def week_links():
    errors = []
    hub = (ROOT / "AWS-Bootcamp" / "index.html").read_text(encoding="utf-8")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    prev = None
    for label, wdir, lessons in WEEKS:
        page = ROOT / "AWS-Bootcamp" / wdir / "index.html"
        if f'href="{wdir}/"' not in hub:
            errors.append(f"AWS-Bootcamp/index.html: no link to {label} ({wdir}/)")
        if label not in home:
            errors.append(f"index.html: the bootcamp tile does not mention {label}")
        if not page.exists():
            errors.append(f"AWS-Bootcamp/{wdir}/index.html: week page missing")
            continue
        s = page.read_text(encoding="utf-8")
        for folder, _, kind, title in lessons:
            if f'href="../{folder}/"' not in s:
                errors.append(f"AWS-Bootcamp/{wdir}/index.html: no card linking {kind} · {title} (../{folder}/)")
            for f in [folder] + ([f"{folder}-v2"] if folder in V2 else []):
                lp = ROOT / "AWS-Bootcamp" / f / "index.html"
                if not lp.exists():
                    errors.append(f"AWS-Bootcamp/{f}/index.html: lesson page missing")
                elif "<!-- awsq:top -->" not in lp.read_text(encoding="utf-8"):
                    errors.append(f"AWS-Bootcamp/{f}/index.html: no bootcamp nav; run python tools/bootcamp_nav.py")
        if prev:
            ps = (ROOT / "AWS-Bootcamp" / prev / "index.html").read_text(encoding="utf-8")
            if f'href="../{wdir}/"' not in ps:
                errors.append(f"AWS-Bootcamp/{prev}/index.html: no 'Next' link to {label} (../{wdir}/)")
        prev = wdir
    return errors


if __name__ == "__main__":
    errors = broken_links() + week_links()
    n = sum(1 for _ in pages())
    for e in errors:
        print("MISSING ", e)
    print(f"Checked {n} pages and {len(WEEKS)} bootcamp weeks: {len(errors)} problem(s).")
    sys.exit(1 if errors else 0)
