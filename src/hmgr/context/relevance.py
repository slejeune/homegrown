from pathlib import Path
import re

from .models import ContextFile


SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".rb",
    ".php",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".sql",
    ".sh",
    ".bash",
}


STOP_WORDS = {
    "add",
    "change",
    "create",
    "make",
    "update",
    "implement",
    "support",
    "remove",
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "this",
    "that",
    "should",
    "would",
    "could",
    "please",
    "want",
    "need",
    "issue",
    "feature",
    "request",
}


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    "dist",
    "build",
    "coverage",
}


IGNORED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}


IGNORED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".mp4",
    ".mov",
    ".avi",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".lock",
    ".pyc",
}


def find_relevant_files(
    git,
    *,
    query: str,
    tracked_files: list[str],
    limit: int = 12,
) -> list[str]:
    """Rank files using both paths and their contents.

    Path names are useful hints, but content is authoritative enough to find
    files whose names do not describe the requested behaviour.
    """
    terms = query_terms(query)
    if not terms:
        return []

    candidates = [path for path in tracked_files if is_allowed_path(path)]
    scored: list[tuple[int, str]] = []
    for path in candidates:
        content = git.file_content(path)
        score = path_score(path, terms) + content_score(content, terms)
        if score > 0:
            scored.append((score, path))

    scored.sort(key=lambda item: (-item[0], item[1].lower()))
    return [path for _, path in scored[:limit]]


def find_related_files(
    git,
    *,
    changed_files: list[str],
    issue,
    max_files: int = 8,
) -> list[str]:
    changed_set = set(changed_files)
    query = "\n".join([*(changed_files), *([issue.title, issue.body] if issue else [])])
    terms = query_terms(query)

    scored: list[tuple[int, str]] = []
    for path in git.tracked_files():
        if (
            path in changed_set
            or not is_allowed_path(path)
            or not looks_like_source_file(path)
        ):
            continue
        content = git.file_content(path)
        score = path_score(path, terms) + content_score(content, terms)
        if looks_like_test_file(path) and score:
            score += 1
        if score:
            scored.append((score, path))

    scored.sort(key=lambda item: (-item[0], item[1].lower()))
    return [path for _, path in scored[:max_files]]


def query_terms(query: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9_/-]+", query.lower())
    return {word for word in words if len(word) >= 3 and word not in STOP_WORDS}


def path_score(path: str, terms: set[str]) -> int:
    normalized = path.lower()
    name = Path(path).name.lower()
    stem = Path(path).stem.lower()
    score = 0

    for term in terms:
        if term in normalized:
            score += 3
        if term in name:
            score += 5
        if term in stem:
            score += 6

    if looks_like_source_file(path):
        score += 2
    return score


def content_score(content: str, terms: set[str]) -> int:
    if not content:
        return 0

    normalized = content.lower()
    score = 0
    for term in terms:
        occurrences = normalized.count(term)
        if occurrences:
            score += min(occurrences, 5) * 2
    return score


def matching_line_numbers(content: str, terms: set[str]) -> list[int]:
    if not content or not terms:
        return []
    lines = content.splitlines()
    return [
        index
        for index, line in enumerate(lines)
        if any(term in line.lower() for term in terms)
    ]


def source_snippet(
    content: str,
    *,
    terms: set[str] | None = None,
    max_chars: int = 12_000,
    context_lines: int = 10,
) -> str:
    """Return focused source around matching lines, never an arbitrary prefix."""
    terms = terms or set()
    lines = content.splitlines()
    matches = matching_line_numbers(content, terms)

    if not matches:
        return ""

    windows: list[tuple[int, int]] = []
    for line_no in matches:
        start = max(0, line_no - context_lines)
        end = min(len(lines), line_no + context_lines + 1)
        if windows and start <= windows[-1][1]:
            windows[-1] = (windows[-1][0], max(windows[-1][1], end))
        else:
            windows.append((start, end))

    pieces: list[str] = []
    used = 0
    for start, end in windows:
        piece = "\n".join(
            f"{index + 1:>5}: {lines[index]}" for index in range(start, end)
        )
        prefix = "\n...\n" if pieces else ""
        if used + len(prefix) + len(piece) > max_chars:
            available = max_chars - used - len(prefix)
            if available > 0:
                pieces.append(prefix + piece[:available] + "\n[truncated]")
            break
        pieces.append(prefix + piece)
        used += len(prefix) + len(piece)

    return "".join(pieces)


def looks_like_source_file(path: str) -> bool:
    return Path(path).suffix.lower() in SOURCE_EXTENSIONS


def looks_like_test_file(path: str) -> bool:
    normalized = path.lower()
    return (
        "/test" in normalized
        or normalized.startswith("test")
        or normalized.endswith("_test.py")
        or normalized.endswith("_test.go")
        or normalized.endswith(".test.ts")
        or normalized.endswith(".test.js")
        or normalized.endswith(".spec.ts")
        or normalized.endswith(".spec.js")
    )


def is_allowed_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    parts = normalized.split("/")

    if any(part in IGNORED_DIRECTORIES for part in parts):
        return False

    filename = parts[-1]
    if filename in IGNORED_FILES:
        return False

    return Path(filename).suffix.lower() not in IGNORED_EXTENSIONS


def deduplicate_files(files: list[ContextFile]) -> list[ContextFile]:
    seen: set[str] = set()
    result: list[ContextFile] = []
    for file in files:
        if file.path in seen:
            continue
        seen.add(file.path)
        result.append(file)
    return result
