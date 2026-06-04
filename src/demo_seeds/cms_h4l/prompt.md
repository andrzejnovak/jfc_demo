# Analysis Prompt: H→4ℓ Mass Measurement with CMS Open Data

**Title:** H⇒4L Mass measurement with CMS Open Data
**Type:** measurement (extraction — mass + signal strength μ)
**Date logged:** 2026-06-03

## Physics goal

Perform a Higgs boson measurement in the 4-lepton (electron or muon) decay
channel using CMS Open Data from 2017 at √s = 13 TeV. The final state is
**4e**, **4μ**, or **2e2μ** arising from a pair of Z bosons (one on-shell,
one off-shell) — H → ZZ* → 4ℓ — with loosely isolated leptons ideally from a
Higgs decay.

Deliverables:
1. Distributions of key observables — particularly the **4-lepton invariant
   mass** — with a clean selection of Higgs candidate events, showing the
   Higgs signal on top of SM backgrounds.
2. A **fit of the 4-lepton mass** and extraction of the **signal strength μ**.
3. Mass-extraction code and μ-extraction fit code that are **easy to
   reproduce** from this setup.

Loosely follows the official CMS publication **JHEP 11 (2017) 047**
(arXiv:1706.09936).

## Scope directives (from the requester)

- **Fake/non-prompt lepton background:** use Drell-Yan+jets MC only
  (DYJetsToLL). Do NOT build a data-driven fake-rate estimate.
- **Systematics to SKIP:** lepton efficiency and trigger efficiency
  uncertainties. Do not spend effort on these now.
- **Systematics to FOCUS on:** overall background normalizations with
  reasonable uncertainties.
- Emphasis: a good selection, plus extraction of the mass and μ values.
- **Keep it quick.** Cut the exploration steps (Phases 1 and 2) short.
  Reviews need not be exhaustive.
- **Analysis note:** does not need the usual depth — **under 20 pages is
  fine**. Convey the main idea.

## Inputs

Flat ntuples produced by `h4l_ntuplize.py` run over CMS Open Data NANOAOD,
located in `data/`.

| Sample | File | Cross section (pb) | Role |
|--------|------|--------------------|------|
| Data (10/fb) | `data_secret_10fb.root` | — | 2017 data, 10 fb⁻¹ |
| ggH→ZZ→4ℓ | `GluGluToHToZZ.root` | 0.00602392 | Signal (ggF) |
| VBF H→ZZ→4ℓ | `VBF_HToZZ.root` | 0.00048794 | Signal (VBF) |
| ZH→ZZ→4ℓ | `ZHToZZ.root` | 0.000098394 | Signal (ZH) |
| W+H→ZZ→4ℓ | `WPHToZZ.root` | 0.0001072352 | Signal (WH) |
| W−H→ZZ→4ℓ | `WMHToZZ.root` | 0.0000670716 | Signal (WH) |
| ZZ→4ℓ (qq) | `ZZTo4L.root` | 1.325 | Irreducible bkg (qqZZ) |
| DY+jets | `DYJetsToLL.root` | 5396.0 | Reducible bkg (M-50) |
| tt̄→2ℓ | `TTBar.root` | 52.70 | Reducible bkg |
| ggZZ→2e2μ | `GGZZ2E2Mu.root` | 0.003185 | Irreducible bkg (ggZZ) |
| ggZZ→4e | `GGZZ4E.root` | 0.001575 | Irreducible bkg (ggZZ) |
| ggZZ→4μ | `GGZZ4Mu.root` | 0.001619 | Irreducible bkg (ggZZ) |

Integrated luminosity: **10 fb⁻¹** (per data sample name).
