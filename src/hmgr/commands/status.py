from ..integrations.git import Git
from ..integrations.github import GitHub
from ..services.status import (
    RepositoryStatusService,
)
from ..ui.console import print_status


def run() -> None:
    service = RepositoryStatusService(
        git=Git(),
        github=GitHub(),
    )

    status = service.get_status()

    print_status(status)
