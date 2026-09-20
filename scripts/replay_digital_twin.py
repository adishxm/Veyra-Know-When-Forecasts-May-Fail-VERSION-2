#!/usr/bin/env python3
"""Reliability Digital Twin Historical Episode Replay (Gate 11 / Phase L).

Replays severe weather episodes cycle-by-cycle to evaluate lead-time warning advantage,
calibration, and operational utility across 4 tiers:
  1. raw (uncalibrated NWP ensemble)
  2. v3 (baseline certified model)
  3. certified-veyra (full certified hazard specialist suite)
  4. frontier (experimental challenger, marked is_simulation: true)

Usage:
    python scripts/replay_digital_twin.py --event historical --compare raw,v3,certified-veyra,frontier
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure SIH26079-RII root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.builder2.digital_twin_engine import DigitalTwinEngine


def main():
    parser = argparse.ArgumentParser(description="Replay severe weather episode via Reliability Digital Twin.")
    parser.add_argument(
        "--event",
        type=str,
        default="historical",
        help="Historical severe weather event key (e.g. historical, cyclone_biparjoy_2023).",
    )
    parser.add_argument(
        "--compare",
        type=str,
        default="raw,v3,certified-veyra,frontier",
        help="Comma-separated list of tiers to compare (raw,v3,certified-veyra,frontier).",
    )
    args = parser.parse_args()

    tiers = [t.strip() for t in args.compare.split(",") if t.strip()]

    print(f"=== Veyra Reliability Digital Twin Replay (Gate 11 / Phase L) ===")
    print(f"Event: {args.event}")
    print(f"Compared Tiers: {tiers}\n")

    engine = DigitalTwinEngine()
    result = engine.replay_event(event_name=args.event, compare_tiers=tiers)

    print(f"Event Replayed: {result.event_name}")
    print(f"Hazard Family: {result.hazard_family}")
    print(f"Total Forecast Cycles: {len(result.cycles)}\n")

    print(f"{'Cycle ID':<10} | {'Lead (h)':<8} | {'Raw Prob':<10} | {'V3 Prob':<10} | {'Cert Veyra':<12} | {'Frontier':<10} | {'Obs Bust'}")
    print("-" * 85)
    for c in result.cycles:
        print(
            f"{c.cycle_id:<10} | {c.lead_hours:<8} | {c.raw_bust_prob:<10.2f} | {c.v3_bust_prob:<10.2f} | "
            f"{c.certified_veyra_bust_prob:<12.2f} | {c.frontier_bust_prob:<10.2f} | {c.ground_truth_failure}"
        )

    print("\n=== Multi-Tier Summary Metrics ===")
    print(f"{'Tier':<16} | {'Brier':<8} | {'ECE':<8} | {'Lead Adv (h)':<13} | {'False Alarm':<12} | {'Utility':<8} | {'Latency':<9} | {'Status'}")
    print("-" * 95)
    for t_name, summary in result.tier_summaries.items():
        sim_tag = " [SIM]" if summary.is_simulation else ""
        print(
            f"{summary.tier_name + sim_tag:<16} | {summary.brier_score:<8.4f} | {summary.expected_calibration_error:<8.4f} | "
            f"{summary.lead_time_advantage_hours:<13.1f} | {summary.false_alarm_rate:<12.2f} | {summary.operational_utility_score:<8.2f} | "
            f"{summary.average_latency_ms:<7.1f}ms | {summary.status}"
        )

    print(f"\nRecommended Tier: {result.recommended_tier}")
    print(f"Rationale: {result.decision_rationale}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
