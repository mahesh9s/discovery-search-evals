# Data

## catalog.jsonl

5,065 films, one JSON object per line: `id`, `title`, `year`, `genres`, `cast`, `extract`.

Source: [prust/wikipedia-movie-data](https://github.com/prust/wikipedia-movie-data) (`movies.json`), commit `cef043a7263498604cd4b26feb84af059a950391`. That dataset lists American film releases from 1900 to 2023, scraped from Wikipedia.

`scripts/build_catalog.py` rebuilds this file from the pinned commit. It keeps a title when:

- the release year is 2000 or later
- the synopsis (`extract`) is at least 40 words
- there is at least one genre and a cast list

`id` is the Wikipedia page slug, for example `The_Martian_(film)`.

**Licence.** The source repository's code and structure are MIT licensed (Copyright (c) 2016 Peter Rust). The `extract` text is taken from Wikipedia articles and is available under the [Creative Commons Attribution-ShareAlike 4.0 licence](https://creativecommons.org/licenses/by-sa/4.0/). This file is redistributed under the same licence. Each article is at `https://en.wikipedia.org/wiki/<id>`.

**Known quirks**, left as they are because real catalogs have them too:

- Cast lists are incomplete for some titles. Two films with Mahershala Ali omit him from `cast` and credit him only in the synopsis.
- A few entries carry a synopsis for a related title. The record titled "Chicken Run: Dawn of the Nugget" has the synopsis of the original Chicken Run.
- The genre vocabulary is uneven. Courtroom films are tagged `Legal`, and some sport films are tagged `Sport` instead of `Sports`.

## queries.yaml and queries_heldout.yaml

The golden set. Each query has an `id`, an intent `slice`, the `query` text as a person would type it, and a `note` that is the rubric its results were graded against.

| File | Queries | Role |
|---|---|---|
| `queries.yaml` | 40 (8 per slice) | Development. Used to find failures and decide what to change |
| `queries_heldout.yaml` | 20 (4 per slice) | Held out. Written after round 1, before the round 2 systems were run. Never used for design |

## qrels.tsv

2,241 relevance judgments: `query_id`, `doc_id`, `grade`, `source`.

Grades: `2` exactly what the person wanted, `1` a reasonable result to show, `0` looked at and judged not relevant. Grade 0 rows are kept on purpose. They record that a result was judged, which is different from a result nobody has looked at.

| Source | Rows | Meaning |
|---|---|---|
| `pooled` | 1,096 | In some system's top 10 for the query. Graded blind from a shuffled sheet with no system names |
| `nominated` | 852 | Added by the judge from prior knowledge of the films, so recall is not capped by what the systems found |
| `cast` | 293 | Actor queries: grade 2 when the actor is in the title's cast list |

Any title without a row for a query is unjudged and scores as not relevant. The `Judged@10` metric reports how often that happens.
