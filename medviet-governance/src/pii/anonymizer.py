import hashlib
import random

import pandas as pd
from faker import Faker

from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")


def fake_cccd() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def fake_phone() -> str:
    return f"0{random.choice(['3', '5', '7', '8', '9'])}" + "".join(
        str(random.randint(0, 9)) for _ in range(8)
    )


def mask_value(value: str) -> str:
    if len(value) <= 2:
        return "*" * len(value)
    return value[0] + ("*" * (len(value) - 2)) + value[-1]


class MedVietAnonymizer:
    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        text = "" if text is None else str(text)
        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        anonymized = text
        for result in sorted(results, key=lambda item: item.start, reverse=True):
            original = anonymized[result.start : result.end]
            replacement = self._replacement_for(result.entity_type, original, strategy)
            anonymized = anonymized[: result.start] + replacement + anonymized[result.end :]
        return anonymized

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()

        if "ho_ten" in df_anon:
            df_anon["ho_ten"] = [fake.name() for _ in range(len(df_anon))]
        if "cccd" in df_anon:
            df_anon["cccd"] = [fake_cccd() for _ in range(len(df_anon))]
        if "so_dien_thoai" in df_anon:
            df_anon["so_dien_thoai"] = [fake_phone() for _ in range(len(df_anon))]
        if "email" in df_anon:
            df_anon["email"] = [fake.email() for _ in range(len(df_anon))]
        if "dia_chi" in df_anon:
            df_anon["dia_chi"] = [
                fake.address().replace("\n", ", ") for _ in range(len(df_anon))
            ]
        if "bac_si_phu_trach" in df_anon:
            df_anon["bac_si_phu_trach"] = [fake.name() for _ in range(len(df_anon))]
        if "ngay_sinh" in df_anon:
            df_anon["ngay_sinh"] = df_anon["ngay_sinh"].map(self._generalize_birth_date)

        return df_anon

    def calculate_detection_rate(self, original_df: pd.DataFrame, pii_columns: list) -> float:
        total = 0
        detected = 0

        for col in pii_columns:
            if col not in original_df:
                continue
            for value in original_df[col].astype(str):
                total += 1
                if detect_pii(value, self.analyzer):
                    detected += 1

        return detected / total if total > 0 else 0.0

    @staticmethod
    def _replacement_for(entity_type: str, original: str, strategy: str) -> str:
        if strategy == "mask":
            return mask_value(original)
        if strategy == "hash":
            return hashlib.sha256(original.encode("utf-8")).hexdigest()
        if strategy != "replace":
            raise ValueError(f"Unsupported anonymization strategy: {strategy}")

        replacements = {
            "PERSON": fake.name(),
            "EMAIL_ADDRESS": fake.email(),
            "VN_CCCD": fake_cccd(),
            "VN_PHONE": fake_phone(),
        }
        return replacements.get(entity_type, "<ANONYMIZED>")

    @staticmethod
    def _generalize_birth_date(value: object) -> str:
        text = "" if pd.isna(value) else str(value)
        year = text[-4:] if len(text) >= 4 and text[-4:].isdigit() else "unknown"
        return f"year:{year}"
