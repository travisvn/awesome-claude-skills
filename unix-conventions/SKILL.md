---
name: unix-conventions
description: Reviews CLI tools, shell scripts, C programs, and man pages against POSIX, GNU Coding Standards, and Unix philosophy — flags violations with exact fixes.
---

# Unix Conventions

Enforces code and documentation against three canonical Unix standards: *The Art of Unix Programming* (ESR), POSIX (IEEE Std 1003.1), and the GNU Coding Standards. Covers option syntax, exit codes, stream usage, error message format, shell script hygiene, C program correctness, and man page structure.

> **Claude Code only.** Clone [agiacalone/unix-conventions](https://github.com/agiacalone/unix-conventions) and run `./install.sh`, which copies the skill and reference documents to `~/.claude/skills/unix-conventions/`.

## When to Use This Skill

- Reviewing a CLI tool for option, exit code, or stream convention violations
- Auditing a shell script for portability and correctness issues
- Checking a C program's error handling and resource management
- Writing or reviewing a man page
- Evaluating a tool's design against Unix philosophy

## What This Skill Does

1. **Loads targeted references** — pulls only the documents relevant to the task (POSIX, GNU, TAOUP, man page conventions) rather than applying everything at once
2. **Resolves standard conflicts explicitly** — POSIX and GNU disagree on several points (`-h`, long options, shebang, `printf` vs `echo`); the skill asks rather than silently picking one
3. **Reports violations in a structured format** — every finding includes location, what was found, what was expected, and an exact fix
4. **Applies the Worse is Better design lens** — flags tradeoffs between implementation simplicity and interface elegance during design reviews

## How to Use

### Basic Usage

```
Review this shell script against Unix conventions
```

```
Does this CLI tool follow POSIX option conventions?
```

### Advanced Usage

Per-project preferences can be set in a `.unix-conventions` file at the project root to resolve conflicts between standards without being prompted each time:

```
# .unix-conventions
standard = gnu          # gnu | posix | ask
shebang = bash          # bash | sh | ask
echo_or_printf = printf # printf | echo | ask
worse_is_better = yes   # yes | no | ask
```

## Example

**User**: "Review fetch-taoup.sh against Unix conventions"

**Output**:
```
WARNINGS

VIOLATION: echo_or_printf = printf
LOCATION:  fetch-taoup.sh:28
FOUND:     echo "fetch-taoup: $*" >&2
EXPECTED:  printf output to stderr with program name prefix
FIX:       printf 'fetch-taoup: %s\n' "$*" >&2

VIOLATION: echo_or_printf = printf
LOCATION:  fetch-taoup.sh:43
FOUND:     echo "fetch-taoup: warning: could not parse..." >&2
EXPECTED:  printf for all diagnostic output
FIX:       printf 'fetch-taoup: warning: could not parse chapter order from index.html, falling back to filename order\n' >&2
```

**Inspired by:** Eric S. Raymond's *The Art of Unix Programming*, the GNU Coding Standards, and Richard P. Gabriel's "Worse is Better"

## Tips

- Set `standard = posix` for tools that must run on macOS, OpenBSD, or musl-based systems; set `gnu` for Linux-only tools
- Set `worse_is_better = yes` in projects that prioritize implementation simplicity — the skill will flag over-engineered designs
- The skill only loads references relevant to the task — you won't get man page rules when reviewing a shell script

## Common Use Cases

- Auditing scripts in a new repo before publishing them
- Reviewing student or junior developer CLI tools against established conventions
- Ensuring a new tool composes cleanly in pipelines (Rule of Silence, filter pattern)
- Writing man pages that follow the canonical section order and macro conventions
