from __future__ import annotations

import os
import re
import sys
from typing import TextIO

RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[94m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"


def _color_enabled(stream: TextIO) -> bool:
    """Return whether ANSI color should be emitted to *stream*."""
    if os.environ.get("NO_COLOR") is not None:
        return False

    force_color = os.environ.get("FORCE_COLOR")
    clicolor_force = os.environ.get("CLICOLOR_FORCE")
    if (force_color and force_color != "0") or (
        clicolor_force and clicolor_force != "0"
    ):
        return True

    if os.environ.get("CLICOLOR") == "0":
        return False
    if os.environ.get("TERM") == "dumb":
        return False

    return stream.isatty()


def _paint(text: str, code: str, *, stream: TextIO | None = None) -> str:
    output: TextIO = sys.stdout if stream is None else stream
    if not _color_enabled(output):
        return text
    return f"{code}{text}{RESET}"


def _label(label: str, value: str, code: str) -> str:
    return _paint(f"{label:<15}", BOLD) + _paint(value, code)


def info(message: str) -> None:
    print(_paint("[info] ", CYAN) + message)


def success(message: str) -> None:
    print(_paint("[ok]   ", GREEN) + message)


def warning(message: str) -> None:
    print(_paint("[warn] ", YELLOW) + message)


def error(message: str) -> None:
    print(_paint("[error]", RED, stream=sys.stderr) + " " + message, file=sys.stderr)


def heading(message: str) -> None:
    print(_paint(message, BOLD))


def context_manifest(manifest: str) -> None:
    """Print a context manifest with a stable table layout and color hierarchy."""
    lines = manifest.splitlines()
    if not lines:
        return

    print(_paint(lines[0], BOLD))
    if len(lines) < 3:
        for line in lines[1:]:
            print(line)
        return

    print(_colorize_manifest_header(lines[1]))
    for line in lines[2:]:
        print(_colorize_manifest_row(line))


def _colorize_manifest_header(line: str) -> str:
    if not _color_enabled(sys.stdout):
        return line
    return _paint(line, BOLD)


def _colorize_manifest_row(line: str) -> str:
    if not _color_enabled(sys.stdout):
        return line

    raw_cells = line.split(" | ")
    if len(raw_cells) != 7:
        return line

    cells = [cell.strip() for cell in raw_cells]
    path, category, priority, included, total, percentage, reason = cells
    styled = [
        _paint(path, BLUE),
        _paint(category, YELLOW),
        _paint(priority, BOLD),
        _paint(included, GREEN if included != "-" else DIM),
        _paint(total, DIM),
        _paint(
            percentage,
            GREEN if percentage == "100%" else YELLOW if percentage != "-" else DIM,
        ),
        _paint(reason, DIM),
    ]
    # Preserve the renderer's padding outside the ANSI sequences so the table
    # stays aligned after colorization.
    values = [
        styled[index] + raw_cells[index][len(cells[index]) :] for index in range(7)
    ]
    return " | ".join(values)


def _colorize_context_line(line: str) -> str:
    """Color presentation-only context output without changing its content."""
    if not _color_enabled(sys.stdout):
        return line

    if line.startswith("### "):
        return _paint("### ", BOLD) + _paint(line[4:], CYAN)
    if line in {"```text", "```"}:
        return _paint(line, DIM)
    if re.fullmatch(r"</?[^>]+>", line):
        return _paint(line, CYAN)
    if line.startswith("[truncated]"):
        return _paint(line, YELLOW)
    return line


def print_context(context: str) -> None:
    for line in context.splitlines():
        print(_colorize_context_line(line))


def print_issue_proposal(proposal) -> None:
    heading("\nISSUE PROPOSAL")
    print(_paint("=" * 60, DIM))
    print(_paint("Title:", BOLD), proposal.title)
    print(f"\n{proposal.body}\n")
    print(_paint("=" * 60, DIM))


def print_pr_proposal(proposal) -> None:
    heading("\nPULL REQUEST PROPOSAL")
    print(_paint("=" * 60, DIM))
    print(_paint("Title:", BOLD), proposal.title)
    print(f"\n{proposal.body}\n")
    print(_paint("=" * 60, DIM))


def print_commit_proposal(proposal) -> None:
    heading("\nCOMMIT PROPOSAL")
    print(_paint("=" * 60, DIM))
    print(f"\n{proposal.subject}")
    if proposal.body:
        print(f"\n{proposal.body}")
    print(_paint("\n" + "=" * 60, DIM))


def print_status(status) -> None:
    heading("\nHMGR STATUS")
    print(_paint("=" * 60, DIM))
    print(_label("Repository:", status.repository, CYAN))
    print(_label("Branch:", status.branch, CYAN))
    if status.issue_number:
        print(
            _label("Issue:", f"#{status.issue_number} {status.issue_title or ''}", CYAN)
        )
    else:
        print(_label("Issue:", "none", DIM))
    if status.pull_request_number:
        print(
            _label(
                "PR:",
                f"#{status.pull_request_number} {status.pull_request_state}",
                CYAN,
            )
        )
        if status.pull_request_title:
            print("              " + status.pull_request_title)
        if status.pull_request_url:
            print("              " + _paint(status.pull_request_url, DIM))
    else:
        print(_label("PR:", "none", DIM))
    working_tree = "changes present" if status.working_tree else "clean"
    tree_code = YELLOW if status.working_tree else GREEN
    print(_label("Working tree:", working_tree, tree_code))


def readiness(ready: bool) -> None:
    print(
        _paint("Readiness:", BOLD),
        _paint("READY" if ready else "NOT READY", GREEN if ready else RED),
    )


def link(url: str) -> None:
    print(_paint(url, CYAN))
