---
parent: More info
nav_order: 600
description: Wrapping an AI coding agent with a security supervision layer.
---

# Safe wrapper pattern

The *safe wrapper pattern* describes wrapping an AI coding agent such as
aider in a narrow supervision layer that mediates between an upstream
planner (for example, a chat client or another LLM session) and the local
agent that actually edits code. The wrapper exposes a small, explicit set
of operations instead of a general-purpose shell, so that every change can
be confined, checked and audited.

This page documents the pattern itself, not any single tool. Aider can be
run under such a wrapper, and can also be the local execution agent that a
wrapper invokes.

## Motivation

When an LLM is allowed to run arbitrary commands against a repository, a
single bad instruction can delete files, read secrets, push to a remote or
modify anything the shell can reach. The safe wrapper pattern reduces that
risk by placing the agent behind a channel that:

- only accepts well-defined operations,
- restricts file access to a configured workspace,
- only runs commands that match a preconfigured allowlist,
- treats out-of-scope changes as policy violations rather than silently
  accepting them, and
- records structured evidence for independent review.

The goal is not to make the agent smarter, but to make its blast radius
small and observable.

## Roles

A typical setup separates three roles:

1. **Planner** &mdash; the upstream LLM session that decides what should be
   done. It talks only to the wrapper's tool surface, never to the agent's
   shell directly.
2. **Wrapper** &mdash; the supervision layer. It receives plans, persists
   them as tasks, starts a preregistered local agent, runs verification,
   and returns bounded results.
3. **Execution agent** &mdash; the program that edits code (for example,
   aider). Its launch command comes from local configuration, not from
   model input.

Keeping these roles separate means a compromised or confused planner cannot
pick its own interpreter, change its own launch arguments, or reach outside
the workspace.

## Core mechanisms

### Workspace confinement

All file access is restricted to a single configured workspace root. Paths
supplied by the planner must resolve inside that root; attempts to escape
with `..` or absolute paths outside the root are rejected. The workspace
root should be a dedicated directory containing the relevant repositories,
not a home directory, a disk root, or a directory full of personal files.

### Command allowlists

Verification and build commands must match an allowlist exactly. There is
no fuzzy matching and no shell interpolation &mdash; a command that is
"almost" the same as an allowed one is rejected. This prevents the planner
from smuggling new commands in by small variations. Per-repository
allowlists can extend the global one, but the repository being operated on
cannot grant itself new commands.

### Sensitive-file blocking

Paths that look like secrets are blocked by name and by content. This
includes `.env` files, API keys, tokens, cookies, SSH keys and other
credential files. Apparent secret values that appear in task artifacts are
redacted before they are written or returned.

### Agent registration

The execution agent's command and arguments are defined in local
configuration and referenced by name. The planner requests an agent by
name; it cannot supply a command line. This means the set of things that
can run is fixed ahead of time and auditable.

### Scope-violation detection

After the agent runs, the wrapper compares the set of changed files against
the expected scope (the target repository, inside the workspace). If
changes appear outside that scope, the task is marked as a scope violation
and fails closed rather than committing or accepting the result. This
catches both accidental edits to unrelated files and prompts that wandered
outside their task.

### Auditable task evidence

Each task produces structured artifacts so the result can be reviewed
without trusting the agent's self-report. Typical artifacts include:

- a status record with the current phase, heartbeat and any error,
- a structured result with changed paths and warnings,
- a full diff of the task's changes,
- per-command verification results, and
- file-level add/remove statistics.

The wrapper never treats "the agent exited cleanly" as "the result is
correct"; completion is a terminal state, not an acceptance state.

## Aider under a safe wrapper

Aider fits the pattern in two ways:

- **As the execution agent.** A wrapper can launch aider with
  `aider --message "..."` against a specific file or repository, then run
  the project's own test and lint commands from the allowlist to verify the
  result. With Aider's default Git integration, edits are automatically
  committed and are easy to review or undo. Because operators can disable
  auto-commits, a wrapper should not assume that a commit exists. See
  [scripting aider](/docs/scripting.html) for the command-line entry points
  a wrapper would use.

- **As the edited target.** When aider is used to develop a project that is
  itself run under a wrapper, confining aider's working directory to the
  workspace root and refusing to let it touch sibling repositories keeps a
  session focused on one task.

In both cases the value comes from the wrapper enforcing confinement,
allowlists and evidence &mdash; aider's own capabilities are unchanged.

## What the pattern is not

- It is not a sandbox that guarantees isolation from the operating system.
  The agent still runs as the local user; the wrapper narrows what it is
  asked to do and checks the result.
- It is not a substitute for human review. The wrapper makes the blast
  radius small and the evidence available, but a person still decides
  whether to accept, commit or publish.
- It is not autopilot. The wrapper does not auto-commit, auto-push, tag or
  release on the agent's behalf. Those actions stay manual.

## Example implementation

[PatchWarden](https://github.com/jiezeng2004-design/PatchWarden) is one
implementation of this pattern: a local MCP bridge that exposes a fixed
tool surface, confines file access to a configured workspace root, matches
verification commands against an exact allowlist, marks out-of-scope
changes as violations, and writes structured task artifacts for review. The
pattern described above does not depend on PatchWarden; any layer that
enforces the same mechanisms provides the same guarantees.

## Further reading

- [Scripting aider](/docs/scripting.html) &mdash; launching aider from
  scripts and wrappers.
- [Git integration](/docs/git.html) &mdash; using git history to review and
  undo AI changes.
- [Troubleshooting](/docs/troubleshooting.html) &mdash; diagnosing common
  problems.
