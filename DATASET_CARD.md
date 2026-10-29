# Dataset card: civil-answer-checks v1

**Origin:** 12 original synthetic prompts authored with AI assistance for this portfolio, October 2026.
**License:** MIT, like the rest of this repository. No employer/client material is present.
**Purpose:** demonstrate case schemas, numerical checks, abstention, traceability and manual evaluation.
**Not intended for:** model ranking, hiring decisions, compliance determination or design approval.

There are 8 development and 4 demonstration holdout cases. Nine require a numeric result;
three require abstention. Cases cover runoff, unit conversion, average-end-area quantities,
pipe crown cover and missing design information. Prompts state the method or information gap.

Reference values come from direct arithmetic documented in each row. The answer fixture includes
six deliberately introduced failures, including a fabricated citation ID; it was not obtained from a model.
The equivalent `480 L/s` answer for H01 is intentionally accepted as `0.48 m3/s`.

There is no personal data, geographic data, external training corpus or scraped answer set.
Sources use local `SYN-` identifiers defined in [the source pack](data/source_pack.md).
They are teaching notes, not real standards. Links in that pack provide method background only.

## Limitations

The dataset is tiny, English-only, mostly arithmetic and hand-constructed. The public holdout is
related to the development tasks. It contains no full drawings, complex networks, ambiguous
multi-document reasoning or verified independent human labels. No statistical confidence interval
or broad model capability claim is justified. Future evaluations need independently reviewed cases,
stronger coverage, blinded human review and a fresh held-out set.
