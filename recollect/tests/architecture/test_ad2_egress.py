"""
AD-2 egress-policy architecture test.

AD-2 (no audio to an unnamed party) is tested as network egress, not as an
import graph. The egress policy denies every outbound destination except the
named-processor allowlist; a misconfigured allowlist (duplicate host, non-SG
processor) is a boot failure.
"""

import pytest

from recollect.core.egress_policy import EgressPolicy, Processor, build_egress_policy
from recollect.core.errors import UnnamedProcessorError


def test_egress_to_allowlisted_processor_permitted() -> None:
    policy = EgressPolicy(allowlist=frozenset({"stt.sg.example"}))
    policy.assert_egress_allowed("stt.sg.example")  # must not raise


def test_egress_to_unnamed_processor_denied() -> None:
    policy = EgressPolicy(allowlist=frozenset({"stt.sg.example"}))
    with pytest.raises(UnnamedProcessorError):
        policy.assert_egress_allowed("unknown.example.com")


def test_empty_allowlist_denies_all() -> None:
    policy = EgressPolicy(allowlist=frozenset())
    with pytest.raises(UnnamedProcessorError):
        policy.assert_egress_allowed("anything.example.com")


def test_build_policy_from_named_processors() -> None:
    policy = build_egress_policy([
        Processor(name="STT", host="stt.sg.example", purpose="stt"),
        Processor(name="TTS", host="tts.sg.example", purpose="tts"),
    ])
    assert policy.allowlist == frozenset({"stt.sg.example", "tts.sg.example"})


def test_build_policy_rejects_duplicate_host() -> None:
    with pytest.raises(UnnamedProcessorError):
        build_egress_policy([
            Processor(name="A", host="stt.sg.example", purpose="stt"),
            Processor(name="B", host="stt.sg.example", purpose="tts"),
        ])


def test_build_policy_rejects_non_singapore_processor() -> None:
    with pytest.raises(UnnamedProcessorError):
        build_egress_policy([
            Processor(name="A", host="stt.us.example", purpose="stt", region="US"),
        ])
