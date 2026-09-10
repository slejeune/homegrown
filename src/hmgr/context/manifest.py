from __future__ import annotations

from typing import TYPE_CHECKING

from .models import ContextEntry

if TYPE_CHECKING:
    from .models import Context


def build_manifest(context: Context) -> list[ContextEntry]:
    """Describe repository resources that can appear in the context."""
    entries = [
        ContextEntry(
            path=file.path,
            category="instructions",
            reason="repository instructions",
            priority=130,
            included_chars=file.included_chars,
            total_chars=file.total_chars,
        )
        for file in context.instructions
    ]
    entries += [
        ContextEntry(
            path=file.path,
            category="documentation",
            reason="repository documentation",
            priority=60,
            included_chars=file.included_chars,
            total_chars=file.total_chars,
        )
        for file in context.documentation
    ]
    if context.template:
        entries.append(
            ContextEntry(
                path=context.template.path,
                category="template",
                reason=f"{context.purpose.value if context.purpose else 'artifact'} template",
                priority=125,
                included_chars=context.template.included_chars,
                total_chars=context.template.total_chars,
            )
        )
    if context.issue:
        entries.append(
            ContextEntry(
                path=f"issue://{context.issue.number}",
                category="issue",
                reason="linked issue",
                priority=110,
            )
        )
    entries += [
        ContextEntry(
            path=file.path,
            category="source",
            reason="relevant to the task",
            priority=80,
            included_chars=file.included_chars,
            total_chars=file.total_chars,
        )
        for file in context.relevant_files
    ]
    entries += [
        ContextEntry(
            path=file.path,
            category="source",
            reason="related to the current change",
            priority=80,
            included_chars=file.included_chars,
            total_chars=file.total_chars,
        )
        for file in context.related_files
    ]
    entries += [
        ContextEntry(
            path=path,
            category="changed-file",
            reason="changed in the current pull request",
            priority=120,
        )
        for path in context.changed_files
    ]
    entries += [
        ContextEntry(
            path=path,
            category="staged-file",
            reason="included in staged diff",
            priority=110,
        )
        for path in context.staged_files
    ]
    if context.diff:
        entries.append(
            ContextEntry(
                path="diff://current-branch",
                category="diff",
                reason="authoritative pull request change",
                priority=120,
            )
        )
    if context.staged_diff:
        entries.append(
            ContextEntry(
                path="diff://staged",
                category="diff",
                reason="authoritative staged change",
                priority=110,
            )
        )
    return entries
