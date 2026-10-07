# Eval results: dev set

40 queries (8 per slice), 5,065 titles, top 10 results per query. Baseline: `keyword_meta`. Regenerate with `python -m evals.run`.

## Overall

| System | NDCG@10 | Recall@10 | MRR@10 | Hit@1 | Empty result pages | Judged@10 |
|---|---|---|---|---|---|---|
| `keyword_meta` | 0.442 | 0.456 | 0.583 | 0.450 | 1 of 40 | 100% |
| `keyword_full` | 0.658 | 0.683 | 0.813 | 0.600 | 1 of 40 | 100% |
| `semantic` | 0.441 | 0.509 | 0.661 | 0.400 | 0 of 40 | 100% |
| `hybrid` | 0.607 | 0.692 | 0.785 | 0.525 | 0 of 40 | 100% |
| `keyword_pinned` | 0.667 | 0.683 | 0.813 | 0.650 | 1 of 40 | 100% |
| `hybrid_pinned` | 0.673 | 0.730 | 0.820 | 0.650 | 0 of 40 | 100% |

## NDCG@10 by intent slice

| System | navigational | person | category | descriptive | vibe |
|---|---|---|---|---|---|
| `keyword_meta` | 0.824 | 0.972 | 0.330 | 0.010 | 0.073 |
| `keyword_full` | 0.785 | 1.000 | 0.715 | 0.640 | 0.149 |
| `semantic` | 0.598 | 0.335 | 0.403 | 0.605 | 0.264 |
| `hybrid` | 0.703 | 0.812 | 0.639 | 0.608 | 0.270 |
| `keyword_pinned` | 0.833 | 1.000 | 0.715 | 0.640 | 0.149 |
| `hybrid_pinned` | 0.858 | 0.989 | 0.639 | 0.608 | 0.270 |

## Hit@1 by intent slice

| System | navigational | person | category | descriptive | vibe |
|---|---|---|---|---|---|
| `keyword_meta` | 0.750 | 1.000 | 0.500 | 0.000 | 0.000 |
| `keyword_full` | 0.500 | 1.000 | 0.875 | 0.625 | 0.000 |
| `semantic` | 0.250 | 0.500 | 0.375 | 0.625 | 0.250 |
| `hybrid` | 0.250 | 0.875 | 0.875 | 0.500 | 0.125 |
| `keyword_pinned` | 0.750 | 1.000 | 0.875 | 0.625 | 0.000 |
| `hybrid_pinned` | 0.750 | 1.000 | 0.875 | 0.500 | 0.125 |

## Change in NDCG@10 against `keyword_meta`

Mean difference with a 95% paired bootstrap interval (10,000 resamples of the queries). An interval that includes zero is not a result.

| System | all | navigational | person | category | descriptive | vibe | Wins / losses / ties |
|---|---|---|---|---|---|---|---|
| `keyword_full` | +0.216 [+0.118, +0.326] | -0.038 [-0.099, +0.011] | +0.028 [+0.000, +0.069] | +0.385 [+0.198, +0.576] | +0.629 [+0.346, +0.882] | +0.076 [+0.022, +0.139] | 22 / 5 / 13 |
| `semantic` | -0.001 [-0.161, +0.158] | -0.225 [-0.503, +0.025] | -0.637 [-0.793, -0.499] | +0.073 [-0.090, +0.217] | +0.595 [+0.310, +0.854] | +0.191 [+0.063, +0.333] | 19 / 16 / 5 |
| `hybrid` | +0.165 [+0.049, +0.285] | -0.121 [-0.327, +0.072] | -0.159 [-0.265, -0.066] | +0.310 [+0.152, +0.476] | +0.598 [+0.329, +0.837] | +0.196 [+0.105, +0.293] | 22 / 11 / 7 |
| `keyword_pinned` | +0.226 [+0.128, +0.335] | +0.009 [-0.067, +0.082] | +0.028 [+0.000, +0.069] | +0.385 [+0.198, +0.576] | +0.629 [+0.346, +0.882] | +0.076 [+0.022, +0.139] | 24 / 4 / 12 |
| `hybrid_pinned` | +0.231 [+0.138, +0.331] | +0.034 [-0.105, +0.166] | +0.017 [+0.000, +0.042] | +0.310 [+0.152, +0.476] | +0.598 [+0.329, +0.837] | +0.196 [+0.105, +0.293] | 27 / 2 / 11 |

## Head to head: `hybrid_pinned` vs `keyword_pinned`

Change in NDCG@10, same interval method.

| all | navigational | person | category | descriptive | vibe | Wins / losses / ties |
|---|---|---|---|---|---|---|
| +0.006 [-0.036, +0.048] | +0.025 [-0.061, +0.135] | -0.011 [-0.034, +0.000] | -0.075 [-0.156, -0.017] | -0.031 [-0.135, +0.037] | +0.121 [+0.027, +0.214] | 12 / 11 / 17 |

## Gates (see gates.yaml)

| System | beats_baseline | title_lookup_guardrail | person_lookup_guardrail | Eligible for A/B |
|---|---|---|---|---|
| `keyword_full` | pass (+0.118) | FAIL (-0.250) | pass (+0.029) | no |
| `semantic` | FAIL (-0.161) | FAIL (-0.500) | FAIL (-0.637) | no |
| `hybrid` | pass (+0.049) | FAIL (-0.500) | FAIL (-0.159) | no |
| `keyword_pinned` | pass (+0.128) | pass (+0.000) | pass (+0.029) | yes |
| `hybrid_pinned` | pass (+0.138) | pass (+0.000) | pass (+0.017) | yes |
