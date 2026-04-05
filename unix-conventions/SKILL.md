---
name: unix-conventions
description: Use when reviewing or writing CLI tools, shell scripts, C programs, man pages, --help output, or error messages. Also use when writing documentation or explanations for a Unix/hacker audience, or when the user asks if something "follows Unix conventions" or "Unix philosophy".
---

# Unix Conventions

## Overview

Honor Unix tradition in code, documentation, and design. Five canonical sources:

- *The Art of Unix Programming* (ESR) — the 17 Rules; the philosophy behind why Unix works
- POSIX — option syntax, exit codes, streams; the portable baseline every Unix tool must meet
- GNU Coding Standards — error format, standard options, shell scripting; what GNU tools actually do
- "Worse is Better" (R.P. Gabriel) — when implementation simplicity beats interface elegance
- The Jargon File — hacker vocabulary and lore; how to write for an audience that groks the tradition

## Task Dispatch

| Task | References to load |
|------|--------------------|
| Review CLI tool (options, exit codes, streams) | `cli-conventions.md`, `taoup-principles.md` |
| Review shell script | `cli-conventions.md`, `gnu-coding-standards.md` |
| Review C program | `gnu-coding-standards.md`, `cli-conventions.md` |
| Write or review man page | `man-page-format.md` |
| Review `--help` / `--version` output | `cli-conventions.md`, `gnu-coding-standards.md` |
| Unix philosophy / design review | `taoup-principles.md`, `worse-is-better.md`, `jargon-lore.md`, `jargon-terms.md` |

Load only the references needed for the task. All references are in the `references/` subdirectory of this skill.

## Configuration

Load preferences in this order (highest to lowest precedence):

1. `.unix-conventions` in the project root
2. `~/.config/unix-conventions/config` (user config)
3. Skill defaults — ask

Read whichever files exist and merge them, with higher-precedence files winning. If a setting is `ask` or absent in all files, follow the conflict rules below.

## Conflicts Between Standards

POSIX, GNU, and TAOUP disagree on these points. **Do not assume — ask the user** unless the config file resolves it.

| Conflict | POSIX | GNU | Resolution |
|----------|-------|-----|------------|
| `-h` option | Not reserved; tools use it for domain purposes (e.g., human-readable) | Reserved strictly for `--help` | Ask: is `-h` for help or domain use? |
| Long options | Not defined | Required alongside short options | Ask: require long options, optional, or none? |
| Options after operands | First non-option ends option parsing | Freely permuted | Ask: POSIX strict or GNU permutation? |
| Shebang | `#!/bin/sh` for portability | `#!/bin/bash` when bash features used | Ask: must it be portable to non-bash? |
| `printf` vs `echo` | Both defined; `echo` behaviour varies | Prefer `printf` | Ask: portability requirement? |
| C indentation | Not specified | 2 spaces | Ask: gnu, kr (8-space tabs), or linux? |
| `error()` function | Not defined | Recommended when on glibc | Ask: glibc-only acceptable? |

When a conflict arises during review and no config setting covers it, stop and ask:

> "This touches a conflict between [standard A] and [standard B]: [describe the conflict].
> Which do you prefer, or should I note it as a warning without favoring either?"

Do not silently pick one. Do not assume GNU because it is more common.

## Checklists

### CLI Tool

1. Option syntax: POSIX short (`-x`), GNU long (`--foo`), clustering, `--` terminator
2. Exit codes: 0=success, 1=error, 2=misuse
3. Streams: errors → stderr, data → stdout, never reversed
4. Error format: `progname: description` (lowercase, no period)
5. `--help`: correct format, exits 0
6. `--version`: correct format, exits 0
7. Reserved options: `-h/--help`, `-V/--version`, `-v/--verbose`, `-q/--quiet`, `-n/--dry-run`
8. Rule of Silence: silent on success by default; no chatty progress output unless `-v`
9. Unix philosophy: does one thing, composes via stdin/stdout

### Shell Script

1. Shebang: `#!/bin/sh` for portable, `#!/bin/bash` only when bash features are used
2. `set -euo pipefail` present
3. All variable expansions quoted: `"$var"`, `"$@"`, `"${var}"`
4. Command substitution uses `$()` not backticks
5. Error messages go to stderr, include script name
6. Temp files via `mktemp`, cleaned up with `trap ... EXIT`
7. No parsing of `ls` output; use globs
8. Exit codes correct

### C Program

1. All system call return values checked
2. Error messages: `progname: description` format
3. `progname` set from `argv[0]` (path stripped)
4. No resource leaks: file descriptors, memory, temp files
5. Signal handling: SIGINT, SIGTERM handled gracefully
6. Option parsing handles `--` terminator

### Man Page

1. Sections present in canonical order: NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXIT STATUS, FILES, ENVIRONMENT, EXAMPLES, SEE ALSO
2. NAME: one line, `\-` separator, lowercase description, no period
3. SYNOPSIS: program bold, meta-variables italic, brackets for optional, ellipsis for repeatable
4. OPTIONS: each in its own `.TP` block
5. EXIT STATUS: all non-zero codes documented
6. SEE ALSO: section numbers in parens, alphabetical, comma-separated
7. Style: third person, present tense, terse

### `--help` / `--version`

1. `Usage:` line with uppercase meta-variables (`FILE`, `DIR`, `NUM`)
2. Two-column option list, `-h`/`-V` listed last
3. Bug report contact at end
4. Exits 0

### Worse is Better Design Review

Controlled by the `worse_is_better` config key (`yes | no | ask`, default: `ask`).

- `yes` — always apply this lens; flag any design that favors interface elegance over implementation simplicity
- `no` — skip this checklist entirely
- `ask` — when a design tradeoff arises where the two approaches diverge, stop and ask: "This is a Worse is Better tradeoff: [describe it]. Apply the lens, skip it, or note it as informational?"

When applying the lens:

1. **Implementation simplicity** — if two designs differ in implementation complexity, prefer the simpler one even if its interface is slightly more awkward
2. **Edge cases pushed out** — are unusual inputs rejected cleanly (error + exit 1) rather than handled with complex internal logic?
3. **Completeness last** — are missing features documented limitations rather than half-implemented handlers?
4. **Not a bug excuse** — correctness violations (unchecked return values, reversed streams, wrong exit codes) are bugs, not tradeoffs

When a design decision pits interface elegance against implementation simplicity, note it explicitly:

> "DESIGN NOTE: [option A] is simpler to implement; [option B] is cleaner to use. Worse is Better favors [option A]."

### Jargon File

The Jargon File is a cultural resource, not a ruleset. Use it for:

- **Vocabulary:** When writing docs, comments, or explanations, reach for the right hacker
  term. "Crufty", "kludge", "elegant", "hairy" — these carry precise meaning to Unix people
  and communicate more than a generic description would.
- **Analogies:** When explaining why a design pattern is good or bad, a Jargon File analogy
  can make it immediately recognizable. A Unix person who hears "cargo cult programming" or
  "creeping featurism" understands instantly.
- **Lore:** When writing for an audience of hackers, cultural touchstones (foo/bar, the Great
  Worm, ITS, the hacker ethic) create shared context and signal that the author knows the
  tradition.

Use `jargon-terms.md` for design vocabulary and `jargon-lore.md` for cultural references.
For anything not covered there, `documentation/jargon.md` has the full text. Don't invent
entries or use terms you're not confident about — the Jargon File is authoritative.

## Reporting Format

```
VIOLATION: [rule or convention name]
LOCATION:  [file:line or section]
FOUND:     [current state]
EXPECTED:  [correct state]
FIX:       [exact correction]
```

Group by severity: **errors** (must fix) → **warnings** (should fix) → **suggestions** (consider).

## Tone

Direct and technical. Show the corrected form; don't handwave. The Unix tradition values
correctness and terseness over diplomacy — a bletcherous interface is bletcherous whether
or not its author intended it. Name things accurately.
