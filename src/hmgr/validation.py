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
    return any(phrase in lowered for phrase in _META_PHRASES)


def _meta_language_error(fields: list[tuple[str, str]]) -> str | None:
    for name, value in fields:
        lowered = value.lower()
        for phrase in _META_PHRASES:
            if phrase in lowered:
                return (
                    f"The {name} field contains meta-language ('{phrase}'). "
                    "Rewrite that field as artifact content, without referring to "
                    "the request, instructions, or assistant."
                )
    return None


_META_PHRASES = (
    "the user requested", "the user wants", "the user asked",
    "the user would like", "the user is asking", "the user's request",
    "the user's prompt", "user request", "user prompt", "i was asked",
    "i was instructed", "i was requested", "i was told to", "as requested",
    "as instructed", "per your request", "per the request", "at your request",
    "based on the request", "based on your request", "based on the user's request",
    "based on your prompt", "based on the user's prompt", "according to the request",
    "according to your request", "the request is", "the prompt asks",
    "the prompt requested", "the prompt says", "the instructions say",
    "the instructions ask", "the instructions requested", "hope this helps",
    "let me know if you'd like", "let me know if you want", "let me know if you need",
    "if you'd like, i can", "if you want, i can", "if you need, i can",
    "i'd be happy to", "i would be happy to",
)


def remove_meta_language(item: CommitProposal | IssueProposal | PullRequestProposal) -> list[str]:
    """Drop sentences that only frame content as a response to instructions."""
    field_names = {
        CommitProposal: ("subject", "body"),
        IssueProposal: ("title", "problem", "expected_outcome", "acceptance_criteria", "implementation_notes"),
        PullRequestProposal: ("title", "summary", "changes", "testing", "related_issue"),
    }[type(item)]
    cleaned_fields = []
    for name in field_names:
        value = getattr(item, name)
        lines = []
        for line in value.splitlines():
            # Keep bullets and paragraph boundaries, but remove a complete
            # sentence that refers to the prompt, user, or assistant.
            sentences = re.split(r"(?<=[.!?])\s+", line)
            retained = [
                sentence for sentence in sentences
                if not any(phrase in sentence.lower() for phrase in _META_PHRASES)
            ]
            cleaned = " ".join(retained).strip()
            if cleaned:
                lines.append(cleaned)
        replacement = "\n".join(lines).strip()
        if replacement != value:
            setattr(item, name, replacement)
            cleaned_fields.append(name)
    return cleaned_fields


def _required_content_error(fields: list[tuple[str, str]]) -> str | None:
    missing = [name for name, value in fields if not value.strip()]
    if missing:
        joined = ", ".join(missing)
        return (
            f"Required template content is empty: {joined}. Fill those fields "
            "with concise, evidence-supported content. If a section has no "
            "applicable information, state that explicitly."
        )
    return None


def validate_commit_proposal(item: CommitProposal) -> str | None:
    return _required_content_error([("subject", item.subject)]) or _meta_language_error(
        [("subject", item.subject), ("body", item.body)]
    )


def validate_issue_proposal(item: IssueProposal) -> str | None:
    fields = [
        ("title", item.title), ("problem", item.problem),
        ("expected_outcome", item.expected_outcome),
        ("acceptance_criteria", item.acceptance_criteria),
    ]
    return _required_content_error(fields) or _meta_language_error(
        [*fields, ("implementation_notes", item.implementation_notes)]
    )


def validate_pull_request_proposal(item: PullRequestProposal) -> str | None:
    fields = [("title", item.title), ("summary", item.summary), ("changes", item.changes), ("testing", item.testing)]
    return _required_content_error(fields) or _meta_language_error(
        [*fields, ("related_issue", item.related_issue)]
    )
