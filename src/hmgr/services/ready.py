class Ready:
    def __init__(self, git, github, base_branch="main"):
        self.git = git
        self.github = github
        self.base_branch = base_branch

    def check(self):
        branch = self.git.current_branch()
        issue = self.git.issue_for_branch(branch)
        prs = self.github.pull_requests_for_branch(branch)
        checks = [
            ("Issue linked", issue is not None),
            ("Branch contains changes", bool(self.git.changed_files(self.base_branch))),
            ("Tests/verification", self._verified()),
            ("Working tree clean", not bool(self.git.status())),
        ]
        return {
            "branch": branch,
            "issue": issue,
            "pr": prs[0] if prs else None,
            "checks": checks,
            "ready": all(ok for _, ok in checks),
        }

    def _verified(self):
        try:
            import json

            data = json.loads(
                (self.git.root() / ".git" / "hmgr" / "verification.json").read_text()
            )
            return bool(data) and all(x.get("status") == "passed" for x in data)
        except (OSError, ValueError):
            return False
