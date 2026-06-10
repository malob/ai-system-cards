# AI System Cards

Archive of AI-lab system cards converted from PDF to faithful web pages (Astro →
GitHub Pages). v1 shipped one card but was too labor-intensive to maintain; the
current focus is designing **v2 of the conversion pipeline**. README.md describes
the shipped v1 site and layout.

## Orientation — read before working

1. [docs/v2/state.md](docs/v2/state.md) — current status, next actions, cold-start
   capsule. **Always read this first.**
2. [docs/v2/charter.md](docs/v2/charter.md) — v2 goal, principles, roadmap.
3. [docs/v2/decisions.md](docs/v2/decisions.md) — append-only decision log (D1…).
4. [docs/v2-design-brief.md](docs/v2-design-brief.md) — v1 retrospective; its §2
   defect taxonomy is load-bearing. Superseded where decisions.md says so.
5. [docs/markdown-conventions.md](docs/markdown-conventions.md) — v1 transcription
   rules (input to the v2 spec, not gospel).

## Process rules

- **Commit early and often, without asking** — standing authorization from the
  owner (D12). Commit at milestones and decision points so git history is
  queryable; imperative, concise messages.
- **Never push** — pushes happen only on explicit owner request; push to main
  also triggers the Pages deploy (D13).
- **Record decisions in decisions.md when they're made**, not at session end —
  sessions can compact or die at any time. Append-only; supersede, don't rewrite.
- **Rewrite state.md before stopping** or after any milestone. It's a snapshot;
  git and decisions.md are the history.
- **Experiments** live in `docs/v2/experiments/NN-name/` with a README (question,
  method, result, conclusion) and committed scripts — re-runnable from the writeup
  alone.
- **Sub-agent findings must land in files**, never only in conversation.
- **Never clean up v1 artifacts** (`tools/`, `cards/*/*/extracted/`, pre-fix git
  states) — they're the verifier calibration corpus (decision D5).
- **Fresh-session test:** these docs must let a cold session continue correctly.
  If they didn't orient you, fixing them is part of your task.
- **Look at the page when data is ambiguous** (owner-encouraged): per-page
  renders live at `cards/*/*/extracted/pages/p-NNN.png` — Read them to resolve
  anything the structured extraction leaves unclear, and `open` them for the
  owner when discussing a page.
