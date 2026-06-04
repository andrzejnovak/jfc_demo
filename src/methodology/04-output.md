## Analysis Note Specification

The AN is versioned 4a→5: 4a writes a concise complete AN v1 (method, systematic
subsections, core results/comparison — no exhaustive diagnostic dumps) with
expected/Asimov numbers; 4b→10%; 4c→full; Phase 5 polishes + typesets.
Phase-stamped, never overwritten; the executor both writes and typesets.
**Completeness test:** a physicist who never saw the analysis reproduces every
number from the AN alone. **Change Log** (`# Change Log {-}`, after the TOC):
reverse-chronological, ≤1 page.

### Required sections
1. **Introduction** — motivation, observable, prior measurements (cite ≥2 from
   other experiments where they exist).
2. **Data samples** — experiment, √s, **luminosity (mandatory; estimate L =
   N_had/σ_had if unpublished)**, MC generators, event counts (data table + MC
   table: generator, σ, N_gen, k-factor).
3. **Event selection** — every cut with motivation, distribution plot, per-cut +
   cumulative efficiency.
4. **Corrections/unfolding** (measurements) — procedure with displayed key
   equations (`$$…$$`: correction formula, likelihood/chi2, systematic
   propagation); closure/stress tests (what/expected/observed chi²/ndf,p/figure).
5. **Systematic uncertainties** — one prose subsection per source: origin;
   evaluation (what varies, formula/reference, cited size — "±50%" is Category A
   unless measured); numerical impact (table row per source + a bin-by-bin
   figure for dominant sources only; flat shifts on a shape measurement are
   Category A). Plus an error-budget narrative (which dominate, stat- vs syst-limited).
6. **Results** — full uncertainties, per-bin tables, summary figures.
7. **Comparison to prior results / theory** — quantitative (chi²/ndf or pull with
   full covariance; overlay published points). "Consistent with published"
   without a number is Category B.
8. **Conclusions**, **known limitations** (3–5: what, attempted?, impact, fix),
   **appendices** (per-bin systematic tables, covariance, reproduction contract:
   exact `pixi` command sequence).

### Statistical standards (Category A if violated)
- **Full covariance** when one exists: $\chi^2=(d-m)^T C^{-1}(d-m)$. Diagonal-only
  never primary.
- **GoF for the primary result:** chi²/ndf < 3 (p > 0.01); p < 0.01 is Category A
  unless the source is identified, shown not to bias, and an acceptable-GoF
  config shown as a cross-check. Picking best-precision while ignoring GoF is forbidden.
- **Closure passes at p > 0.05** (ad-hoc "chi²/ndf < 5" is invalid); p < 0.01 =
  failed, needs 3+ remediation attempts.

## LaTeX compilation
markdown → **pandoc** (≥3.0) `.tex` → **`postprocess_tex.py`** (deterministic
fixes) → **tectonic** PDF; the `build-pdf` pixi task runs this. Never use an LLM
for LaTeX conversion. **Pitfall:** never `$\pm$`/`$<$`/`$>$`/`$-$`/`$\sim$` as
standalone math — use Unicode `± < > − ~` (`$…$` only for real expressions like
`$M_Z$`). Keep table columns narrow, split >6-col tables, 2–3 sig figs. After
compiling, `grep "Overfull.*hbox" *.log` — any overfull hbox on a figure/table
is Category A; check no `??`/`[?]`, figures not clipped, all `@fig:`/`@tbl:`/
`@eq:` resolve.

## Plotting (Category A unless noted — lint-enforced, these are gospel)
Base `mh.style.use("CMS")`; **`figsize=(10,10)` LOCKED** (ratio plots `(10,10)`,
`height_ratios=[3,1]`; any custom figsize is Category A). Save **both** PDF and
PNG with `bbox_inches="tight", dpi=200, transparent=True`; `plt.close(fig)`
after. Never `tight_layout()`/`constrained_layout`. `np.random.seed(42)` if random.
- **Experiment label on every independent axes** via `mh.label.exp_label(exp=…,
  data=True, llabel="Open Data"|"Open Simulation", rlabel=r"$\sqrt{s}=X$", loc=0)`
  — main panel only on ratio plots, never the ratio panel. Labeling as just
  "<EXP>" (implying an official result) or `data=False` with `llabel` is Category A.
- **No `ax.set_title()`**, no numeric `fontsize=` (relative `'x-small'` OK), no
  raw `ax.text()`/`ax.annotate()` on data plots (use `mh.label.add_text`).
  Human-readable labels — no bare `_` outside `$…$`.
- **Histograms:** `mh.histplot()` (never `ax.step/bar/fill_between`). **Derived
  quantities (normalized dists, ratios, efficiencies, correction/systematic
  shifts) MUST pass explicit `yerr=`** — else mplhep applies sqrt(bin-content)
  (e.g. 570% error bars). Filled via `h.fill(values)` → auto-errors OK; assigned
  via `h.view()[:]=…` → MUST pass `yerr=`.
- **Ratio plots:** `sharex=True` AND `fig.subplots_adjust(hspace=0)` (missing
  either is Category A); hide main x-ticks; remove the spurious "Axis 0" text.
- Log y when spanning >2 orders of magnitude; tight axis limits; suppress the
  "1e6" offset notation.
**yerr formulas:** normalized `(1/N)dN/dx` → `sqrt(n)/(N·dx)`; ratio `A/B` →
`R·sqrt((σ_A/A)²+(σ_B/B)²)`; efficiency `k/n` → Clopper-Pearson.
**Conceptual diagrams** (flow/region definitions): no `exp_label`, `figsize`
free, matplotlib patches/arrows/`ax.text` allowed; produced in Phase 5.
**Delegation:** a plotting subagent gets this section + data + plot kind + labels
+ exp_label params + output path; it makes no physics decisions.
