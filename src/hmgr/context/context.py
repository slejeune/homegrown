"""Repository context collection."""

from importlib.resources import files

from ..artifacts import ArtifactKind
from ..integrations.git import Git
from ..integrations.github import GitHub
from .models import Context, ContextFile, IssueContext
from .relevance import (
    deduplicate_files,
    find_related_files,
    find_relevant_files,
    is_allowed_path,
    query_terms,
    source_snippet,
)

IMPORTANT_DOCUMENTS = ["README.md", "README", "CONTRIBUTING.md"]
INSTRUCTION_FILES = ["AGENTS.md", "CLAUDE.md"]
TEMPLATE_FILES = {
    ArtifactKind.ISSUE: [".github/ISSUE_TEMPLATE.md"],
    ArtifactKind.COMMIT: [".github/COMMIT_TEMPLATE.md"],
    ArtifactKind.PULL_REQUEST: [".github/PULL_REQUEST_TEMPLATE.md"],
}
HMGR_RESOURCE_FILES = {
    ArtifactKind.ISSUE: "issue-template.md",
    ArtifactKind.COMMIT: "commit-template.md",
    ArtifactKind.PULL_REQUEST: "pr-template.md",
}


def build_context(
    *,
    purpose: ArtifactKind | None = None,
    github: GitHub | None = None,
    issue_number: int | None = None,
    base_branch: str | None = None,
    query: str | None = None,
    max_file_chars: int,
    relevant_file_limit: int = 20,
    max_related_files: int = 8,
    include_repository_map: bool = True,
    max_tracked_files: int = 500,
) -> Context:
    """Build all repository context through one standardized path.

    ``purpose`` controls the only template that can be included. Other artifact
    templates are never loaded into the context or considered relevant files.
    """
    git = Git()
    repo = github.repo() if github else {}
    branch = git.current_branch()
    tracked_files = (
        git.tracked_files()[:max_tracked_files] if include_repository_map else []
    )

    issue = None
    if issue_number is not None:
        if github is None:
            raise ValueError("github is required when issue_number is provided")
        issue = IssueContext.from_github(github, issue_number)

    if purpose == ArtifactKind.PULL_REQUEST and issue is None:
        detected_issue = git.issue_for_branch(branch) if branch else None
        if detected_issue is not None and github is not None:
            issue = IssueContext.from_github(github, detected_issue)

    task_query = query
    if purpose == ArtifactKind.ISSUE and issue:
        task_query = f"{issue.title}\n{issue.body}"
    elif purpose == ArtifactKind.PULL_REQUEST:
        task_query = "\n".join(
            [
                *(git.changed_files(base_branch or "") if base_branch else []),
                *([issue.title, issue.body] if issue else []),
            ]
        )

    instructions = collect_file_contents(git, INSTRUCTION_FILES, max_file_chars)
    if not instructions:
        fallback = load_hmgr_file("hmgr-instructions.md", max_file_chars)
        if fallback:
            instructions.append(fallback)

    documentation = collect_file_contents(git, IMPORTANT_DOCUMENTS, max_file_chars)

    template = None
    if purpose is not None:
        templates = collect_file_contents(git, TEMPLATE_FILES[purpose], max_file_chars)
        template = (
            templates[0]
            if templates
            else load_hmgr_file(HMGR_RESOURCE_FILES[purpose], max_file_chars)
        )

    excluded_paths = {
        path for paths in TEMPLATE_FILES.values() for path in paths
    } | set(IMPORTANT_DOCUMENTS)
    relevant_paths = []
    if task_query:
        relevant_paths = [
            path
            for path in find_relevant_files(
                git,
                query=task_query,
                tracked_files=tracked_files or git.tracked_files(),
                limit=relevant_file_limit,
            )
            if path not in excluded_paths
        ]

    context = Context(
        purpose=purpose,
        name=str(repo.get("nameWithOwner", "")),
        url=str(repo.get("url", "")),
        description=str(repo.get("description", "")),
        branch=branch,
        base_branch=base_branch,
        issue=issue,
        tracked_files=tracked_files,
        instructions=deduplicate_files(instructions),
        documentation=deduplicate_files(documentation),
        template=template,
        relevant_files=collect_file_contents(
            git,
            relevant_paths,
            max_file_chars,
            query=task_query,
            snippet=True,
        ),
    )

    if purpose == ArtifactKind.COMMIT:
        context.staged_files = git.staged_files()
        context.staged_diff = git.staged_diff()
    elif purpose == ArtifactKind.PULL_REQUEST:
        if not base_branch:
            raise ValueError("base_branch is required for pull request context")
        context.changed_files = git.changed_files(base_branch)
        context.diff = git.diff(base_branch)
        context.commits = git.commits(base_branch)
        for path in context.changed_files:
            if not path or not is_allowed_path(path):
                continue
            diff = git.diff_file(base_branch, path, context_lines=20)
            if diff:
                context.changed_file_contents.append(
                    ContextFile(
                        path=path, content=diff[:max_file_chars], source_chars=len(diff)
                    )
                )
        related_paths = find_related_files(
            git,
            changed_files=context.changed_files,
            issue=issue,
            max_files=max_related_files,
        )
        related_query = "\n".join(
            [*context.changed_files, *([issue.title, issue.body] if issue else [])]
        )
        for path in related_paths:
            content = git.file_content(path)
            if content:
                context.related_files.append(
                    ContextFile(
                        path=path,
                        content=source_snippet(
                            content,
                            terms=query_terms(related_query),
                            max_chars=max_file_chars,
                        ),
                    )
                )

    return context


def load_hmgr_file(name: str, max_file_chars: int) -> ContextFile | None:
    resource = files("hmgr") / "templates" / name
    try:
        content = resource.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    if not content:
        return None
    return ContextFile(
        path=f"hmgr://templates/{name}",
        content=content[:max_file_chars],
        source_chars=len(content),
    )


def collect_file_contents(
    git,
    paths: list[str],
    max_file_chars: int,
    *,
    query: str | None = None,
    snippet: bool = False,
) -> list[ContextFile]:
    result = []
    for path in paths:
        if not is_allowed_path(path):
            continue
        content = git.file_content(path)
        if content:
            source_chars = len(content)
            if snippet:
                content = source_snippet(
                    content,
                    terms=query_terms(query or ""),
                    max_chars=max_file_chars,
                )
                if not content:
                    continue
            else:
                content = content[:max_file_chars]
            result.append(
                ContextFile(path=path, content=content, source_chars=source_chars)
            )
    return deduplicate_files(result)
