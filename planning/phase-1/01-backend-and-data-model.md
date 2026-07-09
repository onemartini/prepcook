# Sub-plan 01 — Backend & Data Model

**Owns:** the server that stores moments, talks to SoundCloud, and coordinates annotation/transcription. **Supports assumptions:** A2 (fidelity via SoundCloud resolve), A3 (SoundCloud sufficiency), and is the substrate for A4/A5.

## Stack

- **FastAPI** (async, typed, auto OpenAPI docs — handy for driving the client).
- **SQLite** in dev via SQLAlchemy; schema kept Postgres-portable (UUID PKs, timestamptz-style columns, no SQLite-only types).
- **Pydantic** models for request/response.
- Reuses the existing `.env` setup (`SOUNDCLOUD_CLIENT_ID`, `SOUNDCLOUD_CLIENT_SECRET`) and the resolve/comments logic from `get-soundcloud-comments.py`.
- Single-user for Phase 1 (no real auth); a static API token or localhost-only binding is enough.

## Data model (Phase 1 slice)

Trimmed from the full product data model to only what Phase 1 needs. Fields we don't use yet are omitted rather than stubbed.

```
Track
  id (uuid, pk)
  soundcloud_id (text, unique)        # canonical SoundCloud track id
  permalink_url (text)
  title (text)
  artist (text)                       # SoundCloud "user"/uploader for now
  artwork_url (text, nullable)
  duration_ms (int, nullable)
  raw_metadata (json)                 # full resolve payload, for later mining
  created_at, updated_at

ScrapbookEntry            # "a saved moment"
  id (uuid, pk)
  track_id (fk -> Track)
  position_ms (int)                   # RAW in-track timestamp at keypress — authoritative, never overwritten
  snapped_position_ms (int, nullable) # Tier-1 phrase/section snap suggestion (see below)
  snap_source (text, nullable)        # "waveform" | "comments" | null — how the snap was derived
  effective_position_ms (int)         # what the UI seeks to; = user-chosen (snapped or raw), defaults to raw
  user_note (text, nullable)
  tags (json array of text)
  source_app (text)                   # "chrome-ext" | "ios-share" | "ios-nowplaying-spike"
  capture_method (text)               # "browser-ext" | "share-url" | "nowplaying" — for fidelity comparison
  status (text)                       # "new" | "reviewed"
  created_at, updated_at

VoiceNote
  id (uuid, pk)
  entry_id (fk -> ScrapbookEntry)
  audio_path (text)                   # stored file reference
  transcript (text, nullable)
  transcription_status (text)         # "pending" | "done" | "failed"
  created_at

Annotation
  id (uuid, pk)
  entry_id (fk -> ScrapbookEntry)     # annotate the moment, not just the track
  persona (text)                      # "dj" for Phase 1
  content (json)                      # structured claims (see sub-plan 03)
  model (text)                        # which LLM produced it
  created_at
```

Notes:
- Annotations attach to the **entry**, not the track, because "why *this* moment" depends on the note/voice/timestamp. A per-track dossier can aggregate its entries' annotations later.
- `capture_method` on every entry is deliberate: it lets different capture surfaces (Chrome extension now, iOS mechanisms later) write real entries and be compared for fidelity (A2).
- **The raw `position_ms` is authoritative and immutable.** Snapping only ever proposes `snapped_position_ms`; `effective_position_ms` is what the UI uses and always resolves to a value the user accepted (raw by default). This keeps the keypress truth intact even if the snap is wrong.

## Endpoints (v1)

```
POST /moments
  body: { soundcloud_url | soundcloud_id, position_ms, note?, tags?, source_app, capture_method }
  -> resolves/【upserts】 Track, creates ScrapbookEntry, returns entry + track

GET  /moments            # scrapbook list, newest first, with track summary
GET  /moments/{id}       # full dossier: entry + track + voice notes + annotations

POST /moments/{id}/voice # multipart audio upload -> VoiceNote (transcription async)
GET  /moments/{id}       # (poll) transcript + annotation fill in as they complete

POST /moments/{id}/annotate   # (re)generate annotation; also auto-triggered on create
POST /tracks/resolve          # url -> normalized track metadata (used by client preview)

POST /moments/{id}/snap       # compute Tier-1 snap suggestion (async on create; can re-run)
PATCH /moments/{id}           # set effective_position_ms (accept snap, or nudge ± beat/bar)
```

## SoundCloud service

- Lift `get_access_token`, `resolve`, and `get_comments` out of the root script into a `soundcloud` module with token caching (tokens last ~1h) and retry.
- `resolve` must follow the `302 → /tracks/{id}` redirect we observed during credential testing (requests follows by default; assert we read the final track payload).
- Persist the full resolve payload in `Track.raw_metadata` so A3 (metadata sufficiency) can be analyzed later without re-fetching.
- Comments are fetched lazily and fed to annotation (sub-plan 03), not stored as first-class objects in Phase 1.

## Phrase snapping — Tier 1 (waveform / comments)

Corrects the human reaction-time lag by proposing an earlier, musically-meaningful position. Tier 1 uses only SoundCloud-native signals — **no audio download, no beat detection** (those are Tiers 2–3, gated on A3).

- **Primary signal — waveform.** SoundCloud's resolve payload includes a `waveform_url` (amplitude-sample JSON). **First task: confirm the field is present** in our stored `raw_metadata`. Fetch + cache the samples per track; to snap, scan **backward from `position_ms`** for the nearest strong energy transition (section/drop boundary).
- **Secondary signal — comments.** We already fetch comments (which carry in-track timestamps). A dense cluster near the keypress is a "notable moment" magnet; use it to corroborate or, if no clear waveform edge exists, as the snap target.
- **Bounded look-back.** Only snap to a boundary within a small window before the keypress (e.g. ≤ ~8s, tunable). No confident boundary in-window → leave `snapped_position_ms` null (no snap). Over-correction is worse than a small lag.
- **Output.** Write `snapped_position_ms` + `snap_source`; do **not** touch `position_ms`. `effective_position_ms` stays at raw until the user accepts the snap (via `PATCH`).
- **Timing.** Runs async right after moment creation (like transcription/annotation); the client shows the suggestion when ready. Cache waveform-derived boundaries on the `Track` to make re-snaps and future entries cheap.
- **Nudge.** `PATCH` lets the client move `effective_position_ms` by a coarse step; without a beat grid, "beat/bar" nudges are approximate (fixed ms steps or waveform-edge hops) until Tier 2 provides a real grid.

Tiers 2–3 (stream-based BPM/beat grid, structural phrase boundaries) are **out of scope** here and depend on the A3 outcome; the schema (`snap_source`, cached boundaries) is written so they can slot in later without migration pain.

## Transcription & annotation coordination

- On voice upload: store the file, mark `transcription_status = pending`, kick off transcription (FastAPI `BackgroundTasks` is enough for single-user; no queue yet).
- Transcription provider is pluggable behind an interface (`transcribe(audio) -> text`). Default to a hosted Whisper-class API for speed; local `whisper` remains an option. Keys via `.env`.
- After transcript completes (or immediately if no voice note), trigger annotation (sub-plan 03).

## Config & secrets

- All keys via `.env` / environment (never committed) — matches the existing pattern and the `.env.example` already in the repo. Add `OPENAI_API_KEY` (or chosen provider) and `TRANSCRIPTION_*` entries to `.env.example`.

## Done when

- Can create a moment from a SoundCloud URL + position and read it back with correct track metadata.
- Voice upload produces a transcript asynchronously.
- Annotation is generated and attached.
- A Tier-1 snap suggestion is computed from waveform/comments (or correctly left null), with raw `position_ms` preserved.
- Schema runs on SQLite locally and has no SQLite-only assumptions blocking a Postgres move.
