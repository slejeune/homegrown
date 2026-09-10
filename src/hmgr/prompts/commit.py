from ..context.models import ContextFile
from ..artifacts import ArtifactKind
from ._common import build_artifact_prompt
from .models import ArtifactSpec


COMMIT_SPEC = ArtifactSpec(
    kind=ArtifactKind.COMMIT,
    task="Write a useful Git commit message for the staged changes.",
    instructions="""
Describe what the staged changes actually do, not what the author may have
intended. Follow the supplied commit template when present. Do not invent
motivation, issue references, tests, or behavior. Avoid vague commit messages.
""".strip(),
    output_requirements="Return only JSON matching the requested output schema.",
)


def build_commit_prompt(
    diff: str,
    files: list[str],
    repository_instructions: list[ContextFile] | None = None,
    template: ContextFile | None = None,
    feedback: str | None = None,
) -> str:
    evidence = "\n\n".join(
        [
            "### Staged files\n"
            + ("\n".join(f"- {path}" for path in files) or "(none)"),
            f"### Staged diff\n```diff\n{diff}\n```",
        ]
    )
    return build_artifact_prompt(
        COMMIT_SPEC,
        repository_instructions=_render_files(repository_instructions or []),
        template=template.content if template else None,
        repository_evidence=evidence,
        feedback=feedback,
    )


def _render_files(files: list[ContextFile]) -> str:
    return "\n\n".join(file.render() for file in files)
