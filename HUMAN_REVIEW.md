# Human evaluation rubric

Automated findings are evidence for review, not the final verdict. Review every answer, including
structural passes. Use `templates/human_review.csv`; do not fill scores without reading the answer.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Reasoning | Wrong or unsupported method | Correct direction, missing a material step | Correct method, units and reproducible steps |
| Evidence | Fabricated or irrelevant support | Relevant ID but incomplete support | Cited note directly supports the claim |
| Assumptions | Invents inputs or approval | Mentions uncertainty but misses a key gap | Explicit assumptions; asks for needed information |
| Communication | Misleading or unusable | Understandable but incomplete | Clear result, units and limits |

A fabricated authority, invented design input or ungrounded approval is a critical error regardless
of total score. Mark `critical_error=yes`, explain it, and set final disposition to `reject`.
Use `needs_revision` for correctable omissions and `acceptable_for_demo` only after full review.
No rating authorizes engineering use.

For a real study, blind the reviewer to model identity, use two independent reviewers on a common
sample, record disagreements, and agree on adjudication rules before reading results. Report the
sample size and missing-output count alongside any aggregate score. Do not claim reviewer agreement
unless it was measured. The template is blank because no independent human review has occurred.
