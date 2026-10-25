---
name: conversation-handoff
description: Save a local, dated handoff digest of every Claude Code conversation for a project. Reads the session transcripts in the project's Claude Code projects folder and writes one markdown digest per session (each user request with the turn's outcome) plus an index. Use when the user asks for a handoff, a record of past sessions, a summary of earlier work, or a way to resume work from earlier sessions. Output stays local.
license: see repository LICENSE
---

# Conversation handoff

## Quick start (for small local models)

1. Find the project's Claude Code projects folder. Pass it as `--projects-dir`.
2. Choose a dated output folder.
3. Run `python scripts/extract_sessions.py --projects-dir <dir> --out-dir <out>`.
4. Open the `README.md` index in the output folder. Check the counts.

Creates local digests of session transcripts. The digests let a new session or
a new agent pick up the work without re-reading full transcripts.

## Where the transcripts are

Claude Code stores one folder per project under `~/.claude/projects/`. The
folder name is the project path with separators replaced. Find yours by
listing that folder and matching the project's name. Pass that folder as
`--projects-dir`. The script has no default path.

## Run

```bash
python scripts/extract_sessions.py \
  --projects-dir "<claude-projects-dir>/<project-slug>" \
  --out-dir "outputs/<YYYY-MM-DD>/conversation_handoff"
```

Use the current date for `<YYYY-MM-DD>`. The script uses only the standard
library. Python 3.10 or later.

## Output

- `README.md` in the output folder: index with first and last event times,
  request counts, and links.
- `session_<id8>.md` per session: each human request with its timestamp and the
  last assistant text of that turn.

## What is kept and dropped

- Kept: human request text (capped), the turn's final assistant text (capped),
  timestamps, and transcript size.
- Dropped: tool results, sidechain (subagent) records, and system wrappers
  such as system reminders and injected browser instructions.
- Subagent and tool-result folders are not read.

## Rules

- Write only to the dated output folder.
- Digests can contain pasted content, file paths, and personal details.
  Keep them local. Do not publish them.
- The current session's file is still growing. Re-run to refresh it.
- Check the index counts against the session you expect before you report.
