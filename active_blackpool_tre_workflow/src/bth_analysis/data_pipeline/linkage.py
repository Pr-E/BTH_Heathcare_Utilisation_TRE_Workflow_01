"""Stage 04: build the pseudonymised patient spine and source-coverage QA.

The patient spine links the pathway and healthcare source families by PatientID,
resolves baseline demographics using a documented source priority, and defines
the working Sports-linked versus Wider MSK candidate groups.  Linkage does not
claim programme exposure or causal treatment assignment.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from bth_analysis.workflow import load_workflow_config, output_path
from bth_analysis.audit import (
    dataframe_preview,
    metric,
    save_stage_summary,
    section,
    stage_footer,
    stage_header,
)


PROCESSED_FILES = {
    "msk_wider_referrals": "msk_wider_referrals.csv",
    "msk_sports_referrals": "msk_sports_referrals.csv",
    "msk_wider_pathway_anchor": "msk_wider_pathway_anchor.csv",
    "msk_sports_pathway_anchor": "msk_sports_pathway_anchor.csv",
    "inpatient_wider_spells": "inpatient_wider_spells.csv",
    "inpatient_sports_spells": "inpatient_sports_spells.csv",
    "ed_wider_attendances": "ed_wider_attendances.csv",
    "ed_sports_attendances": "ed_sports_attendances.csv",
}


DEMO_COLS = [
    "DateOfBirth",
    "DateOfDeath",
    "Age",
    "Sex",
    "EthnicityNationalCodeDesc",
    "PostcodeLAName",
    "Index_of_Multiple_Deprivation_IMD_Decile",
]


def _read(processed_dir: Path, name: str) -> pd.DataFrame:
    """Read one named processed dataset and fail clearly if the prior stage is missing."""
    path = processed_dir / PROCESSED_FILES[name]
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, low_memory=False)


def _first_demographics(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Return the first available demographic record per patient from one source."""
    cols = ["PatientID"] + [c for c in DEMO_COLS if c in df.columns]
    if "PatientID" not in df.columns:
        return pd.DataFrame(columns=["PatientID"] + DEMO_COLS)

    work = df[cols].copy()
    for col in ("DateOfBirth", "DateOfDeath"):
        if col in work.columns:
            work[col] = pd.to_datetime(work[col], errors="coerce")
    out = work.groupby("PatientID", as_index=False).first()
    out["DemographicSource"] = source
    return out


def _coalesce_demographics(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Coalesce demographics using the documented source-priority ordering.

    This is a deterministic data-resolution rule only; source priority must not be
    interpreted as clinical superiority or treatment assignment.
    """
    all_ids = sorted(
        set().union(
            *[
                set(df["PatientID"].dropna().astype(str))
                for df in frames
                if "PatientID" in df.columns
            ]
        )
    )
    spine = pd.DataFrame({"PatientID": all_ids})

    for i, frame in enumerate(frames):
        rename = {
            col: f"{col}__{i}"
            for col in frame.columns
            if col != "PatientID"
        }
        spine = spine.merge(
            frame.rename(columns=rename),
            on="PatientID",
            how="left",
            validate="one_to_one",
        )

    for col in DEMO_COLS:
        candidates = [f"{col}__{i}" for i in range(len(frames)) if f"{col}__{i}" in spine]
        if candidates:
            spine[col] = spine[candidates].bfill(axis=1).iloc[:, 0]

    source_candidates = [
        f"DemographicSource__{i}"
        for i in range(len(frames))
        if f"DemographicSource__{i}" in spine
    ]
    if source_candidates:
        spine["ResolvedDemographicSource"] = (
            spine[source_candidates].bfill(axis=1).iloc[:, 0]
        )

    drop = [
        c for c in spine.columns
        if "__" in c
    ]
    return spine.drop(columns=drop, errors="ignore")


def run_linkage(
    config_path: str | Path = "config/workflow_tre.yaml",
) -> dict[str, pd.DataFrame]:
    """Build the pseudonymised patient spine and report cross-source linkage completeness."""
    cfg = load_workflow_config(config_path)
    processed_dir = output_path(cfg, "processed_dir")
    analysis_dir = output_path(cfg, "analysis_dir")
    qa_dir = output_path(cfg, "qa_dir")
    analysis_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)

    stage_header(
        "04",
        "PATIENT SPINE + CROSS-SOURCE LINKAGE",
        purpose=(
            "Create one patient-level presence/demographic/pathway spine from the processed MSK, "
            "inpatient and ED source families, while preserving source coverage and keeping the "
            "Sports-linked and Wider MSK pathway definitions explicit."
        ),
        inputs=[processed_dir],
        outputs=[analysis_dir / "patient_spine.csv", qa_dir / "04_linkage_overlap_qa.csv"],
    )

    wider_ref = _read(processed_dir, "msk_wider_referrals")
    sports_ref = _read(processed_dir, "msk_sports_referrals")
    wider_anchor = _read(processed_dir, "msk_wider_pathway_anchor")
    sports_anchor = _read(processed_dir, "msk_sports_pathway_anchor")
    wider_ip = _read(processed_dir, "inpatient_wider_spells")
    sports_ip = _read(processed_dir, "inpatient_sports_spells")
    wider_ed = _read(processed_dir, "ed_wider_attendances")
    sports_ed = _read(processed_dir, "ed_sports_attendances")

    presence_sources = {
        "WiderMSK": wider_ref,
        "SportsLinkedMSK": sports_ref,
        "WiderInpatient": wider_ip,
        "SportsInpatient": sports_ip,
        "WiderED": wider_ed,
        "SportsED": sports_ed,
    }

    ids = sorted(
        set().union(
            *[
                set(df["PatientID"].dropna().astype(str))
                for df in presence_sources.values()
            ]
        )
    )
    presence = pd.DataFrame({"PatientID": ids})

    for label, df in presence_sources.items():
        source_ids = set(df["PatientID"].dropna().astype(str))
        presence[f"Present{label}"] = presence["PatientID"].isin(source_ids).astype("Int64")

    # Demographic resolution priority:
    # Sports-linked pathway -> wider pathway -> sports inpatient -> wider inpatient
    # -> sports ED -> wider ED. This is only a source-resolution rule, not a
    # treatment definition.
    demo_frames = [
        _first_demographics(sports_ref, "msk_sports"),
        _first_demographics(wider_ref, "msk_wider"),
        _first_demographics(sports_ip, "inpatient_sports"),
        _first_demographics(wider_ip, "inpatient_wider"),
        _first_demographics(sports_ed, "ed_sports"),
        _first_demographics(wider_ed, "ed_wider"),
    ]
    demographics = _coalesce_demographics(demo_frames)

    spine = presence.merge(
        demographics,
        on="PatientID",
        how="left",
        validate="one_to_one",
    )

    wider_anchor = wider_anchor.rename(
        columns={
            "AnchorReferralObservationId": "WiderAnchorReferralObservationId",
            "AnchorFirstMSKReferralDate": "WiderAnchorFirstMSKReferralDate",
            "AnchorFirstMSKDate": "WiderAnchorFirstMSKDate",
            "AnchorLastMSKDate": "WiderAnchorLastMSKDate",
        }
    )
    sports_anchor = sports_anchor.rename(
        columns={
            "AnchorReferralObservationId": "SportsAnchorReferralObservationId",
            "AnchorFirstMSKReferralDate": "SportsAnchorFirstMSKReferralDate",
            "AnchorFirstMSKDate": "SportsAnchorFirstMSKDate",
            "AnchorLastMSKDate": "SportsAnchorLastMSKDate",
        }
    )

    spine = spine.merge(
        wider_anchor,
        on="PatientID",
        how="left",
        validate="one_to_one",
    ).merge(
        sports_anchor,
        on="PatientID",
        how="left",
        validate="one_to_one",
    )

    spine["SportsLinkedBTHFlag"] = spine["PresentSportsLinkedMSK"].fillna(0).astype("Int64")
    spine["WiderMSKFlag"] = spine["PresentWiderMSK"].fillna(0).astype("Int64")
    spine["EligibleWiderNonSportsCandidateFlag"] = (
        spine["WiderMSKFlag"].eq(1)
        & spine["SportsLinkedBTHFlag"].eq(0)
    ).astype("Int64")

    spine["WorkingCohortLabel"] = np.select(
        [
            spine["SportsLinkedBTHFlag"].eq(1),
            spine["EligibleWiderNonSportsCandidateFlag"].eq(1),
        ],
        [
            cfg["cohort"]["working_exposure_label"],
            cfg["cohort"]["working_comparison_label"],
        ],
        default="Outside current comparative candidate population",
    )

    # Cross-source overlap QA.
    qa_rows = []
    names = list(presence_sources)
    for i, left in enumerate(names):
        left_ids = set(presence_sources[left]["PatientID"].dropna().astype(str))
        for right in names[i + 1:]:
            right_ids = set(presence_sources[right]["PatientID"].dropna().astype(str))
            overlap = len(left_ids & right_ids)
            qa_rows.append({
                "left_source": left,
                "right_source": right,
                "left_unique_patients": len(left_ids),
                "right_unique_patients": len(right_ids),
                "overlap_n": overlap,
                "left_coverage_pct": overlap / len(left_ids) * 100 if left_ids else np.nan,
                "right_coverage_pct": overlap / len(right_ids) * 100 if right_ids else np.nan,
            })

    linkage_qa = pd.DataFrame(qa_rows)

    spine.to_csv(
        analysis_dir / "patient_spine.csv",
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )
    linkage_qa.to_csv(qa_dir / "04_linkage_overlap_qa.csv", index=False)

    # Summarise linkage coverage without printing patient IDs.  These values are
    # important because differential source linkage can mimic utilisation differences.
    sports_n = int(spine["SportsLinkedBTHFlag"].sum())
    wider_n = int(spine["EligibleWiderNonSportsCandidateFlag"].sum())
    outside_n = int(len(spine) - sports_n - wider_n)

    coverage_rows = []
    for label in presence_sources:
        col = f"Present{label}"
        if col in spine.columns:
            coverage_rows.append({
                "source": label,
                "patients_present": int(spine[col].fillna(0).sum()),
                "pct_of_spine": float(spine[col].fillna(0).mean() * 100),
            })
    coverage_df = pd.DataFrame(coverage_rows)

    section("STAGE 04 KEY FINDINGS")
    metric("patient spine unique patients", f"{len(spine):,}")
    metric("Sports-linked pathway patients", f"{sports_n:,}")
    metric("Wider MSK non-Sports candidates", f"{wider_n:,}")
    metric("outside current comparison candidate set", f"{outside_n:,}")
    print("\nSource presence across the patient spine:")
    dataframe_preview(coverage_df, max_rows=12)

    # Print the most directly relevant MSK-to-hospital overlap rows.
    direct_pairs = linkage_qa[
        (linkage_qa["left_source"].eq("WiderMSK") & linkage_qa["right_source"].isin(["WiderInpatient", "WiderED"]))
        | (linkage_qa["left_source"].eq("SportsLinkedMSK") & linkage_qa["right_source"].isin(["SportsInpatient", "SportsED"]))
    ].copy()
    if not direct_pairs.empty:
        print("\nKey pathway-to-healthcare linkage overlap:")
        dataframe_preview(
            direct_pairs,
            columns=[
                "left_source", "right_source", "left_unique_patients",
                "right_unique_patients", "overlap_n", "left_coverage_pct",
                "right_coverage_pct",
            ],
            max_rows=10,
        )

    audit_dir = output_path(cfg, "audit_dir")
    summary_path = save_stage_summary(
        audit_dir,
        stage_key="linkage",
        stage_code="04",
        title="Patient spine + cross-source linkage",
        status="PASS",
        key_findings={
            "patient_spine_n": len(spine),
            "sports_linked_pathway_n": sports_n,
            "wider_non_sports_candidate_n": wider_n,
            "outside_current_comparison_n": outside_n,
        },
        qa_files=[qa_dir / "04_linkage_overlap_qa.csv", analysis_dir / "patient_spine.csv"],
        warnings=[
            "patient_spine.csv is TRE-internal patient-level data and is not an egress candidate.",
            "Source coverage should be compared between pathway groups before interpreting utilisation outcomes.",
            "Working cohort labels represent source/pathway membership, not causal treatment assignment."
        ],
        config_path=config_path,
    )
    stage_footer(
        stage_key="linkage",
        audit_dir=audit_dir,
        summary_path=summary_path,
        qa_files=[qa_dir / "04_linkage_overlap_qa.csv"],
    )

    return {
        "patient_spine": spine,
        "linkage_qa": linkage_qa,
    }
