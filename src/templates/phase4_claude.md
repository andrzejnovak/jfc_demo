# Phase 4: Inference

Build the statistical model and compute results for a **{{analysis_type}}**
analysis. Start in plan mode, then execute. The executor owns the stats AND the
analysis note (write + typeset PDF) at each sub-phase. Each sub-phase: just run
the fit and confirm the baseline holds — no exploration.

## Flow
- **4a — Expected:** build the model, evaluate systematics, fit **Asimov/MC
  pseudo-data (never real data)**. Write AN v1 + compile PDF.
- **4b — 10% data:** fixed-seed 10% subsample (first partial unblinding); run the
  fit, report GoF, compare to expected; confirm the baseline holds. Update AN +
  recompile PDF → **human gate**.
- **4c — Full data:** fit full data; confirm convergence/GoF; compare to expected
  and 10%; investigate anomalies. No re-optimization. Update AN.

| Sub-phase | Artifact | Gate |
|---|---|---|
| 4a | `INFERENCE_EXPECTED.md` + `ANALYSIS_NOTE_4a_v1` | orchestrator light check |
| 4b | `INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_4b_v1` | human gate |
| 4c | `INFERENCE_OBSERVED.md` + `ANALYSIS_NOTE_4c_v1` | orchestrator checklist |

## Requirements
- **Systematic completeness** vs the convention(s) ({{conventions_files}}) +
  Phase-1 references; any "Will implement" source now absent is Category A. Every
  variation size cited/measured — no round numbers.
- **Model:** binned likelihood, NPs for systematics; fit converges, NP pulls
  sensible, results physical.
- **Validation (4a, lean):** only the final signal-extraction fit — converges on
  the correct Asimov, recovers injected inputs (μ, m_H), GoF reported. No broad
  toy batteries.
- **§6.8:** any result > 3σ or > 30% from a well-measured reference is Category A
  unless quantitatively explained.
- **COMMITMENTS.md:** every line `[x]`/`[D]` (any open `[ ]` at Phase 5 = Category A).
- **Number-consistency gate** runs at 4b (10%), only on the final
  signal-extraction distribution (yields + μ/m_H must match `results/*.json`,
  >1% = Category A); does NOT gate 4a. PDF compiled before the 4a light check and
  the 4b human gate.
- **Fit-triviality (4c):** chi² ≡ 0 or fitted params ≡ chain inputs → STOP, check
  circularity. **Closure bands:** chi²/ndf < 0.1 · > 3 or pull > 5σ ·
  `passes:false` while text says OK → Category A.

## Human gate (after 4b)
Orchestrator runs the regression checklist, then presents the **compiled PDF** +
unblinding checklist. APPROVE / ITERATE / REGRESS(N) / PAUSE. Do NOT run 4c
without approval.

## Review
4a: **no reviewer** — orchestrator light check (fit converges + recovers injected
inputs). 4b: human gate. 4c: no reviewer — orchestrator regression + §6.8 checklist.
