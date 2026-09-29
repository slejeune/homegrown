from ..config import Config
from ..context import build_context
from ..integrations.github import GitHub
from ..integrations.git import Git
from ..integrations.ollama import Ollama
from ..models import PullRequestProposal
from ..artifacts import ArtifactKind
from ..prompts.pull_request import (
    build_pull_request_prompt,
)
from ..ui.context import print_context_manifest
from ..validation import mark_unverified_file_references, remove_meta_language, validate_pull_request_proposal
from ..ui.review import review_proposal
from ..ui.console import (
    info,
    link,
    print_pr_proposal,
    success,
)


class PullRequestService:
    def __init__(
        self,
        github: GitHub,
        ollama: Ollama,
        config: Config,
        git: Git | None = None,
    ) -> None:
        self.github = github
        self.ollama = ollama
        self.config = config
        self.git = git or Git()

    def create_pull_request(
        self,
        base_branch: str | None = None,
    ) -> str | None:
        base = base_branch or self.config.base_branch

        info("Gathering pull request context...")

        context = build_context(
            purpose=ArtifactKind.PULL_REQUEST,
            github=self.github,
            base_branch=base,
            max_file_chars=self.config.max_file_chars,
            relevant_file_limit=self.config.max_relevant_files,
        )
        print_context_manifest(context.manifest(), purpose="pull request generation")

        def generate(feedback: str | None) -> PullRequestProposal:
            info(f"Asking Ollama ({self.config.model})...")
            prompt = build_pull_request_prompt(
                context=context,
                max_chars=self.config.max_context_chars,
                optional_context_chars=self.config.max_optional_context_chars,
                feedback=feedback,
            )
            proposal_data = self.ollama.chat_json(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                schema=PullRequestProposal.schema(),
                num_ctx=self.config.context_window_tokens,
            )
            proposal = PullRequestProposal.from_dict(proposal_data)
            proposal.changes = mark_unverified_file_references(
                proposal.changes,
                set(context.changed_files)
                | {file.path for file in context.related_files},
            )
            if context.issue:
                closing_text = f"Fixes #{context.issue.number}"
                if closing_text.lower() not in proposal.related_issue.lower():
                    proposal.related_issue = "\n".join(
                        part for part in (proposal.related_issue, closing_text) if part
                    )
            return proposal

        proposal = review_proposal(
            generate,
            print_pr_proposal,
            validate=validate_pull_request_proposal,
            normalize=remove_meta_language,
        )
        if proposal is None:
            info("Pull request creation cancelled.")
            return None

        info("Pushing current branch before creating pull request...")
        self.git.run("push", "--set-upstream", "origin", "HEAD")

        url = self.github.create_pr(
            title=proposal.title,
            body=proposal.body,
            base=base,
        )

        success("Pull request created.")

        link(url)

        return url
