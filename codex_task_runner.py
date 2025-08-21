#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Task Runner for gh_COPILOT (branch: 1B-gh_copilot_)
Implements:
- README parsing + reference normalization
- File search + adaptation (pyotp availability; fastapi import guard)
- Gap/Pruning documentation (CHANGELOG_CODEX.md)
- Error capture formatted for ChatGPT-5 (research_questions.md)
- Optional test execution + metrics (coverage_metrics.json)
- Strictly avoids touching .github/workflows
"""

import argparse, io, json, os, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
from datetime import datetime

ENC = "utf-8"
ARTIFACTS_DIR = "_artifacts"
CHANGELOG = "CHANGELOG_CODEX.md"
RESEARCH = "research_questions.md"
METRICS = "coverage_metrics.json"
TEST_REQ = "test-requirements.txt"


def log(s: str):
    print(f"[codex] {s}")


def safe_write(path: Path, data: str, mode="w"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode, encoding=ENC) as f:
        f.write(data)


def append_file(path: Path, data: str):
    with path.open("a", encoding=ENC) as f:
        f.write(data)


def load_text(path: Path):
    try:
        return path.read_text(encoding=ENC)
    except Exception as e:
        return None


def save_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=ENC)


def extract_zip(zip_path: Path, dest: Path):
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest)


def discover_repo(root: Path) -> Path:
    # Return top-level repo root (detect single nested dir after unzip)
    entries = [p for p in root.iterdir() if p.is_dir()]
    if len(entries) == 1 and (entries[0] / ".git").exists() is False:
        return entries[0]
    return root


def find_files(root: Path, patterns):
    hits = []
    for pat in patterns:
        hits.extend(root.rglob(pat))
    return list({p.resolve() for p in hits})


def ensure_no_ci_activation(path: Path):
    ghwf = path / ".github" / "workflows"
    if ghwf.exists():
        # Make sure we never modify; mark read-only in our session (best-effort)
        for p in ghwf.rglob("*"):
            try:
                os.chmod(p, 0o444)
            except Exception:
                pass


def add_pyotp_to_test_requirements(repo: Path, changelog: list, rq: list):
    # Strategy A: append to existing test requirements
    candidates = find_files(
        repo,
        [
            TEST_REQ,
            "requirements-test.txt",
            "requirements_dev.txt",
            "dev-requirements.txt",
        ],
    )
    if candidates:
        target = candidates[0]
        txt = load_text(target) or ""
        if re.search(r"^\s*pyotp(\W|$)", txt, flags=re.I | re.M):
            changelog.append(
                f"- Confirmed `pyotp` already present in {target.relative_to(repo)}"
            )
            return ("requirements", target)
        txt += ("\n" if not txt.endswith("\n") else "") + "pyotp>=2,<3\n"
        save_text(target, txt)
        changelog.append(f"- Added `pyotp>=2,<3` to {target.relative_to(repo)}")
        return ("requirements", target)

    # Strategy A2: create test-requirements.txt at root
    target = repo / TEST_REQ
    if not target.exists():
        save_text(target, "pyotp>=2,<3\n")
        changelog.append(f"- Created `{TEST_REQ}` with `pyotp>=2,<3`")
        return ("requirements", target)

    # Fallback (shouldn't reach here)
    changelog.append(
        f"- Could not determine a test requirements channel; will fallback to stub."
    )
    rq.append(
        make_rq(
            step="Phase 2.1: Add pyotp to test dependencies",
            error="No writable test dependency channel discovered",
            ctx=f"Looked for {TEST_REQ}, requirements-test.txt, requirements_dev.txt, dev-requirements.txt",
        )
    )
    return (None, None)


def create_pyotp_stub(repo: Path, changelog: list):
    stub = repo / "tests" / "stubs" / "pyotp.py"
    if stub.exists():
        changelog.append(f"- Reused existing stub at {stub.relative_to(repo)}")
        return stub
    content = """# Minimal pyotp stub for tests
import time, hmac, hashlib, base64

def random_base32(length=32):
    # Deterministic for test repeatability; adjust as needed
    seed = b'CODEx_TEST_SEED__PYOTP'
    return base64.b32encode(hashlib.sha1(seed).digest()).decode('ascii')[:max(16, length)]

class TOTP:
    def __init__(self, secret, interval=30, digits=6):
        self.secret = secret
        self.interval = interval
        self.digits = digits

    def _code(self, for_time=None):
        if for_time is None:
            for_time = int(time.time())
        counter = int(for_time // self.interval)
        key = base64.b32decode(self.secret + '====', casefold=True)
        msg = counter.to_bytes(8, 'big')
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[-1] & 0x0F
        code = (int.from_bytes(h[o:o+4], 'big') & 0x7fffffff) % (10 ** self.digits)
        return str(code).zfill(self.digits)

    def now(self):
        return self._code()

    def verify(self, code, valid_window=1):
        now = int(time.time())
        for w in range(-valid_window, valid_window+1):
            if self._code(now + (w * self.interval)) == str(code):
                return True
        return False
"""
    save_text(stub, content)
    changelog.append(f"- Created pyotp test stub at {stub.relative_to(repo)}")
    # Ensure tests/stubs importable via conftest
    conftest = repo / "tests" / "conftest.py"
    c_text = load_text(conftest) or ""
    if "tests/stubs" not in c_text:
        inject = "\n# Ensure tests/stubs on path for pyotp stub\nimport sys, os\n_stub_path = os.path.join(os.path.dirname(__file__), 'stubs')\nif os.path.isdir(_stub_path) and _stub_path not in sys.path:\n    sys.path.insert(0, _stub_path)\n"
        c_text += inject
        save_text(conftest, c_text)
        changelog.append(
            f"- Updated tests/conftest.py to include tests/stubs in sys.path"
        )
    return stub


def guard_fastapi_imports(repo: Path, changelog: list):
    hits = []
    for p in find_files(repo, ["tests/**/*.py"]):
        txt = load_text(p) or ""
        if "import fastapi" in txt or "from fastapi" in txt:
            if (
                'pytest.importorskip("fastapi"' in txt
                or "pytest.importorskip('fastapi'" in txt
            ):
                continue
            # ensure pytest import and importorskip near top
            lines = txt.splitlines()
            inserted = False
            already_pytest = any(
                re.match(r"^\s*import\s+pytest\b", ln) for ln in lines[:20]
            )
            if not already_pytest:
                lines.insert(0, "import pytest")
            lines.insert(
                1 if not already_pytest else 1,
                "pytest.importorskip('fastapi', reason='FastAPI not installed')",
            )
            new_txt = "\n".join(lines) + ("\n" if not txt.endswith("\n") else "")
            save_text(p, new_txt)
            hits.append(p)
    if hits:
        for p in hits:
            changelog.append(
                f"- Added `pytest.importorskip('fastapi')` to {p.relative_to(repo)}"
            )
    else:
        changelog.append("- No unguarded fastapi imports found in tests")
    return hits


def normalize_readmes(repo: Path, changelog: list):
    readmes = find_files(repo, ["README.md", "README.rst", "README.txt"])
    for r in readmes:
        txt = load_text(r)
        if not txt:
            continue
        # Heuristic: replace stale branch refs if present
        new = re.sub(r"(gh_COPILOT/tree/)[\w\-\._]+", r"\g<1>1B-gh_copilot_", txt)
        # Flag obviously broken markdown links to missing local paths
        new = re.sub(
            r"\(([^)]+)\)",
            lambda m: f"({m.group(1)})"
            if Path(repo, m.group(1)).exists() or "http" in m.group(1)
            else f"([MISSING_REF:{m.group(1)}])",
            new,
        )
        if new != txt:
            save_text(r, new)
            changelog.append(f"- Normalized README references in {r.relative_to(repo)}")


def try_run_tests(repo: Path, changelog: list, rq: list):
    py = shutil.which("pytest")
    if not py:
        changelog.append("- pytest not found; skipping test run")
        return {"executed": False, "exit_code": None, "summary": "pytest not available"}
    cmd = [py, "-q", "-k", "dashboard and auth"]
    log(f"Running tests: {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
        out = proc.stdout + "\n" + proc.stderr
        executed = True
        if proc.returncode != 0 and "no tests ran" in out.lower():
            # fallback
            cmd2 = [py, "-q"]
            log(f"No dashboard/auth tests; running general suite: {' '.join(cmd2)}")
            proc = subprocess.run(cmd2, cwd=str(repo), capture_output=True, text=True)
            out = proc.stdout + "\n" + proc.stderr
        result = {
            "executed": executed,
            "exit_code": proc.returncode,
            "stdout_stderr": out[:200000],
        }
        # Extract a very light summary
        m = re.search(r"(\d+)\s+failed,?\s+(\d+)\s+passed.*", out)
        if m:
            result["summary"] = f"{m.group(2)} passed, {m.group(1)} failed"
        else:
            result["summary"] = "See logs"
        return result
    except Exception as e:
        rq.append(
            make_rq(
                step="Phase 2.4: Execute pytest",
                error=str(e),
                ctx="While running pytest -q -k 'dashboard and auth' with fallback to full suite",
            )
        )
        return {"executed": False, "exit_code": None, "summary": f"Error: {e}"}


def make_rq(step: str, error: str, ctx: str) -> str:
    return (
        "While performing [{}], encountered the following error:\n"
        "{}\n"
        "Context: {}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    ).format(step, error, ctx)


def compute_coverage(s1_done: bool, s2_done: bool, tests_executed: bool):
    w1 = w2 = 1
    numer = (w1 * int(s1_done)) + (w2 * int(s2_done))
    denom = w1 + w2
    C = numer / denom if denom else 0.0
    bonus = 0.25 if tests_executed else 0.0
    C_star = min(1.0, C + bonus)
    return {
        "base": C,
        "bonus": bonus,
        "final": C_star,
        "components": {"s1": s1_done, "s2": s2_done, "tests_executed": tests_executed},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--repo-zip", type=str, help="Path to repo zip (e.g., 1B-gh_copilot_.zip)"
    )
    ap.add_argument("--repo-dir", type=str, help="Path to existing repo directory")
    args = ap.parse_args()

    work = Path(".codex_work").resolve()
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    art = work / ARTIFACTS_DIR
    art.mkdir(parents=True, exist_ok=True)

    # Acquire repo
    if args.repo_zip:
        zip_path = Path(args.repo_zip).resolve()
        extract_dir = work / "repo"
        extract_dir.mkdir(parents=True, exist_ok=True)
        extract_zip(zip_path, extract_dir)
        repo = discover_repo(extract_dir)
    elif args.repo_dir:
        repo = Path(args.repo_dir).resolve()
        # copy into work to avoid modifying source
        dst = work / "repo"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(repo, dst)
        repo = dst
    else:
        print("Provide --repo-zip or --repo-dir", file=sys.stderr)
        sys.exit(2)

    ensure_no_ci_activation(repo)

    changelog = [f"# Codex Change Log ({datetime.utcnow().isoformat()}Z)\n"]
    rq_entries = []

    # Phase 2.1: s1 (pyotp)
    s1_done = False
    mode, target = add_pyotp_to_test_requirements(repo, changelog, rq_entries)
    stub_path = None
    if not mode:
        stub_path = create_pyotp_stub(repo, changelog)
        s1_done = True
    else:
        s1_done = True  # requirements path accepted as completion

    # Phase 2.2: s2 (fastapi guard)
    hits = guard_fastapi_imports(repo, changelog)
    s2_done = (
        True if hits or True else False
    )  # if none found, we treat as not needed => completion

    # Phase 2.3: README normalization
    normalize_readmes(repo, changelog)

    # Phase 2.4: attempt test run
    test_result = try_run_tests(repo, changelog, rq_entries)
    tests_executed = bool(test_result.get("executed"))

    # Metrics
    cov = compute_coverage(s1_done, s2_done, tests_executed)

    # Persist artifacts
    save_text(repo / CHANGELOG, "\n".join(changelog) + "\n")
    save_text(
        repo / RESEARCH,
        "\n\n".join(
            ["Question for ChatGPT-5:\n```\n" + q + "```\n" for q in rq_entries]
        )
        if rq_entries
        else "## No research questions generated.\n",
    )
    save_text(
        repo / METRICS,
        json.dumps(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "coverage": cov,
                "test_result": {
                    k: (v if k != "stdout_stderr" else f"<{len(v)} chars>")
                    for k, v in test_result.items()
                },
            },
            indent=2,
        ),
    )

    # Also copy artifacts to _artifacts/
    for f in [CHANGELOG, RESEARCH, METRICS]:
        shutil.copy2(repo / f, art / f)

    log(
        f"Completed. Metrics: base={cov['base']:.2f} bonus={cov['bonus']:.2f} final={cov['final']:.2f}"
    )
    log(f"Artifacts written to: {art}")


if __name__ == "__main__":
    main()
