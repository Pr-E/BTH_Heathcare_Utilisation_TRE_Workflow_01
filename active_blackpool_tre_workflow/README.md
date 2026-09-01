# Active Blackpool / BTH — TRE-ready analysis workflow

## Final-review release (v0.4.0)

## Purpose

This repository is the **production translation package** for the Active Blackpool / Blackpool Teaching Hospitals healthcare-utilisation evaluation. It contains the data and analysis layers required to rerun the validated development workflow against the **real approved TRE extracts**.

Synthetic-data generation and calibration code are deliberately excluded. The production package starts from approved TRE source tables and rebuilds every cohort, propensity, model and clustering result from the real data.

## Current interpretation boundary

The workflow is currently configured for a comparison between:

- **Sports-linked BTH pathway patients**; and
- **Wider MSK non-Sports-linked candidate patients**.

The default analytical index is a **source-relative `FirstMSKDate` time origin**. It is **not** automatically a confirmed Active Blackpool programme-start date.

Accordingly, the main model estimates an **adjusted comparative association in baseline-to-follow-up healthcare-utilisation change**. It must not be described as a confirmed causal programme effect unless the real-data exposure/index semantics and causal assumptions are separately established.

---

## Production workflow

```text
00  TRE preflight / source semantics
        ↓
01  Ingestion + canonical schema mapping
        ↓
02  Conservative cleaning + chronology QA
        ↓
03  Preprocessing
    • MSK referral/pathway views
    • inpatient episode → spell/admission view
    • ED attendance view
        ↓
04  Pseudonymised patient spine + linkage QA
        ↓
05  Comparative cohort + analytical index + windows
    • 365-day baseline
    • up to 365-day follow-up
    • censor at study end/death
        ↓
06  Healthcare outcomes
    • ED attendances
    • inpatient admissions/spells
    • emergency inpatient admissions
    • total hospital utilisation
    • person-time rates
        ↓
07  Descriptive EDA / data quality / crude rates
        ↓
08  Propensity + primary comparative analysis
    • logistic propensity model
    • structural positivity restrictions
    • empirical common support
    • ATT weighting
    • SMD balance diagnostics
    • 1:3 PSM sensitivity
    • Poisson GEE primary pre/post model
    • Negative Binomial GEE sensitivity
        ↓
09  Exploratory utilisation clustering
    • baseline utilisation only
    • K=2..6 diagnostics recomputed
    • K=4 development-informed candidate retained only if real-data criteria pass
        ↓
10  Optional extended analyses
        ↓
11  Output release pre-screen
    • patient-level output flagging
    • small-cell flagging
    • formal TRE disclosure control still required
```

---

## Folder structure

```text
active_blackpool_tre_workflow/
│
├── config/
│   ├── pipeline_tre.yaml       # real source paths, filenames and mappings
│   ├── workflow_tre.yaml       # cohort, propensity and comparative design
│   ├── clustering_tre.yaml     # exploratory clustering specification
│   └── release_audit.yaml      # disclosure pre-screen configuration
│
├── scripts/
│   ├── run_00_preflight.py
│   ├── run_01_ingestion.py
│   ├── run_02_cleaning.py
│   ├── run_03_preprocessing.py
│   ├── run_04_linkage.py
│   ├── run_05_cohort.py
│   ├── run_06_outcomes.py
│   ├── run_07_descriptive.py
│   ├── run_08_comparative.py
│   ├── run_09_clustering.py
│   ├── run_10_extended_optional.py
│   ├── run_11_release_audit.py
│   └── run_all_tre.py
│
├── src/bth_analysis/
│   ├── data_pipeline/
│   ├── analysis/
│   └── orchestration/
│
├── docs/
│   ├── ANALYSIS_SPECIFICATION.md
│   ├── TRE_RUNBOOK.md
│   ├── TRE_TRANSLATION_CHECKLIST.md
│   ├── OUTPUT_CATALOGUE.md
│   └── source_mapping_template.csv
│
├── tests/
├── requirements.txt
└── pyproject.toml
```

---

# 1. First-time TRE setup

### 1. Copy the repository into the approved TRE workspace

Do not copy patient-level data out of the TRE. The code repository can be transferred according to the local TRE process.

### 2. Create/install the Python environment

From the project root:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

If package installation is restricted, each script also adds the local `src/` directory to `sys.path`, so execution from the repository root remains possible.

### 3. Confirm the real TRE source location

`config/pipeline_tre.yaml` is already populated with the six real BTH extract filenames used in the existing TRE workspace:

- `active_blackpool_msk_cohort_without_sports.csv`
- `active_blackpool_inpatient_msk_.csv`
- `active_blackpool_msk_cohort_without_sports_ed.csv`
- `active_blackpool_only_msk_sports.csv`
- `active_blackpool_inpatient_msk_sports.csv`
- `active_blackpool_only_msk_sports_ed.csv`

The current workspace screenshot places these extracts under `src`, so the default is:

```yaml
data_source:
  mode: tre
  tre_dir: src
```

Change only `tre_dir` if the approved TRE workspace stores the same extracts elsewhere.

### 4. Confirm the real extract coverage window

`config/workflow_tre.yaml` deliberately leaves `study_start_date` and `study_end_date` unset. Populate them from the approved BTH/TRE extract coverage documentation before cohort construction. **Do not reuse the synthetic simulator window.**

### 5. Review the real source mapping

The analysis code uses stable canonical names. If a real extract uses different names, add a mapping under the relevant table:

```yaml
column_mapping:
  actual_tre_patient_hash: sha256_hash
  actual_admission_datetime: AdmissionDate
```

The real-source mapping worksheet is pre-populated at:

```text
docs/source_mapping_tre.csv
```

The source/identifier evidence and remaining interpretation boundaries are documented at:

```text
docs/REAL_TRE_SOURCE_REGISTER.md
```

Do not edit analytical code solely to accommodate a source-column alias unless the meaning of the field itself has changed.

---

# 2. Mandatory preflight

Run:

```bash
python scripts/run_00_preflight.py
```

Preflight checks:

- TRE source directory exists;
- all six configured source files exist;
- canonical required fields can be obtained after column mapping;
- study window is valid;
- propensity covariates are pre-index only;
- baseline/follow-up rules are explicit;
- analysis group semantics have been confirmed;
- analytical index semantics have been confirmed;
- programme start is not being assumed without evidence;
- at least one configured patient/event identifier candidate exists in each real source table.

During Stage 02 and again in Stage 03, healthcare patient hashes are re-verified by overlap with the corresponding MSK cohort. The selected identifier column and aggregate overlap/uniqueness diagnostics are written to `outputs/qa/02_identifier_resolution_qa.csv` and `03_identifier_resolution_qa.csv`.

The source filenames now establish the working pathway-group contrast, so `analysis_group_semantics_confirmed_for_workflow` is already `true` for **Sports-linked BTH pathway versus Wider MSK without Sports**. This still does not imply programme treatment.

The workflow remains intentionally blocked until:

1. the approved real extract coverage dates are entered; and
2. the analytical meaning of `FirstMSKDate` is confirmed and `analytical_index_semantics_confirmed_for_workflow` is changed to `true`.

Programme-start semantics remain false unless separate programme engagement data genuinely establish them.

---

# 3. Run the workflow

### Full default run

```bash
python scripts/run_all_tre.py
```

The default executes through clustering.

### Resume from a stage

```bash
python scripts/run_all_tre.py --from-stage outcomes --to-stage clustering
```

### Run individual stages

```bash
python scripts/run_01_ingestion.py
python scripts/run_02_cleaning.py
python scripts/run_03_preprocessing.py
python scripts/run_04_linkage.py
python scripts/run_05_cohort.py
python scripts/run_06_outcomes.py
python scripts/run_07_descriptive.py
python scripts/run_08_comparative.py
python scripts/run_09_clustering.py
```

---

# 4. Primary comparative analysis

## Propensity design

Logistic regression estimates:

```text
P(Sports-linked BTH pathway | measured pre-index covariates)
```

Configured pre-index covariates are:

- age at index;
- sex;
- ethnicity;
- IMD decile;
- geography;
- index year;
- baseline ED count;
- baseline inpatient count;
- baseline emergency inpatient count.

The propensity layer then performs:

1. **structural positivity checks** for configured categorical strata;
2. **empirical common-support restriction** on propensity score ranges;
3. **ATT weighting** as the primary adjustment;
4. **SMD balance assessment**, target absolute SMD `<0.10`;
5. **1:3 PSM** as a separate sensitivity design.

If ATT balance fails the configured threshold, the real-data primary adjusted model is blocked by default.

## Primary outcome model

For each healthcare outcome, each patient contributes a baseline and follow-up record. The model contains:

```text
Group + Period + Group×Period
```

with:

```text
log(person-time)
```

as an offset and patient-level clustering through GEE.

The exponentiated `Group×Period` coefficient is the **rate ratio of rate ratios**: the relative difference in baseline-to-follow-up rate change between Sports-linked and propensity-adjusted Wider MSK patients.

- **Poisson GEE** = primary prespecified formulation.
- **Negative Binomial GEE** = distributional sensitivity for overdispersion.
- **PSM comparative pre/post** = alternative propensity-design sensitivity.

---

# 5. Clustering layer

The clustering analysis is secondary and descriptive.

Cluster construction uses only:

- `BaselineEDRatePerPY`;
- `BaselineInpatientRatePerPY`;
- `BaselineEmergencyInpatientRatePerPY`.

It does **not** use pathway group, age, sex, ethnicity, IMD, geography or follow-up outcomes to create clusters.

The real TRE run recomputes K=2..6 diagnostics. K=4 is a development-informed candidate because it produced interpretable phenotypes in synthetic validation, but it is retained only when the real-data solution passes minimum size and stability criteria. Synthetic centroids and synthetic cluster memberships are never reused.

---

# 6. Required QA gates before interpreting real results

Do not move directly from a successful script execution to clinical interpretation. Review at minimum:

1. ingestion schema and missing identifiers;
2. cleaning chronology/duplicate QA;
3. episode-to-spell aggregation;
4. linkage coverage across source families;
5. cohort exclusion flow;
6. baseline completeness and follow-up distribution;
7. event counting and emergency-admission coding;
8. crude baseline rates by analysis group;
9. positivity/overlap exclusions;
10. propensity-score overlap;
11. ATT weight distribution and effective sample size;
12. SMD balance before/after weighting;
13. PSM balance and matched sample size;
14. sparse event counts/model status;
15. Poisson vs Negative Binomial consistency;
16. clustering size/stability/interpretability;
17. disclosure-control suitability of any requested output.

---

# 7. Output release

After internal review, run:

```bash
python scripts/run_11_release_audit.py
```

This pre-screen flags obvious patient-level filenames and small aggregate cells. It **does not replace the TRE's formal disclosure-control process**.

Patient-level files such as the patient spine, outcome dataset, matched population, propensity-scored population and cluster assignments are internal analytical artefacts and should not be requested for egress.

---

# 8. Reproducibility

Each full TRE run writes:

```text
outputs/audit/tre_run_manifest.json
outputs/audit/stage_status.csv
```

The manifest records configuration hashes, Python version, timestamp and git commit when available. This provides traceability without containing patient-level data.

---

## Final production principle

**The code architecture transfers; the synthetic findings do not.**

Every real-data cohort count, propensity score, overlap restriction, weight, SMD, model estimate, confidence interval and cluster solution must be regenerated and reviewed inside the TRE.
