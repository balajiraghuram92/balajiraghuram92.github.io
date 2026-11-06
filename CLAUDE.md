# balajiraghuram92.github.io

Static GitHub Pages site (no build step): AI-Infusion lessons, the Scaler AWS AI Bootcamp,
the AWS AI Capstone projects and Interview Ready. Pushing `main` publishes it.

## Working here

- **Delegate in parallel.** When a task splits into independent pieces (one page each, auditing
  many folders, checking many links, drafting content from separate source files), spawn
  Haiku sub-agents (`model: "haiku"`) for them and run them in parallel to save time and tokens.
  Keep design decisions, cross-page edits to shared files (`assets/*.css`, `tools/*.py`) and the
  final check and push in the main session. Skip agents for work one script or a few edits can do.
- **Nav, recordings and project-file links are generated.** Edit the tables in
  `tools/bootcamp_nav.py` (weeks, `CAPSTONE`, `GITHUB`, `ZIPS`, `LINKS`), then run
  `python tools/bootcamp_nav.py`. Don't hand-edit the `<!-- awsq:* -->` / `<!-- aqfiles -->` blocks.
- **Code and zips.** Source code lives in `zips/Code/<Programme>/...`; `python tools/build_code_zips.py`
  rebuilds the downloadable zips in `zips/Code/Zips/`. "Browse the code" links point at
  `https://github.com/balajiraghuram92/balajiraghuram92.github.io/tree/main/zips/Code/...`.
- **Never publish secrets.** Before any push, scan staged files for `.env` and API keys.
  `zips/Code/Ai-Infusion/Lesson-7/` is a clone of github.com/22f1001418/InterviewIQ, holds a real
  `.env`, and is git-ignored on purpose.
- **Git** isn't on PATH; use GitHub Desktop's:
  `C:\Users\raghuram\AppData\Local\GitHubDesktop\app-3.6.10\resources\app\git\cmd\git.exe`.
- Open items are in `MIGRATION-TODO.md`.
