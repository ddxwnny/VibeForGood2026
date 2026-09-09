"""
Retention catalog (FR-27, Story 7.2).

Every store holding a senior's content has a defined retention, access
boundary, and end-of-life path covering withdrawal and death. This module is
the single place that enumerates those definitions, so the erasure path can be
enumerated by inspection rather than remembered (AD-13, AD-16).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetentionPolicy:
    store: str
    retention: str          # how long content is kept
    access_boundary: str    # who may read it
    end_of_life: str        # withdrawal + death path


RETENTION_CATALOG: frozenset[RetentionPolicy] = frozenset({
    RetentionPolicy(
        store="raw_audio",
        retention="discarded once features are extracted (retention sweep)",
        access_boundary="in-memory only; never durable; no human access",
        end_of_life="discarded by sweep; shredded on withdrawal or death",
    ),
    RetentionPolicy(
        store="consent_audio",
        retention="until withdrawal or death",
        access_boundary="enrolment context only (own-voice Ulysses instruction)",
        end_of_life="crypto-shred on withdrawal or death",
    ),
    RetentionPolicy(
        store="observation_log_payloads",
        retention="stated retention period for days- and months-long windows",
        access_boundary="windowed read model via Grants (no comparison primitives)",
        end_of_life="per-senior key destroyed; tombstone appended; content unrecoverable",
    ),
})


def retention_policy_for(store: str) -> RetentionPolicy | None:
    """Returns the policy for a named store, or None if it is not catalogued."""
    return next((p for p in RETENTION_CATALOG if p.store == store), None)
