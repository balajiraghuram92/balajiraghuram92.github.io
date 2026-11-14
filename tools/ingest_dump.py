"""Sort what was dropped into data-dump/ into a plan: what is new, what the site already has, and where each piece goes.

Used by the /ingest-dump skill (.claude/skills/ingest-dump/SKILL.md). It only reads, unzips into
data-dump/.staging/ and writes a plan; it never edits the site and never runs anything it unzips.

    python -I tools/ingest_dump.py plan [--week N]   # unzip + classify; writes data-dump/.staging/plan.json
    python -I tools/ingest_dump.py record SRC DEST   # remember SRC's fingerprint as "on the site at DEST"
    python -I tools/ingest_dump.py remember [STAGED...]  # before the review commit: record the plan's new files
                                                     # (list staged paths that were left out, to skip them)
    python -I tools/ingest_dump.py done              # after the push: move sources to data-dump/_done/

How each file is labelled
    duplicate   the same bytes are already on the site, or were ingested before (tools/ingested.json)
    seen-title  an HTML page whose <title> matches a page already on the site: an older or updated copy, check by hand
    new         nothing like it yet

Where things go
    project     anything under a folder (or in a zip) whose name has "project" or "capstone" in it,
                → AWS-Capstone/<slug>/ and a "Week N projects" row on AWS-Capstone/index.html
    lesson      every other HTML page → AWS-Bootcamp/<slug>/ in Week N (default: the latest week in WEEKS)
    code        .py / .ipynb / requirements / .env.example / .md / data files next to a page: same item's code folder
"""
import hashlib
import html
import json
import pathlib
import re
import shutil
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DUMP = ROOT / "data-dump"
STAGE = DUMP / ".staging"
DONE = DUMP / "_done"
MANIFEST = ROOT / "tools" / "ingested.json"
sys.path.insert(0, str(ROOT / "tools"))
from bootcamp_nav import CAPSTONE, WEEKS  # noqa: E402

CODE_EXT = {".py", ".ipynb", ".txt", ".md", ".toml", ".cfg", ".yaml", ".yml", ".json", ".csv", ".sql", ".sh", ".js", ".ts"}
CODE_NAMES = {"requirements.txt", ".env.example", ".env.sample", "dockerfile", "makefile", "pyproject.toml"}
SECRET_NAMES = re.compile(r"^(\.env(\..*)?|.*\.(pem|key|p12|pfx)|credentials(\.json)?|id_rsa.*|secrets\..*)$", re.I)
JUNK = {"__pycache__", ".ipynb_checkpoints", ".venv", "venv", ".git", "node_modules", "__MACOSX", ".DS_Store", "Thumbs.db"}
PROJECT = re.compile(r"project|capstone", re.I)
SITE_DIRS = ["AWS-Bootcamp", "AWS-Capstone", "Learnings", "zips/Code", "Interview-Ready"]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}


def save_manifest(m):
    MANIFEST.write_text(json.dumps(dict(sorted(m.items())), indent=1) + "\n", encoding="utf-8")


def title_of(p):
    m = re.search(r"<title[^>]*>(.*?)</title>", p.read_text(encoding="utf-8", errors="replace"), re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(m.group(1))).strip() if m else ""


def h1_of(p):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", p.read_text(encoding="utf-8", errors="replace"), re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip() if m else ""


def norm_title(t):
    # site tabs read "<week> · <lesson> · <title> · <brand>"; compare on the words only
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def site_index():
    """Fingerprints and page titles of what is on the site now."""
    hashes, titles = {}, {}
    for d in SITE_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or any(part in JUNK for part in p.parts) or p.stat().st_size > 20_000_000:
                continue
            rel = p.relative_to(ROOT).as_posix()
            hashes.setdefault(sha(p), rel)
            if p.suffix.lower() == ".html" and not rel.startswith("zips/"):
                # the nav script rewrites <title>, but leaves the page's own <h1> alone
                for t in (norm_title(title_of(p)), norm_title(h1_of(p))):
                    if len(t) > 8:
                        titles[t] = rel
    return hashes, titles


def safe_extract(zp, dest, depth=0):
    """Unzip without letting any entry escape dest; unzip zips inside zips one level down."""
    with zipfile.ZipFile(zp) as z:
        for info in z.infolist():
            name = info.filename.replace("\\", "/")
            parts = [s for s in name.split("/") if s not in ("", ".")]
            if not parts or ".." in parts or name.startswith("/") or re.match(r"^[a-zA-Z]:", name):
                continue
            if any(s in JUNK for s in parts):
                continue
            target = dest.joinpath(*parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
            if target.suffix.lower() == ".zip" and depth < 1:
                inner = target.with_suffix("")
                inner.mkdir(exist_ok=True)
                safe_extract(target, inner, depth + 1)
                target.unlink()


def slug(text):
    words = re.sub(r"[^a-z0-9]+", " ", text.lower()).split()
    stop = {"the", "a", "an", "of", "and", "for", "to", "in", "on", "with", "by", "chapter", "code", "explainer", "lesson"}
    words = [w for w in words if w not in stop and not w.isdigit()][:5] or ["page"]
    return "-".join(words)


def sources():
    if not DUMP.exists():
        return []
    return sorted(p for p in DUMP.iterdir() if p.name not in (".staging", "_done", "README.md") and not p.name.startswith("."))


def plan(week=None):
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    hashes, titles = site_index()
    seen = load_manifest()
    week = week or int(re.sub(r"\D", "", WEEKS[-1][0]))
    taken = {p.name for d in ("AWS-Bootcamp", "AWS-Capstone") for p in (ROOT / d).iterdir() if p.is_dir()}

    items = []
    for src in sources():
        if src.is_file() and src.suffix.lower() == ".zip":
            root = STAGE / src.stem
            root.mkdir()
            safe_extract(src, root)
        elif src.is_dir():
            root = STAGE / src.name
            shutil.copytree(src, root, ignore=shutil.ignore_patterns(*JUNK))
        else:
            root = STAGE / "_loose"
            root.mkdir(exist_ok=True)
            shutil.copy2(src, root / src.name)

        files = [p for p in sorted(root.rglob("*")) if p.is_file()]
        pages = [p for p in files if p.suffix.lower() in (".html", ".htm")]
        for f in files:
            rel = f.relative_to(STAGE).as_posix()
            h = sha(f)
            entry = {"source": src.name, "staged": rel, "sha256": h, "bytes": f.stat().st_size}
            if SECRET_NAMES.match(f.name) and f.name not in (".env.example", ".env.sample"):
                entry.update(kind="secret", status="skip", note="secret-shaped file: never copied to the site")
            elif h in seen:
                entry.update(status="duplicate", on_site=seen[h])
            elif h in hashes:
                entry.update(status="duplicate", on_site=hashes[h])
            else:
                entry["status"] = "new"
            is_project = bool(PROJECT.search(rel))
            if f in pages:
                t = title_of(f)
                entry.update(kind="project-page" if is_project else "lesson-page", title=t)
                keys = [k for k in (norm_title(t), norm_title(h1_of(f))) if len(k) > 8]
                if entry["status"] == "new" and keys:
                    match = next((v for k, v in titles.items() for q in keys if q == k or (len(q) > 15 and (q in k or k in q))), None)
                    if match:
                        entry.update(status="seen-title", on_site=match)
                if entry["status"] == "duplicate":
                    items.append(entry)
                    continue
                s = slug(t or f.stem)
                base, n = s, 2
                while s in taken:
                    s, n = f"{base}-{n}", n + 1
                taken.add(s)
                entry["target"] = f"{'AWS-Capstone' if is_project else 'AWS-Bootcamp'}/{s}/index.html"
            elif "kind" not in entry:
                code = f.suffix.lower() in CODE_EXT or f.name.lower() in CODE_NAMES
                entry["kind"] = "code" if code else "asset"
                if is_project:
                    entry["kind"] = f"project-{entry['kind']}"
            items.append(entry)

    out = {"week": week, "next_lesson_number": 1 + max(int(s[1]) for _, _, ls in WEEKS for s in ls if s[1].isdigit()),
           "next_project_number": 1 + len(CAPSTONE), "items": items}
    (STAGE / "plan.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    print(f"Target: Week {week} · next lesson {out['next_lesson_number']} · next project P{out['next_project_number']}")
    if not items:
        print("data-dump/ is empty: nothing to do.")
    for e in items:
        where = e.get("target") or e.get("on_site") or ""
        extra = f"  ← {e['on_site']}" if e.get("on_site") and e.get("target") else ""
        print(f"{e['status']:<10} {e['kind']:<14} {e['staged']}  →  {where}{extra}")
    print(f"Plan written to {(STAGE / 'plan.json').relative_to(ROOT)}")


def record(src, dest):
    m = load_manifest()
    m[sha(pathlib.Path(src))] = dest
    save_manifest(m)


def remember(skipped=()):
    """Record every new file of the plan in tools/ingested.json (before the review commit, so it ships with it)."""
    p = STAGE / "plan.json"
    if not p.exists():
        sys.exit("No plan: run `plan` first.")
    m = load_manifest()
    for e in json.loads(p.read_text(encoding="utf-8"))["items"]:
        if e["status"] in ("new", "seen-title") and e["kind"] != "secret" and e["staged"] not in skipped:
            m[e["sha256"]] = e.get("target") or f"ingested from {e['source']}"
    save_manifest(m)
    print(f"{MANIFEST.relative_to(ROOT)}: {len(m)} fingerprints")


def done():
    """After the push: move the dropped sources to data-dump/_done/ and clear the staging folder."""
    DONE.mkdir(exist_ok=True)
    for src in sources():
        dest = DONE / src.name
        if dest.exists():
            dest = DONE / f"{src.stem}-{len(list(DONE.iterdir()))}{src.suffix}"
        shutil.move(str(src), str(dest))
        print("moved", src.name, "→", dest.relative_to(ROOT))
    shutil.rmtree(STAGE, ignore_errors=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    cmd = args[0] if args else "plan"
    if cmd == "plan":
        wk = int(args[args.index("--week") + 1]) if "--week" in args else None
        plan(wk)
    elif cmd == "record" and len(args) == 3:
        record(args[1], args[2])
    elif cmd == "remember":
        remember(args[1:])
    elif cmd == "done":
        done()
    else:
        sys.exit(__doc__)
