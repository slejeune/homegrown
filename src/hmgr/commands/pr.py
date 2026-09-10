from ..config import Config
from ..integrations.github import GitHub
from ..integrations.ollama import Ollama
from ..services.pull_request import PullRequestService
from ..services.ready import Ready
from ..integrations.git import Git
from ..ui.console import heading, readiness, success, warning


def run(
    config: Config,
    base_branch: str | None = None,
) -> None:

    service = PullRequestService(
        github=GitHub(),
        ollama=Ollama(
            base_url=config.ollama_url,
        ),
        config=config,
    )

    service.create_pull_request(
        base_branch=base_branch,
    )


def check(config: Config) -> None:
    result = Ready(
        Git(),
        GitHub(),
        config.base_branch,
    ).check()

    heading("PR readiness")
    for name, ok in result["checks"]:
        (success if ok else warning)(name)
    readiness(result["ready"])
