# Overnight judgment calls (2026-06-11, owner asleep — review & revert as wanted)

Owner authorized autonomous work toward max fidelity, with judgment calls
logged for morning review. Each entry: what I decided, why, how to revert.

## J1 — p.198 transcript 6.5.2.B — RESOLVED (was deferred; owner steered it the next morning)
**Final state (all committed):**
- Mono: #f0eee6 boxes reclassified as code → the assistant's "Here is my
  design" output renders MONOSPACE (2cc34f0). Owner confirmed mono is faithful
  — all 11 #f0eee6 boxes are RobotoMono in the PDF; the "mono here vs serif
  earlier" is the source's own split (mono code-boxes, serif prose), which we
  reproduce (font-faithfulness, D26-consistent).
- Interjection: a turn whose whole joined body is a single bracketed sentence
  (inner >30 chars, no internal ']') reclassifies to `commentary` → renders as
  plain inter-turn narration, like the gray narration in the #f3f3f3
  transcripts on p.40-41 (6b4004e). The `[^\]]` guard excludes real turns that
  merely start/end with `[…]` pills (06d regression caught + fixed pre-commit).
- Output placement: a code box nested in a turn/transcript fill box keeps
  ::::transcript OPEN, so the mono output sits INSIDE the transcript instead of
  stranded before the caption (d7953ab). Standalone code (§9.2 blocklist) is
  unaffected.
**Result:** p.198 = one transcript — assistant mono thinking card → plain
"[The model proceeds…]" narration → mono output — caption after. DOM- and
screenshot-confirmed; gate 0/31/69 (T1 improved as the interjections aligned
better as commentary). The earlier "ordered-segment turn model" worry was
avoided: the bracket signal + in_transcript flag scoped it tightly (only 06g
changed).

## p.118 "error: gh…" turn — RESEARCHED, NOT the same class (left as-is)
Owner asked me to confirm before folding it in. It is a literal tool-error
string ("error: gh is currently not allowed on devspaces/devboxes…") in black
Lora at the TOP of the box, the input the assistant responds to — NOT a
bracketed `[…]` editorial interjection. So it's out of scope for the J1
commentary rule (which requires whole-body `[…]`). Rendering it as an
input/user turn is defensible (it's not the assistant speaking). Left
unchanged; flag for a future "unlabeled input/tool-output turn" pass if ever
wanted.
