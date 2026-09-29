from ..context import Context
from ..artifacts import ArtifactKind
from ._common import build_artifact_prompt
from .models import ArtifactSpec


ISSUE_SPEC = ArtifactSpec(
    kind=ArtifactKind.ISSUE,
    task=(
        "Turn the user's request into a useful GitHub issue using the supplied "
        "issue template."
    ),
    instructions="""
The bundled issue template is authoritative. Return one JSON string for each
template section: problem, expected_outcome, acceptance_criteria, and
implementation_notes. Also return title for the GitHub issue title. Do not
replace, omit, or add template sections.

Treat the user's request as the source of the requested intent and requirements.

Use only information that is explicitly stated in the user request or directly
supported by repository evidence.

Do not:
- invent a current problem, motivation, requirement, or acceptance criterion;
- assume that a requested change describes an existing bug;
- turn a desired outcome into a claim about the current state;
- invent implementation details;
- repeat the user request verbatim.

Do:
- preserve the actual intent and requirements of the user request;
- rewrite and condense the request where appropriate;
- use repository evidence to clarify concrete paths, names, and existing behavior;
- place information into the matching bundled template sections;
- preserve the template's headings, ordering, formatting, and conventions;
- omit unsupported information rather than guessing;
- preserve ambiguity when the request is genuinely ambiguous.

Acceptance criteria should only be included when they are supported by the user
request or repository evidence.

Return the issue content in the bundled template's section order.
""".strip(),
    output_requirements=(
        "Return only JSON with string fields title, problem, expected_outcome, "
        "acceptance_criteria, and implementation_notes. Put each section's "
        "content in its matching field; do not return markdown headings."
    ),
)


def build_issue_prompt(
    description: str,
    context: Context,
    max_chars: int | None = None,
    max_optional_context_chars: int | None = None,
    feedback: str | None = None,
) -> str:
    repository_instructions = context.render_instructions()
    template = context.render_template()
    fixed_prompt = build_artifact_prompt(
        ISSUE_SPEC,
        user_request=description,
        repository_instructions=repository_instructions,
        template=template,
        feedback=feedback,
    )
    evidence_budget = max_chars
    if evidence_budget is not None:
        evidence_budget -= len(fixed_prompt) + len("\n\n## Repository evidence\n\n")
        if max_optional_context_chars is not None:
            evidence_budget = min(evidence_budget, max_optional_context_chars)
        evidence_budget = max(0, evidence_budget)

    return build_artifact_prompt(
        ISSUE_SPEC,
        user_request=description,
        repository_instructions=repository_instructions,
        template=template,
        repository_evidence=context.render_evidence(max_chars=evidence_budget),
        feedback=feedback,
    )
