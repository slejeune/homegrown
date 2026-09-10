# Homegrown

**Local AI for Git. A more Homegrown way to develop.**

Homegrown (`hmgr`) is a local AI-assisted CLI for understanding and working with your Git repositories.

It brings together Git, GitHub CLI, and Ollama to give a local AI model the context behind your work: your code, Git history, branches, diffs, issues, pull requests, documentation, and project conventions.

That makes Homegrown useful for the parts of development that don't need a full coding agent. Get help with issues, commits, pull requests, and repository work without spending your hosted AI usage on tasks that can happen locally.

And because the model runs locally, your repository context can stay local too.

---

## Contents

- [Why Homegrown?](#why-homegrown)
- [Commands](#commands)
- [Getting started](#getting-started)
- [Local AI](#local-ai)
- [Repository context](#repository-context)
- [Templates](#templates)
- [Configuration](#configuration)
- [Typical workflow](#typical-workflow)
- [Safety](#safety)
- [Roadmap](#roadmap)
- [License](#license)

---

## Why Homegrown?

A commit message should know what actually changed. A pull request should know what changed and why. An issue should give the next developer enough direction to pick up the work.

Homegrown builds that output locally from the repository itself rather than a generic prompt. The AI-assisted surface is deliberately small: issues, commit messages, pull requests, and an interactive repository chat. Git and GitHub operations remain explicit and predictable.

---

## Commands

### Core Git and GitHub workflow

| Command | Purpose |
| --- | --- |
| `hmgr issue "..."` | Create an actionable GitHub issue with local repository context |
| `hmgr develop 123` | Start work on an existing issue |
| `hmgr commit` | Generate a commit message from staged changes and confirm before committing |
| `hmgr pr` | Generate a pull request from the current branch |
| `hmgr pr --check` | Check pull-request readiness without creating one |
| `hmgr merge` | Merge a pull request through GitHub CLI |
| `hmgr push` | Push the current branch |

### Debug and repository inspection

| Command | Purpose |
| --- | --- |
| `hmgr context` | Inspect the context Homegrown assembles |
| `hmgr doctor` | Check Git, GitHub CLI, Ollama, and local configuration |
| `hmgr status` | Show repository and workflow state |

### Interactive chat

`hmgr chat` is intentionally narrow. Ask a question about the current repository and Homegrown selects a small, query-relevant context before asking the local model. It is for quick repository questions, not a replacement for a coding agent.

---

## Getting started

### Requirements

- Python 3.10+
- Git
- GitHub CLI
- Ollama

Homegrown has no Python runtime dependencies outside the standard library.

### Install Ollama and a model

The default model is:

```text
Qwen2.5-Coder:7b
```

Pull it with:

```bash
ollama pull Qwen2.5-Coder:7b
```

### Install Homegrown

For local development, an editable install is useful:

```bash
pip install -e .
```

For a persistent command-line installation, `pipx` keeps Homegrown isolated from your other Python packages:

```bash
pipx install .
```

After installation, use `hmgr` directly:

```bash
hmgr status
hmgr issue "Add caching to the API client"
```

---

## Local AI

Homegrown uses Ollama to run one configured local model. The default is `Qwen2.5-Coder:7b` and can be changed with:

```bash
export HMGR_MODEL=your-model
```

The small model is intentionally used for focused tasks rather than a broad set of overlapping AI commands. Hosted coding agents such as Claude Code or Codex can remain the right tool for implementation-heavy work.

---

## Repository context

Homegrown does not send the entire repository blindly. It assembles context for the current operation from relevant repository files, documentation, instructions, Git state, GitHub data, and templates as appropriate.

Before an AI-assisted operation, Homegrown prints a user-facing **context manifest**: a compact table summarizing the same repository context supplied to the model. The full assembled context remains available through the `context` command.

You can inspect the assembled context directly with:

```bash
hmgr context
hmgr context --issue 123
```

The displayed manifest and the model context are both bounded by configuration so a small local model is not overwhelmed.

---

## Templates

Homegrown ships with default templates for AI-assisted issues, commits, and pull requests. You can override the template for an operation by adding its supported file to the repository:

| Operation | Repository template path |
| --- | --- |
| `hmgr issue` | `.github/ISSUE_TEMPLATE.md` |
| `hmgr commit` | `.github/COMMIT_TEMPLATE.md` |
| `hmgr pr` | `.github/PULL_REQUEST_TEMPLATE.md` |

For each operation, Homegrown uses the first matching repository template in that order; if none exists, it uses its bundled default. It includes only the template for the current operation, never templates for other artifact types.

Repository-wide instructions can live in `AGENTS.md` and/or `CLAUDE.md` at the repository root. Homegrown includes both files when present. If neither exists, it falls back to its bundled instruction file. Keep those files focused on project conventions that should affect generated issues, commits, and pull requests.

The important distinction is that these templates **complement** Claude Code and Codex rather than replace their instruction systems:

- Homegrown's templates shape the output generated by `hmgr issue`, `hmgr commit`, and `hmgr pr`.
- Claude Code and Codex can continue using their own repository instructions and templates for coding-agent work.
- Shared GitHub issue/PR templates can provide a common project structure across all three workflows, while each tool keeps its own local instructions.

Keep project-specific conventions in the repository so they can be versioned and reviewed with the code. Homegrown treats repository content as evidence and never lets text inside source files override its safety rules.

---

## Configuration

| Variable | Description | Default |
| --- | --- | --- |
| `HMGR_MODEL` | Ollama model | `Qwen2.5-Coder:7b` |
| `HMGR_BASE` | Base branch for PR context | `main` |
| `OLLAMA_URL` | Ollama server | `http://localhost:11434` |
| `HMGR_MAX_CONTEXT_CHARS` | Maximum rendered context | `200000` |
| `HMGR_MAX_FILE_CHARS` | Maximum content per file | `12000` |

---

## Typical workflow

A simple issue-driven workflow is:

```bash
hmgr issue "Add caching to the API client"
hmgr develop 123
# make code changes
hmgr status
git add .
hmgr commit
hmgr pr
hmgr merge
```

Use `hmgr chat` whenever you need a quick repository question answered without switching to a larger coding agent.

---

## Safety

Homegrown is AI-assisted, not autonomous. AI-generated issue, commit, and pull request text is shown before consequential actions are taken. Git and GitHub operations are explicit commands rather than hidden side effects.

Generated file references are checked against repository evidence; when a model mentions a path that cannot be verified, Homegrown marks it as unverified rather than presenting it as a fact.

---

## Roadmap

- Improve relevance score for files to be smarter
- Manual editing of whatever is generated
- Give the `context` command a parameter *which* context to render
- Add more extensive tests

---

## License

See the repository for license information.
