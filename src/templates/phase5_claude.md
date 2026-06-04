# Phase 5: Documentation

Produce the final analysis note for a **{{analysis_type}}** analysis. Start in
plan mode, then execute. The AN exists from Phase 4c — **polish, don't rewrite**.
Artifacts: `outputs/ANALYSIS_NOTE_5_v1.{md,tex,pdf}` + machine-readable `results/`.

## Steps
1. **Figures:** aggregate phase figures into `outputs/figures/`; add any missing
   AN-specific figure; verify every `figures/*.pdf` reference resolves (a missing
   figure is Category A).
2. **Polish the AN** (from `ANALYSIS_NOTE_4c_v1.md`): every section has intro
   prose; per-systematic subsections; ≥3 labeled equations; a validation summary
   table; a resolving-power statement; a published-overlay figure with a chi2; a
   systematic-breakdown figure. Numbers quoted from `results/*.json` (>1% = Category
   A). No local filesystem paths.
3. **Typeset:** pandoc (`--standalone --number-sections --toc --filter
   pandoc-crossref --citeproc --bibliography=references.bib`, include
   `preamble.tex`) → `postprocess_tex.py` → compile (tectonic), iterate
   compile→read→fix. No `??`/`[?]`, figures render, captions ≥2 sentences.

## Markdown rules
Unicode `± < > − ~` (never standalone `$\pm$`); `![Cap](figures/x.pdf){#fig:x}`
with `@fig:x`; `[@key]` citations (`references.bib`, ≥10 keys); state the
luminosity; `# Change Log {-}`.

## Pre-finish gate
`pixi run all` reproduces the chain; PDF compiles with all figures.

## Review
**No reviewer.** Self-lint + PDF compilation cover the mechanical checks; the
orchestrator's regression + completeness checklist is the safety net (a fixer
addresses any Category A it surfaces).

> Length: **concise** by default — cover every required section and reproduce
> every number, but keep prose tight. Expand only if the prompt asks for a
> thorough/long note.
