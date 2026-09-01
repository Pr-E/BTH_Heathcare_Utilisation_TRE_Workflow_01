# Code review map — annotated TRE workflow

This document is an index for code review. The source files contain module-level rationale, function docstrings and inline comments around non-obvious analytical operations. This map lets a reviewer move directly from a workflow question to the relevant file/function.

**Commenting convention:** comments explain *why* a transformation/model decision exists; docstrings explain *what* a function performs and the important interpretation boundary. Routine Python syntax is not redundantly commented on every line because doing so can obscure the analytical decisions being reviewed.

## Package map

| File | Primary role | Non-blank code lines | Comment-only lines |
|---|---|---:|---:|
| `src/bth_analysis/__init__.py` | Active Blackpool / BTH real-data TRE analysis package. | 6 | 2 |
| `src/bth_analysis/analysis/__init__.py` | Statistical/descriptive analysis modules for the Active Blackpool TRE workflow. | 4 | 0 |
| `src/bth_analysis/analysis/clustering.py` | Exploratory baseline healthcare-utilisation phenotyping for TRE data. | 1036 | 22 |
| `src/bth_analysis/analysis/comparative.py` | Primary and sensitivity comparative healthcare-utilisation models. | 844 | 19 |
| `src/bth_analysis/analysis/descriptive.py` | Stage 07: descriptive EDA, cohort characterisation and diagnostic figures. | 1532 | 17 |
| `src/bth_analysis/analysis/extended.py` | Optional exploratory/sensitivity analyses for the TRE workflow. | 471 | 1 |
| `src/bth_analysis/analysis/propensity.py` | Propensity-score design for the primary TRE comparative analysis. | 537 | 33 |
| `src/bth_analysis/audit.py` | Small, patient-safe audit/logging helpers used by every TRE workflow stage. | 185 | 3 |
| `src/bth_analysis/data_pipeline/__init__.py` | Public entry points for deterministic real-source data pipeline stages. | 5 | 3 |
| `src/bth_analysis/data_pipeline/cleaning.py` | Stage 02: deterministic source cleaning and data-quality checks. | 505 | 16 |
| `src/bth_analysis/data_pipeline/cohort.py` | Stage 05: freeze the comparative cohort, analytical index and observation windows. | 512 | 18 |
| `src/bth_analysis/data_pipeline/config.py` | Configuration/path helpers for real-source pipeline stages inside the TRE. | 47 | 4 |
| `src/bth_analysis/data_pipeline/identifiers.py` | Real-TRE identifier resolution for the six Active Blackpool source extracts. | 250 | 4 |
| `src/bth_analysis/data_pipeline/ingestion.py` | Stage 01: schema-aware ingestion of approved TRE extracts. | 200 | 2 |
| `src/bth_analysis/data_pipeline/linkage.py` | Stage 04: build the pseudonymised patient spine and source-coverage QA. | 298 | 8 |
| `src/bth_analysis/data_pipeline/mapping.py` | Map real TRE source aliases to the stable canonical analytical schema. | 34 | 5 |
| `src/bth_analysis/data_pipeline/missingness.py` | Column-level missingness audit for the deterministic TRE cleaning stage. | 202 | 4 |
| `src/bth_analysis/data_pipeline/outcomes.py` | Stage 06: construct patient-level healthcare-utilisation outcomes. | 419 | 12 |
| `src/bth_analysis/data_pipeline/preprocessing.py` | Stage 03: convert cleaned source tables into canonical analytical grains. | 639 | 15 |
| `src/bth_analysis/data_pipeline/qa.py` | Small aggregate QA helpers shared by source-data pipeline stages. | 89 | 4 |
| `src/bth_analysis/data_pipeline/schemas.py` | Canonical minimum schemas for the six real Active Blackpool/BTH extracts. | 143 | 21 |
| `src/bth_analysis/orchestration/__init__.py` | Production orchestration, readiness and release-audit entry points. | 5 | 0 |
| `src/bth_analysis/orchestration/preflight.py` | TRE preflight checks. | 256 | 6 |
| `src/bth_analysis/orchestration/readiness.py` | Configuration-level readiness checks for TRE translation and interpretation. | 78 | 3 |
| `src/bth_analysis/orchestration/release_audit.py` | Pre-screen candidate outputs before formal TRE disclosure control. | 141 | 2 |
| `src/bth_analysis/orchestration/tre.py` | End-to-end orchestration for the production TRE workflow. | 146 | 3 |
| `src/bth_analysis/workflow.py` | Shared configuration, path and reproducibility helpers for the TRE workflow. | 111 | 8 |
| `scripts/review_audit_summary.py` | Build one reviewer-facing audit summary from aggregate per-stage JSON files. | 118 | 9 |
| `scripts/run_00_preflight.py` | Run Stage: Preflight. | 16 | 12 |
| `scripts/run_01_ingestion.py` | Run Stage: Ingestion. | 16 | 12 |
| `scripts/run_02_cleaning.py` | Run Stage: Cleaning. | 16 | 12 |
| `scripts/run_03_preprocessing.py` | Run Stage: Preprocessing. | 16 | 12 |
| `scripts/run_04_linkage.py` | Run Stage: Linkage. | 16 | 12 |
| `scripts/run_05_cohort.py` | Run Stage: Cohort/index/windows. | 16 | 12 |
| `scripts/run_06_outcomes.py` | Run Stage: Outcome engineering. | 16 | 12 |
| `scripts/run_07_descriptive.py` | Run Stage: Descriptive/EDA. | 16 | 12 |
| `scripts/run_08_comparative.py` | Run Stage: Propensity + comparative modelling. | 16 | 12 |
| `scripts/run_09_clustering.py` | Run Stage: Exploratory clustering. | 16 | 12 |
| `scripts/run_10_extended_optional.py` | Run Stage: Optional extended analysis. | 16 | 12 |
| `scripts/run_11_release_audit.py` | Run Stage: Release pre-screen. | 16 | 12 |
| `scripts/run_all_tre.py` | Command-line orchestration entry point for the reviewed real-data TRE workflow. | 44 | 19 |

## `src/bth_analysis/__init__.py`

Active Blackpool / BTH real-data TRE analysis package.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `src/bth_analysis/analysis/__init__.py`

Statistical/descriptive analysis modules for the Active Blackpool TRE workflow.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `src/bth_analysis/analysis/clustering.py`

Exploratory baseline healthcare-utilisation phenotyping for TRE data.

| Line | Function / class | Review purpose |
|---:|---|---|
| 73 | `_load_clustering_config(path)` | Load clustering YAML and retain its resolved path for reproducibility. |
| 81 | `_require_columns(df, columns, context)` | Fail early if a required clustering input is absent. |
| 88 | `_clean_numeric(series)` | Coerce one clustering feature to finite numeric values, preserving missingness for explicit checking. |
| 93 | `_pairwise_mean_ari(label_sets)` | Calculate mean pairwise Adjusted Rand Index across repeated cluster fits. |
| 104 | `_cramers_v(table)` | Calculate Cramer's V effect size and chi-square p-value for categorical association. |
| 118 | `_prepare_matrix(df, features, winsor_upper_quantile)` | Winsorise, log-transform and standardise baseline utilisation inputs for K-means. |
| 154 | `_evaluate_k(X, candidate_k)` | Fit candidate K solutions and calculate separation, size and stability diagnostics. |
| 236 | `_choose_k(metrics, minimum_stability_ari)` | Select K using the configured stability/size rules and clustering selection policy. |
| 262 | `_reorder_clusters(df, labels, baseline_features)` | Relabel raw K-means cluster IDs into a stable descriptive order for reporting. |
| 287 | `_baseline_profiles(df, features)` | Summarise raw baseline utilisation distributions within each cluster. |
| 311 | `_cluster_characterisation(baseline_profiles, features)` | Create provisional data-derived phenotype descriptions for later clinical review. |
| 344 | `_centroid_table(model, cluster_mapping, features)` | Return standardised cluster centroids by baseline utilisation feature. |
| 362 | `_demographic_numeric(df)` | Profile numeric demographic/follow-up variables after cluster formation. |
| 390 | `_categorical_profiles(df)` | Profile categorical characteristics after clustering without using them to create clusters. |
| 426 | `_exposure_distribution(df)` | Compare pathway-group composition across clusters and calculate descriptive association. |
| 468 | `_trajectory_tables(df)` | Calculate descriptive baseline/follow-up outcome rates within clusters and pathway groups. |
| 521 | `_followup_profiles(df)` | Summarise follow-up outcome distributions within baseline utilisation phenotypes. |
| 546 | `_plot_cluster_selection(metrics, selected_k, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 561 | `_plot_cluster_sizes(exposure_dist, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 578 | `_plot_centroid_heatmap(centroids, features, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 599 | `_plot_group_cluster_distribution(exposure_dist, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 643 | `_plot_followup_by_cluster(trajectory, outcome_key, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 673 | `run_clustering(workflow_path, clustering_config_path)` | Run the exploratory real-data clustering layer, diagnostics, sensitivities and phenotype audit. |

## `src/bth_analysis/analysis/comparative.py`

Primary and sensitivity comparative healthcare-utilisation models.

| Line | Function / class | Review purpose |
|---:|---|---|
| 51 | `_rate_result(fit, term, outcome, method, family, n)` | Convert one fitted model coefficient into an auditable ratio, confidence interval and p-value row. |
| 99 | `_alpha_mom(y)` | Method-of-moments dispersion parameter used for NB-GEE sensitivity. |
| 117 | `_family(y, family_name)` | Return the configured Poisson or Negative Binomial count-family object. |
| 124 | `_fit_gee_rate(df, outcome, person_time, weight_col, group_col, method, family_name, minimum_events_per_group, minimum_events_per_group_nb)` | Fit one follow-up-only GEE count-rate model with person-time offset and sparse-event gates. |
| 220 | `_prepost_stack(df, followup_outcome)` | Reshape patient outcomes into repeated baseline/follow-up rows for comparative pre/post modelling. |
| 252 | `_fit_prepost(df, outcome, weight_col, cluster_col, method, family_name, minimum_events_per_group)` | Fit the group-by-period GEE model whose interaction is the comparative rate-ratio-of-rate-ratios. |
| 376 | `_crude_period_rates(df, outcomes)` | Calculate unadjusted baseline/follow-up rates per person-time before propensity adjustment. |
| 405 | `_crude_change_summary(period_rates)` | Summarise the unadjusted difference in baseline-to-follow-up change between groups. |
| 445 | `_plot_love(balance, path, threshold)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 472 | `_plot_ps_overlap(data, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 495 | `_plot_weight_distribution(data, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 520 | `_plot_primary_forest(results, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 549 | `run_comparative(config_path)` | Run propensity design, balance gates and the primary/sensitivity comparative models. |

## `src/bth_analysis/analysis/descriptive.py`

Stage 07: descriptive EDA, cohort characterisation and diagnostic figures.

| Line | Function / class | Review purpose |
|---:|---|---|
| 93 | `_to_dt(series)` | Coerce a series to pandas datetime while turning unparseable values into missing timestamps. |
| 100 | `_slug(value)` | Create a filesystem-safe text label for aggregate figure filenames. |
| 106 | `_numeric(series)` | Coerce a series to numeric values for robust descriptive calculations. |
| 111 | `_safe_pct(numerator, denominator)` | Calculate a percentage while returning missing when the denominator is zero. |
| 116 | `_derive_reporting_features(df)` | Derive presentation/EDA-only age bands and IMD quintiles without changing core analysis variables. |
| 148 | `_group_lookup(df)` | Create an ExposureFlag-to-display-label mapping from observed analysis groups. |
| 162 | `_summarise_numeric(df, variables)` | Calculate grouped descriptive statistics for configured numeric baseline variables. |
| 206 | `_summarise_categories(df, variables)` | Calculate grouped counts/percentages for configured categorical baseline variables. |
| 244 | `_numeric_smd(x0, x1)` | Calculate an unweighted SMD for one continuous baseline variable. |
| 256 | `_binary_smd(p0, p1)` | Calculate an unweighted SMD for one binary indicator. |
| 264 | `_baseline_balance(df, numeric_vars, categorical_vars)` | Calculate unadjusted baseline SMDs used to show why confounding adjustment is required. |
| 324 | `_cohort_flow(df)` | Build aggregate cohort-flow counts for descriptive reporting. |
| 357 | `_missingness_summary(df)` | Summarise effective analytical missingness by group for key descriptive variables. |
| 385 | `_source_coverage(df)` | Summarise linked-source availability by analysis group. |
| 414 | `_pathway_timing(df)` | Summarise referral/MSK timing intervals and chronology-related descriptive measures. |
| 475 | `_utilisation_summary(df)` | Calculate crude outcome distributions and person-time rates by group/period. |
| 523 | `_prepost_change(utilisation)` | Calculate crude within-group baseline-to-follow-up changes. |
| 553 | `_index_temporal_summary(df)` | Summarise index-date counts over calendar time. |
| 575 | `_event_structure(ledger, eligible)` | Summarise event-ledger composition by event type/source/period. |
| 618 | `_expand_event_outcomes(ledger)` | Expand event-ledger rows into the configured outcome categories for aggregate summaries. |
| 645 | `_overlap_days(lo, hi, available_before, available_after)` | Calculate the number of observed days overlapping two time intervals. |
| 658 | `_relative_time_rates(ledger, eligible, bin_days)` | Calculate aggregate utilisation trajectories in bins relative to the analytical index. |
| 724 | `_correlations(df)` | Calculate aggregate baseline numeric correlations for EDA. |
| 744 | `_table1(numeric, categorical, balance, group_names)` | Assemble the report-facing baseline-characteristics Table 1. |
| 807 | `_eda_diagnostics(eligible, balance, utilisation, missingness)` | Create explicit review flags for descriptive data-quality or distributional concerns. |
| 902 | `_style_axis(ax)` | Apply restrained common formatting to a Matplotlib axis. |
| 915 | `_group_colour_for_label(df, label)` | Return a stable plotting colour choice for one analysis-group label. |
| 926 | `_save_grouped_horizontal_bar(categorical, variable, figure_path, title)` | Persist the corresponding aggregate analytical/QA output in a reproducible format. |
| 998 | `_plot_age_distribution(df, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1030 | `_plot_followup_days(df, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1065 | `_plot_index_timeline(monthly, path)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1090 | `_plot_utilisation_rates(utilisation, figure_dir)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1123 | `_plot_baseline_smd(balance, path, top_n)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1145 | `_plot_relative_trajectory(relative, figure_dir)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1177 | `_annotated_heatmap(matrix, path, title, label)` | Render an annotated aggregate heatmap for EDA output. |
| 1205 | `_plot_correlation_heatmaps(correlations, figure_dir)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1218 | `_cramers_v(x, y)` | Calculate Cramer's V effect size and chi-square p-value for categorical association. |
| 1236 | `_categorical_associations(df)` | Internal helper for categorical associations; see the surrounding module comments for the analytical rationale. |
| 1253 | `_plot_categorical_associations(associations, figure_dir)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1266 | `_plot_source_coverage(source_coverage, figure_dir)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1326 | `_plot_pathway_timing(pathway, figure_dir)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1364 | `_plot_age_vs_baseline_utilisation(df, path, max_points_per_group)` | Create and save the corresponding aggregate diagnostic/reporting figure. |
| 1394 | `_write_manifest(table_dir, figure_manifest, tables)` | Write a descriptive-output manifest for reproducible review. |
| 1423 | `run_descriptive(config_path)` | Run the complete unadjusted descriptive/EDA layer and emit aggregate key findings. |

## `src/bth_analysis/analysis/extended.py`

Optional exploratory/sensitivity analyses for the TRE workflow.

| Line | Function / class | Review purpose |
|---:|---|---|
| 28 | `_to_dt(series)` | Coerce a series to pandas datetime while turning unparseable values into missing timestamps. |
| 33 | `_km_curve(duration, event)` | Calculate a simple Kaplan-Meier step curve for an optional endpoint. |
| 63 | `_survival_dataset(patient, ledger, event_type)` | Build the optional time-to-first-event dataset from eligible patient outcomes. |
| 99 | `_cox_result(df, endpoint)` | Adjusted Cox sensitivity with transparent fallback specifications. |
| 244 | `_pretrend_tables(patient, ledger, propensity, period_days, periods)` | Create pre-index time-bin summaries used to assess whether stronger DiD assumptions are plausible. |
| 416 | `run_extended(config_path)` | Run optional extended analyses only when explicitly enabled in workflow configuration. |

## `src/bth_analysis/analysis/propensity.py`

Propensity-score design for the primary TRE comparative analysis.

| Line | Function / class | Review purpose |
|---:|---|---|
| 31 | `PropensityResult` | Internal helper for PropensityResult; see the surrounding module comments for the analytical rationale. |
| 43 | `_weighted_mean_var(x, w)` | Return the weighted mean and variance used by balance diagnostics. |
| 56 | `_smd(x, exposure, weights)` | Calculate a standardised mean difference between Sports-linked and comparison groups. |
| 73 | `_derive_design_covariates(df, covariates)` | Create design-only covariates without changing upstream pipeline outputs. |
| 83 | `_normalised_level(series)` | Convert categorical values to stable strings while retaining missingness explicitly. |
| 88 | `_apply_overlap_restrictions(df, restrictions)` | Restrict the propensity-design population to categorical levels represented |
| 149 | `_validate_preindex_covariates(covariates)` | Block accidental post-index/exposure leakage into the propensity model. |
| 170 | `_feature_matrix(df, covariates)` | Build the leakage-safe propensity design matrix and preprocessing pipeline. |
| 231 | `_logit(p)` | Convert propensity probabilities to the log-odds scale used for matching distances. |
| 237 | `_greedy_match(df, ratio, caliper_sd_logit, random_seed, require_full_ratio)` | Create nearest-neighbour propensity matched sets under the configured caliper and ratio. |
| 337 | `_balance_table(X, y, feature_names, att_weights, matched)` | Calculate before/after covariate balance statistics for the propensity design. |
| 380 | `_weight_diagnostics(work)` | Summarise ATT weight distribution and effective sample size without patient-level output. |
| 406 | `_ps_distribution(work)` | Summarise aggregate propensity-score distributions by group and support status. |
| 430 | `fit_propensity(df, covariates, psm_ratio, caliper_sd_logit, random_seed, overlap_restrictions, require_full_psm_ratio)` | Execute the complete propensity design: positivity, logistic PS, ATT, SMD and PSM sensitivity. |

## `src/bth_analysis/audit.py`

Small, patient-safe audit/logging helpers used by every TRE workflow stage.

| Line | Function / class | Review purpose |
|---:|---|---|
| 45 | `_json_safe(value)` | Convert common pandas/numpy values into JSON-safe aggregate values. |
| 69 | `stage_header(stage_code, title)` | Print a consistent stage header so terminal logs are easy to scan. |
| 92 | `section(title)` | Print a visually distinct subsection inside a stage log. |
| 99 | `metric(label, value)` | Print one aggregate key-value result with aligned labels. |
| 105 | `dataframe_preview(df)` | Print a bounded aggregate table preview; never use with patient-level rows. |
| 126 | `save_stage_summary(audit_dir)` | Write one compact JSON stage summary containing no patient-level records. |
| 188 | `stage_footer()` | Print the audit trail and the exact next workflow command. |

## `src/bth_analysis/data_pipeline/__init__.py`

Public entry points for deterministic real-source data pipeline stages.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `src/bth_analysis/data_pipeline/cleaning.py`

Stage 02: deterministic source cleaning and data-quality checks.

| Line | Function / class | Review purpose |
|---:|---|---|
| 36 | `normalize_blank_strings(df)` | Convert whitespace-only text cells to explicit pandas missing values. |
| 50 | `parse_dates(df, columns)` | Parse configured source date/time fields and coerce invalid text to NaT. |
| 68 | `coerce_numeric(df, columns)` | Convert configured numeric fields to numbers; malformed values become NA. |
| 77 | `clean_msk(df, table_key, table_cfg, config)` | Clean one MSK pathway table and return aggregate chronology QA. |
| 163 | `clean_inpatient(df, table_key, table_cfg, config)` | Clean one inpatient episode table without collapsing episodes to spells. |
| 260 | `clean_ed(df, table_key, table_cfg, config)` | Clean one ED attendance table and enforce the resolved patient/event key. |
| 364 | `save_cleaned(df, path)` | Persist the cleaned canonical table using an explicit datetime format. |
| 374 | `run_cleaning(config_path)` | Clean all ingested TRE tables after resolving source identifiers. |

## `src/bth_analysis/data_pipeline/cohort.py`

Stage 05: freeze the comparative cohort, analytical index and observation windows.

| Line | Function / class | Review purpose |
|---:|---|---|
| 26 | `_to_dt(series)` | Parse canonical pipeline timestamps written as ISO-style strings. |
| 43 | `_bool_flag(value, index)` | Return a pipeline-style Int64 flag repeated for every cohort row. |
| 48 | `_assign_index_date(cohort, cohort_cfg)` | Assign the configured analytical index without claiming programme start. |
| 137 | `run_cohort_index(config_path)` | Create the comparative cohort, analytical index and observation windows. |

## `src/bth_analysis/data_pipeline/config.py`

Configuration/path helpers for real-source pipeline stages inside the TRE.

| Line | Function / class | Review purpose |
|---:|---|---|
| 16 | `load_pipeline_config(config_path)` | Load source-pipeline YAML and attach the resolved repository root. |
| 36 | `resolve_from_project(config, value)` | Resolve an absolute path or a project-relative configured path. |
| 44 | `source_dir(config)` | Return the approved real-TRE source directory and reject synthetic mode. |
| 61 | `output_dir(config, key)` | Resolve one named source-pipeline output directory from configuration. |

## `src/bth_analysis/data_pipeline/identifiers.py`

Real-TRE identifier resolution for the six Active Blackpool source extracts.

| Line | Function / class | Review purpose |
|---:|---|---|
| 24 | `IdentifierChoice` | Selected identifier columns for one source table. |
| 31 | `_dedupe(values)` | Return non-empty values once, preserving configured preference order. |
| 45 | `_candidate_columns(table_cfg, role)` | Return configured preferred identifier followed by fallback candidates. |
| 60 | `_as_id_set(series)` | Convert an identifier column to a set without materialising missing tokens. |
| 65 | `_score_candidate(series)` | Create aggregate diagnostics for one candidate identifier column. |
| 89 | `choose_patient_identifier(df, table_key, table_cfg)` | Select the patient identifier, using cohort overlap when available. |
| 162 | `choose_event_identifier(df, table_key, table_cfg)` | Select the event identifier, preferring a field distinct from patient ID. |
| 214 | `resolve_identifier_plan(tables, table_configs)` | Resolve identifiers for all configured real-TRE source tables. |
| 281 | `apply_identifier_choices_to_config(table_configs, choices)` | Return a copied table configuration with resolved ID fields inserted. |

## `src/bth_analysis/data_pipeline/ingestion.py`

Stage 01: schema-aware ingestion of approved TRE extracts.

| Line | Function / class | Review purpose |
|---:|---|---|
| 36 | `_expected_schema(table_key, table_cfg)` | Return the table's canonical expected column order. |
| 46 | `validate_schema(df, table_key, table_cfg)` | Validate required columns after source-to-canonical mapping. |
| 78 | `align_columns(df, table_key, table_cfg)` | Place canonical fields in a deterministic order. |
| 93 | `_read_source(path, table_cfg, low_memory)` | Read CSV or Parquet according to the table configuration. |
| 109 | `_write_ingested(df, path)` | Write a canonical CSV consumed by all downstream stages. |
| 115 | `run_ingestion(config_path)` | Ingest all configured TRE tables into the canonical layer. |

## `src/bth_analysis/data_pipeline/linkage.py`

Stage 04: build the pseudonymised patient spine and source-coverage QA.

| Line | Function / class | Review purpose |
|---:|---|---|
| 49 | `_read(processed_dir, name)` | Read one named processed dataset and fail clearly if the prior stage is missing. |
| 57 | `_first_demographics(df, source)` | Return the first available demographic record per patient from one source. |
| 72 | `_coalesce_demographics(frames)` | Coalesce demographics using the documented source-priority ordering. |
| 124 | `run_linkage(config_path)` | Build the pseudonymised patient spine and report cross-source linkage completeness. |

## `src/bth_analysis/data_pipeline/mapping.py`

Map real TRE source aliases to the stable canonical analytical schema.

| Line | Function / class | Review purpose |
|---:|---|---|
| 15 | `apply_column_mapping(df, table_cfg)` | Rename configured source columns and block ambiguous canonical duplicates. |
| 45 | `canonical_header(columns, table_cfg)` | Apply the same rename map to source header names without loading row data. |

## `src/bth_analysis/data_pipeline/missingness.py`

Column-level missingness audit for the deterministic TRE cleaning stage.

| Line | Function / class | Review purpose |
|---:|---|---|
| 23 | `_cfg(config)` | Return the optional missingness subsection of pipeline configuration. |
| 28 | `_classification(table_key, column, table_cfg, config)` | Resolve the configured interpretation of missingness for one field. |
| 70 | `column_missingness_table(df, table_key, table_cfg, config)` | Return one aggregate missingness row per cleaned source column. |
| 115 | `print_missingness_summary(miss)` | Print the most decision-relevant column-level missingness findings. |
| 163 | `_source_pairs(table_keys)` | Identify wider/sports pairs such as msk_wider versus msk_sports. |
| 175 | `compare_group_missingness(all_missingness, config)` | Compare missing percentages on columns common to matched source families. |
| 216 | `print_group_missingness_comparison(comparison, config)` | Print the largest Sports-linked versus Wider MSK missingness differences. |

## `src/bth_analysis/data_pipeline/outcomes.py`

Stage 06: construct patient-level healthcare-utilisation outcomes.

| Line | Function / class | Review purpose |
|---:|---|---|
| 26 | `_to_dt(series)` | Parse canonical workflow datetimes without locale reinterpretation. |
| 42 | `_load(path)` | Read a required upstream CSV and fail with the exact missing path. |
| 49 | `_build_ed_ledger(df, exposure_flag, source_name)` | Map cleaned ED attendances into the common healthcare-event ledger schema. |
| 67 | `_build_inpatient_ledger(df, exposure_flag, source_name, emergency_patterns)` | Map one row per inpatient spell into the common event-ledger schema. |
| 101 | `run_outcome_features(config_path)` | Build the healthcare event ledger and patient-level counts/person-time outcome features. |

## `src/bth_analysis/data_pipeline/preprocessing.py`

Stage 03: convert cleaned source tables into canonical analytical grains.

| Line | Function / class | Review purpose |
|---:|---|---|
| 25 | `parse_datetime_columns(df, columns)` | Re-parse canonical cleaned timestamps after CSV serialisation. |
| 44 | `days_between(later, earlier)` | Return elapsed days between two parsed timestamp series as floating days. |
| 49 | `make_msk_referral_view(df, table_cfg, sports)` | Create one canonical MSK referral/history view from a cleaned source table. |
| 141 | `make_pathway_anchor(referrals)` | Select the earliest configured MSK referral record as a source-relative anchor. |
| 170 | `derive_relative_timeframe(event_date, anchor_referral, anchor_last)` | Classify an event as before/during/after the source-relative MSK pathway. |
| 206 | `_aggregate_codes_by_spell(episode, group_cols, columns, output_col, count_col)` | Deduplicate repeated diagnosis/procedure codes and aggregate them per spell. |
| 249 | `make_inpatient_views(df, table_cfg, anchor)` | Return both episode-level and spell/admission-level inpatient views. |
| 419 | `make_ed_view(df, table_cfg, anchor)` | Create one row per cleaned ED attendance with canonical IDs and timing QA. |
| 479 | `processed_summary(name, df)` | Return aggregate dimensions/coverage metrics for one processed dataset. |
| 516 | `save_processed(df, path)` | Persist a processed analytical-grain table using canonical datetime text. |
| 526 | `run_preprocessing(config_path)` | Harmonise cleaned source grain, derive pathway views and collapse inpatient episodes to spells. |

## `src/bth_analysis/data_pipeline/qa.py`

Small aggregate QA helpers shared by source-data pipeline stages.

| Line | Function / class | Review purpose |
|---:|---|---|
| 16 | `save_records(records, path)` | Write a list of aggregate QA dictionaries to CSV. |
| 32 | `basic_table_summary(df, table_key, table_cfg)` | Return patient-safe table dimensions and identifier completeness metrics. |
| 86 | `print_table_summary(summary, prefix)` | Print the most useful aggregate table QA metrics in a stable format. |

## `src/bth_analysis/data_pipeline/schemas.py`

Canonical minimum schemas for the six real Active Blackpool/BTH extracts.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `src/bth_analysis/orchestration/__init__.py`

Production orchestration, readiness and release-audit entry points.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `src/bth_analysis/orchestration/preflight.py`

TRE preflight checks.

| Line | Function / class | Review purpose |
|---:|---|---|
| 28 | `_header(path, table_cfg)` | Read and canonicalise only a source-file header for preflight schema checks. |
| 50 | `run_preflight(workflow_path, pipeline_path)` | Run source, schema and methodological-readiness checks. |

## `src/bth_analysis/orchestration/readiness.py`

Configuration-level readiness checks for TRE translation and interpretation.

| Line | Function / class | Review purpose |
|---:|---|---|
| 19 | `translation_readiness(workflow_config)` | Return one aggregate row per interpretation/configuration readiness check. |

## `src/bth_analysis/orchestration/release_audit.py`

Pre-screen candidate outputs before formal TRE disclosure control.

| Line | Function / class | Review purpose |
|---:|---|---|
| 33 | `_looks_like_count_column(name)` | Identify aggregate columns that should be inspected for small-cell disclosure risk. |
| 45 | `run_release_audit(workflow_path, release_config_path)` | Pre-screen outputs for patient-level/internal files and possible small-cell aggregate risks. |

## `src/bth_analysis/orchestration/tre.py`

End-to-end orchestration for the production TRE workflow.

| Line | Function / class | Review purpose |
|---:|---|---|
| 50 | `_stage_log_path(cfg)` | Resolve the run-level stage-status audit CSV path. |
| 57 | `_record_stage(rows, cfg, **row)` | Append one aggregate stage execution status row and persist the run status file. |
| 63 | `run_tre_workflow(workflow_path, pipeline_path, clustering_path)` | Run an ordered section of the TRE workflow. |

## `src/bth_analysis/workflow.py`

Shared configuration, path and reproducibility helpers for the TRE workflow.

| Line | Function / class | Review purpose |
|---:|---|---|
| 22 | `load_workflow_config(path)` | Load analytical workflow YAML and attach portable project metadata. |
| 40 | `resolve_path(cfg, value)` | Resolve absolute paths or project-relative configured paths. |
| 48 | `output_path(cfg, key)` | Resolve a named analytical/audit output directory from workflow config. |
| 55 | `config_sha256(path)` | Return a content digest so every run can be tied to exact configuration. |
| 61 | `_safe_git_commit(project_root)` | Return current Git commit when available without making Git mandatory. |
| 81 | `_dependency_versions()` | Return installed package versions for reproducibility without importing data. |
| 103 | `build_run_manifest(cfg)` | Create non-patient reproducibility metadata for the current run. |
| 133 | `write_run_manifest(cfg, manifest, filename)` | Persist one JSON run manifest in the configured TRE audit directory. |

## `scripts/review_audit_summary.py`

Build one reviewer-facing audit summary from aggregate per-stage JSON files.

| Line | Function / class | Review purpose |
|---:|---|---|
| 32 | `_markdown_table(headers, rows)` | Return a dependency-free Markdown table. |
| 53 | `main()` | Create ``reviewer_summary.csv`` and ``reviewer_summary.md``. |

## `scripts/run_00_preflight.py`

Run Stage: Preflight.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_01_ingestion.py`

Run Stage: Ingestion.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_02_cleaning.py`

Run Stage: Cleaning.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_03_preprocessing.py`

Run Stage: Preprocessing.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_04_linkage.py`

Run Stage: Linkage.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_05_cohort.py`

Run Stage: Cohort/index/windows.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_06_outcomes.py`

Run Stage: Outcome engineering.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_07_descriptive.py`

Run Stage: Descriptive/EDA.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_08_comparative.py`

Run Stage: Propensity + comparative modelling.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_09_clustering.py`

Run Stage: Exploratory clustering.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_10_extended_optional.py`

Run Stage: Optional extended analysis.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_11_release_audit.py`

Run Stage: Release pre-screen.

No top-level callable is exposed; this file is package metadata, constants or an executable wrapper.

## `scripts/run_all_tre.py`

Command-line orchestration entry point for the reviewed real-data TRE workflow.

| Line | Function / class | Review purpose |
|---:|---|---|
| 46 | `main()` | Parse CLI arguments and execute the requested contiguous stage range. |

## Highest-priority methodology files for final review

1. `src/bth_analysis/data_pipeline/cleaning.py` — deterministic cleaning, chronology, identifier resolution and column-level missingness audit.
2. `src/bth_analysis/data_pipeline/cohort.py` — pathway-group definition, analytical index, observation windows and eligibility.
3. `src/bth_analysis/data_pipeline/outcomes.py` — ED/inpatient/emergency event construction, spell-level counting and person-time.
4. `src/bth_analysis/analysis/propensity.py` — logistic selection model, structural positivity, common support, ATT, SMD and PSM.
5. `src/bth_analysis/analysis/comparative.py` — balance gate, group-by-period GEE, person-time offset and sensitivity hierarchy.
6. `src/bth_analysis/analysis/clustering.py` — baseline-only K-means, K diagnostics, stability and descriptive phenotype profiling.
7. `src/bth_analysis/orchestration/preflight.py` — source/configuration blockers before patient-level analysis.
8. `src/bth_analysis/orchestration/release_audit.py` — internal output pre-screen before formal disclosure review.

## Auditability principle

No synthetic denominator, propensity balance result, model effect estimate or cluster centroid is hard-coded as a required real-data result. Design thresholds live in version-controlled configuration; empirical findings are regenerated from approved TRE data.
