# COMMITMENTS — cms_h4l

Machine-readable tracking of every Phase 1 commitment. Update at every phase
boundary. At Phase 5 review, every line must be `[x]` (resolved) or `[D]`
(formally downscoped with documented justification). Any `[ ]` remaining at
Phase 5 is Category A.

Status legend: `[ ]` not yet addressed · `[x]` resolved/implemented ·
`[D]` formally downscoped (with reason).

## Decisions (from STRATEGY.md §7)

- [ ] D1: Reducible background from DYJetsToLL + tt̄ MC only (no data-driven Z+X). [requester directive]
- [ ] D2: Lepton-efficiency and trigger-efficiency systematics skipped. [requester directive]
- [ ] D3: Cut-based selection only, no MVA (quick scope; m4l dominant; MELA inputs absent). Confidence MEDIUM — review-flagged.
- [ ] D4: 1D m4l binned template fit for μ + peak fit for m_H, instead of reference MELA multi-dimensional fit. Confidence MEDIUM — binding, reviewed Phase 4a.
- [ ] D5: Five signal production modes summed into one signal template scaled by inclusive μ.
- [ ] D6: Systematic focus on background normalizations with motivated (xsec/theory) uncertainties.

## Constraints (from STRATEGY.md §7)

- [ ] A1: MC normalization uses requester-provided cross sections (prompt.md) as authoritative inputs.
- [ ] A2: Integrated luminosity fixed at 10 fb⁻¹ (data sample name).
- [ ] A3: MC normalization is a flat per-sample weight (no per-event weight branch).

## Limitations (from STRATEGY.md §7)

- [ ] L1: Low surviving DY/tt̄ MC statistics — quantify Phase 2/3; mitigate with staterror + conservative norm unc.
- [ ] L2: ggZZ large K-factor (theory) uncertainty.
- [ ] L3: Single MC generator per process (no alt-generator acceptance/detector-model systematic).
- [ ] L4: 10 fb⁻¹ vs 35.9 fb⁻¹ reference → larger stat uncertainty; expect consistent-but-less-precise result.

## Selection (from STRATEGY.md §3)

- [ ] SEL1: Implement V_baseline cut-based selection (loose ID/iso, SFOS pairing, Z1/Z2 windows, ghost removal, pT thresholds).
- [ ] SEL2: Implement V_tight variant (tighter iso/ID, narrower Z2) and compare quantitatively in Phase 3.
- [ ] SEL3: Comparison uses common FoM (S/√(S+B) in [118,130] GeV AND expected μ uncertainty) on MC/expected only — never observed data in SR.
- [ ] SEL4: Confirm finalState↔channel mapping (0/1/2 ↔ 4μ/4e/2e2μ) from lepton pdgId in Phase 2.

## Extraction method (from STRATEGY.md §4)

- [ ] EXT1: pyhf per-channel combined binned template fit of m4l; signal scaled by μ; bkg normalization NPs + staterror.
- [ ] EXT2: m_H from peak fit using signal-MC resolution model (primary) + Gaussian/MC-truth cross-checks.
- [ ] EXT3: m4l binning justified by resolution + per-bin occupancy; validate asymptotics vs toys if any signal bin < ~5 expected events.

## Systematic sources (from STRATEGY.md §5) — Will implement

- [ ] S1: Signal cross-section theory uncertainty (ggH N3LO scale + PDF+αs etc.) — source LHCHWG YR4, fetch Phase 4a.
- [ ] S2: qqZZ normalization NP — NLO QCD scale + PDF (~10% intended) — source MCFM/NLO + CMS HZZ4l, fetch Phase 4a.
- [ ] S3: ggZZ normalization NP — large K-factor uncertainty (~30% intended) — source ggZZ K-factor literature, fetch Phase 4a.
- [ ] S4: DY+tt̄ reducible normalization NP — xsec unc ⊕ MC-stat ⊕ MC-only-fake coverage — source Phase 4a.
- [ ] S5: Luminosity normalization NP (~2.3–2.5% CMS 2017) — source CMS-PAS-LUM-17-004, fetch Phase 4a.
- [ ] S6: Lepton momentum/energy scale (for m_H) — source CMS lepton-scale docs, fetch Phase 4a.
- [ ] S7: MC statistical uncertainty via pyhf staterror (Barlow–Beeston-lite).

## Systematic sources — Not applicable (documented, not silent omissions)

- [D] NA1: Signal acceptance/ISR generator systematic — single signal generator available [L3].
- [D] NA2: Lepton EFFICIENCY scale-factor systematic — requester directive [D2].
- [D] NA3: Trigger-efficiency systematic — requester directive [D2].
- [D] NA4: Detector-simulation alternative-model systematic — single fullsim [L3].
- [D] NA5: 2-fermion (qqbar-γ) generator systematic — LEP2-specific, no pp analogue beyond DY norm.
- [D] NA6: Fragmentation/hadronization systematic — leptonic final state.
- [D] NA7: Heavy-flavour treatment — no b-tagging used.
- [D] NA8: Beam-energy systematic — LHC beam energy known to ≪ relevant precision.

## Validation checks (from STRATEGY.md §5.6)

- [ ] V1: Closure — fit Asimov/MC pseudo-data, recover μ=1.
- [ ] V2: Signal injection/recovery at 0×, 1×, 2×, 5× (bias < 20%).
- [ ] V3: NP pulls/constraints within ±1σ (flag > 2σ).
- [ ] V4: Impact ranking of NPs on μ (expect lumi + qqZZ/ggZZ to dominate).
- [ ] V5: GoF — chi²/ndf + toy-based p-value (p > 0.05).
- [D] V6: Look-elsewhere effect — N/A (fixed theory-predicted mass region; report local significance).

## Comparison targets (from STRATEGY.md §6) — binding at Phase 4c

- [ ] C1: μ = 1.05 +0.19/−0.17 (arXiv:1706.09936, verified from abstract).
- [ ] C2: m_H = 125.26 ± 0.21 GeV (arXiv:1706.09936, verified from abstract).
- [ ] C3: Overlay reference μ and m_H on the μ-scan and m_H-peak flagship figures.

## Flagship figures (from STRATEGY.md §8)

- [ ] F1: m4l stacked spectrum with fit (money plot).
- [ ] F2: Per-channel m4l (4e/4μ/2e2μ composed figure).
- [ ] F3: Z1 and Z2 mass distributions (composed figure).
- [ ] F4: μ profile-likelihood scan (combined + per-channel) with μ=1 and reference marked.
- [ ] F5: m_H peak fit with resolution model and reference m_H marked.
- [ ] F6 (optional): NP impact ranking / pull plot.
- [ ] FD1: Analysis-flow methodology diagram (Phase 5).
