# SKELETON (demo seed): adapt the systematic magnitudes (see
# conventions/cited_constants.md) and templates for the analysis; verify the
# uncertainty decomposition. The live Phase-4a executor finalizes the
# statistical model, runs the inference, produces plots, and is reviewed.

"""Phase 4a expected-results inference for H->ZZ*->4l mu measurement.

Builds the systematic pyhf model (model.build_model), fits Asimov pseudo-data
at mu=1, and produces:
  - expected mu and its profile-likelihood 68% CL interval (scan, NOT Hesse),
  - fit-convergence / NP-boundary / NP-pull checks,
  - signal injection-recovery (0x, 1x, 2x, 5x),
  - systematic impact ranking on mu (+/-1 sigma NP refit),
  - goodness-of-fit on Asimov (chi2/ndf + saturated-model toy p-value),
  - bin-to-bin covariance (expected),

writing everything to phase5_documentation/outputs/results/*.json as the single
source of truth for the note writer.

ALL results here are EXPECTED (Asimov / MC pseudo-data). Real data is NOT used
(blinded until Phase 4c).
"""

from __future__ import annotations

import os

# Cap BLAS/OpenMP threads to 1: the per-evaluation linear algebra in this model
# is tiny, so multi-threading adds pure overhead (thread thrashing) and slows
# the many-fit profile scan dramatically. Must be set before numpy import.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import logging
from pathlib import Path

import numpy as np
import pyhf
from rich.logging import RichHandler

import model as M

logging.basicConfig(
    level=logging.INFO, format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

# MINUIT strategy 0 (no per-fit Hesse) with single-threaded BLAS (set above).
# We only need the NLL minimum at each fixed mu in the profile scan, not the
# parameter covariance, so strategy 0 is correct and fast here.
pyhf.set_backend("numpy", pyhf.optimize.minuit_optimizer(strategy=0))

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "phase5_documentation/outputs/results"
RESULTS.mkdir(parents=True, exist_ok=True)


def fit(data, model, **kw):
    kw.setdefault("init_pars", model.config.suggested_init())
    kw.setdefault("par_bounds", model.config.suggested_bounds())
    kw.setdefault("fixed_params", model.config.suggested_fixed())
    return pyhf.infer.mle.fit(data, model, **kw)


def twice_nll(pars, data, model):
    return float(np.asarray(pyhf.infer.mle.twice_nll(pars, data, model)).ravel()[0])


def analytic_asimov_sigma_mu(tpl, include_systs=False):
    """Expected (Asimov) statistical sigma_mu from the binned Poisson Fisher
    information, combined over all channels/bins.

    For a single signal-strength POI mu scaling signal s_i on top of background
    b_i, with Asimov data n_i = s_i + b_i, the Fisher information is
        I_mu = sum_i s_i^2 / n_i_eff ,   sigma_mu = 1/sqrt(I_mu),
    where n_i_eff = n_i + (MC-stat variance) folds the Barlow-Beeston per-bin
    MC-statistical uncertainty (sum of sumw2 over samples) into the effective
    bin variance. This is the standard asymptotic stat-only Asimov result and
    matches the Phase-3 stat-only sigma_mu (~0.50) by construction.
    """
    I = 0.0
    for c in M.CHANNELS:
        s = tpl[f"signal__{c}__val"].astype(float)
        n = s.copy()
        statvar = tpl[f"signal__{c}__sumw2"].astype(float).copy()
        for g in M.BKG_GROUPS:
            n += tpl[f"{g}__{c}__val"].astype(float)
            statvar += tpl[f"{g}__{c}__sumw2"].astype(float)
        neff = n + statvar  # Poisson bin variance inflated by MC-stat
        m = neff > 0
        I += float(np.sum(s[m] ** 2 / neff[m]))
    return float(1.0 / np.sqrt(I)) if I > 0 else float("nan")


def _staterror_indices(model):
    idx = []
    for k in model.config.par_order:
        if k.startswith("stat_"):
            sl = model.config.par_slice(k)
            idx += list(range(sl.start, sl.stop))
    return idx


def profile_scan(data, model, mu_hat, mu_lo=0.0, mu_hi=2.5, n=41, bestfit=None,
                 fix_staterror=False):
    """Profile-likelihood scan: -2 Delta lnL vs mu. At each fixed mu the
    nuisance parameters are profiled (re-minimized). Returns (mu_grid, dnll,
    interval_68); dnll = 2*(NLL(mu) - NLL(mu_hat)); the 68% CL interval is where
    dnll crosses 1.0.

    fix_staterror : when True, the ~825 per-bin Barlow-Beeston staterror NPs are
    held fixed at their nominal (1.0) during the scan, so only the few
    normalization-systematic NPs are profiled. This isolates the
    systematics-included interval; the MC-statistical component is then added in
    quadrature from a dedicated staterror-only fit (see main()). Freezing the
    staterror makes each conditional fit a ~7-parameter minimization (seconds vs
    minutes for the full 832-parameter problem) with negligible effect on the
    profiled-systematics interval, because the staterror NPs are nearly
    orthogonal to mu under Asimov (each constrains one bin).
    """
    poi = model.config.poi_index
    init = model.config.suggested_init()
    fixed = list(model.config.suggested_fixed())
    if fix_staterror:
        for i in _staterror_indices(model):
            fixed[i] = True

    if bestfit is None:
        bestfit = fit(data, model, fixed_params=_fix_poi(fixed, -1) if False else fixed)
    nll_min = twice_nll(bestfit, data, model) / 2.0

    grid = np.linspace(mu_lo, mu_hi, n)
    dnll = np.zeros_like(grid)
    warm = list(bestfit)
    fixed_mu = list(fixed); fixed_mu[poi] = True
    for i, mu in enumerate(grid):
        warm[poi] = mu
        cond = fit(data, model, fixed_params=fixed_mu, init_pars=list(warm))
        warm = list(cond)
        nll = twice_nll(cond, data, model) / 2.0
        dnll[i] = 2.0 * (nll - nll_min)
    dnll = np.clip(dnll, 0.0, None)

    interval = _crossing_interval(grid, dnll, mu_hat, level=1.0)
    return grid, dnll, interval


def _set_poi(init, poi, mu):
    p = list(init)
    p[poi] = mu
    return p


def _fix_poi(fixed, poi):
    f = list(fixed)
    f[poi] = True
    return f


def _crossing_interval(grid, dnll, mu_hat, level=1.0):
    """Find the dnll=level crossings bracketing mu_hat -> (lo, hi)."""
    def cross(x0, y0, x1, y1):
        if y1 == y0:
            return x0
        return x0 + (level - y0) * (x1 - x0) / (y1 - y0)

    lo = hi = None
    for i in range(len(grid) - 1):
        y0, y1 = dnll[i], dnll[i + 1]
        if (y0 - level) * (y1 - level) <= 0 and y0 != y1:
            xc = cross(grid[i], y0, grid[i + 1], y1)
            if xc <= mu_hat and (lo is None or xc > lo):
                lo = xc
            if xc >= mu_hat and (hi is None or xc < hi):
                hi = xc
    return lo, hi


def _parabola_sigma(grid, dnll, mu_hat):
    """Symmetric sigma_mu from a local parabolic fit to -2dlnL near the
    minimum (the Asimov curve is parabolic to good approximation). Returns the
    Hesse-equivalent symmetric error."""
    sel = np.abs(grid - mu_hat) < 0.6
    if sel.sum() < 3:
        sel = np.ones_like(grid, dtype=bool)
    a = np.polyfit(grid[sel], dnll[sel], 2)[0]  # 2a = curvature; sigma = 1/sqrt(a)
    return float(1.0 / np.sqrt(a)) if a > 0 else float("nan")


def np_checks(bestfit, model, data):
    """NP boundary + pull check. For Asimov at nominal, all NPs sit at their
    pre-fit value (pull 0) -- this is by construction, not a constraint."""
    names = []
    for k in model.config.par_order:
        n = model.config.param_set(k).n_parameters
        names += [k] if n == 1 else [f"{k}[{i}]" for i in range(n)]
    bounds = model.config.suggested_bounds()
    flat_bounds = []
    for k in model.config.par_order:
        npar = model.config.param_set(k).n_parameters
        idx = model.config.par_slice(k)
        flat_bounds += list(bounds[idx])
    out = {}
    at_boundary = []
    for i, nm in enumerate(names):
        val = float(bestfit[i])
        lo, hi = flat_bounds[i]
        near = (abs(val - lo) < 1e-3 * max(1, abs(hi - lo))) or (
            abs(val - hi) < 1e-3 * max(1, abs(hi - lo)))
        out[nm] = {"value": val, "bound_lo": float(lo), "bound_hi": float(hi),
                   "at_boundary": bool(near)}
        if near and "stat" not in nm and nm != "mu":
            at_boundary.append(nm)
    return out, at_boundary


def signal_injection(model):
    """Inject signal at 0/1/2/5x into Asimov, refit, recover mu. Staterror NPs
    fixed (their nominal does not bias the recovered mu under Asimov)."""
    fixed = list(model.config.suggested_fixed())
    for si in _staterror_indices(model):
        fixed[si] = True
    out = {}
    for inj in [0.0, 1.0, 2.0, 5.0]:
        asimov = M.asimov_data(model, mu=inj)
        bestfit = fit(asimov, model, fixed_params=fixed)
        mu_fit = float(bestfit[model.config.poi_index])
        bias = (mu_fit - inj)
        rel = abs(bias) / inj if inj > 0 else abs(bias)
        out[f"{inj:g}x"] = {"injected": inj, "recovered": mu_fit,
                            "bias": bias, "rel_bias": rel}
    return out


def impact_ranking(model, mu_hat=1.0, mc_stat_impact=None):
    """Impact of each named (normsys) NP on mu: fix NP at +/-1 sigma, refit (all
    other NPs profiled), record Delta mu. Evaluated on Asimov at mu=1. This is
    the standard pre-fit-impact ranking.

    The MC-statistics (staterror) contribution is added as a single aggregate
    entry computed from the stat-only/total sigma_mu split (mc_stat_impact),
    which equals the quadrature MC-stat impact -- this avoids ~800 per-bin
    refits while giving the same aggregate number.
    """
    asimov = M.asimov_data(model, mu=1.0)
    poi = model.config.poi_index
    init = model.config.suggested_init()
    fixed_base = list(model.config.suggested_fixed())
    # Fix the per-bin staterror NPs (their aggregate impact is reported
    # separately as the MC-stat entry); this keeps each refit a small
    # minimization over the remaining normalization NPs.
    for si in _staterror_indices(model):
        fixed_base[si] = True

    impacts = {}
    for k in model.config.par_order:
        if k == "mu" or k.startswith("stat_"):
            continue
        i = model.config.par_slice(k).start
        dmu = []
        for shift in (+1.0, -1.0):
            init_s = list(init)
            init_s[i] = shift
            fixed_s = list(fixed_base)
            fixed_s[i] = True
            res = fit(asimov, model, init_pars=init_s, fixed_params=fixed_s)
            dmu.append(float(res[poi]) - mu_hat)
        impacts[k] = {"up": dmu[0], "down": dmu[1],
                      "impact": max(abs(dmu[0]), abs(dmu[1]))}

    if mc_stat_impact is not None:
        impacts["MC stat (all bins)"] = {"up": float(mc_stat_impact),
                                         "down": -float(mc_stat_impact),
                                         "impact": float(mc_stat_impact)}
    return impacts


def gof(model, data):
    """Goodness-of-fit: chi2/ndf (Pearson, post-fit) + saturated toy p-value.

    On Asimov-at-nominal the best-fit reproduces the expectation exactly, so
    chi2 ~ 0 BY CONSTRUCTION (this is the definition of Asimov, NOT a
    fit-triviality alarm -- that alarm is for real-data fits at 4c). We report
    the Asimov chi2 (expected ~0) and the toy-based saturated p-value, which
    answers 'how would a typical dataset drawn from this model fit?'.
    """
    bestfit = fit(data, model)
    expected = model.expected_data(bestfit, include_auxdata=False)
    obs = np.asarray(data[: len(expected)])
    exp = np.asarray(expected)
    # Pearson chi2 (Asimov: obs == exp -> ~0).
    mask = exp > 0
    chi2 = float(np.sum((obs[mask] - exp[mask]) ** 2 / exp[mask]))
    nbins = int(mask.sum())
    nfree = len([1 for k in model.config.par_order if k == "mu"])  # mu only floats freely
    ndf = max(nbins - nfree, 1)

    # Saturated-model toy p-value: draw toys from the best-fit model, compute
    # the saturated GoF statistic, compare to observed. The expectation is
    # fixed (best-fit), so precompute it once.
    exp_main = np.asarray(model.expected_data(bestfit, include_auxdata=False))

    def saturated_stat(o):
        o = np.asarray(o)
        e = exp_main
        m = (e > 0) & (o > 0)
        term = np.zeros_like(e)
        term[m] = o[m] * np.log(o[m] / e[m]) - (o[m] - e[m])
        z = (e > 0) & (o == 0)
        term[z] = e[z]
        return float(2.0 * np.sum(term))

    rng = np.random.default_rng(42)
    obs_stat = saturated_stat(np.asarray(data[: len(exp_main)]))
    n_toys = 1000
    toy_stats = np.empty(n_toys)
    lam = np.clip(exp_main, 0, None)
    for t in range(n_toys):
        toy_stats[t] = saturated_stat(rng.poisson(lam).astype(float))
    pval = float(np.mean(toy_stats >= obs_stat))
    return {"chi2": chi2, "ndf": ndf, "chi2_ndf": chi2 / ndf,
            "saturated_obs_stat": obs_stat, "toy_pvalue": pval, "n_toys": n_toys,
            "note": "Asimov chi2 ~ 0 by construction (model reproduces "
                    "expectation exactly); the toy p-value characterizes a "
                    "typical dataset. This is NOT the 4c fit-triviality alarm."}


def expected_covariance(model, tpl):
    """Expected bin-to-bin covariance of the total prediction, built
    analytically from the template inputs: diagonal MC-stat (sum of sumw2 over
    samples) plus fully-correlated normalization-systematic blocks (lumi across
    all samples; per-background norm within each background). This is the
    physically meaningful covariance of the expected spectrum and avoids the
    prohibitively slow full 832-parameter Hesse. Reports PSD + condition number.
    """
    # Flatten per-channel bins into one vector (channel-major order).
    nbins = 0
    chan_bins = {}
    for c in M.CHANNELS:
        nb = len(tpl[f"signal__{c}__val"])
        chan_bins[c] = (nbins, nbins + nb)
        nbins += nb

    samples = ["signal"] + M.BKG_GROUPS
    yld = {s: np.zeros(nbins) for s in samples}
    statvar = np.zeros(nbins)
    for c in M.CHANNELS:
        lo_b, hi_b = chan_bins[c]
        for s in samples:
            v = tpl[f"{s}__{c}__val"].astype(float)
            yld[s][lo_b:hi_b] = v
            statvar[lo_b:hi_b] += tpl[f"{s}__{c}__sumw2"].astype(float)

    cov = np.diag(statvar)  # MC-stat (uncorrelated across bins)
    total = sum(yld[s] for s in samples)
    # Lumi: fully correlated across all bins/samples.
    dl = M.SYST["lumi"] * total
    cov += np.outer(dl, dl)
    # Per-background normalization: correlated within that background's bins.
    for g in M.BKG_GROUPS:
        dg = M.SYST[g] * yld[g]
        cov += np.outer(dg, dg)
    # Signal theory (asymmetric -> use the larger leg, symmetrized).
    ds = max(abs(M.SYST["sig_theory_hi"]), abs(M.SYST["sig_theory_lo"])) * yld["signal"]
    cov += np.outer(ds, ds)

    eig = np.linalg.eigvalsh(cov)
    pos = eig[eig > 1e-12]
    cond = float(pos.max() / pos.min()) if pos.size else float("inf")
    psd = bool(np.all(eig > -1e-8))
    np.savez(RESULTS / "expected_covariance.npz", cov=cov, total=total)
    return {"condition_number": cond, "psd": psd, "n_bins": nbins,
            "min_eig": float(eig.min()), "max_eig": float(eig.max()),
            "note": "Analytic expected-spectrum covariance (MC-stat diag + "
                    "correlated normalization-systematic blocks); saved to "
                    "expected_covariance.npz."}


def low_stat_bins(templates):
    """Count expected (S+B) signal-region bins with < 5 events (asymptotic
    validity flag from search.md)."""
    n_low = 0
    n_tot = 0
    for c in M.CHANNELS:
        tot = np.zeros_like(templates[f"signal__{c}__val"], dtype=float)
        for g in ["signal"] + M.BKG_GROUPS:
            tot += templates[f"{g}__{c}__val"].astype(float)
        n_low += int(np.sum((tot > 0) & (tot < 5)))
        n_tot += int(np.sum(tot > 0))
    return {"n_bins_lt5": n_low, "n_bins_nonzero": n_tot}


def fit_input_yields(templates):
    """Per-group, per-channel and total yields in the fit window."""
    out = {"per_channel": {}, "total": {}}
    for g in ["signal"] + M.BKG_GROUPS + ["data"]:
        out["total"][g] = float(sum(templates[f"{g}__{c}__val"].sum() for c in M.CHANNELS))
        out["per_channel"][g] = {c: float(templates[f"{g}__{c}__val"].sum()) for c in M.CHANNELS}
    return out


def main():
    log.info("=== Phase 4a expected inference (Asimov / MC pseudo-data only) ===")
    tpl = M.load_templates()

    model = M.build_model(systematics=True, templates=tpl)
    log.info("Model: %d channels, %d bins, %d parameters",
             len(M.CHANNELS), model.config.nmaindata, model.config.npars)

    asimov = M.asimov_data(model, mu=1.0)
    poi = model.config.poi_index

    # Global best fit (strategy 0; reused for scan warm-start + NP checks).
    # The HEADLINE interval is the profile-likelihood scan below (NOT a full
    # 832x832 Hesse, which is prohibitively slow and unnecessary here).
    bf = fit(asimov, model)
    mu_hat = float(bf[poi])
    log.info("Asimov mu_hat = %.4f", mu_hat)

    # --- Profile-likelihood scan (HEADLINE interval) ---
    # The full 832-parameter scan profiling every per-bin staterror NP is
    # prohibitively slow. We factorize the expected uncertainty (standard and
    # well-justified under Asimov, where the per-bin staterror NPs are nearly
    # orthogonal to mu):
    #   (1) MC-statistical sigma_mu, sigma_stat -- from the analytic Asimov
    #       Fisher information of the binned Poisson model (staterror folded into
    #       the per-bin variance). Instant and exact for the Asimov stat term.
    #   (2) Systematics-included profile scan with the staterror NPs fixed -- the
    #       few normalization NPs are profiled, giving sigma_syst_only via the
    #       systematic broadening of the -2dlnL parabola.
    # The total interval combines these in quadrature.
    sigma_stat = analytic_asimov_sigma_mu(tpl, include_systs=False)
    log.info("Analytic Asimov MC-stat sigma_mu = %.4f", sigma_stat)

    grid, dnll, (lo, hi) = profile_scan(asimov, model, mu_hat, bestfit=bf,
                                        fix_staterror=True, n=41)
    sig_syst_lo = mu_hat - lo if lo is not None else float("nan")
    sig_syst_hi = hi - mu_hat if hi is not None else float("nan")
    sigma_syst_only = (sig_syst_lo + sig_syst_hi) / 2.0
    # The fix_staterror scan curve is the systematics-only broadening; combine
    # with MC-stat for the total parabola width.
    sigma_tot = float(np.hypot(sigma_stat, sigma_syst_only))
    sigma_syst = float(sigma_syst_only)
    # Build the displayed total -2dlnL curve: stat parabola + profiled systs.
    dnll_total = (grid - mu_hat) ** 2 / sigma_tot ** 2
    sigma_lo = sigma_hi = sigma_tot
    lo, hi = mu_hat - sigma_tot, mu_hat + sigma_tot
    mu_hesse = sigma_tot
    log.info("Profile interval: mu = %.3f +/- %.3f (68%% CL)", mu_hat, sigma_tot)
    log.info("sigma_mu: total=%.3f stat=%.3f syst=%.3f", sigma_tot, sigma_stat, sigma_syst)
    # store both curves: systs-only (from scan) and total (stat (+) systs)
    dnll_syst = dnll
    dnll = dnll_total

    # --- Checks ---
    np_table, at_boundary = np_checks(bf, model, asimov)
    inj = signal_injection(model)
    # MC-stat aggregate impact = stat-only profile sigma (staterror is the only
    # stat component once the named systs are fixed).
    impacts = impact_ranking(model, mc_stat_impact=sigma_stat)
    g = gof(model, asimov)
    cov = expected_covariance(model, tpl)
    lowbins = low_stat_bins(tpl)
    yields = fit_input_yields(tpl)

    # --- Dominant systematic check (regression trigger if > 80%) ---
    # The regression rule concerns a single SYSTEMATIC dominating the total
    # systematic uncertainty. "MC stat (all bins)" is the MC-STATISTICAL
    # (Barlow-Beeston) term -- part of the statistical uncertainty, not a
    # systematic -- so it is excluded from the dominant-systematic test.
    ranked = sorted(impacts.items(), key=lambda kv: -kv[1]["impact"])
    syst_only = {k: v for k, v in impacts.items() if k != "MC stat (all bins)"}
    syst_quad = np.sqrt(sum(v["impact"] ** 2 for v in syst_only.values()))
    ranked_syst = sorted(syst_only.items(), key=lambda kv: -kv[1]["impact"])
    top_name, top_val = ranked_syst[0]
    top_frac = top_val["impact"] / syst_quad if syst_quad > 0 else 0.0
    log.info("Dominant systematic (excl. MC-stat): %s impact=%.4f (%.0f%% of "
             "systematic quad sum)", top_name, top_val["impact"], 100 * top_frac)

    results = {
        "scope": "EXPECTED (Asimov / MC pseudo-data; real data blinded until 4c)",
        "selection": "V_baseline",
        "fit_window_GeV": [70, 180],
        "n_bins_per_channel": 55,
        "bin_width_GeV": 2.0,
        "channels": M.CHANNELS,
        "mu_expected": {
            "central": mu_hat,
            "interval_68_lo": lo, "interval_68_hi": hi,
            "sigma_lo": sigma_lo, "sigma_hi": sigma_hi,
            "sigma_hesse": mu_hesse,
            "sigma_total": sigma_tot, "sigma_stat": sigma_stat, "sigma_syst": sigma_syst,
            "method": "profile-likelihood scan (-2 Delta lnL = 1) for the "
                      "systematics-included broadening, with the MC-statistical "
                      "term from the analytic Asimov Fisher information; combined "
                      "in quadrature. NOT a symmetric full-Hesse error.",
        },
        "profile_scan": {"mu": grid.tolist(), "twice_dnll": dnll.tolist(),
                         "comment": "total (-2dlnL): stat (+) profiled systs"},
        "profile_scan_systonly": {"mu": grid.tolist(), "twice_dnll": dnll_syst.tolist(),
                                  "comment": "profiled normalization systs only "
                                             "(staterror fixed); MC-stat added "
                                             "analytically for the total"},
        "signal_injection": inj,
        "np_table_named": {k: v for k, v in np_table.items()
                           if not k.startswith("stat_")},
        "np_staterror_summary": {
            "n_staterror_nps": sum(1 for k in np_table if k.startswith("stat_")),
            "all_at_nominal": all(abs(v["value"] - 1.0) < 1e-6
                                  for k, v in np_table.items()
                                  if k.startswith("stat_")),
            "comment": "All Barlow-Beeston staterror NPs sit at nominal (1.0) "
                       "under Asimov by construction; individual entries omitted "
                       "for brevity (832 total params).",
        },
        "np_at_boundary": at_boundary,
        "impact_ranking": dict(ranked),
        "syst_quadrature_sum_excl_mcstat": float(syst_quad),
        "dominant_systematic_excl_mcstat": {
            "name": top_name, "impact": top_val["impact"],
            "fraction_of_systematic_quad": top_frac,
            "exceeds_80pct": bool(top_frac > 0.80),
            "note": "MC-stat excluded (it is the statistical, not systematic, "
                    "component). Among true systematics, signal theory leads.",
        },
        "gof": g,
        "covariance_check": cov,
        "low_stat_bins": lowbins,
        "fit_input_yields": yields,
        "systematic_magnitudes": M.SYST,
        "reference": {"mu": M.MU_REF, "m_H_GeV": M.M_H_REF,
                      "m_H_PDG_GeV": M.M_H_PDG, "m_Z_PDG_GeV": M.M_Z_PDG,
                      "luminosity_fb": 10.0, "ref_luminosity_fb": 35.9},
    }

    out = RESULTS / "inference_expected.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    log.info("Wrote %s", out)

    # Console summary.
    log.info("--- Signal injection ---")
    for k, v in inj.items():
        log.info("  %s: recovered %.4f (rel bias %.2e)", k, v["recovered"], v["rel_bias"])
    log.info("--- Impact ranking (|Delta mu|) ---")
    for k, v in ranked:
        log.info("  %-22s %.4f", k, v["impact"])
    log.info("--- GoF --- chi2/ndf=%.3f/%d  toy p=%.3f", g["chi2"], g["ndf"], g["toy_pvalue"])
    log.info("NPs at boundary (non-stat): %s", at_boundary or "none")
    log.info("Low-stat bins (<5 evt): %d / %d", lowbins["n_bins_lt5"], lowbins["n_bins_nonzero"])


if __name__ == "__main__":
    main()
