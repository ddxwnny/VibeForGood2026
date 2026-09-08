"""
Application settings, environment-injected and validated at boot (Architecture
Spine "Config" convention).

Every external dependency the app talks to is configured here. A missing
setting for a *configured* service is a boot failure, not a silent default —
the app never quietly falls back to mock data in a real environment.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="RECOLLECT_", extra="ignore")

    # Runtime mode: "dev" permits in-memory adapters when services aren't
    # configured; anything else requires real adapters for every service.
    environment: str = "dev"

    # --- Persistence (PostgreSQL) ---
    database_url: str = ""

    # --- LLM (Anthropic, decided) ---
    anthropic_api_key: str = ""
    anthropic_model_id: str = "claude-sonnet-5"     # pinned, never a floating alias (AD-15)
    anthropic_weekly_model_id: str = "claude-opus-5"

    # --- TTS (ElevenLabs, assumed) ---
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    elevenlabs_base_url: str = "https://api.elevenlabs.io"

    # --- STT (provider undecided — see Architecture Spine Deferred) ---
    stt_base_url: str = ""
    stt_api_key: str = ""

    # --- Key management (AD-13; custody deferred) ---
    vault_url: str = ""
    vault_token: str = ""

    @property
    def use_real_database(self) -> bool:
        return bool(self.database_url)

    @property
    def use_real_llm(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def use_real_tts(self) -> bool:
        return bool(self.elevenlabs_api_key)

    @property
    def use_real_stt(self) -> bool:
        return bool(self.stt_base_url)

    @property
    def use_real_key_store(self) -> bool:
        return bool(self.vault_url)


def require_real_services(settings: Settings) -> None:
    """
    Boot-time gate for non-dev environments: every voice and persistence
    dependency must be configured, or the app fails to start rather than
    running on mock data.
    """
    if settings.environment == "dev":
        return

    missing: list[str] = []
    if not settings.use_real_database:
        missing.append("RECOLLECT_DATABASE_URL")
    if not settings.use_real_llm:
        missing.append("RECOLLECT_ANTHROPIC_API_KEY")
    if not settings.use_real_tts:
        missing.append("RECOLLECT_ELEVENLABS_API_KEY")
    if not settings.use_real_stt:
        missing.append("RECOLLECT_STT_BASE_URL")
    if not settings.use_real_key_store:
        missing.append("RECOLLECT_VAULT_URL")

    if missing:
        raise RuntimeError(
            "Real services are required outside dev, but these are not configured: "
            + ", ".join(missing)
        )
