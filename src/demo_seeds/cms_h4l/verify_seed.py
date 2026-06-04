#!/usr/bin/env python
"""Demo determinism guard for the cms_h4l seed.

The cms_h4l demo SHIPS pre-baked Phase 1 + Phase 2 artifacts (strategy,
schema summary, per-sample MC normalization weights) instead of re-deriving
them live every run. That pre-baking is only honest if the shipped numbers
still match what the data ACTUALLY contains. This script is the guard: it
re-opens every ROOT file in ``data/`` with uproot and recomputes, from
scratch, the two things the seed claims are fixed by (prompt + dataset):

  (a) the ``h4lTree`` branch set per sample, and
  (b) ``N_gen = sum(Metadata.nEvents)`` per MC sample and the flat
      per-sample normalization weight ``w = sigma[pb] * 1000 * L[fb^-1] / N_gen``
      (L = 10 fb^-1; sigma from the seeded explore_results.json, which copies
      the cross sections from prompt.md).

It then asserts these recomputed values match what the seeded
``schema_summary.json`` and ``explore_results.json`` recorded. If anything
drifts (a re-ntuplized dataset, a changed cross section, a renamed branch),
the guard prints FAIL for that sample and exits nonzero, so the demo never
proceeds on a stale seed.

Run from the analysis root (where ``scaffold --demo`` places the seed):

    pixi run py verify_seed.py

Dependency-light by design: uproot, numpy, json only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import uproot

# --- Constants fixed by the analysis prompt --------------------------------
# Integrated luminosity (data_secret_10fb.root => 10 fb^-1; see prompt.md).
L_FB = 10.0
# Cross sections are quoted in pb in prompt.md; 1 pb = 1000 fb.
PB_TO_FB = 1000.0
# Relative tolerance for the floating-point weight comparison.
RTOL = 1e-9

# Paths are resolved relative to the analysis root (the CWD when the demo
# runs this guard via `pixi run py verify_seed.py`).
ROOT = Path.cwd()
DATA_DIR = ROOT / "data"
SCHEMA_JSON = ROOT / "phase2_exploration" / "outputs" / "schema_summary.json"
EXPLORE_JSON = ROOT / "phase2_exploration" / "outputs" / "explore_results.json"


def _load_json(path: Path) -> dict:
    if not path.exists():
        sys.stderr.write(f"FATAL: required seed artifact missing: {path}\n")
        sys.exit(2)
    with path.open() as fh:
        return json.load(fh)


def recompute_ngen(path: Path) -> int:
    """N_gen = sum of Metadata/nEvents over all entries (one per merged file)."""
    with uproot.open(path) as f:
        nev = f["Metadata"]["nEvents"].array(library="np")
    return int(np.sum(nev))


def recompute_branches(path: Path) -> set[str]:
    """The full h4lTree branch name set, recomputed from the ROOT file."""
    with uproot.open(path) as f:
        return set(f["h4lTree"].keys())


def main() -> int:
    schema = _load_json(SCHEMA_JSON)
    explore = _load_json(EXPLORE_JSON)
    weights = explore["weights"]  # per-MC-sample: xsec_pb, N_gen, weight, group

    if not DATA_DIR.is_dir():
        sys.stderr.write(f"FATAL: data directory not found: {DATA_DIR}\n")
        return 2

    # Sanity: the seeded luminosity must be the one this guard assumes.
    l_seed = explore.get("L_fb")
    if l_seed is not None and abs(float(l_seed) - L_FB) > 1e-12:
        sys.stderr.write(
            f"FATAL: seeded L_fb={l_seed} != guard L_FB={L_FB}; refusing to verify.\n"
        )
        return 2

    rows: list[tuple[str, str, str]] = []
    n_fail = 0

    # Every ROOT file in data/ must have a schema entry; check branch sets for all,
    # and the N_gen/weight chain for the MC samples recorded in explore_results.
    root_files = sorted(
        p.name for p in DATA_DIR.glob("*.root") if not p.name.startswith("._")
    )
    if not root_files:
        sys.stderr.write(f"FATAL: no ROOT files under {DATA_DIR}\n")
        return 2

    for fname in root_files:
        path = DATA_DIR / fname
        details: list[str] = []
        ok = True

        # --- (a) branch set ---
        rec_entry = schema.get(fname)
        if rec_entry is None:
            ok = False
            details.append("no schema_summary entry")
        else:
            recorded_branches = set(
                rec_entry["objects"]["h4lTree"]["branches"].keys()
            )
            got_branches = recompute_branches(path)
            if recorded_branches != got_branches:
                ok = False
                missing = recorded_branches - got_branches
                extra = got_branches - recorded_branches
                details.append(
                    f"branch mismatch (n_rec={len(recorded_branches)}, "
                    f"n_data={len(got_branches)}, missing={sorted(missing)[:3]}, "
                    f"extra={sorted(extra)[:3]})"
                )
            else:
                details.append(f"branches OK ({len(got_branches)})")

        # --- (b) N_gen + weight, MC samples only (data has no weight entry) ---
        wrec = weights.get(fname)
        if wrec is not None:
            xsec_pb = float(wrec["xsec_pb"])
            ngen_rec = int(wrec["N_gen"])
            w_rec = float(wrec["weight"])

            ngen_got = recompute_ngen(path)
            if ngen_got != ngen_rec:
                ok = False
                details.append(f"N_gen mismatch (rec={ngen_rec}, data={ngen_got})")
            else:
                details.append(f"N_gen OK ({ngen_got})")

            w_got = xsec_pb * PB_TO_FB * L_FB / ngen_got
            if not np.isclose(w_got, w_rec, rtol=RTOL, atol=0.0):
                ok = False
                details.append(f"weight mismatch (rec={w_rec:.6e}, recomp={w_got:.6e})")
            else:
                details.append(f"weight OK ({w_got:.6e})")
        elif fname.startswith("data_"):
            details.append("data sample (no MC weight) — branch check only")

        if not ok:
            n_fail += 1
        rows.append((fname, "PASS" if ok else "FAIL", "; ".join(details)))

    # --- Report (plain print: the guard must run with zero extra deps) ---
    print("=" * 78)
    print("cms_h4l SEED DETERMINISM GUARD")
    print(f"  data dir : {DATA_DIR}")
    print(f"  schema   : {SCHEMA_JSON}")
    print(f"  explore  : {EXPLORE_JSON}")
    print(f"  L        : {L_FB} fb^-1   (w = sigma[pb] * {PB_TO_FB:.0f} * L / N_gen)")
    print("=" * 78)
    name_w = max(len(r[0]) for r in rows)
    for fname, status, detail in rows:
        print(f"  {status:4s}  {fname:<{name_w}}  {detail}")
    print("=" * 78)

    n_total = len(rows)
    if n_fail:
        print(f"RESULT: FAIL — {n_fail}/{n_total} samples drifted from the seed.")
        print("The shipped Phase 1/2 artifacts no longer match the data; do NOT")
        print("proceed on this seed. Re-derive the schema/weights or fix the dataset.")
        return 1

    print(f"RESULT: PASS — all {n_total} samples match the seeded schema + weights.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
