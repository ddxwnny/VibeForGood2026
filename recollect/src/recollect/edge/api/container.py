"""
Composition root — builds the adapter set from configuration.

Real adapters are constructed only when their service is configured; otherwise
the in-memory fakes remain (dev). `require_real_services` (in settings.py) is
the gate that prevents a non-dev environment from silently running on fakes.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from recollect.adapters.anthropic_llm import AnthropicLLM
from recollect.adapters.deepgram_stt import DeepgramSTT
from recollect.adapters.elevenlabs_tts import ElevenLabsTTS
from recollect.adapters.http_stt import HttpSTT
from recollect.adapters.openrouter_llm import OpenRouterLLM
from recollect.adapters.postgres.grant_store import PostgresGrantStore
from recollect.adapters.postgres.heartbeat import PostgresHeartbeat
from recollect.adapters.postgres.observation_log import PostgresObservationLog
from recollect.adapters.vault_key_store import VaultKeyStore
from recollect.edge.api.settings import Settings
from recollect.edge.api.state import AppState


def build_store(settings: Settings) -> AppState:
    store = AppState()

    if settings.use_real_database:
        db_url = settings.database_url
        if "sqlite" in db_url and ":memory:" not in db_url:
            import os
            import shutil
            import tempfile
            from pathlib import Path

            # In serverless environments (e.g. Vercel, AWS Lambda), the deployment directory is read-only.
            # Copy/point database to /tmp which has full read-write permissions.
            if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                tmp_db = Path(tempfile.gettempdir()) / "recollect_local.db"
                repo_db = Path(__file__).resolve().parents[4] / "recollect_local.db"
                if not repo_db.is_file():
                    repo_db = Path.cwd() / "recollect_local.db"
                if repo_db.is_file() and not tmp_db.exists():
                    try:
                        shutil.copyfile(repo_db, tmp_db)
                    except Exception:
                        pass
                db_url = f"sqlite+aiosqlite:///{tmp_db.as_posix()}"

        engine = create_async_engine(db_url)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        store.log = PostgresObservationLog(session_factory)
        store.heartbeat = PostgresHeartbeat(session_factory)
        store.grant_store = PostgresGrantStore(session_factory)
        setattr(store, "engine", engine)

    if settings.use_real_llm:
        if settings.groq_api_key:
            from recollect.adapters.groq_llm import GroqLLM
            store.llm = GroqLLM(
                api_key=settings.groq_api_key,
                model_id=settings.groq_model_id,
            )
        elif settings.openrouter_api_key:
            store.llm = OpenRouterLLM(
                api_key=settings.openrouter_api_key,
                model_id=settings.openrouter_model_id,
            )
        else:
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
        if settings.deepgram_api_key:
            store.stt = DeepgramSTT(
                api_key=settings.deepgram_api_key,
                model=settings.deepgram_model,
            )
        else:
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
