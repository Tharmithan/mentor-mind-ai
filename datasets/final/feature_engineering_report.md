# Feature Engineering Report (Day 4)

*Generated: 2026-05-25T10:09:46.895869+00:00*

## Custom features created

| Feature | Formula / logic |
|---------|-----------------|
| `consistency_score` | 100 − scaled std(G1, G2, G3) — stable grades = high consistency |
| `productivity_index` | scale(study_hours × attendance% / (failures + 1)) |
| `exam_readiness_score` | study_scaled×0.4 + attendance×0.3 + assignment_completion×0.3 |
| `assignment_completion_score` | 100 − past_failures×25 (capped 0–100) |
| `grade_momentum_score` | scale(final_grade − G1) — improvement signal |

## Feature selection (Random Forest)

- Features evaluated: **28**
- Features kept: **5**
- Features dropped: **23**
- Hold-out R²: **0.9879**

### Kept (ranked by importance)

| Rank | Feature | Importance % | Engineered |
|------|---------|--------------|------------|
| 1 | `grade_period_2` | 60.57% | no |
| 2 | `grade_momentum` | 17.35% | yes |
| 3 | `grade_momentum_score` | 16.11% | no |
| 4 | `consistency_score` | 3.18% | yes |
| 5 | `grade_period_1` | 1.49% | no |

### Dropped (weak features)

- `productivity_index`
- `exam_readiness_score`
- `going_out`
- `absences`
- `attendance_pct`
- `family_relationship`
- `weekend_alcohol`
- `father_education`
- `free_time`
- `wellness_score`
- `weekday_alcohol`
- `travel_time`
- `mother_education`
- `assignment_completion_score`
- `family_support`
- `study_efficiency`
- `study_hours`
- `school_support`
- `extracurricular`
- `internet_access`
- `gender`
- `past_failures`
- `wants_higher_ed`

## Behavioral model (no prior grades — MentorMind API)

- Features kept: **20** · R²: **0.6526**

| Rank | Feature | Importance % |
|------|---------|--------------|
| 1 | `grade_momentum_score` | 48.99% |
| 2 | `productivity_index` | 6.65% |
| 3 | `consistency_score` | 6.13% |
| 4 | `mother_education` | 3.27% |
| 5 | `exam_readiness_score` | 2.82% |
| 6 | `wellness_score` | 2.72% |
| 7 | `free_time` | 2.61% |
| 8 | `father_education` | 2.58% |

## Outputs

| File | Description |
|------|-------------|
| `performance_features_full.csv` | All base + engineered features |
| `performance_ml_ready.csv` | Selected (includes grades if strong) |
| `performance_ml_ready_behavioral.csv` | Study/attendance/readiness only |
| `train.csv` / `test.csv` | 80/20 split |
| `train_behavioral.csv` | Behavioral split for API-style model |
