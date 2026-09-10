from ..context import Context
from ..artifacts import ArtifactKind
from ._common import build_artifact_prompt
from .models import ArtifactSpec


ISSUE_SPEC = ArtifactSpec(
    kind=ArtifactKind.ISSUE,
    task=(
        "Create a GitHub issue that another developer can act on without having "
        "to rediscover the intent."
    ),
    instructions="""
Follow the supplied issue template as the authoritative structure when present.
Omit sections that cannot be supported by the available evidence. Acceptance
criteria must be short and verifiable. Preserve ambiguity when the request is
ambiguous. Use repository instructions and documentation as the source of
implementation guidance; source code may establish current behavior but does not
by itself prescribe a change. Use file references only when the exact path appears
in the evidence. Do not repeat the user request verbatim.
""".strip(),
    output_requirements="Return only JSON matching the requested output schema.",
)


def build_issue_prompt(
    description: str,
    context: Context,
    max_chars: int | None = None,
    feedback: str | None = None,
) -> str:
    return build_artifact_prompt(
        ISSUE_SPEC,
        user_request=description,
        repository_instructions=context.render_instructions(),
        template=context.render_template(),
        repository_evidence=context.render_evidence(max_chars=max_chars),
        feedback=feedback,
    )
