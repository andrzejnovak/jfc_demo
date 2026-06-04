# Cited Constants and Systematic Magnitudes (pre-sourced)

This table provides the curated, **pre-sourced and cited** numeric constants
and systematic-uncertainty magnitudes used by this H→4ℓ demo analysis. It
exists to satisfy the root **"Numeric Constants: Never From Memory"** rule
*without* every executor re-fetching the same magnitudes from the web on
every run.

**How to use it (executors).** When you need any quantity below, take the
value from this table and **cite the listed `bibkey`** (which resolves
against `references.bib`). Do **not** re-source these magnitudes from the
web — they are already sourced here. This keeps the live act fast and
deterministic.

**What this table does NOT do.** It does **not** exempt the analysis from
citation validation. The BibTeX validator STILL independently verifies
every `references.bib` entry at the documentation phase (correct DOI/eprint,
title, authors, resolvable). This file is an internal sourcing convenience,
not a substitute for the bibliography or its validation. Every `bibkey`
used here must have a corresponding, validated `references.bib` entry.

**When these numbers must be re-derived.** The systematic *magnitudes*
below are tied to **this dataset and this selection**. If the dataset, the
event selection, or the background estimation method changes, the affected
magnitudes (especially the data-driven reducible background and any
normalization uncertainties) must be **re-derived from the new
measurement**, not carried over. The PDG masses are dataset-independent;
the systematic percentages are not. A magnitude reused after a selection
change without re-derivation is a Category A finding at review.

**Provenance.** All magnitudes below are the sourced values from the
completed reference run of this analysis. Each row names the originating
paper/PAS and the `bibkey` to cite.

---

## Particle masses (PDG 2024)

| quantity | value | source (paper/PAS) | bibkey | notes |
|----------|-------|--------------------|--------|-------|
| Higgs boson mass $m_H$ | 125.20 GeV | PDG 2024, Navas et al., Phys. Rev. D 110, 030001 (doi:10.1103/PhysRevD.110.030001) | `PDG_2024` | Gauge & Higgs boson summary table. Dataset-independent. Used for the signal lineshape mean. |
| Z boson mass $m_Z$ | 91.1876 GeV | PDG 2024, Navas et al., Phys. Rev. D 110, 030001 (doi:10.1103/PhysRevD.110.030001) | `PDG_2024` | Z summary table. Dataset-independent. Used for the Z mass window / on-shell pairing. |

## Signal theory uncertainties (ggF H→ZZ→4ℓ)

| quantity | value | source (paper/PAS) | bibkey | notes |
|----------|-------|--------------------|--------|-------|
| ggF signal QCD scale | +4.6% / −6.7% | LHC Higgs WG Yellow Report 4, arXiv:1610.07922 (de Florian et al., CERN-2017-002-M) | `LHCHWG_YR4` | Asymmetric scale variation on the ggF inclusive cross section at $m_H$ = 125 GeV, 13 TeV. |
| ggF signal PDF + $\alpha_s$ | ≈ 3.2% | LHC Higgs WG Yellow Report 4, arXiv:1610.07922 (de Florian et al., CERN-2017-002-M) | `LHCHWG_YR4` | PDF⊕$\alpha_s$ component, combined in quadrature with the scale uncertainty for the total signal theory normalization. |

## Background normalization uncertainties

| quantity | value | source (paper/PAS) | bibkey | notes |
|----------|-------|--------------------|--------|-------|
| qqZZ (qq→ZZ) normalization | 10% | NLO QCD scale + PDF, MCFM, arXiv:1706.09936 | `CMS_H4l_2017` | Combined NLO QCD scale and PDF uncertainty on the irreducible qq→ZZ continuum normalization, per the CMS H→4ℓ analysis. |
| ggZZ (gg→ZZ) normalization | 10% | Caola, Melnikov, Röntsch, Tancredi, arXiv:1509.06734 | `Caola_ggZZ` | Residual K-factor uncertainty for gg→ZZ from the NNLO calculation (≈10% on the residual). |
| DY + tt̄ reducible background | 40% | CMS Z+X data-driven estimate, arXiv:1706.09936 | `CMS_H4l_2017` | Uncertainty on the data-driven reducible (Z+X: Drell–Yan + tt̄) background. Dataset/selection-dependent — re-derive from the fake-rate/sideband measurement if selection changes. |

## Detector / instrumental uncertainties

| quantity | value | source (paper/PAS) | bibkey | notes |
|----------|-------|--------------------|--------|-------|
| Integrated luminosity | 2.3% | CMS-PAS-LUM-17-004 (2017 data-taking, 13 TeV) | `CMS_LUM_17_004` | Integrated-luminosity uncertainty, applied to all MC-normalized yields. |
| Lepton momentum scale on $m_{4\ell}$ | 0.1% | CMS H→4ℓ mass measurement, arXiv:1910.09607 | `CMS_H4l_mass_2019` | Lepton momentum/energy scale propagated to the four-lepton invariant mass. Affects the signal peak position. |

---

## Notes on combination

- The **total signal theory** normalization uncertainty combines the ggF
  QCD scale (asymmetric, +4.6/−6.7%) with PDF⊕$\alpha_s$ (≈3.2%) in
  quadrature, per the Yellow Report 4 prescription (`LHCHWG_YR4`).
- The **reducible background** (40%, `CMS_H4l_2017`) is the dominant
  background normalization uncertainty and is the magnitude most sensitive
  to selection changes — treat it as the canonical re-derivation trigger.
- All percentages are relative uncertainties unless otherwise noted.
