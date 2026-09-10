from __future__ import annotations

from ..context.models import ContextEntry
from ..context.rendering import render_manifest
from .console import context_manifest
from .console import BOLD, _paint


def print_context_manifest(entries: list[ContextEntry], *, purpose: str) -> None:
    print(_paint(f"\nResources used for {purpose}\n".upper(), BOLD))
    context_manifest(render_manifest(entries))
    print()


def print_model_context(prompt: str, *, purpose: str) -> None:
    """Display the exact prompt content passed to the model."""
    print(_paint(f"\nContext sent to Ollama for {purpose}\n".upper(), BOLD))
    print(prompt)
    print()
