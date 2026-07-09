# Sub-plan 02 — Chrome Extension Capture Client (MV3)

**Owns:** the thing a DJ actually touches while listening. **Supports assumptions:** A1 (capture habit / friction), A2 (fidelity on desktop), A5 (voice), A6 (retention), and delivers the surface for A4 (revisiting annotations).

A thin Manifest V3 extension. The backend and annotation layer are platform-agnostic; only this client is Chrome-specific.

## Components

- **Content script** on `soundcloud.com` — reads the player, executes the capture.
- **Main-world injected script** (`world: "MAIN"`) — reaches the page's `<audio>` element / player state that the isolated content-script world can't see directly.
- **Service worker (background)** — owns the `commands` shortcut, talks to the backend, manages auth/config.
- **Popup** — scrapbook list + moment dossier + capture confirmation + voice recording.
- **Offscreen document** (optional) — persistent mic for the wake-word experiment.

## Capture mechanic (the core)

- **Trigger:** MV3 `commands` entry, default **`Ctrl+Shift+S` / `Cmd+Shift+S`** ("save the moment"). Remappable at `chrome://extensions/shortcuts`. Fires only while Chrome is focused — fine, since the user is listening in Chrome.

```json
"commands": {
  "save-moment": {
    "suggested_key": { "default": "Ctrl+Shift+S", "mac": "Command+Shift+S" },
    "description": "Save the current SoundCloud moment"
  }
}
```

- **Identity:** the content script reads the footer player's current-track `<a>` **permalink** (e.g. `/artist/track-slug`). The backend resolves it to the exact SoundCloud track ID — this correctly captures **DJ edits/bootlegs**, which fingerprinting would misidentify as the original.
- **Position:** read the page `<audio>` element's `currentTime` (float seconds → ms) via the main-world script **at the instant the shortcut fires**. Fallback: parse the visible elapsed-time element (second granularity) if the media element isn't reachable.
- **Save flow:** shortcut → capture `{permalink, position_ms}` immediately → POST to `/moments` (`source_app: "chrome-ext"`, `capture_method: "browser-ext"`) → show a lightweight confirmation (toast in-page or popup) where note/tags/voice can be added. **Never block the capture on the note or network** — snapshot first, enrich after.

## Phrase snap refinement (Tier 1)

Corrects the "pressed slightly too late" problem without changing what was captured.

- The raw keypress `position_ms` is captured and shown **immediately**; the backend computes a `snapped_position_ms` async (waveform/comments — sub-plan 01) and the UI surfaces it when ready.
- In the confirmation toast / dossier, show the suggestion as a **one-tap accept** ("snap to section start −2.3s"), never auto-applied silently. Accepting sends a `PATCH` setting `effective_position_ms`; the raw value stays intact and reversible.
- **Nudge control** in the dossier: step the marker earlier/later. Without a beat grid these are approximate (fixed steps / waveform-edge hops); it upgrades to true beat/bar snapping only if Tier 2 lands.
- If no confident boundary was found, show nothing — no empty "snap unavailable" noise.

## Resilience to SoundCloud DOM changes

- Prefer stable signals: the media element's `currentTime` and the track permalink `href` change less than styling classes.
- Wrap DOM reads in defensive selectors with a couple of fallbacks; log a "capture-failed" event (feeds A2 monitoring) rather than failing silently.
- Keep all SoundCloud-specific selectors in one module so a markup change is a one-file fix.

## Voice notes (A5)

- Record via `getUserMedia` from the popup (or offscreen doc), triggered from the capture confirmation or added later to an existing moment.
- Upload to `POST /moments/{id}/voice`; transcript + annotation fill in asynchronously — the popup shows "transcribing…/annotating…" and updates on poll.
- One click to start / one to stop; friction here directly affects A5.

## Optional: in-Chrome wake word (experiment, not required)

- Persistent **offscreen document** holding a `getUserMedia` stream + an on-device wake-word engine (e.g. **Picovoice Porcupine** WASM). Wake word runs locally; only after detection do we capture + transcribe.
- Constraints to remember: works **only while Chrome is open**, shows a persistent mic indicator, and does **not** port to iOS. Layer it on top of the hotkey; the hotkey stays the primary trigger.
- Same "timestamp at detection instant" rule applies — capture position when the wake word fires, not when the spoken note ends.

## Scrapbook & dossier (A6, surfaces A4)

- **Scrapbook list** (popup or a full extension page): artwork, title/artist, position timestamp, note preview, relative time, status. Newest-first; simple tag/text filter.
- **Dossier view:** the full moment — a link/deep-link back to the SoundCloud track at `position_ms`, the AI annotation (sub-plan 03), voice-note transcript, note, tags. This is where A4 ("worth revisiting") is felt; make it feel good, not like a form.

## Capture friction budget (A1)

The most important UX metric is time from "I like this part" to a confirmed save:

- Shortcut → moment captured with sensible defaults in **≤ 2 seconds**, note/voice optional and addable later.
- Capture locally and POST in the background; reconcile on failure.

## Instrumentation

Emit lightweight events (save latency, saves/day, capture-failed rate, voice-note attach rate, dossier reopen rate) to the backend, feeding the assumption metrics. Also emit a per-session signal for **A7 coverage** (was a SoundCloud tab active/playing?) — see sub-plan 04.

## MV3 permissions (minimal)

- `commands` (shortcut), host permission for `soundcloud.com` (content script), `scripting` (main-world injection), `storage` (config/token). `offscreen` + mic permission only if the wake-word experiment is enabled. No broad `<all_urls>`.

## Out of scope for the client

iOS/CarPlay/widgets/share-sheet (Phase 2+ and a separate capture bet — sub-plan 04). Audio fingerprinting and tab-audio capture (`tabCapture`) are not needed for SoundCloud identity; `tabCapture` is only a future option if we want the raw stream for audio analysis (A3).

## Done when

- Pressing `Cmd/Ctrl+Shift+S` while a SoundCloud track plays in Chrome creates a correct moment (right track incl. edits, position within ±2s).
- Voice notes record, upload, and show a transcript.
- A phrase-snap suggestion appears when available and can be accepted/nudged, with the raw capture preserved.
- The popup shows the scrapbook and a dossier with the annotation and a seek-back link to the moment.
