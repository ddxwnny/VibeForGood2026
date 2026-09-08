"""
Composition root — builds the adapter set from configuration.

Real adapters are constructed only when their service is configured; otherwise
the in-memory fakes remain (dev). `require_real_services` (in settings.py) is
the gate that prevents a non-dev environment from silently running on fakes.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from recollect.adapters.anthropic_llm import AnthropicLLM
from recollect.adapters.elevenlabs_tts import ElevenLabsTTS
from recollect.adapters.http_stt import HttpSTT
from recollect.adapters.postgres.observation_log import PostgresObservationLog
from recollect.adapters.vault_key_store import VaultKeyStore
from recollect.edge.api.settings import Settings
from recollect.edge.api.state import AppState


def build_store(settings: Settings) -> AppState:
    store = AppState()

    if settings.use_real_database:
        engine = create_async_engine(settings.database_url)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        store.log = PostgresObservationLog(session_factory)

    if settings.use_real_llm:
        store.llm = AnthropicLLM(
            api_key=settings.anthropic_api_key,
            model_id=settings.anthropic_model_id,
        )

    if settings.use_real_tts:
        store.tts = ElevenLabsTTS(
            api_key=settings.elevenlabs_api_key,
            voice_id=settings.elevenlabs_voice_id,
            base_url=settings.elevenlabs_base_url,
        )

    if settings.use_real_stt:
        store.stt = HttpSTT(
            base_url=settings.stt_base_url,
            api_key=settings.stt_api_key,
        )

    if settings.use_real_key_store:
        store.key_store = VaultKeyStore(
            vault_url=settings.vault_url,
            vault_token=settings.vault_token,
        )

    return store
