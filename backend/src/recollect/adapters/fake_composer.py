"""Fake ComposerPort for tests — returns a configurable ComposedWindow."""

from __future__ import annotations

from recollect.core.ports.composer_port import ComposerPort
from recollect.core.weekly_window import (
    BASELINE_LEARNING_NOTE,
    ComposedWindow,
    ComposerInput,
)


class FakeComposer(ComposerPort):
    def __init__(
        self,
        recipient_text: str = "Mrs Tan rested well on Tuesday and handled her post on Thursday.",
        senior_text: str = "You rested well on Tuesday and handled your post on Thursday.",
        dated_detail_count: int = 1,
    ) -> None:
        self._recipient_text = recipient_text
        self._senior_text = senior_text
        self._dated_detail_count = dated_detail_count
        self.calls: list[ComposerInput] = []

    async def compose(self, composer_input: ComposerInput) -> ComposedWindow:
        self.calls.append(composer_input)
        if composer_input.is_baseline:
            note = " " + BASELINE_LEARNING_NOTE
            recipient = self._recipient_text + note
            senior = self._senior_text + note
        else:
            recipient = self._recipient_text
            senior = self._senior_text
        return ComposedWindow(
            recipient_text=recipient,
            senior_text=senior,
            dated_detail_count=self._dated_detail_count,
            is_baseline=composer_input.is_baseline,
            has_baseline_note=composer_input.is_baseline,
        )
