# Extraction Measurements (Double-Tag / Hemisphere Counting)

For analyses whose result comes from a closed-form expression of tagged/untagged yields in hemisphere pairs (the canonical case: R_b from N_tt/N_had via hemisphere tagging efficiencies), exploiting the self-calibrating property of multi-tag counting.

## When this applies
The primary result is computed from a closed-form formula on tagged/untagged hemisphere yields — NOT from a template fit or unfolding. **If the analysis is a binned likelihood fit to a discriminant shape, use `search.md` (signal extraction) or `unfolding.md` instead.** Tag-and-probe, branching-fraction ratios, and cross-section ratios share some conventions but should use dedicated files when available.

## Standard configuration
- **MC pseudo-data for Phase 4a** — generate counts from MC truth via the extraction formula (never real data); optionally Poisson-fluctuate to assess statistical reach. **Fixed seeds** for pseudo-data and the 10% subsample.
- **Per-subperiod granularity** — track the result per data-taking period as a standard cross-check.
- **Counting vs likelihood** — pure counting (closed-form) when the formula is simple and systematics transparent; likelihood extraction when multiple parameters/nuisances/correlations are involved. Document the choice.
- **Uncertainty propagation** — analytical (partial derivatives) for few inputs; toy-based (Poisson-fluctuate inputs, repeat, take RMS) for many correlated/non-linear inputs. Verify analytical against toys for the dominant sources.
- **Efficiency binning** — fine enough for kinematic dependence, coarse enough for ≥~100 MC events/bin.
- **Data-derived calibration (scale factors)** — when the extraction uses MC-derived efficiencies, derive data/MC scale factors from a control sample (tag-and-probe or similar) and apply them before extraction; if infeasible, assign the full data/MC difference as a systematic and document why. **Calibration independence is mandatory:** each calibration must come from an observable independent of the primary result. Deriving the correction by assuming the primary result equals a reference (back-substitution) is a diagnostic, NOT a calibration. Uncalibrated MC efficiencies without justification are Category A.

## Required systematic sources
**Efficiency modeling:** tag/selection efficiency (vary within its uncertainty — the result depends directly on it); efficiency correlation (hemisphere/object correlation — double-tag assumes independence; violations bias the result); MC efficiency model (alternative generators — fragmentation affects tagging efficiency).
**Background contamination:** non-signal contamination (vary background fractions within uncertainty); background composition (alternative mixture models).
**MC model dependence:** hadronization model (string vs cluster); physics parameters (heavy-quark mass, fragmentation-function parameters).
**Sample composition:** flavour composition (non-signal flavour fractions); production fractions (any external input contributes its uncertainty).

## Required validation checks
1. **Independent closure (Category A if fails):** apply the full procedure to a statistically independent MC sample (not the one used to derive efficiencies/corrections); pull (extracted − truth)/uncertainty must be < 2σ. If only one MC sample exists, split it with a fixed seed. A self-consistent extraction (deriving efficiencies and counting yields from the same sample) recovers the answer by construction — that is an algebra check, not closure (pull = 0 everywhere is a red flag).
2. **Parameter sensitivity table:** for each MC-derived input, compute |dResult/dParam|·σ_param; flag any contributing > 5× the data statistical uncertainty.
3. **10% diagnostic sensitivity (Phase 4b):** include ≥1 diagnostic genuinely sensitive to data/MC differences (data-derived tag/double-tag rates vs MC; self-calibrated parameter comparison) — comparing only the final extracted quantity is insensitive at 10% statistics.

## Pitfalls
- **Running on real data in Phase 4a** defeats the staged 4a→4b→4c validation (4a is MC pseudo-data only).
- **Insensitive 10% test** — the final quantity is dominated by correlated systematics; use intermediate diagnostics.
- **Assuming hemisphere independence** — QCD correlations (gluon splitting, color reconnection) violate it; evaluate the correlation coefficient from MC and propagate its uncertainty. With an MVA tagger, classifier inputs correlated with event-level/coupled-hemisphere quantities inflate the correlation factor C_q — check C_b near 1 (C_b < 0.8 or > 1.3 is a flag).
- **Circular luminosity derivation is Category A when published luminosities exist.** Deriving L = N/(ε·σ_theory) makes the rate fit recover its inputs (chi² = 0 by construction). Use published per-point luminosities (from the dedicated luminometer, the cited paper's tables, or HEPData); only after exhausting these may L be derived — and then the results use the heading "self-consistency check", not "measurement".
- **Correlated uncertainties in combinations** — shared sources (scale variation, generator choice) must enter 100% correlated, not in quadrature; document the correlation assumption per source.

## References
LEP/SLD EWWG, "Precision EW measurements on the Z resonance" (Phys. Rept. 427, 257, 2006); ALEPH R_b (Phys. Lett. B401, 163, 1997); SLD R_b (Phys. Rev. Lett. 80, 660, 1998); PDG EW review. Use `search_lep_corpus` for technique-specific double-tag systematic programs.
