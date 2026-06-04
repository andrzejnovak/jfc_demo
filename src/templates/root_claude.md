# Analysis: {{name}}

Type: {{analysis_type}}

Five-phase pipeline: Strategy → Exploration → Selection → Inference (4a/4b/4c) →
Documentation. Goal: a correct result fast — one strategy, optimized, to a result.

## Execution Model
**You are the orchestrator** — a thin coordinator. You do NOT write code, debug,
or produce figures; you delegate to subagents (`model:"opus"`, started in plan
mode, reading files with the Read tool) and keep your context small.
**First action:** write the physics prompt to `prompt.md`.
Before spawning a role, read `agents/{role}.md` and base the prompt on it.
If `.analysis_config` has a `demo_seed=` line, read **Fast Demo Mode** below
before starting the phase loop — Phases 1+2 are pre-seeded and Phase 4a gains
an extra review panel.

**Post a task list** of all phases with their gate:
```
Phase 1: Strategy      — executor + reviewer
Phase 2: Exploration   — executor + self-review
Phase 3: Selection     — executor + reviewer
Phase 4a: Expected     — executor (no reviewer; orchestrator light check)
Phase 4b: 10% data     — executor + human gate
Phase 4c: Full data    — executor (no reviewer)
Phase 5: Documentation — executor (no reviewer)
```

**Loop per phase:** EXECUTE (spawn executor) → REVIEW (reviewer at Phases 1, 3
only; at 4a run the light "fit converges + recovers injected inputs" check) →
CHECK (Category A → fixer → re-check; regression trigger → §6.7) → COMMIT →
(HUMAN GATE after 4b) → ADVANCE. Commit before spawning each subagent. Don't
accept weak reviews to save tokens.

**Regression checklist (after every result — the safety net for 4a/4b/4c/5):**
- [ ] Validation/closure failure without ≥3 documented remediations?
- [ ] Any single systematic > 80% of total?
- [ ] Result > 3σ or > 30% from a well-measured reference (§6.8)?
- [ ] All binding [D] commitments from STRATEGY.md fulfilled (not silently replaced)?
- [ ] Fit χ² identically zero (circularity)?
Any box checked → trigger regression or re-run, even if a reviewer said PASS.

## Fast Demo Mode (pre-seeded analyses)
Active **only** when `.analysis_config` has a `demo_seed=<name>` line. The
strategy, schema/weights, citations, and selection/fit skeletons ship
already-reviewed under the seed; you do **not** re-derive Phases 1 and 2.

- **Phases 1+2 — VALIDATE-AND-ADOPT (not live).** (a) Run the determinism guard:
  `pixi run py verify_seed.py` — it re-opens the ROOT files, recomputes
  schema/`N_gen`/weights, and asserts they match the seeded
  `schema_summary.json`/`explore_results.json`; a **FAIL exits nonzero and halts
  the demo** (seed no longer matches data — stop, do not adopt). (b) Sanity-read
  the seeded `STRATEGY.md` + `EXPLORATION.md` (internalize the strategy and the
  binding `[D]` commitments). (c) Log the adoption to `experiment_log.md`
  (seed name, guard PASSED, artifact paths), then advance to Phase 3. The seeded
  artifacts on disk + a PASSED guard **satisfy the Phase 1/2 artifact gate**
  without a live execute-and-review.
- **Phase 3 onward runs LIVE.** Executors adapt from
  `<analysis>/skeletons/{selection,fit}/` — starting code with named parameters
  to fill in, not finished results. The live executor still sets/justifies every
  cut and value, runs the code, produces figures, writes the artifact, and is
  reviewed normally.
- **Demo review profile — extra Phase 4a panel.** In ADDITION to the base 4a
  light check, run a **parallel mini-panel**:
  **critical_reviewer + bibtex_validator + plot_validator** (spawn concurrently,
  `model:"opus"`). No separate arbiter — the **orchestrator adjudicates**: any
  Category A → fixer → re-check the affected reviewer; B/C → note and proceed.
- **Everything else stays lean:** 4b is the native human gate; 4c and 5 keep the
  orchestrator checklist; Phases 1/3 keep the single critical_reviewer. The 4a
  panel is the only added gate, and only in demo mode.

**Base (non-demo) analyses are unaffected** — with no `demo_seed=` line, every
phase runs live and gates are exactly the table below (reviewer at Phases 1 and
3 only, no 4a panel).

## Methodology
Read from `methodology/` as needed: `01-core.md` (principles, numeric-constant
policy §2.3, tools), `02-phases.md` (phases, orchestration, artifacts),
`03-review.md` (review + §6.7 regression + §6.8), `04-output.md` (AN + plotting),
`05-practices.md` (coding, blinding, downscoping), `06-appendix.md`.

## Phase gates
Each phase writes its artifact before the next begins; keep a `pixi.toml` `all`
task reproducing the full chain; append to `experiment_log.md` throughout.

| Phase | Artifact | Gate |
|---|---|---|
| 1 | `STRATEGY.md` | reviewer |
| 2 | `EXPLORATION.md` | self-review |
| 3 | `SELECTION.md` | reviewer |
| 4a | `INFERENCE_EXPECTED.md` + `ANALYSIS_NOTE_4a_v1` | orchestrator light check |
| 4b | `INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_4b_v1` | human gate |
| 4c | `INFERENCE_OBSERVED.md` + `ANALYSIS_NOTE_4c_v1` | orchestrator checklist |
| 5 | `ANALYSIS_NOTE_5_v{final}` | orchestrator checklist |

## Key rules
- **Numeric constants** never from memory — every PDG/σ/L/target cites a source;
  uncited = Category A (§2.3).
- **Tools:** `uproot`, `awkward`/`numpy`, `hist`, `matplotlib`+`mplhep`, `pyhf`
  (binned)/`zfit` (unbinned); `pixi` for everything (`pixi run py …`, never bare
  `python`/`pip`).
- **§6.8:** any result > 3σ or > 30% from a well-measured reference is Category A
  unless quantitatively explained (magnitude matched, simpler causes ruled out).
- **Regression (§6.7):** a physics issue traceable to an earlier phase → spawn the
  Investigator → fix the origin non-destructively (new artifact versions) →
  re-run affected downstream. Local current-phase bugs are normal Category A fixes.
- **Human gate (after 4b):** present the compiled PDF + unblinding checklist;
  APPROVE → 4c, ITERATE → fix in 4b scope, REGRESS(N), PAUSE. Never run 4c without
  approval.
- **Coding:** columnar (arrays + masks, no event loops); prototype on ~500-event
  slices; conventional commits; every script a pixi task.
- **Plotting:** `mh.style.use("CMS")`, `figsize=(10,10)`, `mh.histplot()`,
  `exp_label` on main axes only (`data=True`, `llabel="Open Data"/"Open
  Simulation"`), ratio `subplots_adjust(hspace=0)`, no titles/absolute fonts,
  save PDF+PNG; derived quantities pass explicit `yerr=`. Self-lint with
  `pixi run lint-plots`.
- **Conventions:** read the applicable `conventions/` file at Ph1, 4a, 5
  (unfolded → `unfolding.md`; extraction/counting → `extraction.md`; shape-fit →
  `search.md`).
- **AN:** pandoc markdown, concise by default; a physicist reproduces every
  number from the AN alone; Unicode `± < > − ~` (never standalone `$\pm$`);
  numbers quoted from `results/*.json`.
