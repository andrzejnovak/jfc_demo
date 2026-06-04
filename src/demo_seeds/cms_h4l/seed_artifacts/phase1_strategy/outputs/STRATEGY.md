# Phase 1 Strategy: H→ZZ*→4ℓ Mass and Signal-Strength Measurement

**Analysis:** cms_h4l — Higgs boson measurement in the four-lepton channel
with CMS Open Data (2017, √s = 13 TeV, 10 fb⁻¹).
**Type:** measurement (parameter extraction — mass m₄ℓ peak position and
signal strength μ).
**Reference analysis:** CMS, JHEP 11 (2017) 047, arXiv:1706.09936.
**Scope:** Quick analysis per requester directives (lean Phases 1–2,
DY-only fakes, skipped lepton/trigger-efficiency systematics, focus on
background normalizations, analysis note under 20 pages).

> Numeric-constant policy: every number that enters the analysis must trace
> to a citable source (PDG, the reference paper, or CMS luminosity
> documentation). Cross sections used for normalization are taken from
> `prompt.md` (the requester-provided sample table) and are treated as the
> authoritative inputs for this analysis. Physical constants (m_Z, m_H) and
> uncertainty magnitudes carry an explicit "source to be fetched in
> Phase 4a" tag where they are not yet pinned to a citation.

---

## 1. Physics Motivation and Observable

The Higgs boson decays H→ZZ*→4ℓ (4ℓ = 4e, 4μ, 2e2μ) produce a fully
reconstructed final state with a narrow four-lepton invariant-mass peak on a
smoothly falling and continuum background. This "golden channel" has the best
mass resolution and highest signal purity of the Higgs decay modes, despite a
small branching fraction. One Z is on-shell (Z₁) and one is off-shell (Z₂).

**Primary observable: the four-lepton invariant mass m₄ℓ.**
$$ m_{4\ell} = \left| \sum_{i=1}^{4} p_i \right| = \sqrt{\left(\textstyle\sum_i E_i\right)^2 - \left|\textstyle\sum_i \vec{p}_i\right|^2} $$
where the sum runs over the four selected leptons' four-momenta. The input
ntuples already provide `m4l`, `mZ1`, `mZ2` per candidate, plus per-lepton
kinematics, so we can recompute m₄ℓ for cross-checks (e.g. under lepton-scale
variations) from the lepton four-vectors using `vector`.

Two physical quantities are extracted from the m₄ℓ spectrum:

1. **Signal strength μ** — the ratio of the observed H→4ℓ yield to the
   Standard-Model expectation, μ = σ·BR (observed) / σ·BR (SM). Extracted from
   a binned maximum-likelihood template fit of m₄ℓ (Section 4). μ = 1 by
   construction in the SM.
2. **Higgs mass m_H** — the position of the m₄ℓ peak, extracted from the
   signal-dominated region (Section 4.2).

The interpretation: μ tests the overall H→4ℓ rate against the SM; m_H is a
direct mass measurement. Both are compared to the reference (Section 6).

---

## 2. Signal and Background Inventory

All samples are flat ntuples (`h4lTree`) in `data/`, produced by
`h4l_ntuplize.py` over CMS Open Data NANOAOD. Each entry is one pre-built 4ℓ
candidate; `finalState ∈ {0,1,2}` labels the three channels (exact mapping to
4μ/4e/2e2μ to be confirmed in Phase 2 from lepton `pdgId`). The `Metadata`
tree carries `nEvents` (sum of generated events) for MC normalization. There
is **no per-event weight branch** — MC normalization is therefore a flat
per-sample weight (Section 2.3).

### 2.1 Classification

| Process | Sample file | σ (pb) | Class | Role |
|---------|-------------|--------|-------|------|
| ggH→ZZ→4ℓ | GluGluToHToZZ.root | 0.00602392 | **signal** | ggF production (dominant) |
| VBF H→ZZ→4ℓ | VBF_HToZZ.root | 0.00048794 | **signal** | VBF production |
| ZH→ZZ→4ℓ | ZHToZZ.root | 0.000098394 | **signal** | associated ZH |
| W⁺H→ZZ→4ℓ | WPHToZZ.root | 0.0001072352 | **signal** | associated W⁺H |
| W⁻H→ZZ→4ℓ | WMHToZZ.root | 0.0000670716 | **signal** | associated W⁻H |
| qqZZ→4ℓ | ZZTo4L.root | 1.325 | **irreducible** | dominant continuum background |
| ggZZ→2e2μ | GGZZ2E2Mu.root | 0.003185 | **irreducible** | gg→ZZ (loop), 2e2μ |
| ggZZ→4e | GGZZ4E.root | 0.001575 | **irreducible** | gg→ZZ (loop), 4e |
| ggZZ→4μ | GGZZ4Mu.root | 0.001619 | **irreducible** | gg→ZZ (loop), 4μ |
| DY+jets (M-50) | DYJetsToLL.root | 5396.0 | **reducible** | Z+X fakes / non-prompt leptons |
| tt̄→2ℓ | TTBar.root | 52.70 | **reducible** | non-prompt leptons |
| Data (10 fb⁻¹) | data_secret_10fb.root | — | — | 2017 collision data, 719 candidates |

The five signal samples are **summed into a single signal template** (all
production modes), scaled coherently by μ in the fit — μ measures the
inclusive H→4ℓ rate relative to the SM, matching the requester's "signal
strength μ" deliverable.

### 2.2 Relative importance (order of magnitude)

- **qqZZ (irreducible)** is the dominant background under and around the peak:
  largest cross section among the ZZ→4ℓ processes (1.325 pb) and the same
  final state as signal. Estimated to dominate the background by ~5–10×.
- **ggZZ (irreducible)** is a ~10–15% correction to the total ZZ→4ℓ continuum;
  it has a large theory (K-factor) uncertainty [L2].
- **DY+jets and tt̄ (reducible)** contribute fake/non-prompt-lepton candidates,
  concentrated at low m₄ℓ; expected to be subdominant after selection. Per the
  requester directive [D1], these are taken from **MC only** (no data-driven
  fake-rate / Z+X estimate). DY has a huge cross section (5396 pb) but a tiny
  efficiency to yield four selected leptons — Phase 2/3 will quantify the
  surviving yield and its MC statistical adequacy [L1].

### 2.3 MC normalization

Each MC sample is normalized to the data luminosity L = 10 fb⁻¹ with a flat
per-sample weight
$$ w = \frac{\sigma \cdot L}{N_\text{gen}} $$
where σ is from the table above and N_gen is the `Metadata/nEvents` value for
that sample. There is no generator weight branch, so all events in a sample
carry the same weight (to be confirmed in Phase 2). The cross sections are the
requester-provided authoritative inputs [A1]; L = 10 fb⁻¹ is fixed by the data
sample name [A2].

---

## 3. Selection Strategy

The selection follows the established CMS H→ZZ→4ℓ cut-based logic (loosely, per
the reference), adapted to the available ntuple branches. The ntuples already
provide pre-built candidates with `mZ1`, `mZ2`, `m4l`, and per-lepton ID /
isolation / impact-parameter variables (`pfRelIso03`, `miniRelIso`, `sip3d`,
`muMedium`/`muTight`, `elCutBased`/`elMvaWP90`, etc.), so Phase 3 applies
object-level and pair-level cuts on top.

### 3.1 Baseline selection logic (V_baseline)

1. **Lepton ID/isolation (loose, prompt-like).** Muons: `muPF` && (`muMedium`
   or `muTight`); electrons: `elMvaWP90` (or `elCutBased ≥ medium`). Isolation:
   `pfRelIso03` below a loose threshold (target ~0.35, to be fixed in Phase 3
   from S/√B optimization on MC). Impact parameter: `sip3d < 4`, with loose
   `dxy`/`dz` cuts — standard prompt-lepton requirements.
2. **Lepton kinematics.** All four leptons within tracker/muon acceptance
   (|η| < 2.5 for e, < 2.4 for μ); pT-ordered thresholds on the leading two
   leptons (target 20/10 GeV) and a floor (~5–7 GeV) on the softer two.
3. **Pairing.** Build two same-flavour opposite-sign (SFOS) lepton pairs.
   **Z₁** = the SFOS pair with invariant mass closest to the PDG m_Z; **Z₂** =
   the remaining pair. (The ntuple `zId`/`mZ1`/`mZ2` encode this; Phase 2/3
   verify the convention.)
4. **Z mass windows.** mZ1 ∈ [40, 120] GeV; mZ2 ∈ [12, 120] GeV (off-shell Z
   allowed down to 12 GeV) — the standard HZZ4l windows.
5. **Ghost / QCD-suppression.** Remove low-mass dilepton resonances and ghosts:
   m(ℓᵢℓⱼ) > 4 GeV for all SFOS pairs, and ΔR(ℓᵢ,ℓⱼ) > 0.02 to suppress
   overlapping/duplicate tracks.
6. **Mass range.** Retain candidates with m₄ℓ in a broad fit window (target
   [70, 180] GeV) so the template fit sees both the peak and the surrounding
   background continuum.

### 3.2 Selection variant for comparison (V_tight)

Per the spec's "≥2 candidate selection approaches" requirement, Phase 3
compares V_baseline against a **qualitatively distinct, tighter-purity
variant V_tight**: tighter isolation (`pfRelIso03` ~0.20 and/or
`miniRelIso`-based), tighter electron ID (`elMvaWP80`) and `muTight`, plus a
narrower off-shell window (mZ2 ≥ 12 GeV with an additional smart-cut
m(Z₂)-vs-m₄ℓ requirement). V_tight trades signal efficiency for reduced
reducible (DY/tt̄) and fake contamination.

**Quantitative comparison plan (Phase 3):** evaluate both on MC with a common
figure of merit — expected S/√(S+B) in a signal window (target m₄ℓ ∈
[118,130] GeV) **and** the m₄ℓ-fit expected μ uncertainty — on the same
sample. The chosen baseline is the one giving the smaller expected μ
uncertainty at acceptable purity. The comparison is evaluated on **MC /
expected sensitivity only**, never on observed data in the signal region
(search.md pitfall: "optimizing cuts on observed data").

### 3.3 MVA decision [D3]

No MVA-based selection is planned. **[D3] Decision: cut-based selection only.**
Rationale: (a) the requester explicitly scoped a *quick* analysis emphasizing a
clean cut-based selection and the m₄ℓ fit; (b) cut-based SFOS-pairing +
Z-window selection is the established, well-understood HZZ4l baseline and is
fully adequate for a 1D m₄ℓ template fit; (c) the discriminating power here is
overwhelmingly in m₄ℓ itself, not in a multivariate combination of the
available per-lepton variables. MVA inputs that *would* be available if an MVA
were pursued (per-lepton `elMvaBdt`, isolation, SIP3D, Z₁/Z₂ masses, pT4l,
η4l) are noted here for the record. Per `methodology/03-phases.md`, Phase 3
treats cut-based as a downscope from MVA; this [D3] documents the
infeasibility-by-scope and is flagged for Phase 1 review validation.
**Confidence: MEDIUM** — a reviewer may judge that at least a minimal BDT
cross-check is warranted; flagged for the human/review gate.

---

## 4. Extraction Method

### 4.1 Signal strength μ — binned likelihood template fit (primary)

The μ extraction is a **binned maximum-likelihood fit of the m₄ℓ spectrum**
implemented in **pyhf** (HistFactory model). This is a *search-like* shape fit,
so `conventions/search.md` is the governing conventions file (Section 5).

- **Templates:** one signal template (all five production modes summed,
  scaled by the parameter of interest μ) and one template per background
  group (qqZZ, ggZZ summed over its three final states, DY+jets, tt̄), each
  normalized per Section 2.3.
- **Fit:** done **per channel (4e, 4μ, 2e2μ) as separate pyhf channels in a
  single combined workspace**, sharing μ, so per-channel μ and combined μ are
  both available.
- **POI:** μ (signal strength), bounded μ ≥ 0 for limit/CLs-style statements
  but allowed to float for the central measurement (a measurement quotes the
  best-fit μ̂ with its profile-likelihood interval).
- **Nuisance parameters:** background normalization NPs (Section 5) plus
  per-bin MC statistical terms (Barlow–Beeston-lite, pyhf `staterror`),
  important here because the DY/tt̄ MC has low surviving statistics [L1].
- **Test statistic / interval:** profile-likelihood ratio; the central result
  is μ̂ with its 68% CL interval from the likelihood scan. We also report the
  expected (Asimov) μ uncertainty at Phase 4a.

**Binning:** uniform m₄ℓ bins (target ~2 GeV) over the fit window
[70, 180] GeV, with a finer peak region if statistics allow; to be justified in
Phase 3/4a by resolution and per-bin occupancy (search.md asymptotic-validity
note: validate against toys if any signal bin has < ~5 expected events).

### 4.2 Higgs mass m_H — peak extraction

m_H is extracted from the **position of the m₄ℓ peak**:

- **Primary approach:** build a signal **resolution model** from the summed
  signal MC (e.g. a double-sided Crystal Ball or a Gaussian core fit to the MC
  m₄ℓ shape), fix its shape, and fit the peak position to data in a narrow
  window around the peak (background modeled as a smooth function or the MC
  template). The fitted peak mean is m_H.
- **Cross-check:** a simple Gaussian fit to the signal-region m₄ℓ distribution
  (data minus background-MC), and the MC-truth peak of the signal template as a
  closure reference.
- This is implemented with `zfit`/`iminuit` (unbinned) or via a fine-binned
  `pyhf`/`iminuit` fit; the choice is finalized in Phase 4a.

### 4.3 Method parity with the reference (binding) [D4]

The reference (arXiv:1706.09936) extracts μ and m_H from a **multi-dimensional
fit** using a matrix-element kinematic discriminant (MELA, e.g. D_bkg^kin
combined with m₄ℓ and its per-event mass uncertainty). We deliberately use a
**simpler 1D m₄ℓ template fit** [D4].

**Justification (not "because it's easier"):** (a) the requester scoped a quick
analysis whose deliverable is explicitly a 1D m₄ℓ fit and μ; (b) the MELA
discriminant requires per-event matrix-element probabilities that are **not
available** in these ntuples (no D_bkg/D_kin branches), making the
multi-dimensional fit infeasible without re-deriving MELA inputs from full
kinematics — outside the quick-analysis scope; (c) for an inclusive μ and a
mass measurement, m₄ℓ carries the dominant signal/background separation, so a
1D fit captures most of the sensitivity, at the cost of a somewhat larger μ
uncertainty than the reference. We record the reference's MELA-based
multi-dimensional fit as **the more sophisticated method** and note that adding
even a simple kinematic discriminant would be the natural improvement beyond
this quick analysis. Per `methodology/03-phases.md` method-parity rule, this
decision is binding and reviewed at Phase 4a; the infeasibility (missing MELA
inputs) is the documented technical limitation. **Confidence: MEDIUM.**

---

## 5. Systematic Uncertainty Plan

The governing conventions file is `conventions/search.md` (the μ extraction is
a search-like binned-likelihood shape fit). Below, **every** required source in
search.md is enumerated with "Will implement" or "Not applicable because
[reason]". Per the requester directives, lepton-efficiency and
trigger-efficiency systematics are explicitly out of scope and marked N/A with
the directive as the reason. **Focus** is on background normalizations with
motivated uncertainties. All numeric magnitudes below are *intended* values
flagged "source in Phase 4a" unless already pinned to the requester-provided
cross-section table.

### 5.1 search.md "Signal modeling"

| Source | Decision | Plan / sizing |
|--------|----------|---------------|
| Signal cross-section theory unc (μR, μF, higher-order) | **Will implement** | Normalization NP on the signal template. Size from LHCHWG ggH N3LO + VBF/VH theory uncertainties (intended ~few %, e.g. QCD scale + PDF+αs on the dominant ggF mode). Source: LHC Higgs WG YR4 / PDG — fetch in Phase 4a [S1]. |
| Signal acceptance (generator/ISR) | **Not applicable because** single signal generator per mode is provided in the ntuples; no alternative generator available. Documented as limitation [L3]; the dominant signal uncertainty here is the cross-section/μ scale, not acceptance. |
| Signal shape (mass/width/resolution) | **Will implement (mass only)** | For m_H: propagate the lepton-momentum-scale effect on the m₄ℓ peak as a shape/scale variation (Section 5.4). For μ: signal-shape variation is subdominant and covered by the staterror + scale terms. |
| ISR modeling | **Not applicable because** this is a pp (not e⁺e⁻) analysis; ISR is not a primary beam systematic. The pp equivalents (PDF, pileup) are handled below. |

### 5.2 search.md "Background estimation"

| Source | Decision | Plan / sizing |
|--------|----------|---------------|
| Irreducible-background generator/normalization (the search.md "4-fermion backgrounds" row) | **Will implement** | **qqZZ normalization NP:** sized from the NLO QCD scale + PDF uncertainty on the qq→ZZ→4ℓ cross section (intended ~10%; source: CMS HZZ4l 2017 / MCFM NLO — fetch Phase 4a [S2]). **ggZZ normalization NP:** sized from the large gg→ZZ K-factor uncertainty (intended ~30%, reflecting the NLO/LO loop-induced K-factor spread; source: reference paper + Caola/Melnikov ggZZ K-factor literature — fetch Phase 4a [S3]). This is the FOCUS of the systematic program per requester directive. |
| Background normalization (theory/CR) | **Will implement** | **DY+jets and tt̄ normalization NPs:** sized from their cross-section uncertainties combined with the (large) MC statistical uncertainty on the surviving yield. Because fakes are MC-only [D1], the normalization unc must cover the absence of a data-driven Z+X estimate; intended a conservative but motivated value (target ~30–50%) justified by the cross-section unc ⊕ MC-stat ⊕ the known MC-vs-data fake-rate mismodeling documented in the reference. Final magnitude sourced in Phase 4a [S4]; sizing rule from CLAUDE.md "Systematic variation sizing" applies (no arbitrary inflation). |
| Background shape | **Will implement (limited)** | qqZZ shape variation from μR/μF scale reweighting if available; otherwise the dominant background-shape effect is captured by the per-bin staterror. Documented at Phase 4a. |
| qqbar(γ) / 2-fermion modeling | **Not applicable because** this LEP2-specific row (KK2f-type 2-fermion processes) does not map onto the pp HZZ4l background set; the analogous reducible background (DY) is handled via its normalization NP above. |
| MC statistics | **Will implement** | pyhf `staterror` (Barlow–Beeston-lite): one NP per bin absorbing finite-MC-sample uncertainty. Essential given low DY/tt̄ surviving statistics [L1]. |

### 5.3 search.md "Detector and reconstruction"

| Source | Decision | Plan / sizing |
|--------|----------|---------------|
| Detector simulation model | **Not applicable because** Open Data ntuples provide a single fullsim; no alternative detector model. Documented as limitation [L3]. |
| Object calibration (energy scale/resolution/efficiency SF) | **Lepton ENERGY/MOMENTUM SCALE: Will implement** (it directly moves the m₄ℓ peak → m_H, see 5.4). **Lepton EFFICIENCY scale factors: Not applicable because [requester directive — skip lepton-efficiency systematics].** **Trigger efficiency: Not applicable because [requester directive — skip trigger-efficiency systematics].** |
| Beam energy | **Not applicable because** LHC beam energy is known to ≪ relevant precision for this measurement and is not a LEP-style calibration systematic. |
| Luminosity | **Will implement** | Normalization NP applied to all MC (signal + backgrounds). Size from the CMS 2017 integrated-luminosity uncertainty (intended ~2.3–2.5%; source: CMS LUM-17-004 / CMS-PAS-LUM-17-004 — fetch Phase 4a [S5]). |

### 5.4 Lepton momentum-scale systematic (for m_H) — Will implement

A lepton momentum/energy-scale variation (±, intended ~0.1–0.3% for muons,
slightly larger for electrons; source to be fetched in Phase 4a [S6]) is
applied to the per-lepton four-vectors, m₄ℓ recomputed, and the shift in the
fitted peak position propagated to m_H. This is the dominant *mass* systematic.
It is distinct from lepton-efficiency (which is skipped). Implemented by
recomputing m₄ℓ from the per-lepton branches with scaled pT.

### 5.5 search.md "Theory inputs"

| Source | Decision | Plan / sizing |
|--------|----------|---------------|
| QCD scale variations (μR, μF) | **Will implement** | Folded into the signal [S1] and qqZZ/ggZZ [S2,S3] normalization NPs above (scale uncertainty is the principal component of those theory normalizations). |
| Fragmentation model | **Not applicable because** the final state is leptonic (4ℓ); hadronization does not affect the signal or the leptonic-decay backgrounds at leading order. |
| Heavy-flavour treatment | **Not applicable because** no b-tagging is used in this inclusive 4ℓ selection. |

### 5.6 Validation checks (search.md "Required validation checks")

Planned for Phase 4: (1) **closure** — fit Asimov/MC pseudo-data and recover
μ=1; (2) **signal injection and recovery** at 0×, 1×, 2×, 5× (bias < 20%);
(3) **NP pulls/constraints** within ±1σ, flag pulls > 2σ; (4) **impact
ranking** of NPs on μ (expect lumi + qqZZ/ggZZ norm to dominate); (5)
**goodness-of-fit** chi²/ndf and toy-based p-value (p > 0.05). Look-elsewhere
effect is **not applicable** — m_H is a fixed, theory-predicted mass region
(local significance is the relevant one; state explicitly per search.md
pitfall).

### 5.7 Completeness note

Sources explicitly **omitted by requester directive** (not silent omissions):
lepton-efficiency SF systematic, trigger-efficiency systematic. Sources
omitted as **N/A by physics/data constraints** (documented above): signal
acceptance/ISR (single generator), detector-simulation alternative,
2-fermion-generator, fragmentation, heavy-flavour, beam energy. This table is
binding and is re-checked at Phase 4a against both search.md and the reference
program (Section 6).

---

## 6. Reference Analysis and Comparison Targets

### 6.1 Primary reference

**CMS, "Measurements of properties of the Higgs boson decaying into the
four-lepton final state in pp collisions at √s = 13 TeV," JHEP 11 (2017) 047,
arXiv:1706.09936.** Headline results (verified from the paper abstract via
WebFetch, 2026-06-03):

- **m_H = 125.26 ± 0.21 GeV**
- **μ = 1.05 +0.19/−0.17** (at the reference mass m_H = 125.09 GeV)
- 35.9 fb⁻¹, √s = 13 TeV.

These are the **binding Phase 4c comparison targets** (§6.8). Note our dataset
is 10 fb⁻¹ (≈0.28× the reference luminosity) and uses a simpler 1D fit, so we
expect a **larger statistical μ uncertainty** (naively ~√(35.9/10) ≈ 1.9× the
reference stat error, before the additional penalty from the 1D-vs-MELA method)
and a larger m_H uncertainty. Our μ should be statistically consistent with
both the reference (1.05) and the SM (μ=1); m_H should be consistent with the
PDG/reference value.

### 6.2 Reference systematic program (high level)

| Source | Reference treatment | Our treatment |
|--------|---------------------|---------------|
| Luminosity | ~2.3–2.5% normalization (CMS 2017) | Will implement [S5] |
| Lepton reco/ID/iso efficiency | Per-lepton scale factors, few % | **Skipped (requester directive)** |
| Lepton momentum/energy scale | Sub-percent, affects mass | Will implement [S6] (mass) |
| qqZZ normalization + shape | NLO QCD (scale) + PDF, ~10% | Will implement [S2] |
| ggZZ K-factor | Large, ~10–30% | Will implement [S3] |
| Reducible (Z+X) background | **Data-driven fake-rate** estimate | **MC-only DY+tt̄ [D1]**, normalization NP [S4] |
| Signal theory (ggH N3LO etc.) | LHCHWG QCD scale + PDF+αs | Will implement [S1] |
| MC statistics | Bin-by-bin | Will implement (staterror) |

The two methodological departures from the reference are: **(i)** MC-only
reducible background instead of the data-driven Z+X estimate [D1], and **(ii)**
1D m₄ℓ template fit instead of the MELA multi-dimensional fit [D4].

### 6.3 Other references (to consult in Phase 4a)

- CMS H→4ℓ legacy / Run 1 (1312.5353-type) and ATLAS H→4ℓ — for cross-checking
  the qqZZ/ggZZ normalization-uncertainty magnitudes and the reducible-
  background size. To be queried/fetched in Phase 4a when pinning [S1]–[S6].

---

## 7. Decision / Constraint / Limitation Labels

**Decisions [D]:**
- **[D1]** Reducible (fake/non-prompt) background from **DYJetsToLL + tt̄ MC
  only** — no data-driven fake-rate / Z+X estimate. (Requester directive.)
- **[D2]** Lepton-efficiency and trigger-efficiency systematics **skipped**.
  (Requester directive.)
- **[D3]** **Cut-based selection only**, no MVA (quick-analysis scope; m₄ℓ
  carries the dominant separation; MELA-type inputs unavailable). Confidence
  MEDIUM — flagged for review.
- **[D4]** **1D m₄ℓ binned template fit** for μ (and peak fit for m_H) instead
  of the reference MELA multi-dimensional fit. Justified by missing per-event
  MELA inputs and quick-analysis scope; reference method noted as the more
  sophisticated alternative. Confidence MEDIUM — binding, reviewed Phase 4a.
- **[D5]** **Five signal production modes summed into one signal template**,
  scaled by a single inclusive μ.
- **[D6]** Systematic **focus on background normalizations** with motivated
  (cross-section/theory-derived) uncertainties; signal theory + luminosity +
  lepton momentum scale (for mass) also included.

**Constraints [A]:**
- **[A1]** MC normalization uses the **requester-provided cross sections**
  (prompt.md table) as authoritative inputs.
- **[A2]** Integrated luminosity fixed at **10 fb⁻¹** (data sample name).
- **[A3]** MC normalization is a **flat per-sample weight** (no per-event
  generator weight branch in the ntuples).

**Limitations [L]:**
- **[L1]** Low surviving MC statistics for DY/tt̄ may make the reducible
  template noisy; mitigated by per-bin staterror NPs and a conservative
  normalization unc. To be quantified in Phase 2/3.
- **[L2]** ggZZ carries a large K-factor (theory) uncertainty.
- **[L3]** Single MC generator per process (no alternative-generator
  acceptance/detector-model systematic available).
- **[L4]** 10 fb⁻¹ (vs 35.9 fb⁻¹ reference) → larger statistical uncertainty on
  μ and m_H; the result is expected to be statistically consistent with but
  less precise than the reference.

---

## 8. Flagship Figures (~5, for a <20-page note)

1. **m₄ℓ stacked spectrum with fit** — data points over stacked signal +
   background templates across the full fit window, with the post-fit signal
   overlaid. *The* money plot.
2. **Per-channel m₄ℓ** — 4e / 4μ / 2e2μ m₄ℓ distributions (one composed
   multi-panel figure), showing the peak in each channel.
3. **Z₁ and Z₂ mass distributions** — mZ1 and mZ2 after selection (one
   composed figure), validating the SFOS pairing and the on-shell/off-shell
   structure.
4. **μ likelihood scan** — profile-likelihood −2Δln L vs μ (combined and
   per-channel), showing μ̂ and its 68% interval, with μ=1 and the reference
   μ=1.05 marked.
5. **m_H peak fit** — the signal-region m₄ℓ peak with the fitted resolution
   model and extracted m_H, with the reference/PDG m_H marked.

(Optional 6th if space allows: NP impact ranking / pull plot. Kept optional to
respect the <20-page directive.)

**Methodology diagram:** a single schematic of the analysis flow
(ntuples → selection → per-channel m₄ℓ templates → pyhf combined fit → μ, m_H)
for the AN method section.

---

## 9. Summary

We will measure the H→ZZ*→4ℓ signal strength μ and the Higgs mass m_H from the
four-lepton invariant-mass spectrum in CMS Open Data (2017, 10 fb⁻¹), loosely
following arXiv:1706.09936. The selection is cut-based (SFOS pairing,
Z-mass windows, loose lepton ID/isolation), with a tighter-purity variant
compared in Phase 3. μ is extracted from a per-channel-combined **pyhf binned
template fit of m₄ℓ**; m_H from a peak fit using a signal-MC resolution model.
The systematic program **focuses on background normalizations** (qqZZ NLO scale
[S2], ggZZ K-factor [S3], DY/tt̄ cross-section ⊕ MC-stat [S4]) plus luminosity
[S5], signal theory [S1], lepton momentum scale for mass [S6], and per-bin MC
statistics; lepton- and trigger-efficiency systematics are skipped per
directive. Comparison targets are the reference μ = 1.05 +0.19/−0.17 and
m_H = 125.26 ± 0.21 GeV.

---

## 10. Open Issues / Confidence Flags

- **finalState ↔ channel mapping** (4μ/4e/2e2μ ↔ 0/1/2): **LOW confidence**,
  to be confirmed in Phase 2 from lepton `pdgId`. Does not block the strategy.
- **[D3] MVA omission** and **[D4] 1D-vs-MELA fit**: **MEDIUM confidence** —
  both are scope-driven and physically justified, but a reviewer may request a
  minimal BDT or kinematic-discriminant cross-check. Flagged for the review /
  human gate.
- **Systematic magnitudes [S1]–[S6]:** stated as intended values; **all must be
  pinned to citations in Phase 4a** (LHCHWG, MCFM/NLO, ggZZ K-factor
  literature, CMS LUM-17-004, lepton-scale notes). No magnitude is taken from
  memory.
- **Reducible-background MC-stat adequacy [L1]:** to be quantified in Phase 2;
  if DY/tt̄ yields are too sparse, the normalization-NP sizing may need
  revisiting at Phase 4a.

---

## References

- CMS Collaboration, "Measurements of properties of the Higgs boson decaying
  into the four-lepton final state in pp collisions at √s = 13 TeV,"
  JHEP 11 (2017) 047, arXiv:1706.09936. (μ, m_H comparison targets; verified
  from abstract 2026-06-03.)
- A. L. Read, "Presentation of search results: the CLs technique,"
  J. Phys. G 28, 2693 (2002). (Fit/limit methodology — search.md.)
- G. Cowan, K. Cranmer, E. Gross, O. Vitells, "Asymptotic formulae for
  likelihood-based tests of new physics," Eur. Phys. J. C71, 1554 (2011).
- L. Heinrich, M. Feickert, G. Stark, "pyhf," JOSS 6, 2823 (2021). (Statistical
  model implementation.)
- Cross sections and luminosity: `prompt.md` sample table (requester-provided,
  authoritative for normalization).
- Systematic magnitudes [S1]–[S6]: sources to be fetched in Phase 4a (LHC
  Higgs WG YR4; MCFM/NLO qqZZ; ggZZ K-factor literature; CMS-PAS-LUM-17-004;
  CMS lepton-scale documentation; PDG for m_Z, m_H).
