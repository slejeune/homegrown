import json
import subprocess
from pathlib import Path


class Git:
    def run(
        self,
        *args: str,
        check: bool = True,
    ) -> str:
        result = subprocess.run(
            ["git", *args],
            text=True,
            capture_output=True,
            check=False,
        )

        if check and result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(message)

        return result.stdout.strip()

    def check(self) -> None:
        self.run("--version")

        if not self.is_repository():
            raise RuntimeError("Current directory is not a Git repository.")

    def is_repository(self) -> bool:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
        )
        return result.returncode == 0

    def root(self) -> Path:
        return Path(self.run("rev-parse", "--show-toplevel"))

    def current_branch(self) -> str:
        return self.run(
            "branch",
            "--show-current",
        )

    def status(self) -> str:
        return self.run(
            "status",
            "--short",
        )

    def diff(
        self,
        base_branch: str,
    ) -> str:
        return self.run(
            "diff",
            f"{base_branch}...HEAD",
            "--",
        )

    def diff_file(
        self,
        base_branch: str,
        path: str,
        *,
        context_lines: int = 20,
    ) -> str:
        return self.run(
            "diff",
            f"{base_branch}...HEAD",
            f"--unified={context_lines}",
            "--",
            path,
        )

    def commits(
        self,
        base_branch: str,
    ) -> str:
        return self.run(
            "log",
            f"{base_branch}..HEAD",
            "--pretty=format:%h | %s%n%b",
        )

    def changed_files(
        self,
        base_branch: str,
    ) -> list[str]:
        output = self.run(
            "diff",
            "--name-only",
            f"{base_branch}...HEAD",
        )

        if not output:
            return []

        return output.splitlines()

    def tracked_files(self) -> list[str]:
        output = self.run(
            "ls-files",
        )

        if not output:
            return []

        return output.splitlines()

    def file_content(self, path: str) -> str:
        root = self.root()
        file_path = root / path

        if not file_path.is_file():
            return ""

        try:
            return file_path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            return ""

    def save_issue_mapping(
        self,
        branch_name: str,
        issue_number: int,
    ) -> None:
        root = self.root()
        directory = root / ".git" / "hmgr"
        directory.mkdir(parents=True, exist_ok=True)

        mapping_file = directory / "branch-issues.json"

        mapping = {}

        if mapping_file.exists():
            try:
                mapping = json.loads(
                    mapping_file.read_text(
                        encoding="utf-8",
                    )
                )
            except (json.JSONDecodeError, OSError):
                mapping = {}

        mapping[branch_name] = issue_number

        mapping_file.write_text(
            json.dumps(mapping, indent=2),
            encoding="utf-8",
        )

    def issue_for_branch(
        self,
        branch_name: str | None = None,
    ) -> int | None:
        branch = branch_name or self.current_branch()

        mapping_file = self.root() / ".git" / "hmgr" / "branch-issues.json"

        if not mapping_file.exists():
            return None

        try:
            mapping = json.loads(
                mapping_file.read_text(
                    encoding="utf-8",
                )
            )
        except (json.JSONDecodeError, OSError):
            return None

        if not isinstance(mapping, dict):
            return None

        value = mapping.get(branch)

        if value is None:
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def staged_diff(self) -> str:
        return self.run(
            "diff",
            "--cached",
        )

    def staged_files(self) -> list[str]:
        output = self.run(
            "diff",
            "--cached",
            "--name-only",
        )

        if not output:
            return []

        return output.splitlines()

    def commit(
        self,
        message: str,
        body: str | None = None,
    ) -> str:
        args = [
            "commit",
            "-m",
            message,
        ]

        if body:
            args.extend(
                [
                    "-m",
                    body,
                ]
            )

        return self.run(*args)
