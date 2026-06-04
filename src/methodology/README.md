# Methodology Specification

Lean methodology for the LLM-driven HEP analysis framework — six files. Read the
relevant one as needed; original §-numbers preserved so cross-references hold.
Goal: a correct result fast — one strategy, optimized, to a result.

| File | Covers |
|------|--------|
| `01-core.md` | Principles (§1); inputs incl. numeric-constant policy (§2); tools (§7) |
| `02-phases.md` | Phases 1–5 incl. 4a/4b/4c (§3); orchestration (§3a); artifact format (§5) |
| `03-review.md` | Review gate (§6.2), human gate (§6.6), regression (§6.7), validation target (§6.8) |
| `04-output.md` | Analysis-note spec + the plotting rules (lint-enforced) |
| `05-practices.md` | Coding (§11); blinding/staged validation (§4); downscoping (§12) |
| `06-appendix.md` | Automation, phase graph, RAG, agent roles |

**Scope reminders (baked in):** the critical reviewer runs at **Phases 1 and 3
only** and blocks only on Category-A correctness errors; Phase 2 is self-review;
4b is the human gate; 4a/4c/5 have no reviewer (orchestrator checklist — 4a gets
a light "fit converges + recovers injected inputs" check). The executor writes
*and* typesets the AN. Phases 4a/4b/4c just run the fit and confirm the baseline
holds — no further exploration.
