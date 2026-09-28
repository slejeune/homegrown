from datetime import date

from ..config import Config
from ..context import build_context
from ..integrations.github import GitHub
from ..integrations.ollama import Ollama
from ..models import IssueProposal
from ..artifacts import ArtifactKind
from ..prompts.issue import build_issue_prompt
from ..ui.context import print_context_manifest
from ..validation import mark_unverified_file_references, validate_issue_proposal
from ..ui.review import review_proposal
from ..ui.console import (
    info,
    print_issue_proposal,
    success,
)


class IssueService:
    def __init__(
        self,
        github: GitHub,
        ollama: Ollama,
        config: Config,
    ) -> None:
        self.github = github
        self.ollama = ollama
        self.config = config

    def create_issue(
        self,
        description: str,
    ) -> int | None:
        info("Gathering repository context...")

        context = build_context(
            purpose=ArtifactKind.ISSUE,
            github=self.github,
            query=description,
            max_file_chars=self.config.max_file_chars,
            relevant_file_limit=self.config.max_relevant_files,
        )
        print_context_manifest(context.manifest(), purpose="issue generation")

        def generate(feedback: str | None) -> IssueProposal:
            info(f"Asking Ollama ({self.config.model})...")
            prompt = build_issue_prompt(
                description=description,
                context=context,
                max_chars=self.config.max_context_chars,
                max_optional_context_chars=self.config.max_optional_context_chars,
                feedback=feedback,
            )
            proposal_data = self.ollama.chat_json(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                schema=IssueProposal.schema(),
                num_ctx=self.config.context_window_tokens,
            )
            proposal = IssueProposal.from_dict(proposal_data)
            proposal.body = mark_unverified_file_references(
                proposal.body, set(context.tracked_files)
            )
            return proposal

        proposal = review_proposal(
            generate,
            print_issue_proposal,
            validate=validate_issue_proposal,
        )
        if proposal is None:
            info("Issue creation cancelled.")
            return None

        issue_number = self.github.create_issue(
            title=proposal.title,
            body=proposal.body,
            labels=[
                (
                    f"{date.today().isocalendar().year}"
                    f"-week-"
                    f"{date.today().isocalendar().week}"
                )
            ],
        )

        success(f"Created issue #{issue_number}.")

        return issue_number
