# Sub-plan 03 — AI Annotation Layer (single persona)

**Owns:** turning a bare saved moment into something worth reopening. **Supports assumption:** A4 (annotation value). This is the deliberately-included slice of the plan's Phase-2 "expert annotation" idea, kept minimal.

## Scope

- **One persona for Phase 1: the DJ.** Multi-persona (producer, historian, crate-digger, scene-insider) is Phase 2. One good voice beats five shallow ones for testing A4.
- Annotation attaches to the **ScrapbookEntry** (the moment), not just the track, so it can speak to *why this part* using the note, voice transcript, and timestamp.

## Inputs

Assemble a context bundle per moment:

- **Track metadata** — from `Track.raw_metadata` (title, artist/user, genre tags, description, duration, play/like counts).
- **The moment** — `position_ms` (and its human timestamp), user note, tags.
- **Voice transcript** — if present (sub-plan 01/02).
- **SoundCloud comments near the timestamp** — reuse the existing comments fetcher; comments carry in-track `timestamp` values, so we can surface what other listeners said *right around this moment*. This is a cheap, high-signal, SoundCloud-native input and a nice tie-in to existing code.

## Output (structured)

Return JSON, not prose, so the client can render it well and we can evaluate it:

```json
{
  "summary": "one or two sentences on what this moment is",
  "why_it_might_matter": "read on why the user may have saved THIS part",
  "genre_and_style": ["..."],
  "production_notes": "texture/arrangement observation tied to the timestamp",
  "dj_utility": "how a DJ might use this (intro/outro/loopable section/energy shift)",
  "similar_touchpoints": ["loose reference points, clearly labeled as guesses"],
  "confidence": "low | medium | high",
  "caveats": "what the model is unsure about"
}
```

- Every claim should be honest about uncertainty — `confidence` and `caveats` are first-class, because a confidently-wrong annotation kills A4 faster than a hedged one.
- Keep `similar_touchpoints` explicitly labeled as guesses; do not fabricate specific track IDs.

## Mechanics

- Provider behind a pluggable `annotate(context) -> Annotation` interface; default to a hosted LLM, key via `.env` (`OPENAI_API_KEY` or chosen provider).
- Triggered automatically after moment creation (and after transcript completion, so voice context is included), plus a manual `POST /moments/{id}/annotate` to regenerate.
- Store `model` used and the raw structured output in `Annotation.content` for later evaluation.

## Evaluating A4

- In-app thumbs up/down (or 1–5) on each annotation → simple quality signal.
- Compare **revisit rate** of moments with vs. without a satisfying annotation.
- Qualitative: sit with a DJ and ask "did this tell you something true and useful about *your* moment?"

## Out of scope

Multiple personas, cross-track synthesis ("what do you usually play after this"), and any claim requiring audio analysis we haven't built (BPM/key/phrases) — unless A3 shows SoundCloud metadata already carries it. Annotations should lean on metadata + comments + the user's own note/voice, not invented audio facts.

## Done when

- Creating a moment yields a structured DJ annotation within a few seconds.
- Annotations incorporate the user's note/voice and nearby SoundCloud comments when available.
- The client can render it and collect a quality rating.
