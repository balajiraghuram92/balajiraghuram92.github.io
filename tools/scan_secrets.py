"""Scan for API keys and secret files before a push. Prints a short report; exit code 1 if anything real is found.

    python -I tools/scan_secrets.py            # what HEAD would publish (every file, and inside every zip)
    python -I tools/scan_secrets.py --history  # every blob ever pushed to origin/main (slow)

Keys are printed masked (first 9 + last 3 characters). Obvious placeholders (xxxx, your-, example, ...) are skipped.
"""
import io
import re
import subprocess
import sys
import zipfile

GIT = r"C:\Users\raghuram\AppData\Local\GitHubDesktop\app-3.6.10\resources\app\git\cmd\git.exe"
KEY = re.compile(rb"((?:sk|pk|rk)_(?:test|live)_[A-Za-z0-9]{10,}|whsec_[A-Za-z0-9]{16,}|gsk_[A-Za-z0-9]{20,}"
                 rb"|sk-(?:proj|ant|svcacct)-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}"
                 rb"|tvly-[A-Za-z0-9-]{16,}|AIza[0-9A-Za-z_-]{30,}|hf_[A-Za-z0-9]{30,}|gh[pousr]_[A-Za-z0-9]{30,}"
                 rb"|github_pat_\w{30,}|lsv2_[a-z]{2}_\w{20,}|pk-lf-[a-f0-9-]{20,}|sk-lf-[a-f0-9-]{20,}"
                 rb"|xox[abpr]-[A-Za-z0-9-]{20,}|SG\.[\w-]{16,}\.[\w-]{16,}|AC[a-f0-9]{32}|ya29\.[\w-]{20,}"
                 rb"|[0-9]{8,10}:AA[\w-]{33}|BEGIN [A-Z ]*PRIVATE KEY"
                 rb"|mongodb(?:\+srv)?://[^:\s\"']+:[^@\s\"']+@|postgres(?:ql)?://[^:\s\"']+:[^@\s\"']{6,}@)")
PLACEHOLDER = re.compile(rb"x{4,}|your|example|placeholder|dummy|fake|redacted", re.I)
ENV_FILE = re.compile(r"(^|/)\.env(\.(?!example$|sample$)[^/]*)?$")


def git(*args, text=True):
    return subprocess.run([GIT, *args], capture_output=True, text=text, **({"encoding": "utf-8"} if text else {})).stdout


def blobs(path, data):
    if not path.endswith(".zip"):
        return [(path, data)]
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return [(path, data)]
    return [(f"{path}!{n}", z.read(n)) for n in z.namelist() if not n.endswith("/") and z.getinfo(n).file_size < 5_000_000]


def main():
    history = "--history" in sys.argv
    if history:
        items = []
        for line in git("rev-list", "--objects", "origin/main").splitlines():
            sha, _, path = line.partition(" ")
            if path and git("cat-file", "-t", sha).strip() == "blob":
                items.append((path, sha))
    else:
        items = [(p, f"HEAD:{p}") for p in git("ls-tree", "-r", "--name-only", "HEAD").splitlines()]
    keys, envs = {}, set()
    for path, ref in items:
        data = git("cat-file", "-p", ref, text=False) if history else git("show", ref, text=False)
        for name, content in blobs(path, data):
            if ENV_FILE.search(name.split("!")[-1]):
                envs.add(name)
            for m in KEY.finditer(content):
                v = m.group(0)
                if not PLACEHOLDER.search(v):
                    keys.setdefault(v[:9].decode(errors="replace") + "…" + v[-3:].decode(errors="replace"), set()).add(name)
    scope = "pushed history (origin/main)" if history else "HEAD"
    print(f"Scanned {len(items)} files in {scope}: {len(keys)} real-looking keys, {len(envs)} .env files.")
    for k, where in sorted(keys.items()):
        print(f"KEY  {k}  in  {', '.join(sorted(where))}")
    for e in sorted(envs):
        print(f"ENV  {e}")
    sys.exit(1 if keys or envs else 0)


if __name__ == "__main__":
    main()
