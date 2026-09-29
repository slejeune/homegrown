from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..artifacts import ArtifactKind

if TYPE_CHECKING:
    from ..integrations.github import GitHub


@dataclass(frozen=True)
class ContextFile:
    path: str
    content: str
    source_chars: int | None = None

    @property
    def included_chars(self) -> int:
        return len(self.content)

    @property
    def total_chars(self) -> int:
        return self.included_chars if self.source_chars is None else self.source_chars

    def render(self) -> str:
        return f"### {self.path}\n```text\n{self.content}\n```"


@dataclass(frozen=True)
class ContextEntry:
    path: str
    category: str
    reason: str
    priority: int
    included_chars: int | None = None
    total_chars: int | None = None


@dataclass(frozen=True)
class RenderSection:
    name: str
    content: str
    priority: int = 50
    truncatable: bool = False


@dataclass
class IssueContext:
    number: int
    title: str
    body: str
    state: str
    url: str
    labels: list[str]

    @classmethod
    def from_github(cls, github: GitHub, issue_number: int) -> "IssueContext":
        issue: dict[str, Any] = github.get_issue(issue_number)
        return cls(
            number=int(issue["number"]),
            title=str(issue.get("title", "")),
            body=str(issue.get("body", "")),
            state=str(issue.get("state", "")),
            url=str(issue.get("url", "")),
            labels=[
                str(label.get("name", ""))
                for label in issue.get("labels", [])
                if label.get("name")
            ],
        )

    def as_text(self) -> str:
        labels = ", ".join(self.labels)
        return (
            f"GitHub Issue #{self.number}\n"
            f"Title: {self.title}\n"
            f"State: {self.state}\n"
            f"URL: {self.url}\n"
            f"Labels: {labels or 'none'}\n\n"
            f"Description:\n{self.body or '(no description)'}"
        )


@dataclass
class Context:
    purpose: ArtifactKind | None
    name: str
    url: str
    description: str
    branch: str
    base_branch: str | None = None
    issue: IssueContext | None = None
    tracked_files: list[str] = field(default_factory=list)
    staged_files: list[str] = field(default_factory=list)
    staged_diff: str = ""
    changed_files: list[str] = field(default_factory=list)
    diff: str = ""
    commits: str = ""
    changed_file_contents: list[ContextFile] = field(default_factory=list)
    related_files: list[ContextFile] = field(default_factory=list)
    relevant_files: list[ContextFile] = field(default_factory=list)
    instructions: list[ContextFile] = field(default_factory=list)
    documentation: list[ContextFile] = field(default_factory=list)
    template: ContextFile | None = None

    def manifest(self, max_chars: int | None = None) -> list[ContextEntry]:
        from .manifest import build_manifest

        return build_manifest(self)

    def render_manifest(self, max_chars: int | None = None) -> str:
        from .rendering import render_manifest

        return render_manifest(self.manifest(max_chars=max_chars))

    def render_instructions(self) -> str:
        from .rendering import render_files

        return render_files(self.instructions)

    def render_template(self) -> str | None:
        return self.template.render() if self.template else None

    def render_evidence(
        self, max_chars: int | None = None, optional_max_chars: int | None = None
    ) -> str:
        from .rendering import render_evidence

        return render_evidence(
            self, max_chars=max_chars, optional_max_chars=optional_max_chars
        )

    def render(self, max_chars: int | None = None) -> str:
        from .rendering import render_context

        return render_context(self, max_chars=max_chars)

    def as_text(self) -> str:
        return self.render()
