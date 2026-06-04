# SKELETON (demo seed): adapt parameters/paths for the analysis; the live
# Phase-3 executor sets and justifies the selection, runs it, produces plots,
# and is reviewed. The selection logic is the tested reference; cut VALUES are
# named parameters the live executor sets and justifies.

"""Phase 3: H->ZZ*->4l event selection library.

Implements the two cut-based selection variants (V_baseline, V_tight) on the
pre-built 4l candidates in the flat ``h4lTree`` ntuples, the best-candidate
per-event choice (required on data; a no-op on MC), per-channel mapping, the
flat per-sample MC normalisation weight ``w = sigma * L / N_gen``, and a
weighted cutflow accumulator.

Cut values trace to the Phase 1 STRATEGY (Sec 3) and the reference HZZ4l
analysis (arXiv:1706.09936). The ntuplizer pre-applies loose object cuts
(pT>=5 GeV, |eta|<=2.5(e)/2.4(mu), sip3d<4, pfRelIso03<0.35, loose dxy/dz);
the analysis-level selection here tightens lepton ID, isolation, pT thresholds
and the Z-mass windows on top of that loose preselection.

No I/O side-effects on import. Pure-columnar (numpy boolean masks), no event
loops over candidates.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import uproot

log = logging.getLogger(__name__)

ANALYSIS_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ANALYSIS_ROOT / "data"

# --- Physics constants (cited) ---
# PDG world-average Z-boson mass. Source: Particle Data Group, Review of
# Particle Physics (Z-boson listings), m_Z = 91.1876 +/- 0.0021 GeV. Only the
# central value enters the Z1 definition and the best-candidate tie-break,
# where sub-MeV precision is irrelevant.
M_Z = 91.1876  # GeV

# --- Normalisation inputs ---
L_FB = 10.0  # integrated luminosity, fb^-1 (data sample name; Metadata/lumi_fb=10)
PB_TO_FB = 1000.0

# Cross sections in pb, from prompt.md (requester-authoritative [A1]).
XSEC_PB = {
    "GluGluToHToZZ.root": 0.00602392,
    "VBF_HToZZ.root": 0.00048794,
    "ZHToZZ.root": 0.000098394,
    "WPHToZZ.root": 0.0001072352,
    "WMHToZZ.root": 0.0000670716,
    "ZZTo4L.root": 1.325,
    "DYJetsToLL.root": 5396.0,
    "TTBar.root": 52.70,
    "GGZZ2E2Mu.root": 0.003185,
    "GGZZ4E.root": 0.001575,
    "GGZZ4Mu.root": 0.001619,
}

GROUP = {
    "GluGluToHToZZ.root": "signal",
    "VBF_HToZZ.root": "signal",
    "ZHToZZ.root": "signal",
    "WPHToZZ.root": "signal",
    "WMHToZZ.root": "signal",
    "ZZTo4L.root": "qqZZ",
    "GGZZ2E2Mu.root": "ggZZ",
    "GGZZ4E.root": "ggZZ",
    "GGZZ4Mu.root": "ggZZ",
    "DYJetsToLL.root": "DY",
    "TTBar.root": "ttbar",
}

DATA_FILE = "data_secret_10fb.root"
MC_FILES = list(XSEC_PB.keys())
ALL_FILES = MC_FILES + [DATA_FILE]

# finalState code -> channel (Phase 2: 100% pure mapping).
CHANNEL = {0: "4mu", 1: "4e", 2: "2e2mu"}
CHANNELS = ["4mu", "4e", "2e2mu"]


@dataclass
class SelectionConfig:
    """Parameterised cut definition for one selection variant."""

    name: str
    # Lepton kinematics
    pt_lead: float = 20.0
    pt_sublead: float = 10.0
    pt_other: float = 5.0
    eta_max_e: float = 2.5
    eta_max_mu: float = 2.4
    # Lepton ID
    mu_use_tight: bool = False  # False -> muMedium, True -> muTight (both & muPF)
    el_wp: str = "WP90"  # "WP90" or "WP80"
    # Isolation
    iso_max: float = 0.35
    # Impact parameter
    sip3d_max: float = 4.0
    dxy_max: float = 0.5
    dz_max: float = 1.0
    # Z-mass windows
    mZ1_lo: float = 40.0
    mZ1_hi: float = 120.0
    mZ2_lo: float = 12.0
    mZ2_hi: float = 120.0
    # Z2 leading-lepton pT floor (tight variant uses this; 0 disables)
    z2_lead_pt: float = 0.0
    # Ghost / overlap removal
    mll_min: float = 4.0
    dR_min: float = 0.02
    # 4l fit window
    m4l_lo: float = 70.0
    m4l_hi: float = 180.0
    # Ordered cut stages for the cutflow
    stages: list[str] = field(
        default_factory=lambda: [
            "ntuple_preselection",
            "lepton_pt",
            "lepton_eta",
            "lepton_id",
            "lepton_iso",
            "lepton_ip",
            "mZ1_window",
            "mZ2_window",
            "ghost_overlap",
            "m4l_window",
        ]
    )


V_BASELINE = SelectionConfig(
    name="V_baseline",
    mu_use_tight=False,
    el_wp="WP90",
    iso_max=0.35,
    mZ2_lo=12.0,
    z2_lead_pt=0.0,
)

# V_tight: three simultaneous tightenings vs baseline -- tighter lepton ID
# (muTight + elMvaWP80), tighter isolation (0.20), and a narrower effective Z2
# region via a 12 GeV floor on the leading Z2 lepton. Genuinely distinct from a
# single-parameter tweak (Phase 1 review Cat-C note).
V_TIGHT = SelectionConfig(
    name="V_tight",
    mu_use_tight=True,
    el_wp="WP80",
    iso_max=0.20,
    mZ2_lo=12.0,
    z2_lead_pt=12.0,
)

VARIANTS = {"V_baseline": V_BASELINE, "V_tight": V_TIGHT}

# Per-lepton branches needed for selection.
_LEP_VARS = [
    "pt", "eta", "phi", "mass", "charge", "pdgId", "zId",
    "dxy", "dz", "sip3d", "pfRelIso03",
    "muMedium", "muTight", "muPF",
    "elMvaWP90", "elMvaWP80",
]
_CAND_VARS = ["run", "lumi", "event", "finalState", "mZ1", "mZ2", "m4l"]


def get_ngen(path: Path) -> int:
    """N_gen = sum of Metadata/nEvents over all entries (one per merged file)."""
    with uproot.open(path) as f:
        nev = f["Metadata"]["nEvents"].array(library="np")
    return int(np.sum(nev))


def sample_weight(fname: str) -> float:
    """Flat per-sample MC weight w = sigma[fb] * L[fb^-1] / N_gen."""
    ngen = get_ngen(DATA_DIR / fname)
    return XSEC_PB[fname] * PB_TO_FB * L_FB / ngen


def load_sample(fname: str) -> dict:
    """Load all needed branches as a dict of numpy arrays.

    Per-lepton arrays are stacked into shape (n_cand, 4) under key ``lep_<var>``;
    candidate-level arrays keep their branch names.
    """
    branches = list(_CAND_VARS)
    for i in (1, 2, 3, 4):
        for v in _LEP_VARS:
            branches.append(f"l{i}{v}")
    with uproot.open(DATA_DIR / fname) as f:
        a = f["h4lTree"].arrays(branches, library="np")
    out = {k: a[k] for k in _CAND_VARS}
    for v in _LEP_VARS:
        out[f"lep_{v}"] = np.stack([a[f"l{i}{v}"] for i in (1, 2, 3, 4)], axis=1)
    return out


def _lepton_masks(d: dict, cfg: SelectionConfig) -> dict:
    """Per-lepton boolean masks (shape (n_cand, 4)) for each lepton-level cut."""
    pdg = np.abs(d["lep_pdgId"])
    is_e = pdg == 11
    is_mu = pdg == 13

    # pT: leading >= pt_lead, subleading >= pt_sublead, all >= pt_other.
    # Stored l1 is the leading lepton; per-lepton floor is pt_other.
    pt = d["lep_pt"]
    pt_ok = pt >= cfg.pt_other  # per-lepton floor

    eta = np.abs(d["lep_eta"])
    eta_ok = (is_e & (eta <= cfg.eta_max_e)) | (is_mu & (eta <= cfg.eta_max_mu))

    # ID: muons -> muPF & (muMedium|muTight); electrons -> WP90|WP80.
    mu_id_flag = d["lep_muTight"] if cfg.mu_use_tight else d["lep_muMedium"]
    mu_id = (d["lep_muPF"] == 1) & (mu_id_flag == 1)
    el_flag = d["lep_elMvaWP80"] if cfg.el_wp == "WP80" else d["lep_elMvaWP90"]
    el_id = el_flag == 1
    id_ok = (is_mu & mu_id) | (is_e & el_id)

    iso_ok = d["lep_pfRelIso03"] < cfg.iso_max

    ip_ok = (
        (d["lep_sip3d"] < cfg.sip3d_max)
        & (np.abs(d["lep_dxy"]) < cfg.dxy_max)
        & (np.abs(d["lep_dz"]) < cfg.dz_max)
    )
    return {
        "pt": pt_ok,
        "eta": eta_ok,
        "id": id_ok,
        "iso": iso_ok,
        "ip": ip_ok,
    }


def _pt_event_mask(d: dict, cfg: SelectionConfig) -> np.ndarray:
    """Leading/subleading pT requirement at the candidate level."""
    pt_sorted = np.sort(d["lep_pt"], axis=1)[:, ::-1]  # descending
    return (pt_sorted[:, 0] >= cfg.pt_lead) & (pt_sorted[:, 1] >= cfg.pt_sublead)


def _ghost_overlap_mask(d: dict, cfg: SelectionConfig) -> np.ndarray:
    """m(ll)>mll_min for all OS pairs and dR>dR_min for all lepton pairs."""
    import vector

    n = len(d["m4l"])
    leps = []
    for i in range(4):
        leps.append(
            vector.array({
                "pt": d["lep_pt"][:, i],
                "eta": d["lep_eta"][:, i],
                "phi": d["lep_phi"][:, i],
                "mass": d["lep_mass"][:, i],
            })
        )
    charge = d["lep_charge"]
    ok = np.ones(n, dtype=bool)
    for i in range(4):
        for j in range(i + 1, 4):
            dphi = np.abs(leps[i].phi - leps[j].phi)
            dphi = np.where(dphi > np.pi, 2 * np.pi - dphi, dphi)
            deta = leps[i].eta - leps[j].eta
            dR = np.sqrt(deta**2 + dphi**2)
            ok &= dR > cfg.dR_min
            # m(ll) for opposite-sign pairs only
            os = charge[:, i] != charge[:, j]
            mll = (leps[i] + leps[j]).mass
            ok &= ~os | (mll > cfg.mll_min)
    return ok


def _z2_lead_pt_mask(d: dict, cfg: SelectionConfig) -> np.ndarray:
    """Leading Z2 lepton pT >= z2_lead_pt (tight variant). zId==2 -> Z2."""
    if cfg.z2_lead_pt <= 0:
        return np.ones(len(d["m4l"]), dtype=bool)
    z2 = d["lep_zId"] == 2
    pt = np.where(z2, d["lep_pt"], -np.inf)
    return np.max(pt, axis=1) >= cfg.z2_lead_pt


def cut_masks(d: dict, cfg: SelectionConfig) -> dict[str, np.ndarray]:
    """Return per-candidate boolean masks for each cut stage (cumulative-ready).

    Each value is the mask for that individual stage (not yet ANDed); the
    cutflow ANDs them in order. ``ntuple_preselection`` is all-True (every
    stored candidate already passed the loose ntuple object cuts).
    """
    n = len(d["m4l"])
    lm = _lepton_masks(d, cfg)
    masks: dict[str, np.ndarray] = {}
    masks["ntuple_preselection"] = np.ones(n, dtype=bool)
    masks["lepton_pt"] = _pt_event_mask(d, cfg) & np.all(lm["pt"], axis=1)
    masks["lepton_eta"] = np.all(lm["eta"], axis=1)
    masks["lepton_id"] = np.all(lm["id"], axis=1)
    masks["lepton_iso"] = np.all(lm["iso"], axis=1)
    masks["lepton_ip"] = np.all(lm["ip"], axis=1)
    masks["mZ1_window"] = (d["mZ1"] >= cfg.mZ1_lo) & (d["mZ1"] <= cfg.mZ1_hi)
    masks["mZ2_window"] = (
        (d["mZ2"] >= cfg.mZ2_lo)
        & (d["mZ2"] <= cfg.mZ2_hi)
        & _z2_lead_pt_mask(d, cfg)
    )
    masks["ghost_overlap"] = _ghost_overlap_mask(d, cfg)
    masks["m4l_window"] = (d["m4l"] >= cfg.m4l_lo) & (d["m4l"] <= cfg.m4l_hi)
    return masks


def full_mask(d: dict, cfg: SelectionConfig) -> np.ndarray:
    """Final per-candidate selection mask (all stages ANDed)."""
    masks = cut_masks(d, cfg)
    sel = np.ones(len(d["m4l"]), dtype=bool)
    for stage in cfg.stages:
        sel &= masks[stage]
    return sel


def nminus1_mask(d: dict, cfg: SelectionConfig, drop: str) -> np.ndarray:
    """Selection with every stage applied EXCEPT ``drop`` (for N-1 plots)."""
    masks = cut_masks(d, cfg)
    sel = np.ones(len(d["m4l"]), dtype=bool)
    for stage in cfg.stages:
        if stage == drop:
            continue
        sel &= masks[stage]
    return sel


def best_candidate_mask(d: dict, presel: np.ndarray) -> np.ndarray:
    """Best-candidate-per-event mask among candidates passing ``presel``.

    HZZ4l rule: within each (run, lumi, event), keep the single candidate with
    the smallest |mZ1 - m_Z|; tie-break on the highest scalar-sum pT of the Z2
    leptons. Returns a boolean mask over ALL candidates (True only for the kept
    best candidate of each event; False for everything failing ``presel``).

    On MC (1 candidate/event) this is a no-op among preselected candidates.
    """
    n = len(d["m4l"])
    keep = np.zeros(n, dtype=bool)
    idx = np.nonzero(presel)[0]
    if idx.size == 0:
        return keep

    run, lumi, event = d["run"][idx], d["lumi"][idx], d["event"][idx]
    dmz1 = np.abs(d["mZ1"][idx] - M_Z)
    z2 = d["lep_zId"][idx] == 2
    z2_sumpt = np.sum(np.where(z2, d["lep_pt"][idx], 0.0), axis=1)

    # Build a composite event key and a sort that puts the best candidate first
    # within each event: sort by (event-key, dmz1 asc, -z2_sumpt).
    ev_key = (
        run.astype(np.int64) * np.int64(10_000_000_000)
        + lumi.astype(np.int64) * np.int64(1_000_000_000)
        + event.astype(np.int64)
    )
    order = np.lexsort((-z2_sumpt, dmz1, ev_key))
    ev_sorted = ev_key[order]
    # First occurrence of each event key in the sorted order is the best cand.
    first = np.ones(len(order), dtype=bool)
    first[1:] = ev_sorted[1:] != ev_sorted[:-1]
    best_local = order[first]
    keep[idx[best_local]] = True
    return keep


def channel_of(d: dict) -> np.ndarray:
    """Per-candidate channel string from finalState (0=4mu,1=4e,2=2e2mu)."""
    fs = d["finalState"]
    out = np.empty(len(fs), dtype=object)
    for code, name in CHANNEL.items():
        out[fs == code] = name
    return out.astype(str)
