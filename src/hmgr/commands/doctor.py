from __future__ import annotations

import shutil

from hmgr.config import Config
from hmgr.integrations.github import GitHub
from hmgr.integrations.ollama import Ollama, OllamaError
from hmgr.ui.console import error, heading, success


def _check(name: str, ok: bool, detail: str = "") -> bool:
    if ok:
        message = f"{name}: OK"
    else:
        message = f"{name}: FAILED"

    if detail:
        message += f" - {detail}"

    (success if ok else error)(message)
    return ok


def run(config: Config) -> int:
    """Run environment diagnostics."""

    print()
    heading("hmgr environment")
    print()

    all_ok = True

    # Git
    git_available = shutil.which("git") is not None
    all_ok &= _check(
        "Git", git_available, "git executable not found" if not git_available else ""
    )

    # GitHub CLI
    gh_available = shutil.which("gh") is not None
    all_ok &= _check(
        "GitHub CLI",
        gh_available,
        "gh executable not found" if not gh_available else "",
    )

    # GitHub authentication
    if gh_available:
        github = GitHub()
        try:
            github.check_auth()
            auth_ok = True
            auth_detail = ""
        except Exception as exc:
            auth_ok = False
            auth_detail = str(exc)

        all_ok &= _check(
            "GitHub authentication",
            auth_ok,
            auth_detail,
        )
    else:
        all_ok &= _check(
            "GitHub authentication",
            False,
            "GitHub CLI is not installed",
        )

    # Ollama
    ollama = Ollama(config.ollama_url)

    try:
        ollama.list_models()
        ollama_ok = True
        ollama_detail = ""
    except OllamaError as exc:
        ollama_ok = False
        ollama_detail = str(exc)

    all_ok &= _check(
        "Ollama",
        ollama_ok,
        ollama_detail,
    )

    # Ollama model
    if ollama_ok:
        try:
            model_ok = ollama.model_installed(config.model)

            all_ok &= _check(
                f"Ollama model '{config.model}'",
                model_ok,
                (f"Model '{config.model}' is not installed." if not model_ok else ""),
            )
        except OllamaError as exc:
            all_ok &= _check(
                f"Ollama model '{config.model}'",
                False,
                str(exc),
            )
    else:
        all_ok &= _check(
            f"Ollama model '{config.model}'",
            False,
            "Ollama is unavailable",
        )

    print()

    if all_ok:
        success("All checks passed.")
        return 0

    error("One or more checks failed.")
    return 1
