from __future__ import annotations

from ..integrations.github import GitHub
from ..ui.console import info, success


def run(
    *,
    method: str = "merge",
    delete_branch: bool = True,
    pull_request_number: int | None = None,
) -> None:
    """Shortcut for ``gh pr merge``; it makes no merge decision."""
    args = ["pr", "merge"]
    if pull_request_number is not None:
        args.append(str(pull_request_number))
    args.extend([f"--{method}"])
    if delete_branch:
        args.append("--delete-branch")

    info("Running: gh " + " ".join(args))
    GitHub().run(*args)
    success("Pull request merged.")
