# workflows

`evals.yml` runs on every push to `main` and every pull request: the unit tests, the golden-set checks and the ship gates, then it regenerates the results tables and posts the dev-set summary to the run page.
