"""
Application state for the API — the set of adapters the use cases run against.

Defaults are in-memory fakes so the app runs in dev with no external services.
The composition root (edge/api/container.py) swaps in real adapters (Postgres,
Anthropic, ElevenLabs, STT, Vault) from configuration. The senior registry
(id -> display_name) is used only by the roster endpoint, since the domain's
log port intentionally has no "list seniors" method.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from recollect.adapters.fake_alert import FakeAlert
from recollect.adapters.fake_audio_store import FakeAudioStore
from recollect.adapters.fake_composer import FakeComposer
from recollect.adapters.fake_delivery_log import FakeDeliveryLog
from recollect.adapters.fake_grant_store import FakeGrantStore
from recollect.adapters.fake_heartbeat import FakeHeartbeat
from recollect.adapters.fake_key_store import FakeKeyStore
from recollect.adapters.fake_log import FakeObservationLog
from recollect.adapters.fake_raw_audio import FakeRawAudio
from recollect.adapters.fake_stt import FakeSTT
from recollect.core.ports.alert_port import AlertPort
from recollect.core.ports.audio_store_port import AudioStorePort
from recollect.core.ports.composer_port import ComposerPort
from recollect.core.ports.delivery_port import DeliveryLogPort
from recollect.core.ports.grant_store_port import GrantStorePort
from recollect.core.ports.heartbeat_port import HeartbeatPort
from recollect.core.ports.key_store_port import KeyStorePort
from recollect.core.ports.llm_port import LLMPort
from recollect.core.ports.log_port import ObservationLogPort
from recollect.core.ports.raw_audio_port import RawAudioPort
from recollect.core.ports.stt_port import STTPort
from recollect.core.ports.tts_port import TTSPort


@dataclass
class AppState:
    log: ObservationLogPort = field(default_factory=FakeObservationLog)
    audio_store: AudioStorePort = field(default_factory=FakeAudioStore)
    heartbeat: HeartbeatPort = field(default_factory=FakeHeartbeat)
    alert: AlertPort = field(default_factory=FakeAlert)
    key_store: KeyStorePort = field(default_factory=FakeKeyStore)
    raw_audio: RawAudioPort = field(default_factory=FakeRawAudio)
    composer: ComposerPort = field(default_factory=FakeComposer)
    delivery_log: DeliveryLogPort = field(default_factory=FakeDeliveryLog)
    grant_store: GrantStorePort = field(default_factory=FakeGrantStore)
    stt: STTPort = field(default_factory=FakeSTT)
    llm: LLMPort | None = None       # real adapter injected when configured
    tts: TTSPort | None = None       # real adapter injected when configured
