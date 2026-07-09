# Phase 1 — SoundCloud Scrapbook MVP (Chrome extension validation)

**Goal:** Prove — with a Chrome extension that captures the user's *real* SoundCloud listening — that the core Prep Cook loop is real and valuable, before committing to iOS and its capture surfaces (CarPlay, Action Button, widgets).

The core loop we are testing:

```
Listen (SoundCloud in Chrome) → Save moment (track + timestamp + note + voice) → Enrich (AI annotation) → Revisit → keep doing it
```

We are explicitly **not** shipping this at scale. It is a validation instrument. That framing lets us read the SoundCloud tab's DOM and use rough edges to answer questions cheaply.

---

## Why a Chrome extension first

We considered a SwiftUI macOS app (reusable toward iOS) and system-level "Now Playing" capture. A Chrome extension wins for **validation** because:

- It captures the DJ's **real in-the-wild listening** in their normal SoundCloud tab — not "listen inside our app."
- It gets **exact identity + position** by reading SoundCloud's own player DOM: the current track's **permalink** (→ resolve to the exact track ID, including DJ edits/bootlegs) and the `<audio>` element's `currentTime`. No user OAuth, no undocumented internal API, no fuzzy string matching, no audio fingerprinting (which would misidentify edits as the original).
- It's likely **less work** than a SwiftUI app + embedded-widget bridge.

The cost, stated honestly:

- **It does not port to iOS.** iOS Chrome has no extensions; Safari extensions can't do this. The extension validates *product value* and *desktop ambient capture* cheaply, but the **iOS capture mechanism remains a separate, unsolved bet** (see sub-plan 04).
- **Browser-tab only** — it sees SoundCloud in Chrome, not the SoundCloud native app. We must measure how much real listening is in-browser.

The risk of validating on a surface that doesn't port is proving the wrong thing. We mitigate by (a) tying every workstream to a named, measurable assumption below, and (b) keeping the backend and annotation layer platform-agnostic so only the thin capture client is Chrome-specific.

---

## Key assumptions (this is the point of Phase 1)

Each assumption has: what we believe, how we measure it, what would kill or pivot it, and **where it is validated** (build slice + sub-plan). This table is the canonical traceability index — sub-plans point back here.

| # | Assumption | Belief | Signal / metric | Kill / pivot trigger | Validated in |
|---|-----------|--------|-----------------|----------------------|--------------|
| **A1** | Capture habit | DJs will repeatedly capture moments if friction is low | Moments saved per active week; median time-to-save from intent to confirmation | Novelty spike then zero; save takes so long people give up | Slice 1 starts, Slice 2–3 over the trial (sub-plan 02) |
| **A2** | Capture fidelity | We can capture the right track + in-track timestamp reliably | % of moments with correct track and timestamp within ±2s | Extension DOM read is flaky, or the iOS-capture spike (sub-plan 04) finds no viable mobile path | Slice 1 desktop (sub-plan 02); Slice 3 iOS bet (sub-plan 04, Part B) |
| **A3** | SoundCloud sufficiency | SoundCloud API + metadata is enough to identify and enrich moments without owning files | % of target tracks resolvable; metadata + comment completeness | A large share of real target tracks are unresolvable or metadata-poor | Slice 1 resolve (sub-plan 01); partial early probe via Tier-1 snap (sub-plans 01/02) |
| **A4** | Annotation value | AI annotation turns a saved moment into something worth revisiting | User rating of annotations; revisit rate of annotated vs. bare moments | Annotations feel generic; no lift in revisit | Slice 2 (sub-plan 03) |
| **A5** | Voice as input | Voice notes lower friction and capture *why* the moment mattered | % of moments with a voice note; transcript usefulness | Nobody uses voice; transcripts add no signal | Slice 2 (sub-plans 02 + 01) |
| **A6** | Retention | The scrapbook habit persists past novelty | Week-2 return + continued saving | Saving stops after week 1 | Slice 2–3 over the trial (scrapbook/dossier in sub-plan 02) |
| **A7** | Capture coverage | Enough real listening happens where we can capture it | % of listening sessions in-browser (Chrome) vs. native SoundCloud app | Almost all real listening is in the native app, so the extension misses the moments that matter | Slice 3 (sub-plan 04, Part A) |

The Chrome extension makes A2 nearly free **on desktop**. The residual A2/A7 risk — and the whole iOS capture question — lives in sub-plan 04.

---

## The capture mechanic (decided)

Full detail in [`02-chrome-extension-client.md`](./02-chrome-extension-client.md) (Chrome extension client) and [`04-capture-mechanics-spike.md`](./04-capture-mechanics-spike.md) (coverage + iOS bet).

- **Trigger:** a keyboard shortcut, **`Ctrl+Shift+S` (Windows/Linux) / `Cmd+Shift+S` (macOS)** via the MV3 `commands` API ("S = save the moment"). Chosen over a wake word for reliability and latency; users can remap at `chrome://extensions/shortcuts`. (`commands` fire only while Chrome is focused, which is fine since they're listening in Chrome.)
- **On trigger:** the content script reads the current track permalink + `audio.currentTime` **at the instant of the keypress**, so the saved position matches the part they liked — note/tags/voice are added after, never blocking the capture.
- **Phrase snap (Tier 1):** to correct reaction-time lag, the backend proposes an earlier, musically-meaningful position from SoundCloud's **waveform data** (and comment clusters) — a one-tap "snap to section start" suggestion. The raw keypress timestamp stays authoritative; snapping only ever suggests. Richer beat/phrase snapping (Tiers 2–3) needs stream audio analysis and is gated on A3.
- **Voice + wake word:** voice notes via `getUserMedia` (offscreen doc / popup) are in scope (A5). An always-listening **wake word is feasible *in-Chrome*** (persistent offscreen document + on-device engine like Porcupine) and is an optional hands-free experiment layered on top of the hotkey — but it is **not** system-wide and does **not** port to iOS.

---

## Architecture overview

```
┌─────────────────────────────────┐         ┌──────────────────────────────┐
│  Chrome extension (MV3)          │  HTTPS  │  Python backend (FastAPI)     │
│  - content script: read SC tab   │ ──────▶ │  - SoundCloud service         │
│    (permalink + audio.currentTime)│        │  - Moments / tracks store     │
│  - Cmd/Ctrl+Shift+S save trigger  │        │  - Annotation service (LLM)   │
│  - popup: scrapbook + dossier     │        │  - Transcription service      │
│  - voice notes (getUserMedia)     │ ◀────── │  - SQLite (dev) → Postgres    │
│  - (opt) wake word (offscreen)    │  JSON   │                               │
└─────────────────────────────────┘         └──────────────────────────────┘
```

- **Client:** thin Chrome MV3 extension — the only Chrome-specific part.
- **Backend:** Python/FastAPI — reuses the existing SoundCloud/comments scripts and the `.env` credential setup already in the repo. Platform-agnostic, so an iOS client later talks to the same API.
- **Storage:** SQLite for dev, schema Postgres-portable.

---

## Sub-plans

1. [`01-backend-and-data-model.md`](./01-backend-and-data-model.md) — FastAPI service, SoundCloud integration, storage, the Phase-1 slice of the data model.
2. [`02-chrome-extension-client.md`](./02-chrome-extension-client.md) — the Chrome extension: content-script capture, `Cmd/Ctrl+Shift+S` trigger, popup scrapbook/dossier, voice notes, optional wake word.
3. [`03-ai-annotation.md`](./03-ai-annotation.md) — single-persona AI annotation, inputs (metadata + note + transcript + SoundCloud comments), structured output.
4. [`04-capture-mechanics-spike.md`](./04-capture-mechanics-spike.md) — capture-coverage measurement (A7) and the **still-unsolved iOS ambient-capture bet** (Now Playing / play-history / share sheet).

---

## Suggested sequencing

Three build slices, front-loading the fastest path to a usable loop:

1. **Slice 1 — Walking skeleton.** Backend: create/list moments + SoundCloud resolve. Extension: content-script read of the SoundCloud tab + `Cmd/Ctrl+Shift+S` writing a real moment. End state: hit the shortcut while playing a track and see a moment with correct track + timestamp. Proves A2 (desktop), starts A1.
2. **Slice 2 — Make it worth revisiting.** Voice notes + transcription (A5) and single-persona AI annotation (A4). Popup scrapbook list + track dossier (A6).
3. **Slice 3 — Keep us honest.** Coverage instrumentation (A7) and the iOS-capture spike (sub-plan 04); optional in-Chrome wake-word experiment.

Slices 1–2 are the product; Slice 3 is de-risking that can run in parallel once the backend exists.

---

## Explicitly out of scope for Phase 1

Acquisition assistant, Rekordbox/Serato export, cue/loop generation, discovery graph traversal, multi-persona annotation, transition/taste models, and any iOS/CarPlay/widget/share-sheet work. Deep audio analysis (librosa/openl3/demucs) is deferred unless the SoundCloud-sufficiency test (A3) says we need owned files — including Tier 2–3 beat/phrase snapping (only Tier 1 waveform/comment snapping is in scope). A system-wide (non-Chrome) wake word is out — the plan's difficulty ranking still holds for anything beyond the browser.

---

## What "Phase 1 succeeded" looks like

A DJ, after a week, is still saving moments without prompting; the saved moments are correct (A2); the annotations make them want to reopen entries (A4); we know how much of their real listening we can actually reach (A7); and we have a data-backed read on whether an iOS capture surface is viable. At that point we design Phase 2 (expert annotation layer) and the iOS client with evidence instead of guesses.
