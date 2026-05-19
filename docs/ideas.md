# Deferred ideas — to revisit after MVP

Each entry has: the **idea**, its **intention / purpose**, and **halfway considerations** — the trade-offs or open questions to think about when this gets picked up again.

This is the parking lot, not a backlog — order doesn't imply priority. When something moves into scoped work, mark it (or move it out).

---

## Low-friction content adding (browser extension)

**Idea:** A browser extension (or share-sheet / bookmarklet alternative) that lets the user one-click add an item they liked to AIFeeder, with an optional "why I liked this" insight field.

**Intention / purpose:** Reduce friction in feeding the app's understanding of what the user finds meaningful. The "why I liked this" capture is the highest-quality personalization signal — far richer than thumbs feedback alone.

**Halfway considerations:**
- Pairs with the *Insights / reflections section* below — the insight has to live somewhere.
- "Adding an item" vs. "following a source" should be distinct primitives — single items are signal, not subscriptions.
- Friction tradeoff: if it requires writing an insight, most users won't use it; if it doesn't, the signal is just a bookmark. Likely optional but framed as the rewarding behaviour.
- Cross-browser story (Chrome / Firefox / Safari) roughly doubles build cost.

---

## AI source-recommender

**Idea:** When the user adds a one-off item from a source they don't follow, the AI scans that source for items that match the user's taste. If items consistently land well in feedback, prompt: "follow this source?"

**Intention / purpose:** Grow the user's source list *intentionally* — not via the "more = better" attitude of mainstream readers. Also a way to compensate for cold-start: users don't know what sources exist that match their "why".

**Halfway considerations:**
- Token-cost guard: don't scan a new source aggressively. Sample a small window, see if matches surface, expand only on positive signal.
- This is a recommender — every recommender failure mode applies (filter bubble, novelty bias, exploration vs. exploitation).
- Clear "no thanks, stop suggesting" affordance required.

---

## Periodic "why" revisits — insight-shift trigger

**Idea:** In addition to feedback-pattern shifts (in MVP), trigger a "why" revisit when the AI detects misalignment between the user's stated "why" and the insights they're writing on saved items.

**Intention / purpose:** Catch comfort-zone calcification — the strict intent-filter risk surfaced in handoff §7.

**Halfway considerations:**
- Depends on the *Insights / reflections section* existing.
- Too many revisit prompts = nag. Cap frequency hard.
- The user might *want* their "why" to be stable; treat drift as a problem only if they confirm.

---

## Insights / reflections section

**Idea:** A section of the app that stores the user's written reflections on content they've engaged with.

**Intention / purpose:** Personalization signal + personal-knowledge benefit. Builds a longitudinal map of what the user found meaningful, and feeds back into "why" calibration.

**Halfway considerations:**
- Overlap with the elaborate library/journal cluster below — these may collapse into one design.
- Privacy posture: insights are diary-like. Default private; opt-in to social.
- Wedge vs. Readwise / Obsidian is the *integration* with the curation loop — reflections close the loop back to the "why".

---

## Social section

**Idea:** Users can friend each other, see each other's reflections on shared items, see what content others enjoy (modulo privacy), see how their taste overlaps.

**Intention / purpose:** Make reflections feel less like solo journaling; create a space for thoughtful conversation around content.

**Halfway considerations:**
- **Direct contradiction risk:** the wedge of this app is *not* being a distracting social media app. Any social layer must be designed adversarially.
- Friend counts, taste-match percentages, notifications — all engagement-bait patterns. Strip them or skip the feature.
- Could be opt-in per-item ("share my reflection on this") rather than profile-level.
- Revisit only after MVP proves the core loop works *without* social proof.

---

## Twitter / non-RSS source support

**Idea:** Ingest from sources without RSS — Twitter being the canonical example.

**Intention / purpose:** Many high-signal sources (researchers, practitioners, niche communities) live on Twitter or platforms without standard feeds.

**Halfway considerations:**
- Twitter API costs and restrictions are hostile to small apps.
- Alternative: nitter / RSS-bridge services — fragile.
- Could outsource to the user: "paste your Twitter list export" or use existing list-archiver tools.

---

## Whisper fallback for YouTube transcripts

**Idea:** When `yt-dlp` can't get captions, fall back to Whisper for transcription.

**Intention / purpose:** Catch the ~5–10% of videos without auto-captions, especially older or non-English content.

**Halfway considerations:**
- Whisper inference per video is non-trivial cost.
- Possible refinement: only run Whisper on items the user explicitly wants summarised (post-click signal), not preemptively at ingestion.

---

## Audio + transcript + thumbnail YouTube mode

**Idea:** Custom in-app YouTube player: audio playback + live transcript + thumbnail. No iframe.

**Intention / purpose:** Avoid the recommendation-surface leak that iframe embeds carry (end-cards, related-video overlays pulling user back into YouTube's algorithm).

**Halfway considerations:**
- Audio-only playback for monetized content is a YouTube ToS gray area.
- Technically much more complex than iframe — not worth it until iframe leak is confirmed as a real user problem (track this in MVP).
- If picked up: "watch on YouTube" escape hatch must remain — both for creators (traffic) and for power users.

---

## Newsletter email forwarding

**Idea:** Give each user a forwarding inbox; they forward newsletters to it; the app ingests them as a source.

**Intention / purpose:** Cover the large category of high-signal content that's email-only.

**Halfway considerations:**
- Email parsing is messy — unsubscribe footers, tracking pixels, HTML soup.
- Hosting cost: per-user inboxes.
- Privacy: forwarded mail can contain unrelated personal info — strict access boundaries needed.

---

## Page-diff ingestion (ChangeDetection.io reference)

**Idea:** Watch a page URL for changes (new posts on a blog without RSS, new sections, etc.).

**Intention / purpose:** Cover RSS-less sites that still have a stable enough structure to diff.

**Halfway considerations:**
- Diffing HTML produces noise — layout changes, ad rotations, footer updates.
- Better than headless-browser ingestion in cost terms, worse in coverage.

---

## Agent-driven headless-browser discovery

**Idea:** For JS-heavy sites with no other ingestion path, an agent uses a headless browser to extract content.

**Intention / purpose:** Last-resort coverage for sites that resist every other ingestion method.

**Halfway considerations:**
- Expensive (browser sessions + agent tokens) — use sparingly.
- Brittle: site changes break the agent's selectors.
- Explicitly de-scoped for MVP minimalism. Only revisit if a critical source can't be covered any other way.

---

## The "v2 cluster" — richer library, journal, intellectual-challenge, quests

**Idea:** A richer personal-knowledge layer on top of the feed:
- **Library** — beyond the simple "read items archive" of MVP: notes, tags, cross-links.
- **Journal** — longer-form reflections, possibly spanning multiple items.
- **Intellectual-challenge recommender** — periodically surface content that contradicts or pressure-tests the user's stated assumptions.
- **Quests** — applied practice prompts based on what the user has consumed.

**Intention / purpose:** Turn consumption into formation. The original ideation arc framed these as the long-term shape of the app; MVP cuts them out to prove the curation loop first. This is where the *value defensibility* likely eventually lives — the feed is the on-ramp; this cluster is the destination.

**Halfway considerations:**
- **Anti-gamification posture is critical** — quests/challenges drift toward streaks and badges, which is the opposite of mindful. If built, build them adversarially.
- Intellectual-challenge needs care: "challenge the user's assumptions" is one slip away from being culture-war engagement bait.
- The library should compose with the *Insights / reflections section* rather than duplicating it.
- May collapse into a single coherent "personal knowledge" surface in design — don't ship the pieces independently.

---

## Content-type-adaptive prompt design

**Idea:** Per-content-format AI prompts (one for debates, one for tutorials, one for philosophical essays, one for narrative pieces, etc.), with the content-type classification routing the input to the right prompt.

**Intention / purpose:** Higher-fidelity summaries by tuning the prompt shape to the content's structure — e.g. for a debate, "Key point 1: X vs. Y" rather than separate pro/con bullets; for a philosophical essay, central-argument emphasis rather than key-points-as-list.

**Halfway considerations:**
- Requires a content-type taxonomy. Start small (3–5 categories) and expand from observed gaps.
- **The right trigger:** revisit this only after watching which content types produce visibly poor summaries with the v1 single general prompt. Those become the priority list.
- Per-type prompts add maintenance overhead — each is its own iteration loop.
- Alternative approach: instead of hand-tuned per-type prompts, feed the LLM a description of the content type and let it produce a tailored summary. Self-adaptive but harder to validate.

**Refs:** decisions.md → *2026-05-20 — Single general AI summary prompt; defer content-type-adaptive prompting*.

---

## Public distribution (auth, multi-tenancy, billing, hosting)

**Idea:** Make AIFeeder available beyond the builder — friends, paying users, public. Requires adding back: user accounts + auth, multi-tenancy on the schema, subscription billing, hosting infrastructure, ToS / privacy policy.

**Intention / purpose:** The mission is broader than one user. If the local v1 proves the curation loop is the wedge, distribution lets others benefit.

**Halfway considerations:**
- **This is weeks of retrofit work** — ~15–25 hours engineering, plus operational setup (Stripe account, domain, SSL, ToS, privacy policy, support inbox).
- **Schema migration is the hard part.** v1 ships a single-user-only schema with no `user_id` columns; multi-tenancy needs careful migration to preserve the builder's data without leaking it across new users.
- **Subscription business model decision reactivates here** — $10–25/mo, no free tier, per the [original decision](decisions.md).
- **Privacy story changes fundamentally.** Local v1 has data only on the user's machine; distribution means user data on someone's servers — training-data posture, export/portability, GDPR if EU users.
- **YouTube ToS posture tightens.** Personal `yt-dlp` use is safer than running it as a service for paying users.
- **Cost telemetry becomes operationally critical** — per-user, per-source attribution at scale, vs. the simple personal tracking in v1.
- **Naming + domain** — "AIFeeder" is the working title; a public-facing name + domain is needed before launch.
- **Cache-sharing across users** rejoins as a real concern (the "1 summary for N users" economics from handoff §6).
- **Pre-condition:** decide whether v1 proved the loop before paying this cost. If thumbs+reasons + per-source "why" don't produce visibly better filtering than mainstream readers, distribution is throwing good money after bad.

**Refs:** decisions.md → *2026-05-20 — Local-only, single-user app for v1*, *~2026-05-19 — Subscription business model from day one*.

---

_Last updated: 2026-05-20 — added [content-type-adaptive prompt design] and [public distribution] following the local-only scope cut._
