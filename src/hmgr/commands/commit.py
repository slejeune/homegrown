from ..config import Config
from ..integrations.git import Git
from ..integrations.ollama import Ollama
from ..services.commit import CommitService


def run(
    config: Config,
) -> None:
    service = CommitService(
        git=Git(),
        ollama=Ollama(
            base_url=config.ollama_url,
        ),
        config=config,
    )

    service.run()
