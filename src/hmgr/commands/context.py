from ..config import Config
from ..context import build_context
from ..artifacts import ArtifactKind
from ..integrations.github import GitHub
from ..ui.console import print_context
from ..ui.context import print_context_manifest


def run(
    issue_number: int | None = None,
) -> None:
    config = Config.from_env()
    github = GitHub()

    if issue_number is not None:
        context = build_context(
            purpose=ArtifactKind.ISSUE,
            github=github,
            issue_number=issue_number,
            max_file_chars=config.max_file_chars,
        )

        print_context_manifest(context.manifest(), purpose="issue context")
        print_context(
            context.render(
                max_chars=config.max_context_chars,
            )
        )

        return

    context = build_context(
        purpose=ArtifactKind.PULL_REQUEST,
        github=github,
        base_branch=config.base_branch,
        max_file_chars=config.max_file_chars,
    )

    print_context_manifest(context.manifest(), purpose="pull request context")
    print_context(
        context.render(
            max_chars=config.max_context_chars,
        )
    )
