from dataclasses import dataclass
from typing import Any


@dataclass
class IssueProposal:
    title: str
    problem: str
    expected_outcome: str
    acceptance_criteria: str
    implementation_notes: str

    @property
    def body(self) -> str:
        return _render_sections((
            ("Problem", self.problem),
            ("Expected outcome", self.expected_outcome),
            ("Acceptance criteria", self.acceptance_criteria),
            ("Implementation notes", self.implementation_notes),
        ))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IssueProposal":
        return cls(
            title=str(data.get("title", "")).strip(),
            problem=str(data.get("problem", "")).strip(),
            expected_outcome=str(data.get("expected_outcome", "")).strip(),
            acceptance_criteria=str(data.get("acceptance_criteria", "")).strip(),
            implementation_notes=str(data.get("implementation_notes", "")).strip(),
        )

    @staticmethod
    def schema() -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {key: {"type": "string"} for key in (
                "title", "problem", "expected_outcome", "acceptance_criteria", "implementation_notes"
            )},
            "required": ["title", "problem", "expected_outcome", "acceptance_criteria", "implementation_notes"],
            "additionalProperties": False,
        }


@dataclass
class CommitProposal:
    subject: str
    body: str

    @property
    def message(self) -> str:
        return self.subject

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommitProposal":
        return cls(
            subject=str(data.get("subject", "")).strip(),
            body=str(data.get("body", "")).strip(),
        )

    @staticmethod
    def schema() -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"subject": {"type": "string"}, "body": {"type": "string"}},
            "required": ["subject", "body"],
            "additionalProperties": False,
        }


@dataclass
class PullRequestProposal:
    title: str
    summary: str
    changes: str
    testing: str
    related_issue: str

    @property
    def body(self) -> str:
        return _render_sections((
            ("Summary", self.summary),
            ("Changes", self.changes),
            ("Testing", self.testing),
            ("Related issue", self.related_issue),
        ))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PullRequestProposal":
        return cls(
            title=str(data.get("title", "")).strip(),
            summary=str(data.get("summary", "")).strip(),
            changes=str(data.get("changes", "")).strip(),
            testing=str(data.get("testing", "")).strip(),
            related_issue=str(data.get("related_issue", "")).strip(),
        )

    @staticmethod
    def schema() -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {key: {"type": "string"} for key in (
                "title", "summary", "changes", "testing", "related_issue"
            )},
            "required": ["title", "summary", "changes", "testing", "related_issue"],
            "additionalProperties": False,
        }


@dataclass
class RepositoryStatus:
    repository: str
    branch: str
    issue_number: int | None
    issue_title: str | None
    pull_request_number: int | None
    pull_request_title: str | None
    pull_request_state: str | None
    pull_request_url: str | None
    working_tree: str


def _render_sections(sections: tuple[tuple[str, str], ...]) -> str:
    return "\n\n".join(f"## {heading}\n\n{value}" for heading, value in sections)
