# Phase 1: Strategy

Develop the strategy for a **{{analysis_type}}** analysis. Start in plan mode,
then execute. Artifact: `outputs/STRATEGY.md`.

> **Demo seed?** If `.analysis_config` has a `demo_seed=` line, this phase's
> `STRATEGY.md` is pre-provided. Do not run it live — the orchestrator
> validates-and-adopts the seeded artifact (see root CLAUDE.md "Fast Demo Mode").

## Requirements
- Physics motivation and discriminating observable(s).
- Sample inventory (data + MC); backgrounds classified (irreducible / reducible
  / instrumental).
- **A single selection approach** (MVA-based, or document why not [D]) — no
  multi-approach exploration plan.
- **Systematic plan:** enumerate every source in the applicable convention(s)
  ({{conventions_files}}) as "Will implement" / "Not applicable because…"; each
  size tied to a citable/measured value.
- **Reference table:** 2 published analyses with their systematic programs and
  **published numerical results** (the §6.8 comparison targets).
- Technique selection (determines the downstream convention). Define [A]/[L]/[D].
- Every numeric constant cited (RAG / web / paper) — never from memory.

## Self-check
- [ ] Single approach defined; systematic plan covers every convention source.
- [ ] Reference table with published results present; all constants cited.

## Review
Single critical reviewer — PASS / ITERATE; only Category A blocks.
