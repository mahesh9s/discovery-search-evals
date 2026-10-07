"""Paired bootstrap over queries.

Forty queries is a small sample. A difference in means is only worth acting on
if it survives resampling the queries, so every comparison against the
baseline is reported with a 95% interval, not just a point estimate.
"""
import numpy as np


def paired_bootstrap(candidate: list[float], baseline: list[float],
                     n_resamples: int = 10_000, seed: int = 7) -> dict:
    diff = np.asarray(candidate, dtype=np.float64) - np.asarray(baseline, dtype=np.float64)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(diff), size=(n_resamples, len(diff)))
    means = diff[idx].mean(axis=1)
    low, high = np.percentile(means, [2.5, 97.5])
    return {
        "delta": float(diff.mean()),
        "ci_low": float(low),
        "ci_high": float(high),
        "wins": int((diff > 1e-9).sum()),
        "losses": int((diff < -1e-9).sum()),
        "ties": int((np.abs(diff) <= 1e-9).sum()),
    }
