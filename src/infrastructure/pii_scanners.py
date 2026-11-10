import re

from src.domain.entities import PIIMatch
from src.domain.ports import PIIScannerPort

# Default detection rules, keyed by the PII type used in the token name
DEFAULT_PII_RULES: dict[str, str] = {
    "EMAIL": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "AWS_KEY": r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
    "GITHUB_TOKEN": r"\b(?:gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82})\b",
    "PRIVATE_KEY": (
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----"
    ),
    "IPV4": r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b",
}


class RegexScannerAdapter(PIIScannerPort):
    """Infrastructure implementation of the scanner port using Regex."""

    def __init__(self, rules: dict[str, str] | None = None):
        rules = DEFAULT_PII_RULES if rules is None else rules
        self.patterns: dict[str, re.Pattern[str]] = {
            name: re.compile(pattern) for name, pattern in rules.items()
        }

    def scan(self, payload: str) -> list[PIIMatch]:
        matches = []
        for pii_type, pattern in self.patterns.items():
            for match in pattern.finditer(payload):
                matches.append(
                    PIIMatch(pii_type=pii_type, original_value=match.group(0))
                )
        return matches
