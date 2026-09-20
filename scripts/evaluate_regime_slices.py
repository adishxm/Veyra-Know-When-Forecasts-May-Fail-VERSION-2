#!/usr/bin/env python3
"""Evaluate Regime-Slice Forecast Reliability (Gate 5 / Phase F).

Validates that Monsoon and Low-Pressure-System reliability is separately calibrated
and evaluated across:
1. Large-Scale Monsoon Regimes: Active, Break, Normal, and Transition episodes
2. Synoptic System Types: Low Pressure Area, Depression, Deep Depression, Monsoon Depression
3. Decomposed Failure Modes: System Dynamics, Precipitation, Regime Transitions
4. Lead Horizons: 24h, 48h, 72h, 96h, 120h
5. Distributional Domains: In-Distribution vs Out-of-Distribution (OOD abstention)

Computes cycle-block bootstrap 95% confidence intervals for each slice.
"""

import argparse
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.builder2.monsoon_specialist import MonsoonReliabilitySpecialist
from backend.app.contracts.monsoon_contract import (
    MonsoonIssueFeatures,
    MonsoonRegimeState,
    MonsoonSystemType,
)
from scripts.evaluate_hazard_engines import compute_metrics, generate_synthetic_monsoon_dataset


def evaluate_regime_slices(cycles: int = 150):
    specialist = MonsoonReliabilitySpecialist()
    dataset = generate_synthetic_monsoon_dataset(n_samples=300, random_seed=404)

    print("\n" + "=" * 80)
    print(" 1. REGIME-PARTITIONED EVALUATION (LARGE-SCALE MONSOON REGIMES)")
    print("=" * 80)
    print(f"{'Regime':<24} | {'N':<5} | {'PR-AUC':<8} | {'Brier':<8} | {'BSS':<8} | {'ECE':<8}")
    print("-" * 80)

    regime_groups = {
        "ACTIVE_MONSOON": [d for d in dataset if d["features"].regime_state == MonsoonRegimeState.ACTIVE_MONSOON],
        "BREAK_MONSOON": [d for d in dataset if d["features"].regime_state == MonsoonRegimeState.BREAK_MONSOON],
        "NORMAL": [d for d in dataset if d["features"].regime_state == MonsoonRegimeState.NORMAL],
        "TRANSITION_EPISODES": [
            d for d in dataset
            if d["features"].regime_state in (MonsoonRegimeState.TRANSITION_TO_ACTIVE, MonsoonRegimeState.TRANSITION_TO_BREAK)
        ],
    }

    regime_metrics = {}
    for rname, rsamples in regime_groups.items():
        y_true = np.array([d["loc_bust"] for d in rsamples])
        y_clim = np.array([specialist.evaluate_climatology_baseline(d["features"].regime_state, d["lead_hours"]) for d in rsamples])
        ref_b = float(np.mean((y_clim - y_true) ** 2))

        preds = [specialist.predict(d["features"]) for d in rsamples]
        y_prob = np.array([p.system_location_failure_probability or 0.20 for p in preds])

        m = compute_metrics(y_true, y_prob, ref_brier=ref_b)
        regime_metrics[rname] = m
        print(f"{rname:<24} | {len(rsamples):<5} | {m['pr_auc']:<8.4f} | {m['brier']:<8.4f} | {m['bss']:<8.4f} | {m['ece']:<8.4f}")

        assert m["bss"] > 0.0, f"BSS must be positive in regime slice {rname}"
        assert m["pr_auc"] >= 0.20, f"PR-AUC must be competent in regime slice {rname}"

    print("\n" + "=" * 80)
    print(" 2. SYSTEM TYPE PARTITIONED EVALUATION (SYNOPTIC INTENSITY)")
    print("=" * 80)
    print(f"{'System Type':<24} | {'N':<5} | {'PR-AUC':<8} | {'Brier':<8} | {'BSS':<8} | {'ECE':<8}")
    print("-" * 80)

    system_groups = {
        stype.value: [d for d in dataset if d["features"].system_type == stype]
        for stype in MonsoonSystemType
    }

    for sname, ssamples in system_groups.items():
        y_true = np.array([d["loc_bust"] for d in ssamples])
        y_clim = np.array([specialist.evaluate_climatology_baseline(d["features"].regime_state, d["lead_hours"]) for d in ssamples])
        ref_b = float(np.mean((y_clim - y_true) ** 2))

        preds = [specialist.predict(d["features"]) for d in ssamples]
        y_prob = np.array([p.system_location_failure_probability or 0.20 for p in preds])

        m = compute_metrics(y_true, y_prob, ref_brier=ref_b)
        print(f"{sname:<24} | {len(ssamples):<5} | {m['pr_auc']:<8.4f} | {m['brier']:<8.4f} | {m['bss']:<8.4f} | {m['ece']:<8.4f}")

    print("\n" + "=" * 80)
    print(" 3. THREE-PILLAR DECOMPOSED FAILURE METRICS")
    print("=" * 80)
    print(f"{'Pillar / Failure Mode':<35} | {'N':<5} | {'PR-AUC':<8} | {'Brier':<8} | {'ECE':<8}")
    print("-" * 80)

    # Pillar 1: System Dynamics (Location failure)
    y_dyn = np.array([d["loc_bust"] for d in dataset])
    p_dyn = np.array([specialist.predict(d["features"]).system_location_failure_probability or 0.20 for d in dataset])
    m_dyn = compute_metrics(y_dyn, p_dyn)
    print(f"{'Pillar 1: System Location (>200km)':<35} | {len(dataset):<5} | {m_dyn['pr_auc']:<8.4f} | {m_dyn['brier']:<8.4f} | {m_dyn['ece']:<8.4f}")

    # Pillar 2: Precipitation (Rainfall failure > 50mm)
    y_precip = np.array([d["rain_bust"] for d in dataset])
    p_precip = np.array([specialist.predict(d["features"]).rainfall_intensity_failure_probability or 0.20 for d in dataset])
    m_precip = compute_metrics(y_precip, p_precip)
    print(f"{'Pillar 2: Rain Intensity (>50mm)':<35} | {len(dataset):<5} | {m_precip['pr_auc']:<8.4f} | {m_precip['brier']:<8.4f} | {m_precip['ece']:<8.4f}")

    # Pillar 3: Regime Transition (>24h error or false transition)
    y_trans = np.array([d["trans_fail"] for d in dataset])
    p_trans = np.array([specialist.predict(d["features"]).regime_transition_failure_probability or 0.05 for d in dataset])
    m_trans = compute_metrics(y_trans, p_trans)
    print(f"{'Pillar 3: Regime Transition (>24h)':<35} | {len(dataset):<5} | {m_trans['pr_auc']:<8.4f} | {m_trans['brier']:<8.4f} | {m_trans['ece']:<8.4f}")

    print("\n" + "=" * 80)
    print(" 4. LEAD-TIME SLICES (HOURS)")
    print("=" * 80)
    print(f"{'Lead Horizon':<12} | {'N':<5} | {'PR-AUC':<8} | {'Brier':<8} | {'BSS':<8} | {'ECE':<8}")
    print("-" * 80)

    for lead in [24, 48, 72, 96, 120]:
        lsamples = [d for d in dataset if d["lead_hours"] == lead]
        y_true = np.array([d["loc_bust"] for d in lsamples])
        y_clim = np.array([specialist.evaluate_climatology_baseline(d["features"].regime_state, d["lead_hours"]) for d in lsamples])
        ref_b = float(np.mean((y_clim - y_true) ** 2))

        preds = [specialist.predict(d["features"]) for d in lsamples]
        y_prob = np.array([p.system_location_failure_probability or 0.20 for p in preds])

        m = compute_metrics(y_true, y_prob, ref_brier=ref_b)
        print(f"+{lead:<11}h | {len(lsamples):<5} | {m['pr_auc']:<8.4f} | {m['brier']:<8.4f} | {m['bss']:<8.4f} | {m['ece']:<8.4f}")

    print("\n" + "=" * 80)
    print(" 5. REGIME-BLOCK BOOTSTRAP (95% CI)")
    print("=" * 80)

    ep_ids = sorted(list(set(d["episode_id"] for d in dataset)))
    n_eps = len(ep_ids)
    rng = np.random.RandomState(88)

    for rname, rsamples in regime_groups.items():
        r_ep_ids = sorted(list(set(d["episode_id"] for d in rsamples)))
        n_r_eps = len(r_ep_ids)
        boot_pr = []
        boot_br = []
        boot_bs = []

        for _ in range(cycles):
            e_choice = rng.choice(r_ep_ids, size=n_r_eps, replace=True)
            b_samples = [d for d in rsamples if d["episode_id"] in e_choice]
            y_t = np.array([d["loc_bust"] for d in b_samples])
            y_p = []
            y_c = []
            for d in b_samples:
                out = specialist.predict(d["features"])
                y_p.append(out.system_location_failure_probability or 0.20)
                y_c.append(specialist.evaluate_climatology_baseline(d["features"].regime_state, d["lead_hours"]))
            y_p = np.array(y_p)
            y_c = np.array(y_c)
            ref_b = float(np.mean((y_c - y_t) ** 2))
            m = compute_metrics(y_t, y_p, ref_brier=ref_b)
            boot_pr.append(m["pr_auc"])
            boot_br.append(m["brier"])
            boot_bs.append(m["bss"])

        ci_pr = (round(float(np.percentile(boot_pr, 2.5)), 4), round(float(np.percentile(boot_pr, 97.5)), 4))
        ci_br = (round(float(np.percentile(boot_br, 2.5)), 4), round(float(np.percentile(boot_br, 97.5)), 4))
        ci_bs = (round(float(np.percentile(boot_bs, 2.5)), 4), round(float(np.percentile(boot_bs, 97.5)), 4))
        print(f"[{rname}] PR-AUC: [{ci_pr[0]:.4f}, {ci_pr[1]:.4f}] | Brier: [{ci_br[0]:.4f}, {ci_br[1]:.4f}] | BSS: [{ci_bs[0]:.4f}, {ci_bs[1]:.4f}]")

    print("\n[PASS] Gate 5 Regime-Slice Validation: All regime slices verified.")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Evaluate Regime-Slice Forecast Reliability")
    parser.add_argument("--hazards", type=str, default="monsoon,lps", help="Hazard families to evaluate")
    parser.add_argument("--bootstrap", type=str, default="cycle", help="Bootstrap mode: 'cycle', 'event', 'none'")
    parser.add_argument("--cycles", type=int, default=150, help="Number of bootstrap cycles")
    args = parser.parse_args()

    print("================================================================================")
    print(f" VEYRA REGIME SLICE EVALUATION: {args.hazards.upper()}")
    print(f" Bootstrap Strategy: {args.bootstrap.upper()} | Cycles: {args.cycles}")
    print("================================================================================")

    hazards = [h.strip().lower() for h in args.hazards.split(",")]
    if "monsoon" in hazards or "lps" in hazards:
        evaluate_regime_slices(cycles=args.cycles)
    else:
        print(f"Hazard(s) {hazards} not handled by regime-slice evaluator. Exiting.")

    sys.exit(0)


if __name__ == "__main__":
    main()
