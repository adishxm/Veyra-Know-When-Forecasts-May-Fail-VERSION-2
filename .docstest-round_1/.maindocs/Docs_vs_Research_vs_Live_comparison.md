# Docs vs Research Docs vs Live Product — Complete One-by-One Comparison

**Sources compared:**
- **A. Main Docs** = `SIH26079 — Forecast-Bust Sentinel (1) (1).md` (v2.0, compiled 24 Aug 2026)
- **B. Research Docs** = `SIH26079_120_RESEARCH_PAPERS_MERGED.md` (120 study briefs) **+** repo science docs Day-22/Day-23 (cited where they add substance)
- **C. Live Product** = Render backend + GitHub Pages frontend + GitHub repo (evidence: Sentinel audit V1–V9, ~110 timestamped requests, 2026-09-17/18)

**Legend — Live Product verdict:**
- ✅ **HAVE** — live, verified with evidence
- ⚠️ **PARTIAL** — exists but incomplete / renamed / weaker than specified
- ❌ **MISSING** — specified in docs/research but absent live
- ➕ **EXTRA** — live has it, docs don't specify it
- 📜 **STALE-DOC** — docs/research describe old reality; live has moved on (or vice versa)

---

## A. Mission, scope & positioning

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| A1 | Reliability layer over NWP (grades forecasts, doesn't make them) | ✅ §1 core thesis | ✅ Files 001/010 | ✅ Live: scores GEFS forecasts, abstains, never issues weather | ✅ HAVE |
| A2 | Human-in-the-loop; no autonomous emergency decisions | ✅ §1, §12 | ✅ File 006 | ⚠️ Guidance text says "human review"; no explicit human-approval gate/state in API | ⚠️ PARTIAL |
| A3 | Public-proxy prototype; NCMRWF validation future/conditional | ✅ §2.1, §7 | ✅ Truth boundary in all 120 files + Day-22/23 caveats | ⚠️ Limits text honest, BUT serves uncertified geos/vars/horizons as HIGH_CONFIDENCE (V1–V3 S1s) | ⚠️ PARTIAL |
| A4 | India-focused scope | ✅ §3.1 regions | ✅ Files 018/023, Day-22 (25 stations) | ⚠️ Certified 25 India stations, but serves London/NY/pole/ocean without warning | ⚠️ PARTIAL |
| A5 | Day 1–10 lead times | ✅ §3.1 | ✅ File 042 | ⚠️ Certified 24–240h ✅; but also serves 12/18h sub-24h + 264–384h uncertified, all SUCCESS | ⚠️ PARTIAL |
| A6 | First variables: Z500 + t2m (smooth, verifiable) | ✅ §3.1 | ✅ Files 052/061 | ❌ Live vars: temperature_2m, wind_speed_10m, surface_pressure (+uncertified extras). No Z500 anywhere | ❌ MISSING |
| A7 | Region-based units (India core / admin / grid-patch) | ✅ §3.1, §6 | ✅ Files 042/058 | ❌ Live is station-point only (lat/lon + 25 fixed stations); no regions, no masks | ❌ MISSING |
| A8 | Fits inside IMD-style dissemination (not a rival) | ✅ PPT/doc positioning | — (not covered) | ❌ 0 IMD mentions in repo guide; no integration artefact — prose only (V5) | ❌ MISSING |
| A9 | Theme = Disaster Management | ✅ Docs say this | — | ➕/📜 PPT says "Smart Automation" (wrong per official SIH index — docs are right, V5) | 📜 STALE-DOC (PPT side) |

## B. Bust definition & labeling

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| B1 | q95 conditional percentile label (per region/var/lead/season) | ✅ §8.1 project decision | ✅ File 054 | ✅ Day-22 certifies q95 per location/var/lead-bin, Train-only, 100% parity | ✅ HAVE |
| B2 | Sensitivity reruns at q90 / q97.5 / q99 | ✅ §8.1 required | ✅ File 055 | ❌ No sensitivity outputs disclosed anywhere | ❌ MISSING |
| B3 | Ambiguity / gray-band flag near threshold | ✅ §8.2 | ✅ File 056 | ❌ No ambiguity field in any response | ❌ MISSING |
| B4 | Continuous normalized error + severity classes (low/mod/severe) | ✅ §8.2, §12 | ✅ File 057 | ❌ No severity output; only p + risk band | ❌ MISSING |
| B5 | Neighborhood / object-aware spatial labels (FSS-style) | ✅ §8.2 | ✅ File 058 | ❌ No spatial labels of any kind | ❌ MISSING |
| B6 | Event grouping (one cyclone episode never split train/test) | ✅ §8.3 | ✅ Files 049/059 | ⚠️ Cycle-block bootstrap used; explicit event grouping not evidenced | ⚠️ PARTIAL |
| B7 | Label versioning (label_version in every artefact) | ✅ §8.1, §14 | ✅ File 060 | ⚠️ "Day 22 label definitions" string only; no `label_version` field in responses | ⚠️ PARTIAL |
| B8 | Thresholds/normalization fit on Train only | ✅ §8.1, §10.4 | ✅ Files 053/054 | ✅ Day-22 certified: Train-only, 0 Val/Test rows in thresholds | ✅ HAVE |

## C. Data sources & pipeline

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| C1 | GEFS ensemble input | ✅ §7.1 | ✅ File 019 | ✅ Live via Open-Meteo adapter, N=31, upstream SUCCESS (V1/V4) | ✅ HAVE |
| C2 | WeatherBench 2 benchmark track | ✅ §7.1, §5 | ✅ Files 020/028/034 | ❌ Benchmark is custom canonical reforecast, not WB2; WB2 unused live | ❌ MISSING |
| C3 | ERA5 as verification-only reference (never a predictor) | ✅ §7.1–7.2 | ✅ Files 020/035/036 | ⚠️ Claimed; plausible (no truth fields in responses, leakage guard in code) but no provenance endpoint to verify | ⚠️ PARTIAL |
| C4 | NCMRWF NEPS future integration | ✅ §7.1 future | ✅ Files 018/023 | ❌ Correctly absent (future) — kept conditional as specified | ❌ MISSING (correctly) |
| C5 | Multi-model disagreement input (IFS/AIFS/GFS) | ✅ §7.1 optional | ✅ File 066 | ❌ Not built (optional; correctly deferred) | ❌ MISSING (correctly) |
| C6 | Zarr/NetCDF gridded field storage | ✅ §7.3 | ✅ File 038 | ❌ No evidence; product is point-based | ❌ MISSING |
| C7 | Parquet feature/label tables | ✅ §7.3 | ✅ File 039 | ✅ Canonical parquet 34,062,126 bytes, SHA-certified (Day-22) | ✅ HAVE |
| C8 | PostgreSQL metadata/provenance store | ✅ §7.3, §16 | ✅ File 040 | ❌ No evidence; metrics are process-local (reset on restart) | ❌ MISSING |
| C9 | Immutable manifests + checksums per artefact | ✅ §7.3 | ✅ File 037 | ⚠️ SHA-256 published in Day-22/23 docs, but NOT exposed via any API | ⚠️ PARTIAL |
| C10 | Data-quality gates → Gray/abstain, never silent fill | ✅ §7.4 | ✅ File 045 | ⚠️ Abstain paths work (INVALID_LOCATION, DATA_NOT_READY); Gray band itself missing | ⚠️ PARTIAL |
| C11 | License/terms URI per dataset snapshot | ✅ §7.3 | ✅ File 032 | ❌ Not exposed anywhere | ❌ MISSING |

## D. Feature engineering

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| D1 | Ensemble geometry (mean/std/IQR/skew/tails/spread-growth…) | ✅ §9 | ✅ Files 061/062 | ✅ 16 ensemble stats in 50-feature contract (verified in feature_names.json) | ✅ HAVE |
| D2 | Cycle-revision trajectory features (THE lead innovation) | ✅ §9.1 | ✅ Files 063/064 | ❌ In contract but **0 booster splits** (Day-22); live values always 0.0 — structurally dead (V2–V4) | ❌ MISSING |
| D3 | Regime / monsoon context features | ✅ §9 | ✅ File 065 | ❌ No regime fields in contract or outputs | ❌ MISSING |
| D4 | Analog similarity features | ✅ §9 | ✅ File 067 | ❌ No analog features, endpoint, or UI | ❌ MISSING |
| D5 | Static/contextual (region, season, lead, model version, grid) | ✅ §9 | ✅ Files 042/065 | ⚠️ Lead + time harmonics ✅; region/model-version/grid ❌ | ⚠️ PARTIAL |
| D6 | Quality/safety features (missingness, staleness, member count) | ✅ §9 | ✅ File 045 | ⚠️ member_count + has_full_ensemble ✅; staleness/missingness signals ❌ | ⚠️ PARTIAL |
| D7 | availability_time ≤ issue_time hard enforcement | ✅ §9 hard control | ✅ Files 047/048 | ⚠️ Time validation correct (+05:30/millis OK); but no availability timestamps exposed; issue_time is metadata-only (V4 code proof) | ⚠️ PARTIAL |
| D8 | Forbidden future-feature exclusion (truth/labels never predictors) | ✅ §9, §10.4 | ✅ File 048 | ✅ Day-22 certified + FORBIDDEN_GROUND_TRUTH_FIELDS guard in serving code | ✅ HAVE |

## E. Models, baselines & training discipline

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| E1 | Calibrated LightGBM/XGBoost core | ✅ §10.1 decision | ✅ File 070 | ✅ V3 LightGBM + isotonic served live (default model) | ✅ HAVE |
| E2 | E0 climatology baseline | ✅ §10.2 | ✅ File 068 | ✅ Day-23: E0 AP 0.0622, Brier anchor | ✅ HAVE |
| E3 | E1 persistence / previous-cycle baseline | ✅ §10.2 | ✅ File 068 | ⚠️ E1b 3-moment logistic exists; pure persistence variant unclear | ⚠️ PARTIAL |
| E4 | E2 spread-only baseline | ✅ §10.2 | ✅ File 069 | ✅ Legacy spread ROC/PR + E1b 3-moment (mean/spread/lead) | ✅ HAVE |
| E5 | E3 logistic regression on issue-safe features | ✅ §10.2 | ✅ File 069 | ✅ E2 23-feature logistic + serving baseline-logistic-v1.0 | ✅ HAVE |
| E6 | Go/no-go rule (beat baselines w/o calibration/abstention damage) | ✅ §10.3 | ✅ File 090 | ✅ Day-23 RETAIN_WITH_TARGETED_FOLLOWUP + 1000× paired bootstrap (abstention-burden metric still unreported) | ✅ HAVE |
| E7 | Chronological splits + temporal embargoes | ✅ §10.4 | ✅ File 049 | ✅ 2000–13 / 14–16 / 17–19 + 14-day & 21-day purges, 0 contaminated rows | ✅ HAVE |
| E8 | Event / region / model-version holdouts | ✅ §10.4 | ✅ File 049 | ❌ Temporal-only; Day-22 explicitly: NOT a geographic holdout | ❌ MISSING |
| E9 | Automated leakage integration tests | ✅ §10.4 | ✅ File 050 | ⚠️ Day-22 7-stage read-only cert ✅; CI-runnable test badges unevidenced | ⚠️ PARTIAL |

## F. Calibration, OOD & abstention

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| F1 | Isotonic / Platt / beta calibration on later block | ✅ §11.1 | ✅ Files 071/072 | ✅ Isotonic on Validation for V3 (ECE 0.0064); sigmoid for legacy | ✅ HAVE |
| F2 | Calibration reporting (Brier, reliability diagram, ECE, slope) | ✅ §11.1 | ✅ Files 083/084 | ⚠️ Brier + ECE served ✅; reliability diagrams, slope/intercept ❌ | ⚠️ PARTIAL |
| F3 | EasyUQ / DRN optional post-hoc methods | ✅ §11.1 optional | ✅ File 073 | ❌ Not built (correctly deferred) | ❌ MISSING (correctly) |
| F4 | Conformal prediction (conditional coverage only) | ✅ §11.2 gated | ✅ File 074 | ❌ No conformal fields/intervals — frontend mentions it anyway (overclaim, V1–V6) | ❌ MISSING |
| F5 | OOD scoring (distance, drift, regime novelty…) | ✅ §11.3 | ✅ File 075 | ❌ ood_score constant 0.0 everywhere incl. North Pole; schema admits "diagnostic only" | ❌ MISSING |
| F6 | NORMAL / UNUSUAL / OOD / ABSTAIN states | ✅ §11.3 table | ✅ File 076 | ❌ Different vocabulary (HIGH_CONFIDENCE…/UNAVAILABLE); no UNUSUAL/OOD states | ❌ MISSING |
| F7 | Selective abstention + coverage-risk evaluation | ✅ §11.4 | ✅ Files 077/088 | ⚠️ Abstention works (3 reason paths verified); coverage-risk curve + review-burden metrics unreported | ⚠️ PARTIAL |
| F8 | abstain=true ⇒ p_bust=null, never substituted | ✅ §15.1 hard rule | ✅ File 076 | ✅ Verified on every abstention path (invalid loc, past date, bad input) | ✅ HAVE |

## G. Outputs (per cycle / region / variable / lead)

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| G1 | p_bust calibrated probability | ✅ §12 | ✅ Files 071/094 | ✅ Served on every success path | ✅ HAVE |
| G2 | Probability interval / uncertainty band | ✅ §12 | ✅ File 074 | ❌ confidence_index/uncertainty_pct are boundary-distance heuristics, NOT intervals | ❌ MISSING |
| G3 | Severity estimate + versioned class | ✅ §12 | ✅ File 057 | ❌ Absent | ❌ MISSING |
| G4 | Spatial extent (area fraction, objects, centroids, risk field) | ✅ §12 | ✅ File 087 | ❌ Absent (point-only) | ❌ MISSING |
| G5 | Time-to-first-failure (first lead crossing threshold) | ✅ §12 | ✅ File 086 | ⚠️ Dashboard summary has first_elevated_risk_lead_hours + max_risk_lead_hours — closest equivalent | ⚠️ PARTIAL |
| G6 | Leadwise risk trajectory + trust state per lead | ✅ §12 | ✅ File 103 | ✅ Timeline (1/7/16 pts) + within_trust_horizon + is_certified_horizon per point | ✅ HAVE |
| G7 | Auditable reason codes (revision accel, spread-to-error…) | ✅ §12 | ✅ File 078 | ⚠️ SUCCESS/INVALID_LOCATION/DATA_NOT_READY + 3 fixed factors — far thinner than specified | ⚠️ PARTIAL |
| G8 | OOD status output | ✅ §12 | ✅ Files 075/076 | ⚠️ ood_score + trust_state fields exist but stub (always 0.0 / HIGH) | ⚠️ PARTIAL |
| G9 | Historical analog cards (similar past cases + outcomes) | ✅ §12 | ✅ Files 067/079/104 | ❌ No endpoint, no fields, zero frontend mentions | ❌ MISSING |
| G10 | Claim-scope banner (PUBLIC_PROXY_… etc.) | ✅ §12, §15 | ✅ File 120 | ⚠️ Limits text in eval + dashboard scientific_context; no per-prediction claim_scope field | ⚠️ PARTIAL |
| G11 | Verification status (pending → revealed) | ✅ §12, §17 | ✅ File 106 | ❌ No truth_status / verification field | ❌ MISSING |
| G12 | Risk bands Green/Yellow/Orange/Red/Gray | ✅ §12.1 | ✅ File 080 | ❌ Different system: LOW/MEDIUM/HIGH/CRITICAL (0.20/0.50/0.75); no mapping table | ❌ MISSING |
| G13 | Plain-English decision guidance per band | ✅ §12.1 actions | ✅ File 080 | ✅ decision_mode + decision_guidance on every response | ✅ HAVE |

## H. API contract (docs specify 12 endpoints)

| # | Endpoint | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| H1 | GET /v1/health | ✅ §15 | ✅ File 095 | ✅ ok v0.1.0 | ✅ HAVE |
| H2 | GET /v1/models (registry listing) | ✅ §15 | ✅ Files 095/099 | ❌ Only /v1/model/evaluation (metrics for 2 models); no registry | ❌ MISSING |
| H3 | GET /v1/forecasts (cycles / replay cases) | ✅ §15 | ✅ File 095 | ❌ Absent | ❌ MISSING |
| H4 | POST /v1/predict | ✅ §15 | ✅ File 095 | ✅ Full-featured + validated + abstains correctly | ✅ HAVE |
| H5 | GET /v1/risk-map (GeoJSON / field URI) | ✅ §15 | ✅ Files 095/102 | ❌ Absent | ❌ MISSING |
| H6 | GET /v1/risk-trajectory | ✅ §15 | ✅ Files 095/103 | ⚠️ Covered by POST /v1/dashboard/intelligence (different contract, richer payload) | ⚠️ PARTIAL |
| H7 | GET /v1/analogs | ✅ §15 | ✅ Files 095/104 | ❌ Absent | ❌ MISSING |
| H8 | GET /v1/explanation (reason codes + SHAP + analogs + scope) | ✅ §15 | ✅ Files 095/104 | ⚠️ Inline explanation object only (3 fixed factors, no SHAP, no analogs) | ⚠️ PARTIAL |
| H9 | GET /v1/metrics (eval metrics + CI + split + scope) | ✅ §15 | ✅ Files 095/101 | ⚠️ Split/renamed: /v1/metrics = ops counters; eval metrics at /v1/model/evaluation | ⚠️ PARTIAL |
| H10 | GET /v1/metadata (data/model/license/claim versions) | ✅ §15 | ✅ File 095 | ❌ Absent | ❌ MISSING |
| H11 | GET /v1/data-provenance (URLs, checksums, lineage) | ✅ §15 | ✅ File 095 | ❌ Absent | ❌ MISSING |
| H12 | GET /v1/export (CSV/Parquet/GeoJSON/NetCDF) | ✅ §15 | ✅ File 095 | ❌ Absent | ❌ MISSING |
| H13 | Standard error shape + stable codes + request_id | ✅ §15.2 | ✅ File 096 | ⚠️ VALIDATION_ERROR + req_* ✅, clean, no leaks; docs' code list (DATA_DELAYED, OOD_ABSTAIN…) not implemented | ⚠️ PARTIAL |
| H14 | ➕ POST /v1/predict/batch (dedup, isolation, ordering) | — not specified | — | ✅ Verified: dedup, per-location isolation, deterministic order | ➕ EXTRA |
| H15 | ➕ POST /v1/historical/batch (archive records) | — not specified | — | ✅ Verified: records + record_ids + isolation + 422s | ➕ EXTRA |
| H16 | ➕ POST /v1/dashboard/intelligence (1/7/16-day orchestration) | — not specified | — | ✅ Verified: timelines + summary + scientific_context + limits | ➕ EXTRA |
| H17 | ➕ Interactive Swagger /docs + /dashboard route | — not specified | — | ⚠️ /docs ✅ live; /dashboard = "Frontend build not found" (dead end) | ➕ EXTRA (half-broken) |

## I. Dashboard / UI (docs §17, §20 + research Files 101–107)

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| I1 | Map (Leaflet + GeoJSON risk objects) | ✅ §13–17 | ✅ File 102 | ⚠️ Leaflet + OSM map renders; no risk objects/fields on it | ⚠️ PARTIAL |
| I2 | Risk-trajectory chart (leadwise + intervals + trust) | ✅ §17 | ✅ File 103 | ✅ Timeline chart panel + certified/operational badges | ✅ HAVE |
| I3 | Evidence panel (top signals + values + timestamps) | ✅ §17 | ✅ File 104 | ⚠️ Top factors + archetype shown; no timestamps, no SHAP values | ⚠️ PARTIAL |
| I4 | Analog explorer ("No eligible analog found" state) | ✅ §17 | ✅ File 104 | ❌ No analog UI (0 mentions in bundle) | ❌ MISSING |
| I5 | Trust banners + abstention UI ("I don't know—human review") | ✅ §17 | ✅ File 105 | ⚠️ Abstention box exists; wording differs; no banner taxonomy | ⚠️ PARTIAL |
| I6 | Deterministic historical replay view (frozen case + reveal step) | ✅ §20 demo | ✅ File 106 | ❌ Live-mode only; no replay UI | ❌ MISSING |
| I7 | Model-vs-baseline toggle (full vs spread-only) | ✅ §20 demo | ✅ File 090 | ❌ Endpoint data only; no UI toggle | ❌ MISSING |
| I8 | Provenance drawer (sources, checksums, lineage) | ✅ §17 | ✅ File 095 | ⚠️ scientific_context panel (benchmark numbers + limits) — closest equivalent | ⚠️ PARTIAL |
| I9 | Loading / empty / delayed / degraded / error states | ✅ §17 table | ✅ File 105 | ⚠️ Standby notice + abstention alert exist; full state matrix untested (no browser) | ⚠️ PARTIAL |
| I10 | Research metrics page (PR-AUC, Brier, reliability, coverage-risk) | ✅ §17–18 | ✅ File 101 | ❌ No UI page; JSON endpoint only | ❌ MISSING |

## J. Evaluation framework (docs §18 + research Files 081–089)

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| J1 | PR-AUC primary (never ROC/accuracy alone) | ✅ §18.1 | ✅ File 082 | ✅ AP 0.2047 + PR-AUC-trap 0.2124 + ROC secondary | ✅ HAVE |
| J2 | Brier / log-loss / ECE / reliability / slope | ✅ §18.1 | ✅ Files 083/084 | ⚠️ Brier + ECE ✅; log-loss, slope/intercept, diagrams ❌ | ⚠️ PARTIAL |
| J3 | Warning lead-time gain vs spread-only (24/48/72h flagged) | ✅ §18.1 | ✅ File 086 | ❌ Unreported | ❌ MISSING |
| J4 | Spatial/object metrics (FSS, overlap, top-k, centroid) | ✅ §18.1 | ✅ File 087 | ❌ Unreported (no spatial outputs) | ❌ MISSING |
| J5 | Coverage-risk, retained-case, high-conf-error, abstention-rate | ✅ §18.1 | ✅ File 088 | ❌ Unreported | ❌ MISSING |
| J6 | Stratification (season/lead/region/var/regime/provider/version) | ✅ §18.1 | ✅ File 089 | ❌ Only anecdote (Goa 17.87% in Day-22 text) | ❌ MISSING |
| J7 | Block bootstrap confidence intervals | ✅ §8.3, §18 | ✅ File 089 | ✅ 1000× cycle-block paired bootstrap (Day-23) | ✅ HAVE |
| J8 | Operational burden (false alerts/cycle, persistence, review time) | ✅ §18.1 | ✅ File 080 | ❌ Unreported | ❌ MISSING |
| J9 | Explanation quality (stability, fidelity, forecaster agreement) | ✅ §18.1 | ✅ File 078 | ❌ Unmeasured (and F9-02 incoherence found instead) | ❌ MISSING |
| J10 | Deterministic reproducibility (same input → same score) | ✅ §18 | — | ✅ Byte-identical across ~110 requests / 9 versions | ✅ HAVE |

## K. Failure handling (docs §21 + research File 115) — key rows

| # | Failure → Specified fallback | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| K1 | Download failure → "data delayed", last good cycle, no invented risk | ✅ §21 | ✅ File 115 | ⚠️ Upstream-failure path never observed (0 failures); DATA_NOT_READY abstention exists for bad dates | ⚠️ PARTIAL |
| K2 | Incomplete forecast / missing member → preserve missingness or abstain | ✅ §21 | ✅ File 115 | ⚠️ has_full_ensemble feature exists; degraded behaviour untested live | ⚠️ PARTIAL |
| K3 | Model unavailable → calibrated spread-only / unavailable state | ✅ §21 | ✅ File 115 | ❌ No fallback evidenced; single model path always served | ❌ MISSING |
| K4 | OOD detected → abstain / human review, no confident number | ✅ §21 | ✅ Files 076/115 | ❌ OOD never triggers (stub) — pole/ocean get confident numbers | ❌ MISSING |
| K5 | No analog → "No eligible analog found" (valid outcome) | ✅ §21 | ✅ File 115 | ❌ No analog system at all | ❌ MISSING |
| K6 | Provider/model upgrade → shadow period + recalibration | ✅ §21–22 | ✅ File 110 | ❌ No shadow/version-holdout machinery evidenced | ❌ MISSING |

## L. Security, MLOps & reproducibility (docs §22 + research Files 099/100/109/110)

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| L1 | Model registry + promotion lifecycle (candidate→approved→serving) | ✅ §19/22 | ✅ File 099 | ⚠️ Frozen V3 + Day-23 RETAIN decision ≈ process on paper; no registry API/pointer | ⚠️ PARTIAL |
| L2 | Auth, RBAC, secrets, CORS, rate limits, input limits | ✅ §22 | ✅ File 100 | ❌ Public open API, no auth observed; input limits ✅ (maxItems 50) only | ❌ MISSING |
| L3 | Audit logs (request/job/prediction IDs, versions, latency) | ✅ §22 | ✅ File 100 | ⚠️ request_id ✅ on errors; prediction/job IDs, version logging ❌ | ⚠️ PARTIAL |
| L4 | Monitoring: drift, calibration, feedback, retraining proposals | ✅ §22 | ✅ File 110 | ❌ Ops counters only (requests/cache/upstream); no drift/calibration monitors | ❌ MISSING |
| L5 | Reproducibility package (manifests, cards, splits, seeds, changelog) | ✅ §22 | ✅ File 114 | ⚠️ Day-22/23 + checksums + manifests ≈ package in repo; no single bundle/API | ⚠️ PARTIAL |

## M. Currency & honesty (where docs/research trail the product)

| # | Capability / Claim | Main Docs | Research Docs | Live Product | Verdict |
|---|---|---|---|---|---|
| M1 | "No model has been trained or evaluated" | 📜 True 24 Aug; stale now | 📜 Stale in all 120 files | ✅ V3 trained, frozen, evaluated 10 Sep, serving live | 📜 STALE-DOC |
| M2 | "120 research papers merged" | — | 📜 Actually 120 templated study briefs (~90% boilerplate), not papers | — (real rigor is in Day-22/23 instead) | 📜 STALE-DOC (misnomer) |
| M3 | API/tech status ("specified, not claimed built") | 📜 Says unbuilt | 📜 Says unbuilt | ✅ Built, deployed, CI/CD, 92-test claim | 📜 STALE-DOC |
| M4 | Advanced models correctly gated (GNN/Transformer/diffusion/LLM agent) | ✅ §3.2 future | ✅ File 119 | ✅ Correctly absent | ✅ HAVE (correctly) |

---

## Totals

| Verdict | Count | Share of 118 rows |
|---|---|---|
| ✅ HAVE | **25** | 21% |
| ⚠️ PARTIAL | **35** | 30% |
| ❌ MISSING (incl. 3 correctly-deferred future items) | **50** | 42% |
| ➕ EXTRA (live-only, incl. 1 half-broken) | **4 rows** | — |
| 📜 STALE-DOC rows | 4 rows flagged | — |
| **Total rows** | **118** | |

*(✅+⚠️+❌ = 110 specified items; +4 live-only rows +4 currency rows = 118. "Correctly missing" future items C4/C5/F3 are honest gaps, not defects.)*

## Reading the table — 5 takeaways
1. **The spine is built**: GEFS→features→LightGBM→isotonic→risk+abstain→dashboard works end-to-end and is rock-stable. Core loop rows are overwhelmingly ✅/⚠️.
2. **The evidence layer is missing**: analogs, maps, provenance, severity, intervals, ambiguity flags, regime/disagreement features — nearly all ❌. Docs promise an *auditable* system; live is a *scoring* system.
3. **The safety layer is half-built**: abstention mechanics ✅, but OOD is a stub, certification gates don't exist (S1s), and horizon/issue_time are advisory-only.
4. **Evaluation is strong offline, thin live**: frozen benchmark + bootstrap ✅, but no lead-time gain, coverage-risk, stratification, burden, or replay-loop metrics.
5. **Docs trail reality in both directions**: stale "nothing built" claims (M1–M3) coexist with unbuilt promises (analogs/maps/provenance) — a doc-sync pass fixes both.

*Evidence pointers: V1 = baseline inventory · V2 = gap deepening · V3 = reproducibility · V4 = fetch-layer forensics + code refs · V5 = vendor/competitor · V6 = state · V7 = perf · V8 = adversarial · V9 = regression.*
