"""Unit Tests for Hazard-Specific Reliability Engines (Gate 3 / Phase D).

Verifies:
- PrecipitationReliabilitySpecialist baseline ladder progression
- Multi-component prediction (Occurrence, Amount, Heavy Rain, Extreme, Timing, Spatial)
- Strict null-safety on unsupported features
- Continuous error distribution estimation (CRPS)
- Out-of-Distribution (OOD) detection and selective prediction abstention
- Full integration with universal ReliabilityState schema
"""

import pytest

from backend.app.builder2.precipitation_specialist import PrecipitationReliabilitySpecialist
from backend.app.builder2.cyclone_specialist import CycloneReliabilitySpecialist
from backend.app.contracts.precipitation_contract import PrecipitationIssueFeatures
from backend.app.contracts.cyclone_contract import CycloneBasin, CycloneIssueFeatures
from backend.app.schemas.reliability_state import (
    DecisionMode,
    OperationalReliabilityState,
    ReliabilityState,
)


@pytest.fixture
def specialist():
    return PrecipitationReliabilitySpecialist()


@pytest.fixture
def nominal_features():
    return PrecipitationIssueFeatures(
        lead_hours=48,
        ensemble_mean_precip_mm=22.0,
        ensemble_median_precip_mm=20.5,
        ensemble_spread_precip_mm=8.4,
        ensemble_p90_precip_mm=32.0,
        wet_member_fraction=0.80,
        dry_member_fraction=0.20,
        heavy_exceedance_fraction=0.10,
        cape_proxy_jkg=1800.0,
        precipitable_water_mm=52.0,
        low_level_moisture_convergence=0.03,
        orographic_lift_proxy=0.5,
        terrain_class="mountain",
    )


def test_climatology_baseline(specialist):
    """Test Level 1: Climatological baseline rates."""
    p_monsoon = specialist.evaluate_climatology_baseline(season="monsoon", terrain_class="inland")
    p_winter = specialist.evaluate_climatology_baseline(season="winter", terrain_class="inland")
    assert 0.0 < p_winter < p_monsoon < 1.0


def test_raw_ensemble_baseline(specialist):
    """Test Level 2: Raw ensemble spread uncertainty proxy."""
    p_low_spread = specialist.evaluate_raw_ensemble_baseline(spread_mm=2.0, mean_mm=20.0)
    p_high_spread = specialist.evaluate_raw_ensemble_baseline(spread_mm=25.0, mean_mm=20.0)
    assert p_high_spread > p_low_spread


def test_spread_logistic_baseline(specialist):
    """Test Level 3: Calibrated spread logistic regression."""
    p_short = specialist.evaluate_spread_logistic_baseline(spread_mm=10.0, lead_hours=24)
    p_long = specialist.evaluate_spread_logistic_baseline(spread_mm=10.0, lead_hours=120)
    assert p_long > p_short


def test_continuous_error_distribution(specialist):
    """Test Level 5: Continuous error distribution and CRPS estimation."""
    dist = specialist.evaluate_continuous_error_distribution(mean_mm=25.0, spread_mm=10.0, lead_hours=48)
    assert dist.rmse > 0.0
    assert dist.mae > 0.0
    assert dist.q10 <= dist.q50 <= dist.q90
    assert dist.crps is not None and dist.crps > 0.0


def test_predict_nominal(specialist, nominal_features):
    """Test comprehensive specialist prediction under nominal conditions."""
    out = specialist.predict(nominal_features, has_subdaily_data=True, has_spatial_radar=True)
    assert out.hazard == "PRECIPITATION"
    assert out.occurrence_failure_probability is not None
    assert out.amount_failure_probability is not None
    assert out.heavy_rain_failure_probability is not None
    assert out.timing_failure_probability is not None
    assert out.spatial_displacement_probability is not None
    assert out.overall_reliability is not None
    assert out.ood is False
    assert len(out.evidence) >= 3


def test_unsupported_fields_null(specialist, nominal_features):
    """Test that unsupported sub-daily timing and spatial radar inputs remain null."""
    out = specialist.predict(nominal_features, has_subdaily_data=False, has_spatial_radar=False)
    assert out.timing_failure_probability is None
    assert out.spatial_displacement_probability is None
    # Occurrence and amount are still evaluated
    assert out.occurrence_failure_probability is not None
    assert out.amount_failure_probability is not None


def test_ood_detection_and_abstention(specialist):
    """Test OOD detection and abstention state when inputs exceed physical support."""
    ood_features = PrecipitationIssueFeatures(
        lead_hours=72,
        ensemble_mean_precip_mm=120.0,
        ensemble_median_precip_mm=115.0,
        ensemble_spread_precip_mm=95.0,  # Exceeds ood_spread_threshold_mm (80.0)
        ensemble_p90_precip_mm=180.0,
        wet_member_fraction=0.90,
        dry_member_fraction=0.10,
        cape_proxy_jkg=5200.0,            # Extreme CAPE
        precipitable_water_mm=92.0,       # Extreme PWAT
        terrain_class="mountain",
    )

    out = specialist.predict(ood_features)
    assert out.ood is True
    assert float(out.provenance.get("ood_score", 0.0)) >= 0.70

    # Universal ReliabilityState integration under OOD
    state = specialist.to_reliability_state(ood_features)
    assert state.abstention_state is True
    assert state.decision_mode == DecisionMode.ABSTAIN_UNSUPPORTED
    assert state.reliability_state == OperationalReliabilityState.ABSTAIN
    assert state.bust_probability is None  # Must be null when abstaining


def test_to_reliability_state_integration(specialist, nominal_features):
    """Test full generation of universal 30-field ReliabilityState contract."""
    state = specialist.to_reliability_state(
        nominal_features,
        forecast_id="FCST-TEST-DELHI",
        location="DELHI",
    )
    assert isinstance(state, ReliabilityState)
    assert state.forecast_identity == "FCST-TEST-DELHI"
    assert state.hazard_type == "PRECIPITATION"
    assert state.bust_probability is not None
    assert len(state.hazard_curve) > 0
    assert len(state.survival_curve) == len(state.hazard_curve)

    # Invariant: Survival curve must be monotonically non-increasing
    for i in range(len(state.survival_curve) - 1):
        assert state.survival_curve[i+1] <= state.survival_curve[i]

    assert state.decision_mode == DecisionMode.NOMINAL
    assert state.reliability_state == OperationalReliabilityState.STABLE


# ==============================================================================
# Tropical Cyclone Reliability Specialist Tests (Gate 4 / Phase E)
# ==============================================================================

@pytest.fixture
def cyclone_specialist():
    return CycloneReliabilitySpecialist()


@pytest.fixture
def nominal_cyclone_landfall_features():
    return CycloneIssueFeatures(
        lead_hours=48,
        basin=CycloneBasin.BAY_OF_BENGAL,
        forecast_lat=18.5,
        forecast_lon=86.2,
        forward_speed_kmh=18.0,
        ensemble_track_spread_km=85.0,
        ensemble_track_clustering=0.25,
        forecast_max_wind_ms=45.0,
        ensemble_intensity_spread_ms=5.5,
        vertical_wind_shear_ms=12.0,
        steering_flow_speed_ms=6.5,
        steering_flow_dir_deg=315.0,
        central_pressure_tendency_hpa_12h=-10.0,
        distance_to_coast_km=140.0,
        forecast_landfall=True,
        forecast_landfall_lead_hours=54,
    )


def test_cyclone_baselines(cyclone_specialist):
    """Test Level 1, 2, 3 cyclone track baselines."""
    p_clim = cyclone_specialist.evaluate_climatology_baseline(basin=CycloneBasin.BAY_OF_BENGAL, lead_hours=48)
    assert 0.05 < p_clim < 0.50

    p_raw_low = cyclone_specialist.evaluate_raw_ensemble_baseline(track_spread_km=40.0, lead_hours=48)
    p_raw_high = cyclone_specialist.evaluate_raw_ensemble_baseline(track_spread_km=140.0, lead_hours=48)
    assert p_raw_high > p_raw_low

    p_log = cyclone_specialist.evaluate_spread_logistic_baseline(track_spread_km=85.0, lead_hours=48)
    assert 0.01 < p_log < 0.99


def test_cyclone_conformal_uncertainty(cyclone_specialist):
    """Test Level 5: Conformal track uncertainty radius."""
    r90 = cyclone_specialist.evaluate_conformal_track_radius(track_spread_km=85.0, lead_hours=48, target_coverage=0.90)
    r80 = cyclone_specialist.evaluate_conformal_track_radius(track_spread_km=85.0, lead_hours=48, target_coverage=0.80)
    assert r90 > r80 > 85.0


def test_cyclone_landfall_vs_non_landfall_null_safety(cyclone_specialist, nominal_cyclone_landfall_features):
    """Verify strict null-safety: landfall fields are present for landfall and None for offshore."""
    # Landfall case
    out_lf = cyclone_specialist.predict(nominal_cyclone_landfall_features)
    assert out_lf.landfall_location_failure_probability is not None
    assert out_lf.landfall_timing_failure_probability is not None

    # Non-landfall offshore case
    offshore_features = nominal_cyclone_landfall_features.model_copy(
        update={"forecast_landfall": False, "distance_to_coast_km": 500.0}
    )
    out_offshore = cyclone_specialist.predict(offshore_features)
    assert out_offshore.landfall_location_failure_probability is None
    assert out_offshore.landfall_timing_failure_probability is None
    # Track and intensity are still computed
    assert out_offshore.track_failure_probability is not None
    assert out_offshore.intensity_failure_probability is not None


def test_cyclone_ood_and_abstention(cyclone_specialist, nominal_cyclone_landfall_features):
    """Verify OOD detection and abstention state under extreme shear/spread."""
    ood_features = nominal_cyclone_landfall_features.model_copy(
        update={
            "ensemble_track_spread_km": 350.0,  # Exceeds 280km
            "vertical_wind_shear_ms": 52.0,     # Exceeds 45 m/s
        }
    )
    out = cyclone_specialist.predict(ood_features)
    assert out.ood is True

    state = cyclone_specialist.to_reliability_state(ood_features)
    assert state.abstention_state is True
    assert state.decision_mode == DecisionMode.ABSTAIN_UNSUPPORTED
    assert state.reliability_state == OperationalReliabilityState.ABSTAIN
    assert state.bust_probability is None


def test_cyclone_to_reliability_state_integration(cyclone_specialist, nominal_cyclone_landfall_features):
    """Verify universal ReliabilityState generation for cyclone."""
    state = cyclone_specialist.to_reliability_state(
        nominal_cyclone_landfall_features,
        forecast_id="FCST-TEST-FANI",
        location="ODISHA_COAST",
    )
    assert isinstance(state, ReliabilityState)
    assert state.forecast_identity == "FCST-TEST-FANI"
    assert state.hazard_type == "CYCLONE"
    assert state.bust_probability is not None
    assert len(state.hazard_curve) > 0
    assert len(state.survival_curve) == len(state.hazard_curve)

    # Invariant: Monotonic survival curve
    for i in range(len(state.survival_curve) - 1):
        assert state.survival_curve[i+1] <= state.survival_curve[i]

    assert state.decision_mode == DecisionMode.NOMINAL
    assert state.reliability_state == OperationalReliabilityState.STABLE
