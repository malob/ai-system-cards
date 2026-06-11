# Overnight judgment calls (2026-06-11, owner asleep — review & revert as wanted)

Owner authorized autonomous work toward max fidelity, with judgment calls
logged for morning review. Each entry: what I decided, why, how to revert.

## J1 — p.198 transcript 6.5.2.B: fixed mono, LEFT the deeper structure
**Decided:** reclassified #f0eee6 boxes as code → the assistant's "Here is my
design" output now renders MONOSPACE (was a serif :::example). Committed
2cc34f0. I did NOT rework the two remaining structural issues:
  (a) the elision note "[The model proceeds to work on the task.]" still
      renders as a `:::turn{role=user}` (blue user bubble) — it is black text
      inside the assistant's #faf9f5 box, a narrator note, not a user message;
  (b) the "Here is my design" mono box sits just OUTSIDE the transcript
      container (the transcript closes on the first non-turn block).
**Why I stopped there:** the faithful structure is ONE assistant turn holding
[thinking-pre][elision note][output-pre] in order. Representing that needs an
ordered-segment turn model (turns today are body-text + a single appended
code_lines, no interleaving). Reworking turn classification — used by all 17
transcripts — unsupervised overnight is too risky for one transcript's sake;
the diff guard can't substitute for eyeballing the whole transcript family.
**Root cause for when you tackle it:** #faf9f5 is mapped to "user" in
TURN_FILLS but is used as the ASSISTANT bubble here (it carries the
[Assistant] label); the label flips the labeled line to assistant, but bare
continuation lines in the same box keep the user default, and the nested
#f0eee6 sub-boxes + flush-on-kind-change split the single assistant turn into
[turn][code][turn][code]. A proper fix: track the enclosing turn-fill box
identity, treat all content within one such box (label + bare lines + nested
mono sub-boxes) as one turn with ordered text/code segments.
**Revert:** `git revert 2cc34f0` restores the serif :::example (worse, but
if you dislike a lone mono box outside the transcript, that's the toggle).
