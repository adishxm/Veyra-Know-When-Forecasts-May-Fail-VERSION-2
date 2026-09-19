/**
 * Veyra API Schema Contracts and Typed Interfaces
 * Synchronized with Backend Pydantic Schemas.
 */

export type TrustState =
  | 'UNAVAILABLE'
  | 'HIGH_CONFIDENCE'
  | 'MODERATE_CONFIDENCE'
  | 'LOW_CONFIDENCE'
  | 'ABSTAINED';

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type SupportedVariable =
  | 'temperature_2m'
  | 'surface_pressure'
  | 'wind_speed_10m'
  | 'relative_humidity_2m'
  | 'precipitation';

export interface ContributingFactor {
  factor: string;
  value: number | null;
  signal: string;
  shap_value?: number | null;
  availability_time?: string | null;
  unit?: string | null;
  reason_code?: string | null;
}

export interface ExplanationItem {
  primary_driver: string;
  driver_summary: string;
  top_contributing_factors: ContributingFactor[];
  reason_codes?: string[];
  disclaimer?: string;
}

export interface PredictionRequest {
  location: string;
  issue_time?: string;
  valid_time?: string;
  variable?: string;
  model_type?: string;
  target_date?: string;
}

export interface PredictionResponse {
  location: string;
  bust_probability: number | null;
  risk_level: RiskLevel | null;
  trust_state: TrustState;
  abstain: boolean;
  reason_codes: string[];
  model_version: string | null;
  data_version: string | null;
  explanation: ExplanationItem | null;
  calibration_status?: string | null;
  confidence_index?: number | null;
  uncertainty_pct?: number | null;
  ood_score?: number | null;
  stability_index?: number | null;
  structural_overconfidence?: boolean | null;
  failure_fingerprint?: Record<string, any> | null;
  dominant_risk_drivers?: string[] | null;
  decision_mode?: string | null;
  decision_guidance?: string | null;
  within_trust_horizon?: boolean | null;
  operational_trust_horizon_hours?: number | null;
  lead_hours?: number | null;
  valid_time?: string | null;
  issue_time?: string | null;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface ModelEvaluationMetrics {
  roc_auc: number;
  brier_score: number;
  pr_auc: number;
  expected_calibration_error: number;
  f1_score: number;
  accuracy: number;
  decision_threshold: number;
}

export interface ModelEvaluationResponse {
  model_name: string;
  model_version: string;
  model_type?: string;
  data_version?: string;
  evaluation_dataset?: string;
  sample_count?: number;
  calibration?: {
    is_calibrated: boolean;
    method?: string;
    decision_threshold?: number;
  };
  metrics?: ModelEvaluationMetrics;
  feature_importance?: Record<string, number>;
}

export interface ApiErrorDetail {
  loc?: (string | number)[];
  msg?: string;
  type?: string;
  ctx?: Record<string, unknown>;
}

export interface ApiError {
  error: string;
  message?: string;
  detail?: string | ApiErrorDetail[];
  retry_after_seconds?: number;
  request_id?: string;
  status_code?: number;
}

export type HorizonPreset = '7_DAY' | '10_DAY' | '16_DAY';

export interface HorizonPointResult {
  lead_hours: number;
  lead_days: number;
  valid_time: string;
  response: PredictionResponse | null;
  status: 'SUCCESS' | 'ABSTAINED' | 'ERROR';
  error_message?: string;
}

export interface HorizonTimelineRequest {
  location: string;
  variable?: SupportedVariable;
  issue_time?: string;
  preset?: HorizonPreset;
  custom_leads?: number[];
}

export interface HorizonTimelineResult {
  location: string;
  variable: string;
  issue_time: string;
  preset: HorizonPreset;
  points: HorizonPointResult[];
  successful_count: number;
  abstained_count: number;
  error_count: number;
}

export interface V3EvaluationMetrics {
  average_precision: number;
  pr_auc_trapezoidal: number;
  roc_auc: number;
  brier_score: number;
  bss_vs_e0: number;
  bss_vs_e1b: number;
  ece: number;
}

export interface V3ModelEvaluationResponse {
  model_name: string;
  model_version: string;
  model_family: string;
  feature_count: number;
  calibration_method: string;
  evaluation_dataset: string;
  evaluation_split?: string;
  evaluation_period: string;
  test_samples: number;
  test_cycles: number;
  benchmark_scope: string;
  evaluation_status: string;
  metrics: V3EvaluationMetrics;
  provenance: Record<string, any>;
  generalization_limits: string[];
}

export type DashboardMode = 'single' | 'standard_7d' | 'full_16d';
export type DashboardStatus = 'SUCCESS' | 'PARTIAL' | 'ABSTAINED';

export interface DashboardLocationContext {
  query: string;
  resolved_name?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  region_id?: string | null;
}

export interface DashboardTimelinePoint {
  lead_hours: number;
  lead_days: number;
  valid_time: string;
  bust_probability: number | null;
  risk_level: RiskLevel | null;
  trust_state: TrustState;
  abstain: boolean;
  reason_codes: string[];
  calibration_status?: string | null;
  decision_mode?: string | null;
  within_trust_horizon?: boolean | null;
  operational_trust_horizon_hours?: number | null;
  is_certified_horizon: boolean;
}

export interface DashboardSummary {
  available_points: number;
  abstained_points: number;
  total_points: number;
  max_bust_probability: number | null;
  max_risk_level: RiskLevel | null;
  max_risk_lead_hours: number | null;
  mean_bust_probability: number | null;
  elevated_risk_points: number;
  first_elevated_risk_lead_hours: number | null;
  overall_decision_mode: string;
}

export interface DashboardScientificContext {
  model_version: string;
  model_family: string;
  calibration_method: string;
  feature_count: number;
  probability_semantics: string;
  benchmark_scope: string;
  benchmark_lead_horizon_max_hours: number;
  operational_horizon_max_hours: number;
  historical_benchmark: V3EvaluationMetrics & {
    dataset: string;
    period: string;
    test_samples: number;
    test_cycles: number;
  };
  generalization_limits: string[];
}

export interface DashboardRequest {
  location: string;
  variable?: string;
  mode?: DashboardMode;
  issue_time?: string | null;
}

export interface DashboardIntelligenceResponse {
  status: DashboardStatus;
  location: DashboardLocationContext;
  variable: string;
  issue_time?: string | null;
  mode: DashboardMode;
  selected_prediction: PredictionResponse;
  timeline: DashboardTimelinePoint[];
  summary: DashboardSummary;
  scientific_context: DashboardScientificContext;
  request_id?: string | null;
}

export interface MultiLocationPredictionRequest {
  locations: string[];
  variable?: string;
  target_date?: string;
  issue_time?: string;
  valid_time?: string;
  model_type?: string;
}

export interface MultiLocationPredictionItemResult {
  input_location: string;
  is_success: boolean;
  response: PredictionResponse;
}

export interface HistoricalAnalogItem {
  analog_id: string;
  target_date: string;
  similarity_score: number;
  distance: number;
  lead_hours: number;
  variable: string;
  forecast_value: number;
  observed_value: number;
  error_magnitude: number;
  bust_occurred: boolean;
  synoptic_regime: string;
  is_eligible: boolean;
  exclusion_reason?: string | null;
}

export interface HistoricalAnalogResponse {
  query_event_id?: string;
  variable: string;
  lead_hours: number;
  total_candidates: number;
  eligible_analogs_count: number;
  analogs: HistoricalAnalogItem[];
  status: 'ELIGIBLE_FOUND' | 'NO_ELIGIBLE_ANALOGS';
  message: string;
}

export interface RiskMapItem {
  region_id: string;
  region_name: string;
  bust_probability: number;
  risk_band: 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED' | 'GRAY';
  coordinates: [number, number]; // [lat, lon]
  boundary_coordinates?: [number, number][];
  area_fraction?: number;
  centroid_error_km?: number;
}

export interface RiskMapResponse {
  valid_time: string;
  variable: string;
  lead_hours: number;
  regions: RiskMapItem[];
  overall_risk_band: string;
}

export interface DataProvenanceResponse {
  schema_version: string;
  primary_sources: {
    forecast_model: string;
    forecast_resolution: string;
    reference_analysis: string;
    reference_resolution: string;
    verification_only_invariant: string;
  };
  artifacts_checksums: Record<string, string>;
  licenses: Record<string, { license: string; uri: string; attribution: string }>;
  pipeline_lineage: string[];
}

export interface ReliabilityDiagramData {
  prob_pred: number[];
  prob_true: number[];
  bin_counts: number[];
  bin_edges: number[];
  ece: number;
  mce: number;
}

export interface ComprehensiveEvaluationResponse {
  model_name: string;
  model_version: string;
  sample_count: number;
  bust_count: number;
  bust_prevalence: number;
  discrimination_and_probability: {
    pr_auc: number;
    average_precision?: number;
    roc_auc: number;
    brier_score: number;
    log_loss_value: number;
    expected_calibration_error: number;
    max_calibration_error: number;
    calibration_slope?: number;
    calibration_intercept?: number;
    reliability_diagram: ReliabilityDiagramData;
  };
  warning_lead_time_gain: {
    total_bust_events: number;
    median_lead_time_gain_hours: number;
    mean_lead_time_gain_hours: number;
    pct_flagged_24h_veyra: number;
    pct_flagged_48h_veyra: number;
    pct_flagged_72h_veyra: number;
    pct_flagged_24h_spread: number;
    pct_flagged_48h_spread: number;
    pct_flagged_72h_spread: number;
    lead_time_gain_24h_gain_pct: number;
    lead_time_gain_48h_gain_pct: number;
    lead_time_gain_72h_gain_pct: number;
  };
  spatial_metrics?: {
    fss_by_scale: Record<string, number>;
    mean_fss: number;
    fss_useful_scale?: string;
    object_iou: number;
    centroid_error_km?: number;
    top_k_recall: number;
    k_value: number;
    pred_area_fraction: number;
    obs_area_fraction: number;
    area_fraction_error: number;
  };
  safety_coverage_risk: {
    coverage_risk_curve: Array<{
      rejection_threshold: number;
      coverage: number;
      risk: number;
      abstention_rate: number;
      high_confidence_error_rate: number;
      review_burden_cases: number;
    }>;
    overall_abstention_rate: number;
    retained_samples_count: number;
    retained_case_brier_score?: number;
    retained_case_pr_auc?: number;
    high_confidence_error_rate: number;
    risk_reduction_pct: number;
  };
  stratified_evaluation?: {
    total_samples: number;
    total_busts: number;
    dimensions: string[];
    strata: Record<
      string,
      Array<{
        dimension: string;
        stratum_value: string;
        sample_count: number;
        bust_count: number;
        bust_prevalence: number;
        status: string;
        pr_auc?: number;
        roc_auc?: number;
        brier_score?: number;
      }>
    >;
  };
  operational_burden: {
    total_samples: number;
    total_cycles: number;
    decision_threshold: number;
    total_alerts: number;
    false_alerts: number;
    false_alerts_per_cycle: number;
    alert_rate: number;
    alert_persistence_rate?: number;
    alert_flicker_rate?: number;
    estimated_review_time_hours: number;
    estimated_review_hours_per_cycle: number;
    recall_at_5pct_budget: number;
    recall_at_10pct_budget: number;
    recall_at_20pct_budget: number;
  };
  explanation_quality: {
    total_evaluated_cases: number;
    mean_attribution_stability: number;
    mean_rank_correlation: number;
    mean_fidelity_drop: number;
    fidelity_score: number;
    forecaster_agreement_rate?: number;
    analog_eligibility_rate?: number;
    top_drivers_frequency: Record<string, number>;
    summary_verdict: string;
  };
  evaluation_status: string;
  generated_at?: string;
}


