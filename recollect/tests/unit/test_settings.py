"""Tests for Settings boot validation."""

import pytest

from recollect.edge.api.settings import Settings, require_real_services


def test_dev_mode_allows_missing_services() -> None:
    settings = Settings(environment="dev")
    require_real_services(settings)  # must not raise


def test_production_requires_real_services() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        anthropic_api_key="",
        openrouter_api_key="",
        elevenlabs_api_key="",
    )
    with pytest.raises(RuntimeError) as exc:
        require_real_services(settings)
    assert "RECOLLECT_DATABASE_URL" in str(exc.value)
    assert "RECOLLECT_OPENROUTER_API_KEY" in str(exc.value)


def test_production_passes_when_services_configured() -> None:
    settings = Settings(
        environment="production",
        database_url="postgresql+asyncpg://u:p@host/db",
        anthropic_api_key="k",
        elevenlabs_api_key="k",
        stt_base_url="https://stt.example",
        vault_url="https://vault.example",
    )
    require_real_services(settings)  # must not raise
