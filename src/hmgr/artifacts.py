from enum import Enum


class ArtifactKind(str, Enum):
    ISSUE = "issue"
    COMMIT = "commit"
    PULL_REQUEST = "pull_request"
