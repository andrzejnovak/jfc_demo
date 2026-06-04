# SKELETON (demo seed): adapt parameters/paths for the analysis; the live
# Phase-3 executor sets and justifies the selection, runs it, produces plots,
# and is reviewed. The selection logic is the tested reference; cut VALUES are
# named parameters the live executor sets and justifies.

"""Phase 3: run both selection variants over all samples + data.

For each variant:
  * compute the weighted, per-channel + combined cutflow (monotone-checked),
  * apply the best-candidate-per-event choice,
  * persist the selected events (parquet) and the binned m4l fit-input
    templates per group per channel (npz).

Outputs (phase3_selection/outputs/):
  cutflow_<variant>.json
  fit_inputs/events_<variant>.parquet
  fit_inputs/templates_<variant>.npz
  selection_yields.json   (Higgs-window yields per sample/channel, both variants)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import sys

import awkward as ak
import numpy as np
from rich.logging import RichHandler

sys.path.insert(0, str(Path(__file__).resolve().parent))
import selection as S  # noqa: E402

logging.basicConfig(
    level=logging.INFO, format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

OUT_DIR = S.ANALYSIS_ROOT / "phase3_selection" / "outputs"
FIT_DIR = OUT_DIR / "fit_inputs"

# Fit binning: [70,180] GeV, 2 GeV bins (STRATEGY Sec 4.1).
FIT_EDGES = np.arange(70.0, 180.0 + 1e-6, 2.0)
HIGGS_LO, HIGGS_HI = 118.0, 130.0  # Higgs window for yields/FoM


def weighted_cutflow(d: dict, cfg: S.SelectionConfig, w: float,
                     chan: np.ndarray) -> dict:
    """Cumulative weighted cutflow per channel + combined for one sample."""
    masks = S.cut_masks(d, cfg)
    cum = np.ones(len(d["m4l"]), dtype=bool)
    flow = {c: [] for c in S.CHANNELS}
    flow["combined"] = []
    flow["raw_combined"] = []
    for stage in cfg.stages:
        cum = cum & masks[stage]
        flow["combined"].append(float(np.sum(cum) * w))
        flow["raw_combined"].append(int(np.sum(cum)))
        for c in S.CHANNELS:
            flow[c].append(float(np.sum(cum & (chan == c)) * w))
    return flow


def main() -> None:
    FIT_DIR.mkdir(parents=True, exist_ok=True)

    weights = {f: S.sample_weight(f) for f in S.MC_FILES}
    log.info("Sample weights: %s", {k: round(v, 6) for k, v in weights.items()})

    # Pre-load every sample once (reused across variants).
    log.info("Loading samples...")
    samples = {f: S.load_sample(f) for f in S.ALL_FILES}
    channels = {f: S.channel_of(d) for f, d in samples.items()}

    all_yields: dict = {}
    for vname, cfg in S.VARIANTS.items():
        log.info("=== Variant %s ===", vname)
        cutflows: dict = {}
        # Per-sample selection + best-candidate + persistence rows.
        rows_m4l, rows_w, rows_chan, rows_sample, rows_group = [], [], [], [], []
        higgs_yields: dict = {}

        for f in S.ALL_FILES:
            d = samples[f]
            chan = channels[f]
            is_data = f == S.DATA_FILE
            w = 1.0 if is_data else weights[f]
            group = "data" if is_data else S.GROUP[f]

            cf = weighted_cutflow(d, cfg, w, chan)
            cutflows[f] = {"group": group, "weight": w, "flow": cf}

            presel = S.full_mask(d, cfg)
            best = S.best_candidate_mask(d, presel)

            # Best-candidate must be a no-op on MC (already 1 cand/event):
            if not is_data:
                n_pre = int(np.sum(presel))
                n_best = int(np.sum(best))
                if n_pre != n_best:
                    log.warning("%s: best-cand changed MC yield %d->%d (expected no-op)",
                                f, n_pre, n_best)

            sel = best
            m4l_sel = d["m4l"][sel]
            chan_sel = chan[sel]
            rows_m4l.append(m4l_sel)
            rows_w.append(np.full(len(m4l_sel), w))
            rows_chan.append(chan_sel)
            rows_sample.append(np.full(len(m4l_sel), f, dtype=object))
            rows_group.append(np.full(len(m4l_sel), group, dtype=object))

            # Higgs-window yields per channel
            hw = (m4l_sel >= HIGGS_LO) & (m4l_sel <= HIGGS_HI)
            per_chan = {}
            for c in S.CHANNELS:
                m = hw & (chan_sel == c)
                per_chan[c] = int(np.sum(m)) if is_data else float(np.sum(m) * w)
            tot = int(np.sum(hw)) if is_data else float(np.sum(hw) * w)
            higgs_yields[f] = {"group": group, "total": tot, "per_channel": per_chan,
                               "n_selected_raw": int(np.sum(sel))}
            log.info("%-22s sel_raw=%d  higgs_window=%.3f",
                     f, int(np.sum(sel)), tot)

        # Monotonicity check on combined weighted cutflow (per sample).
        for f, cfd in cutflows.items():
            comb = cfd["flow"]["combined"]
            for k in range(1, len(comb)):
                if comb[k] > comb[k - 1] + 1e-9:
                    log.error("NON-MONOTONE cutflow %s at stage %s: %.4f > %.4f",
                              f, cfg.stages[k], comb[k], comb[k - 1])

        (OUT_DIR / f"cutflow_{vname}.json").write_text(
            json.dumps({"stages": cfg.stages, "samples": cutflows}, indent=2))
        log.info("Wrote cutflow_%s.json", vname)

        # --- Persist selected events (parquet) ---
        m4l = np.concatenate(rows_m4l)
        wcol = np.concatenate(rows_w)
        ccol = np.concatenate(rows_chan).astype(str)
        scol = np.concatenate(rows_sample).astype(str)
        gcol = np.concatenate(rows_group).astype(str)
        tbl = ak.Array({"m4l": m4l, "weight": wcol, "channel": ccol,
                        "sample": scol, "group": gcol})
        ak.to_parquet(tbl, FIT_DIR / f"events_{vname}.parquet")
        log.info("Wrote events_%s.parquet (%d rows)", vname, len(m4l))

        # --- Binned m4l templates per group per channel (npz) ---
        groups = ["signal", "qqZZ", "ggZZ", "DY", "ttbar", "data"]
        tpl: dict = {"edges": FIT_EDGES}
        for g in groups:
            for c in S.CHANNELS:
                m = (gcol == g) & (ccol == c)
                vals, _ = np.histogram(m4l[m], bins=FIT_EDGES, weights=wcol[m])
                # sum of weights^2 for MC-stat (data: same as counts)
                sumw2, _ = np.histogram(m4l[m], bins=FIT_EDGES, weights=wcol[m] ** 2)
                tpl[f"{g}__{c}__val"] = vals
                tpl[f"{g}__{c}__sumw2"] = sumw2
        np.savez_compressed(FIT_DIR / f"templates_{vname}.npz", **tpl)
        log.info("Wrote templates_%s.npz", vname)

        all_yields[vname] = higgs_yields

    (OUT_DIR / "selection_yields.json").write_text(json.dumps(all_yields, indent=2))
    log.info("Wrote selection_yields.json")


if __name__ == "__main__":
    main()
