# SKELETON (demo seed): adapt the systematic magnitudes (see
# conventions/cited_constants.md) and templates for the analysis; verify the
# uncertainty decomposition. The live Phase-4a executor finalizes the
# statistical model, runs the inference, produces plots, and is reviewed.

"""Phase 4a figures (expected results, Asimov / MC pseudo-data only).

Produces (CMS style, Open Simulation label, figsize (10,10), no titles):
  1. m4l_expected_stack        -- expected m4l stacked spectrum + total-unc band
  2. mu_profile_scan           -- mu profile-likelihood -2 Delta lnL scan
  3. syst_impact_ranking       -- systematic impact ranking on mu
  4. signal_lineshape          -- DSCB fit to signal MC m4l
  5. mH_expected_fit           -- expected m_H Asimov peak + resolution model

Reads results from phase5_documentation/outputs/results/.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np
from mplhep import mpl_magic
from rich.logging import RichHandler

import model as M
from mass_fit import dscb_unnorm

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

np.random.seed(42)
mh.style.use("CMS")

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "phase5_documentation/outputs/results"
FIGDIR = ROOT / "phase4_inference/4a_expected/outputs/figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

RLABEL = r"$\sqrt{s} = 13$ TeV, 10 fb$^{-1}$"


def exp_label(ax):
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Simulation",
                       rlabel=RLABEL, loc=0, ax=ax)


def save(fig, name):
    fig.savefig(FIGDIR / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIGDIR / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("wrote %s pdf and png", name)


def plot_m4l_stack(tpl, res):
    edges = tpl["edges"]
    centers = 0.5 * (edges[:-1] + edges[1:])
    groups = ["DY", "ttbar", "ggZZ", "qqZZ"]
    labels = {"DY": "Drell-Yan", "ttbar": r"$t\bar{t}$", "ggZZ": r"gg$\to$ZZ",
              "qqZZ": r"qq$\to$ZZ"}
    stacks = []
    for g in groups:
        v = sum(tpl[f"{g}__{c}__val"] for c in M.CHANNELS)
        stacks.append(v)
    sig = sum(tpl[f"signal__{c}__val"] for c in M.CHANNELS)
    total = np.sum(stacks, axis=0) + sig

    # total uncertainty band: MC-stat (sumw2) + normalization systs in quadrature
    var = np.zeros_like(total)
    for g in groups + ["signal"]:
        var += sum(tpl[f"{g}__{c}__sumw2"] for c in M.CHANNELS)
    # add normalization systs
    for g in groups:
        v = sum(tpl[f"{g}__{c}__val"] for c in M.CHANNELS)
        var += (M.SYST[g] * v) ** 2
    var += (M.SYST["lumi"] * total) ** 2
    band = np.sqrt(var)

    fig, ax = plt.subplots(figsize=(10, 10))
    mh.histplot(stacks, bins=edges, stack=True, histtype="fill",
                label=[labels[g] for g in groups], ax=ax,
                color=["#7fbf7f", "#c7a3d4", "#fdae61", "#4575b4"])
    mh.histplot(sig + np.sum(stacks, axis=0), bins=edges, histtype="step",
                color="red", label=r"Signal ($\mu=1$) + bkg", ax=ax, linewidth=2)
    # expected (Asimov) "data" = total expectation, shown as points
    ax.errorbar(centers, total, yerr=np.sqrt(total), fmt="o", color="black",
                markersize=4, label="Asimov ($\\mu=1$)")
    ax.fill_between(edges[:-1], total - band, total + band, step="post",
                    alpha=0.3, color="gray", label="Total unc.", zorder=5)
    ax.set_xlabel(r"$m_{4\ell}$ [GeV]")
    ax.set_ylabel("Events / 2 GeV")
    ax.set_xlim(edges[0], edges[-1])
    ax.set_yscale("log")
    ax.set_ylim(0.5, None)
    ax.legend(loc="upper right", fontsize="x-small")
    mpl_magic(ax)
    exp_label(ax)
    save(fig, "m4l_expected_stack")


def plot_mu_scan(res):
    sc = res["profile_scan"]
    mu = np.array(sc["mu"]); dnll = np.array(sc["twice_dnll"])
    me = res["mu_expected"]
    # stat-only parabola for overlay (analytic MC-stat sigma)
    mu_s = mu
    dnll_s = (mu_s - me["central"]) ** 2 / me["sigma_stat"] ** 2

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(mu, dnll, color="#4575b4", linewidth=2, label=r"Stat $\oplus$ syst")
    ax.plot(mu_s, dnll_s, color="#d73027", linewidth=2, linestyle="--",
            label="Stat only")
    ax.axhline(1.0, color="gray", linestyle=":", linewidth=1)
    ax.axvline(1.0, color="black", linestyle="-", linewidth=1, label=r"SM ($\mu=1$)")
    ax.axvline(M.MU_REF, color="green", linestyle="-.", linewidth=1.5,
               label=r"Ref. $\mu=1.05$ [1706.09936]")
    mh.label.add_text(r"68% CL", x=0.04, y=0.10, ax=ax)
    ax.set_xlabel(r"$\mu$")
    ax.set_ylabel(r"$-2\,\Delta\ln L$")
    ax.set_xlim(mu.min(), mu.max())
    ax.legend(loc="upper right", fontsize="x-small")
    # Fix the y-range AFTER the legend so the parabola fills the panel; the
    # empty upper region holds the legend without mpl_magic over-expansion.
    ax.set_ylim(0, 6.5)
    exp_label(ax)
    save(fig, "mu_profile_scan")


def plot_impact(res):
    imp = res["impact_ranking"]
    nice = {"lumi": "Luminosity (2.3%)", "norm_qqZZ": "qqZZ norm (10%)",
            "norm_ggZZ": "ggZZ norm (10%)", "norm_DY": "DY norm (40%)",
            "norm_ttbar": r"$t\bar{t}$ norm (40%)", "sig_theory": "Signal theory",
            "MC stat (all bins)": "MC statistics"}
    items = sorted(imp.items(), key=lambda kv: kv[1]["impact"])
    names = [nice.get(k, k) for k, _ in items]
    ups = [v["up"] for _, v in items]
    downs = [v["down"] for _, v in items]
    y = np.arange(len(items))

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(y, ups, color="#4575b4", alpha=0.8, label=r"$+1\sigma$")
    ax.barh(y, downs, color="#d73027", alpha=0.8, label=r"$-1\sigma$")
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel(r"$\Delta\mu$")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.legend(loc="lower right", fontsize="x-small")
    exp_label(ax)
    save(fig, "syst_impact_ranking")


def plot_signal_lineshape():
    arr = np.load(RESULTS / "mass_fit_arrays.npz")
    edges = arr["edges_fit"]; raw = arr["raw"]
    p = arr["dscb_params"]  # mu,sigma,aL,nL,aR,nR
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    dens = dscb_unnorm(centers, *p)
    dens = dens / (dens * widths).sum() * raw.sum() * widths

    fig, ax = plt.subplots(figsize=(10, 10))
    mh.histplot(raw, bins=edges, histtype="errorbar", color="black",
                label="Signal MC", ax=ax)
    ax.plot(centers, dens, color="red", linewidth=2, label="DSCB fit")
    mh.label.add_text(rf"peak = {p[0]:.2f} GeV", x=0.05, y=0.80, ax=ax)
    mh.label.add_text(rf"$\sigma$ = {p[1]:.2f} GeV", x=0.05, y=0.73, ax=ax)
    ax.set_xlabel(r"$m_{4\ell}$ [GeV]")
    ax.set_ylabel("Signal candidates / 0.25 GeV")
    ax.set_xlim(edges[0], edges[-1])
    ax.legend(loc="upper right", fontsize="x-small")
    mpl_magic(ax)
    exp_label(ax)
    save(fig, "signal_lineshape")


def plot_mH_fit():
    arr = np.load(RESULTS / "mass_fit_arrays.npz")
    edges = arr["edges_asimov"]; asimov = arr["asimov"]
    s, mpeak, b, tau = arr["asimov_params"]
    dscb_p = arr["dscb_params"]
    centers = 0.5 * (edges[:-1] + edges[1:]); widths = np.diff(edges)
    sd = dscb_unnorm(centers, mpeak, *dscb_p[1:])
    sd = sd / (sd * widths).sum()
    bd = np.exp(-tau * (centers - edges[0])); bd = bd / (bd * widths).sum()
    sig_curve = s * sd * widths
    bkg_curve = b * bd * widths
    with open(RESULTS / "mass_expected.json") as f:
        mres = json.load(f)
    smH = mres["expected_mH"]["sigma_mH_stat_GeV"]

    fig, ax = plt.subplots(figsize=(10, 10))
    mh.histplot(asimov, bins=edges, histtype="errorbar", color="black",
                label="Asimov S+B", ax=ax)
    ax.plot(centers, sig_curve + bkg_curve, color="red", linewidth=2,
            label="S+B fit")
    ax.plot(centers, bkg_curve, color="#4575b4", linewidth=1.5, linestyle="--",
            label="Background")
    ref_lbl = "Ref. $m_H$ = " + f"{M.M_H_REF}" + " GeV"
    ax.axvline(M.M_H_REF, color="green", linestyle="-.", linewidth=1.5,
               label=ref_lbl)
    mh.label.add_text(rf"$m_H$ = {mpeak:.2f} ± {smH:.2f} GeV (stat)",
                      x=0.04, y=0.80, ax=ax)
    ax.set_xlabel(r"$m_{4\ell}$ [GeV]")
    ax.set_ylabel("Events / 0.5 GeV")
    ax.set_xlim(edges[0], edges[-1])
    ax.legend(loc="upper right", fontsize="x-small")
    mpl_magic(ax)
    exp_label(ax)
    save(fig, "mH_expected_fit")


def main():
    tpl = M.load_templates()
    with open(RESULTS / "inference_expected.json") as f:
        res = json.load(f)
    plot_m4l_stack(tpl, res)
    plot_mu_scan(res)
    plot_impact(res)
    plot_signal_lineshape()
    plot_mH_fit()
    log.info("All Phase 4a figures written to %s", FIGDIR)


if __name__ == "__main__":
    main()
