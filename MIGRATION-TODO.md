# Migration to neuralascent.top: open items

Everything below is a placeholder on the site today. Most of it is filled from one
file, [tools/bootcamp_nav.py](tools/bootcamp_nav.py): edit its tables, then run

```bash
python tools/bootcamp_nav.py
```

## 1. GitHub links for project files

Every lesson page has a **Project files** box, at the top and the bottom, with:

- **Browse the code**: opens the GitHub repo, so learners can read each script on its own.
- **Download all (.zip)**: the zip in `/zips` where there is one; otherwise GitHub's
  zip of the `main` branch once the repo link is in.

Placeholders show "GitHub link coming soon" and carry `data-todo="github"` in the HTML,
so `grep -r 'data-todo="github"'` lists every one still open.

To fill one, paste the repo URL into `GITHUB` in `tools/bootcamp_nav.py`:

| Key in `GITHUB` | Page | Zip on site now |
|---|---|---|
| `part-00-AWS-Revision` | Bootcamp Day 1 · Part 00 | none |
| `your-first-agent` | Bootcamp Day 1 · Lesson 1 | yes |
| `giving-agents-tools` | Bootcamp Day 1 · Lesson 2 | yes |
| `Agents-that-remember` | Bootcamp Day 1 · Lesson 3 | yes |
| `agents-that-work-together` | Bootcamp Day 1 · Lesson 4 | none |
| `How-agents-talk` | Bootcamp Day 1 · Lesson 5 | yes |
| `shipping-agents-to-production` | Bootcamp Day 1 · Lesson 6 | none |
| `finance-section-1` | Bootcamp Day 1 · Project 1 | none |
| `finance-nps-project` | Bootcamp Day 1 · Project 2 | none |
| `Class-1` … `Class-9` | AI-Infusion Lessons 1–10 (`Class-9` covers 9 and 10) | Classes 1, 2, 3-4, 5, 6 |

New zips go in `/zips` and into `ZIPS` in the same file. The Day 1 page cards still
say "solution zip soon" for Lessons 4 and 6 and both projects: swap those in
`AWS-Bootcamp/day-1/index.html` by hand.

**On the new site:** "Browse the code" can become an on-site file viewer that reads
the repo through the GitHub API, so learners never leave the site. Keep the
GitHub link as the fallback.

## 2. Bootcamp Day 2

- [ ] Add the Day 2 lesson pages under `AWS-Bootcamp/`.
- [ ] Build `AWS-Bootcamp/day-2/` from `day-1/`, and turn the Day 2 card on
      `AWS-Bootcamp/index.html` from "coming soon" into a link.
- [ ] Give Day 2 its own lesson list and recordings in `tools/bootcamp_nav.py`
      (Day 1 uses `SEQ` and `DAY1_RECORDINGS`).

## 3. Other placeholders

- [ ] Recording links: Day 1 and all 11 AI-Infusion classes are in. Class 4 points at a
      mentee-dashboard page, not a meetings archive.
- [ ] Lessons 4 and 6 and both finance projects are straight copies of the Scaler
      pages, without the pseudo-code toggles and practice questions the other lessons have.

## 4. Moving hosts

- All links between pages are relative, so the folders can move as they are.
- Shared styles live in `/assets` (`hub.css`, `site.css`, `bootcamp.css`, `learn-kit.*`).
- `index.html` sends old single-page anchors (`/#wsl`, `/#aws-bootcamp`, …) to their new pages.
