---
description: Append a manual note to the current session's conversation log
argument-hint: <the note to record>
---

Append a note to the current session's conversation log file (`docs/conversation/<YYYY-MM-DD>_<short-id>.md`, the same file the Stop hook is writing to — find the newest file in that directory whose short-id matches this session). Use the format in `CLAUDE.md`'s *Conversation log* section, but use `**Note:**` instead of the `**Me:**` / `**Claude:**` structure. Note content:

$ARGUMENTS

Use the current timestamp (`YYYY-MM-DD HH:MM`) in the entry header. Append only; do not modify earlier entries. This is for out-of-band thoughts I want preserved without spinning up a full exchange.
