from ..config import Config
from ..context import Context, build_context
from ..integrations.git import Git
from ..integrations.ollama import Ollama
from ..models import CommitProposal
from ..artifacts import ArtifactKind
from ..prompts.commit import build_commit_prompt
from ..ui.console import info, print_commit_proposal, success
from ..ui.context import print_context_manifest
from ..ui.review import review_proposal
from ..validation import remove_meta_language, validate_commit_proposal


class CommitService:
    def __init__(self, git: Git, ollama: Ollama, config: Config) -> None:
        self.git = git
        self.ollama = ollama
        self.config = config

    def suggest(
        self,
        feedback: str | None = None,
    ) -> CommitProposal:
        context = self._build_context()
        print_context_manifest(context.manifest(), purpose="commit message generation")
        return self._suggest(context, feedback)

    def _build_context(self) -> Context:
        files = self.git.staged_files()
        if not files:
            raise RuntimeError("There are no staged files.")

        diff = self.git.staged_diff()
        if not diff:
            raise RuntimeError("The staged diff is empty.")

        return build_context(
            purpose=ArtifactKind.COMMIT,
            max_file_chars=self.config.max_file_chars,
            include_repository_map=False,
        )

    def _suggest(
        self,
        context: Context,
        feedback: str | None = None,
    ) -> CommitProposal:
        diff = context.staged_diff[: self.config.max_context_chars]
        if len(context.staged_diff) > len(diff):
            diff += "\n[truncated]"
        prompt = build_commit_prompt(
            diff=diff,
            files=context.staged_files,
            repository_instructions=context.instructions,
            template=context.template,
            feedback=feedback,
        )
        info(f"Asking Ollama ({self.config.model})...")
        data = self.ollama.chat_json(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            schema=CommitProposal.schema(),
            num_ctx=self.config.context_window_tokens,
        )
        return CommitProposal.from_dict(data)

    def run(self) -> CommitProposal:
        context = self._build_context()
        print_context_manifest(context.manifest(), purpose="commit message generation")

        def generate(feedback: str | None) -> CommitProposal:
            return self._suggest(context, feedback)

        proposal = review_proposal(
            generate,
            print_commit_proposal,
            validate=validate_commit_proposal,
            normalize=remove_meta_language,
        )
        if proposal is None:
            info("Commit creation cancelled.")
            return CommitProposal("", "")

        self.git.commit(message=proposal.message, body=proposal.body)
        success("Commit created.")
        return proposal
