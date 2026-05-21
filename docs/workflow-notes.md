# Working with Claude — workflow notes

A living reference for collaborating effectively with Claude Code on this project. Add to this file as we discover new patterns worth keeping. The goal is to build muscle memory for the practices below, not to memorise the docs.

---

## Core file layout

| File | Question it answers | Lifetime | Edited by |
|---|---|---|---|
| `CLAUDE.md` | What rules / conventions always apply here? | Persistent, slow-changing | You + Claude, deliberately |
| `docs/state.md` | Where are we *right now*? | Mutable, refreshed at session boundaries | Claude, via `/state` |
| `docs/conversation/<date>_<id>.md` | How did we get here? | Append-only per-session log | Claude, every turn (per CLAUDE.md) |
| `docs/decisions.md` | *Why* did we choose X over Y? | Append-only, cross-referenced to ideas.md + session log | Claude, when a real decision lands |
| `docs/ideas.md` | What did we defer, and why? | Append-only; entries promoted out or expanded | Claude, when scope cuts happen |
| `docs/workflow-notes.md` *(this file)* | How do I work with Claude well? | Living reference | You + Claude |

`state.md` is the "where" file, `conversation/` is the "how we got here" file, `decisions.md` is the "why" file, `ideas.md` is the "what we didn't do (yet)" file. They don't overlap; each catches a different failure mode of working with an LLM.

**decisions.md ↔ ideas.md are deliberately bidirectional.** A decision to defer is also an entry in ideas.md; a decision to pick approach A over B should link to the deferred B in ideas.md. The cross-reference convention is mandated in [`CLAUDE.md`](../CLAUDE.md#decisions-log).

---

## Design decision spectrum (A/B/C split)

A framework for which decisions you weigh in on vs. which Claude makes autonomously. Lets you "own" the product without getting bogged down in every library pick.

### A — you decide (Claude always escalates)

Anything that shapes user experience or product identity. If Claude assumes here, it'll get it wrong because these reflect *your* values, not engineering best-practice.

- Mission alignment (mindful, not engagement-bait)
- UX / UI / flow decisions, empty states, screen-level interactions
- Features in/out of scope
- AI behaviour (prompts, output shape, tone, ambiguity handling)
- RAG / retrieval / context strategy
- Model placement (cloud vs. local, provider choice)
- Privacy posture
- Cost-vs-quality tradeoffs
- Content-type handling
- Mission-vs-pragma tensions (e.g. iframe leaking YouTube recommendations)

Logged in [`docs/decisions.md`](decisions.md).

### B — Claude decides, briefs you (you can override)

Routine engineering choices with sensible defaults. Claude makes the call, surfaces it inline as a `**Engineering choice:** <what + why + main alternative>` one-liner. You can silently approve, comment, or push back.

- Language / framework / library picks
- Schema structure (unless it touches scope — that escalates to A)
- Project layout, file organisation, naming conventions
- Error handling / retry strategies (unless UX-visible)
- Logging, testing approach, build tooling
- Specific library versions, dep management

Logged in [`docs/engineering-decisions.md`](engineering-decisions.md). Includes silent approvals and pushbacks-with-resolutions both.

### C — Claude just does (no briefing)

- Variable / function names, code style
- Internal patterns (when to extract a helper, when to inline)
- Auto-formatter, linter config
- Anything reversible in 5 minutes

Not logged anywhere — captured implicitly in git history.

### Pre-session checklist (you run on yourself)

A 90-second pre-flight before a build session. Catches "I forgot to tell you X":

1. **Mission check.** Anything in this session that risks the mindful posture? Anything that should not feel TikTok-like?
2. **UX check.** New screen / interaction / empty state / error message? You have a take?
3. **AI behaviour check.** Any prompt being written or changed? Want to see it before Claude runs it?
4. **Scope check.** Anything Claude might "naturally" add that you actually want deferred?
5. **Cost / privacy check.** Anything that changes what data goes where, or what costs more?
6. **Mission-vs-pragma tension.** Any place we're trading mission purity for build speed? Worth surfacing now?

If anything fires, tell Claude up front. If nothing fires, say "go" and Claude executes with B-category briefings as they land.

### Escalation rule

If Claude's about to make a B-category choice and it turns out to touch any A-category dimension → escalate. Don't pre-commit to an engineering pattern that locks in an A-category answer.

---

## Slash commands

Slash commands are saved prompts at `.claude/commands/<name>.md`. When you type `/<name>` (optionally with arguments), the file's body becomes the prompt sent to Claude. Use them to bake repeated workflows into a single keystroke.

A slash command is just a prompt template — it doesn't carry tools, permissions, or auto-invocation. It runs in the main conversation like anything else you type.

### Active in this project

| Command | Purpose |
|---|---|
| `/state` | Update `docs/state.md` based on the current session. |
| `/resume` | Cold-start a session by reading CLAUDE.md + state.md + recent conversation log. |
| `/decide <decision>` | Pose 2–3 options + tradeoffs for a decision. No implementation. |
| `/plan-feature <task>` | Plan an implementation before writing code. |
| `/log <note>` | Manually append an out-of-band note to the current session's conversation log. |

### When to add a new one

If you find yourself typing the same prompt twice — "review my branch", "summarise test failures", "draft a commit message that follows the style in this repo" — turn it into a slash command. Cheap to make, instant payoff.

---

## Skills (built-in)

Skills are different from slash commands in two important ways:

1. **They're discoverable.** Each skill has a description Claude reads at session start. When your message looks like a fit, Claude can invoke the skill *on its own* — you don't have to type `/<name>`.
2. **They can carry capabilities.** A skill can define its own tools, scripts, sub-agents, and structured instructions — not just a prompt body. Built-in skills are richer than anything you'd write as a slash command.

Mental model: slash commands = "*you* fire this prompt." Skills = "*Claude* knows when this is relevant and follows its instructions." Most skills can also be triggered manually with `/<skill-name>`.

### Useful built-in skills

| Skill | What it does | When to use |
|---|---|---|
| `/init` | Generates a starter `CLAUDE.md` from your codebase. | Once this project actually has code worth describing. |
| `/review` | Reviews a pull request or branch. | Before opening or merging a PR. |
| `/security-review` | Security audit of pending changes. | Before merging anything that touches auth, input handling, secrets, or deps. |
| `/simplify` | Reviews changed code for reuse, quality, efficiency; offers fixes. | After Claude writes a non-trivial chunk of code. |
| `/loop` | Runs a prompt on a recurring interval. | Polling a CI run, watching a deploy, repeatedly running a check. |
| `/schedule` | Cron-style scheduled remote agents. | Recurring automated tasks (daily report, weekly cleanup). |
| `/fewer-permission-prompts` | Scans transcripts and auto-allowlists safe tool calls. | After your first real coding session, to cut prompt fatigue. |
| `/claude-api` | Auto-invoked when you work with the Anthropic SDK. | If AIFeeder ends up using the Claude API — relevant for this project. |
| `/update-config` | Modifies `settings.json` — permissions, hooks, env vars. | When you want hooks, permissions, or env vars changed. |

Skills you don't need to think about: Claude auto-invokes the right one when relevant. Worth scanning the list once just so you know what's possible.

---

## Hooks

Hooks run shell commands on Claude Code lifecycle events. They're how you get *real* automation — CLAUDE.md and memory only influence what Claude tries to do, hooks influence what *happens* in the harness.

Events worth knowing:

- `Stop` — fires when Claude finishes responding. Good for logging, syncing, post-turn checks.
- `PreToolUse` / `PostToolUse` — run before / after a tool call, with optional matcher (`Write|Edit`, `Bash`, etc.). Good for auto-formatting, linting, or blocking unsafe operations.
- `PreCompact` / `PostCompact` — fires around context compaction. Good for forcing a state.md update *before* losing nuance, or reloading critical files after.
- `SessionStart` — fires when a new session opens. Good for showing a "where we left off" summary.
- `UserPromptSubmit` — fires when you hit send. Good for routing or augmenting prompts.

Hooks can be `command` (shell), `prompt` (LLM check), `agent` (subagent runs), `http` (POST to a URL), or `mcp_tool` (call an MCP server). Most of the time you want `command`.

---

## Per-turn logging: hook → main Claude *(May 2026)*

Originally a `Stop` hook spawned a Haiku call (`claude -p`) to read the JSONL transcript and append a per-turn entry. Two problems killed it:

1. **Non-deterministic CLI crash.** `claude -p` crashed during init ~50% of the time with `TypeError: Cannot read properties of null (reading 'effortLevel')` — inside Claude Code's minified bundle. No flag combination defeated it reliably. A 5-attempt retry loop masked the failures but didn't fix them.
2. **Wrong-exchange picks.** Even when the call succeeded, Haiku had to read a >500 KB transcript it didn't participate in and guess "the most recent exchange." It sometimes picked the wrong one — the model that *had* the intent was main Claude, not the one writing the log.

Now: main Claude writes entries directly via `Write` / `Edit` as the last action of every turn. [`CLAUDE.md`](../CLAUDE.md)'s *Conversation log* section spells out the file-path and seed-header convention. Tradeoff: no automated safety net — relies on Claude remembering. Worth it for higher-quality entries (full intent in context) and zero CLI flakiness.

General pattern: prefer in-context work over delegating to a headless model when the in-context model has strictly more information. Hooks are still the right tool for *deterministic* automation (formatters, linters, gate checks) — just not for tasks that depend on understanding intent.

Decision detail in [`conversation/2026-05-20_b670.md`](conversation/2026-05-20_b670.md).

---

## State.md + /compact workflow

`/compact` summarises older messages to free context. Auto-fires when context fills; you can also run it manually with a hint: `/compact preserve all decisions about the auth refactor`.

The risk: summaries lose nuance. The pattern that mitigates it:

1. **Prime `state.md` at the start of a session** with `/resume`, so the load-bearing context is in a *file*, not just in conversational context.
2. **Refresh `state.md` at natural pauses** with `/state` — end of a feature, before switching topics, before stepping away.
3. **When context gets heavy**, run `/compact <hint>` with explicit preservation instructions.
4. **After compaction**, ask Claude to re-read `state.md`. Reloads what matters.
5. **If you can tell something important got lost**, open the relevant session file in `docs/conversation/`, find the entry, paste it back into chat. The append-only log is your audit trail.

The append-only `conversation.md` + the mutable `state.md` form a deliberate split: the log preserves *everything* (low signal, complete), state captures *what currently matters* (high signal, lossy).

---

## Subagents

Subagents are isolated Claude instances spawned for one task. Their context doesn't pollute the main thread; only their summary comes back.

**Good fits:**

- Broad codebase search (>3 queries to find something) — use the `Explore` subagent
- Independent parallel investigations (e.g. "audit unused endpoints" + "check deps for CVEs" in parallel)
- Second-opinion reviews — they haven't seen Claude's reasoning, so the read is genuinely independent
- Long noisy tasks producing a short answer — main thread gets the punchline, not 200 grep hits
- Risky isolated changes — run in a git worktree so the main checkout stays clean

**Avoid for:**

- Simple one-file edits
- Anything where you want to see the thinking happen
- Tasks where Claude already has all the context loaded

Subagents start cold. Brief them like a smart colleague who just walked into the room.

---

## Tutor mode

Defined in `CLAUDE.md`. Claude watches the conversation for opportunities to improve how I work — missed slash commands, missed plan mode, decision blind spots, prompt friction, follow-through gaps — and surfaces them as one-per-turn `💡 Tutor note:` blocks at the end of relevant responses. Silence is fine; most turns won't have one.

Purpose: I'm intentionally building these collaboration skills, so I want feedback in-flight rather than discovering gaps after the fact. The notes should be specific to *what just happened*, not generic advice.

When a tutor observation reflects a *durable* new practice, Claude also updates this file (and says so in the note). One-off tips stay in conversation only.

**Toggle:** say "tutor off" / "pause tutor mode" to silence for the session. Remove the section in CLAUDE.md to disable permanently.

## Plan mode

For non-trivial implementations, ask Claude to plan first — or use `/plan-feature`. Claude lays out the approach without touching files. Cheap to redirect a bad plan, expensive to undo bad code. Default to plan mode whenever the task crosses ~30 lines of intended changes or touches >2 files.

---

## Parallel sessions

Running multiple Claude Code sessions against this codebase concurrently breaks two assumptions: that the conversation log is a single thread, and that `docs/state.md` has one writer. Two patterns, picked by whether the work is branch-divergent:

**Option A — Per-session conversation files, shared `state.md`** *(default — same-checkout parallel work)*

```
docs/
  conversation/
    2026-05-19_360d_workflow-setup.md
    2026-05-20_b1c2_ingestion-design.md
    2026-05-20_d4e7_auth-refactor.md      ← parallel to b1c2
  state.md                                ← canonical, single source of truth
```

Filename pattern: `<date>_<short-session-id>[_<topic-slug>].md`. Each Claude session writes to its *own* per-session file (per CLAUDE.md's *Conversation log* section), so concurrent sessions never collide on the log — routing is automatic, no hook required. `state.md` stays singular and is the real hazard: concurrent `/state` runs from two sessions can clobber each other. Serialise — have one session finish `/state` before the other starts.

**Option C — Git worktrees** *(deferred — for branch-divergent feature work)*

```bash
git worktree add ../AIFeeder-auth feature/auth
# run a separate Claude Code session inside the new worktree
```

Each worktree has its own checkout — and its own `.claude/` and `docs/`. No conflicts; merge by merging the branch. Use this when the parallel work is on an independent feature branch rather than a different concern within the same checkout. The tutor has a triggered reminder in [`CLAUDE.md`](../CLAUDE.md) to surface this distinction when a second session starts.

## Memory system

Claude maintains a persistent memory directory (separate from this project's `docs/`). It stores facts *about you* — your role, preferences, recurring corrections — across conversations. Auto-managed: Claude writes to it when it learns something durable. Force a save by saying "remember that …". Force a forget by saying "forget that …".

This is *not* a replacement for `state.md` or `conversation.md`. Memory is about *you and how you work*; state and conversation are about *this project*.

---

## What's implemented in this project

| Practice | Status | Where |
|---|---|---|
| `CLAUDE.md` with conversation-log instruction | ✅ | [`CLAUDE.md`](../CLAUDE.md) |
| Per-turn conversation logging by main Claude (was: Stop hook + Haiku) | ✅ | [`CLAUDE.md`](../CLAUDE.md) — *Conversation log* section |
| Per-session conversation files in `docs/conversation/` (Option A) | ✅ | [`docs/conversation/`](conversation/) |
| `/state` slash command | ✅ | [`.claude/commands/state.md`](../.claude/commands/state.md) |
| `/resume` slash command | ✅ | [`.claude/commands/resume.md`](../.claude/commands/resume.md) |
| `/decide` slash command | ✅ | [`.claude/commands/decide.md`](../.claude/commands/decide.md) |
| `/plan-feature` slash command | ✅ | [`.claude/commands/plan-feature.md`](../.claude/commands/plan-feature.md) |
| `/log` slash command | ✅ | [`.claude/commands/log.md`](../.claude/commands/log.md) |
| `docs/state.md` | ✅ | [`docs/state.md`](state.md) |
| `docs/decisions.md` | ✅ | [`docs/decisions.md`](decisions.md) |
| `docs/ideas.md` | ✅ | [`docs/ideas.md`](ideas.md) |
| `docs/workflow-notes.md` (this file) | ✅ | [`docs/workflow-notes.md`](workflow-notes.md) |
| Tutor mode (in-flight collaboration coaching) | ✅ | [`CLAUDE.md`](../CLAUDE.md) — *Tutor mode* section |

---

## Practice cues

A few habits that turn the setup above into actual leverage:

- **Start sessions with `/resume`** — even short ones. Five seconds of orientation, big payoff.
- **End sessions with `/state`** — even if it feels unnecessary. The cost of an empty update is zero; the cost of *not* updating is a stale state.md.
- **When in doubt, plan first.** Default to `/plan-feature` over jumping into code.
- **Use `/decide` before any choice you'd later second-guess** — schemas, naming, architecture, build tooling.
- **Drop a `/log` for thoughts you don't want to act on yet** — half-formed ideas, things to revisit, "we should think about X later." Don't let them die in your head.
- **When Claude proposes something surprising, say so explicitly** — that's how memory gets useful feedback signal.
