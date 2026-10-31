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
| `part-00-AWS-Revision` | Bootcamp Week 1 · Part 00 | none |
| `your-first-agent` | Bootcamp Week 1 · Lesson 1 | yes |
| `giving-agents-tools` | Bootcamp Week 1 · Lesson 2 | yes |
| `Agents-that-remember` | Bootcamp Week 1 · Lesson 3 | yes |
| `agents-that-work-together` | Bootcamp Week 1 · Lesson 4 | none |
| `How-agents-talk` | Bootcamp Week 1 · Lesson 5 | yes |
| `shipping-agents-to-production` | Bootcamp Week 1 · Lesson 6 | none |
| `finance-section-1` | Bootcamp Week 1 · Project 1 | none |
| `finance-nps-project` | Bootcamp Week 1 · Project 2 | none |
| `trip-buddy` | Bootcamp Week 2 · Project 1 | yes |
| `Class-1` … `Class-9` | AI-Infusion Lessons 1–10 (`Class-9` covers 9 and 10) | Classes 1, 2, 3-4, 5, 6 |

New zips go in `/zips` and into `ZIPS` in the same file. The Week 1 page cards still
say "solution zip soon" for Lessons 4 and 6 and both projects: swap those in
`AWS-Bootcamp/week-1/index.html` by hand.

**On the new site:** "Browse the code" can become an on-site file viewer that reads
the repo through the GitHub API, so learners never leave the site. Keep the
GitHub link as the fallback.

## 2. Bootcamp Week 2

- [x] `AWS-Bootcamp/week-2/` is live, with Project 1, Trip Buddy (`AWS-Bootcamp/trip-buddy/`,
      zip in `/zips/trip-buddy.zip`).
- [ ] Week 2 recordings: paste them into `WEEK_RECORDINGS["week-2"]` in `tools/bootcamp_nav.py`.
- [ ] More Week 2 projects: add each one to `WEEK2` in `tools/bootcamp_nav.py`, and a card on
      `AWS-Bootcamp/week-2/index.html`.

## 3. Other placeholders

- [ ] Recording links: Week 1 and all 11 AI-Infusion classes are in. Class 4 points at a
      mentee-dashboard page, not a meetings archive.
- [ ] Lessons 4 and 6 and both finance projects are straight copies of the Scaler
      pages, without the pseudo-code toggles and practice questions the other lessons have.

## 4. Moving hosts

- All links between pages are relative, so the folders can move as they are.
- Shared styles live in `/assets` (`hub.css`, `site.css`, `bootcamp.css`, `learn-kit.*`).
- `index.html` sends old single-page anchors (`/#wsl`, `/#aws-bootcamp`, …) to their new pages.
