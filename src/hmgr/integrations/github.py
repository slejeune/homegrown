import json
import subprocess
from typing import Any


class GitHub:
    def run(
        self,
        *args: str,
        check: bool = True,
    ) -> str:
        result = subprocess.run(
            ["gh", *args],
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

    def check_auth(self) -> None:
        self.run(
            "auth",
            "status",
        )

    def get_issue(
        self,
        issue_number: int,
    ) -> dict[str, Any]:
        output = self.run(
            "issue",
            "view",
            str(issue_number),
            "--json",
            "number,title,body,state,labels,assignees,url",
        )

        return json.loads(output)

    def list_labels(self) -> list[str]:
        output = self.run(
            "label",
            "list",
            "--limit",
            "100",
            "--json",
            "name",
        )

        labels = json.loads(output)

        return [item["name"] for item in labels if item.get("name")]

    def ensure_label(self, label: str) -> None:
        if label in self.list_labels():
            return

        result = self.run(
            "label",
            "create",
            label,
            check=False,
        )

        if result:
            return

    def create_issue(
        self,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> int:
        labels = labels or []

        for label in labels:
            self.ensure_label(label)

        args = [
            "issue",
            "create",
            "--title",
            title,
            "--body",
            body,
        ]

        for label in labels:
            args.extend(["--label", label])

        output = self.run(*args)

        issue_number = self._extract_issue_number(output)

        if issue_number is None:
            raise RuntimeError(f"Could not determine issue number from: {output}")

        return issue_number

    def develop_issue(
        self,
        issue_number: int,
        branch_name: str,
        checkout: bool = True,
    ) -> None:
        args = [
            "issue",
            "develop",
            str(issue_number),
            "--name",
            branch_name,
        ]

        if checkout:
            args.append("--checkout")

        self.run(*args)

    def create_pr(
        self,
        title: str,
        body: str,
        base: str,
    ) -> str:
        return self.run(
            "pr",
            "create",
            "--base",
            base,
            "--title",
            title,
            "--body",
            body,
        )

    def repo(self) -> dict[str, Any]:
        output = self.run(
            "repo",
            "view",
            "--json",
            "nameWithOwner,url,description,defaultBranchRef",
        )

        return json.loads(output)

    def _extract_issue_number(
        self,
        output: str,
    ) -> int | None:
        import re

        match = re.search(
            r"/issues/(\d+)",
            output,
        )

        if match:
            return int(match.group(1))

        match = re.search(
            r"#(\d+)",
            output,
        )

        if match:
            return int(match.group(1))

        return None

    def pull_requests_for_branch(
        self,
        branch: str,
    ) -> list[dict[str, Any]]:
        output = self.run(
            "pr",
            "list",
            "--head",
            branch,
            "--json",
            "number,title,state,url",
            "--limit",
            "10",
        )

        return json.loads(output)
