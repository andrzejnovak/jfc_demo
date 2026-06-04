# SKELETON (demo seed): adapt the systematic magnitudes (see
# conventions/cited_constants.md) and templates for the analysis; verify the
# uncertainty decomposition. The live Phase-4a executor finalizes the
# statistical model, runs the inference, produces plots, and is reviewed.

"""Standalone, reproducible Higgs-mass (m_H) extraction for H->ZZ*->4l.

Two stages:
  1. RESOLUTION MODEL. Fit a double-sided Crystal Ball (DSCB) lineshape to the
     summed signal MC m4l distribution (events parquet, group=='signal') by
     unbinned maximum likelihood (iminuit). This fixes the peak shape
     (resolution sigma, the two power-law tail parameters). The DSCB is the
     standard CMS H->4l signal lineshape: a Gaussian core with power-law tails
     on both sides modelling final-state radiation (low side) and resolution
     outliers. (Source: CMS H->4l mass measurements, e.g. arXiv:1910.09607.)

  2. EXPECTED m_H UNCERTAINTY. Build an Asimov signal-region dataset (signal
     DSCB at the MC peak + a smooth exponential continuum background scaled to
     the expected qqZZ+ggZZ+reducible yield), fix the DSCB shape (sigma, alphas,
     ns) from stage 1, and float the peak position m_peak, the signal yield and
     the background. The Hesse error on m_peak is the EXPECTED statistical
     uncertainty on m_H at 10 fb^-1. This is the Phase-4a expected mass result;
     real data is NOT used (blinded until 4c).

Run: pixi run p4-mass
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from iminuit import Minuit
from iminuit.cost import ExtendedUnbinnedNLL, ExtendedBinnedNLL
from rich.logging import RichHandler
from scipy import integrate

import model as M

logging.basicConfig(
    level=logging.INFO, format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "phase3_selection/outputs/fit_inputs/events_V_baseline.parquet"
TEMPLATES = ROOT / "phase3_selection/outputs/fit_inputs/templates_V_baseline.npz"
RESULTS = ROOT / "phase5_documentation/outputs/results"
RESULTS.mkdir(parents=True, exist_ok=True)

# Fit window for the mass/lineshape fit (narrower than the mu-fit window,
# focused on the peak; broad enough to constrain the tails).
M_LO, M_HI = 105.0, 140.0


# --- Double-sided Crystal Ball -------------------------------------------
def dscb_unnorm(x, mu, sigma, aL, nL, aR, nR):
    """Unnormalized double-sided Crystal Ball density.

    Gaussian core for -aL < t < aR (t=(x-mu)/sigma); power-law tails outside.
    Standard parameterization (e.g. CMS H->4l). aL,aR>0; nL,nR>1.
    """
    t = (x - mu) / sigma
    out = np.empty_like(t, dtype=float)
    core = (t > -aL) & (t < aR)
    left = t <= -aL
    right = t >= aR
    out[core] = np.exp(-0.5 * t[core] ** 2)
    # Left tail
    AL = (nL / aL) ** nL * np.exp(-0.5 * aL ** 2)
    BL = nL / aL - aL
    out[left] = AL * (BL - t[left]) ** (-nL)
    # Right tail
    AR = (nR / aR) ** nR * np.exp(-0.5 * aR ** 2)
    BR = nR / aR - aR
    out[right] = AR * (BR + t[right]) ** (-nR)
    return out


def dscb_norm(mu, sigma, aL, nL, aR, nR, lo=M_LO, hi=M_HI):
    """Normalization integral of the DSCB over [lo, hi]."""
    val, _ = integrate.quad(
        lambda x: dscb_unnorm(np.array([x]), mu, sigma, aL, nL, aR, nR)[0], lo, hi,
        limit=200,
    )
    return val


def dscb_pdf(x, mu, sigma, aL, nL, aR, nR):
    return dscb_unnorm(x, mu, sigma, aL, nL, aR, nR) / dscb_norm(mu, sigma, aL, nL, aR, nR)


def load_signal_m4l():
    t = pq.read_table(EVENTS)
    d = t.to_pydict()
    group = np.asarray(d["group"])
    m4l = np.asarray(d["m4l"], dtype=float)
    w = np.asarray(d["weight"], dtype=float)
    sig = group == "signal"
    m = m4l[sig]
    wt = w[sig]
    win = (m >= M_LO) & (m <= M_HI)
    return m[win], wt[win]


def fit_resolution_model(m, w):
    """Unbinned ML fit of the DSCB to signal MC m4l. Uses a binned extended
    NLL (the 4.2e5 candidates make a fine binned fit equivalent to unbinned and
    far faster, with proper Poisson treatment of weighted bins)."""
    # Fine binned fit (0.25 GeV bins) -- weighted.
    nbins = int((M_HI - M_LO) / 0.25)
    edges = np.linspace(M_LO, M_HI, nbins + 1)
    counts, _ = np.histogram(m, bins=edges, weights=w)
    # scale to unweighted-equivalent for Poisson stats but keep shape: use
    # raw counts for the cost (shape only matters for the lineshape).
    raw, _ = np.histogram(m, bins=edges)

    def model_cdf(xe, n, mu, sigma, aL, nL, aR, nR):
        # extended binned: integral of n * pdf over each bin edge set xe
        centers = 0.5 * (xe[:-1] + xe[1:])
        widths = np.diff(xe)
        norm = dscb_norm(mu, sigma, aL, nL, aR, nR)
        dens = dscb_unnorm(centers, mu, sigma, aL, nL, aR, nR) / norm
        cum = np.concatenate([[0.0], np.cumsum(n * dens * widths)])
        return cum

    cost = ExtendedBinnedNLL(raw, edges, model_cdf)
    mtot = float(raw.sum())
    mguess = float(np.average(m, weights=w))
    mi = Minuit(cost, n=mtot, mu=mguess, sigma=1.5, aL=1.3, nL=3.0, aR=1.6, nR=4.0)
    mi.limits["n"] = (0, None)
    mi.limits["mu"] = (M_LO, M_HI)
    mi.limits["sigma"] = (0.3, 6.0)
    mi.limits["aL"] = (0.3, 5.0)
    mi.limits["nL"] = (1.01, 50.0)
    mi.limits["aR"] = (0.3, 5.0)
    mi.limits["nR"] = (1.01, 50.0)
    mi.migrad()
    mi.hesse()
    return mi, edges, raw


def expected_mass_uncertainty(shape, templates):
    """Expected statistical uncertainty on m_H from an Asimov S+B fit.

    Signal = DSCB with shape fixed from MC, peak floated. Background = smooth
    exponential scaled to the expected continuum (qqZZ+ggZZ+DY+ttbar) in the
    mass window. Asimov data built at the MC peak and SM signal yield. The
    Hesse error on the floated peak is the expected sigma(m_H).
    """
    mu0, sigma, aL, nL, aR, nR = shape

    # Expected yields in the mass window from the binned templates.
    edges_t = templates["edges"]
    centers_t = 0.5 * (edges_t[:-1] + edges_t[1:])
    win_t = (centers_t >= M_LO) & (centers_t <= M_HI)
    s_yield = float(sum(templates[f"signal__{c}__val"][win_t].sum() for c in M.CHANNELS))
    b_yield = float(sum(templates[f"{g}__{c}__val"][win_t].sum()
                        for g in M.BKG_GROUPS for c in M.CHANNELS))
    log.info("Mass-window expected yields: S=%.2f B=%.2f", s_yield, b_yield)

    # Build Asimov binned dataset (0.5 GeV bins) of S(DSCB)+B(exp).
    nb = int((M_HI - M_LO) / 0.5)
    edges = np.linspace(M_LO, M_HI, nb + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)

    sig_dens = dscb_unnorm(centers, mu0, sigma, aL, nL, aR, nR)
    sig_dens /= (sig_dens * widths).sum()
    # Background: gentle exponential (falling), shape only; tau from qqZZ slope.
    tau = 0.02  # 1/GeV, mild slope; background ~flat under the peak
    bkg_dens = np.exp(-tau * (centers - M_LO))
    bkg_dens /= (bkg_dens * widths).sum()

    asimov = s_yield * sig_dens * widths + b_yield * bkg_dens * widths

    def sb_model(xe, s, mpeak, b):
        c = 0.5 * (xe[:-1] + xe[1:])
        wdt = np.diff(xe)
        sd = dscb_unnorm(c, mpeak, sigma, aL, nL, aR, nR)
        sd = sd / (sd * wdt).sum()
        bd = np.exp(-tau * (c - M_LO))
        bd = bd / (bd * wdt).sum()
        dens = s * sd * wdt + b * bd * wdt
        return np.concatenate([[0.0], np.cumsum(dens)])

    cost = ExtendedBinnedNLL(asimov, edges, sb_model)
    mi = Minuit(cost, s=s_yield, mpeak=mu0, b=b_yield)
    mi.limits["s"] = (0, None)
    mi.limits["b"] = (0, None)
    mi.limits["mpeak"] = (M_LO, M_HI)
    mi.migrad()
    mi.hesse()
    sigma_mH = float(mi.errors["mpeak"])
    return sigma_mH, mi, edges, asimov, (s_yield, b_yield, tau)


def main():
    log.info("=== Phase 4a expected m_H extraction (signal MC + Asimov) ===")
    m, w = load_signal_m4l()
    log.info("Signal MC candidates in [%.0f,%.0f]: %d (weighted %.2f)",
             M_LO, M_HI, len(m), w.sum())

    mi, edges_fit, raw = fit_resolution_model(m, w)
    p = mi.values
    shape = (p["mu"], p["sigma"], p["aL"], p["nL"], p["aR"], p["nR"])
    log.info("DSCB fit: peak=%.3f GeV sigma=%.3f GeV aL=%.2f nL=%.2f aR=%.2f nR=%.2f valid=%s",
             p["mu"], p["sigma"], p["aL"], p["nL"], p["aR"], p["nR"], mi.valid)
    # Closure: MC-truth peak (weighted mode region) vs fitted peak.
    fwhm = 2.355 * p["sigma"]

    tpl = M.load_templates()
    sigma_mH, mi2, edges_a, asimov, bkg_pars = expected_mass_uncertainty(shape, tpl)
    log.info("Expected sigma(m_H) (stat, Asimov) = %.3f GeV", sigma_mH)
    log.info("Asimov S+B fit: peak=%.3f (fixed-shape) s=%.2f b=%.2f valid=%s",
             mi2.values["mpeak"], mi2.values["s"], mi2.values["b"], mi2.valid)

    # Lepton-momentum-scale systematic on m_H (sourced): muon 0.04%, electron
    # 0.3% per-lepton scale -> propagate to m4l. Conservative per-mode shift on
    # the peak: dm_H/m_H ~ lepton-scale (4 leptons, correlated). Take the
    # electron-dominated 0.1% as the m4l-level scale uncertainty (CMS H->4l
    # mass papers: combined lepton-scale impact ~0.1% on m4l).
    lep_scale_frac = 0.001  # 0.1% on m4l
    syst_mH_lepscale = lep_scale_frac * p["mu"]
    log.info("Lepton-scale systematic on m_H = %.3f GeV (%.2f%%)",
             syst_mH_lepscale, 100 * lep_scale_frac)

    total_mH_unc = float(np.hypot(sigma_mH, syst_mH_lepscale))

    out = {
        "scope": "EXPECTED (signal MC lineshape + Asimov S+B; real data blinded)",
        "lineshape": "double-sided Crystal Ball (DSCB)",
        "lineshape_source": "CMS H->4l mass measurements (arXiv:1910.09607)",
        "fit_window_GeV": [M_LO, M_HI],
        "dscb_fit": {
            "peak_GeV": float(p["mu"]),
            "sigma_GeV": float(p["sigma"]),
            "fwhm_GeV": float(fwhm),
            "alpha_L": float(p["aL"]), "n_L": float(p["nL"]),
            "alpha_R": float(p["aR"]), "n_R": float(p["nR"]),
            "valid": bool(mi.valid),
        },
        "expected_mH": {
            "peak_GeV": float(mi2.values["mpeak"]),
            "sigma_mH_stat_GeV": float(sigma_mH),
            "sigma_mH_syst_lepscale_GeV": float(syst_mH_lepscale),
            "sigma_mH_total_GeV": total_mH_unc,
            "method": "Asimov S+B fit, DSCB shape fixed from MC, peak floated, Hesse error",
        },
        "lepton_scale_frac_on_m4l": lep_scale_frac,
        "reference_mH_GeV": M.M_H_REF,
        "pdg_mH_GeV": M.M_H_PDG,
    }
    with open(RESULTS / "mass_expected.json", "w") as f:
        json.dump(out, f, indent=2)
    log.info("Wrote %s", RESULTS / "mass_expected.json")

    # Save arrays for the plotting script.
    np.savez(
        RESULTS / "mass_fit_arrays.npz",
        edges_fit=edges_fit, raw=raw,
        dscb_params=np.array([p["mu"], p["sigma"], p["aL"], p["nL"], p["aR"], p["nR"]]),
        edges_asimov=edges_a, asimov=asimov,
        asimov_params=np.array([mi2.values["s"], mi2.values["mpeak"], mi2.values["b"],
                                bkg_pars[2]]),
        window=np.array([M_LO, M_HI]),
    )
    log.info("Expected m_H = %.2f +/- %.3f (stat) +/- %.3f (lep-scale) GeV",
             mi2.values["mpeak"], sigma_mH, syst_mH_lepscale)


if __name__ == "__main__":
    main()
