import unittest

from hmgr.models import CommitProposal, IssueProposal, PullRequestProposal
from hmgr.validation import (
    mark_unverified_file_references,
    validate_commit_proposal,
    validate_issue_proposal,
    validate_pull_request_proposal,
)


class ValidationTests(unittest.TestCase):
    def test_meta_language_validators_reject_meta_language(self):
        self.assertIsNotNone(
            validate_commit_proposal(CommitProposal("I was asked to fix this", ""))
        )
        self.assertIsNotNone(
            validate_issue_proposal(IssueProposal("The user wants this", ""))
        )
        self.assertIsNotNone(
            validate_pull_request_proposal(
                PullRequestProposal("Implement the change", "Based on your request")
            )
        )

    def test_file_reference_marker_preserves_known_paths(self):
        text = "Use `src/hmgr/models.py` and `src/hmgr/missing.py`."
        result = mark_unverified_file_references(text, {"src/hmgr/models.py"})
        self.assertIn("`src/hmgr/models.py`", result)
        self.assertIn(
            "`src/hmgr/missing.py` *(unverified file reference)*",
            result,
        )


if __name__ == "__main__":
    unittest.main()
