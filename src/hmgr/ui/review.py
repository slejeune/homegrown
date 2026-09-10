from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from .console import info

T = TypeVar("T")


def review_proposal(
    generate: Callable[[str | None], T],
    display: Callable[[T], None],
    validate: Callable[[T], str | None] | None = None,
    max_validation_retries: int = 2,
) -> T | None:
    """Generate, validate, display, and optionally regenerate from feedback."""
    feedback: str | None = None
    validation_retries = 0

    while True:
        proposal = generate(feedback)
        validation_error = validate(proposal) if validate else None
        if validation_error:
            if validation_retries >= max_validation_retries:
                info("Automatic validation retries exhausted; stopping generation.")
                return None

            validation_retries += 1
            info(
                "The generated proposal failed validation; "
                f"retrying automatically ({validation_retries}/{max_validation_retries}) "
                "with the validation feedback."
            )
            feedback = validation_error
            continue

        display(proposal)

        while True:
            answer = input("Accept, reject, or give feedback? [A/r/f] ").strip().lower()
            if answer in {"", "a", "accept", "y", "yes"}:
                return proposal
            if answer in {"r", "reject", "n", "no"}:
                return None
            if answer in {"f", "feedback"}:
                new_feedback = input("Feedback: ").strip()
                if new_feedback:
                    info(
                        "Feedback received, generating a new proposal from the original request."
                    )
                    feedback = new_feedback
                    validation_retries = 0
                    break
            print("Please choose A to accept, r to reject, or f to give feedback.")
