# Eval results: heldout set

20 queries (4 per slice), 5,065 titles, top 10 results per query. Baseline: `keyword_meta`. Regenerate with `python -m evals.run`.

## Overall

| System | NDCG@10 | Recall@10 | MRR@10 | Hit@1 | Empty result pages | Judged@10 |
|---|---|---|---|---|---|---|
| `keyword_meta` | 0.512 | 0.540 | 0.660 | 0.500 | 0 of 20 | 100% |
| `keyword_full` | 0.637 | 0.705 | 0.725 | 0.600 | 0 of 20 | 100% |
| `semantic` | 0.383 | 0.440 | 0.545 | 0.400 | 0 of 20 | 100% |
| `hybrid` | 0.525 | 0.575 | 0.672 | 0.600 | 0 of 20 | 100% |
| `keyword_pinned` | 0.641 | 0.710 | 0.725 | 0.600 | 0 of 20 | 100% |
| `hybrid_pinned` | 0.620 | 0.680 | 0.722 | 0.650 | 0 of 20 | 100% |

## NDCG@10 by intent slice

| System | navigational | person | category | descriptive | vibe |
|---|---|---|---|---|---|
| `keyword_meta` | 0.985 | 0.967 | 0.523 | 0.000 | 0.085 |
| `keyword_full` | 0.987 | 0.982 | 0.619 | 0.207 | 0.391 |
| `semantic` | 0.750 | 0.274 | 0.539 | 0.000 | 0.350 |
| `hybrid` | 0.750 | 0.778 | 0.658 | 0.000 | 0.440 |
| `keyword_pinned` | 0.987 | 1.000 | 0.619 | 0.207 | 0.391 |
| `hybrid_pinned` | 1.000 | 1.000 | 0.658 | 0.000 | 0.440 |

## Hit@1 by intent slice

| System | navigational | person | category | descriptive | vibe |
|---|---|---|---|---|---|
| `keyword_meta` | 1.000 | 1.000 | 0.500 | 0.000 | 0.000 |
| `keyword_full` | 1.000 | 1.000 | 0.500 | 0.250 | 0.250 |
| `semantic` | 0.750 | 0.250 | 0.500 | 0.000 | 0.500 |
| `hybrid` | 0.750 | 1.000 | 0.500 | 0.000 | 0.750 |
| `keyword_pinned` | 1.000 | 1.000 | 0.500 | 0.250 | 0.250 |
| `hybrid_pinned` | 1.000 | 1.000 | 0.500 | 0.000 | 0.750 |

## Change in NDCG@10 against `keyword_meta`

Mean difference with a 95% paired bootstrap interval (10,000 resamples of the queries). An interval that includes zero is not a result.

| System | all | navigational | person | category | descriptive | vibe | Wins / losses / ties |
|---|---|---|---|---|---|---|---|
| `keyword_full` | +0.125 [+0.040, +0.230] | +0.002 [+0.000, +0.005] | +0.015 [+0.000, +0.029] | +0.096 [+0.000, +0.192] | +0.207 [+0.000, +0.620] | +0.306 [+0.157, +0.454] | 10 / 0 / 10 |
| `semantic` | -0.129 [-0.320, +0.042] | -0.235 [-0.750, +0.045] | -0.693 [-0.905, -0.480] | +0.016 [-0.105, +0.126] | +0.000 [+0.000, +0.000] | +0.265 [+0.059, +0.521] | 7 / 6 / 7 |
| `hybrid` | +0.013 [-0.136, +0.146] | -0.235 [-0.750, +0.045] | -0.189 [-0.361, -0.017] | +0.135 [+0.032, +0.239] | +0.000 [+0.000, +0.000] | +0.355 [+0.130, +0.581] | 8 / 4 / 8 |
| `keyword_pinned` | +0.129 [+0.045, +0.233] | +0.002 [+0.000, +0.005] | +0.033 [+0.000, +0.082] | +0.096 [+0.000, +0.192] | +0.207 [+0.000, +0.620] | +0.306 [+0.157, +0.454] | 10 / 0 / 10 |
| `hybrid_pinned` | +0.108 [+0.039, +0.194] | +0.015 [+0.000, +0.045] | +0.033 [+0.000, +0.082] | +0.135 [+0.032, +0.239] | +0.000 [+0.000, +0.000] | +0.355 [+0.130, +0.581] | 10 / 0 / 10 |

## Head to head: `hybrid_pinned` vs `keyword_pinned`

Change in NDCG@10, same interval method.

| all | navigational | person | category | descriptive | vibe | Wins / losses / ties |
|---|---|---|---|---|---|---|
| -0.021 [-0.121, +0.045] | +0.013 [+0.000, +0.040] | +0.000 [+0.000, +0.000] | +0.039 [+0.012, +0.059] | -0.207 [-0.620, +0.000] | +0.050 [-0.092, +0.184] | 7 / 2 / 11 |

## Gates (see gates.yaml)

| System | beats_baseline | title_lookup_guardrail | person_lookup_guardrail | Eligible for A/B |
|---|---|---|---|---|
| `keyword_full` | pass (+0.040) | pass (+0.000) | pass (+0.015) | yes |
| `semantic` | FAIL (-0.320) | FAIL (-0.250) | FAIL (-0.693) | no |
| `hybrid` | FAIL (-0.136) | FAIL (-0.250) | FAIL (-0.189) | no |
| `keyword_pinned` | pass (+0.045) | pass (+0.000) | pass (+0.033) | yes |
| `hybrid_pinned` | pass (+0.039) | pass (+0.000) | pass (+0.033) | yes |
