"""
Audio store port — used exclusively for the own-voice Ulysses consent recording.

This is the sole exception to AD-2's no-durable-audio rule: the enrolment
consent recording is a deliberate durable artefact (AD-2, Architecture Spine).
All other audio is destroyed after transcription and never touches this port.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AudioStorePort(ABC):
    @abstractmethod
    async def store_consent_audio(
        self,
        senior_id_str: str,
        audio_bytes: bytes,
    ) -> str:
        """
        Stores the Ulysses instruction audio and returns an opaque ref string.
        The ref is recorded on the ConsentArtifact (FR-23).
        Only consent audio may be stored here — never interaction audio (AD-2).
        """
        ...

    @abstractmethod
    async def get_consent_audio(self, audio_ref: str) -> bytes: ...

    @abstractmethod
    async def shred_senior(self, senior_id_str: str) -> None:
        """
        Removes all consent audio for a senior. The erasure path reaches this
        store on withdrawal or death (AD-13 reach: enrolment consent audio).
        """
        ...
