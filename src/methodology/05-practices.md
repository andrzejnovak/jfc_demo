## 11. Coding & Version Control
- **`__file__`-relative output paths** (`HERE = Path(__file__).resolve().parent`)
  so output is CWD-independent. **Columnar** — arrays + masks, no event loops.
- **Testing:** focus on structural bugs (wrong branch/weight, inverted cut) —
  they re-run everything and produce plausible wrong numbers. Per-phase smoke
  test (~100 events) + integration test (files exist, no NaN). Check
  variable→quantity mapping, cut complements, monotonic cutflow, systematic
  directions. Bit-identical parallel outputs across independent inputs = a
  fork/threading bug.
- **Debug outputs** `debug_`-prefixed or in `scratch/`, never in the `all` chain;
  but preserve diagnostics that informed a decision. `outputs/` = production;
  `outputs/figures/` = AN figures; `logs/` = session/experiment-log narrative.
- Every script is a pixi task; `all` runs the chain. No bare `print` (logging+rich).
  Conventional commits `<type>(phase): …`. KISS/YAGNI — scripts, not frameworks.

## 4. Blinding / Staged Validation
"Blinding" = not examining the SR discriminant in data (searches) or not
computing the final quantity on real data (measurements).

| Stage | Data access | Gate |
|---|---|---|
| Phases 1–3 | MC only | — |
| Phase 4a | Asimov/MC pseudo-data | orchestrator light check (no reviewer) |
| Phase 4b | 10% subsample (fixed seed) | human gate (no reviewer) |
| Phase 4c | full data | orchestrator checklist (no reviewer) |

**Asimov data** = nominal-model pseudo-data at exact expected bin contents (no
fluctuations). **4b:** 10% with a fixed seed, MC normalized to 10% L, full
chain, compare to 4a expected; fix problems before seeing more. **4c:** only
after human APPROVE; post-unblinding changes documented and justified.

## 12. Downscoping
Downscope only as a last resort — after attempting the stronger method or
documenting infeasibility (a concrete approach tried, a specific documented
failure, or compute beyond a few minutes). A limitation with no attempted fix is
Category B; a silent downscope of a binding [D] commitment is Category A.
