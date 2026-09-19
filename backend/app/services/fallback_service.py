"""Forecast Failure & Degraded Operation Fallback Service.

Implements robust failure handling per SIH26079 §21, §22, and Research Files 006, 018, 076:
- K1: Upstream NWP download failure -> retrieve cached last good cycle, flag "DATA_DELAYED".
- K2: Incomplete forecast / missing ensemble members -> degraded operation mode or safe abstention.
- K3: Primary ML model unavailable -> fallback to calibrated spread-only baseline.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.app.schemas.prediction import ReasonCode, RiskLevel, TrustState
from backend.app.services.base import ModelResult, WeatherResult

logger = logging.getLogger(__name__)

# Minimum ensemble members required for meaningful evaluation
MIN_ENSEMBLE_MEMBERS_REQUIRED = 10
FULL_GEFS_ENSEMBLE_MEMBERS = 31


@dataclass
class FallbackCycleResult:
    """Result of attempting to recover from an upstream download failure using cached cycle."""

    recovered: bool
    cycle_time: Optional[str] = None
    is_fallback_cycle: bool = False
    status_code: str = "OK"  # "OK", "DATA_DELAYED", "CYCLE_UNAVAILABLE"
    warning_message: Optional[str] = None
    weather_data: Optional[WeatherResult] = None


@dataclass
class DegradedEnsembleAssessment:
    """Assessment of ensemble completeness and degraded operation status."""

    is_degraded: bool
    abstain_required: bool
    available_members: int
    missing_members: int
    completeness_ratio: float
    uncertainty_inflation_factor: float
    reason_codes: List[str] = field(default_factory=list)
    guidance: str = "Ensemble complete."


@dataclass
class BaselineFallbackResult:
    """Calibrated spread-only baseline fallback prediction when primary ML model is unavailable."""

    probability: float
    risk_level: RiskLevel
    trust_state: TrustState
    fallback_model_name: str = "spread_only_logistic_baseline_v1"
    reason_codes: List[str] = field(default_factory=list)
    explanation_summary: str = ""


class ForecastFallbackService:
    """Orchestrates fallbacks for download failures, missing members, and model unavailability."""

    def __init__(self):
        # In-memory last-good-cycle cache by location
        self._last_good_cycles: Dict[str, WeatherResult] = {}

    def record_good_cycle(self, location: str, result: WeatherResult) -> None:
        """Cache a successful weather ingestion cycle for fallback recovery."""
        if result.is_available and not result.error:
            self._last_good_cycles[location.strip().lower()] = result

    def handle_download_failure(
        self,
        location: str,
        target_date: Optional[str] = None,
    ) -> FallbackCycleResult:
        """Attempt to fallback to the previous valid forecast cycle if upstream NWP download fails (K1)."""
        loc_key = location.strip().lower()
        cached = self._last_good_cycles.get(loc_key)

        if cached is not None:
            logger.warning(
                "Upstream download failed for %s. Falling back to cached cycle: %s",
                location,
                cached.metadata.get("issue_time", "unknown"),
            )
            return FallbackCycleResult(
                recovered=True,
                cycle_time=cached.metadata.get("issue_time"),
                is_fallback_cycle=True,
                status_code="DATA_DELAYED",
                warning_message=(
                    f"Real-time NWP ingestion delayed for '{location}'. "
                    f"Using previous valid forecast cycle ({cached.metadata.get('issue_time', 'cached')})."
                ),
                weather_data=cached,
            )

        return FallbackCycleResult(
            recovered=False,
            is_fallback_cycle=False,
            status_code="DATA_DELAYED",
            warning_message=(
                f"NWP data delayed from upstream provider for '{location}' and no prior cycle is cached. "
                "Forecast evaluation temporarily unavailable."
            ),
            weather_data=None,
        )

    def assess_ensemble_completeness(
        self,
        available_members: int,
        expected_members: int = FULL_GEFS_ENSEMBLE_MEMBERS,
    ) -> DegradedEnsembleAssessment:
        """Assess whether an ensemble is degraded or requires safe abstention (K2)."""
        completeness = max(0.0, min(1.0, available_members / max(1, expected_members)))
        missing = max(0, expected_members - available_members)

        # Critical failure: fewer than minimum required members
        if available_members < MIN_ENSEMBLE_MEMBERS_REQUIRED:
            return DegradedEnsembleAssessment(
                is_degraded=True,
                abstain_required=True,
                available_members=available_members,
                missing_members=missing,
                completeness_ratio=completeness,
                uncertainty_inflation_factor=2.0,
                reason_codes=[
                    "DEGRADED_ENSEMBLE_INSUFFICIENT_MEMBERS",
                    ReasonCode.INSUFFICIENT_DATA.value,
                ],
                guidance=(
                    f"Only {available_members}/{expected_members} ensemble members available. "
                    f"Below operational minimum ({MIN_ENSEMBLE_MEMBERS_REQUIRED}). Model safely abstained."
                ),
            )

        # Degraded mode: some members missing
        if available_members < expected_members:
            # Inflation factor scales with missingness (e.g., 20/31 -> 1.35x)
            inflation = round(1.0 + (missing / expected_members) * 0.8, 3)
            return DegradedEnsembleAssessment(
                is_degraded=True,
                abstain_required=False,
                available_members=available_members,
                missing_members=missing,
                completeness_ratio=completeness,
                uncertainty_inflation_factor=inflation,
                reason_codes=["DEGRADED_ENSEMBLE_INCOMPLETE"],
                guidance=(
                    f"Incomplete ensemble ({available_members}/{expected_members} members). "
                    f"Operating in degraded mode with uncertainty inflated by {inflation}x."
                ),
            )

        # Full nominal ensemble
        return DegradedEnsembleAssessment(
            is_degraded=False,
            abstain_required=False,
            available_members=available_members,
            missing_members=0,
            completeness_ratio=1.0,
            uncertainty_inflation_factor=1.0,
            reason_codes=[],
            guidance="Nominal full ensemble available.",
        )

    def compute_spread_only_fallback(
        self,
        ensemble_spread: float,
        lead_hours: int = 48,
        variable: str = "temperature_2m",
    ) -> BaselineFallbackResult:
        """Fallback to calibrated spread-only logistic baseline when primary ML model is unavailable (K3).
        
        Uses logistic sigmoid on normalized spread:
        p_bust = 1 / (1 + exp(-(beta_0 + beta_1 * normalized_spread)))
        """
        # Baseline coefficients calibrated on 2000-2018 training reforecasts
        beta_0 = -2.20
        beta_1 = 0.85

        # Variable-specific spread normalization scales
        spread_scales = {
            "temperature_2m": 2.5,
            "wind_speed_10m": 4.0,
            "surface_pressure": 3.0,
            "geopotential_height_500hPa": 45.0,
            "precipitation_24h": 15.0,
        }
        scale = spread_scales.get(variable, 2.5)
        norm_spread = ensemble_spread / scale

        # Logistic computation
        z = beta_0 + beta_1 * norm_spread
        import math
        p = round(1.0 / (1.0 + math.exp(-z)), 4)

        if p >= 0.70:
            risk = RiskLevel.CRITICAL
            trust = TrustState.MODERATE_CONFIDENCE
        elif p >= 0.50:
            risk = RiskLevel.HIGH
            trust = TrustState.MODERATE_CONFIDENCE
        elif p >= 0.30:
            risk = RiskLevel.MEDIUM
            trust = TrustState.MODERATE_CONFIDENCE
        else:
            risk = RiskLevel.LOW
            trust = TrustState.MODERATE_CONFIDENCE

        return BaselineFallbackResult(
            probability=p,
            risk_level=risk,
            trust_state=trust,
            fallback_model_name="spread_only_logistic_baseline_v1",
            reason_codes=[
                "MODEL_UNAVAILABLE_SPREAD_FALLBACK",
                "SPREAD_ONLY_ESTIMATE",
            ],
            explanation_summary=(
                f"Primary ML model unavailable. Estimated bust probability ({p:.1%}) "
                f"derived from calibrated ensemble spread ({ensemble_spread:.2f}) baseline."
            ),
        )


default_fallback_service = ForecastFallbackService()
