# balajiraghuram92.github.io

Static GitHub Pages site (no build step): AI-Infusion lessons, the Scaler AWS AI Bootcamp,
the AWS AI Capstone projects and Interview Ready. Pushing `main` publishes it.

## Working here

- **Delegate in parallel.** When a task splits into independent pieces (one page each, auditing
  many folders, checking many links, drafting content from separate source files), spawn
  Haiku sub-agents (`model: "haiku"`) for them and run them in parallel to save time and tokens.
  Keep design decisions, cross-page edits to shared files (`assets/*.css`, `tools/*.py`) and the
  final check and push in the main session. Skip agents for work one script or a few edits can do.
- **Long-running checks go to a background Haiku agent**, so the main session keeps working and
  doesn't pay for the waiting: secret scans, link checks, checking the live site after a push.
  For secrets the agent runs `python -I tools/scan_secrets.py` (add `--history` for everything
  ever pushed) and reports the short summary.
- **Nav, recordings and project-file links are generated.** Edit the tables in
  `tools/bootcamp_nav.py` (weeks, `CAPSTONE`, `GITHUB`, `ZIPS`, `LINKS`), then run
  `python tools/bootcamp_nav.py`. Don't hand-edit the `<!-- awsq:* -->` / `<!-- aqfiles -->` blocks.
- **Adding a bootcamp week or lesson: link it everywhere.** A new week was once added without the
  hub links being checked. Every time:
  1. Lesson page at `AWS-Bootcamp/<folder>/index.html`. If it is a self-contained page with its own
     `<main>` (e.g. a code explainer with a side TOC), put empty `<!-- awsq:top -->`/`<!-- /awsq:top -->`
     markers just inside `<main>` and `<!-- awsq:bottom -->`/`<!-- /awsq:bottom -->` before its footer,
     add the folder to `INMAIN` (and to `NOCODE` if it has no code), and give `main .awsq` colour
     overrides that match the page.
  2. Add the lesson to its `WEEKn` list and the week to `WEEKS` (with an entry in `WEEK_RECORDINGS`,
     `[]` until the links exist) in `tools/bootcamp_nav.py`; code goes in `_CODE` and `tools/build_code_zips.py`.
  3. Week page `AWS-Bootcamp/week-N/index.html` (copy the previous week's), with a card per lesson
     and an empty `<!-- recs:weekN -->` block.
  4. Link the week from **all** of: `AWS-Bootcamp/index.html` (a `.awsb-day` card, the "New" badge
     and the `awsb-latest` bar; move both off the older week), the bootcamp tile in the home
     `index.html`, the previous week page's "Next" note, and the meta descriptions that list weeks.
  5. Run `python tools/build_code_zips.py`, `python tools/bootcamp_nav.py`, then
     **`python -I tools/check_links.py`** and **`python -I tools/check_blueprint.py`**: both must report
     0 problems. check_links checks every relative link on the site and that each week is linked from
     the hub, the home tile, the previous week and its own week page; check_blueprint checks each
     lesson / project page, week page and hub has the standard structure (nav top and bottom, meta
     tags, cards, in-page links, one "New" badge on the latest week).
  5b. **Verify with Opus before any review or push.** One `model: "opus"` agent (report only, no
     edits) opens every new or changed page on the preview next to a reference page of the same kind
     and checks: same blueprint, every nav link lands right, every TOC link / button / demo / copy
     button works, no console errors or failed requests, no horizontal scroll at phone width. Fix
     and re-run until it says `VERDICT: PASS`. The prompt is in `.claude/skills/ingest-dump/SKILL.md`.
  6. After the push, check the live page (GitHub Pages takes a minute or two to deploy, so an old
     copy right after a push is normal; reload with Ctrl+F5).
- **New material goes through `data-dump/` and `/ingest-dump`.** The user drops zips, folders, HTML,
  `.py` or notebooks in `data-dump/` (git-ignored) and runs `/ingest-dump [week]`
  (`.claude/skills/ingest-dump/SKILL.md`; `.claude/` is git-ignored, so the skill is local to this PC).
  `tools/ingest_dump.py plan` unzips and labels each file duplicate / seen-title / new using
  `tools/ingested.json` and the site's own files; Haiku agents build the pages; the main session
  wires nav, hubs and the Capstone "AWS Week N projects" row, runs the checks, commits, and **stops
  for the user's review. Never push without their yes.** Folder or zip names with "project" or
  "capstone" mean a Capstone project; everything else is a lesson in the week.
- **Code and zips.** Source code lives in `zips/Code/<Programme>/...`; `python tools/build_code_zips.py`
  rebuilds the downloadable zips in `zips/Code/Zips/`. "Browse the code" links point at
  `https://github.com/balajiraghuram92/balajiraghuram92.github.io/tree/main/zips/Code/...`.
- **Never publish secrets.** Before any push, run `tools/scan_secrets.py` (via a background Haiku agent).
  It scans HEAD, so commit first, then scan, then push. Also run `python -I tools/check_links.py`
  before every push.
  GitHub push protection blocks known key formats (it caught a Stripe docs key once): replace with
  a placeholder and amend; never Bypass.
  `zips/Code/Ai-Infusion/Lesson-7/` is a clone of github.com/22f1001418/InterviewIQ, holds a real
  `.env`, and is git-ignored on purpose.
- **Git** isn't on PATH; use GitHub Desktop's:
  `C:\Users\raghuram\AppData\Local\GitHubDesktop\app-3.6.10\resources\app\git\cmd\git.exe`.
- **Pushing: Claude pushes, after the user's yes.** `.claude/settings.local.json` pre-approves exactly
  `& "<that git.exe>" push origin main` (plus `fetch origin`, `status`, `log`); force pushes are
  denied. Order: commit locally, `scan_secrets.py`, `check_links.py` and `check_blueprint.py` clean,
  the Opus verifier's PASS for page changes, show the review, push
  only on the user's yes in chat, then `git fetch origin` and confirm `origin/main` has the commit.
  If the push says it can't read a username, Git Credential Manager has no saved GitHub sign-in:
  ask the user to run that push command once in their own terminal and sign in in the browser
  (GitHub Desktop's Push origin also works as a fallback). Never enter credentials for them.
- `_config.yml` keeps the source-code folders, `tools/` and these notes off the live site (smaller deploys).
  If you add a folder that pages must link to directly, check it is not excluded there.
- Open items are in `MIGRATION-TODO.md`.
