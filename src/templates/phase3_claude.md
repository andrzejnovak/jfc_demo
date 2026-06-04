# Phase 3: Selection

Implement the Phase-1 approach for a **{{analysis_type}}** analysis (read
`STRATEGY.md` first). Start in plan mode, then execute. Artifact:
`outputs/SELECTION.md` (selection, cutflow, working-point optimization,
validation). Save per-sample selected events for Phase 4.

## Requirements
- **Single strategy:** implement the Phase-1 selection approach and optimize its
  working point on a figure of merit (MC expected sensitivity) — no
  multi-approach comparison. If MVA: ROC + score (train/test) + feature
  importance + data/MC of the score.
- **Every cut motivated by a plot;** cutflow monotonically non-increasing.
- **Background model closes:** data/MC for variables entering the selection;
  report a closure χ²/p. A failed test needs ≥3 documented remediations first.
- **Blinding:** optimize on MC expected sensitivity, never on observed SR data.
- Apply every required step in the matching convention(s) ({{conventions_files}})
  — omissions are Category A. Figures pass `pixi run lint-plots`.

## Closure alarm bands (Category A)
χ²/ndf < 0.1 (suspicious) · χ²/ndf > 3 or pull > 5σ (failure) · `passes:false`
while text claims OK.

## Review
Single critical reviewer — PASS / ITERATE; only Category A blocks.
