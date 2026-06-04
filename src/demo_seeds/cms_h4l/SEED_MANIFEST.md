# SEED_MANIFEST — cms_h4l demo seed (honesty ledger)

This file documents exactly what the `cms_h4l` demo seed ships pre-baked,
**why** that pre-baking is legitimate, how the orchestrator adopts it, and —
most importantly — the **three intentional planted items** that must survive
into the live demo. If you are tempted to "fix" any of the three, stop and
read the relevant section first: they are the demo's best moments.

---

## 1. Why pre-bake at all (the two-tier demo)

The full jfc-lite analysis re-derives its deterministic setup every run
(~4.5–5 h). Almost none of that early work *changes* run-to-run: given the
fixed prompt (`prompt.md`) and the fixed dataset (`data/*.root`), the
strategy, the data schema, the per-sample MC normalization weights, the
literature citations, and the shape of the selection/fit code are all
**determined**. Re-deriving them live burns hours to reproduce a known answer.

So the demo is split into two tiers:

- **Tier 0 — "cold open" (pre-baked, shipped in this seed).** Everything
  fixed by (prompt + dataset): Phase 1 strategy + commitments, Phase 2
  exploration (schema summary + weights), the citation library, and
  *tested* selection and fit code **skeletons**. The orchestrator does not
  generate these live; it **validates-and-adopts** them (see §3).
- **Tier 1 — "live act" (stays LIVE).** Phase 3 selection → Phase 4a
  inference (review catches a real bug) → Phase 4b regression + human gate →
  Phase 4c result → final note. This is the show.

Agreed scope this round: pre-bake Phases 1 + 2 artifacts + citations +
tested selection/fit **skeletons**; the **first live act is Phase 3**.

---

## 2. What is pre-baked, and why each item is deterministic

| Seed file (relative to analysis root after scaffold) | What it is | Why it's safe to pre-bake |
|---|---|---|
| `prompt.md` | Founding analysis prompt | The founding document; identical every run by definition |
| `COMMITMENTS.md` | Phase-1-state commitment ledger (all `[ ]`) | Captured at the Phase-1 commit (`1091b88`); the live run closes/downscopes each line as it progresses |
| `phase1_strategy/outputs/STRATEGY.md` | Phase 1 strategy (technique, systematics plan, references) | Fixed by the prompt + reference analyses; already 4-bot reviewed in the source run |
| `phase2_exploration/outputs/EXPLORATION.md` | Phase 2 exploration write-up | Describes the fixed dataset; deterministic given the ntuples |
| `phase2_exploration/outputs/schema_summary.json` | Per-file branch sets, entry counts, object map | Read directly off the ROOT files; deterministic |
| `phase2_exploration/outputs/explore_results.json` | Per-sample `N_gen`, `xsec_pb`, normalization `weight`, group map, yields | `weight = xsec[pb]·1000·L / N_gen`, `L = 10 fb⁻¹`; pure function of (prompt cross sections + dataset) |
| `phase5_documentation/outputs/references.bib` | Citation library (PDG, YR4, pyhf, Cowan, etc.) | Fixed by the physics; cited constants do not change run-to-run |
| `skeletons/selection/*.py` | Tested selection library + drivers + plotting | Adaptable starting code; cut **values** stay as named params the live executor sets/justifies |
| `skeletons/fit/*.py` | Tested pyhf model + inference + mass fit + plots | Adaptable starting code; the live executor finalizes systematics/templates and is reviewed |

The cross sections inside `explore_results.json` are exactly the ones tabulated
in `prompt.md`. The luminosity is `10 fb⁻¹` (the `data_secret_10fb.root` name).

---

## 3. Validate-and-adopt flow (how `scaffold --demo` uses this seed)

`scaffold_analysis.py --demo cms_h4l`:

1. Copies `seed_artifacts/*` into the analysis directory, **preserving the
   relative paths** (so `phase1_strategy/outputs/STRATEGY.md` etc. land where
   the orchestrator expects them).
2. Copies `skeletons/` to `<analysis>/skeletons/`.
3. Copies `prompt.md`, `verify_seed.py`, and `SEED_MANIFEST.md` to the
   analysis root.
4. Writes `demo_seed=cms_h4l` into `.analysis_config`.

The orchestrator then runs a **quick artifact-exists gate** instead of
generating Tier-0 live: it confirms the pre-baked artifacts are present and
runs the determinism guard (`pixi run py verify_seed.py`). If the guard
passes, the orchestrator *adopts* Phases 1 + 2 (it can still show the
artifact-exists check on screen) and begins the live act at Phase 3. If the
guard fails, the seed no longer matches the dataset and the run must stop.

---

## 4. The determinism guard (`verify_seed.py`)

`verify_seed.py` is the honesty check that makes pre-baking legitimate. Run
from the analysis root via `pixi run py verify_seed.py`, it:

- re-opens every `data/*.root` file with `uproot`;
- recomputes the `h4lTree` branch set per sample and asserts it matches
  `schema_summary.json`;
- recomputes `N_gen = sum(Metadata.nEvents)` and the weight
  `w = xsec[pb]·1000·L / N_gen` (`L = 10 fb⁻¹`) per MC sample and asserts
  both match `explore_results.json`;
- prints a per-sample PASS/FAIL table and **exits nonzero on any mismatch**.

It is dependency-light (uproot, numpy, json only). If a dataset is re-ntuplized,
a cross section is edited, or a branch is renamed, the guard fails and the demo
does not proceed on a stale seed.

---

## 5. Intentional planted items (DO NOT "fix")

These three flaws are **deliberately seeded**. Each is caught LIVE by the
normal analysis process, and catching them is the point of the demo. Do not
pre-correct any of them in the seed.

### (i) `sigma_mu` double-count bug — `skeletons/fit/run_inference.py`

The fit skeleton's `run_inference.py` (harvested from git commit `93faa2b`,
the state **before** the fix `070705b`) computes the systematic-only
uncertainty as the **full width of the staterror-fixed profile scan**:

```python
sigma_syst_only = (sig_syst_lo + sig_syst_hi) / 2.0
sigma_tot = float(np.hypot(sigma_stat, sigma_syst_only))
sigma_syst = float(sigma_syst_only)
```

This **double-counts the statistical term**: fixing the per-bin Barlow–Beeston
staterror NPs does *not* remove the Poisson/statistical content of the Asimov
likelihood, so that scan width is dominated by statistics — quadrature-adding
`sigma_stat` on top counts the stat uncertainty twice. The buggy total is
≈ 0.716; the correct value (per-NP impact quadrature for `sigma_syst`) is
≈ 0.514.

- **Caught by:** the LIVE Phase-4a review, which re-derives the uncertainty
  decomposition and flags the double-count.
- **Do NOT** add the correction to the skeleton. Only a natural-looking
  in-code comment (the original "systematics-only broadening" framing) and a
  generic header hint ("verify the uncertainty decomposition") are present —
  never the fix.
- Provenance: `git show 93faa2b:phase4_inference/src/run_inference.py`.
  The fix lives at `070705b` and must NOT be harvested.

### (ii) Un-normalized qqZZ (`ZZTo4L`) — selection skeleton + weights

`ZZTo4L` (qqZZ) is normalized with its **raw theory cross section only**
(`xsec = 1.325 pb`, `w = xsec·1000·L / N_gen`) — there is **no data-driven
normalization and no scale factor** anywhere in the seed. At full data this
MC over-predicts by ≈ 2× at the on-shell Z→4ℓ peak (88–96 GeV), producing a
**−4.56σ data/MC pull**.

- **Caught by:** the LIVE Phase-4b control-region (Z→4ℓ) data/MC anchor,
  which surfaces the pull → investigator → regression ticket → human gate.
- **Do NOT** pre-scale qqZZ, add a data-driven `ZZTo4L` normalization, or
  introduce any control-region scale factor in any seed file
  (`skeletons/selection/*`, `explore_results.json`, etc.).
- Verified absent: no `data-driven` / `scale_factor` / `rescale` /
  `norm_factor` logic exists in the selection skeletons; `ZZTo4L` carries
  only its raw cross section.

### (iii) YR4 citation slip — `phase5_documentation/outputs/references.bib`

Exactly **one** bib entry is intentionally wrong. The `LHCHWG_YR4` entry's
`title` still claims it is the *"Handbook of LHC Higgs Cross Sections: 4.
Deciphering the Nature of the Higgs Sector"* (CERN Yellow Report 4), but its
`eprint` points to `2402.09955` — the 13.6 TeV "ad interim recommendations"
(Karlberg et al.), **not** YR4. The correct YR4 eprint is `1610.07922`. This
analysis is at 13 TeV, so the slipped reference is also the wrong energy.

- **Caught by:** the LIVE BibTeX validator, which checks the eprint against
  the claimed title/report and flags the mismatch.
- **Do NOT** correct the `eprint`. All **other** bib entries are correct;
  this is the single planted slip. (The seed bib was started from the
  *corrected* 4a bib and this one field was re-slipped.)

---

## 6. What stays LIVE (Tier 1)

These are generated/run live every demo and are NOT pre-baked:

- **Phase 3 — Selection (first live act).** The executor adapts the selection
  skeleton, sets and justifies the cut values, runs it over all samples,
  produces cutflow + N-1 + m4l spectrum plots, and is reviewed (1-bot).
- **Phase 4a — Expected inference.** Executor builds/finalizes the model from
  the fit skeleton, computes Asimov expected μ / m_H + systematics, writes
  AN v1; the **4-bot+bib review catches the `sigma_mu` double-count (planted
  item i)** and the **BibTeX validator catches the YR4 slip (planted item iii)**.
- **Phase 4b — 10% data validation + regression + human gate.** The Z→4ℓ
  data/MC anchor surfaces the **un-normalized qqZZ pull (planted item ii)**,
  triggering the investigator → regression ticket → human gate.
- **Phase 4c — Full data result.** Live, 1-bot review.
- **Phase 5 — Final analysis note.** Live, 5-bot review.

The orchestration, all reviews, the regression machinery, and the human gate
all run live. The seed only removes the deterministic *setup* work, never the
*analysis* work or the moments where the process catches a real problem.

---

## 7. Provenance (git commits the seed was harvested from)

| Seed file | Source |
|---|---|
| `seed_artifacts/prompt.md`, root `prompt.md` | `analyses/cms_h4l/prompt.md` (working tree) |
| `seed_artifacts/phase1_strategy/outputs/STRATEGY.md` | working tree |
| `seed_artifacts/phase2_exploration/outputs/{EXPLORATION.md,schema_summary.json,explore_results.json}` | working tree |
| `seed_artifacts/COMMITMENTS.md` | `git show 1091b88:COMMITMENTS.md` (phase-1 state, all `[ ]`) |
| `seed_artifacts/phase5_documentation/outputs/references.bib` | started from `phase4_inference/4a_expected/outputs/references.bib` (corrected), with the single YR4 `eprint` re-slipped to `2402.09955` |
| `skeletons/selection/*.py` | working tree `phase3_selection/src/*` (+ skeleton header; logic unchanged) |
| `skeletons/fit/*.py` (all four) | `git show 93faa2b:phase4_inference/src/*` — the **pre-fix** state (BUGGY `run_inference.py`); all four taken together for mutual consistency |

The `sigma_mu` fix commit `070705b` was deliberately **not** harvested.
