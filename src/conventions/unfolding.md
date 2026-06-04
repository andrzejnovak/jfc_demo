# Unfolding Measurements

For analyses that correct a measured distribution for detector effects to a particle-level result, by any method (matrix inversion, iterative, bin-by-bin, ML, …).

## When this applies
Any analysis correcting a detector-level distribution to a particle-level result, regardless of correction method.

## What the measurement must deliver
1. **A precise particle-level definition** (which particles, phase space, ISR/FSR treatment, lifetime threshold) — stated in Phase 1 and held fixed throughout; it determines what the measurement *means*.
2. **A correction procedure that passes the quality gates** (method is the analyst's choice).
3. **A covariance matrix** — statistical + systematic + total, positive semi-definite, machine-readable.
4. **An alternative-method cross-check** — ≥1 independent correction procedure on the same data; disagreement requires investigation.

## Literature requirement
Before choosing a method, read how ≥2 published analyses of the same/similar observable handled the correction (method, response-matrix construction, validation tests, dominant systematics). Cite them and justify any deviation. If published analyses successfully unfold an observable this analysis claims is unfoldable, the burden of proof is on this analysis.

## Quality gates (pass/fail; method is the analyst's choice)
1. **Closure** — the correction applied to MC recovers MC truth within statistical precision (chi² p > 0.05). Bin-by-bin requires split-sample closure (derive factors on one half, apply to the other).
2. **Stress test** — the correction applied to a reweighted MC truth (different shape) recovers the reweighted truth; use graded magnitudes (5/10/20/50%) to characterize resolving power.
3. **Prior/model dependence** — quantify how much the result depends on the MC model used to derive the correction (typically the dominant shape systematic).
4. **Covariance validation** — PSD (all eigenvalues ≥ 0), condition number < 10¹⁰, visualize the correlation matrix. Construction must match the method: bootstrap (bin-by-bin; event-level resample, N ≥ 500), toy MC (iterative; Poisson-fluctuate the input, unfold each), or analytical propagation (simple bin-by-bin; misses shared-denominator correlations). Compute on the full dataset (subset scaling by N/n is approximate — document if used). **chi² uses the full covariance** (diagonal-only underestimates chi² for positively-correlated bins); report both for transparency; if condition number > 10⁸ note the covariance chi² may be unreliable.
5. **Data/MC input validation** — data/MC comparisons for all kinematic variables entering the observable, before building the correction.

If any gate fails: investigate and attempt remediation before accepting as a limitation; document what was tried.

## Pitfalls
- **Normalizing before correcting** — normalize after correction + efficiency (pre-normalization introduces bin correlations the correction doesn't model).
- **Confusing closure with validation** — applying factors to the same MC that derived them is an algebraic identity.
- **Flat systematic estimates** — a perfectly flat relative shift across all bins likely means the systematic was assigned, not propagated.
- **Double-counting model dependence** — two "independent" sources using the same variation mechanism (e.g. both a 50% truth tilt) are not independent; merge or orthogonalize.
- **Wrong matching strategy** — for variable-multiplicity observables (substructure, fragmentation functions, Lund declusterings), matching individual sub-objects (1st reco ↔ 1st gen) can produce artificially terrible response matrices; read how published analyses construct theirs.
- **Observable redefinition is not a systematic** — removing a particle category (e.g. neutrals from thrust) changes WHAT is measured, not the uncertainty; keep it as a cross-check or run separate unfolding chains with separate covariances, and evaluate detector response by varying response parameters at fixed particle-level definition.

## References
Cowan, "Statistical Data Analysis" (Oxford, 1998) — unfolding and covariance propagation in HEP.
