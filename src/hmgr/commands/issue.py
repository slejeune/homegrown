from ..config import Config
from ..integrations.github import GitHub
from ..integrations.ollama import Ollama
from ..services.issue import IssueService


def run(
    description: str,
    config: Config,
) -> None:

    service = IssueService(
        github=GitHub(),
        ollama=Ollama(
            base_url=config.ollama_url,
        ),
        config=config,
    )

    service.create_issue(description)
