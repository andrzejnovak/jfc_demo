# SKELETON (demo seed): adapt parameters/paths for the analysis; the live
# Phase-3 executor sets and justifies the selection, runs it, produces plots,
# and is reviewed. The selection logic is the tested reference; cut VALUES are
# named parameters the live executor sets and justifies.

"""Phase 3: selection figures for the PRIMARY variant (V_baseline).

  * N-1 motivation plots for the main analysis cuts: isolation, sip3d, mZ2
    (each: all selection cuts applied EXCEPT the one shown, stacked bkg +
    signal + data, with the cut threshold marked).
  * Final m4l stacked spectrum (combined + per channel) on the fit window
    [70,180] GeV after the full selection + best-candidate choice.

CMS style, figsize (10,10), exp_label Open Data, no titles, PDF+PNG.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import hist
import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np
from mplhep import mpl_magic
from rich.logging import RichHandler

sys.path.insert(0, str(Path(__file__).resolve().parent))
import selection as S  # noqa: E402

logging.basicConfig(
    level=logging.INFO, format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

mh.style.use("CMS")

OUT_DIR = S.ANALYSIS_ROOT / "phase3_selection" / "outputs"
FIG_DIR = OUT_DIR / "figures"

PRIMARY = "V_baseline"
CFG = S.V_BASELINE

BKG_GROUPS = ["DY", "ttbar", "ggZZ", "qqZZ"]
BKG_LABELS = {
    "DY": "Drell-Yan", "ttbar": r"$t\bar{t}$",
    "ggZZ": r"gg$\to$ZZ", "qqZZ": r"q$\bar{q}\to$ZZ",
}
BKG_COLORS = {"DY": "#7f7f7f", "ttbar": "#8c564b", "ggZZ": "#2ca02c", "qqZZ": "#1f77b4"}
SIG_LABEL = r"H$\to$ZZ$^*\to$4$\ell$ ($\mu=1$)"
RLABEL = r"$\sqrt{s} = 13$ TeV, 10 fb$^{-1}$"

CHAN_TITLE = {"4mu": r"4$\mu$", "4e": "4e", "2e2mu": r"2e2$\mu$"}


def _load_all() -> dict:
    """Load every sample's branches + weight + per-cand masks for the primary cfg."""
    weights = {f: S.sample_weight(f) for f in S.MC_FILES}
    out = {}
    for f in S.ALL_FILES:
        d = S.load_sample(f)
        is_data = f == S.DATA_FILE
        out[f] = {
            "d": d,
            "chan": S.channel_of(d),
            "weight": 1.0 if is_data else weights[f],
            "group": "data" if is_data else S.GROUP[f],
            "is_data": is_data,
        }
    return out


def _fill_grouped(samples: dict, axis: hist.axis.Regular, var_fn, mask_fn,
                  chan: str | None = None) -> dict:
    """Build group->Hist for bkg+signal and a data Hist, given per-sample
    value function var_fn(d)->array and mask function mask_fn(f,d)->bool mask."""
    hists = {}
    for g in BKG_GROUPS + ["signal"]:
        h = hist.Hist(axis, storage=hist.storage.Weight())
        for f, s in samples.items():
            if s["group"] != g:
                continue
            m = mask_fn(f, s["d"])
            if chan is not None:
                m = m & (s["chan"] == chan)
            v = var_fn(s["d"])[m]
            h.fill(v, weight=np.full(len(v), s["weight"]))
        hists[g] = h
    hd = hist.Hist(axis, storage=hist.storage.Weight())
    for f, s in samples.items():
        if not s["is_data"]:
            continue
        m = mask_fn(f, s["d"])
        if chan is not None:
            m = m & (s["chan"] == chan)
        hd.fill(var_fn(s["d"])[m])
    hists["data"] = hd
    return hists


def _stacked(hists: dict, xlabel: str, fname: str, logy: bool = True,
             vlines: list[float] | None = None, xunit: str = "GeV",
             legend_title: str | None = None) -> None:
    fig, ax = plt.subplots(figsize=(10, 10))
    bkg_h = [hists[g] for g in BKG_GROUPS]
    mh.histplot(bkg_h, stack=True, histtype="fill",
                label=[BKG_LABELS[g] for g in BKG_GROUPS],
                color=[BKG_COLORS[g] for g in BKG_GROUPS],
                ax=ax, edgecolor="black", linewidth=0.5)
    mh.histplot(hists["signal"], histtype="step", color="red", linewidth=2.0,
                label=SIG_LABEL, ax=ax)
    mh.histplot(hists["data"], histtype="errorbar", color="black",
                label="Data", ax=ax, xerr=True)

    bw = bkg_h[0].axes[0].widths[0]
    unitsfx = f" [{xunit}]" if xunit else ""
    ax.set_xlabel(f"{xlabel}{unitsfx}")
    ax.set_ylabel(f"Events / {bw:g} {xunit}".rstrip())
    if vlines:
        for x in vlines:
            ax.axvline(x, color="black", linestyle="--", linewidth=1.2)
    if logy:
        ax.set_yscale("log")
        ymax = max(h.values().max() for h in bkg_h + [hists["data"]] if h.values().size)
        ax.set_ylim(0.3, max(ymax, 1.0) * 50)
        ax.legend(loc="upper right", fontsize="x-small", title=legend_title)
    else:
        ax.legend(loc="upper right", fontsize="x-small", title=legend_title)
        mpl_magic(ax)
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Data",
                       rlabel=RLABEL, loc=0, ax=ax)
    fig.savefig(FIG_DIR / f"{fname}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / f"{fname}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Wrote %s.{pdf,png}", fname)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    samples = _load_all()

    # ---- N-1 plots (full selection minus the shown cut) ----
    # Isolation: max lepton pfRelIso03 per candidate, N-1 dropping lepton_iso.
    def iso_var(d):
        return np.max(d["lep_pfRelIso03"], axis=1)

    def best_nm1(f, d, drop):
        presel = S.nminus1_mask(d, CFG, drop)
        return S.best_candidate_mask(d, presel)

    h_iso = _fill_grouped(samples, hist.axis.Regular(35, 0.0, 0.35, name="iso"),
                          iso_var, lambda f, d: best_nm1(f, d, "lepton_iso"))
    _stacked(h_iso, r"max lepton $I_{rel}^{PF}$ (N-1)", "nm1_isolation",
             logy=True, vlines=[CFG.iso_max], xunit="")

    # sip3d: max lepton sip3d, N-1 dropping lepton_ip.
    def sip_var(d):
        return np.max(d["lep_sip3d"], axis=1)

    h_sip = _fill_grouped(samples, hist.axis.Regular(40, 0.0, 4.0, name="sip"),
                          sip_var, lambda f, d: best_nm1(f, d, "lepton_ip"))
    _stacked(h_sip, r"max lepton SIP$_{3D}$ (N-1)", "nm1_sip3d",
             logy=True, vlines=[CFG.sip3d_max], xunit="")

    # mZ2: N-1 dropping mZ2_window.
    h_mz2 = _fill_grouped(samples, hist.axis.Regular(54, 12.0, 120.0, name="mZ2"),
                          lambda d: d["mZ2"], lambda f, d: best_nm1(f, d, "mZ2_window"))
    _stacked(h_mz2, r"$m_{Z_2}$ (N-1)", "nm1_mZ2", logy=True,
             vlines=[CFG.mZ2_lo, CFG.mZ2_hi])

    # ---- Final m4l spectra (full selection) ----
    full = lambda f, d: S.best_candidate_mask(d, S.full_mask(d, CFG))  # noqa: E731
    edges = hist.axis.Regular(55, 70.0, 180.0, name="m4l")

    h_comb = _fill_grouped(samples, edges, lambda d: d["m4l"], full)
    _stacked(h_comb, r"$m_{4\ell}$", "m4l_final_combined", logy=True)

    for c in S.CHANNELS:
        h_c = _fill_grouped(samples, edges, lambda d: d["m4l"], full, chan=c)
        _stacked(h_c, r"$m_{4\ell}$", f"m4l_final_{c}", logy=True,
                 legend_title=CHAN_TITLE[c])


if __name__ == "__main__":
    main()
