from dataclasses import dataclass
from typing import Any


@dataclass
class IssueProposal:
    title: str
    body: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IssueProposal":
        return cls(
            title=str(data.get("title", "")).strip(),
            body=str(data.get("body", "")).strip(),
        )

    @staticmethod
    def schema() -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"title": {"type": "string"}, "body": {"type": "string"}},
            "required": ["title", "body"],
            "additionalProperties": False,
        }


@dataclass
class CommitProposal:
    message: str
    body: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommitProposal":
        return cls(
            message=str(data.get("message", "")).strip(),
            body=str(data.get("body", "")).strip(),
        )

    @staticmethod
    def schema() -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"message": {"type": "string"}, "body": {"type": "string"}},
            "required": ["message", "body"],
            "additionalProperties": False,
        }


@dataclass
class PullRequestProposal:
    title: str
    body: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PullRequestProposal":
        return cls(
            title=str(data.get("title", "")).strip(),
            body=str(data.get("body", "")).strip(),
        )

    @staticmethod
    def schema() -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"title": {"type": "string"}, "body": {"type": "string"}},
            "required": ["title", "body"],
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
