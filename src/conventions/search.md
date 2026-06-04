# Search / Limit-Setting Analyses

For analyses testing for a signal against a background-only hypothesis — an exclusion limit, or a significance/p-value. Also the right file for a **shape-based signal-strength (μ) template fit** of a discriminant distribution.

## When this applies
The primary result is an observed/expected upper limit on a signal cross-section, coupling, or branching ratio, or a discovery significance — including bump hunts, cut-and-count, and shape-based fits. If the primary result is a corrected spectrum or extracted physical parameter, use `unfolding.md` or `extraction.md`.

## Standard configuration
- **CLs** (= CL_s+b / CL_b) for upper limits — avoids excluding signals the analysis has no sensitivity to.
- **Asymptotic approximation** acceptable when expected counts > ~5 per bin; validate against toys (or use toys) at low statistics.
- **Test statistic:** profile likelihood ratio with μ ≥ 0 (one-sided) for limits; q0 (with q0 = 0 when μ̂ < 0) for discovery significance — only upward fluctuations count as evidence. See Cowan et al. (2010).
- **Signal injection** at 0×, 1×, 2×, 5× the expected cross-section (see validation #2).
- **Blinding:** the signal-region discriminant in data is not examined until Phase 4b (10% subsample) / 4c (§4 protocol).

## Required systematic sources
For pp colliders, remove beam/ISR, and add luminosity as a normalization source.
**Signal modeling:** signal shape (alternative MC or mass/width/coupling variations — determines how signal spreads across bins).
**Background estimation:** irreducible-background normalization (within CR-constrained or theory uncertainty); 
**Detector and reconstruction:** object calibration (energy scale/resolution, efficiency SFs); luminosity (normalizes all simulation-based predictions). (Beam energy / ISR for e+e−.)
**Theory inputs:** QCD scale (independent μR, μF); PDF; fragmentation (string vs cluster) where relevant.

## Required validation checks
1. **Closure in validation regions** — predict VR yields from CR extrapolation; pass at p > 0.005 (chi²). Failure is Category A — fix the background model first.
2. **Impact ranking** — rank NPs by impact on μ/limit; top-ranked should be the physically expected dominant uncertainties.
3. **Goodness-of-fit** — chi²/ndf for the final extraction variable; acceptable p > 0.005.

## Pitfalls
- **Ignoring the look-elsewhere effect** — a 3σ local excess over a wide scan may be < 2σ globally.
- **Optimizing cuts on observed data** — optimize on expected sensitivity (MC S/√B), never on observed SR data.

## References
Read, "Presentation of search results: the CLs technique" (J. Phys. G 28, 2693, 2002); Cowan, Cranmer, Gross, Vitells, "Asymptotic formulae…" (EPJC 71, 1554, 2011); Heinrich et al., "pyhf" (JOSS 6, 2823, 2021); 
