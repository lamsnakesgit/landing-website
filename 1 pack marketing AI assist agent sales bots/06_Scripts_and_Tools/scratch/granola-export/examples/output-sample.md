# Sample output

This is what a single rendered meeting Markdown file looks like after running `extract.py`. The content below is **fully synthetic** — fake names, fake topics, made-up doc IDs — so you can preview the format before you run the script against your own data.

Each meeting becomes one file at `meetings/YYYY-MM-DD_HHMM_<title-slug>_<id-prefix>.md`. Plus a master `INDEX.md` that lists everything sorted chronologically.

---

```markdown
# Quarterly review: rough numbers

- **Date:** 2025-09-12T14:00:00.000Z
- **ID:** `00000000-aaaa-bbbb-cccc-dddddddddddd`
- **Type:** meeting
- **Workspace:** 11111111...
- **Valid meeting:** yes
- **Audio file (server-side, not downloadable):** `<user-id>/00000000-AAAA-BBBB-CCCC-DDDDDDDDDDDD.m4a`
- **Status:** ready
- **Created via:** auto_calendar
- **Calendar:** Quarterly review (2025-09-12T14:00:00-07:00)
- **Public:** False

## Attendees

- Alex Researcher <alex@example.org>
- Pat Manager <pat@example.org>
- Sam Engineer <sam@example.org>

## My Notes

- Headline: revenue tracking ahead of plan
- Need to dig into the cohort numbers next quarter
- Action: schedule deep-dive with Sam

---

## AI Summaries

### Summary (template: `default-summary`)

#### Key Decisions

- Continue with the current quarterly review cadence
- Prioritise the cohort analysis Sam proposed for next quarter

#### Open Questions

- What does the underlying retention curve look like at the 90-day mark?
- How are competitors handling this in the same segment?

#### Suggested follow-up questions

- What are the leading indicators we should track between now and next quarter's review?
- Who owns the cohort deep-dive and by when?

---

## Transcript

`14:00:12` **[MIC]** Alright, thanks everyone for joining. Let's start with the headline numbers.
`14:00:18` **[SYS]** Sounds good. Want me to share my screen?
`14:00:22` **[MIC]** Yeah, please.
`14:00:31` **[SYS]** Okay so as you can see we're tracking ahead of plan on the top-line, but the breakdown by segment is where it gets interesting.
`14:00:45` **[MIC]** Right. The mid-market piece looks healthy.
`14:00:51` **[SYS]** It does. Enterprise is the one I want to dig into more.
...
```

---

## Notes on the format

- **`[MIC]` = your microphone, `[SYS]` = system audio** (the other participants, captured via ScreenCaptureKit / Core Audio Taps). Granola preserves this distinction at the API level, and the export keeps it. Useful for filtering "things I said" vs "things they said".
- **`audio_file_handle`** is recorded for traceability but the file itself is **not retrievable** — Granola's API has no audio download endpoint (their own desktop app cannot replay either).
- **AI Summaries** are rendered from ProseMirror JSON. Most accounts only have one panel per meeting (the default summary template), but custom panel templates appear here too.
- **`original_content` / suggested questions / user_feedback** appear if present on the panel — when an AI summary has been edited by the user, the original AI version is preserved and shown alongside.
- **Filenames are slug-safe**: whitespace (including embedded newlines from occasional AI-generated multi-line titles) is collapsed to hyphens, and the doc ID prefix disambiguates same-titled meetings.

## INDEX.md format

The master index has one line per meeting, sorted chronologically:

```markdown
# Granola Export — Meeting Index

Total: **N** documents extracted on YYYY-MM-DD HH:MM

Legend: `[M]` valid meeting · `[T]` transcript · `[S]` AI summaries

- 2025-09-10 09:30 `[MTS]` [Engineering standup](2025-09-10_0930_engineering-standup_aaaaaaaa.md)
- 2025-09-10 14:00 `[MTS]` [Customer call: Acme Inc](2025-09-10_1400_customer-call-acme-inc_bbbbbbbb.md)
- 2025-09-11 11:00 `[M-S]` [Strategy sync](2025-09-11_1100_strategy-sync_cccccccc.md)
...
```

Each row's flags tell you at a glance whether the meeting has a real transcript (`T`), AI summary (`S`), and was classified as a valid meeting (`M`) by Granola itself.
