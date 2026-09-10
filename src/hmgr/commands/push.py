from __future__ import annotations

from ..integrations.git import Git
from ..ui.console import info, success


def run() -> None:
    """Shortcut for ``git push -u origin HEAD``; no AI or decision-making."""
    args = ["push", "--set-upstream", "origin", "HEAD"]
    info("Running: git " + " ".join(args))
    Git().run(*args)
    success("Current branch pushed to origin.")
