"""
Redaction of named third parties to role (FR-3, story 4.1).

The record may hold "her daughter", never a named person who never consented.
The caller supplies a mapping of names to roles (the senior's own name and any
consented party are simply absent from the map, so they are left untouched).
Longest names are replaced first so that a short name never clobbers a longer one.
"""

from __future__ import annotations


def redact_named_parties(text: str, person_roles: dict[str, str]) -> str:
    """Replace every occurrence of each named person with their role."""
    redacted = text
    for name in sorted(person_roles, key=len, reverse=True):
        redacted = redacted.replace(name, person_roles[name])
    return redacted
