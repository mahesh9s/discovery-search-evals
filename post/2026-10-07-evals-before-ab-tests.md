---
layout: post
title: "The eval that told me not to A/B test my own POC"
description: "A 60-query golden set, three ship gates, and a semantic search candidate that tied the baseline for all the wrong reasons."
date: 2026-10-07
tags: [evals, search, product-management, ai]
---

I build search and recommendation products for streaming services. The most expensive habit I see on AI projects is the jump from a demo that looks great straight to a request for an A/B test. An A/B slot costs weeks of traffic and answers one question. An offline eval costs very little and tells you which question deserves those weeks.

This post is one eval, start to finish, on a POC that looked like an obvious win. It was not. Everything is in a [public repo](https://github.com/mahesh9s/discovery-search-evals) that reruns in seconds: the catalog, the queries, the judgments, the gates and the code.

## The POC

The feature is a search bar that understands requests like "something scary but not gory" or "rat who wants to be a chef in paris". The catalog is 5,065 films from a public Wikipedia dataset. The baseline is what catalog search usually is: keyword matching on title, cast and genre. The candidate is embedding retrieval over each film's synopsis.

I used a deliberately small embedding model (WordLlama, 16 MB, runs on a CPU) so anyone can reproduce the numbers without a GPU or an API key. Keep that in mind throughout. This is a verdict on one candidate, not on embeddings.

## 1. Decide what good means before running anything

Two files existed before the first score did.

**The golden set.** Forty queries, eight for each of five intents, typed the way people type them.

| Intent | Example query | A good answer |
|---|---|---|
| Navigational | `the dark knight` | That film, first |
| Person | `movies with florence pugh` | Her films |
| Category | `found footage horror` | The sub-genre |
| Descriptive | `rat who wants to be a chef in paris` | Ratatouille |
| Vibe | `movies that will make me cry` | Tearjerkers |

Each query has a one-line rubric, and every result is graded 0, 1 or 2 against it. To grade, I pooled the top 10 from every system, shuffled them and stripped the system names, so the grader could not tell which system produced which result. A first pass of the grading was done with an LLM, and I reviewed the grades against the rubrics. The set ended up with 2,241 judgments.

**The gates.** Three rules in a [YAML file](https://github.com/mahesh9s/discovery-search-evals/blob/main/gates.yaml) that a candidate must clear to earn an online test:

1. Beat the baseline on NDCG@10, with the whole 95% confidence interval above zero.
2. Never be worse than the baseline at putting the right film first when someone types a title.
3. Stay within 0.02 of the baseline on actor lookups.

For a PM, these two files are the real requirements document. The golden set says what users will ask and what a right answer looks like. The gates say what you refuse to trade away. Writing them first matters, because once you have seen results, every threshold starts to look negotiable.

## 2. The headline number was the least useful one

| System | NDCG@10 | Change vs baseline (95% interval) | Right title first | Gates |
|---|---|---|---|---|
| Baseline: keywords on title, cast, genre | 0.442 | | 75% | |
| Semantic POC | 0.441 | -0.001 [-0.161, +0.158] | 25% | fails 3 of 3 |
| Keywords with the synopsis indexed too | 0.658 | +0.216 [+0.118, +0.326] | 50% | fails 1 of 3 |
| Hybrid of the two | 0.607 | +0.165 [+0.049, +0.285] | 25% | fails 2 of 3 |

The semantic POC landed within 0.001 of the baseline. Had the review stopped at the average, the conclusion would have been "no effect".

![NDCG@10 by query intent for the baseline, the semantic POC and the candidate going to A/B](https://raw.githubusercontent.com/mahesh9s/discovery-search-evals/main/results/dev/ndcg_by_slice.png)

The slices show two large effects that cancel. On plot descriptions the baseline scores 0.01 and the POC scores 0.60. On actor names the baseline scores 0.97 and the POC scores 0.33. Asked for "movies with florence pugh", it returned Funny Games and The Purge.

Two more things in that table changed the project. The biggest gain came from the least exciting row: indexing the synopsis with the keyword engine that already existed. And nothing passed, because every candidate got worse at the most basic promise search makes. You type a title, you get that title.

## 3. Read the failures

Metrics tell you that something is wrong. Only reading the results tells you what. I took every query the hybrid candidate failed (20 of 40), read what it returned, and gave each one a root cause.

| Root cause | Queries | Example |
|---|---|---|
| Mood is not in the metadata | 7 | `movies that will make me cry` returns Cry Macho and Cry Wolf |
| The model does not know who people are | 5 | `amy adams`: none of the embedding's top 10 are her films |
| The right title is outranked | 4 | `the dark knight` returns The Dark Knight Rises first |
| Vocabulary gap | 3 | `courtroom drama`: the genre tag is "Legal" and 2 of 5,065 synopses say "courtroom" |
| Typo | 1 | `intersteller` gets an empty page from keyword search |

This table is the most valuable thing in the repo, because it sorts the problems by the kind of fix they need.

Nine of the 20 are known-item lookups: a title or a name. They do not need a model. One deterministic rule fixes eight of them: if the query is exactly a title or exactly an actor's name, pin those results to the top and let the ranker fill the rest of the page. The ninth, "spiderman" typed without its hyphen, needs fuzzy matching, the same as the typo.

Seven are requests for a feeling, and no ranker can fix those. A synopsis says who directed a film and what happens in it. It does not say the film is warm, or bleak, or fine to watch with a nine-year-old. The information is not in the catalog.

## 4. Rerun, then try to break the result

With the pinning rule in front of each ranker:

| System | NDCG@10 | Change vs baseline (95% interval) | Right title first | Gates |
|---|---|---|---|---|
| Keywords + synopsis + pinning | 0.667 | +0.226 [+0.128, +0.335] | 75% | passes |
| Hybrid + pinning | 0.673 | +0.231 [+0.138, +0.331] | 75% | passes |

Both pass. So the question changes from "does it beat the baseline" to the one that decides the roadmap: **once the cheap fixes are in, what does the model add?** Head to head, the hybrid leads the keyword version by +0.006, with an interval of [-0.036, +0.048]. That is nothing I can measure. It is better on vibe queries (+0.121) and worse on category queries (-0.075).

Then I tried to break it. I had changed the system after looking at these 40 queries, so their scores were no longer a fair test. I wrote 20 new queries, graded them the same way and ran everything once.

| | Development set (40) | Held-out set (20) |
|---|---|---|
| Keywords + synopsis + pinning, vs baseline | +0.226 [+0.128, +0.335] | +0.129 [+0.045, +0.233] |
| Hybrid + pinning, vs keywords + pinning | +0.006 [-0.036, +0.048] | -0.021 [-0.121, +0.045] |
| Semantic POC on descriptive queries (NDCG@10) | 0.60 | 0.00 |

The main result held. It is smaller, still clearly positive, and the guardrails are intact. The model's contribution was still indistinguishable from zero.

The slice I had been most pleased with did not hold. On four fresh plot descriptions the POC found none of the films. "Man who is born old and ages backwards" misses a synopsis that says "ages in reverse". Part of that 0.60 was luck in how I had phrased eight queries.

The new queries also surfaced a bug the first 40 never touched: `boxing movies` returns The Box and Black Box, because the stemmer reduces "boxing" to "box".

## The decision

- **Goes to A/B:** the keyword engine with synopses indexed and exact-match pinning. It clears every gate on both query sets, and there is no model to host, monitor or pay for.
- **Does not, yet:** the embedding model. This is not a finding that embeddings fail. This one, at this size, did not beat a cheaper alternative. Swapping in a stronger encoder is a one-function change, and it will face the same gates.
- **Next POC:** vibe queries. The best any system managed was 0.27 on the development set and 0.44 on the held-out set. The bottleneck is the metadata, not the ranking, so the next experiment is LLM-generated mood and tone tags, judged by the same 60 queries.

## What a PM should take from this

None of this needed a model-training background. It needed product judgment written down in a form a machine can check.

- **The golden set is the spec.** Forty queries with rubrics said more about what we were building than any requirements document I could have written.
- **Slices and guardrails are where the product thinking lives.** The average said "no effect". The slices said "ship one thing, hold another, build a third".
- **An eval should end in a decision and the next experiment.** If all you get is a score, you ran a benchmark.

## Limits

Sixty queries is a small set. Per-intent numbers rest on eight queries, or four on the held-out set, so I treat them as directional and read the intervals. One person reviewed the labels, which matters most for the vibe rubrics. The embedding model is intentionally tiny. And offline relevance is not engagement, which is the whole reason the winner goes to an A/B test and not straight to production.

The repo is [here](https://github.com/mahesh9s/discovery-search-evals). If you rerun it with a better model and the verdict changes, I would like to see it.
