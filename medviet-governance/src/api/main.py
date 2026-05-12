from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException

from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer

app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "patients_raw.csv"


def load_patients() -> pd.DataFrame:
    if not RAW_DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Raw patient dataset not found")
    return pd.read_csv(RAW_DATA_PATH)


@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(current_user: dict = Depends(get_current_user)):
    df = load_patients()
    return {"records": df.head(10).to_dict(orient="records")}


@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(current_user: dict = Depends(get_current_user)):
    df = load_patients()
    df_anon = anonymizer.anonymize_dataframe(df)
    return {"records": df_anon.head(10).to_dict(orient="records")}


@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(current_user: dict = Depends(get_current_user)):
    df = load_patients()
    by_condition = df["benh"].value_counts().sort_index().to_dict()
    return {
        "total_patients": int(len(df)),
        "patients_by_condition": by_condition,
        "average_lab_result": float(df["ket_qua_xet_nghiem"].mean()),
    }


@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    return {
        "status": "accepted",
        "patient_id": patient_id,
        "message": "Delete request authorized for admin workflow",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}
