import argparse
import sys

from .commands import (
    chat,
    commit,
    context as context_command,
    develop,
    doctor,
    issue,
    merge,
    pr,
    push,
    status,
)
from .config import Config
from .ui.console import error, warning


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hmgr", description="Local AI for Git and GitHub workflows"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    issue_parser = subparsers.add_parser("issue", help="Create a GitHub issue")
    issue_parser.add_argument("description", help="What the issue should address")

    develop_parser = subparsers.add_parser(
        "develop", help="Start work on an existing issue"
    )
    develop_parser.add_argument("issue_number", type=int, help="GitHub issue number")
    develop_parser.add_argument("--branch", help="Optional branch name")

    commit_parser = subparsers.add_parser(
        "commit", help="Generate a commit message from staged changes"
    )
    commit_parser.add_argument("--apply", action="store_true", help=argparse.SUPPRESS)

    pr_parser = subparsers.add_parser("pr", help="Create a pull request")
    pr_parser.add_argument("--base", help="Base branch")
    pr_parser.add_argument(
        "--check", action="store_true", help="Check PR readiness without creating one"
    )

    merge_parser = subparsers.add_parser(
        "merge", help="Merge a pull request via GitHub CLI"
    )
    merge_parser.add_argument(
        "--method", choices=("squash", "merge", "rebase"), default="merge"
    )
    merge_parser.add_argument("--pr", dest="pull_request_number", type=int)
    merge_parser.add_argument("--keep-branch", action="store_true")

    subparsers.add_parser("push", help="Push the current branch")

    context_parser = subparsers.add_parser("context", help="Inspect repository context")
    context_parser.add_argument(
        "--issue", type=int, dest="issue_number", help="Show context for an issue"
    )

    subparsers.add_parser("doctor", help="Check the hmgr environment")
    subparsers.add_parser("status", help="Show repository and workflow status")
    subparsers.add_parser(
        "chat", help="Ask questions about the repository interactively"
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        config = Config.from_env()
        if args.command == "issue":
            issue.run(args.description, config)
        elif args.command == "develop":
            develop.run(config, args.issue_number, args.branch)
        elif args.command == "commit":
            commit.run(config=config)
        elif args.command == "pr":
            pr.check(config) if args.check else pr.run(config, args.base)
        elif args.command == "merge":
            merge.run(
                method=args.method,
                delete_branch=not args.keep_branch,
                pull_request_number=args.pull_request_number,
            )
        elif args.command == "push":
            push.run()
        elif args.command == "context":
            context_command.run(args.issue_number)
        elif args.command == "doctor":
            doctor.run(config)
        elif args.command == "status":
            status.run()
        elif args.command == "chat":
            chat.Chat(config).run()
    except KeyboardInterrupt:
        warning("Cancelled.")
        sys.exit(130)
    except Exception as exc:
        error(f"Error: {exc}")
        sys.exit(1)
