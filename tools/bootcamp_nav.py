"""Rebuild the navigation, recordings and project-file links on every lesson page.

- Scaler AWS AI Bootcamp pages (AWS-Bootcamp/<lesson>/): prev / next / week nav at
  the top and bottom, the AI-Infusion home button, the class recordings and the
  Project files box. Also fills the recordings on each AWS-Bootcamp/week-N/ page.
- AI-Infusion pages (Learnings/*): the AI-Infusion home button, the class
  recordings and the Project files box in the existing lesson nav. Also fills
  the recordings list on AI-Infusion/.

Safe to re-run. Edit the tables below (recordings, GITHUB, ZIPS) and run:
    python tools/bootcamp_nav.py
"""
import html
import pathlib
import re
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Each week's lessons, in order: (folder, step label, kind, title)
WEEK1 = [
    ("part-00-AWS-Revision", "0", "Part 00", "AWS Revision"),
    ("your-first-agent", "1", "Lesson 1", "Your first AI agent"),
    ("giving-agents-tools", "2", "Lesson 2", "Giving agents tools"),
    ("Agents-that-remember", "3", "Lesson 3", "Agents that remember"),
]
WEEK2 = [
    ("agents-that-work-together", "4", "Lesson 4", "Agents that work together"),
    ("How-agents-talk", "5", "Lesson 5", "How agents talk"),
    ("shipping-agents-to-production", "6", "Lesson 6", "Shipping agents to production"),
    ("evals-observability-governance", "7", "Lesson 7", "Evals, observability and governance"),
]
WEEK3 = [
    ("llm-building-blocks", "8", "Lesson 8", "Building blocks of LLM systems"),
    ("agentic-bug-fixing", "9", "Lesson 9", "Agentic bug fixing"),
]
WEEK4 = [
    ("observability-explained", "10", "Lesson 10", "Observability, explained simply"),
    ("observability-langsmith", "11", "Lesson 11", "Observability demo with LangSmith"),
    ("guardrails-explained", "12", "Lesson 12", "Guardrails, explained simply"),
    ("guardrails-nemo", "13", "Lesson 13", "Guardrails demo with NeMo"),
    ("inventory-agent", "14", "Lesson 14", "Inventory agent, v0 to v7"),
]
# Week 5: lessons, then the homework reading ("H" steps, numbered within the week)
WEEK5 = [
    ("memory-explained", "15", "Lesson 15", "Memory, explained simply"),
    ("mcp-explained", "16", "Lesson 16", "MCP, explained simply"),
    ("memory-mcp-code", "17", "Lesson 17", "Memory and MCP in code"),
    ("evals-explained", "18", "Lesson 18", "Evals, explained simply"),
    ("component-evals", "19", "Lesson 19", "Component evals in code"),
    # hands-on: RAG and tool calling (code-first workshop modules)
    ("embeddings-reranking", "20", "Lesson 20", "Embeddings, similarity and reranking"),
    ("chunking-hyde", "21", "Lesson 21", "Chunking strategies and HyDE"),
    ("tool-calling-basics", "22", "Lesson 22", "Tool calling basics"),
    ("inventory-agent-steps", "23", "Lesson 23", "Inventory agent, step by step"),
    ("ai-evals-why", "H1", "Homework 1", "AI Evals 1 · Why AI evals"),
    ("ai-evals-methods", "H2", "Homework 2", "AI Evals 2 · Evaluation methods"),
    ("ai-evals-quantitative", "H3", "Homework 3", "AI Evals 3 · Metrics, judges, test sets"),
    ("ai-evals-after-launch", "H4", "Homework 4", "AI Evals 4 · After launch"),
    ("ai-evals-governance", "H5", "Homework 5", "AI Evals 5 · Tools and governance"),
]
# (label, folder of the week page, lessons)
WEEKS = [("Week 1", "week-1", WEEK1), ("Week 2", "week-2", WEEK2), ("Week 3", "week-3", WEEK3), ("Week 4", "week-4", WEEK4),
         ("Week 5", "week-5", WEEK5)]
# Every page in order across the weeks: (folder, step, kind, title, week label, week folder)
SEQ = [(*item, week, wdir) for week, wdir, items in WEEKS for item in items]

# AWS AI Capstone projects (AWS-Capstone/<folder>/), in order: (folder, step, title).
# Row 1: the bootcamp projects; row 2: the RAG and research courses; row 3: the capstone itself.
CAP_BRAND = "AWS AI Capstone"
CAPSTONE = [
    ("trip-buddy", "P1", "Trip Buddy"),
    ("finance-section-1", "P2", "AI agents in finance"),
    ("finance-nps-project", "P3", "NPS analyst in a box"),
    ("production-rag", "P4", "Production RAG from scratch"),
    ("agentic-rag", "P5", "Agentic RAG"),
    ("deep-search-agents", "P6", "Deep search agents"),
    ("vendor-risk-assessor", "P7", "Capstone · AI vendor risk assessor"),
    # row 4: AWS Week 5 projects (Parts 2-7 of the AI agents in finance course; Part 1 is P2), and a design case study
    ("finance-part-2-frameworks", "P8", "Finance Part 2 · Agent frameworks"),
    ("finance-part-3-deep-search", "P9", "Finance Part 3 · Deep search"),
    ("finance-part-4-reasoning", "P10", "Finance Part 4 · Reasoning paradigms"),
    ("finance-part-5-teams", "P11", "Finance Part 5 · Teams of agents"),
    ("finance-part-6-agentic-rag", "P12", "Finance Part 6 · Agentic RAG"),
    ("finance-part-7-production", "P13", "Finance Part 7 · Evaluation and production"),
    ("adaptive-learning-case-study", "P14", "Case study · Adaptive learning app"),
]

# Lessons that keep Scaler's original page at <folder>/ and our reworked page at <folder>-v2/.
# The bottom nav on each links to the other version.
V2 = {"your-first-agent", "giving-agents-tools", "Agents-that-remember", "agents-that-work-together",
      "How-agents-talk", "shipping-agents-to-production", "evals-observability-governance"}
# The same for AI-Infusion classes: the original (Classes 1-6 from their zips, 7-9 as written before the
# pseudo code and quizzes went in) at Learnings/<folder>/, and the page with them at <folder>-v2/.
LEARN_V2 = {"Class-1-AI-infusion", "Class-2-AI-infusion", "Class-3-4-AI-infusion", "Class-5-AI-infusion", "Class-6-AI-infusion",
            "Class-7-AI-infusion", "Class-8-AI-infusion", "Class-9-Ai-Infusion"}

_REC = "https://www.scaler.com/meetings/i/{}/archive"

# Bootcamp recordings: shown on each week's page and on every lesson of that week.
WEEK_RECORDINGS = {
    "week-1": [
        ("Week 1 · session 1", _REC.format("ai-bootcamp-1")),
        ("Week 1 · session 2", _REC.format("ai-bootcamp-2")),
    ],
    "week-2": [
        ("Week 2 · session 1", _REC.format("ai-bootcamp-3")),
        ("Week 2 · session 2", _REC.format("ai-bootcamp-4")),
    ],
    # an empty list shows "link coming soon"
    "week-3": [],
    "week-4": [],
    "week-5": [],
}
RECORDINGS = {folder: WEEK_RECORDINGS[wdir] for folder, *_, wdir in SEQ}

# AI-Infusion class recordings: (page, nav block) -> [(label, url)].
# The "mid" block on the Class 9 page is where Lesson 10 starts.
# The Scaler meeting slugs run one ahead from Class 4 on (Class 4 is ai-infused-learning-5).
LEARN_RECORDINGS = {
    ("Class-1-AI-infusion/index.html", "top"): [("Class 1", "https://www.scaler.com/meetings/i/ai-infused-learning-1-2/")],
    ("Class-1-AI-infusion/simulators.html", "top"): [("Class 1", "https://www.scaler.com/meetings/i/ai-infused-learning-1-2/")],
    ("Class-2-AI-infusion/index.html", "top"): [("Class 2", _REC.format("ai-infused-learning-2-2"))],
    ("Class-3-4-AI-infusion/index.html", "top"): [("Class 3", _REC.format("ai-infused-learning-3")),
                                                  ("Class 4", _REC.format("ai-infused-learning-5"))],
    ("Class-5-AI-infusion/index.html", "top"): [("Class 5", _REC.format("ai-infused-learning-6"))],
    ("Class-6-AI-infusion/index.html", "top"): [("Class 6", _REC.format("ai-infused-learning-7"))],
    ("Class-7-AI-infusion/index.html", "top"): [("Class 7", _REC.format("ai-infused-learning-8"))],
    ("Class-8-AI-infusion/index.html", "top"): [("Class 8", _REC.format("ai-infused-learning-9"))],
    ("Class-9-Ai-Infusion/index.html", "top"): [("Class 9", _REC.format("ai-infused-learning-10"))],
    ("Class-9-Ai-Infusion/index.html", "mid"): [("Class 10", _REC.format("ai-infused-learning-10-2"))],
}
LEARN_RECORDINGS[("Class-10-AI-infusion/index.html", "top")] = LEARN_RECORDINGS[("Class-9-Ai-Infusion/index.html", "mid")]

# AI-Infusion tab titles, named as in the lesson nav. Each page's tab reads "<this> · AI-Infusion".
LEARN_TITLES = {
    "Class-1-AI-infusion/index.html": "Lesson 1 · Build & ship your first AI app",
    "Class-1-AI-infusion/simulators.html": "Lesson 1 · Interactive simulators",
    "Class-2-AI-infusion/index.html": "Lesson 2 · LangChain & your first agent",
    "Class-3-4-AI-infusion/index.html": "Lessons 3–4 · RAG: give your AI a library",
    "Class-5-AI-infusion/index.html": "Lesson 5 · Dockerize everything",
    "Class-6-AI-infusion/index.html": "Lesson 6 · AI agents on AWS",
    "Class-7-AI-infusion/index.html": "Lesson 7 · The interview coach",
    "Class-8-AI-infusion/index.html": "Lesson 8 · The shipment exception desk",
    "Class-9-Ai-Infusion/index.html": "Lessons 9–10 · The Refund Bench",
    "Class-10-AI-infusion/index.html": "Lesson 10 · Build & evaluate the bench",
}

# Project files. Keys are AWS-Bootcamp folders, AWS-Capstone folders or AI-Infusion classes.
# Code lives in this site's own repo under zips/Code/; tools/build_code_zips.py builds the zips in
# zips/Code/Zips/. An empty string shows "GitHub link coming soon".
_REPO = "https://github.com/balajiraghuram92/balajiraghuram92.github.io/tree/main/zips/Code"
_CAP_REPO = f"{_REPO}/Capstone-Projects"
# page key -> (folder under zips/Code, zip in zips/Code/Zips)
_CODE = {
    "part-00-AWS-Revision": ("Aws-Bootcamp/section-00-AWS-Revision", "aws-bootcamp-section-00-aws-revision"),
    "your-first-agent": ("Aws-Bootcamp/section-01-your-first-agent", "aws-bootcamp-section-01-your-first-agent"),
    "giving-agents-tools": ("Aws-Bootcamp/section-02-agent-tools", "aws-bootcamp-section-02-agent-tools"),
    "Agents-that-remember": ("Aws-Bootcamp/section-03-agent-memory", "aws-bootcamp-section-03-agent-memory"),
    "agents-that-work-together": ("Aws-Bootcamp/section-04-multi-agent-patterns", "aws-bootcamp-section-04-multi-agent-patterns"),
    "How-agents-talk": ("Aws-Bootcamp/section-05-mcp-and-a2a", "aws-bootcamp-section-05-mcp-and-a2a"),
    "shipping-agents-to-production": ("Aws-Bootcamp/section-06-production-deployment", "aws-bootcamp-section-06-production-deployment"),
    "evals-observability-governance": ("Aws-Bootcamp/section-07-evals-observability-governance", "aws-bootcamp-section-07-evals-observability-governance"),
    "agentic-bug-fixing": ("Aws-Bootcamp/section-08-agentic-bug-fixing", "aws-bootcamp-section-08-agentic-bug-fixing"),
    "observability-langsmith": ("Aws-Bootcamp/section-11-observability-langsmith", "aws-bootcamp-section-11-observability-langsmith"),
    "guardrails-nemo": ("Aws-Bootcamp/section-13-guardrails-nemo", "aws-bootcamp-section-13-guardrails-nemo"),
    "inventory-agent": ("Aws-Bootcamp/section-14-inventory-agent", "aws-bootcamp-section-14-inventory-agent"),
    "memory-mcp-code": ("Aws-Bootcamp/section-17-memory-mcp", "aws-bootcamp-section-17-memory-mcp"),
    "component-evals": ("Aws-Bootcamp/section-19-component-evals", "aws-bootcamp-section-19-component-evals"),
    "embeddings-reranking": ("Aws-Bootcamp/section-20-embeddings-reranking", "aws-bootcamp-section-20-embeddings-reranking"),
    "chunking-hyde": ("Aws-Bootcamp/section-21-chunking-hyde", "aws-bootcamp-section-21-chunking-hyde"),
    "tool-calling-basics": ("Aws-Bootcamp/section-22-tool-calling", "aws-bootcamp-section-22-tool-calling"),
    "inventory-agent-steps": ("Aws-Bootcamp/section-23-inventory-agent-steps", "aws-bootcamp-section-23-inventory-agent-steps"),
    # the five AI Evals homework chapters share one code folder
    **{f: ("Aws-Bootcamp/homework-ai-evals-in-practice", "aws-bootcamp-homework-ai-evals-in-practice")
       for f in ("ai-evals-why", "ai-evals-methods", "ai-evals-quantitative", "ai-evals-after-launch", "ai-evals-governance")},
    "Class-1": ("Ai-Infusion/lesson-1", "ai-infusion-lesson-1"),
    "Class-2": ("Ai-Infusion/lesson-2", "ai-infusion-lesson-2"),
    "Class-3-4": ("Ai-Infusion/lesson-3", "ai-infusion-lesson-3-4"),
    "Class-5": ("Ai-Infusion/lesson-5", "ai-infusion-lesson-5"),
    "Class-6": ("Ai-Infusion/Lesson-6", "ai-infusion-lesson-6"),
    "Class-7": (None, "ai-infusion-lesson-7"),
    "Class-9": ("Ai-Infusion/Lesson-9", "ai-infusion-lesson-9"),
    "Class-10": ("Ai-Infusion/Lesson-10", "ai-infusion-lesson-10"),
    "production-rag": ("Capstone-Projects/Production-RAG-Course-Shivank-Agrawal/code", "Production-RAG-Course-Shivank-Agrawal-code"),
    "agentic-rag": ("Capstone-Projects/Agentic_RAG_Study_Kit/code", "Agentic_RAG_Study_Kit-code"),
    "deep-search-agents": ("Capstone-Projects/shivank-deep-search-agent/code", "shivank-deep-search-agent-code"),
    "vendor-risk-assessor": ("Capstone-Projects/project-vendor-risk-assessor/code", "project-vendor-risk-assessor-code"),
}
GITHUB = {
    **{folder: "" for folder, *_ in SEQ},
    **{folder: "" for folder, *_ in CAPSTONE},
    **{f"Class-{n}": "" for n in ("1", "2", "3-4", "5", "6", "7", "8", "9", "10")},
    **{key: f"{_REPO}/{src}" for key, (src, _) in _CODE.items() if src},
    "trip-buddy": "https://github.com/balajiraghuram92/Scaler-AI-Infusion-Bootcamp/tree/main/excersices/Lab-project/Trip-Buddy",
    # Lesson 7 is its own repo (InterviewIQ); the site keeps a zip of it
    "Class-7": "https://github.com/22f1001418/InterviewIQ",
}
# Zips under /zips, served from this site, so the button downloads in one click.
ZIPS = {
    **{key: f"Code/Zips/{z}.zip" for key, (_, z) in _CODE.items()},
    "trip-buddy": "HTML/trip-buddy.zip",
}
# Extra links in the Project files box: (label, small note, url). Slides are linked, not copied in.
LINKS = {
    "evals-observability-governance": [
        ("▦ Session 7 slides", "opens in a new tab", "https://scaler2101.github.io/Section7.github.io/#/1/0"),
        ("↗ Original lesson", "Scaler", "https://scaler-content.github.io/evals-observability-governance/"),
    ],
}

# Pages built on the finance template sit inside <main>, not the lesson .wrap.
FINANCE = {"finance-section-1", "finance-nps-project", "trip-buddy", "finance-part-2-frameworks", "finance-part-3-deep-search",
           "finance-part-4-reasoning", "finance-part-5-teams", "finance-part-6-agentic-rag", "finance-part-7-production"}
# Pages whose nav sits inside their own padded <main> (the finance ones, plus code explainers with a side TOC).
# The explainers carry the awsq markers by hand: top just inside <main>, bottom before <footer>.
INMAIN = FINANCE | {"llm-building-blocks", "agentic-bug-fixing", "observability-explained", "observability-langsmith",
                    "guardrails-explained", "guardrails-nemo", "inventory-agent", "memory-explained", "mcp-explained",
                    "memory-mcp-code", "evals-explained", "component-evals", "ai-evals-why", "ai-evals-methods",
                    "ai-evals-quantitative", "ai-evals-after-launch", "ai-evals-governance", "adaptive-learning-case-study",
                    "embeddings-reranking", "chunking-hyde", "tool-calling-basics", "inventory-agent-steps"}
# Reading chapters with no code: no Project files box.
NOCODE = {"llm-building-blocks", "observability-explained", "guardrails-explained", "memory-explained", "mcp-explained",
          "evals-explained", "finance-part-2-frameworks", "finance-part-3-deep-search", "finance-part-4-reasoning",
          "finance-part-5-teams", "finance-part-6-agentic-rag", "finance-part-7-production", "adaptive-learning-case-study"}

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
.awsq-recs{display:flex;flex-wrap:wrap;gap:8px;margin:11px 0 0}
.awsq-rec{flex:1 1 220px;display:flex;align-items:center;gap:10px;padding:9px 13px;border-radius:9px;border:1px solid var(--q-acc);background:var(--q-acc-t);
  color:var(--q-acc-ink);font-weight:700;font-size:.92rem;line-height:1.3;text-decoration:none}
a.awsq-rec:hover{text-decoration:none;filter:brightness(.97)}
.awsq-rec i{flex:none;display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--q-acc);color:var(--q-on);font-style:normal;font-size:.7rem}
.awsq-rec small{margin-left:auto;font:600 .68rem/1.3 var(--q-mono);letter-spacing:.08em;text-transform:uppercase;opacity:.8}
.awsq-files{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:11px 0 0;padding:10px 0 0;border-top:1px dashed var(--q-rule)}
.awsq-files > b{margin-right:4px;font:600 .7rem/1.3 var(--q-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--q-muted)}
.awsq-fb{display:inline-flex;align-items:center;gap:7px;padding:6px 12px;border-radius:999px;border:1px solid var(--q-rule);color:var(--q-ink);
  font-size:.85rem;font-weight:700;line-height:1.3;text-decoration:none}
a.awsq-fb:hover{border-color:var(--q-acc);text-decoration:none}
.awsq-fb small{font:600 .66rem/1.3 var(--q-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--q-muted)}
span.awsq-fb{border-style:dashed;color:var(--q-muted);font-weight:600}
.awsq a:focus-visible{outline:2px solid var(--q-focus);outline-offset:2px}
.awsq a.aih{flex:none;display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:999px;background:var(--q-acc);color:var(--q-on);
  font:700 .74rem/1.2 var(--q-mono);letter-spacing:.04em;text-decoration:none;white-space:nowrap}
.awsq a.aih:hover{filter:brightness(1.08);text-decoration:none}
.awsq-ver{display:flex;justify-content:flex-end;margin:11px 0 0;padding:10px 0 0;border-top:1px dashed var(--q-rule)}
a.awsq-vl{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;border:1px solid var(--q-acc);color:var(--q-acc-ink);
  font-size:.85rem;font-weight:700;line-height:1.3;text-decoration:none}
a.awsq-vl:hover{background:var(--q-acc-t);text-decoration:none}
.awsq-vl small{font:600 .66rem/1.3 var(--q-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--q-muted)}
.awsq-bottom{padding:0 !important;margin:48px 0 8px;max-width:none}
.awsq-inmain{padding:0 !important;margin:0 0 28px;max-width:none}
@media (max-width:1100px){.awsq{padding:0 24px}}
@media (max-width:640px){.awsq-steps{flex-wrap:wrap}.awsq-steps li{flex:1 0 28px}.awsq{padding:0 16px}.awsq-t{white-space:normal;overflow-wrap:anywhere}.awsq-row{grid-template-columns:1fr 1fr}a.awsq-home{grid-column:1 / -1;grid-row:1;flex-direction:row;gap:8px}a.awsq-rec small{display:none}}
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
.aiseq .aq-files{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:10px 0 0;padding:9px 0 0;border-top:1px dashed var(--aq-line)}
.aiseq .aq-files > b{margin-right:4px;font:600 10.5px/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--aq-dim)}
.aiseq .aq-fb{display:inline-flex;align-items:center;gap:7px;padding:5px 11px;border-radius:999px;border:1px solid var(--aq-line);color:var(--aq-ink);
  font-size:13px;font-weight:600;line-height:1.3;text-decoration:none}
.aiseq a.aq-fb:hover{border-color:var(--aq-acc);color:var(--aq-ink);text-decoration:none}
.aiseq .aq-fb small{font:600 10px/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--aq-dim)}
.aiseq span.aq-fb{border-style:dashed;color:var(--aq-dim);font-weight:500}
.aiseq .aq-ver{display:flex;justify-content:flex-end;margin:10px 0 0;padding:9px 0 0;border-top:1px dashed var(--aq-line)}
.aiseq a.aq-vl{display:inline-flex;align-items:center;gap:8px;padding:5px 11px;border-radius:999px;border:1px solid var(--aq-acc);color:var(--aq-ink);
  font-size:13px;font-weight:600;line-height:1.3;text-decoration:none}
.aiseq a.aq-vl:hover{background:var(--aq-off);color:var(--aq-ink);text-decoration:none}
.aiseq .aq-vl small{font:600 10px/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--aq-dim)}
</style><!-- /aih:style -->"""

HOME_BTN = '<a class="aih" href="../../" title="Back to the AI-Infusion home page">⌂ AI-Infusion</a>'


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


def files_box(key, cls):
    """Project files: browse the code on GitHub, and download it all as a zip.

    cls is the class prefix of the nav it sits in ("awsq" or "aq").
    """
    if key in NOCODE:
        return ""
    repo = GITHUB.get(key, "").rstrip("/")
    zip_name = ZIPS.get(key, "")
    fb = f"{cls}-fb"
    if repo:
        browse = (f'<a class="{fb}" href="{e(repo)}" target="_blank" rel="noopener">&lt;/&gt; Browse the code'
                  f'<small>GitHub</small></a>')
    else:
        browse = f'<span class="{fb}" data-todo="github">&lt;/&gt; Browse the code<small>GitHub link coming soon</small></span>'
    if zip_name:
        download = (f'<a class="{fb}" href="../../zips/{e(zip_name)}" download>⬇ Download all'
                    f'<small>.zip</small></a>')
    elif repo:
        download = (f'<a class="{fb}" href="{e(repo)}/archive/refs/heads/main.zip">⬇ Download all'
                    f'<small>.zip from GitHub</small></a>')
    else:
        download = f'<span class="{fb}" data-todo="github">⬇ Download all<small>coming soon</small></span>'
    extra = "".join(f'<a class="{fb}" href="{e(url)}" target="_blank" rel="noopener">{e(label)}<small>{e(note)}</small></a>'
                    for label, note, url in LINKS.get(key, []))
    return f'<div class="{cls}-files"><b>Project files</b>{browse}{download}{extra}</div>'


def week_items(wdir):
    return [s for s in SEQ if s[5] == wdir]


def href(folder, v2):
    """On a v2 page, prev / next and the step dots stay on v2 wherever a lesson has one."""
    return f"{folder}-v2" if v2 and folder in V2 else folder


def caption(i, v2=False):
    _, step, kind, _, week, wdir = SEQ[i]
    tag = " · v2" if v2 else ""
    if step == "0":
        return f"{BRAND} · {week} · Revision{tag}"
    if step[0] in "PH":
        # projects and homework are numbered within their week
        n = sum(1 for s in week_items(wdir) if s[1][0] == step[0])
        return f"{BRAND} · {week} · {kind} of {n}{tag}"
    # lessons are numbered across the whole course, so count them across every week
    n = max(int(s[1]) for s in SEQ if s[1].isdigit())
    return f"{BRAND} · {week} · {kind} of {n}{tag}"


def version_link(folder, v2):
    if folder not in V2:
        return ""
    if v2:
        link = f'<a class="awsq-vl" href="../{folder}/">← Original version<small>as taught on Scaler</small></a>'
    else:
        link = f'<a class="awsq-vl" href="../{folder}-v2/">Read the v2 version →<small>reworked edition</small></a>'
    return f'<div class="awsq-ver">{link}</div>'


def side(i, cur_week, cls, label, v2=False):
    if i < 0 or i >= len(SEQ):
        # the capstone projects are their own section of the site, so the bootcamp simply ends here
        msg = "You're at the start" if i < 0 else "End of the bootcamp · more weeks coming soon"
        return f'<span class="awsq-l {cls}"><span class="awsq-d">{label}</span><span class="awsq-t">{msg}</span></span>'
    folder, _, kind, title, week, _ = SEQ[i]
    # name the week when prev / next crosses into another one
    where = f"{e(week)} · " if week != cur_week else ""
    return (f'<a class="awsq-l {cls}" href="../{href(folder, v2)}/"><span class="awsq-d">{label}</span>'
            f'<span class="awsq-t">{where}{e(kind)} · {e(title)}</span></a>')


def recordings(folder):
    recs = RECORDINGS.get(folder) or []
    if not recs:
        return ('<div class="awsq-recs"><span class="awsq-rec"><i aria-hidden="true">▶</i>Scaler class recording'
                '<small>link coming soon</small></span></div>')
    links = "".join(f'<a class="awsq-rec" href="{e(url)}" target="_blank" rel="noopener">'
                    f'<i aria-hidden="true">▶</i>Watch {e(label)}<small>Scaler</small></a>' for label, url in recs)
    return f'<div class="awsq-recs">{links}</div>'


def nav(i, where, v2=False):
    folder, *_, week, wdir = SEQ[i]
    steps = []
    for j, (f, step, kind, title, _, d) in enumerate(SEQ):
        if d != wdir:
            continue
        cls = "cur" if j == i else ("done" if j < i else "")
        cur = ' aria-current="page"' if j == i else ""
        steps.append(f'<li><a class="{cls}" href="../{href(f, v2)}/" title="{e(kind)} · {e(title)}"{cur}>{step}</a></li>')
    extra = " awsq-inmain" if folder in INMAIN and where == "top" else ""
    every ="all projects" if all(s[1].startswith("P") for s in week_items(wdir)) else "all lessons"
    return (f'<nav class="awsq awsq-{where}{extra}" aria-label="Bootcamp navigation ({where})"><div class="awsq-box">'
            f'<div class="awsq-head"><span class="awsq-cap">{e(caption(i, v2))}</span>{HOME_BTN}</div>'
            f'<div class="awsq-row">{side(i - 1, week, "awsq-prev", "← Previous", v2)}'
            f'<a class="awsq-home" href="../{wdir}/"><b>{BRAND}</b>{e(week)} · {every}</a>'
            f'{side(i + 1, week, "awsq-next", "Next →", v2)}</div>'
            f'<ol class="awsq-steps" aria-label="All lessons">{"".join(steps)}</ol>'
            f'{recordings(folder) if where == "top" else ""}{files_box(folder, "awsq")}'
            f'{version_link(folder, v2) if where == "bottom" else ""}</div></nav>')


def set_title(s, title):
    """Every lesson's tab reads "<lesson> · <name> · <site>"."""
    s, n = re.subn(r"<title>.*?</title>", lambda m: f"<title>{e(title)}</title>", s, count=1, flags=re.S)
    assert n == 1
    return s


def build_aws():
    pages = [(i, False) for i in range(len(SEQ))] + [(i, True) for i, s in enumerate(SEQ) if s[0] in V2]
    for i, v2 in pages:
        folder, _, kind, title, week, _ = SEQ[i]
        p = ROOT / "AWS-Bootcamp" / href(folder, v2) / "index.html"
        s = set_title(p.read_text(encoding="utf-8"), f"{week} · {kind} · {title}{' (v2)' if v2 else ''} · {BRAND}")
        top = f"<!-- awsq:top -->\n{AWSQ_STYLE}\n{nav(i, 'top', v2)}\n<!-- /awsq:top -->\n"
        bottom = f"<!-- awsq:bottom -->\n{nav(i, 'bottom', v2)}\n<!-- /awsq:bottom -->\n"
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


# The four Study-Material pages bring their own colours; point the nav at their tokens so it follows their theme.
CAP_OWN = {"production-rag", "agentic-rag", "deep-search-agents", "vendor-risk-assessor"}
CAP_STYLE = """<style>
.awsq.awsq-own{--q-card:var(--panel,var(--surface,#fff));--q-card2:var(--panel-2,var(--surface-2,var(--paper,#f3f3f0)));
  --q-rule:var(--rule,var(--line,#ddd));--q-muted:var(--ink-3,var(--muted,var(--ink-2,#666)));
  --q-acc:var(--teal,var(--web,var(--accent,#0b7f73)));--q-acc-t:var(--teal-soft,var(--web-soft,var(--accent-soft,#d6f2ee)));
  --q-acc-ink:var(--ink,#1a1a1a);--q-cur:var(--amber,#b07600);--q-on:var(--panel,var(--surface,#fff));
  --q-mono:var(--f-code,var(--mono,"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace));
  font-family:var(--f-ui,var(--sans,system-ui,sans-serif));font-size:16px;line-height:1.5;position:static;height:auto;overflow:visible;border:0;background:none}
.awsq.awsq-own.awsq-top{margin:14px auto}
.awsq-steps a.key{box-shadow:inset 0 0 0 1.5px #E5484D}
</style>"""


def cap_side(i, cls, label):
    if i < 0 or i >= len(CAPSTONE):
        msg = "You're at the start" if i < 0 else "That's every project"
        return f'<span class="awsq-l {cls}"><span class="awsq-d">{label}</span><span class="awsq-t">{msg}</span></span>'
    folder, step, title = CAPSTONE[i]
    return (f'<a class="awsq-l {cls}" href="../{folder}/"><span class="awsq-d">{label}</span>'
            f'<span class="awsq-t">Project {step[1:]} · {e(title)}</span></a>')


def cap_nav(i, where):
    folder, step, title = CAPSTONE[i]
    steps = []
    for j, (f, st, t) in enumerate(CAPSTONE):
        cls = "cur" if j == i else ("done" if j < i else "")
        if f == "vendor-risk-assessor":
            cls = f"{cls} key".strip()
        cur = ' aria-current="page"' if j == i else ""
        steps.append(f'<li><a class="{cls}" href="../{f}/" title="Project {st[1:]} · {e(t)}"{cur}>{st}{" ★" if f == "vendor-risk-assessor" else ""}</a></li>')
    extra = " awsq-inmain" if folder in INMAIN and where == "top" else ""
    own = " awsq-own" if folder in CAP_OWN else ""
    cap = f"{CAP_BRAND} · Project {step[1:]} of {len(CAPSTONE)}"
    return (f'<div class="awsq awsq-{where}{extra}{own}" role="navigation" aria-label="Capstone navigation ({where})"><div class="awsq-box">'
            f'<div class="awsq-head"><span class="awsq-cap">{e(cap)}</span>{HOME_BTN}</div>'
            f'<div class="awsq-row">{cap_side(i - 1, "awsq-prev", "← Previous")}'
            f'<a class="awsq-home" href="../"><b>{CAP_BRAND}</b>All {len(CAPSTONE)} projects</a>'
            f'{cap_side(i + 1, "awsq-next", "Next →")}</div>'
            f'<ol class="awsq-steps" aria-label="All projects">{"".join(steps)}</ol>'
            f'{files_box(folder, "awsq")}</div></div>')


def build_capstone():
    for i, (folder, step, title) in enumerate(CAPSTONE):
        p = ROOT / "AWS-Capstone" / folder / "index.html"
        s = set_title(p.read_text(encoding="utf-8"), f"Project {step[1:]} · {title} · {CAP_BRAND}")
        style = AWSQ_STYLE + ("\n" + CAP_STYLE if folder in CAP_OWN else "")
        top = f"<!-- awsq:top -->\n{style}\n{cap_nav(i, 'top')}\n<!-- /awsq:top -->\n"
        bottom = f"<!-- awsq:bottom -->\n{cap_nav(i, 'bottom')}\n<!-- /awsq:bottom -->\n"
        s, n = re.subn(r"<!-- awsq:top -->.*?<!-- /awsq:top -->\n", lambda m: top, s, flags=re.S)
        if not n:
            m = re.search(r"<body[^>]*>\n", s)
            assert m, folder
            s = s[:m.end()] + top + s[m.end():]
        s, n = re.subn(r"<!-- awsq:bottom -->.*?<!-- /awsq:bottom -->\n", lambda m: bottom, s, flags=re.S)
        if not n:
            k = s.rfind("<footer")
            assert k > 0, folder
            s = s[:k] + bottom + s[k:]
        assert s.count("<!-- awsq:top -->") == 1 and s.count("<!-- awsq:bottom -->") == 1, folder
        write(p, s)
        print("cap  ", p.relative_to(ROOT))


def insert_after_steps(s, where, block, rel):
    m = re.search(rf'<div class="aiseq aiseq-{where}"[^\n]*?</ol>', s)
    assert m, (rel, where)
    return s[:m.end()] + block + s[m.end():]


def build_learnings():
    for p in sorted((ROOT / "Learnings").glob("*/*.html")):
        s = p.read_text(encoding="utf-8")
        if "<!-- aih:style -->" in s:
            s = re.sub(r"<!-- aih:style -->.*?<!-- /aih:style -->", lambda m: AIH_STYLE, s, flags=re.S)
        else:
            s = s.replace("<!-- aiseq:top -->", "<!-- aiseq:top -->\n" + AIH_STYLE, 1)
        s = re.sub(r'(?<!<div class="aq-head">)(<span class="aq-cap">.*?</span>)(?!<a class="aih")',
                   lambda m: f'<div class="aq-head">{m.group(1)}{HOME_BTN}</div>', s)
        # the centre link opens the AI-Infusion lessons page; the home button stays on the site home
        s = s.replace('<a class="aq-home" href="../../">', '<a class="aq-home" href="../../AI-Infusion/">')
        s = re.sub(r"<!-- aqrec -->.*?<!-- /aqrec -->", "", s)
        s = re.sub(r"<!-- aqfiles -->.*?<!-- /aqfiles -->", "", s)
        v2 = p.parent.name.endswith("-v2")
        folder = p.parent.name.removesuffix("-v2")
        rel = f"{folder}/{p.name}"
        s = set_title(s, f"{LEARN_TITLES[rel]}{' (v2)' if v2 else ''} · AI-Infusion")
        if v2:
            # prev / next and the step dots stay on v2 wherever a class has one
            s = re.sub(r'href="\.\./([^"/]+)/', lambda m: f'href="../{m.group(1)}-v2/' if m.group(1) in LEARN_V2 else m.group(0), s)
            s = re.sub(r'(<div class="aiseq aiseq-top".*?<span class="aq-cap">[^<]*?)(?<! · v2)</span>', r"\1 · v2</span>", s, count=1)
        s = re.sub(r"<!-- aqver -->.*?<!-- /aqver -->", "", s)
        if folder in LEARN_V2:
            page = "" if p.name == "index.html" else p.name
            if v2:
                link = f'<a class="aq-vl" href="../{folder}/{page}">← Original version<small>as taught on Scaler</small></a>'
            else:
                link = f'<a class="aq-vl" href="../{folder}-v2/{page}">Read the v2 version →<small>reworked edition</small></a>'
            # the Project files box goes in after the steps below, so this ends up under it
            s = insert_after_steps(s, "bottom", f'<!-- aqver --><div class="aq-ver">{link}</div><!-- /aqver -->', rel)
        # Class-10 redirects to the Class 9 page, whose code it shares
        key = re.match(r"Class-\d+(?:-\d+)?", rel).group(0)
        for where in ("top", "mid"):
            recs = LEARN_RECORDINGS.get((rel, where))
            if not recs:
                continue
            links = "".join(f'<a class="aq-rec" href="{e(url)}" target="_blank" rel="noopener"><i aria-hidden="true">▶</i>'
                            f'Watch the {e(label)} recording<small>Scaler</small></a>' for label, url in recs)
            s = insert_after_steps(s, where, f'<!-- aqrec --><div class="aq-recs">{links}</div><!-- /aqrec -->', rel)
        for where in ("top", "bottom"):
            s = insert_after_steps(s, where, f"<!-- aqfiles -->{files_box(key, 'aq')}<!-- /aqfiles -->", rel)
        write(p, s)
        print("home ", p.relative_to(ROOT))


def build_hubs():
    # AI-Infusion lessons page: every class recording in one list
    p = ROOT / "AI-Infusion" / "index.html"
    s = p.read_text(encoding="utf-8")
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

    # Bootcamp week pages: each week's recordings
    for _, wdir, _ in WEEKS:
        p = ROOT / "AWS-Bootcamp" / wdir / "index.html"
        s = p.read_text(encoding="utf-8")
        links = "".join(f'<a href="{e(url)}" target="_blank" rel="noopener"><i aria-hidden="true">▶</i>'
                        f'<span>{e(label)}<small>Scaler recording · opens in a new tab</small></span></a>'
                        for label, url in WEEK_RECORDINGS[wdir]) or (
                    '<span><i aria-hidden="true">▶</i><span>Class recordings<small>link coming soon</small></span></span>')
        tag = "recs:" + wdir.replace("-", "")
        block = f'<!-- {tag} --><div class="awsb-recs">{links}</div><!-- /{tag} -->'
        s, n = re.subn(rf"<!-- {tag} -->.*?<!-- /{tag} -->", lambda m: block, s, flags=re.S)
        assert n == 1, p
        write(p, s)
        print("rec  ", p.relative_to(ROOT))


if __name__ == "__main__":
    build_hubs()
    build_aws()
    build_capstone()
    build_learnings()
