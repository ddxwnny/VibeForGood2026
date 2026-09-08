"""
Composer port — AD-8.

There is exactly ONE Composer. It receives a single window and a senior name;
it never sees a prior period and it never decides what to include.
The LLM is the adapter; this port is the domain contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from recollect.core.weekly_window import ComposedWindow, ComposerInput


class ComposerPort(ABC):
    @abstractmethod
    async def compose(self, composer_input: ComposerInput) -> ComposedWindow:
        """
        Compose the weekly window for one senior.
        Must not embed prior-period comparisons; must not include scoring vocabulary.
        """
