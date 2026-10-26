import re
from pathlib import Path

_JA4C_PATTERN = re.compile(r"^[0-9a-f]{12}$")
_JA4_PATTERN = re.compile(r"^[^_]+_[0-9a-f]{12}_[0-9a-f]{12}$")


def load_blocklist(path):
    entries = set()
    with Path(path).open(encoding="utf-8") as blocklist_file:
        for line_number, line in enumerate(blocklist_file, start=1):
            entry = line.partition("#")[0].strip().lower()
            if not entry:
                continue
            if not (_JA4C_PATTERN.fullmatch(entry) or _JA4_PATTERN.fullmatch(entry)):
                raise ValueError(
                    f"Invalid blocklist entry on line {line_number}: "
                    "expected a 12-character JA4C hash or a full JA4 fingerprint"
                )
            entries.add(entry)
    return frozenset(entries)


def is_blocked(fingerprint, entries):
    fingerprint = fingerprint.strip().lower()
    if fingerprint in entries:
        return True

    parts = fingerprint.split("_")
    return len(parts) >= 2 and parts[1] in entries
