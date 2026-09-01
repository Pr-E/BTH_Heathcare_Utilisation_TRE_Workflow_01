# TRE step-by-step execution and translation guide

This guide is the operational sequence to follow after the repository has been approved for ingress. It is designed so another analyst can stop after any stage, inspect aggregate QA, and resume without modifying Python code.

## A. One-time environment setup

From the project root:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python -m compileall -q src scripts tests
python -m pytest -q
```

Expected outcome:

- package imports without error;
- all source/scripts compile;
- toy-data tests pass;
- no real TRE data are needed by the tests.

Do not proceed to real data if the deployment checks fail.

---

## B. Configuration freeze before patient-level execution

### 1. Confirm real source directory

Review `config/pipeline_tre.yaml`:

```yaml
data_source:
  mode: tre
  tre_dir: src
```

Change `tre_dir` only if the approved source folder differs.

### 2. Enter approved BTH extract coverage dates

Review `config/workflow_tre.yaml`:

```yaml
project:
  study_start_date: null
  study_end_date: null
```

Replace `null` with dates from approved BTH/TRE source documentation. Do **not** reuse the synthetic simulator dates.

### 3. Confirm analytical index semantics

Only after review of the real source definition should this become true:

```yaml
cohort:
  analytical_index_semantics_confirmed_for_workflow: true
```

`index_is_programme_start` remains false unless genuine programme-start data establish otherwise.

---

# Stage-by-stage run sequence

## Stage 00 — Preflight

```bash
python scripts/run_00_preflight.py
```

Purpose:

- verify all six real files exist;
- verify required canonical fields/candidate identifiers exist;
- verify real study window has been supplied;
- verify cohort/index interpretation flags;
- verify propensity covariates do not contain known post-index fields;
- block unsafe execution before patient-level transformations.

Inspect:

- terminal `BLOCKERS` section;
- `outputs/qa/00_tre_preflight.csv`;
- `outputs/audit/stage_summaries/00_preflight_summary.md`.

**Decision:** every mandatory blocker must be resolved before Stage 01.

Next command printed by a passing run:

```bash
python scripts/run_01_ingestion.py
```

---

## Stage 01 — Ingestion + schema mapping

```bash
python scripts/run_01_ingestion.py
```

Purpose:

- read each approved source extract;
- apply configured source-to-canonical column mapping;
- validate minimum schema;
- retain/report approved extra fields;
- write canonical ingested copies without analytical cleaning or cohort derivation.

Key terminal findings:

- rows and columns per table;
- unique patient/event/spell counts where configured;
- missing required fields;
- extra-field counts;
- canonical schema/order status.

Inspect:

- `outputs/qa/01_ingestion_summary.csv`
- Stage 01 audit summary.

**Decision:** required canonical fields must be present. Mapping issues are fixed in YAML, not by ad-hoc analysis-code edits.

Next:

```bash
python scripts/run_02_cleaning.py
```

---

## Stage 02 — Deterministic cleaning + missingness audit

```bash
python scripts/run_02_cleaning.py
```

Purpose:

- resolve real patient/event hash roles by cross-source overlap/uniqueness;
- normalise blank strings to explicit missing values;
- remove fully blank rows and exact duplicates;
- remove duplicate ED patient-event keys under the configured rule;
- parse dates and numeric fields;
- replace configured ED sentinel/invalid values with missing rather than guessing;
- identify chronology/integrity problems;
- quantify missingness per column and compare Sports-linked vs Wider MSK.

Key terminal findings per table:

- rows/columns and unique identifiers;
- rows removed;
- total missing-cell count and percentage;
- number of columns affected;
- critical missingness;
- top missing variables with n/%/classification;
- chronology/integrity issues.

Final Stage 02 comparison:

- Sports-linked vs Wider-MSK missingness percentage-point differences;
- configured group-difference flags.

Inspect:

- `02_identifier_resolution_qa.csv`
- `02_cleaning_actions_and_issues.csv`
- `02_cleaned_table_summary.csv`
- `02_column_missingness.csv`
- `02_missingness_group_comparison.csv`

**Decision:** critical missingness or ambiguous identifiers require review before preprocessing. Stage 02 does not impute analytical covariates.

Next:

```bash
python scripts/run_03_preprocessing.py
```

---

## Stage 03 — Preprocessing / source-grain harmonisation

```bash
python scripts/run_03_preprocessing.py
```

Purpose:

- reverify identifier choices after cleaning;
- create canonical MSK referral/pathway views;
- derive pathway intervals;
- create ED attendance view;
- collapse inpatient episode rows to one admission/spell grain;
- reconcile source versus date-derived pathway timeframe.

Key terminal findings:

- chosen identifier columns and aggregate evidence;
- inpatient episode rows versus unique spells and percentage reduction;
- processed patient/event/spell counts;
- timeframe agreement metrics.

Inspect:

- `03_identifier_resolution_qa.csv`
- `03_preprocessing_summary.csv`

**Decision:** confirm that admission/spell grain is sensible and identifier selections remain stable.

Next:

```bash
python scripts/run_04_linkage.py
```

---

## Stage 04 — Patient spine + linkage QA

```bash
python scripts/run_04_linkage.py
```

Purpose:

- construct the pseudonymised patient spine;
- attach pathway anchors/demographics;
- retain source-presence flags;
- quantify linkage overlap separately for Sports-linked and Wider MSK source families.

Key terminal findings:

- spine n;
- Sports-linked/Wider candidate counts;
- source-presence counts;
- MSK-to-ED and MSK-to-inpatient overlap by source family.

Inspect:

- `04_linkage_overlap_qa.csv`
- patient spine internally only.

**Decision:** investigate meaningful differential linkage completeness before interpreting utilisation differences.

Next:

```bash
python scripts/run_05_cohort.py
```

---

## Stage 05 — Cohort, analytical index and observation windows

```bash
python scripts/run_05_cohort.py
```

Purpose:

- assign working pathway group;
- assign source-relative analytical index;
- calculate 365-day baseline window;
- calculate up-to-365-day follow-up with study/death censoring;
- apply age/alive/baseline-completeness eligibility rules.

Key terminal findings:

- working and eligible denominators by group;
- complete baseline/full follow-up counts;
- follow-up days distribution;
- observation coverage dates;
- exclusion reasons;
- index strategy QA by group.

Inspect:

- `05_cohort_flow.csv`
- `05_cohort_exclusions.csv`
- `05_index_strategy_qa.csv`
- analysis index internally only.

**Decision:** denominator and index/window construction must be clinically/data-semantically credible before outcome engineering.

Next:

```bash
python scripts/run_06_outcomes.py
```

---

## Stage 06 — Event ledger + outcome features

```bash
python scripts/run_06_outcomes.py
```

Purpose:

- construct ED attendance events;
- count inpatient outcomes at spell/admission level;
- classify emergency inpatient admissions using reviewed `MethodOfAdmission` rules;
- classify events into baseline/follow-up/outside window;
- calculate counts, person-time and rates.

Key terminal findings:

- ledger event counts by type/window;
- eligible patient n;
- crude baseline/follow-up rates per 100 person-years;
- zero-event patient percentages.

Inspect:

- `06_outcome_feature_qa.csv`
- `06_outcome_rate_qa.csv`
- event ledger and patient outcomes internally only.

**Decision:** validate event grain and emergency-admission coding before interpreting rates.

Next:

```bash
python scripts/run_07_descriptive.py
```

---

## Stage 07 — Descriptive / EDA

```bash
python scripts/run_07_descriptive.py
```

Purpose:

- describe cohort composition and data quality;
- quantify baseline demographic/geographic/utilisation differences;
- report crude baseline/follow-up utilisation;
- diagnose follow-up availability, missingness, timing, zero-heavy outcomes and source coverage.

Key terminal findings:

- eligible denominators;
- largest unadjusted SMD and top imbalanced features;
- largest effective missingness by group;
- crude baseline/follow-up rates;
- crude pre/post change;
- flagged EDA diagnostics.

Inspect:

- `outputs/descriptive/tables/descriptive_key_findings.csv`
- Table 1 and SMD tables;
- descriptive figures/tables.

**Decision:** this stage is unadjusted. Do not call crude differences pathway effects.

Next:

```bash
python scripts/run_08_comparative.py
```

---

## Stage 08 — Propensity design + comparative pre/post models

```bash
python scripts/run_08_comparative.py
```

Purpose:

1. logistic-regression propensity model using pre-index covariates only;
2. structural positivity restriction;
3. empirical propensity common support;
4. ATT weighting;
5. SMD balance assessment;
6. 1:3 propensity-score matching sensitivity;
7. ATT-weighted comparative pre/post Poisson GEE;
8. Negative Binomial GEE sensitivity;
9. PSM comparative sensitivity.

Key terminal findings:

- structural exclusions by group;
- common-support bounds and supported n;
- ATT effective sample size;
- maximum post-ATT |SMD| and PASS/FAIL;
- PSM max |SMD| and matched sample;
- largest before/after covariate imbalances;
- crude comparative change;
- outcome RRR, 95% CI, p-value and model status for primary/sensitivity models.

**Hard gate:** if ATT balance exceeds the configured threshold, model interpretation is blocked and all design diagnostics are still saved for review.

Inspect:

- `design_overlap_audit.csv`
- `propensity_balance.csv`
- `propensity_logistic_model_terms.csv`
- `att_weight_diagnostics.csv`
- `propensity_score_distribution.csv`
- `comparative_results.csv`
- `primary_comparative_key_findings.csv`

**Interpretation:** adjusted association for measured covariates only; unmeasured confounding remains possible.

Next:

```bash
python scripts/run_09_clustering.py
```

---

## Stage 09 — Exploratory baseline utilisation clustering

```bash
python scripts/run_09_clustering.py
```

Purpose:

- identify baseline ED/inpatient/emergency-inpatient utilisation phenotypes;
- recompute K=2–6 diagnostics;
- assess cluster size/stability and winsorisation sensitivity;
- profile pathway-group composition after clustering;
- run mutually exclusive inpatient-dimension sensitivity.

Key terminal findings:

- selected and automatic best K;
- silhouette, Davies-Bouldin and stability ARI;
- cluster n/% and Sports/Wider counts;
- provisional phenotype descriptions;
- Cramér's V;
- sparse Sports-linked cluster warnings.

Inspect:

- `clustering_key_findings.csv`
- `clustering_summary.csv`
- `cluster_selection_metrics.csv`
- cluster profile/centroid/exposure tables.

**Interpretation:** exploratory/descriptive only. Do not interpret cluster-specific trajectories as treatment-effect heterogeneity.

Next:

```bash
python scripts/run_10_extended_optional.py
```

only if the optional extension has been enabled and justified. Otherwise proceed to Stage 11.

---

Next:

```bash
python scripts/run_11_release_audit.py
```

---

## Stage 10 — Output release pre-screen

```bash
python scripts/run_11_release_audit.py
```

Purpose:

- identify obvious patient-level/internal-only files;
- flag aggregate outputs containing configured small-cell risks;
- prepare internal disclosure-review information.

**This is not export approval.** Formal local TRE disclosure control remains mandatory.

---

# Reviewer summary after any run

```bash
python scripts/review_audit_summary.py
```

Use:

- `outputs/audit/reviewer_summary.md` for human review;
- `outputs/audit/reviewer_summary.csv` for stage-status tracking.

# Full orchestrated run

Only after the stage-by-stage first real-data run has been reviewed:

```bash
python scripts/run_all_tre.py
```

or resume a validated interval:

```bash
python scripts/run_all_tre.py --from-stage outcomes --to-stage clustering
```

The first execution on real data should remain stage-by-stage so every assumption and decision gate is visible.
