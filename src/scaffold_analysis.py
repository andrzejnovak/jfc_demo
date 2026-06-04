#!/usr/bin/env python
"""Scaffold a new analysis directory with per-phase CLAUDE.md files.

Usage:
    pixi run scaffold analyses/my_analysis --type measurement
    pixi run scaffold analyses/my_analysis --type search

The script creates the directory structure, generates CLAUDE.md files
from src/templates/, initializes a git repo, and creates the pixi environment.
The technique (unfolding, template fit, etc.) is determined during Phase 1,
not at scaffold time.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATES = HERE / "templates"
DEMO_SEEDS = HERE / "demo_seeds"

# ---------------------------------------------------------------------------
# Conventions routing — determines which conventions files apply per type
# ---------------------------------------------------------------------------

CONVENTIONS_FOR_TYPE = {
    "measurement": (
        "- `conventions/unfolding.md` — for unfolded measurements\n"
        "- `conventions/extraction.md` — for extraction/counting measurements\n"
        "\n"
        "The technique selected in Phase 1 determines which file applies.\n"
        "Read the \"When this applies\" section of each to confirm."
    ),
    "search": (
        "- `conventions/search.md`"
    ),
}

# ---------------------------------------------------------------------------
# Phase directories
# ---------------------------------------------------------------------------

PHASES = [
    "phase1_strategy",
    "phase2_exploration",
    "phase3_selection",
    "phase4_inference",
    "phase5_documentation",
]

PHASE_SUBDIRS = ["outputs", "outputs/figures", "src", "review", "logs"]

PHASE_TEMPLATE_MAP = {
    "phase1_strategy": "phase1_claude.md",
    "phase2_exploration": "phase2_claude.md",
    "phase3_selection": "phase3_claude.md",
    "phase4_inference": "phase4_claude.md",
    "phase5_documentation": "phase5_claude.md",
}


def _read_template(name: str) -> str:
    """Read a template file from src/templates/."""
    path = TEMPLATES / name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text()


def _substitute(template: str, variables: dict) -> str:
    """Replace {{key}} placeholders in template with values from variables."""
    result = template
    for key, value in variables.items():
        result = result.replace("{{" + key + "}}", value)
    return result


def scaffold(analysis_dir: Path, analysis_type: str):
    """Create the analysis directory structure with CLAUDE.md files."""
    analysis_dir.mkdir(parents=True, exist_ok=True)

    variables = {
        "name": analysis_dir.name,
        "analysis_type": analysis_type,
        "conventions_files": CONVENTIONS_FOR_TYPE.get(analysis_type, ""),
    }

    # Analysis-root CLAUDE.md from template
    root_claude = analysis_dir / "CLAUDE.md"
    if not root_claude.exists():
        template = _read_template("root_claude.md")
        root_claude.write_text(_substitute(template, variables))
        print(f"  wrote {root_claude}")

    # Per-phase directories and CLAUDE.md
    for phase_name in PHASES:
        phase_dir = analysis_dir / phase_name
        phase_dir.mkdir(exist_ok=True)
        for subdir in PHASE_SUBDIRS:
            (phase_dir / subdir).mkdir(exist_ok=True)

        claude_path = phase_dir / "CLAUDE.md"
        template_name = PHASE_TEMPLATE_MAP.get(phase_name)
        if template_name and not claude_path.exists():
            template = _read_template(template_name)
            claude_path.write_text(_substitute(template, variables))
            print(f"  wrote {claude_path}")

    # Symlink conventions/ and methodology/ into the analysis directory
    conventions_link = analysis_dir / "conventions"
    conventions_src = HERE / "conventions"
    if not conventions_link.exists() and conventions_src.exists():
        conventions_link.symlink_to(conventions_src.resolve())
        print(f"  linked {conventions_link} -> {conventions_src}")

    methodology_link = analysis_dir / "methodology"
    methodology_src = HERE / "methodology"
    if not methodology_link.exists() and methodology_src.exists():
        methodology_link.symlink_to(methodology_src.resolve())
        print(f"  linked {methodology_link} -> {methodology_src}")

    agents_link = analysis_dir / "agents"
    agents_src = HERE / "agents"
    if not agents_link.exists() and agents_src.exists():
        agents_link.symlink_to(agents_src.resolve())
        print(f"  linked {agents_link} -> {agents_src}")

    # .analysis_config (for isolation hook — set data_dir before running)
    config_path = analysis_dir / ".analysis_config"
    if not config_path.exists():
        config_path.write_text(
            "# The isolation hook allows access to these directories.\n"
            "# Set data_dir to the path where your input ROOT files live.\n"
            "# Add extra allow= lines for additional paths (one per line).\n"
            "data_dir=\n"
            "# allow=/path/to/mc/samples\n"
            "# allow=/path/to/calibration\n"
        )
        print(f"  wrote {config_path}")

    # Analysis-local pixi.toml from template
    pixi_path = analysis_dir / "pixi.toml"
    if not pixi_path.exists():
        template = _read_template("pixi.toml")
        pixi_path.write_text(template.replace("{name}", variables["name"]))
        print(f"  wrote {pixi_path}")

    # Stub references.bib for citations
    bib_path = analysis_dir / "phase5_documentation" / "outputs" / "references.bib"
    if not bib_path.exists():
        bib_path.write_text(
            "% BibTeX references for the analysis note.\n"
            "% Add entries as you cite them with [@key] in the AN.\n"
            "% Use get_paper from the RAG corpus to retrieve entries.\n"
        )
        print(f"  wrote {bib_path}")

    # Experiment log and retrieval log
    for log_name in ["experiment_log.md", "retrieval_log.md"]:
        log_path = analysis_dir / log_name
        if not log_path.exists():
            log_path.write_text(
                f"# {log_name.replace('_', ' ').replace('.md', '').title()}\n"
            )
            print(f"  wrote {log_path}")

    # Initialize git repo for the analysis
    git_dir = analysis_dir / ".git"
    if not git_dir.exists():
        subprocess.run(["git", "init"], cwd=analysis_dir, check=True,
                       capture_output=True)
        # Create .gitignore
        gitignore = analysis_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text(
                "# pixi\n"
                ".pixi/\n"
                "pixi.lock\n"
                "\n"
                "# Python\n"
                "__pycache__/\n"
                "*.pyc\n"
                "\n"
                "# SLURM logs\n"
                ".slurm_*.out\n"
            )
            print(f"  wrote {gitignore}")
        print(f"  initialized git repo")

    print(f"\nScaffolded {analysis_dir}/ ({analysis_type})")
    print(f"\nNext steps:")
    print(f"  1. Edit .analysis_config to set data_dir")
    print(f"  2. cd {analysis_dir} && pixi install")
    print(f"  3. claude   # starts the orchestrator agent")


def _copy_tree(src: Path, dst: Path):
    """Copy a directory tree, preserving relative paths.

    Existing destination files are left untouched (a user's own work is
    never overwritten). Only files that do not already exist are created.
    """
    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                print(f"  skipped (exists) {target}")
            else:
                shutil.copy2(item, target)
                print(f"  wrote {target}")


def copy_demo_seed(analysis_dir: Path, demo_name: str):
    """Overlay a pre-baked demo seed onto a freshly scaffolded analysis.

    The seed for fast-demo mode ships already-reviewed Phase 1 + Phase 2
    artifacts, citations, and tested selection/fit skeletons. The
    orchestrator validates-and-adopts these instead of generating them
    live (see root CLAUDE.md "Fast Demo Mode"). Layout under
    src/demo_seeds/NAME/:

      seed_artifacts/   -> copied into the analysis dir, relative paths
                           preserved (e.g. phase1_strategy/outputs/STRATEGY.md,
                           phase5_documentation/outputs/references.bib)
      skeletons/        -> copied to <analysis>/skeletons/
      prompt.md         -> analysis root
      verify_seed.py    -> analysis root (the determinism guard)
      SEED_MANIFEST.md  -> analysis root (the honesty ledger)

    Existing user files are preserved; the only exception is the stub
    references.bib, which the seed is allowed to replace.
    """
    seed_dir = DEMO_SEEDS / demo_name
    if not seed_dir.is_dir():
        print(f"\nERROR: demo seed '{demo_name}' not found at {seed_dir}")
        available = (
            sorted(p.name for p in DEMO_SEEDS.iterdir() if p.is_dir())
            if DEMO_SEEDS.is_dir()
            else []
        )
        if available:
            print(f"  available seeds: {', '.join(available)}")
        else:
            print(f"  no demo seeds are defined under {DEMO_SEEDS}")
        sys.exit(1)

    print(f"\nApplying demo seed '{demo_name}' from {seed_dir}")

    # seed_artifacts/* -> analysis dir, relative paths preserved.
    # The stub references.bib is the one file the seed may replace.
    artifacts_dir = seed_dir / "seed_artifacts"
    if artifacts_dir.is_dir():
        stub_bib = (
            analysis_dir / "phase5_documentation" / "outputs" / "references.bib"
        )
        seed_bib = (
            artifacts_dir / "phase5_documentation" / "outputs" / "references.bib"
        )
        if seed_bib.exists() and stub_bib.exists():
            stub_bib.unlink()
            print(f"  replacing stub {stub_bib}")
        _copy_tree(artifacts_dir, analysis_dir)
    else:
        print(f"  WARNING: no seed_artifacts/ under {seed_dir}")

    # skeletons/ -> <analysis>/skeletons/
    skeletons_dir = seed_dir / "skeletons"
    if skeletons_dir.is_dir():
        _copy_tree(skeletons_dir, analysis_dir / "skeletons")
    else:
        print(f"  WARNING: no skeletons/ under {seed_dir}")

    # Loose root-level files: prompt.md, verify_seed.py, SEED_MANIFEST.md
    for loose_name in ["prompt.md", "verify_seed.py", "SEED_MANIFEST.md"]:
        src_file = seed_dir / loose_name
        if not src_file.exists():
            print(f"  WARNING: seed missing {loose_name}")
            continue
        target = analysis_dir / loose_name
        if target.exists():
            print(f"  skipped (exists) {target}")
        else:
            shutil.copy2(src_file, target)
            print(f"  wrote {target}")

    # Record the seed in .analysis_config so the orchestrator knows to
    # take the validate-and-adopt path for Phases 1 and 2.
    config_path = analysis_dir / ".analysis_config"
    existing = config_path.read_text() if config_path.exists() else ""
    if "demo_seed=" not in existing:
        if existing and not existing.endswith("\n"):
            existing += "\n"
        config_path.write_text(existing + f"demo_seed={demo_name}\n")
        print(f"  wrote demo_seed={demo_name} to {config_path}")

    print(f"\nDemo seed '{demo_name}' applied.")
    print(f"  Phases 1 + 2 are pre-seeded (validate-and-adopt).")
    print(f"  First live act is Phase 3. Run verify_seed.py before adopting.")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new analysis with per-phase CLAUDE.md files."
    )
    parser.add_argument("dir", type=Path, help="Analysis directory to create")
    parser.add_argument(
        "--type",
        choices=["measurement", "search"],
        required=True,
        dest="analysis_type",
        help="Analysis type",
    )
    parser.add_argument(
        "--demo",
        metavar="NAME",
        default=None,
        help="Apply a pre-baked demo seed from src/demo_seeds/NAME/ after "
        "scaffolding (fast-demo mode: Phases 1+2 pre-seeded, first live "
        "act is Phase 3).",
    )
    args = parser.parse_args()
    scaffold(args.dir, args.analysis_type)
    if args.demo:
        copy_demo_seed(args.dir, args.demo)


if __name__ == "__main__":
    main()
