# jfc_demo

A fast, self-contained **demo of [JFC](#about-jfc)** — an autonomous multi-agent
framework for high-energy-physics analysis. This repo runs one end-to-end analysis
live: a **H → ZZ\* → 4ℓ Higgs-boson mass and signal-strength (μ) measurement** on
CMS Open Data (2017, √s = 13 TeV).

It uses JFC's **fast demo mode**: the deterministic setup (strategy, data
exploration, citations, code skeletons) ships **pre-baked** as a "cold open," so the
demo opens directly on the *interesting* part — building the fit, catching a real
bug in review, handling a data/MC regression at the human gate, and writing the
note. Live runtime is **~45–55 min** instead of the ~4.5–5 h of a from-scratch run.

> **Data is a separate download** — see [Get the data](#2-get-the-data). No ROOT
> files are stored in this repo.

---

## What the demo showcases

A single physics prompt drives the whole pipeline. The orchestrator never writes
code — it delegates to specialized subagents and gates each phase on an on-disk
artifact + independent review. With fast mode, **Phases 1–2 are validated-and-adopted
from the seed**, and the live act runs **Phase 3 → 4a → 4b (human gate) → 4c → 5**.

The demo deliberately contains **three planted-but-organic issues** so you can watch
the review/regression layers earn their place (all documented in
[`src/demo_seeds/cms_h4l/SEED_MANIFEST.md`](src/demo_seeds/cms_h4l/SEED_MANIFEST.md)):

| # | Planted issue | Caught by |
|---|---------------|-----------|
| 1 | A σ_μ uncertainty **double-count** in the fit skeleton | the **Phase 4a review** (re-derives ~0.51 vs the buggy ~0.72) |
| 2 | The qq→ZZ background is **not data-normalized** (~2× over-prediction at the on-shell Z→4ℓ peak) | the **Phase 4b** control-region anchor → investigator → **regression + human gate** |
| 3 | One **citation slip** in `references.bib` (a Yellow-Report-4 entry pointing to the wrong arXiv ID) | the **BibTeX validator** at the documentation phase |

If the demo runs correctly, all three are surfaced by the agents — not by you.

---

## Quick start

### 0. Prerequisites
- [pixi](https://pixi.sh) (environment management)
- [Claude Code](https://claude.com/claude-code) (the agent runtime)

### 1. Clone & install the scaffolder env
```bash
git clone https://github.com/andrzejnovak/jfc_demo
cd jfc_demo
pixi install
```

### 2. Get the data
The ntuples (~866 MB, produced from CMS Open Data NANOAOD) are distributed
**separately**. Point the fetch script at the download location and run it:
```bash
# set DATA_URL to where the ntuples are hosted (or edit scripts/fetch_data.sh)
DATA_URL=https://<your-host>/jfc_demo_data bash scripts/fetch_data.sh
```
This downloads the 12 ROOT files (listed in the script header, with cross sections)
into `analyses/cms_h4l/data/` and checks their sizes.

### 3. Scaffold the demo analysis (drops in the pre-baked seed)
```bash
pixi run scaffold analyses/cms_h4l --type measurement --demo cms_h4l
```
This creates the analysis directory and overlays the `cms_h4l` seed: the
pre-reviewed Phase-1/2 artifacts, `references.bib`, the selection/fit **skeletons**,
`verify_seed.py`, and `SEED_MANIFEST.md`, and sets `demo_seed=cms_h4l` in
`.analysis_config`. (You can run this before or after step 2 — the fetch script
creates `analyses/cms_h4l/data/` if needed.)

### 4. Set the data path & install the analysis env
```bash
cd analyses/cms_h4l
# edit .analysis_config → data_dir=/abs/path/to/jfc_demo/analyses/cms_h4l/data
pixi install
pixi run py verify_seed.py     # determinism guard: confirms the seed matches your data
```
`verify_seed.py` must print **PASS** before you start — it confirms the pre-baked
schema/weights still match the ROOT files you downloaded.

### 5. Run the demo
```bash
claude
```
The orchestrator reads the seeded prompt, validates-and-adopts Phases 1–2, then runs
Phases 3–5 live. Watch for the three catches above and the human gate after Phase 4b.

---

## About JFC

JFC ("Just Furnish Context") is a proof-of-concept framework for autonomous HEP
analysis: a structured methodology (planning → exploration → selection → statistical
analysis → paper drafting) with tiered multi-agent review and a human gate. The full
specification lives in [`src/`](src/):

```
src/
  methodology/         Full spec: phases, review, orchestration, blinding, appendices
  conventions/         Domain knowledge (HEP tools, plotting, technique conventions, cited_constants)
  agents/              Subagent role definitions (executor, reviewers, arbiter, typesetter, ...)
  templates/           root + per-phase CLAUDE.md and pixi.toml templates
  demo_seeds/cms_h4l/  The pre-baked "cold open" for this demo (see its SEED_MANIFEST.md)
  scaffold_analysis.py Scaffolder (supports --demo)
```

Fast demo mode is documented in `src/templates/root_claude.md` ("Fast Demo Mode")
and realized by `scaffold_analysis.py --demo <name>` + `src/demo_seeds/<name>/`.

For the science behind JFC:
> *AI Agents Can Already Autonomously Perform Experimental High Energy Physics*
> E. A. Moreno, S. Bright-Thonney, A. Novak, D. Garcia, P. Harris

---

## Notes for testers

- **No data in git.** `.gitignore` blocks `*.root`, `/data/`, and `analyses/` — please
  keep it that way; the `data_secret_*` file in particular must not be committed.
- Each scaffolded analysis is its **own git repo** under `analyses/` (gitignored here).
- Re-running `scaffold --demo` is idempotent and never overwrites your edits.
- The full set of intentional planted items and the fast-mode rationale are in the
  seed's `SEED_MANIFEST.md`.
