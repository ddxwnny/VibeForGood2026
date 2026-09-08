"""
Egress policy (AD-2) — device-side enforcement, tested as network egress.

Audio may leave the device only toward a named processor in the enrolment
allowlist (named in consent, contracted for zero retention / no training,
Singapore-resident, enumerable for AD-13 erasure). Every other outbound
destination is denied. This is the object the AD-2 architecture test asserts
on — a dependency-direction test cannot see a socket, so the guarantee lives
here as a boot-validated policy, not a code convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from recollect.core.errors import UnnamedProcessorError


@dataclass(frozen=True)
class Processor:
    """A named processor from the enrolment consent (AD-16)."""
    name: str
    host: str
    purpose: str          # "stt" | "tts" | "llm"
    region: str = "SG"    # Singapore-resident (AD-2)


@dataclass(frozen=True)
class EgressPolicy:
    """
    The set of hosts the device is permitted to reach. Constructed from
    configuration at boot and immutable thereafter; adding a processor is a
    consent change, not a deployment change (AD-2).
    """
    allowlist: frozenset[str] = field(default_factory=frozenset)

    def assert_egress_allowed(self, destination_host: str) -> None:
        """Raises UnnamedProcessorError if the destination is not allowlisted."""
        if destination_host not in self.allowlist:
            raise UnnamedProcessorError(
                f"Egress to {destination_host!r} denied: not a named processor "
                "in the enrolment allowlist (AD-2)."
            )


def build_egress_policy(processors: list[Processor]) -> EgressPolicy:
    """
    Boot-time validation: builds the allowlist from named processors. Rejects
    duplicate hosts and non-Singapore processors so a misconfigured allowlist
    is a boot failure, not a silent widening of the egress surface (AD-2).
    """
    hosts: set[str] = set()
    for p in processors:
        if p.host in hosts:
            raise UnnamedProcessorError(f"Duplicate processor host {p.host!r} in allowlist.")
        if p.region != "SG":
            raise UnnamedProcessorError(
                f"Processor {p.name!r} is not Singapore-resident (region={p.region!r})."
            )
        hosts.add(p.host)
    return EgressPolicy(allowlist=frozenset(hosts))
