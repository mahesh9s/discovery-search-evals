"""Turn eval results into a go / no-go for an online test."""
import pathlib

import yaml

from .data import ROOT


def load_gates(path: pathlib.Path = ROOT / "gates.yaml") -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_gates(system: str, means: dict, comparisons: dict, config: dict) -> list[dict]:
    """means[system][slice][metric] -> float
    comparisons[system][slice][metric] -> paired_bootstrap() output vs baseline
    """
    outcomes = []
    for gate in config["gates"]:
        cmp = comparisons[system][gate["slice"]][gate["metric"]]
        if gate["rule"] == "ci_low_above":
            observed, passed = cmp["ci_low"], cmp["ci_low"] > gate["value"]
        elif gate["rule"] == "delta_at_least":
            observed, passed = cmp["delta"], cmp["delta"] >= gate["value"] - 1e-9
        else:
            raise ValueError(f"unknown rule: {gate['rule']}")
        outcomes.append({"gate": gate["name"], "rule": gate["rule"], "threshold": gate["value"],
                         "observed": round(observed, 4), "passed": bool(passed)})
    return outcomes
