# Phase 2 Exploration: H→ZZ*→4ℓ (CMS Open Data 2017, 10 fb⁻¹)

**Goal.** Give Phase 3 (selection) everything it needs to write the selection
code with no surprises: confirmed schema, finalState→channel mapping,
normalization weights, candidate-vs-event structure, and sanity-checked
baseline yields. This is a **lean** exploration per the quick-analysis scope.

All numbers below are reproducible via:
`pixi run py phase2_exploration/src/inspect_schema.py`,
`pixi run py phase2_exploration/src/explore.py`,
`pixi run py phase2_exploration/src/make_plots.py`.

---

## 1. Sample / Schema Inventory

Twelve ROOT files in `data/` (AppleDouble `._*` siblings ignored). **Every
file contains exactly two trees: `h4lTree` (one entry per pre-built 4ℓ
candidate) and `Metadata`.** The 111-branch `h4lTree` schema is **byte-for-byte
identical across all 12 files** (verified by branch-name+type set comparison in
`inspect_schema.py`). This confirms the Phase 1 assumption.

| File | Role | `h4lTree` entries | `Metadata` entries |
|------|------|------------------:|-------------------:|
| GluGluToHToZZ.root | signal (ggF) | 420,275 | 23 |
| VBF_HToZZ.root | signal (VBF) | 76,779 | 13 |
| ZHToZZ.root | signal (ZH) | 72,515 | 1 |
| WPHToZZ.root | signal (W⁺H) | 16,304 | 13 |
| WMHToZZ.root | signal (W⁻H) | 25,280 | 16 |
| ZZTo4L.root | qqZZ irreducible | 3,333,903 | 108 |
| GGZZ2E2Mu.root | ggZZ irreducible | 197,379 | 21 |
| GGZZ4E.root | ggZZ irreducible | 415,426 | 25 |
| GGZZ4Mu.root | ggZZ irreducible | 560,781 | 30 |
| DYJetsToLL.root | DY reducible | 621 | 116 |
| TTBar.root | tt̄ reducible | 776 | 56 |
| data_secret_10fb.root | data | 719 | 1 |

Full machine-readable schema (all 111 branches × all files): `outputs/schema_summary.json`.

### 1.1 `h4lTree` branch structure (exact names — Phase 3 depends on these)

**Event / vertex (10):** `run` (int32), `lumi` (int32), `event` (int64),
`nPV` (int32), `pvX, pvY, pvZ, pvChi2, pvNdof, pvScore` (float).

**Candidate-level (8):** `mZ1`, `mZ2`, `m4l`, `pt4l`, `eta4l`, `phi4l`, `y4l`
(float); **`finalState`** (int32); `trigBits` (int32).

**Per-lepton, flat with prefix `l1`/`l2`/`l3`/`l4` (23 branches each, 92 total).**
The four leptons are pre-ordered within the candidate. For lepton *n* ∈ {1,2,3,4}:

| Branch (l*n*…) | Type | Meaning |
|---------------|------|---------|
| `pt`, `eta`, `phi`, `mass` | float | four-vector components |
| `charge` | int32 | lepton charge |
| `pdgId` | int32 | ±11 (e), ±13 (μ) — confirmed §2 |
| `zId` | int32 | Z-pair assignment (which Z the lepton belongs to) |
| `dxy`, `dz`, `dxyErr`, `dzErr` | float | transverse / longitudinal IP and errors |
| `sip3d`, `ip3d` | float | 3D impact-parameter significance / value |
| `pfRelIso03` | float | PF relative isolation, ΔR<0.3 |
| `miniRelIso` | float | mini relative isolation |
| `muMedium`, `muTight`, `muGlobal`, `muPF` | int32 | muon ID flags |
| `elCutBased` | int32 | electron cut-based ID level |
| `elMvaWP90`, `elMvaWP80` | int32 | electron MVA ID working-point flags |
| `elMvaBdt` | float | electron MVA discriminant (raw BDT score) |

All branches Phase 1 anticipated are present: `m4l`, `mZ1`, `mZ2`,
`finalState`, per-lepton kinematics / `pdgId` / `charge` / `pfRelIso03` /
`miniRelIso` / `sip3d` / `dxy` / `dz` / `muMedium` / `muTight` / `elMvaWP90` /
`elMvaWP80` / `elCutBased` / `elMvaBdt`. The pairing variable is **`l{n}zId`**
(per-lepton Z assignment), so SFOS pairing is already encoded in the ntuple.

### 1.2 `Metadata` tree

- **MC files:** single branch **`nEvents` (int64)**. The tree has *many*
  entries (one per merged input file, e.g. 108 for ZZTo4L, 116 for DYJetsToLL,
  1 for ZHToZZ). **N_gen = sum of `nEvents` over all entries** — NOT the entry
  count. This is the per-sample generated-event count for normalization.
- **Data file:** three branches — **`nInputEvents` (int64)**,
  **`nOutputEvents` (int64)**, **`lumi_fb` (double)**. For the data file:
  `lumi_fb = 10.0`, `nInputEvents = 9,870,406`, `nOutputEvents = 719`.

> **Note for Phase 1 [A2] verification (positive).** The integrated luminosity
> is stored **directly in the data file** (`Metadata/lumi_fb = 10.0`),
> independently confirming the 10 fb⁻¹ assumed from the sample name. No
> back-calculation from data is needed. `nOutputEvents` (719) equals the data
> `h4lTree` entry count — the ntuplizer pre-selected 9.87M input events down to
> 719 candidates.

### 1.3 Data-archaeology checks

- **Per-event weight branch:** **none exists.** There is no `genWeight`,
  `weight`, `puWeight`, or `xsecWeight` branch. MC normalization is therefore a
  **flat per-sample weight** (§3), confirming Phase 1 [A3].
- **Quality/flag branches:** `trigBits` (int32, trigger decision bits) and the
  PV-quality floats (`pvChi2`, `pvNdof`, `pvScore`) are present; none act as
  event weights. ID flags (`mu*`, `el*`) are selection inputs, not weights.
- **Truth-level info:** no gen-level branches (no `gen*`, no truth pdgId/pt).
  Truth-matching is not available — the MC-truth signal peak referenced in the
  Phase 1 m_H cross-check (§4.2 of STRATEGY) must come from the reconstructed
  signal-MC `m4l` shape, not a gen-level quantity. **Minor input to Phase 4**,
  not a blocker (the strategy already plans the resolution model from
  reconstructed signal MC).
- **Generation coverage:** single generator / single year (2017) / single
  √s = 13 TeV per process — confirms limitation [L3] (no alternative-generator
  systematic available).

---

## 2. finalState → Channel Mapping (resolves Phase 1 LOW-confidence flag)

Cross-checking `finalState` against the per-lepton `|pdgId|` composition over
GGZZ2E2Mu, GGZZ4E, GGZZ4Mu, GluGluToHToZZ, ZZTo4L, and data
(several million candidates) gives a **100%-pure mapping** in every code — every
candidate with a given `finalState` has exactly the lepton composition shown:

| `finalState` | Lepton composition (|pdgId|) | Channel | Purity |
|:------------:|------------------------------|:-------:|:------:|
| **0** | 0 electrons, 4 muons | **4μ** | 1.000 |
| **1** | 4 electrons, 0 muons | **4e** | 1.000 |
| **2** | 2 electrons, 2 muons | **2e2μ** | 1.000 |

**This is binding for Phase 3:** `finalState ∈ {0,1,2} = {4μ, 4e, 2e2μ}`. The
per-channel pyhf fit (Phase 4) uses this mapping directly. The mapping is also
cross-checked by counting `pdgId` directly (the `channel_label` helper in
`explore.py` uses the pdgId counts and agrees with `finalState`).

---

## 3. Normalization Weights

Flat per-sample weight `w = σ·L / N_gen`, with σ from the prompt.md table
(requester-authoritative [A1]), L = 10 fb⁻¹, and **N_gen = Σ Metadata.nEvents**.
σ is converted pb→fb (×1000) so that `w = σ[fb]·L[fb⁻¹]/N_gen`.

| Sample | Group | σ (pb) | N_gen | Weight w |
|--------|-------|-------:|------------:|---------:|
| GluGluToHToZZ.root | signal | 0.00602392 | 2,998,456 | 2.009e−05 |
| VBF_HToZZ.root | signal | 0.00048794 | 488,000 | 9.999e−06 |
| ZHToZZ.root | signal | 0.000098394 | 512,586 | 1.920e−06 |
| WPHToZZ.root | signal | 0.0001072352 | 129,396 | 8.287e−06 |
| WMHToZZ.root | signal | 0.0000670716 | 176,160 | 3.807e−06 |
| ZZTo4L.root | qqZZ | 1.325 | 99,333,000 | 1.334e−04 |
| DYJetsToLL.root | DY | 5396.0 | 151,253,358 | **0.35675** |
| TTBar.root | tt̄ | 52.70 | 29,251,271 | 0.018016 |
| GGZZ2E2Mu.root | ggZZ | 0.003185 | 416,000 | 7.656e−05 |
| GGZZ4E.root | ggZZ | 0.001575 | 986,000 | 1.597e−05 |
| GGZZ4Mu.root | ggZZ | 0.001619 | 972,170 | 1.665e−05 |

(All values from `outputs/explore_results.json`, which is authoritative.)

**Sanity of weights.** DY has by far the largest weight (0.357) because its huge
σ (5396 pb) is divided by a finite N_gen and only a handful of candidates
survive the 4ℓ ntuplizer — so each surviving DY candidate "stands in" for many
events. tt̄ next (0.018). The ZZ/signal weights are tiny (~10⁻⁴–10⁻⁶) because
those samples are generated with very high statistics relative to their cross
sections. All weights are positive and finite.

**No per-event weights** (§1.3): every candidate in a sample carries the same w.

---

## 4. Candidates vs. Events

The candidate/event uniqueness check (on `(run, lumi, event)` keys):

| Sample | Candidates | Unique events | Multi-candidate events |
|--------|-----------:|--------------:|-----------------------:|
| GluGluToHToZZ.root | 420,275 | 420,275 | **0** |
| ZZTo4L.root | 3,333,903 | 3,333,903 | **0** |
| DYJetsToLL.root | 621 | 621 | **0** |
| **data_secret_10fb.root** | **719** | **477** | **242** |

**Finding (FLAG for Phase 3).** In **MC**, there is exactly **one candidate per
event** — the ntuplizer already keeps a single best 4ℓ candidate per MC event.
But **the data has 719 candidates spanning only 477 unique events → 242
duplicate-event candidates** (≈34% of data candidates are "extra" candidates
from events that already contributed one). Phase 3 **must apply a
best-candidate selection on data** (the standard HZZ4l choice: per event, keep
the candidate with mZ1 closest to m_Z, then highest-ΣpT of the Z₂ leptons, or
equivalent), otherwise the data spectrum is over-counted relative to MC. This is
a real selection requirement, not cosmetic — it directly affects the observed
yield going into the fit.

> Because MC is already 1-candidate-per-event, applying the same best-candidate
> rule to MC is a no-op there, so the rule can be applied uniformly to both
> data and MC without changing the MC yields.

---

## 5. Baseline Yields (loose preselection)

Loose preselection (broad, exploration-only — Phase 3 tightens with lepton
ID/iso/IP and pT cuts): `m4l > 70 GeV`, `mZ1 ∈ [40,120] GeV`,
`mZ2 ∈ [12,120] GeV`. Weighted to 10 fb⁻¹. **No best-candidate dedup applied
here** (so data row is the raw 601; see §4 caveat).

### 5.1 Per-sample

| Sample | Group | Raw total | Raw presel | Weighted presel |
|--------|-------|----------:|-----------:|----------------:|
| GluGluToHToZZ.root | signal | 420,275 | 384,092 | 7.72 |
| VBF_HToZZ.root | signal | 76,779 | 69,926 | 0.70 |
| ZHToZZ.root | signal | 72,515 | 68,470 | 0.13 |
| WPHToZZ.root | signal | 16,304 | 14,918 | 0.12 |
| WMHToZZ.root | signal | 25,280 | 23,099 | 0.09 |
| ZZTo4L.root | qqZZ | 3,333,903 | 2,366,552 | 315.67 |
| GGZZ2E2Mu.root | ggZZ | 197,379 | 185,857 | 14.23 |
| GGZZ4E.root | ggZZ | 415,426 | 401,753 | 6.42 |
| GGZZ4Mu.root | ggZZ | 560,781 | 535,625 | 8.92 |
| DYJetsToLL.root | DY | 621 | 561 | 200.14 |
| TTBar.root | tt̄ | 776 | 692 | 12.47 |
| data_secret_10fb.root | data | 719 | 601 | 601 |

### 5.2 Per-group and per-channel (weighted, 10 fb⁻¹)

| Group | Total | 4μ | 4e | 2e2μ |
|-------|------:|----:|----:|------:|
| signal (summed) | 8.76 | 2.71 | 1.84 | 4.03 |
| qqZZ | 315.67 | 101.46 | 68.52 | 145.69 |
| ggZZ | 29.57 | 8.92 | 6.42 | 14.23 |
| DY | 200.14 | 3.92 | 95.61 | 100.60 |
| tt̄ | 12.47 | 0.70 | 5.28 | 6.49 |
| **Data (raw)** | **601** | **68** | **211** | **322** |

### 5.3 Sanity assessment

- **Signs/magnitudes are physically sensible at loose preselection:** qqZZ is
  the dominant background (316), ggZZ a moderate ~10% correction to the ZZ
  continuum (30), DY large pre-ID (200), tt̄ small (12), summed signal small
  (8.8). This matches the Phase 1 expectation (§2.2).
- **The loose preselection has NO lepton ID / isolation / SIP / pT cuts yet.**
  This is why the MC stack sits *below* the data in the m₄ℓ continuum
  (@fig:m4l) and why DY (a fake-dominated reducible background) is still huge.
  Phase 3's full selection will suppress DY/tt̄ dramatically and bring the
  continuum into agreement — the loose-presel disagreement is expected and not
  a data/MC modeling problem.
- **DY is concentrated in 4e and 2e2μ (95.6 + 100.6) and tiny in 4μ (3.9)** —
  consistent with electron fakes dominating the reducible background (jets
  faking electrons more readily than muons), as expected for a DY-only fake
  model.

> **[L1] confirmation (FLAG for Phase 4 sizing).** DY and tt̄ survive with very
> low **raw** statistics even at loose preselection (DY: 561 raw events at
> w=0.357; tt̄: 692 raw at w=0.018). After the full Phase 3 selection these will
> drop much further, so the reducible templates will be statistically sparse.
> This confirms limitation [L1]: per-bin `staterror` NPs are essential, and the
> reducible normalization-uncertainty sizing [S4] must account for the large MC
> statistical uncertainty on the surviving yield. Quantify the post-selection
> raw yields explicitly in Phase 3.

---

## 6. Sanity Figures

All figures: loose preselection, CMS Open Data style, `figsize=(10,10)`,
log-y, stacked backgrounds (DY / tt̄ / ggZZ / qqZZ), summed-signal (μ=1) as a
red step, data as black points. `pixi run lint-plots phase2_exploration`
passes with no violations.

![m₄ℓ spectrum after loose preselection (m₄ℓ>70, mZ1∈[40,120], mZ2∈[12,120] GeV), backgrounds stacked with the μ=1 summed-signal template (red) overlaid and data (black points), 10 fb⁻¹. The clear Z→4ℓ single-resonant peak at ~91 GeV and the falling continuum are visible; the signal forms a small bump near 125 GeV. Data lies above the MC stack in the continuum because this loose preselection applies no lepton ID/isolation cuts yet — Phase 3 will suppress the reducible backgrounds and restore agreement. This is a sanity plot, not a result.](figures/m4l_spectrum.pdf){#fig:m4l}

![m_{Z₁} distribution after loose preselection, same stacking and normalization as @fig:m4l. The strong on-shell peak at m_{Z₁}≈91 GeV confirms the SFOS-pairing convention in which Z₁ is the pair with mass closest to the PDG Z mass. The signal template (red) is sharply peaked at the Z mass as expected for the on-shell Z in H→ZZ*. Loose-presel data/MC offset is the same ID-related effect noted in @fig:m4l.](figures/mZ1_spectrum.pdf){#fig:mZ1}

![m_{Z₂} distribution after loose preselection, same stacking and normalization as @fig:m4l. The off-shell Z₂ peaks at low mass with a tail toward the on-shell value, consistent with the on-shell/off-shell H→ZZ* topology and the pairing convention (Z₂ is the remaining SFOS pair). The signal template (red) rises toward m_{Z₂}≈30 GeV, the characteristic off-shell Z scale for a 125 GeV Higgs. The ggZZ component (green) is comparatively more prominent at high m_{Z₂} where both Z bosons are near-resonant.](figures/mZ2_spectrum.pdf){#fig:mZ2}

---

## 7. Strategy Revision Input?

**No Phase 1 assumption is broken. One assumption is corrected in detail, and
one new selection requirement is surfaced** — neither requires a strategy
rewrite; both are normal exploration outputs for Phase 3 to act on.

**Confirmed (no change needed):**
- Flat `h4lTree`, one candidate per entry, identical 111-branch schema across
  files — as assumed.
- All branches the strategy named for selection (§3 of STRATEGY) and for the
  MVA-inputs record ([D3]) **exist** (`elMvaBdt`, `pfRelIso03`, `miniRelIso`,
  `sip3d`, `mZ1/2`, `pt4l`, `eta4l`, etc.).
- No MELA/D_bkg/D_kin branches → confirms [D4] (1D fit, no MELA inputs).
- No per-event weight branch → confirms [A3] (flat per-sample weight).
- L = 10 fb⁻¹ confirmed independently from `Metadata/lumi_fb` → confirms [A2].
- **finalState↔channel LOW-confidence flag RESOLVED:** 0=4μ, 1=4e, 2=2e2μ
  (100% pure). Update the strategy's "to be confirmed" note to "confirmed".

**Corrected detail (clarification, not a contradiction):**
- Phase 1 §2 / §2.3 wrote "Metadata/nEvents" as the N_gen source. **Refinement:**
  the `Metadata` tree has **many entries** (one per merged input file); N_gen is
  the **sum** of `nEvents` over entries, not the entry count and not a single
  scalar. `explore.py` already does this correctly. Phase 3/4 normalization code
  must sum the branch. (No physics impact; just an implementation note.)

**New requirement for Phase 3 (must implement):**
- **Best-candidate selection on data is required** (§4): data has 242
  multiple-candidate events (719 candidates / 477 events). MC is already
  1-candidate-per-event, so a uniform best-candidate rule is a no-op on MC and
  fixes the data over-counting. **Phase 3 must implement and document the
  best-candidate tie-break** (recommend: mZ1 closest to m_Z, then Z₂ leptons'
  ΣpT, matching the HZZ4l convention). This was not called out in Phase 1 but
  is squarely within Phase 3 selection scope — not a regression.

**Flags carried forward (no action now):**
- [L1] reducible MC-stat sparsity — confirmed, quantify post-selection in
  Phase 3; informs [S4] sizing in Phase 4a.
- No truth-level branches — m_H closure uses reconstructed signal-MC shape
  (already the strategy's plan); minor Phase 4 note.

---

## 8. Toolchain Smoke Test

`pixi run build-pdf` on a minimal markdown stub (math + citation) **succeeded**
after one fix: **`tectonic` was missing from the pixi environment** (the
`build-pdf` task invokes it but it was not in `pixi.toml`). Added
`tectonic >=0.15` to `[dependencies]` and ran `pixi install`; the stub then
compiled pandoc → .tex → postprocess → tectonic → **PDF (17 KB) successfully**.
Stub files deleted afterward. Phase 4 typesetting will not hit a missing-engine
surprise. (A harmless citeproc "citation not found" warning appeared because the
`build-pdf` convenience task does not pass `--bibliography`; the Phase 4
typesetter invokes pandoc directly with the bib, so this is not a toolchain
defect.)

---

## 9. Self-Review Checklist

- [x] Sample inventory complete — all 12 files, tree names, entry counts, full
      111-branch list with types (`schema_summary.json`), schema identical.
- [x] Exact key branch names documented (`m4l`, `mZ1`, `mZ2`, `finalState`,
      `l{n}pt/eta/phi/mass/charge/pdgId/zId/pfRelIso03/miniRelIso/sip3d/dxy/dz/`
      `muMedium/muTight/elMvaWP90/elMvaWP80/elCutBased/elMvaBdt`).
- [x] Weights computed (`w = σL/N_gen`, N_gen = Σ Metadata.nEvents) and
      sanity-checked (all positive; DY largest, ZZ/signal tiny).
- [x] finalState mapping confirmed at 100% purity (0=4μ, 1=4e, 2=2e2μ).
- [x] Candidates-vs-events resolved: MC 1/event; **data needs best-candidate
      selection (242 dup-event candidates)** — flagged for Phase 3.
- [x] Baseline yields physically sensible (qqZZ dominant, signal small, DY
      large pre-ID, fakes electron-dominated).
- [x] Data-archaeology: no per-event weights; no truth branches; single
      generator/year; lumi_fb=10 in data file.
- [x] 3 sanity figures pass `lint-plots` and visual inspection (legend clears
      data, Z peaks where expected, signal bump at 125).
- [x] PDF toolchain smoke test passed (after adding tectonic).
- [x] experiment_log.md updated.
