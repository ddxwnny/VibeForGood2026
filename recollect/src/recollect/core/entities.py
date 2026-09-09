"""
Core domain entities for Recollect.

All entities are immutable dataclasses. The observation log is append-only:
corrections arrive as new superseding events (AD-1). No entity here depends
on any infrastructure — core depends on nothing (Architecture Spine).

Banned names: Patient, Score, Level, Risk, Flag (Architecture Spine conventions).
IDs: UUIDv7 prefixed by type in logs (snr_, obs_, int_).
Timestamps: UTC datetime; windowing in Asia/Singapore is the caller's concern (AD-11).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


class SignalType(str, Enum):
    """Observable signal types from signal-catalog.md. v1 records, never scores."""
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    MAIL = "mail"
    ROUTINE = "routine"
    MEMORY = "memory"
    PLACE_MEMORY = "place_memory"
    DATE_TIME = "date_time"
    LANGUAGE = "language"
    MISPLACING = "misplacing"
    JUDGEMENT = "judgement"
    FINANCES = "finances"
    ATTENTION = "attention"
    SOCIAL_BEHAVIOURAL = "social_behavioural"
    INSTRUMENT = "instrument"
    MOOD = "mood"
    SLEEP = "sleep"
    APPETITE = "appetite"
    MENTION = "mention"


class TaskOutcome(str, Enum):
    COMPLETED = "completed"
    DECLINED = "declined"
    INCOMPLETE = "incomplete"
    UNRECOGNISED = "unrecognised"


class GapReason(str, Enum):
    DEVICE_UNREACHABLE = "device_unreachable"
    UNRECOGNISED = "unrecognised"


class ErasureReason(str, Enum):
    """Reasons a senior's data is crypto-shredded (AD-13)."""
    WITHDRAWAL = "withdrawal"
    DEATH = "death"


class ConsentArtifactKind(str, Enum):
    ULYSSES_INSTRUCTION = "ulysses_instruction"        # own-voice recording (FR-23)
    RECIPIENT_CO_SIGNATURE = "recipient_co_signature"  # named recipient co-signs
    RESEARCH_CONSENT = "research_consent"
    PROCESSOR_DISCLOSURE = "processor_disclosure"      # four processors acknowledged

    @classmethod
    def required_set(cls) -> frozenset[ConsentArtifactKind]:
        return frozenset({
            cls.ULYSSES_INSTRUCTION,
            cls.RECIPIENT_CO_SIGNATURE,
            cls.RESEARCH_CONSENT,
            cls.PROCESSOR_DISCLOSURE,
        })


class GrantRole(str, Enum):
    NAMED_RECIPIENT = "named_recipient"
    CARE_WORKER = "care_worker"
    RESEARCHER = "researcher"


class GrantScope(str, Enum):
    WEEKLY_WINDOW = "weekly_window"
    ROSTER = "roster"
    RESEARCH_PROJECTION = "research_projection"


# ---------------------------------------------------------------------------
# Observation provenance (AD-10)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Provenance:
    """Every observation must carry this; write is rejected without it (AD-10)."""
    interaction_id: UUID
    occurred_at: datetime          # UTC (AD-11)
    signal_type: SignalType
    item_variant: str | None = None   # set for instrument items (AD-9)
    extraction_model_id: str | None = None   # versioned (AD-15)
    prompt_version: str | None = None        # versioned (AD-15)
    stt_model_version: str | None = None     # versioned (AD-15)


# ---------------------------------------------------------------------------
# Core entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Senior:
    """Owned exclusively by the Enrolment context (AD-7)."""
    id: UUID
    display_name: str          # how the device addresses her (FR-30)
    preferred_language: str    # IETF tag, e.g. "zh-cmn-Hans-SG"
    created_at: datetime       # UTC


@dataclass(frozen=True)
class Interaction:
    """
    Minted by the device (AD-14). UUIDv7 id, occurred-at, idempotency key.
    Ingest is idempotent on idempotency_key and never mints its own.
    """
    id: UUID
    senior_id: UUID
    occurred_at: datetime      # UTC, authoritative device clock (AD-14)
    idempotency_key: str


@dataclass(frozen=True)
class Observation:
    """
    Immutable, dated, provenance-carrying event (AD-1, AD-10).
    Never edited — a correction is a new Observation with supersedes_id set.
    An Observation without full provenance must be rejected at write (AD-10).
    Payloads encrypted under per-senior key (AD-13); content never in logs (NFR-16).
    """
    id: UUID
    senior_id: UUID
    provenance: Provenance
    content: str                       # encrypted payload in storage; plain text in domain
    outcome: TaskOutcome | None = None
    supersedes_id: UUID | None = None  # set when this event corrects a prior one


@dataclass(frozen=True)
class Gap:
    """
    Recorded when the device is unreachable or a turn is unrecognised (AD-6).
    A Gap is never an observation about the senior — it is a record about the device
    or the pipeline. The windowed read model excludes gap periods (FR-24, FR-25).
    """
    id: UUID
    senior_id: UUID
    reason: GapReason
    started_at: datetime    # UTC
    ended_at: datetime | None = None  # None = still open


@dataclass(frozen=True)
class Tombstone:
    """
    Appended on withdrawal or death (AD-13). The log structure survives; the
    content becomes unrecoverable because the per-senior key is destroyed.
    stores_shredded enumerates every store the erasure path reached.
    """
    id: UUID
    senior_id: UUID
    reason: ErasureReason
    shredded_at: datetime                 # UTC
    stores_shredded: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class ConsentArtifact:
    """One of the four artefacts required for active enrolment (FR-21, AD-4)."""
    id: UUID
    enrolment_id: UUID
    kind: ConsentArtifactKind
    captured_at: datetime     # UTC; all four timestamped to the visit (FR-22)
    audio_ref: str | None = None  # only set for ULYSSES_INSTRUCTION (FR-23)


@dataclass(frozen=True)
class Enrolment:
    """
    A senior's enrolment. Active only when all four consent artefacts are present.
    The write path rejects observations for a senior without an active enrolment (AD-4).
    """
    id: UUID
    senior_id: UUID
    enrolled_at: datetime     # UTC
    artefacts: frozenset[ConsentArtifactKind] = field(default_factory=frozenset)
    withdrawn_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        """All four artefacts captured and not withdrawn."""
        return (
            ConsentArtifactKind.required_set().issubset(self.artefacts)
            and self.withdrawn_at is None
        )


@dataclass(frozen=True)
class Grant:
    """
    Authorises a person (by role, never by unsolicited name) to access a
    senior's data within a defined scope. Family and care workers are Grants,
    not entities of their own (AD-7).
    """
    id: UUID
    senior_id: UUID
    role: GrantRole
    scope: GrantScope
    granted_at: datetime   # UTC
    revoked_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None
