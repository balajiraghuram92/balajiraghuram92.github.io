"""Rebuild the navigation on every lesson page.

- Scaler AWS AI Bootcamp pages (AWS-Bootcamp/*): prev / next / all-lessons nav at
  the top and bottom, the AI-Infusion home button, and the class-recording link.
- AI Infusion pages (Learnings/*): adds the AI-Infusion home button to the
  existing lesson nav.

Safe to re-run. To add a recording, paste its URL into RECORDINGS and run:
    python tools/bootcamp_nav.py
"""
import html
import pathlib
import re
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (folder, step label, kind, title)
SEQ = [
    ("part-00-AWS-Revision", "0", "Part 00", "AWS Revision"),
    ("your-first-agent", "1", "Lesson 1", "Your first AI agent"),
    ("giving-agents-tools", "2", "Lesson 2", "Giving agents tools"),
    ("Agents-that-remember", "3", "Lesson 3", "Agents that remember"),
    ("agents-that-work-together", "4", "Lesson 4", "Agents that work together"),
    ("How-agents-talk", "5", "Lesson 5", "How agents talk"),
    ("shipping-agents-to-production", "6", "Lesson 6", "Shipping agents to production"),
    ("finance-section-1", "P1", "Project 1", "AI agents in finance"),
    ("finance-nps-project", "P2", "Project 2", "NPS analyst in a box"),
]

# Scaler class recording per page; an empty string shows "link coming soon".
RECORDINGS = {folder: "" for folder, *_ in SEQ}

# AI Infusion class recordings: (page, nav block) -> [(label, url)].
# The "mid" block on the Class 9 page is where Lesson 10 starts.
_REC = "https://www.scaler.com/meetings/i/{}/archive"
LEARN_RECORDINGS = {
    ("Class-1-AI-infusion/index.html", "top"): [("Class 1", _REC.format("ai-infused-learning-1-2"))],
    ("Class-1-AI-infusion/simulators.html", "top"): [("Class 1", _REC.format("ai-infused-learning-1-2"))],
    ("Class-2-AI-infusion/index.html", "top"): [("Class 2", _REC.format("ai-infused-learning-2-2"))],
    ("Class-3-4-AI-infusion/index.html", "top"): [("Class 3", _REC.format("ai-infused-learning-3")),
                                                  ("Class 4", "https://www.scaler.com/academy/mentee-dashboard/class/558449")],
    ("Class-5-AI-infusion/index.html", "top"): [("Class 5", _REC.format("ai-infused-learning-5"))],
    ("Class-6-AI-infusion/index.html", "top"): [("Class 6", _REC.format("ai-infused-learning-6"))],
    ("Class-7-AI-infusion/index.html", "top"): [("Class 7", _REC.format("ai-infused-learning-7"))],
    ("Class-8-AI-infusion/index.html", "top"): [("Class 8", _REC.format("ai-infused-learning-8"))],
    ("Class-9-Ai-Infusion/index.html", "top"): [("Class 9", _REC.format("ai-infused-learning-9"))],
    ("Class-9-Ai-Infusion/index.html", "mid"): [("Class 10 · part 1", _REC.format("ai-infused-learning-10")),
                                                ("Class 10 · part 2", _REC.format("ai-infused-learning-10-2"))],
}
LEARN_RECORDINGS[("Class-10-AI-infusion/index.html", "top")] = LEARN_RECORDINGS[("Class-9-Ai-Infusion/index.html", "mid")]

# Pages built on the finance template sit inside <main>, not the lesson .wrap.
FINANCE = {"finance-section-1", "finance-nps-project"}

BRAND = "Scaler AWS AI Bootcamp"

AWSQ_STYLE = """<style>
.awsq{--q-card:var(--card,var(--surface,#fff));--q-card2:var(--card-2,var(--surface-2,#f3f3f0));--q-rule:var(--rule,var(--line,#ddd));
  --q-ink:var(--ink,#1a1a1a);--q-muted:var(--muted,#666);--q-acc:var(--tool,var(--accent,#0b7f73));--q-acc-t:var(--tool-t,var(--accent-soft,#d6f2ee));
  --q-acc-ink:var(--tool-ink,var(--accent,#075a51));--q-cur:var(--brain,var(--gold,#b07600));--q-on:var(--card,var(--surface,#fff));
  --q-focus:var(--focus,var(--accent,#2958c4));--q-mono:var(--font-mono,"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace);
  max-width:72rem;margin:18px auto;padding:0 40px;font-family:var(--font-body,inherit)}
.awsq-box{background:var(--q-card);border:1px solid var(--q-rule);border-radius:12px;padding:12px 14px}
.awsq-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 9px}
.awsq-cap{display:block;margin:0;font:600 .7rem/1.4 var(--q-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--q-muted)}
.awsq-row{display:grid;grid-template-columns:1fr auto 1fr;gap:10px;align-items:stretch}
.awsq-l{display:flex;flex-direction:column;justify-content:center;gap:2px;min-width:0;padding:9px 13px;border-radius:9px;border:1px solid var(--q-rule);color:var(--q-ink);text-decoration:none;font-size:.95rem;line-height:1.3}
a.awsq-l:hover{border-color:var(--q-acc);text-decoration:none}
.awsq-next{text-align:right;align-items:flex-end}
.awsq-d{font:600 .7rem/1.3 var(--q-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--q-acc)}
.awsq-t{font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100%}
span.awsq-l{border-style:dashed;color:var(--q-muted)} span.awsq-l .awsq-d,span.awsq-l .awsq-t{color:var(--q-muted);font-weight:400}
a.awsq-home{display:flex;flex-direction:column;justify-content:center;align-items:center;padding:6px 12px;border-radius:9px;text-decoration:none;color:var(--q-ink);text-align:center;font-size:.85rem;line-height:1.3}
a.awsq-home:hover{background:var(--q-card2);text-decoration:none}
.awsq-home b{font:600 .7rem/1.3 var(--q-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--q-muted)}
.awsq-steps{display:flex;gap:5px;margin:11px 0 0;padding:0;list-style:none}
.awsq-steps li{flex:1 1 0;margin:0;padding:0;list-style:none}
.awsq-steps li::before{content:none}
.awsq-steps a{display:block;text-align:center;padding:4px 0;border-radius:5px;font:600 .75rem/1.4 var(--q-mono);text-decoration:none;background:var(--q-card2);border:1px solid var(--q-rule);color:var(--q-muted)}
.awsq-steps a.done{background:var(--q-acc-t);color:var(--q-acc-ink);border-color:transparent}
.awsq-steps a.cur{background:var(--q-cur);color:var(--q-on);border-color:transparent}
.awsq-steps a:hover{border-color:var(--q-acc);text-decoration:none}
.awsq-rec{display:flex;align-items:center;gap:10px;margin:11px 0 0;padding:9px 13px;border-radius:9px;border:1px solid var(--q-acc);background:var(--q-acc-t);
  color:var(--q-acc-ink);font-weight:700;font-size:.92rem;line-height:1.3;text-decoration:none}
a.awsq-rec:hover{text-decoration:none;filter:brightness(.97)}
.awsq-rec i{flex:none;display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--q-acc);color:var(--q-on);font-style:normal;font-size:.7rem}
.awsq-rec small{margin-left:auto;font:600 .68rem/1.3 var(--q-mono);letter-spacing:.08em;text-transform:uppercase;opacity:.8}
span.awsq-rec{border-style:dashed;background:transparent;color:var(--q-muted)} span.awsq-rec i{background:var(--q-rule);color:var(--q-muted)}
.awsq a:focus-visible{outline:2px solid var(--q-focus);outline-offset:2px}
.awsq a.aih{flex:none;display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:999px;background:var(--q-acc);color:var(--q-on);
  font:700 .74rem/1.2 var(--q-mono);letter-spacing:.04em;text-decoration:none;white-space:nowrap}
.awsq a.aih:hover{filter:brightness(1.08);text-decoration:none}
.awsq-bottom{padding:0 !important;margin:48px 0 8px;max-width:none}
.awsq-inmain{padding:0 !important;margin:0 0 28px;max-width:none}
@media (max-width:1100px){.awsq{padding:0 24px}}
@media (max-width:640px){.awsq{padding:0 16px}.awsq-t{white-space:normal;overflow-wrap:anywhere}.awsq-row{grid-template-columns:1fr 1fr}a.awsq-home{grid-column:1 / -1;grid-row:1;flex-direction:row;gap:8px}.awsq-rec small{display:none}}
@media print{.awsq{display:none}}
</style>"""

AIH_STYLE = """<!-- aih:style --><style>
.aiseq .aq-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 8px}
.aiseq .aq-head .aq-cap{margin:0}
.aiseq a.aih{flex:none;display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:999px;background:var(--aq-acc);color:var(--aq-bg);
  font:700 11.5px/1.2 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.04em;text-decoration:none;white-space:nowrap}
.aiseq a.aih:hover{filter:brightness(1.1);color:var(--aq-bg);text-decoration:none}
.aiseq .aq-recs{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 0}
.aiseq a.aq-rec{flex:1 1 200px;display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:5px;border:1px solid var(--aq-acc);
  color:var(--aq-ink);font-size:14px;font-weight:600;line-height:1.3;text-decoration:none}
.aiseq a.aq-rec:hover{background:var(--aq-off);color:var(--aq-ink);text-decoration:none}
.aiseq a.aq-rec i{flex:none;display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--aq-acc);color:var(--aq-bg);font-style:normal;font-size:10px}
.aiseq a.aq-rec small{margin-left:auto;font:600 10px/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--aq-dim)}
</style><!-- /aih:style -->"""

HOME_BTN = '<a class="aih" href="../../" title="Back to all AI-Infusion lessons">⌂ AI-Infusion</a>'


def write(p, s):
    """Write only when changed; retry briefly if another program has the file open."""
    if p.read_text(encoding="utf-8") == s:
        return
    for attempt in range(5):
        try:
            p.write_text(s, encoding="utf-8", newline="\n")
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.5)


def e(s):
    return html.escape(s, quote=True)


def caption(i):
    _, step, kind, _ = SEQ[i]
    if step == "0":
        return f"{BRAND} · Part 1 · Revision"
    if step.startswith("P"):
        n = sum(1 for s in SEQ if s[1].startswith("P"))
        return f"{BRAND} · Part 1 · {kind} of {n}"
    n = sum(1 for s in SEQ if s[1].isdigit() and s[1] != "0")
    return f"{BRAND} · Part 1 · {kind} of {n}"


def side(i, cls, label):
    if i < 0 or i >= len(SEQ):
        msg = "You're at the start" if cls == "awsq-prev" else "Part 2 · coming soon"
        return f'<span class="awsq-l {cls}"><span class="awsq-d">{label}</span><span class="awsq-t">{msg}</span></span>'
    folder, _, kind, title = SEQ[i]
    return (f'<a class="awsq-l {cls}" href="../{folder}/"><span class="awsq-d">{label}</span>'
            f'<span class="awsq-t">{e(kind)} · {e(title)}</span></a>')


def recording(folder):
    url = RECORDINGS.get(folder, "")
    if url:
        return (f'<a class="awsq-rec" href="{e(url)}" target="_blank" rel="noopener">'
                f'<i aria-hidden="true">▶</i>Watch the Scaler class recording<small>opens in a new tab</small></a>')
    return ('<span class="awsq-rec"><i aria-hidden="true">▶</i>Scaler class recording'
            '<small>link coming soon</small></span>')


def nav(i, where):
    folder = SEQ[i][0]
    steps = []
    for j, (f, step, kind, title) in enumerate(SEQ):
        cls = "cur" if j == i else ("done" if j < i else "")
        cur = ' aria-current="page"' if j == i else ""
        steps.append(f'<li><a class="{cls}" href="../{f}/" title="{e(kind)} · {e(title)}"{cur}>{step}</a></li>')
    extra = " awsq-inmain" if folder in FINANCE and where == "top" else ""
    return (f'<nav class="awsq awsq-{where}{extra}" aria-label="Bootcamp navigation ({where})"><div class="awsq-box">'
            f'<div class="awsq-head"><span class="awsq-cap">{e(caption(i))}</span>{HOME_BTN}</div>'
            f'<div class="awsq-row">{side(i - 1, "awsq-prev", "← Previous")}'
            f'<a class="awsq-home" href="../../#aws-bootcamp"><b>{BRAND}</b>all lessons</a>'
            f'{side(i + 1, "awsq-next", "Next →")}</div>'
            f'<ol class="awsq-steps" aria-label="All lessons">{"".join(steps)}</ol>'
            f'{recording(folder) if where == "top" else ""}</div></nav>')


def build_aws():
    for i, (folder, *_) in enumerate(SEQ):
        p = ROOT / "AWS-Bootcamp" / folder / "index.html"
        s = p.read_text(encoding="utf-8")
        top = f"<!-- awsq:top -->\n{AWSQ_STYLE}\n{nav(i, 'top')}\n<!-- /awsq:top -->\n"
        bottom = f"<!-- awsq:bottom -->\n{nav(i, 'bottom')}\n<!-- /awsq:bottom -->\n"
        s, n = re.subn(r"<!-- awsq:top -->.*?<!-- /awsq:top -->\n", lambda m: top, s, flags=re.S)
        if not n:
            if folder in FINANCE:
                s = s.replace('<main id="main">\n', '<main id="main">\n' + top, 1)
            else:
                s = s.replace('\n<div class="wrap">\n<section class="hero"', "\n" + top + '\n<div class="wrap">\n<section class="hero"', 1)
        s, n = re.subn(r"<!-- awsq:bottom -->.*?<!-- /awsq:bottom -->\n", lambda m: bottom, s, flags=re.S)
        if not n:
            anchor = "</main>\n" if folder in FINANCE else "\n<footer>"
            k = s.rfind(anchor)
            s = s[:k] + ("" if folder in FINANCE else "\n") + bottom + s[k + (0 if folder in FINANCE else 1):]
        assert s.count("<!-- awsq:top -->") == 1 and s.count("<!-- awsq:bottom -->") == 1, folder
        write(p, s)
        print("nav  ", p.relative_to(ROOT))


def build_learnings():
    for p in sorted((ROOT / "Learnings").glob("*/*.html")):
        s = p.read_text(encoding="utf-8")
        if "<!-- aih:style -->" in s:
            s = re.sub(r"<!-- aih:style -->.*?<!-- /aih:style -->", lambda m: AIH_STYLE, s, flags=re.S)
        else:
            s = s.replace("<!-- aiseq:top -->", "<!-- aiseq:top -->\n" + AIH_STYLE, 1)
        s = re.sub(r'(?<!<div class="aq-head">)(<span class="aq-cap">.*?</span>)(?!<a class="aih")',
                   lambda m: f'<div class="aq-head">{m.group(1)}{HOME_BTN}</div>', s)
        s = re.sub(r"<!-- aqrec -->.*?<!-- /aqrec -->", "", s)
        rel = p.relative_to(ROOT / "Learnings").as_posix()
        for where in ("top", "mid"):
            recs = LEARN_RECORDINGS.get((rel, where))
            if not recs:
                continue
            links = "".join(f'<a class="aq-rec" href="{e(url)}" target="_blank" rel="noopener"><i aria-hidden="true">▶</i>'
                            f'Watch the {e(label)} recording<small>Scaler</small></a>' for label, url in recs)
            block = f'<!-- aqrec --><div class="aq-recs">{links}</div><!-- /aqrec -->'
            m = re.search(rf'<div class="aiseq aiseq-{where}"[^\n]*?</ol>', s)
            assert m, (rel, where)
            s = s[:m.end()] + block + s[m.end():]
        write(p, s)
        print("home ", p.relative_to(ROOT))


def build_hub():
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")
    for folder, url in RECORDINGS.items():
        if url:
            chip = (f'<a class="awsb-rec" data-rec="{folder}" href="{e(url)}" target="_blank" rel="noopener">'
                    f'▶ Recording</a>')
        else:
            chip = f'<span class="awsb-rec" data-rec="{folder}">▶ Recording soon</span>'
        s = re.sub(rf'<(span|a) class="awsb-rec" data-rec="{re.escape(folder)}"[^>]*>.*?</\1>', lambda m: chip, s)
    seen, items = set(), []
    for recs in LEARN_RECORDINGS.values():
        for label, url in recs:
            if url not in seen:
                seen.add(url)
                items.append(f'<li><a href="{e(url)}" target="_blank" rel="noopener"><i aria-hidden="true">▶</i>{e(label)}</a></li>')
    block = ('<!-- recs:lessons --><div class="recs" id="recordings"><h3>Class recordings</h3>'
             '<p>Every AI-Infusion class on Scaler. Each lesson page also links its own recording at the top.</p>'
             f'<ul>{"".join(items)}</ul></div><!-- /recs:lessons -->')
    s = re.sub(r"<!-- recs:lessons -->.*?<!-- /recs:lessons -->", lambda m: block, s, flags=re.S)
    write(p, s)
    print("rec  ", p.relative_to(ROOT))


if __name__ == "__main__":
    build_hub()
    build_aws()
    build_learnings()
