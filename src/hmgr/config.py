from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    model: str = "Qwen2.5-Coder:7b"

    base_branch: str = "main"

    ollama_url: str = "http://localhost:11434"

    max_context_chars: int = 30_000
    max_optional_context_chars: int = 15_000
    max_file_chars: int = 4_000
    context_window_tokens: int = 24_576

    max_relevant_files: int = 5
    max_related_files: int = 2

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            model=os.getenv(
                "HMGR_MODEL",
                "Qwen2.5-Coder:7b",
            ),
            base_branch=os.getenv(
                "HMGR_BASE",
                "main",
            ),
            ollama_url=os.getenv(
                "OLLAMA_URL",
                "http://localhost:11434",
            ),
            max_context_chars=int(
                os.getenv(
                    "HMGR_MAX_CONTEXT_CHARS",
                    "30000",
                )
            ),
            max_optional_context_chars=int(
                os.getenv(
                    "HMGR_MAX_OPTIONAL_CONTEXT_CHARS",
                    "15000",
                )
            ),
            max_file_chars=int(
                os.getenv(
                    "HMGR_MAX_FILE_CHARS",
                    "4000",
                )
            ),
            context_window_tokens=int(
                os.getenv(
                    "HMGR_CONTEXT_WINDOW_TOKENS",
                    "24576",
                )
            ),
            max_relevant_files=int(
                os.getenv(
                    "HMGR_MAX_RELEVANT_FILES",
                    "5",
                )
            ),
            max_related_files=int(
                os.getenv(
                    "HMGR_MAX_RELATED_FILES",
                    "2",
                )
            ),
        )
