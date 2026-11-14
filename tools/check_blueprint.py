"""Check that every bootcamp and capstone page follows the site blueprint (exit code 1 if not).

    python -I tools/check_blueprint.py            # every page
    python -I tools/check_blueprint.py FOLDER...  # only these lesson / project folders (plus the hubs)

Structure only; the Opus verifier in the /ingest-dump skill checks how pages look and behave in a browser.

Lesson and project pages (AWS-Bootcamp/<folder>/, AWS-Capstone/<folder>/)
  - <meta charset>, <meta name="viewport">, <meta name="description">, a <title> carrying the brand
  - exactly one generated nav at the top and one at the bottom, top before bottom
  - pages whose nav sits inside their own <main> (INMAIN) carry a `.awsq{--q-acc:…}` colour override
  - every in-page link (href="#id") has a matching id
  - external scripts only from the CDNs the site allows
Week pages (AWS-Bootcamp/week-N/)
  - a recordings block, and one card per lesson in WEEKS order, each with number, kind line,
    title link, bullet list, lab line and footer; lessons with code show GitHub + zip links
Hubs
  - AWS-Bootcamp/index.html: exactly one "New" week card and one awsb-latest bar, both on the latest week
  - AWS-Capstone/index.html: a card linking every CAPSTONE project
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from bootcamp_nav import BRAND, CAP_BRAND, CAPSTONE, GITHUB, INMAIN, NOCODE, V2, WEEKS, ZIPS  # noqa: E402

CDNS = ("https://cdnjs.cloudflare.com/", "https://cdn.jsdelivr.net/npm/", "https://unpkg.com/",
        "https://cdn.tailwindcss.com", "https://code.jquery.com/")


def text(p):
    return p.read_text(encoding="utf-8", errors="replace")


def page_errors(rel, brand, inmain):
    p = ROOT / rel
    if not p.exists():
        return [f"{rel}: missing"]
    s = text(p)
    errs = []
    head = s.split("</head>", 1)[0]
    if not re.search(r"<meta\s+charset", head, re.I):
        errs.append("no <meta charset>")
    if 'name="viewport"' not in head:
        errs.append('no <meta name="viewport">')
    if 'name="description"' not in head:
        errs.append('no <meta name="description">')
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    if not m or brand not in m.group(1):
        errs.append(f"<title> does not end with the brand ({brand}); run python tools/bootcamp_nav.py")
    for tag in ("top", "bottom"):
        n = s.count(f"<!-- awsq:{tag} -->")
        if n != 1:
            errs.append(f"{n} awsq:{tag} navs (want exactly 1)")
    if -1 < s.find("<!-- awsq:bottom -->") < s.find("<!-- awsq:top -->"):
        errs.append("bottom nav comes before the top nav")
    if "<!-- awsq:top -->\n<!-- /awsq:top -->" in s:
        errs.append("nav markers are empty; run python tools/bootcamp_nav.py")
    if inmain and not re.search(r"\.awsq\s*\{[^}]*--q-acc", s):
        errs.append("nav sits inside <main> but the page has no `.awsq{--q-acc:…}` colour override")
    if inmain and 'class="mobile-toc"' not in s and re.search(r"\.mobile-toc\s*\{", s):
        errs.append("CSS styles a .mobile-toc menu but the page has none (no contents on phones)")
    if 'class="mobile-toc"' in s and "closest('details').open = false" not in s:
        errs.append("phone contents menu does not close after a tap (add the close-on-tap line)")
    body = re.sub(r"<script\b.*?</script>", "", s, flags=re.S | re.I)
    ids = set(re.findall(r'\bid\s*=\s*"([^"]+)"', body))
    for a in sorted(set(re.findall(r'href\s*=\s*"#([^"]+)"', body))):
        if a not in ids:
            errs.append(f'in-page link #{a} has no matching id')
    for src in re.findall(r'<script[^>]*\bsrc\s*=\s*"(https?://[^"]+)"', s, re.I):
        if not src.startswith(CDNS):
            errs.append(f"external script from an unapproved host: {src}")
    return [f"{rel}: {e}" for e in errs]


def week_errors(wdir, lessons):
    rel = f"AWS-Bootcamp/{wdir}/index.html"
    p = ROOT / rel
    if not p.exists():
        return [f"{rel}: missing"]
    s = text(p)
    errs = []
    tag = "recs:" + wdir.replace("-", "")
    if f"<!-- {tag} -->" not in s:
        errs.append(f"no <!-- {tag} --> recordings block")
    cards = re.findall(r'<article class="awsb-card"[^>]*>(.*?)</article>', s, re.S)
    linked = []
    for c in cards:
        m = re.search(r'<h3><a href="\.\./([^"/]+)/">', c)
        if not m:
            errs.append("a card has no <h3><a href=\"../folder/\"> title link")
            continue
        folder = m.group(1)
        linked.append(folder)
        for cls, what in (("awsb-num", "number"), ("awsb-ln", "kind line"), ("awsb-lab", "lab line"), ("awsb-foot", "footer")):
            if f'class="{cls}"' not in c:
                errs.append(f"card {folder}: no {what} (.{cls})")
        if "<ul>" not in c:
            errs.append(f"card {folder}: no bullet list")
        if folder not in NOCODE and (GITHUB.get(folder) or ZIPS.get(folder)):
            if "GitHub" not in c or ".zip" not in c:
                errs.append(f"card {folder}: has code but no GitHub + zip links")
    want = [f for f, *_ in lessons]
    lesson_cards = [f for f in linked if f in want]
    if lesson_cards != want:
        errs.append(f"lesson cards {lesson_cards} do not match WEEKS order {want}")
    return [f"{rel}: {e}" for e in errs]


def hub_errors():
    errs = []
    rel = "AWS-Bootcamp/index.html"
    s = text(ROOT / rel)
    latest = WEEKS[-1][1]
    new_cards = re.findall(r'<a class="awsb-day is-new" href="([^"]+)"', s)
    if new_cards != [f"{latest}/"]:
        errs.append(f'{rel}: "New" week cards {new_cards}, want exactly one on {latest}/')
    bars = re.findall(r'<a class="awsb-latest" href="([^"]+)"', s)
    if bars != [f"{latest}/"]:
        errs.append(f"{rel}: awsb-latest bars {bars}, want exactly one linking {latest}/")
    rel = "AWS-Capstone/index.html"
    s = text(ROOT / rel)
    for folder, step, title in CAPSTONE:
        if f'href="{folder}/"' not in s:
            errs.append(f"{rel}: no card for {step} · {title} ({folder}/)")
    return errs


def main(only):
    errs, n = [], 0
    for _, wdir, lessons in WEEKS:
        for folder, *_ in lessons:
            if only and folder not in only:
                continue
            for f in [folder] + ([f"{folder}-v2"] if folder in V2 else []):
                errs += page_errors(f"AWS-Bootcamp/{f}/index.html", BRAND, folder in INMAIN)
                n += 1
        if not only or any(f in only for f, *_ in lessons):
            errs += week_errors(wdir, lessons)
    for folder, *_ in CAPSTONE:
        if only and folder not in only:
            continue
        errs += page_errors(f"AWS-Capstone/{folder}/index.html", CAP_BRAND, False)
        n += 1
    errs += hub_errors()
    for e in errs:
        print("BLUEPRINT", e)
    print(f"Checked {n} lesson/project pages, the week pages and the hubs: {len(errs)} problem(s).")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(set(sys.argv[1:])))
