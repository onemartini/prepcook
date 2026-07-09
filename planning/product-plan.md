# Prep Cook — Product Plan

A DJ discovery, capture, annotation, acquisition, and preparation system that turns fleeting musical inspiration into a performance-ready library.

> Prep Cook is not just a DJ library manager. It is a musical memory system: capture what moved you, understand why, legally acquire it when needed, prepare it for performance, and let the system learn from your taste over time.

## Core thesis

- **Discovery is broken.** Spotify and SoundCloud recommendations are useful but shallow. DJs need graph traversal, tastemaker signals, recency, comments, reposts, scene context, and personal intent signals.
- **Inspiration is perishable.** The key product moment is "I like this part." Prep Cook should capture the track, timestamp, voice note, and context before the idea disappears.
- **Preparation is fragmented.** DJs discover in one place, buy in another, analyze elsewhere, and prepare in Rekordbox or Serato. Prep Cook can connect the whole chain.

## The full workflow

`Discover → Save moment → Annotate → Recommend → Acquire → Analyze → Cue / loop → Export → Learn`

The scrapbook is the hub. Everything either creates, enriches, or uses scrapbook entries and track dossiers.

## Major product areas

1. **Scrapbook** — Frictionless capture of musical moments from SoundCloud, Spotify, CarPlay, mobile, voice, widgets, and eventually desktop. (Track, timestamp, voice note, tags, source)
2. **Expert annotation** — AI commentary on genre, production, cultural context, musical relatives, DJ utility, loops, and why the user may have saved the moment. Personas: DJ, producer, historian, crate digger, scene insider.
3. **Discovery graph** — Traverse SoundCloud recommendations, reposts, comments, tastemakers, mixes, labels, artists, and user saves. Rank candidates by signals that matter to DJs.
4. **Track dossier** — A living page for every track: annotations, audio analysis, cue points, loops, purchase source, notes, similar tracks, transitions, and usage history.
5. **Acquisition assistant** — Find legal download sources, compare formats and prices, assist purchase/download, import files, dedupe, and attach metadata.
6. **DJ prep** — Generate BPM, key, phrase boundaries, loop candidates, hot cues, memory cues, comments, playlists, and Rekordbox/Mixed In Key-compatible outputs.

## Feature list ranked by implementation difficulty

| Feature | Difficulty | Why |
| --- | --- | --- |
| Scrapbook entries | Very low | Database objects for track, timestamp, note, tags, source, and status. |
| Voice notes + transcription | Low | Standard mobile recording and speech-to-text workflow. |
| Basic AI annotations | Low | LLM-generated commentary from metadata and user notes. |
| Multiple expert personas | Low | Mostly prompt design and structured outputs. |
| Track identification | Low–medium | Metadata integration or audio fingerprinting fallback. |
| SoundCloud-first discovery traversal | Medium | Requires API usage, graph traversal, dedupe, ranking, and careful ToS compliance. |
| Recommendation ranking | Medium | Start heuristic, then use saves/revisits/acquisitions as signals. |
| CarPlay capture | Medium | Very useful surface, but constrained UI and platform review requirements. |
| Action Button / widget capture | Medium | Likely more realistic than wake-word activation. |
| Audio analysis from accessible streams/files | Medium | BPM/key/energy are manageable; phrase quality takes iteration. |
| Loop detection | Medium–high | Good musical loops require structure, beat grid, and taste judgment. |
| Cue point generation | Medium–high | Requires reliable structure detection and DJ-specific heuristics. |
| Rekordbox XML export | Medium–high | Technically feasible but full fidelity and edge cases matter. |
| Acquisition assistant | High | Store-by-store variability, authentication, purchase flow, downloads, and ToS review. |
| Cross-app capture | High | Mobile OS restrictions limit what is possible. |
| Wake-word assistant | Very high | Third-party apps cannot generally provide system-wide always-listening wake words. |
| Transition recommendation engine | Very high | Hard ML/product problem requiring play history and transition outcomes. |
| Personal DJ taste model | Very high | Powerful moat, but needs longitudinal behavioral data. |

## SoundCloud-first validation path

The current strategic decision: prove the front half of the product using SoundCloud before investing heavily in acquisition.

- **Hypothesis** — SoundCloud streaming plus metadata may be enough to validate discovery, capture, annotation, and recommendation.
- **Test** — Use 100 real target tracks. Ask whether streaming access allows BPM, key, phrases, loops, embeddings, and useful annotations.
- **Decision** — If DJs still want to use the scrapbook without owned files, delay acquisition. If they quickly want to play the tracks, move acquisition earlier.

## Phased roadmap

1. **SoundCloud scrapbook MVP** — Save SoundCloud moments, timestamps, notes, voice memos, and basic track metadata. Goal: prove the core capture habit.
2. **Expert annotation layer** — Add DJ, producer, historian, crate-digger, and scene-insider annotations. Goal: make saved moments enjoyable and useful to revisit.
3. **Discovery graph** — Traverse related tracks, reposts, comments, mixes, tastemakers, and labels. Rank by recency, engagement, credibility, and similarity to saved moments.
4. **Audio analysis** — Where audio access is available, generate BPM, key, energy curve, phrase boundaries, and preliminary loop candidates.
5. **Track dossier** — Consolidate all knowledge about a track: annotations, analysis, notes, versions, musical relatives, and saved moments.
6. **Acquisition assistant** — Only after clear need: find legal purchase sources, compare formats, assist download/import, and connect the owned file to the existing dossier.
7. **DJ prep/export** — Generate cue points, loops, comments, playlists, and Rekordbox-compatible exports.
8. **Headless expert** — Voice-first assistant that answers technical and taste questions by traversing the personal music graph.

## Headless expert assistant

A voice-first interface for asking questions about the current track, the user's library, and broader musical context.

- **Track-level questions** — "Why does this groove work?" "Where should I mix in?" "What does this remind me of?"
- **Library-level questions** — "Do I own anything like this?" "What do I usually play after tracks like this?"
- **Scene-level questions** — "Why are new wave edits popular now?" "Which labels are pushing this sound?"

Example graph traversal:

```
Saved moment → Track → Artist → Label → Genre → Similar tracks → User notes → Cue points → DJ sets → Transition history
```

## Core data model

```
Track
  artist, title, versions, source IDs, artwork, duration

ScrapbookEntry
  track_id, timestamp, source_app, user_note, voice_note, tags, created_at

Annotation
  track_id, persona, claim, confidence, source, created_at

AudioAnalysis
  track_id, bpm, key, beat_grid, phrase_boundaries, energy_curve, loop_candidates

CuePoint
  track_id, time, type, label, color, confidence, source

Acquisition
  track_id, store, price, format, purchase_status, file_id

Transition
  from_track_id, to_track_id, mix_point, confidence, source

UserTasteSignal
  action_type, track_id, weight, timestamp
```

## Network effects and moat

- **Personal moat** — The system learns what the user saves, revisits, buys, prepares, exports, and plays. That becomes a taste model generic music services do not have.
- **Community moat** — At scale, Prep Cook can learn which tracks DJs mark, loop, cue, buy, export, and actually use in transitions.

Long-term insight: the valuable dataset is not just "likes." It is **DJ intent**: where people mark cue points, what they buy after discovery, which loops survive, and what gets played.

## Open questions

- How much analysis can be done from SoundCloud streaming within supported terms?
- How often do DJs want to acquire a track immediately after saving it?
- Is CarPlay a meaningful capture surface for real users?
- Which expert persona produces the most "wow" moment?
- What is the minimum useful loop/cue export workflow?
- Which acquisition sources cover the target users' actual buying behavior?

## Suggested beachhead

> Start with SoundCloud-first capture + expert annotation + discovery ranking. Do not start with acquisition, Rekordbox export, or wake-word control unless the SoundCloud MVP proves that users quickly hit the limits of streaming-only workflows.

The first adoption wedge is not "AI prepares your DJ library." It is simpler: **"Never lose a great musical moment again."**
