# Engineering answer evaluation

**Synthetic fixture — not a benchmark of a model.**

| Split | Cases | Answers present | Task result passes | All structural checks pass |
|---|---:|---:|---:|---:|
| all | 12 | 12 | 8 | 6 |
| development | 8 | 8 | 5 | 4 |
| holdout | 4 | 4 | 3 | 2 |

| Case | Result | Findings | Human review |
|---|---|---|---|
| D01 | Structural checks pass | None detected by these checks | Required |
| D02 | Needs correction | NUMERIC_ERROR | Required |
| D03 | Structural checks pass | None detected by these checks | Required |
| D04 | Needs correction | NUMERIC_ERROR | Required |
| D05 | Needs correction | UNSUPPORTED_RESULT_ON_INSUFFICIENT_INFORMATION | Required |
| D06 | Structural checks pass | None detected by these checks | Required |
| D07 | Needs correction | MISSING_OR_UNKNOWN_CITATION_ID | Required |
| D08 | Structural checks pass | None detected by these checks | Required |
| H01 | Structural checks pass | None detected by these checks | Required |
| H02 | Needs correction | EMPTY_REASONING | Required |
| H03 | Structural checks pass | None detected by these checks | Required |
| H04 | Needs correction | UNSUPPORTED_RESULT_ON_INSUFFICIENT_INFORMATION | Required |

Citation matching checks identifiers only; it does not validate whether a source supports the answer. Reasoning is checked for presence, not correctness.
