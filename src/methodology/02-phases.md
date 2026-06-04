## 3. Analysis Phases

Five sequential phases; parallelize independent tasks within a phase (§3a.5).
The goal is a correct result fast — one strategy, optimized, to a result.

### 3.0 Gates
Each boundary is hard: Phase N+1 starts only after Phase N's artifact clears its
gate — critical reviewer at **Phases 1/3**, human gate at 4b, orchestrator
checklist at 4a/4c/5 (§6.2). Protocol: artifact → update experiment log → gate
→ resolve Category A → advance. Never skip an artifact under context pressure —
write it and stop cleanly. Phase CLAUDE.md templates (`templates/`) are the
runtime entry points.

### Analysis types
**Search:** signal/background, SR/CR, blinding (§4), limits/significance.
**Measurement:** corrected spectra / extracted parameters; staged validation
(§4) replaces blinding. Where a phase says SR/CR/S/B, measurements read
fiducial region / sidebands / purity.

### Philosophy (non-negotiable)
- **Correctness above all** — the right answer with honest uncertainties; no
  polish fixes a wrong result. Assume you are wrong when you disagree with a
  published value until proven otherwise.
- **Never adjust parameters to match.** Every parameter is justified BEFORE
  seeing its effect. Tuning a cut until data/MC agrees, dropping a systematic
  for being "too large", smoothing a band, or hiding a discrepancy with binning
  is fabrication — the #1 failure mode.
- **Solve, don't accept limitations.** Accept one only after a concrete attempt
  failed for a documented reason; a limitation with no attempted fix is Category B.
- **Context + cross-checks are the physics.** Every result compares to a
  reference (consistency + why); a published overlay with chi2 is mandatory at 4a.

---

### Phase 1: Strategy — `STRATEGY.md` · reviewer
- Query the corpus for prior work/datasets; identify signal, backgrounds
  (irreducible/reducible/instrumental), discriminating variables.
- Commit to a **single selection approach** (MVA-based unless infeasibility is
  documented [D]).
- **Method parity (binding):** compare the method incl. the statistical
  extraction to references; match or beat it, or justify a simpler one by a
  specific technical limitation. "Easier" is not a justification. Silent
  downscoping is Category A (orchestrator tracks at 4a).
- **Systematic plan:** read the applicable `conventions/` doc; mark every source
  "Will implement" / "Not applicable because…" (binding).
- Identify **2 reference analyses**, tabulate their systematics, and extract
  their **published numerical results** (the §6.8 comparison targets — not deferred).
- Label constraints [A], limitations [L], decisions [D]; propagate downstream.
- **Measurements:** define observable(s), correction strategy, validation target,
  theory predictions (≥1 comparison generator independent of the correction MC).
  Identify ~4 flagship "money plots" + any methodology diagrams.

### Phase 2: Exploration — `EXPLORATION.md` · self-review
- Inventory samples (files/trees/branches/events/σ); validate data quality;
  apply standard objects; rank discriminating variables by separation; report
  **data/MC chi²/ndf per candidate variable**; baseline yields after preselection.
- **Published-yield cross-check** when data is pre-selected: f_presel = N_obs /
  (L_pub·σ_pub) per point/year; flag energy dependence > 2%.
- **Data archaeology (open data):** check weight/flag branches, compare counts to
  σ×L (what was cut), check MC coverage and truth info. If a discovery changes
  feasibility, flag it as a strategy-revision input ("Ph1 assumed X; Ph2 found Y;
  implication Z") — orchestrator updates STRATEGY.md before Phase 3.

### Phase 3: Selection — `SELECTION.md` · reviewer
Implement the Phase-1 strategy (don't redesign it).
- **Single strategy:** implement the one approach and optimize its working point
  on MC expected sensitivity — no multi-approach comparison.
- **MVA input quality gate:** survey table (variable | discrimination | data/MC
  chi²/ndf | decision); discard inputs with chi²/ndf > 5 unless exceptional
  discrimination AND a validated data-driven calibration. If MVA: train +
  check data/MC on the output; save ROC/score/importance.
- Every cut motivated by a plot; cutflows monotonically non-increasing.
- **Searches:** CRs (bkg-enriched) + VRs (between CR and SR); estimate SR from
  CRs; VR closure p > 0.05 or Category A.
- **Measurements:** data/MC for all observable-entering variables; response
  matrix (early gate on ~10K MC — if diagonal < 50% investigate before the full
  chain); closure + stress tests (failure p < 0.05 = Category A); justify binning.
- A failed required test needs **≥3 documented remediation attempts** before
  being called a limitation (accepting without remediation is Category A).

**Closure alarm bands (Ph3 AND 4a):** chi²/ndf < 0.1 → Category A (too good —
tautology/same-sample); chi²/ndf > 3 or any pull > 5σ → Category A (method
failure); `passes:false` while text says OK → Category A. First hypothesis for a
failure is a code bug, not physics.

### Phase 4: Statistical Analysis (4a → 4b → 4c)
Each sub-phase: just run the fit and confirm the baseline holds — no exploration.

**4a — Expected (Asimov only).** `INFERENCE_EXPECTED.md` + `ANALYSIS_NOTE_4a_v1`.
- Obtain any committed published value [D] (escalate RAG → get_paper → PDF);
  substituting a data-derived value is Category A.
- Every systematic sized from a measurement/calibration/published uncertainty,
  never a round number ("±50%" is Category A unless 50% is measured).
- Build the binned likelihood (Asimov + systematic NPs); confirm convergence.
  **Validation (lean):** only the final signal-extraction fit — converges on the
  correct Asimov, recovers injected inputs (μ, m_H), GoF reported. No broad toy
  batteries. **Boundary check:** no fitted parameter within 1% of a bound.
- **COMMITMENTS.md:** every Phase-1 commitment `[x]`/`[D]`/`[ ]`; any `[ ]` at
  Phase 5 is Category A.
- PDF mandatory before the light check. **Review:** none — orchestrator light
  check (fit converges + recovers injected inputs).

**4b — 10% data.** `INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_4b_v1`. Fixed-seed
10% subsample, MC normalized to 10% L; run the chain; report GoF; compare to 4a
expected (overlay + chi2). Confirm stability — no further diagnostics.
**Number-consistency gate (first applied):** the final distribution's
yields and the extracted μ/m_H in the AN must match `results/*.json` (>1% =
Category A). PDF mandatory. **Review:** human gate — orchestrator runs its
checklist, then presents the PDF.

**4c — Full data.** `INFERENCE_OBSERVED.md` + `ANALYSIS_NOTE_4c_v1`. Run the
full-data fit; confirm convergence + GoF; compare to both 10% and expected
(flag >2σ vs expected); investigate anomalies. No re-optimization.
**Fit-triviality gate:** chi² ≡ 0 or fitted params ≡ chain inputs → STOP, check
circularity (an input derived from the same cross-section the fit measures is
circular — use independent published inputs, present as a "self-consistency
check"). **Viability (§6.8):** >3σ pull or >50% deviation without a quantitative
explanation is unacceptable; unphysical intermediate values → "not reliably
extractable". `results/` JSON is the single source of truth. **Review:** none —
orchestrator checklist (incl. §6.8).

### Phase 5: Documentation — `ANALYSIS_NOTE_5_v1` + PDF + `results/` · no reviewer
Polish the existing AN (do not rewrite). Concise by default.
- Add remaining AN-specific figures (per-cut, per-systematic dominant only) +
  Phase-1 methodology diagrams; flagship figures get extra care.
- Completeness test: a physicist reproduces every number from the AN alone.
  **≥3 displayed equations** (observable, correction/likelihood, systematic);
  interpretive sentences after each key table/figure; a validation summary
  table; a resolving-power statement; ≥1 published-overlay figure with a chi2.
- **Number-consistency gate** before compiling (>1% vs `results/` = Category A).
- Typeset: pandoc → `postprocess_tex.py` → merge `<!-- COMPOSE -->`-annotated
  figure groups into side-by-side composites → compile→read→fix (tectonic, ≤3
  iterations). Typesetting changes layout only, never numbers — fix physics at
  the source.

---

## 3a. Orchestration

**3a.1 Orchestrator** — a thin coordinator: spawns subagents (`model:"opus"`),
reads summaries, makes phase-transition decisions; never writes code/figures.
Loop EXECUTE → REVIEW → CHECK → COMMIT → ADVANCE (`templates/root_claude.md`).
**Binding-commitment tracking:** at each gate verify all Phase-1 "Will
implement" commitments due are fulfilled — unfulfilled = Category A even if the
reviewer missed it. The orchestrator is the last line of defense.

**3a.2 Subagents** — executors do plan-then-code (and write+typeset the AN from
4a); the critical reviewer (Phases 1/3) finds correctness errors and issues
PASS/ITERATE directly.

**3a.3 Health** — commit before spawning each subagent; check the crash-resilient
session log before respawning a stalled agent. Under context pressure at 4b/5,
split stats and AN-writing into separate executor calls.

**3a.4 Context** — artifacts are the only handoff. Three layers per agent:
bird's-eye framing (~1 pg), relevant methodology sections (~2–5 pg), upstream
artifacts (~2–10 pg). Budget 5–10 pages; summarize long artifacts; read the
experiment log on demand. Under pressure, write the artifact and stop cleanly.

**3a.5 Parallelism** — within a phase, parallel subagents write to separate
dirs, consolidated before the gate; across phases, sequential. Per-channel work
in Ph2–3 and compute-heavy tasks (MVA, systematics, plotting) can be delegated.

---

## 5. Artifact Format

**5.1 Experiment log** — `experiment_log.md` is an append-only lab notebook
(never edited) of what was tried and what happened. Append after every material
decision/discovery/failure; an empty log at phase end is a finding.

**5.2 Primary artifact** — each phase produces a self-contained markdown
artifact (the handoff + record). **AN versioning:** phase-stamped, never
overwritten (`ANALYSIS_NOTE_{phase}_v{N}`); each phase reads the latest and
produces a new v1; fix cycles increment v. Sections: Summary, Method, Results
(numbers+uncertainties), Validation, Open issues, Code reference.
- **Captions** self-contained, context + conclusion, 2–4 sentences (under two =
  Category A); co-generated with the figure.
- **Numerical self-consistency:** `results/*.json` is the single truth; every AN
  instance must match it (a contradiction is Category A).
- Dead-end approaches with code: an appendix subsection + quantitative failure
  criterion + ≥1 diagnostic figure. Supplementary artifacts:
  `UPSTREAM_FEEDBACK.md`, `REGRESSION_TICKET.md` (§6.7).
