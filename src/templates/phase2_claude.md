# Phase 2: Exploration

Explore data and MC for a **{{analysis_type}}** analysis. Start in plan mode,
then execute. Keep it short — prototype on ~500-event slices. Artifact:
`outputs/EXPLORATION.md`.

> **Demo seed?** If `.analysis_config` has a `demo_seed=` line, this phase's
> `EXPLORATION.md` (and `schema_summary.json`/`explore_results.json`) is
> pre-provided. Do not run it live — the orchestrator validates-and-adopts the
> seeded artifact via `verify_seed.py` (see root CLAUDE.md "Fast Demo Mode").

## Requirements
- **Schema inventory:** per file — tree/branch names+types, #events, σ, L. The
  contract later phases build on.
- **Data archaeology (open data):** compare counts to σ×L to detect pre-selection.
  If a discovery changes feasibility, flag it as a **strategy-revision input**
  ("Ph1 assumed X; Ph2 found Y; implication Z").
- **Data quality:** NaN/Inf, unphysical values, empty branches.
- **Variable survey:** signal-vs-background distributions ranked by separation
  (ROC AUC or S/√B); data/MC chi²/ndf per candidate (feeds Phase 3).
- **Baseline yields** after preselection, normalized, data + each MC sample.

## Plotting
mplhep CMS, `figsize=(10,10)`, `mh.histplot()`, `exp_label` on main axes only,
ratio `hspace=0`, save PDF+PNG; lint before finishing (`pixi run lint-plots`).

## Review
**Self-review** (no separate reviewer): schema complete, quality checked,
survey + yields present, figures lint clean. Write to `review/self/`.
