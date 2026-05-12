import re
from pathlib import Path

import pandas as pd

VALID_CONDITIONS = {"Tieu duong", "Huyet ap cao", "Tim mach", "Khoe manh"}
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def build_patient_expectation_suite() -> dict:
    """
    Lightweight expectation-suite description for environments without
    Great Expectations installed.
    """
    return {
        "suite_name": "patient_data_suite",
        "expectations": [
            "patient_id not null",
            "cccd length equals 12",
            "ket_qua_xet_nghiem between 0 and 50",
            "benh belongs to allowed condition set",
            "email matches email regex",
            "patient_id unique",
        ],
    }


def validate_anonymized_data(filepath: str) -> dict:
    df = pd.read_csv(filepath, dtype={"cccd": str, "so_dien_thoai": str})
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns),
        },
    }

    def fail(message: str) -> None:
        results["success"] = False
        results["failed_checks"].append(message)

    important_columns = ["patient_id", "cccd", "so_dien_thoai", "email", "benh"]
    missing_columns = [column for column in important_columns if column not in df.columns]
    if missing_columns:
        fail(f"Missing required columns: {missing_columns}")
        return results

    if df[important_columns].isnull().any().any():
        fail("Null values found in important columns")

    if not df["patient_id"].is_unique:
        fail("Duplicate patient_id values found")

    if not df["cccd"].astype(str).str.fullmatch(r"\d{12}").all():
        fail("CCCD values must be 12 digits after replacement")

    if not df["so_dien_thoai"].astype(str).str.fullmatch(r"0[35789]\d{8}").all():
        fail("Phone values must match Vietnamese mobile format")

    if not df["email"].astype(str).map(lambda value: bool(EMAIL_RE.match(value))).all():
        fail("Email values must match email format")

    if "ket_qua_xet_nghiem" in df and not df["ket_qua_xet_nghiem"].between(0, 50).all():
        fail("ket_qua_xet_nghiem values must be between 0 and 50")

    raw_path = Path(filepath).resolve().parents[1] / "raw" / "patients_raw.csv"
    if raw_path.exists():
        original_df = pd.read_csv(raw_path, dtype={"cccd": str, "so_dien_thoai": str})
        if len(df) != len(original_df):
            fail("Anonymized row count does not match raw dataset")

        original_cccd = set(original_df["cccd"].astype(str))
        anonymized_cccd = set(df["cccd"].astype(str))
        if original_cccd & anonymized_cccd:
            fail("Original CCCD values still appear in anonymized data")

    return results
