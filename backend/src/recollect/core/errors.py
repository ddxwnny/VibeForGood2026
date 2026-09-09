"""
Typed domain errors. Rule violations raise these and fail the write — never
a warning, never a log-and-continue (Architecture Spine conventions).
"""


class RecollectError(Exception):
    """Base for all domain errors."""


class MissingProvenanceError(RecollectError):
    """Raised when an Observation write lacks required provenance (AD-10)."""


class InactiveEnrolmentError(RecollectError):
    """Raised when an Observation is written for a senior without an active enrolment (AD-4)."""


class PartialEnrolmentError(RecollectError):
    """Raised when an Enrolment is marked active with fewer than four artefacts (FR-22)."""


class ImmutableObservationError(RecollectError):
    """Raised when code attempts to update or delete an existing Observation (AD-1)."""


class DuplicateInteractionError(RecollectError):
    """Raised when Ingest receives an interaction whose idempotency key already exists (AD-14)."""


class ForbiddenComparisonError(RecollectError):
    """Raised when a read-model query tries to aggregate, score, or compare entries (AD-3)."""


class UnnamedProcessorError(RecollectError):
    """Raised when audio would egress to a processor not in the enrolment allowlist (AD-2, AD-16)."""


class NonTaskSignalError(RecollectError):
    """Raised when record_task is asked to record a non-task signal type (FR-4..7)."""


class AlreadyErasedError(RecollectError):
    """Raised when erasing a senior who already has a tombstone (AD-13)."""
