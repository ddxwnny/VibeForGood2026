"""
Application settings, environment-injected and validated at boot (Architecture
Spine "Config" convention).

Every external dependency the app talks to is configured here. A missing
setting for a *configured* service is a boot failure, not a silent default —
the app never quietly falls back to mock data in a real environment.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILES = [
    str(Path.cwd() / ".env"),
    str(Path.cwd() / "recollect" / ".env"),
    str(Path(__file__).resolve().parents[3] / ".env"),
    str(Path(__file__).resolve().parents[4] / ".env"),
    ".env",
    "recollect/.env",
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILES, env_prefix="RECOLLECT_", extra="ignore")

    # Runtime mode: "dev" permits in-memory adapters when services aren't
    # configured; anything else requires real adapters for every service.
    environment: str = "dev"
    seed_demo_data: bool = True

    # --- Persistence (PostgreSQL) ---
    database_url: str = ""

    # --- LLM (Anthropic or OpenRouter) ---
    anthropic_api_key: str = ""
    anthropic_model_id: str = "claude-sonnet-5"     # pinned, never a floating alias (AD-15)
    anthropic_weekly_model_id: str = "claude-opus-5"

    openrouter_api_key: str = ""
    openrouter_model_id: str = "meta-llama/llama-3.3-70b-instruct:free"

    # --- LLM (Groq) ---
    groq_api_key: str = ""
    groq_model_id: str = "qwen/qwen3.8-27b"

    # --- TTS (ElevenLabs, assumed) ---
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    elevenlabs_base_url: str = "https://api.elevenlabs.io"

    # --- STT (Deepgram or generic HTTP STT) ---
    stt_base_url: str = ""
    stt_api_key: str = ""
    deepgram_api_key: str = ""
    deepgram_model: str = "nova-3"

    # --- Key management (AD-13; custody deferred) ---
    vault_url: str = ""
    vault_token: str = ""

    # --- Device + phone-surface credentials (NFR-15, AD-14, AD-16) ---
    # The device authenticates with this shared key to record heartbeats and
    # report turns; the senior never authenticates. Human surfaces authenticate
    # via per-grant API keys resolved against GrantStorePort.
    device_api_key: str = ""

    # --- CORS (api-standards: explicit origin whitelist, never "*" in prod) ---
    # Comma-separated allowlist of browser origins. Empty means "same-origin only"
    # (the Node proxy serves frontend + backend from the same origin). Dev may set
    # e.g. "http://localhost:3000,http://127.0.0.1:3000" for split-hosting.
    cors_allow_origins: str = ""

    # --- TLS / HSTS (security-standards: HSTS in production) ---
    # When behind a TLS-terminating proxy, enable Strict-Transport-Security.
    hsts_enabled: bool = False
    hsts_max_age: int = 63072000

    @property
    def use_real_database(self) -> bool:
        return bool(self.database_url)

    @property
    def use_real_llm(self) -> bool:
        return bool(self.anthropic_api_key or self.groq_api_key or self.openrouter_api_key)

    @property
    def use_real_tts(self) -> bool:
        return bool(self.elevenlabs_api_key)

    @property
    def use_real_stt(self) -> bool:
        return bool(self.deepgram_api_key or self.stt_base_url)

    @property
    def use_real_key_store(self) -> bool:
        return bool(self.vault_url)

    @property
    def cors_origin_list(self) -> list[str]:
        """Parsed origin allowlist; empty list means same-origin only (no CORS header)."""
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


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
        missing.append("RECOLLECT_OPENROUTER_API_KEY (or RECOLLECT_ANTHROPIC_API_KEY)")
    if not settings.use_real_tts:
        missing.append("RECOLLECT_ELEVENLABS_API_KEY")
    if not settings.use_real_stt:
        missing.append("RECOLLECT_DEEPGRAM_API_KEY (or RECOLLECT_STT_BASE_URL)")
    if not settings.use_real_key_store:
        missing.append("RECOLLECT_VAULT_URL")

    if missing:
        raise RuntimeError(
            "Real services are required outside dev, but these are not configured: "
            + ", ".join(missing)
        )
