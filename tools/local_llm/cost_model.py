#!/usr/bin/env python3
"""Compute Claude vs local cost scenarios from a JSON config."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class Pricing:
    input_per_mtok: float
    output_per_mtok: float


@dataclass(frozen=True)
class Scenario:
    name: str
    input_tokens: int
    output_tokens: int
    local_share: float


def load_config(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_pricing(data: Dict[str, Any]) -> Pricing:
    return Pricing(
        input_per_mtok=float(data["input_per_mtok"]),
        output_per_mtok=float(data["output_per_mtok"]),
    )


def parse_scenarios(data: List[Dict[str, Any]]) -> List[Scenario]:
    scenarios: List[Scenario] = []
    for item in data:
        scenarios.append(
            Scenario(
                name=str(item["name"]),
                input_tokens=int(item["input_tokens"]),
                output_tokens=int(item["output_tokens"]),
                local_share=float(item["local_share"]),
            )
        )
    return scenarios


def validate_scenario(scenario: Scenario) -> None:
    if scenario.input_tokens < 0 or scenario.output_tokens < 0:
        raise ValueError(f"Negative token counts in {scenario.name}")
    if not (0.0 <= scenario.local_share <= 1.0):
        raise ValueError(f"local_share out of range in {scenario.name}")


def mtok(tokens: int) -> float:
    return tokens / 1_000_000.0


def compute_costs(
    pricing: Pricing, local_cost_per_mtok: float, scenario: Scenario
) -> Dict[str, float]:
    validate_scenario(scenario)
    local_share = scenario.local_share
    claude_input = int(round(scenario.input_tokens * (1.0 - local_share)))
    claude_output = int(round(scenario.output_tokens * (1.0 - local_share)))
    local_tokens = (scenario.input_tokens + scenario.output_tokens) - (
        claude_input + claude_output
    )

    claude_cost = (mtok(claude_input) * pricing.input_per_mtok) + (
        mtok(claude_output) * pricing.output_per_mtok
    )
    local_cost = mtok(local_tokens) * local_cost_per_mtok
    total = claude_cost + local_cost
    baseline = (mtok(scenario.input_tokens) * pricing.input_per_mtok) + (
        mtok(scenario.output_tokens) * pricing.output_per_mtok
    )
    savings = baseline - total
    savings_pct = 0.0 if baseline == 0 else (savings / baseline) * 100.0

    return {
        "claude_cost": claude_cost,
        "local_cost": local_cost,
        "total_cost": total,
        "baseline_cost": baseline,
        "savings": savings,
        "savings_pct": savings_pct,
    }


def render_report(rows: List[Dict[str, Any]]) -> str:
    lines = []
    header = (
        "scenario,baseline_cost,total_cost,claude_cost,local_cost,savings,savings_pct"
    )
    lines.append(header)
    for row in rows:
        lines.append(
            f"{row['name']},{row['baseline_cost']:.4f},{row['total_cost']:.4f},"
            f"{row['claude_cost']:.4f},{row['local_cost']:.4f},"
            f"{row['savings']:.4f},{row['savings_pct']:.2f}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to scenario JSON")
    parser.add_argument("--output", help="Write CSV output to file")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    pricing = parse_pricing(config["claude_pricing"])
    local_cost_per_mtok = float(config["local_cost_per_mtok"])
    scenarios = parse_scenarios(config["scenarios"])

    rows: List[Dict[str, Any]] = []
    for scenario in scenarios:
        costs = compute_costs(pricing, local_cost_per_mtok, scenario)
        costs["name"] = scenario.name
        rows.append(costs)

    report = render_report(rows)
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
