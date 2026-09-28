from ..config import Config
from ..context import build_context
from ..integrations.github import GitHub
from ..integrations.git import Git
from ..integrations.ollama import Ollama
from ..ui.console import heading


class Chat:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.github = GitHub()
        self.git = Git()
        self.ollama = Ollama(base_url=config.ollama_url)

    def run(self) -> None:
        heading('hmgr repository chat. Type "exit" to quit.')
        while True:
            try:
                question = input("> ").strip()
            except EOFError:
                break
            if question.lower() in {"exit", "quit"}:
                break
            if not question:
                continue

            context = build_context(
                github=self.github,
                max_file_chars=self.config.max_file_chars,
                query=question,
                relevant_file_limit=min(12, self.config.max_relevant_files),
            )
            prompt = (
                "Answer the user's question using only the repository evidence "
                "below. If the evidence is insufficient, you MUST say so. Do not "
                "invent files, APIs, behavior, or requirements.\n\n"
                f"Question: {question}\n\n"
                f"{context.render(max_chars=self.config.max_context_chars)}"
            )
            print(
                self.ollama.chat(
                    self.config.model,
                    [{"role": "user", "content": prompt}],
                    num_ctx=self.config.context_window_tokens,
                )
            )
