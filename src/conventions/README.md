# Physics Conventions

Accumulated domain knowledge for specific analysis techniques. These are **not** part of the methodology spec — the spec describes *process* (phases, reviews, gates); conventions encode *which* systematic sources and validation checks are standard for a given technique.

Conventions are consulted, not blindly followed. If one doesn't apply, document why and proceed; if one is missing, use literature/RAG and add what you learned for next time.

## Structure
One file per technique, each covering: when to use it, standard configuration, required systematic sources (with rationale), required validation checks, and known pitfalls. Consulted at **Phase 1** (plan the systematic program) and **Phase 4a** (completeness check). Current files: `extraction.md`, `search.md`, `unfolding.md`. `TEMPLATE.md` is a skeleton for new files — agents ignore it.

## Maintenance
Living, empirically-grounded documents (from real analysis experience + published references), updated by agents after an analysis with human review before merging.

## LaTeX preamble governance
`preamble.tex` is the shared standard preamble — **not modified during an analysis**. If an analysis needs extra packages (tikz, siunitx): put them in `phase5_documentation/outputs/analysis_preamble.tex`, document the rationale in the experiment log, include both via `--include-in-header=...preamble.tex --include-in-header=outputs/analysis_preamble.tex`, and verify no conflict at the first PDF compile. If a custom package proves generally useful, propose adding it to the standard preamble.
