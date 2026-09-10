from dataclasses import dataclass

from ..artifacts import ArtifactKind


@dataclass(frozen=True)
class ArtifactSpec:
    kind: ArtifactKind
    task: str
    instructions: str
    output_requirements: str
