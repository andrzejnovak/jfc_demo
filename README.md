# jfc_demo

Run an autonomous HEP analysis end-to-end with an AI agent: a **H → ZZ\* → 4ℓ
Higgs mass + signal-strength (μ) measurement** on CMS Open Data, using the **JFC**
multi-agent framework.

This is the *fast* demo: the deterministic setup (strategy, exploration, citations,
code skeletons) is pre-baked, so the live run is **~45–55 min** and opens straight on
the interesting parts — building the fit, review catching a real bug, a data/MC
regression at a human gate, and writing the note.

## step 0 — install Claude Code and Pixi
```
curl -fsSL https://claude.ai/install.sh | bash    # needs Claude Pro ($20/mo) or an API key
curl -fsSL https://pixi.sh/install.sh | sh
```

## step 1 — get the repo
```
git clone https://github.com/andrzejnovak/jfc_demo
cd jfc_demo
pixi install
```

## step 2 — scaffold the demo (drops in the pre-baked seed)
```
pixi run scaffold analyses/cms_h4l --type measurement --demo cms_h4l
```

## step 3 — download the data (~866 MB, hosted separately)
```
DATA_URL=<host-url> bash scripts/fetch_data.sh     # downloads into analyses/cms_h4l/data/
```
Then point the analysis at it: set `data_dir=` to that folder in
`analyses/cms_h4l/.analysis_config`.

## step 4 — check and run
```
cd analyses/cms_h4l
pixi install
pixi run py verify_seed.py     # must print PASS (confirms the seed matches your data)
cat prompt.md | claude         # the agent takes it from here
```

That's it. Phases 1–2 are adopted from the seed; Phases 3–5 run live. The demo
deliberately contains three issues the agents catch on their own — a fit-uncertainty
bug (review), an un-normalized background (regression + human gate after the 10%
check), and a citation slip (bibtex validator). Details:
[`src/demo_seeds/cms_h4l/SEED_MANIFEST.md`](src/demo_seeds/cms_h4l/SEED_MANIFEST.md).

---

The full JFC framework spec lives in [`src/`](src/) (methodology, conventions, agents,
templates). No data is stored in git. Background:
*AI Agents Can Already Autonomously Perform Experimental High Energy Physics*
(Moreno, Bright-Thonney, Novak, Garcia, Harris).
