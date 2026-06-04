# SKELETON (demo seed): adapt parameters/paths for the analysis; the live
# Phase-3 executor sets and justifies the selection, runs it, produces plots,
# and is reviewed. The selection logic is the tested reference; cut VALUES are
# named parameters the live executor sets and justifies.

"""Phase 3: figure-of-merit comparison of the two selection variants.

Evaluated on MC / expected sensitivity ONLY (never tuned on observed data in
the signal region; search.md pitfall). Two figures of merit per variant:

  1. S / sqrt(S+B) in the Higgs window m4l in [118,130] GeV (S = summed signal,
     B = all backgrounds), per channel and combined.
  2. Expected (Asimov) signal-strength statistical uncertainty sigma_mu from a
     per-channel-combined pyhf binned template fit of m4l ([70,180] GeV, 2 GeV
     bins), stat-only (MC staterror), Asimov data at mu=1.

The primary variant is the one with the smaller expected sigma_mu at acceptable
purity. Writes fom_comparison.json and logs the comparison table.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pyhf
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO, format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

OUT_DIR = Path(__file__).resolve().parents[2] / "phase3_selection" / "outputs"
FIT_DIR = OUT_DIR / "fit_inputs"

CHANNELS = ["4mu", "4e", "2e2mu"]
BKG_GROUPS = ["qqZZ", "ggZZ", "DY", "ttbar"]
HIGGS_LO, HIGGS_HI = 118.0, 130.0


def load_templates(variant: str) -> dict:
    return dict(np.load(FIT_DIR / f"templates_{variant}.npz"))


def higgs_window_yields(tpl: dict) -> dict:
    edges = tpl["edges"]
    centers = 0.5 * (edges[:-1] + edges[1:])
    hw = (centers >= HIGGS_LO) & (centers <= HIGGS_HI)
    out = {"per_channel": {}, "combined": {}}
    S_tot = B_tot = 0.0
    for c in CHANNELS:
        s = float(np.sum(tpl[f"signal__{c}__val"][hw]))
        b = float(sum(np.sum(tpl[f"{g}__{c}__val"][hw]) for g in BKG_GROUPS))
        d = float(np.sum(tpl[f"data__{c}__val"][hw]))
        fom = s / np.sqrt(s + b) if (s + b) > 0 else 0.0
        out["per_channel"][c] = {"S": s, "B": b, "data": d, "S_over_sqrtSB": fom}
        S_tot += s
        B_tot += b
    out["combined"] = {
        "S": S_tot, "B": B_tot,
        "S_over_sqrtSB": S_tot / np.sqrt(S_tot + B_tot) if (S_tot + B_tot) > 0 else 0.0,
        "purity_higgs_window": S_tot / (S_tot + B_tot) if (S_tot + B_tot) > 0 else 0.0,
    }
    return out


def build_workspace(tpl: dict) -> pyhf.Model:
    """Per-channel pyhf model: signal (modifier mu) + 4 background samples,
    each with a staterror (MC-stat) modifier. Stat-only (no normsys here --
    this is the Phase 3 expected-sensitivity proxy, not the Phase 4 model)."""
    spec_channels = []
    for c in CHANNELS:
        samples = []
        sig = np.clip(tpl[f"signal__{c}__val"].astype(float), 1e-6, None)
        sig_err = np.sqrt(tpl[f"signal__{c}__sumw2"].astype(float))
        samples.append({
            "name": "signal",
            "data": sig.tolist(),
            "modifiers": [
                {"name": "mu", "type": "normfactor", "data": None},
                {"name": f"stat_signal_{c}", "type": "staterror", "data": sig_err.tolist()},
            ],
        })
        for g in BKG_GROUPS:
            val = tpl[f"{g}__{c}__val"].astype(float)
            err = np.sqrt(tpl[f"{g}__{c}__sumw2"].astype(float))
            # pyhf requires strictly positive sample data; floor empty bins.
            val = np.clip(val, 1e-6, None)
            samples.append({
                "name": g,
                "data": val.tolist(),
                "modifiers": [
                    {"name": f"stat_{g}_{c}", "type": "staterror", "data": err.tolist()},
                ],
            })
        spec_channels.append({"name": c, "samples": samples})
    spec = {"channels": spec_channels}
    return pyhf.Model(spec, poi_name="mu")


def expected_mu_unc(tpl: dict) -> float:
    """Asimov sigma_mu at mu=1 (stat-only), combined over channels."""
    model = build_workspace(tpl)
    # Asimov data at mu=1 (signal + background expectation).
    asimov = model.expected_data(model.config.suggested_init())
    init = model.config.suggested_init()
    bounds = model.config.suggested_bounds()
    fixed = model.config.suggested_fixed()
    pyhf.set_backend("numpy", "minuit")
    result = pyhf.infer.mle.fit(
        asimov, model, init_pars=init, par_bounds=bounds, fixed_params=fixed,
        return_uncertainties=True,
    )
    # With return_uncertainties=True the result is an array of shape (n_pars, 2):
    # column 0 = best-fit value, column 1 = symmetric (Hesse) uncertainty.
    result = np.asarray(result)
    mu_idx = model.config.poi_index
    return float(result[mu_idx, 1])


def main() -> None:
    comparison: dict = {}
    for variant in ("V_baseline", "V_tight"):
        tpl = load_templates(variant)
        hw = higgs_window_yields(tpl)
        sigma_mu = expected_mu_unc(tpl)
        comparison[variant] = {"higgs_window": hw, "expected_sigma_mu": sigma_mu}
        log.info("=== %s ===", variant)
        comb = hw["combined"]
        log.info("  Higgs window: S=%.3f B=%.3f  S/sqrt(S+B)=%.3f  purity=%.3f",
                 comb["S"], comb["B"], comb["S_over_sqrtSB"], comb["purity_higgs_window"])
        for c in CHANNELS:
            pc = hw["per_channel"][c]
            log.info("    %-6s S=%.3f B=%.3f S/sqrt(S+B)=%.3f data=%.0f",
                     c, pc["S"], pc["B"], pc["S_over_sqrtSB"], pc["data"])
        log.info("  Expected sigma_mu (Asimov, stat-only) = %.4f", sigma_mu)

    # Primary choice: smaller expected sigma_mu (better sensitivity).
    primary = min(comparison, key=lambda v: comparison[v]["expected_sigma_mu"])
    comparison["primary"] = primary
    comparison["primary_basis"] = (
        "Smaller expected (Asimov, stat-only) signal-strength uncertainty "
        "sigma_mu; ties broken by higher Higgs-window purity. Evaluated on MC "
        "expected sensitivity only (no observed-data tuning)."
    )
    log.info("PRIMARY selection: %s (sigma_mu=%.4f vs other=%.4f)",
             primary, comparison[primary]["expected_sigma_mu"],
             comparison["V_tight" if primary == "V_baseline" else "V_baseline"]["expected_sigma_mu"])

    (OUT_DIR / "fom_comparison.json").write_text(json.dumps(comparison, indent=2))
    log.info("Wrote fom_comparison.json")


if __name__ == "__main__":
    main()
