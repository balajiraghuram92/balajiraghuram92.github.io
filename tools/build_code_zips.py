"""Zip each lesson's / project's code from zips/Code/ into zips/Code/Zips/.

Every zip has one top folder named like the zip, and leaves out secrets and
build junk (.env, virtualenvs, .git, caches, vector DBs). Safe to re-run:
    python tools/build_code_zips.py
Then run tools/bootcamp_nav.py so the pages pick the links up.
"""
import fnmatch
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE = ROOT / "zips" / "Code"
OUT = CODE / "Zips"

# zip name (no .zip) -> folder under zips/Code
ZIPS = {
    "aws-bootcamp-section-00-aws-revision": "Aws-Bootcamp/section-00-AWS-Revision",
    "aws-bootcamp-section-01-your-first-agent": "Aws-Bootcamp/section-01-your-first-agent",
    "aws-bootcamp-section-02-agent-tools": "Aws-Bootcamp/section-02-agent-tools",
    "aws-bootcamp-section-03-agent-memory": "Aws-Bootcamp/section-03-agent-memory",
    "aws-bootcamp-section-04-multi-agent-patterns": "Aws-Bootcamp/section-04-multi-agent-patterns",
    "aws-bootcamp-section-05-mcp-and-a2a": "Aws-Bootcamp/section-05-mcp-and-a2a",
    "aws-bootcamp-section-06-production-deployment": "Aws-Bootcamp/section-06-production-deployment",
    "aws-bootcamp-section-07-evals-observability-governance": "Aws-Bootcamp/section-07-evals-observability-governance",
    "aws-bootcamp-section-08-agentic-bug-fixing": "Aws-Bootcamp/section-08-agentic-bug-fixing",
    "aws-bootcamp-setup":"Aws-Bootcamp/setup",
    "ai-infusion-lesson-1": "Ai-Infusion/lesson-1",
    "ai-infusion-lesson-2": "Ai-Infusion/lesson-2",
    "ai-infusion-lesson-3-4": "Ai-Infusion/lesson-3",
    "ai-infusion-lesson-5": "Ai-Infusion/lesson-5",
    "ai-infusion-lesson-6": "Ai-Infusion/Lesson-6",
    "ai-infusion-lesson-7": "Ai-Infusion/Lesson-7",
    "ai-infusion-lesson-9": "Ai-Infusion/Lesson-9",
    "ai-infusion-lesson-10": "Ai-Infusion/Lesson-10",
}

SKIP_DIRS = {".git", ".venv", "venv", "env", "__pycache__", ".ipynb_checkpoints", "chroma_db", "node_modules",
             ".gradio", ".vscode", ".idea", ".mem0_course", ".bedrock_agentcore", ".aws-sam", "eval_output", ".pytest_cache"}
SKIP_FILES = [".env", ".env.*", "*.pyc", ".DS_Store", "Thumbs.db", ".bedrock_agentcore.yaml"]
KEEP_FILES = [".env.example", ".env.sample"]


def skipped(name):
    return any(fnmatch.fnmatch(name, p) for p in SKIP_FILES) and not any(fnmatch.fnmatch(name, p) for p in KEEP_FILES)


def build(name, rel):
    src = CODE / rel
    assert src.is_dir(), src
    dest = OUT / f"{name}.zip"
    files = []
    for p in sorted(src.rglob("*")):
        parts = p.relative_to(src).parts
        if any(d in SKIP_DIRS for d in parts[:-1]) or p.is_dir() or skipped(p.name):
            continue
        files.append(p)
    tmp = dest.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            z.write(p, f"{name}/{p.relative_to(src).as_posix()}")
    tmp.replace(dest)
    print(f"zip  {dest.relative_to(ROOT)}  {len(files)} files  {dest.stat().st_size // 1024} KB")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, rel in ZIPS.items():
        build(name, rel)
