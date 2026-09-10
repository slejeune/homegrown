from ..config import Config
from ..integrations.git import Git
from ..integrations.github import GitHub
from ..ui.console import info, success
from ..utils import slugify


class DevelopService:
    def __init__(
        self,
        github: GitHub,
        git: Git,
        config: Config,
    ) -> None:
        self.github = github
        self.git = git
        self.config = config

    def start_issue(
        self,
        issue_number: int,
        branch_name: str | None = None,
    ) -> str:
        issue = self.github.get_issue(issue_number)

        if branch_name is None:
            title_slug = slugify(
                issue.get(
                    "title",
                    "issue",
                )
            )

            branch_name = f"{issue_number}-{title_slug}"

        info(f"Creating development branch '{branch_name}'...")

        self.github.develop_issue(
            issue_number=issue_number,
            branch_name=branch_name,
            checkout=True,
        )

        self.git.save_issue_mapping(
            branch_name=branch_name,
            issue_number=issue_number,
        )

        success(f"Now working on issue #{issue_number}.")

        info(f"Branch: {branch_name}")

        return branch_name
