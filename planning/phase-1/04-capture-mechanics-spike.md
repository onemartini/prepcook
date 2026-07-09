# Sub-plan 04 — Capture Coverage & the iOS Capture Bet

**Owns:** the two questions the Chrome extension can *not* answer on its own — **A7 (coverage)** and the still-unsolved **iOS ambient-capture** mechanism. The extension gives high-fidelity capture *inside Chrome*; this sub-plan measures how much that matters and what a mobile capture surface could be.

This is a **measurement + research spike, not a shipped feature.** Its output is data and a go/no-go read for iOS, not polished UX.

## Part A — Coverage (A7): does enough listening happen where we can capture it?

The extension only sees SoundCloud in a Chrome tab. If DJs mostly listen in the native SoundCloud app (desktop or mobile), the extension misses the moments that matter.

Measure, per validation user over the trial:
- **In-browser share:** fraction of SoundCloud listening time that happens in Chrome (where we can capture) vs. native apps / other browsers.
- **Missed-moment reports:** a lightweight "I wanted to save something but couldn't" signal, to size the gap the extension leaves.
- **Instrumentation source:** the extension already emits a per-session "SoundCloud tab active/playing" signal (sub-plan 02); pair it with a short listening-habits interview.

Read:
- **Good** — enough real listening is in-browser that the extension validates the loop honestly.
- **Warning** — heavy native-app usage; the desktop extension under-samples real behavior, so weight the iOS bet (Part B) more heavily.

## Part B — The iOS capture bet (does not port from the extension)

The Chrome extension proves nothing about iOS capture. iOS has no Chrome extensions and restricted Safari extensions, so a mobile capture surface is a separate design. Candidate mechanisms, to research and prototype-test (not necessarily build in Phase 1):

### B1 — Share sheet from the SoundCloud app
- User shares the current track to Prep Cook from the SoundCloud iOS app.
- **Identity:** the shared URL resolves to the exact track (clean, like the extension's permalink read).
- **Position:** the share sheet does **not** include in-track position — likely lost, or requires manual entry. This is the key weakness to evaluate.

### B2 — Now Playing (MediaRemote) + SoundCloud query
- iOS "Now Playing" gives current title/artist + elapsed time system-wide.
- **Position:** from elapsed time. **Identity:** fuzzy from title/artist, OR upgraded via a SoundCloud query (below).
- On iOS, MediaRemote is private/restricted for third-party apps — a real shipping blocker, unlike the macOS validation case. Evaluate feasibility honestly.

### B3 — SoundCloud play-history for identity (verified constraints)
Querying SoundCloud for what the authorized user just played can supply exact identity to pair with a local position:
- Requires **user-authorized OAuth** (`authorization_code` + PKCE), not the app-only `client_credentials` we use today.
- **Verified during planning:**
  - `/me` with an **app token → HTTP 502** (no user context) → user OAuth is required.
  - `/me/play-history/tracks` on the **public** `api.soundcloud.com` → **`unknown route`, HTTP 405** → play-history is **not** on the documented public API; it lives on the internal `api-v2.soundcloud.com`.
- Implication: depending on an **undocumented internal endpoint** — powerful (exact track ID) but **ToS-sensitive and liable to change.** Verify a user-authorized token can read it, and how quickly it reflects the current play.

## What we measure for the iOS bet

Against the ~100 real target tracks (the SoundCloud-sufficiency set, including messy DJ edits), for each candidate mechanism:
- **Identity hit rate** on the DJ-edit long tail (share-URL / play-history / Now-Playing string match).
- **Position availability & accuracy** — can we get in-track position at all, and within ±2s?
- **Friction** — steps from moment to saved entry on mobile.
- **Shippability** — App Store / API / ToS blockers per mechanism.

## Go / no-go for iOS

- **Go** if at least one mechanism yields correct identity on the long tail **and** a usable position **and** is shippable (share-sheet + optional manual position is a plausible floor).
- **Pivot** if position is the blocker → consider an owned in-app player on iOS (the SoundCloud widget in a `WKWebView`, the Model-A idea) as the mobile capture surface, accepting "listen in our app" on mobile.
- **No-go (ambient on iOS)** if nothing resolves identity + position acceptably → mobile capture is constrained to share-sheet/manual, which reshapes the product's mobile promise.

## Risks / notes

- **ToS & fragility:** play-history is internal/undocumented; document exactly what we'd call and treat any dependency as provisional.
- **User OAuth scope:** `authorization_code` + PKCE and token refresh are net-new vs. current credentials.
- **Private OS APIs:** MediaRemote is a validation-only crutch on macOS and is not sanctioned for shipping iOS apps.

## Done when

- We have measured in-browser coverage (A7) with a written read.
- We have a comparison table of iOS capture mechanisms (identity / position / friction / shippability) on the ~100-track set and a written go / no-go / pivot recommendation for the iOS client.
