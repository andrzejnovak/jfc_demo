# LLM-Driven HEP Analysis: Methodology Specification

This spec defines *what* each phase must produce, not *how*. The agent selects
tools, writes code, and makes physics judgments within these constraints. Goal:
a correct result fast — one strategy, optimized, to a result.

## 1. Principles
- **Correct and publication-ready**, but lean — cover what's needed, skip
  exhaustive diagnostics and documentation.
- **Conventions over encoded physics** — operational knowledge lives in
  `conventions/`, consulted at Phases 1, 4a, 5.

## 2. Inputs
**2.1 Physics prompt.** Natural-language goal (target, dataset, final state,
energy). Need not specify methodology.
**2.2 Experiment context (RAG).** Query the corpus (SciTreeRAG via MCP) for
detector/object/MC definitions, performance numbers, prior analyses; cite all
retrieved info. No RAG → proceed on `docs/` + training knowledge, mark
uncorroborated claims "unverified". Data is ground truth — on discrepancy, trust
data. Log failed retrievals to `retrieval_log.md`.
**2.3 Numeric constants — never from training data.** Every number entering the
analysis (masses, widths, BRs, couplings, cross-sections, luminosities, world
averages, SM predictions, validation targets) must cite a source: RAG (paper +
table/eq), web fetch (PDG/HEPData), or a published paper. **At review, any
uncited numeric constant is Category A.** A curated, pre-sourced table may be
provided at `conventions/cited_constants.md`; executors cite its bibkeys instead
of re-deriving from memory (citation validation still applies).
**2.4 Self-consistency for derived constants.** Substitute PDG inputs and
confirm the formula reproduces the known result within ~1%; a larger gap signals
a wrong input or convention mismatch.

## 7. Tools (use these, not alternatives)
ROOT I/O → `uproot`; arrays → `awkward`/`numpy` (not pandas for event data);
histograms → `hist`/`boost-histogram`; stats → `pyhf`/`cabinetry` (binned),
`zfit` (unbinned) — not RooFit/custom; MVA → `xgboost`/`scikit-learn`;
plotting → `matplotlib`+`mplhep`.
**Paradigms.** Prototype on a ~1000-event slice, then scale. Columnar — arrays +
boolean masks, no event loops. Pin random seeds; record versions. MC norm:
weight = σ·L / Σw_gen; when MC mismatches data after proper scaling, add a
control region with a floating normalization — do not hand-scale MC. Systematic
naming `{source}Up`/`{source}Down`. No bin with < ~5 expected events.
**Scale-out.** <2 min local; 2–15 min multicore (`ProcessPoolExecutor`); >15 min
SLURM. With process pools + threaded libs set `forkserver`/`spawn` (default
`fork` can return cached parent data); N parallel outputs must not be bit-identical.
