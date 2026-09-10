from ..context import Context
from ..artifacts import ArtifactKind
from ._common import build_artifact_prompt
from .models import ArtifactSpec


PULL_REQUEST_SPEC = ArtifactSpec(
    kind=ArtifactKind.PULL_REQUEST,
    task=(
        "Prepare a pull request that gives a maintainer a clear, actionable "
        "review of the current branch."
    ),
    instructions="""
The diff is authoritative for what changed. Follow the supplied pull request
template as the authoritative structure when present. Report testing only when
the evidence explicitly shows it was performed. Call out risks, limitations, or
follow-up work only when supported by evidence. Never claim that an issue was
resolved or that a design decision was intentional unless supported by evidence.
Use exact file paths only when they appear in the evidence.
        """.strip(),
    output_requirements="Return only JSON matching the requested output schema.",
)


def build_pull_request_prompt(
    context: Context,
    max_chars: int | None = None,
    feedback: str | None = None,
) -> str:
    return build_artifact_prompt(
        PULL_REQUEST_SPEC,
        repository_instructions=context.render_instructions(),
        template=context.render_template(),
        repository_evidence=context.render_evidence(max_chars=max_chars),
        feedback=feedback,
    )
