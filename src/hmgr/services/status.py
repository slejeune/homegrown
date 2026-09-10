from ..integrations.git import Git
from ..integrations.github import GitHub
from ..models import RepositoryStatus


class RepositoryStatusService:
    def __init__(
        self,
        git: Git,
        github: GitHub,
    ) -> None:
        self.git = git
        self.github = github

    def get_status(self) -> RepositoryStatus:
        repo = self.github.repo()

        branch = self.git.current_branch()

        issue_number = self.git.issue_for_branch(branch)

        issue_title = None

        if issue_number:
            issue = self.github.get_issue(issue_number)
            issue_title = issue.get("title")

        prs = self.github.pull_requests_for_branch(branch)

        pr = prs[0] if prs else None

        return RepositoryStatus(
            repository=str(
                repo.get(
                    "nameWithOwner",
                    "",
                )
            ),
            branch=branch,
            issue_number=issue_number,
            issue_title=issue_title,
            pull_request_number=(int(pr["number"]) if pr else None),
            pull_request_title=(str(pr["title"]) if pr else None),
            pull_request_state=(str(pr["state"]) if pr else None),
            pull_request_url=(str(pr["url"]) if pr else None),
            working_tree=(self.git.status()),
        )
