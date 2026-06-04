## 6. Review Protocol

### 6.1 Classification
- **(A) Must resolve** — a genuine correctness error: a wrong result, broken
  computation, circular/tautological method, or a result contradicting a
  well-measured reference (§6.8). Only Category A blocks advancement.
- **(B)/(C) Advisory** — completeness gaps, prose, style, "could be stronger".
  Optional notes; they do NOT block.

### 6.2 Review gate
One reviewer where a gate has one — the critical reviewer
(`agents/critical_reviewer.md`); no panel, no arbiter. **Lean scope:** reviewer
at **Phases 1, 3** only; Phase 2 self-review; 4b → human gate; 4a/4c/5 → no
reviewer (orchestrator checklist; 4a additionally gets a light "fit converges +
recovers injected inputs" check). Block only on correctness, with cited evidence
(a number/file: "closure chi2/ndf = 1.3/36, p=0.24 from results/closure.json").
"Looks reasonable" clears nothing. The standing gates are the closure alarm
bands, the fit-triviality/circularity gate, and §6.8.

### 6.6 Human gate (between 4b and 4c)
The human gets a compiled PDF with 10% results + the unblinding checklist.

| Response | Action |
|---|---|
| APPROVE | proceed to 4c |
| ITERATE | fix within 4b scope, re-present |
| REGRESS(N) | non-destructive regression (§6.7) |
| PAUSE | wait |

APPROVE means methodology + 10% validation are clean, NOT the final result; the
agent never fully unblinds autonomously. Checklist: yields match the reference
~10%; data/MC acceptable; closure/stress pass; systematics cover the reference
sources; 10%/expected agree; figures interpretable; **"where I wasn't sure"
items flagged** for explicit human review.

### 6.7 Phase regression
**Triggered, not avoided.** Triggers: data/MC disagreement on observable/MVA
inputs; closure failure (p<0.05); unremediated stress-test failure; single
systematic > 80% of total; result > 3σ or > 30% from a well-measured reference
(§6.8); > 50% of bins excluded; two "independent" distributions identical;
systematic double-counting; a binding [D] silently replaced.
**Procedure:** document issue + origin → orchestrator spawns the Investigator
(→ `REGRESSION_TICKET.md`) → fixer fixes the origin (new artifact versions,
never overwrite) → re-review → re-run affected downstream. The post-regression
AN body reads as if the current approach was always the plan; the Change Log
carries the audit trail.
**Upstream cascade:** when a component improves, trace every downstream consumer
and re-run; if a result shifts > 1σ or changes a ranking, propagate further.
When in doubt, re-run — stale contradictory numbers are expensive.

### 6.8 Validation-target rule
Applies at 4a/4b/4c/5 (not Ph1–3). Any extracted parameter with **pull > 3σ from
a well-measured reference OR relative deviation > 30%** blocks advancement until
resolved with a quantitative explanation (magnitude matched, simpler causes
ruled out — a "possible causes" narrative is insufficient). 30% is a trigger for
investigation, not gospel — use physics judgment.
