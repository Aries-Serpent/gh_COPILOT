#!/usr/bin/env python3
"""
codex_workflow.py — End-to-end workflow executor for the gh_COPILOT repo family.

Features:
- Zip or local repo ingestion (without running any remote actions)
- README parsing + reference replacement/removal
- Component search → module mapping (+ roadmap scaffolding for Phases 6–10)
- Best-effort adaptation attempts (safe, file-only; no external execution)
- Gap documentation (change log)
- Error capture formatted as ChatGPT-5 research questions
- Finalization with deliverables bundle

Safety:
- Will NOT activate GitHub Actions; if present under .github/workflows, they are disabled via rename to workflows.disabled
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import sys
import textwrap
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# -------------------------
# Utilities & Data Models
# -------------------------

@dataclass
class StepCtx:
    number: str
    description: str

@dataclass
class ComponentMetric:
    name: str
    status: str
    coverage: float  # 0.0..1.0
    performance: Optional[float]  # 0.0..1.0 or None

@dataclass
class RunArtifacts:
    workdir: Path
    repo_root: Path
    deliverables_dir: Path
    changelog: Path
    questions_md: Path
    mapping_json: Path
    scores_json: Path
    scores_md: Path
    report_md: Path
    log: Path


DEFAULT_COMPONENTS: List[ComponentMetric] = [
    ComponentMetric("Core Systems", "Active", 0.94, None),
    ComponentMetric("Database Layer", "Active", 0.96, None),
    ComponentMetric("ML Pipeline", "Active", 0.87, None),
    ComponentMetric("Quantum Simulation", "Development", 0.73, None),
    ComponentMetric("Security Framework", "Active", 0.99, None),
    ComponentMetric("Compliance Engine", "Active", 0.92, None),
    ComponentMetric("Performance Monitor", "Active", 0.89, None),
]

STATUS_PRIOR = {
    "Active": 0.85,
    "Development": 0.70,
    "Deprecated": 0.50,
}

ROADMAP_PHASES = {
    6: "Advanced Quantum Algorithms",
    7: "ML Pattern Recognition Enhancement",
    8: "Compliance Framework Evolution",
    9: "Reporting Enhancements",
    10: "Enterprise Integration",
}


def log(art: RunArtifacts, msg: str) -> None:
    art.log.parent.mkdir(parents=True, exist_ok=True)
    with art.log.open("a", encoding="utf-8") as fh:
        fh.write(msg.rstrip() + "\n")


def write_question(art: RunArtifacts, step: StepCtx, err: Exception, context: str) -> None:
    art.questions_md.parent.mkdir(parents=True, exist_ok=True)
    q = textwrap.dedent(f"""
    ### Question for ChatGPT-5
    While performing [{step.number}:{step.description}], encountered the following error:
    `{type(err).__name__}: {str(err).strip()}`
    Context: {context.strip()}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """).strip()
    with art.questions_md.open("a", encoding="utf-8") as fh:
        fh.write(q + "\n\n")
    log(art, f"[{step.number}] ERROR captured and appended to {art.questions_md}")


def append_changelog(art: RunArtifacts, title: str, details: str) -> None:
    art.changelog.parent.mkdir(parents=True, exist_ok=True)
    block = textwrap.dedent(f"""
    ## {title}
    {details.strip()}
    """).strip()
    with art.changelog.open("a", encoding="utf-8") as fh:
        fh.write(block + "\n\n")
    log(art, f"CHANGELOG updated: {title}")

def safe_extract_zip(zip_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)
    # Heuristic: many GitHub zips have a top-level folder
    candidates = [p for p in out_dir.iterdir() if p.is_dir()]
    if len(candidates) == 1:
        return candidates[0]
    return out_dir


def disable_github_actions(repo_root: Path, art: RunArtifacts, step: StepCtx) -> None:
    try:
        wf = repo_root / ".github" / "workflows"
        if wf.exists() and wf.is_dir():
            disabled = wf.with_name("workflows.disabled")
            if disabled.exists():
                # Already disabled
                append_changelog(art, "GitHub Actions Already Disabled",
                                 f"Found existing {disabled} — no action taken.")
            else:
                wf.rename(disabled)
                append_changelog(art, "GitHub Actions Disabled",
                                 f"Renamed {wf} -> {disabled}")
    except Exception as e:
        write_question(art, step, e, f"Attempting to disable workflows under {repo_root!s}")


def parse_and_clean_readmes(repo_root: Path, branch_hint: str, art: RunArtifacts, step: StepCtx) -> None:
    """
    - Remove CI badges and workflow shields
    - Normalize branch-specific GitHub links to {branch_hint}
    - Remove inline links to GitHub Actions pages
    - Leave content otherwise intact; write cleaned copies in-place and into deliverables
    """
    try:
        readmes = list(repo_root.rglob("README*.md"))
        if not readmes:
            append_changelog(art, "README Not Found", f"No README*.md under {repo_root}")
            return

        ci_badge_re = re.compile(
            r"^\s*!\[.*?(badge|build|ci|workflow).*?\]\(.*?\)\s*$", re.IGNORECASE)
        actions_link_re = re.compile(r"https?://github\.com/.+?/actions[^\s\)]*", re.IGNORECASE)
        branch_link_re = re.compile(r"(/tree/)([^/\s\)]+)")

        for md in readmes:
            original = md.read_text(encoding="utf-8", errors="ignore")
            cleaned_lines: List[str] = []
            removed: List[str] = []
            for line in original.splitlines():
                if ci_badge_re.search(line):
                    removed.append(line)
                    continue
                if actions_link_re.search(line):
                    # Drop entire line containing Actions links
                    removed.append(line)
                    continue
                # normalize branch links
                line2 = branch_link_re.sub(rf"\1{branch_hint}", line)
                cleaned_lines.append(line2)

            cleaned = "\n".join(cleaned_lines).rstrip() + "\n"
            if cleaned != original:
                md.write_text(cleaned, encoding="utf-8")
                rel = md.relative_to(repo_root)
                append_changelog(art, f"README Cleaned: {rel}",
                                 f"- Removed {len(removed)} CI/action lines\n- Normalized branch links to '{branch_hint}'")

                # Save a copy to deliverables
                out_copy = art.deliverables_dir / rel
                out_copy.parent.mkdir(parents=True, exist_ok=True)
                out_copy.write_text(cleaned, encoding="utf-8")
    except Exception as e:
        write_question(art, step, e, f"Parsing/cleaning READMEs under {repo_root}")


def map_components(repo_root: Path, art: RunArtifacts, step: StepCtx) -> Dict[str, List[str]]:
    """
    Heuristic keyword mapping from file paths to components.
    Returns dict: component -> list of relative paths
    """
    try:
        keymap = {
            "Core Systems": ["core", "kernel", "infra", "foundation"],
            "Database Layer": ["db", "database", "sql", "orm", "migrations"],
            "ML Pipeline": ["ml", "model", "training", "inference", "pipeline"],
            "Quantum Simulation": ["quantum", "qpu", "anneal", "vqe", "qiskit", "cirq"],
            "Security Framework": ["security", "auth", "crypto", "iam", "policy"],
            "Compliance Engine": ["compliance", "audit", "gdpr", "hipaa", "sox"],
            "Performance Monitor": ["perf", "performance", "metrics", "telemetry", "monitor"],
        }
        mapping: Dict[str, List[str]] = {k: [] for k in keymap}

        for p in repo_root.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(repo_root).as_posix().lower()
            # Skip disabled workflows explicitly
            if rel.startswith(".github/workflows") or rel.startswith(".github/workflows.disabled"):
                continue
            for comp, keys in keymap.items():
                if any(k in rel for k in keys):
                    mapping[comp].append(p.relative_to(repo_root).as_posix())

        art.mapping_json.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
        append_changelog(art, "Component Mapping Completed",
                         f"Component-to-path mapping written to {art.mapping_json.relative_to(art.deliverables_dir)}")
        return mapping
    except Exception as e:
        write_question(art, step, e, f"Mapping components under {repo_root}")
        return {}

def scaffold_roadmap(repo_root: Path, art: RunArtifacts, step: StepCtx) -> None:
    """
    Create minimal, non-executable scaffolding for phases 6–10.
    """
    try:
        base = repo_root / "roadmap"
        base.mkdir(exist_ok=True)

        def stub(mod_name: str, doc: str) -> str:
            return textwrap.dedent(f"""
            {mod_name}
            Purpose: {doc}

            This is a scaffold. Replace with production implementation.
            from typing import Any, Dict, List, Optional, Tuple

            class {mod_name.replace(" ", "")}:  # CamelCase class
                def __init__(self) -> None:
                    pass

                def plan(self) -> dict:
                    return {{"status": "scaffold", "module": "{mod_name}"}}
            """)

        # Phase 6
        (base / "phase6_advanced_quantum").mkdir(exist_ok=True)
        (base / "phase6_advanced_quantum" / "phase_estimation.py").write_text(
            stub("PhaseEstimation", "Integrate phase estimation demos with lightweight library"),
            encoding="utf-8")
        (base / "phase6_advanced_quantum" / "vqe_demo.py").write_text(
            stub("VQEDemo", "Variational Quantum Eigensolver demonstrator (CPU fallback)"),
            encoding="utf-8")
        (base / "phase6_advanced_quantum" / "annealing_opt.py").write_text(
            stub("AnnealingOptimization", "Hardware-backed annealing scaffolding (abstracted)"),
            encoding="utf-8")
        (base / "phase6_advanced_quantum" / "qml_algorithms.py").write_text(
            stub("QuantumML", "Quantum ML algorithms for pattern recognition (stubs)"),
            encoding="utf-8")
        (base / "phase6_advanced_quantum" / "quantum_crypto.py").write_text(
            stub("QuantumCrypto", "Quantum cryptography scaffolding (KEM, QKD placeholders)"),
            encoding="utf-8")

        # Phase 7
        (base / "phase7_ml_pattern_recog").mkdir(exist_ok=True)
        (base / "phase7_ml_pattern_recog" / "anomaly_broadening.py").write_text(
            stub("AnomalyBroadening", "Broaden anomaly detection & auto-healing recommendations"),
            encoding="utf-8")
        (base / "phase7_ml_pattern_recog" / "advanced_nn.py").write_text(
            stub("AdvancedNN", "Advanced neural net architectures for complex patterns"),
            encoding="utf-8")
        (base / "phase7_ml_pattern_recog" / "reinforcement_opt.py").write_text(
            stub("ReinforcementOptimization", "RL for autonomous system optimization"),
            encoding="utf-8")
        (base / "phase7_ml_pattern_recog" / "federated_learning.py").write_text(
            stub("FederatedLearning", "Federated learning for distributed enterprise"),
            encoding="utf-8")

        # Phase 8
        (base / "phase8_compliance_evolution").mkdir(exist_ok=True)
        (base / "phase8_compliance_evolution" / "session_validation.py").write_text(
            stub("SessionValidation", "Stricter session validation & audit logging improvements"),
            encoding="utf-8")
        (base / "phase8_compliance_evolution" / "industry_frameworks.py").write_text(
            stub("IndustryFrameworks", "Industry-specific compliance frameworks (placeholders)"),
            encoding="utf-8")
        (base / "phase8_compliance_evolution" / "auto_reporting.py").write_text(
            stub("AutoReporting", "Automated compliance reporting & certification workflows"),
            encoding="utf-8")
        (base / "phase8_compliance_evolution" / "realtime_monitoring.py").write_text(
            stub("RealtimeMonitoring", "Real-time compliance monitoring & alerting"),
            encoding="utf-8")

        # Phase 9
        (base / "phase9_reporting").mkdir(exist_ok=True)
        (base / "phase9_reporting" / "std_text_reports.py").write_text(
            stub("StandardTextReports", "Standardized text output (alongside JSON/Markdown)"),
            encoding="utf-8")
        (base / "phase9_reporting" / "interactive_dash.py").write_text(
            stub("InteractiveDashboard", "Interactive dashboard with drill-down capabilities"),
            encoding="utf-8")
        (base / "phase9_reporting" / "auto_distribution.py").write_text(
            stub("AutoDistribution", "Automated report generation & distribution"),
            encoding="utf-8")
        (base / "phase9_reporting" / "viz_analytics.py").write_text(
            stub("VisualizationAnalytics", "Advanced visualization & analytics"),
            encoding="utf-8")

        # Phase 10
        (base / "phase10_enterprise_integration").mkdir(exist_ok=True)
        (base / "phase10_enterprise_integration" / "script_classify.py").write_text(
            stub("ScriptClassification", "Improved script classification w/ broader file-type detection"),
            encoding="utf-8")
        (base / "phase10_enterprise_integration" / "api_gateway.py").write_text(
            stub("APIGateway", "Advanced API gateway & microservices architecture (stubs)"),
            encoding="utf-8")
        (base / "phase10_enterprise_integration" / "multi_region.py").write_text(
            stub("MultiRegion", "Global deployment with multi-region support (placeholders)"),
            encoding="utf-8")

        append_changelog(art, "Roadmap Scaffolding Created", f"Scaffolded Phases 6–10 under {base.relative_to(repo_root)}")
    except Exception as e:
        write_question(art, step, e, f"Creating roadmap scaffolding under {repo_root}")


def compute_scores(components: List[ComponentMetric],
                   status_prior: Dict[str, float],
                   art: RunArtifacts,
                   step: StepCtx) -> Tuple[Dict, str]:
    """
    s_i = sqrt(c_i * p_i)
    Overall = mean(s_i)
    If p_i missing, use prior by status.
    """
    try:
        rows = []
        s_vals = []
        for cm in components:
            p = cm.performance if cm.performance is not None else status_prior.get(cm.status, 0.75)
            s = (cm.coverage * p) ** 0.5
            s_vals.append(s)
            rows.append({
                "component": cm.name,
                "status": cm.status,
                "coverage": round(cm.coverage * 100, 2),
                "performance": round(p * 100, 2),
                "composite": round(s * 100, 2),
            })
        overall = round(sum(s_vals) / len(s_vals) * 100, 2)
        coverage_avg = round(sum(cm.coverage for cm in components) / len(components) * 100, 2)
        out = {
            "coverage_average_pct": coverage_avg,
            "composite_overall_pct": overall,
            "by_component": rows,
            "prior_policy": status_prior,
        }
        art.scores_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

        # Also write a simple MD
        lines = ["# Coverage & Performance Scores",
                 f"- Coverage average: **{coverage_avg}%**",
                 f"- Composite overall (\u221A(coverage\u00b7performance)): **{overall}%**",
                 "",
                 "| Component | Status | Coverage | Performance (used) | Composite |",
                 "|---|---|---:|---:|---:|"]
        for r in rows:
            lines.append(f"| {r['component']} | {r['status']} | {r['coverage']}% | {r['performance']}% | {r['composite']}% |")
        art.scores_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

        append_changelog(art, "Scores Computed",
                         f"Saved to {art.scores_json.relative_to(art.deliverables_dir)} and {art.scores_md.relative_to(art.deliverables_dir)}")
        return out, "\n".join(lines)
    except Exception as e:
        write_question(art, step, e, "Computing coverage/performance scores")
        return {}, ""

def write_report(art: RunArtifacts,
                 mapping: Dict[str, List[str]],
                 scores_md: str) -> None:
    body = textwrap.dedent(f"""
    # Codex Run Report

    ## Mapping Summary
    (See {art.mapping_json.name} for complete details.)
    - Components discovered with file associations:
      {", ".join(k for k, v in mapping.items() if v)}

    ## Scores Summary
    {scores_md}

    ## Artifacts
    - Change Log: {art.changelog.name}
    - ChatGPT-5 Questions: {art.questions_md.name}
    - Component Mapping: {art.mapping_json.name}
    - Scores (JSON): {art.scores_json.name}
    - Scores (Markdown): {art.scores_md.name}
    """).strip()
    art.report_md.write_text(body + "\n", encoding="utf-8")


def bundle_deliverables(art: RunArtifacts) -> Path:
    out_zip = art.deliverables_dir.with_suffix(".zip")
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in art.deliverables_dir.rglob("*"):
            if p.is_file():
                zf.write(p, p.relative_to(art.deliverables_dir).as_posix())
    return out_zip


def ensure_repo(args: argparse.Namespace, art: RunArtifacts, step: StepCtx) -> Path:
    if args.repo_dir and Path(args.repo_dir).exists():
        return Path(args.repo_dir).resolve()

    if args.repo_zip:
        # Support local zip path or URL-prefetched zip
        zp = Path(args.repo_zip).resolve()
        if not zp.exists():
            raise FileNotFoundError(f"Repo zip not found: {zp}")
        root = safe_extract_zip(zp, art.workdir / "extracted")
        return root

    raise ValueError("You must supply either --repo-dir or --repo-zip (prefetched/attached zip path).")


def write_pruning_report(art: RunArtifacts, mapping: Dict[str, List[str]]) -> None:
    lines = ["# Controlled Pruning Report",
             "",
             "Policy: Only prune after adaptation attempts fail AND no viable mapping exists.",
             "",
             "Result:"]
    pruned = []
    retained = []
    for comp, paths in mapping.items():
        if paths:
            retained.append((comp, len(paths)))
        else:
            # We *retain* components by default and scaffold missing pieces,
            # so nothing is pruned by this automated run.
            pass
    lines.append(f"- No items pruned automatically. {len(retained)} components retain evidence of implementation.")
    if retained:
        lines.append("")
        lines.append("| Component | Evidence paths |")
        lines.append("|---|---:|")
        for comp, count in sorted(retained, key=lambda x: -x[1]):
            lines.append(f"| {comp} | {count} |")
    out = art.deliverables_dir / "PRUNING.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Codex-ready end-to-end workflow executor.")
    ap.add_argument("--repo-dir", type=str, help="Path to local repository root.")
    ap.add_argument("--repo-zip", type=str, help="Path to a previously downloaded repo ZIP.")
    ap.add_argument("--workdir", type=str, default="./codex_workdir", help="Working directory.")
    ap.add_argument("--branch-hint", type=str, default="1B-gh_copilot_", help="Branch name to normalize links to.")
    ap.add_argument("--metrics-json", type=str, help="Optional JSON file with components/metrics.")
    ap.add_argument("--prior-active", type=float, default=0.85, help="Performance prior for Active components.")
    ap.add_argument("--prior-development", type=float, default=0.70, help="Performance prior for Development components.")
    args = ap.parse_args(argv)

    workdir = Path(args.workdir).resolve()
    deliverables = workdir / "deliverables"
    artifacts = RunArtifacts(
        workdir=workdir,
        repo_root=workdir / "repo",
        deliverables_dir=deliverables,
        changelog=deliverables / "CHANGELOG_Codex_Audit.md",
        questions_md=deliverables / "CHATGPT5_QUESTIONS.md",
        mapping_json=deliverables / "component_mapping.json",
        scores_json=deliverables / "coverage_performance.json",
        scores_md=deliverables / "coverage_performance.md",
        report_md=deliverables / "RUN_REPORT.md",
        log=workdir / "codex_run.log",
    )
    workdir.mkdir(parents=True, exist_ok=True)
    deliverables.mkdir(parents=True, exist_ok=True)

    # Phase 1: Preparation
    step = StepCtx("1.1", "Ensure repository is available and safe to modify")
    try:
        repo_root = ensure_repo(args, artifacts, step)
        artifacts.repo_root = repo_root
        log(artifacts, f"[{step.number}] Repo root resolved: {repo_root}")
    except Exception as e:
        write_question(artifacts, step, e, "Ingest zip or use local repo dir")
        return 2

    step = StepCtx("1.2", "Disable GitHub Actions if present")
    disable_github_actions(artifacts.repo_root, artifacts, step)

    # Phase 2: README cleaning
    step = StepCtx("2.1", "Parse and clean README files")
    parse_and_clean_readmes(artifacts.repo_root, args.branch_hint, artifacts, step)

    # Phase 3: Mapping
    step = StepCtx("3.1", "Map file paths to components via heuristics")
    mapping = map_components(artifacts.repo_root, artifacts, step)

    # Phase 4: Best-effort construction (Roadmap scaffolding)
    step = StepCtx("4.1", "Scaffold roadmap phases 6–10")
    scaffold_roadmap(artifacts.repo_root, artifacts, step)

    # Phase 4b: Controlled Pruning Report
    write_pruning_report(artifacts, mapping)

    # Phase 5: Scores
    # Load metrics if provided
    comps: List[ComponentMetric] = DEFAULT_COMPONENTS
    if args.metrics_json:
        step = StepCtx("5.0", "Load metrics JSON")
        try:
            data = json.loads(Path(args.metrics_json).read_text(encoding="utf-8"))
            comps = [ComponentMetric(
                name=d["name"], status=d["status"],
                coverage=float(d["coverage"]), performance=d.get("performance"))
                for d in data.get("components", [])]
        except Exception as e:
            write_question(artifacts, step, e, f"Loading metrics from {args.metrics_json}; falling back to defaults.")

    step = StepCtx("5.1", "Compute coverage/performance composite scores")
    prior = {
        "Active": args.prior_active,
        "Development": args.prior_development,
        "Deprecated": STATUS_PRIOR["Deprecated"],
    }
    scores, scores_md = compute_scores(comps, prior, artifacts, step)

    # Phase 6: Report & bundle
    step = StepCtx("6.1", "Write consolidated run report")
    write_report(artifacts, mapping, scores_md)

    step = StepCtx("6.2", "Bundle deliverables as zip")
    out_zip = bundle_deliverables(artifacts)
    append_changelog(artifacts, "Deliverables Bundled", f"Created {out_zip.name}")

    print(f"✅ Done. Deliverables: {artifacts.deliverables_dir} and {out_zip}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
