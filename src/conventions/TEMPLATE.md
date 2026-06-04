<!-- Skeleton for spec developers creating a new conventions file. Agents
     ignore it — it contains no analysis requirements. See unfolding.md,
     extraction.md, or search.md for actual conventions. Keep new files
     lean: the required-systematic tables and validation checks are the
     load-bearing content; trim prose. -->

# [Technique Name]

Conventions for analyses that [one-sentence description].

## When this applies
[When this file is relevant — technique, observable type, detector config. Note which other conventions file applies if this one does not.]

## Standard configuration
[Default settings/parameters/definitions analyses of this type adopt unless justified otherwise.]

## Required systematic sources
Group by category (detector/reconstruction, method-specific, theory). Each: source — what to vary — rationale.

## Required validation checks
Enumerated pass/fail checks. Each: what is tested, what constitutes a pass (with the threshold), and what to do on failure (mark Category A where it blocks).

## Pitfalls
- **[Name].** [The mistake, why it happens, how to avoid it.]

## References
[Published analyses / methodology papers that define or motivate these conventions.]
