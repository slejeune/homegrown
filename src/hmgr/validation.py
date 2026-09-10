from __future__ import annotations

import re
from .models import CommitProposal, IssueProposal, PullRequestProposal


_PATH = re.compile(r"`([^`]+)`")


def mark_unverified_file_references(text: str, existing_paths: set[str]) -> str:
    """Prevent model-invented backticked repository paths from looking factual."""

    def replace(match: re.Match[str]) -> str:
        value = match.group(1).strip()
        if (
            not value
            or value in existing_paths
            or value.startswith(("http://", "https://"))
        ):
            return match.group(0)
        path_like = (
            "/" in value
            or value.startswith(("src/", "tests/", "lib/", "app/", "./"))
            or value.endswith(
                (
                    ".py",
                    ".js",
                    ".ts",
                    ".tsx",
                    ".jsx",
                    ".go",
                    ".rs",
                    ".java",
                    ".rb",
                    ".md",
                    ".json",
                    ".toml",
                    ".yaml",
                    ".yml",
                )
            )
        )
        if not path_like:
            return match.group(0)
        return f"`{value}` *(unverified file reference)*"

    return _PATH.sub(replace, text)


def has_ai_meta_language(text: str) -> bool:
    """Detect model framing or conversational/meta language in artifacts."""
    lowered = text.lower()
    phrases = (
        # References to the user's request
        "the user requested",
        "the user wants",
        "the user asked",
        "the user would like",
        "the user is asking",
        "the user's request",
        "the user's prompt",
        "user request",
        "user prompt",
        # References to being instructed
        "i was asked",
        "i was instructed",
        "i was requested",
        "i was told to",
        "as requested",
        "as instructed",
        "per your request",
        "per the request",
        "at your request",
        # Request/prompt framing
        "based on the request",
        "based on your request",
        "based on the user's request",
        "based on your prompt",
        "based on the user's prompt",
        "according to the request",
        "according to your request",
        "the request is",
        "the prompt asks",
        "the prompt requested",
        "the prompt says",
        "the instructions say",
        "the instructions ask",
        "the instructions requested",
        # Conversational scaffolding that shouldn't appear in artifacts
        "hope this helps",
        "let me know if you'd like",
        "let me know if you want",
        "let me know if you need",
        "if you'd like, i can",
        "if you want, i can",
        "if you need, i can",
        "i'd be happy to",
        "i would be happy to",
    )
    return any(phrase in lowered for phrase in phrases)


def validate_commit_proposal(item: CommitProposal) -> str | None:
    if has_ai_meta_language(f"{item.message}\n{item.body}"):
        return (
            "Remove any meta-language about the user or request. "
            "Write only the commit message."
        )
    return None


def validate_issue_proposal(item: IssueProposal) -> str | None:
    if has_ai_meta_language(f"{item.title}\n{item.body}"):
        return (
            "Remove any meta-language about the user or request. "
            "Write only the issue itself."
        )
    return None


def validate_pull_request_proposal(item: PullRequestProposal) -> str | None:
    if has_ai_meta_language(f"{item.title}\n{item.body}"):
        return (
            "Remove any meta-language about the user or request. "
            "Write only the pull request itself."
        )
    return None
