from ..config import Config
from ..integrations.git import Git
from ..integrations.github import GitHub
from ..services.develop import DevelopService


def run(config: Config, issue_number: int, branch_name: str | None = None) -> None:
    DevelopService(GitHub(), Git(), config).start_issue(issue_number, branch_name)
