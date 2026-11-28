#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys

BYPASS_ENVIRONMENT_VARIABLE = "HOLON_GIT_GUARD_BYPASS"
MAIN_WORKTREE = re.compile(r"(?:^|/)apps/(?:holon-agentic-coder|holon-coherence)/main(?:/|$)")
FLOW_BRANCH = re.compile(r"^(?:[IPE]-|flow-)")
FORCE_PUSH_CLUSTER = re.compile(r"^-[A-Za-z]*f[A-Za-z]*$")
HEREDOC_MARKER = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
COMMAND_SUBSTITUTION = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")
WRAPPER_COMMANDS = {"sudo", "env", "command", "time", "nohup", "exec", "builtin"}
SHELL_COMMANDS = {"bash", "sh", "zsh"}
OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
MUTATING_SUBCOMMANDS = {
    "add",
    "am",
    "checkout",
    "cherry-pick",
    "clean",
    "commit",
    "merge",
    "mv",
    "pull",
    "rebase",
    "reset",
    "restore",
    "revert",
    "rm",
    "switch",
}
FAST_FORWARD_SUBCOMMANDS = {"merge", "pull"}
STAGE_EVERYTHING = {"-A", "--all", ".", "./"}


def strip_heredoc_bodies(text: str) -> str:
    kept: list[str] = []
    delimiter: str | None = None
    for line in text.replace("\\\n", " ").split("\n"):
        if delimiter is not None:
            if line.strip() == delimiter:
                delimiter = None
            continue
        kept.append(line)
        marker = HEREDOC_MARKER.search(line)
        if marker:
            delimiter = marker.group(2)
    return "\n".join(kept)


def split_segments(text: str) -> list[str]:
    segments: list[str] = []
    current: list[str] = []
    quote = ""
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            current.append(char)
            if char == "\\" and quote == '"' and index + 1 < len(text):
                index += 1
                current.append(text[index])
            elif char == quote:
                quote = ""
        elif char == "\\" and index + 1 < len(text):
            current.append(char)
            index += 1
            current.append(text[index])
        elif char in "'\"":
            quote = char
            current.append(char)
        elif char in ";&|\n()`":
            segments.append("".join(current))
            current = []
        else:
            current.append(char)
        index += 1
    segments.append("".join(current))
    return [segment.strip() for segment in segments if segment.strip()]


def tokenize(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def is_flow_worktree(directory: str) -> bool:
    if any(part.startswith("flow-") for part in directory.split("/")):
        return True
    if not os.path.isdir(directory):
        return False
    result = subprocess.run(
        ["git", "-C", directory, "symbolic-ref", "--short", "-q", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(FLOW_BRANCH.match(result.stdout.strip()))


def resolve_directory(base: str, target: str) -> str:
    return os.path.normpath(os.path.join(base, os.path.expanduser(target)))


def check_git_tokens(tokens: list[str], cwd: str) -> str | None:
    directory = cwd
    index = 1
    while index < len(tokens) and tokens[index].startswith("-"):
        option = tokens[index]
        if option == "-C" and index + 1 < len(tokens):
            directory = resolve_directory(directory, tokens[index + 1])
        index += 2 if option in OPTIONS_WITH_VALUE else 1
    if index >= len(tokens):
        return None
    subcommand = tokens[index]
    arguments = tokens[index + 1 :]

    if subcommand == "stash":
        return "git stash is forbidden: the stash stack is shared by every worktree; use a patch file or a WIP commit"
    if "--no-verify" in arguments or (subcommand == "commit" and "-n" in arguments):
        return "--no-verify is forbidden: fix the hook failure or stop and report"
    if subcommand == "add" and any(argument in STAGE_EVERYTHING for argument in arguments):
        return "git add -A / --all / . is forbidden: stage explicit paths only"
    if subcommand == "push" and any(
        argument in ("--force", "--force-with-lease")
        or argument.startswith("--force-with-lease=")
        or argument.startswith("+")
        or FORCE_PUSH_CLUSTER.match(argument)
        for argument in arguments
    ):
        return "force-push is forbidden: never rewrite published history"
    rebases = subcommand == "rebase" or (
        subcommand == "pull" and any(argument == "-r" or argument.startswith("--rebase") for argument in arguments)
    )
    if rebases and is_flow_worktree(directory):
        return "rebasing a flow branch is forbidden: merge origin/main into it instead"
    if MAIN_WORKTREE.search(directory + "/") and subcommand in MUTATING_SUBCOMMANDS:
        fast_forward = subcommand in FAST_FORWARD_SUBCOMMANDS and "--ff-only" in arguments
        if not fast_forward:
            return "a main worktree is never edited: only git merge --ff-only / git pull --ff-only may change it"
    return None


def check_command(command: str, cwd: str) -> str | None:
    text = strip_heredoc_bodies(command)
    for match in COMMAND_SUBSTITUTION.finditer(text):
        reason = check_command(match.group(1) or match.group(2) or "", cwd)
        if reason:
            return reason
    directory = cwd
    for segment in split_segments(text):
        tokens = tokenize(segment)
        while tokens and (ASSIGNMENT.match(tokens[0]) or tokens[0] in WRAPPER_COMMANDS):
            tokens = tokens[1:]
        if not tokens:
            continue
        program = os.path.basename(tokens[0])
        if program == "cd" and len(tokens) > 1:
            directory = resolve_directory(directory, tokens[1])
        elif program in SHELL_COMMANDS and "-c" in tokens[:-1]:
            reason = check_command(tokens[tokens.index("-c") + 1], directory)
            if reason:
                return reason
        elif program == "eval":
            reason = check_command(" ".join(tokens[1:]), directory)
            if reason:
                return reason
        elif program == "git":
            reason = check_git_tokens(tokens, directory)
            if reason:
                return reason
    return None


def run_hook() -> int:
    if os.environ.get(BYPASS_ENVIRONMENT_VARIABLE):
        return 0
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    reason = check_command(command, payload.get("cwd") or os.getcwd())
    if reason:
        print(f"git-guard blocked this command: {reason}", file=sys.stderr)
        return 2
    return 0


def run_wrapper(arguments: list[str]) -> int:
    if os.environ.get(BYPASS_ENVIRONMENT_VARIABLE):
        return 0
    reason = check_git_tokens(["git", *arguments], os.getcwd())
    if reason:
        print(f"git-guard blocked this command: {reason}", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--hook"]:
        return run_hook()
    if argv[:1] == ["--argv"]:
        return run_wrapper(argv[1:])
    print("usage: git_guard.py --hook | --argv <git arguments>", file=sys.stderr)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
