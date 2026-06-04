# SKELETON (demo seed): adapt the systematic magnitudes (see
# conventions/cited_constants.md) and templates for the analysis; verify the
# uncertainty decomposition. The live Phase-4a executor finalizes the
# statistical model, runs the inference, produces plots, and is reviewed.

"""Shared pyhf model builder for the Phase 4 H->ZZ*->4l mu fit.

Builds a per-channel (4mu/4e/2e2mu) combined binned-likelihood model of the
m4l spectrum from the Phase 3 persisted templates. Signal = sum of 5 H
production modes scaled by a single POI mu. Backgrounds = qqZZ, ggZZ, DY,
ttbar. Systematics implemented as pyhf modifiers with magnitudes sourced from
the literature (see references.bib / INFERENCE_EXPECTED.md).

This module is imported by run_inference.py and make_p4a_plots.py so the model
definition lives in exactly one place.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pyhf

log = logging.getLogger(__name__)

# --- Paths -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "phase3_selection/outputs/fit_inputs/templates_V_baseline.npz"

# --- Sample groups ---------------------------------------------------------
CHANNELS = ["4mu", "4e", "2e2mu"]
BKG_GROUPS = ["qqZZ", "ggZZ", "DY", "ttbar"]

# --- Sourced systematic magnitudes (fractional) ----------------------------
# Every number here is sourced; see references.bib and INFERENCE_EXPECTED.md.
SYST = {
    # CMS 2017 integrated-luminosity uncertainty (CMS-PAS-LUM-17-004).
    # Applied as one correlated normsys to ALL MC samples.
    "lumi": 0.023,
    # qqZZ NLO QCD scale + PDF normalization uncertainty
    # (CMS 1706.09936 / MCFM, ~8-10%); use 10%.
    "qqZZ": 0.10,
    # ggZZ NNLO K-factor uncertainty (Caola/Melnikov; Grazzini et al.), ~10%.
    "ggZZ": 0.10,
    # Reducible DY+ttbar (Z+X) normalization uncertainty. CMS data-driven Z+X
    # spans 31-43% depending on final state (1706.09936); take 40%. Covers the
    # absence of a data-driven fake estimate here (DY/ttbar MC-only, [D1]) plus
    # the sparse surviving MC statistics [L1].
    "DY": 0.40,
    "ttbar": 0.40,
    # Signal theory normalization. ggF (~90% of signal) dominates: LHCHWG YR4
    # N3LO QCD scale +4.6/-6.7%, PDF+alpha_s +/-3.9% (arXiv:2402.09955).
    # Combine scale and PDF in quadrature -> hi=+6.0%, lo=-7.7%. VBF/VH are
    # subdominant (few %) and folded into this single ggF-dominated signal NP.
    "sig_theory_hi": 0.060,
    "sig_theory_lo": -0.077,
}

# Reference values (PDG 2024) -- used by mass_fit.py / plots, sourced.
M_Z_PDG = 91.1876  # GeV, PDG 2024 Z-boson listings
M_H_PDG = 125.20  # GeV, PDG 2024 gauge & Higgs boson summary
M_H_REF = 125.26  # GeV, arXiv:1706.09936 (reference analysis)
MU_REF = 1.05  # arXiv:1706.09936


def load_templates(path: Path = TEMPLATES) -> dict:
    """Load the npz templates into a plain dict of numpy arrays."""
    npz = np.load(path)
    return {k: npz[k] for k in npz.files}


def signal_theory_normsys(nbins: int) -> dict:
    """Asymmetric signal-theory normsys data (per-bin hi/lo factors)."""
    hi = 1.0 + SYST["sig_theory_hi"]
    lo = 1.0 + SYST["sig_theory_lo"]
    return {"hi": hi, "lo": lo}


def build_model(systematics: bool = True, templates: dict | None = None) -> pyhf.Model:
    """Build the combined per-channel pyhf model.

    Parameters
    ----------
    systematics : bool
        If True, include the full systematic NP set (lumi, per-background
        normalizations, signal theory) on top of the per-bin staterror.
        If False, build the stat-only model (staterror only) -- used as a
        cross-check / for the Phase-3-equivalent sensitivity.
    templates : dict, optional
        Pre-loaded template dict; loaded from disk if None.
    """
    tpl = templates if templates is not None else load_templates()

    lumi_hi = 1.0 + SYST["lumi"]
    lumi_lo = 1.0 - SYST["lumi"]
    sig_ts = signal_theory_normsys(0)

    spec_channels = []
    for c in CHANNELS:
        samples = []

        # --- Signal: summed 5 production modes, scaled by mu ---
        sig = np.clip(tpl[f"signal__{c}__val"].astype(float), 1e-6, None)
        sig_err = np.sqrt(tpl[f"signal__{c}__sumw2"].astype(float))
        sig_mods = [
            {"name": "mu", "type": "normfactor", "data": None},
            {"name": f"stat_signal_{c}", "type": "staterror", "data": sig_err.tolist()},
        ]
        if systematics:
            sig_mods += [
                {"name": "lumi", "type": "normsys",
                 "data": {"hi": lumi_hi, "lo": lumi_lo}},
                {"name": "sig_theory", "type": "normsys",
                 "data": {"hi": sig_ts["hi"], "lo": sig_ts["lo"]}},
            ]
        samples.append({"name": "signal", "data": sig.tolist(), "modifiers": sig_mods})

        # --- Backgrounds ---
        for g in BKG_GROUPS:
            val = np.clip(tpl[f"{g}__{c}__val"].astype(float), 1e-6, None)
            err = np.sqrt(tpl[f"{g}__{c}__sumw2"].astype(float))
            mods = [
                {"name": f"stat_{g}_{c}", "type": "staterror", "data": err.tolist()},
            ]
            if systematics:
                frac = SYST[g]
                mods += [
                    {"name": "lumi", "type": "normsys",
                     "data": {"hi": lumi_hi, "lo": lumi_lo}},
                    {"name": f"norm_{g}", "type": "normsys",
                     "data": {"hi": 1.0 + frac, "lo": 1.0 - frac}},
                ]
            samples.append({"name": g, "data": val.tolist(), "modifiers": mods})

        spec_channels.append({"name": c, "samples": samples})

    spec = {"channels": spec_channels}
    return pyhf.Model(spec, poi_name="mu")


def asimov_data(model: pyhf.Model, mu: float = 1.0) -> np.ndarray:
    """Asimov dataset at signal strength `mu`, all NPs at nominal."""
    pars = model.config.suggested_init()
    pars[model.config.poi_index] = mu
    return model.expected_data(pars)
