# cms_h4l demo seed

This directory is the **pre-baked seed** for the `cms_h4l` demo (H→ZZ*→4ℓ
Higgs μ / mass measurement with CMS Open Data). It lets the demo skip the
~hours of deterministic setup work (Phase 1 strategy, Phase 2 exploration,
citations, tested code skeletons) and jump straight to the live analysis act
starting at **Phase 3**.

See **`SEED_MANIFEST.md`** for the full honesty ledger: what is pre-baked and
why, the validate-and-adopt flow, the determinism guard, and — importantly —
the **three intentional planted items** (the `sigma_mu` double-count bug, the
un-normalized qqZZ background, and the YR4 citation slip) that must survive
into the live run.

## Layout

```
README.md          # this file
SEED_MANIFEST.md   # honesty ledger + planted-item documentation (read this)
prompt.md          # founding analysis prompt
verify_seed.py     # determinism guard: re-derive schema + weights, assert match
seed_artifacts/    # copied verbatim into the analysis dir (relative paths preserved)
  prompt.md
  COMMITMENTS.md
  phase1_strategy/outputs/STRATEGY.md
  phase2_exploration/outputs/EXPLORATION.md
  phase2_exploration/outputs/schema_summary.json
  phase2_exploration/outputs/explore_results.json
  phase5_documentation/outputs/references.bib   # has the planted YR4 slip
skeletons/
  selection/  # selection.py, run_selection.py, compare_variants.py, make_selection_plots.py
  fit/        # model.py, run_inference.py (BUGGY sigma), mass_fit.py, make_p4a_plots.py
```

## How `scaffold_analysis.py --demo cms_h4l` consumes it

`scaffold_analysis.py --demo cms_h4l`:

1. Copies `seed_artifacts/*` into the new analysis directory, **preserving
   relative paths** (so the Phase 1/2/5 outputs land where the orchestrator
   expects them).
2. Copies `skeletons/` to `<analysis>/skeletons/`.
3. Copies `prompt.md`, `verify_seed.py`, and `SEED_MANIFEST.md` to the
   analysis root.
4. Writes `demo_seed=cms_h4l` into `<analysis>/.analysis_config`.

The orchestrator then runs the determinism guard
(`pixi run py verify_seed.py`) from the analysis root. If it PASSes, the
pre-baked Phases 1 + 2 are adopted and the **live act begins at Phase 3**.
If it FAILs, the seed no longer matches the dataset and the run stops.

This directory is owned by the demo-seed harvester. Do not edit
`src/conventions/`, `src/templates/`, or `src/scaffold_analysis.py` from here —
those are owned by other agents.
