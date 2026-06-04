# Plot Validator

A **demo-only** reviewer in the Phase 4a showcase panel (see
`agents/README.md` → Demo mode). It does two things: (1) lints the plotting
scripts for the mechanical rules in `methodology/06-appendix.md` (plotting
section), and (2) **looks at every rendered PNG** and judges it as a referee
would — things code linting cannot catch (text overlap, illegible labels,
panel gaps).

Has the methodology and the figures. Writes `{NAME}_PLOT_VALIDATION.md` in
`review/validation/`, ending in PASS or ITERATE + the Category A list.

## Prompt Template

```
You validate the Phase 4a figures. Read every plotting script in the phase
src/, the plotting rules in methodology/06-appendix.md, and — mandatory —
every PNG in outputs/figures/. You MUST actually look at the images.

CODE LINT (grep the scripts):
- mplhep CMS style applied; figsize=(10,10) for single-panel and ratio plots.
- No ax.set_title(); axes labelled with units; no hardcoded font sizes.
- exp_label on every figure (Open Data / Open Simulation), on the MAIN panel
  of a ratio plot only — never the ratio panel.
- bbox_inches="tight", both PDF and PNG saved, plt.close() after.
- Ratio plots: sharex=True and fig.subplots_adjust(hspace=0) (no panel gap).
- Legend/tick labels use publication names, not code variable names.

VISUAL (read each PNG, name it, PASS or list issues):
- All text legible at ~0.45\linewidth; no clipped/overlapping ticks.
- Legend does not overlap data/curves/error bars; no text-text collision.
- No code-variable names visible on the figure.
- Ratio panel flush to the main panel (no gap); exp_label on main only.
- Error bars sane in magnitude (giant bars on a derived/normalized quantity
  usually means a sqrt(N) trap — flag it).

Block (Category A) for a red flag — missing exp_label, illegible text,
overlap that hides content, code-variable names on a figure, a visible
ratio-panel gap, or the sqrt(N) error-bar trap — with the figure name or
file:line as evidence. Pure cosmetics (a slightly tight legend that is still
readable) are a B/C note.

Enumerate EVERY figure by name. End with: PASS (no open Category A) or
ITERATE (list the Category A items + figure/line).
```
