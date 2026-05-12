import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pii.anonymizer import MedVietAnonymizer
from src.quality.validation import validate_anonymized_data


def main() -> None:
    raw_path = Path("data/raw/patients_raw.csv")
    processed_path = Path("data/processed/patients_anonymized.csv")
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(raw_path)
    df_anon = MedVietAnonymizer().anonymize_dataframe(df)
    df_anon.to_csv(processed_path, index=False)

    validation = validate_anonymized_data(str(processed_path))
    print(f"Wrote {processed_path}")
    print(validation)


if __name__ == "__main__":
    main()
