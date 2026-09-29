from __future__ import annotations

from typing import TYPE_CHECKING

from .models import ContextEntry, ContextFile, RenderSection

if TYPE_CHECKING:
    from .models import Context


def render_sections(
    sections: list[RenderSection],
    max_chars: int | None = None,
) -> str:
    """Render sections without ever exceeding max_chars.

    Higher-priority sections are considered first. Ties preserve input order.
    Truncatable sections may use the remaining budget; lower-priority sections
    are skipped rather than emitting partial evidence.
    """
    ordered = sorted(
        enumerate(sections),
        key=lambda item: (-item[1].priority, item[0]),
    )
    rendered: list[str] = []
    used = 0

    for _, section in ordered:
        section_text = f"<{section.name}>\n{section.content}\n</{section.name}>"
        separator = "\n\n" if rendered else ""

        if max_chars is None:
            rendered.append(separator + section_text)
            continue

        available = max_chars - used - len(separator)
        if available <= 0:
            break

        if len(section_text) <= available:
            rendered.append(separator + section_text)
            used += len(separator) + len(section_text)
            continue

        if section.truncatable and available > 0:
            marker = "\n[truncated]"
            if available <= len(marker):
                rendered.append(separator + section_text[:available])
            else:
                rendered.append(
                    separator + section_text[: available - len(marker)] + marker
                )
            used = max_chars
            break

    return "".join(rendered)


def render_files(files: list[ContextFile]) -> str:
    return "\n\n".join(file.render() for file in files)


def _manifest_row(entry: ContextEntry) -> list[str]:
    if entry.included_chars is None:
        included = total = percentage = "-"
    else:
        total_value = entry.total_chars or entry.included_chars
        included = str(entry.included_chars)
        total = str(total_value)
        percentage = (
            f"{entry.included_chars / total_value * 100:.0f}%"
            if total_value
            else "100%"
        )

    return [
        entry.path,
        entry.category,
        str(entry.priority),
        included,
        total,
        percentage,
        entry.reason,
    ]


def render_manifest(entries: list[ContextEntry]) -> str:
    """Render the user-facing context manifest as a stable plain-text table.

    ANSI styling is intentionally left to the console layer so this renderer
    remains useful in tests, redirected output, and non-terminal consumers.
    """
    headers = ["PATH", "CATEGORY", "PRIORITY", "INCLUDED", "TOTAL", "USED", "REASON"]
    rows = [
        _manifest_row(entry)
        for entry in sorted(entries, key=lambda item: -item.priority)
    ]
    widths = [len(header) for header in headers]
    for row_values in rows:
        for index, value in enumerate(row_values):
            widths[index] = max(widths[index], len(value))

    def row(values: list[str]) -> str:
        return " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(values)
        )

    lines = [
        row(headers),
        "-+-".join("-" * width for width in widths),
    ]
    lines.extend(row(values) for values in rows)
    return "\n".join(lines)


def render_evidence(
    context: Context,
    max_chars: int | None = None,
    optional_max_chars: int | None = None,
) -> str:
    sections = [
        RenderSection(
            "repository",
            "\n".join(
                filter(
                    None,
                    [
                        f"Name: {context.name}",
                        f"URL: {context.url}",
                        f"Description: {context.description}",
                        f"Current branch: {context.branch}",
                        f"Base branch: {context.base_branch}"
                        if context.base_branch
                        else None,
                    ],
                )
            ),
            priority=90,
            truncatable=True,
        )
    ]
    if context.issue:
        sections.append(
            RenderSection("linked_issue", context.issue.as_text(), 110, True)
        )
    if context.staged_files:
        sections.append(
            RenderSection(
                "staged_files",
                "\n".join(f"- {path}" for path in context.staged_files),
                110,
                True,
            )
        )
    if context.staged_diff:
        sections.append(
            RenderSection(
                "staged_diff", f"```diff\n{context.staged_diff}\n```", 110, True
            )
        )
    if context.changed_files:
        sections.append(
            RenderSection(
                "changed_files",
                "\n".join(f"- {path}" for path in context.changed_files),
                120,
                True,
            )
        )
    if context.diff:
        sections.append(
            RenderSection("diff", f"```diff\n{context.diff}\n```", 120, True)
        )
    if context.related_files:
        sections.append(
            RenderSection(
                "related_source_files", render_files(context.related_files), 80, True
            )
        )
    if context.relevant_files:
        sections.append(
            RenderSection(
                "relevant_source_files", render_files(context.relevant_files), 80, True
            )
        )
    if context.documentation:
        sections.append(
            RenderSection("documentation", render_files(context.documentation), 60)
        )
    if context.commits:
        sections.append(RenderSection("commits", context.commits, 40))
    if context.tracked_files:
        sections.append(
            RenderSection("repository_files", "\n".join(context.tracked_files), 20)
        )

    mandatory = [section for section in sections if section.priority >= 100]
    optional = [section for section in sections if section.priority < 100]
    mandatory_text = render_sections(mandatory)

    if max_chars is None:
        optional_budget = optional_max_chars
    else:
        optional_budget = max(0, max_chars - len(mandatory_text))
        if optional_max_chars is not None:
            optional_budget = min(optional_budget, optional_max_chars)

    optional_text = render_sections(optional, max_chars=optional_budget)
    if mandatory_text and optional_text:
        return f"{mandatory_text}\n\n{optional_text}"
    return mandatory_text or optional_text


def render_context(context: Context, max_chars: int | None = None) -> str:
    sections = [
        RenderSection(
            "project_instructions",
            render_files(context.instructions) or "No project instructions found.",
            130,
            True,
        )
    ]
    if context.template:
        sections.append(RenderSection("template", context.template.render(), 125))
    sections.append(
        RenderSection("repository_evidence", render_evidence(context), 90, True)
    )
    return render_sections(sections, max_chars=max_chars)
