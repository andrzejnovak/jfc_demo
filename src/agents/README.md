# Agent Definitions

Four roles. The note writer + typesetter are merged into the executor; the
review panel is collapsed to one critical reviewer that also makes the
PASS / ITERATE call (no arbiter, plot validator, or BibTeX reviewer).

| Role | File | Does |
|------|------|------|
| Executor | `executor.md` | Plan, code, figures, artifact, AND the AN write + typeset (4a+) |
| Fixer | `fixer.md` | Targeted fixes for findings / regression tickets (replaces executor on ITERATE) |
| Critical reviewer | `critical_reviewer.md` | The single reviewer — Phases 1, 3 only |
| Investigator | `investigator.md` | Regression diagnosis + scoped fix ticket |

The executor is the producing step for every phase (Ph4a+ also writes + compiles
the AN PDF). The fixer replaces it on ITERATE.

## Gates by phase (lean scope)

| | Ph1 | Ph2 | Ph3 | Ph4a | Ph4b | Ph4c | Ph5 |
|---|---|---|---|---|---|---|---|
| Critical reviewer | x | | x | | | | |
| Self-review | | x | | | | | |
| Human gate | | | | | x | | |
| Orchestrator checklist | x | x | x | x | x | x | x |

The reviewer runs at **Phases 1 and 3 only**; 4a gets a light orchestrator
check (fit converges, recovers injected inputs); 4b is the human gate; 4c/5 rely
on the orchestrator's regression + completeness checklist. Mechanical
figure/citation/render checks are the executor's self-lint + the mandatory PDF
compile (4a, 4b). Only Category A blocks; on ITERATE the fixer clears it and the
orchestrator re-reviews. Context assembly per §3a.4.

## Demo mode (seeded analyses)

When `.analysis_config` sets `demo_seed=<name>`, Phase 4a **additionally** runs
a small parallel mini-panel — `critical_reviewer` + `bibtex_validator` +
`plot_validator`, run concurrently, with the **orchestrator adjudicating** (no
arbiter). This is a showcase moment: the bots fan out and catch real, seeded
issues. The two extra roles (`bibtex_validator.md`, `plot_validator.md`) exist
**only** for this demo panel. The base gate matrix above is otherwise
**unchanged** — outside demo mode there is the single `critical_reviewer` at
Phases 1 and 3 and no panels anywhere.
