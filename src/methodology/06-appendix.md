# Appendix

Reference: orchestration automation, phase graph, RAG, agent roles. Phase
definitions are in `02-phases.md` (§3, §3a); review in `03-review.md`.

## Automation (pseudocode)
One executor call per phase (stats + AN + typeset in one role); one review
function spawning a single critical reviewer (no panel).

```
for phase in [1, 2, 3, 4a, 4b, 4c, 5]:
    run_executor(phase)                 # plan → code → artifact (+ AN+PDF from 4a)
    if phase in (1, 3):                 # reviewer; 4b→human gate; 4a/4c/5→checklist
        loop: run_critical_reviewer(phase); if not PASS: run_fixer(phase)
    commit(phase)
    if phase == 4b: present_PDF_to_human(); wait_for_decision()
```

## Phase graph
```
Prompt → Ph1 Strategy → Ph2 Exploration → Ph3 Selection →
  Ph4a Expected (light check) → Ph4b 10% (HUMAN GATE) → Ph4c Full → Ph5 Docs
      ▲ RAG corpus queried throughout   └ regression re-enters at the origin phase
```
For searches 4b is a 10% SR partial unblinding; for measurements a 10%-vs-expected
check. The human gate sits between 4b and 4c.

## RAG
SciTreeRAG corpus via MCP (no per-session setup); cite sources (paper + section);
failed retrievals → `retrieval_log.md`. Tools: `search_lep_corpus`, `get_paper`,
`list_corpus_papers`, `compare_measurements`. No RAG → `docs/` + training
knowledge, marking uncorroborated claims unverified.

## Agent roles
Full definitions in `../agents/*.md`. All subagents run `model:"opus"` and read
with the Read tool.

| Role | Writes |
|------|--------|
| Executor | `outputs/` artifacts, `src/` code, figures, `ANALYSIS_NOTE_{phase}_v{N}` (4a+), `logs/` |
| Fixer | updated artifact + code (replaces executor on ITERATE) |
| Critical reviewer | `review/critical/` (PASS/ITERATE; only Category A blocks) |
| Investigator | `REGRESSION_TICKET.md` (regression diagnosis only) |

PDF compilation is mandatory before the 4a light check and the 4b human gate.
Mechanical figure/BibTeX lint is the executor's self-lint, not a reviewer.
