import re
from dataclasses import dataclass
from typing import Iterable


@dataclass
class SimpleRecognizerResult:
    entity_type: str
    start: int
    end: int
    score: float


class VietnamesePIIAnalyzer:
    """Small analyzer compatible with the Presidio analyze() call shape."""

    CCCD_RE = re.compile(r"(?<!\d)\d{12}(?!\d)")
    PHONE_RE = re.compile(r"(?<!\d)0?[35789]\d{8}(?!\d)")
    EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    NAME_RE = re.compile(
        r"\b[A-Za-zÀ-ỹĐđ]+(?:\s+[A-Za-zÀ-ỹĐđ]+){1,5}\b",
        re.UNICODE,
    )

    def analyze(
        self,
        text: str,
        language: str = "vi",
        entities: Iterable[str] | None = None,
        **_: object,
    ) -> list[SimpleRecognizerResult]:
        wanted = set(entities or ["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"])
        text = "" if text is None else str(text)
        results: list[SimpleRecognizerResult] = []

        if "EMAIL_ADDRESS" in wanted:
            results.extend(self._matches(text, self.EMAIL_RE, "EMAIL_ADDRESS", 0.9))
        if "VN_CCCD" in wanted:
            results.extend(self._matches(text, self.CCCD_RE, "VN_CCCD", 0.9))
        if "VN_PHONE" in wanted:
            results.extend(self._matches(text, self.PHONE_RE, "VN_PHONE", 0.85))
        if "PERSON" in wanted:
            results.extend(self._person_matches(text))

        return self._dedupe_overlaps(results)

    @staticmethod
    def _matches(
        text: str,
        pattern: re.Pattern[str],
        entity_type: str,
        score: float,
    ) -> list[SimpleRecognizerResult]:
        return [
            SimpleRecognizerResult(entity_type, match.start(), match.end(), score)
            for match in pattern.finditer(text)
        ]

    def _person_matches(self, text: str) -> list[SimpleRecognizerResult]:
        results: list[SimpleRecognizerResult] = []
        for match in self.NAME_RE.finditer(text):
            value = match.group(0).strip()
            lower = value.lower()
            if "@" in value or any(char.isdigit() for char in value):
                continue
            if lower in {"email", "cccd", "phone", "sdt"}:
                continue
            # Treat full-name-like cells and labels followed by names as PERSON.
            if len(value.split()) >= 2:
                results.append(SimpleRecognizerResult("PERSON", match.start(), match.end(), 0.65))
        return results

    @staticmethod
    def _dedupe_overlaps(
        results: list[SimpleRecognizerResult],
    ) -> list[SimpleRecognizerResult]:
        ordered = sorted(results, key=lambda r: (r.start, -(r.end - r.start), -r.score))
        kept: list[SimpleRecognizerResult] = []
        for result in ordered:
            if any(result.start < item.end and item.start < result.end for item in kept):
                continue
            kept.append(result)
        return kept


def build_vietnamese_analyzer() -> VietnamesePIIAnalyzer:
    return VietnamesePIIAnalyzer()


def detect_pii(text: str, analyzer: VietnamesePIIAnalyzer) -> list[SimpleRecognizerResult]:
    return analyzer.analyze(
        text=text,
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"],
    )
