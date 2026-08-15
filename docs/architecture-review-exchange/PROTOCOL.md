# Architecture review exchange protocol

This directory is a mailbox for a truth-seeking architecture debate between two
models that share this repository.

## Roles

- **A / maintainer:** the Codex task that proposed the refactor.
- **B / reviewer:** the independent second-opinion model.

A writes only under `maintainer/`. B writes only under `reviewer/`. Neither model
edits, deletes, renames, or amends the other model's messages.

During the debate, neither model changes production code, generated card content,
project documentation outside this exchange directory, git history, or remotes.
Architecture experiments require a separate explicit phase after the debate agrees
that they are warranted.

## Message format

Each message is a new Markdown file:

- A: `maintainer/A0001-short-subject.md`, then `A0002-...`, and so on.
- B: `reviewer/B0001-short-subject.md`, then `B0002-...`, and so on.

Never overwrite a sent message. Correct it with a later message.

Begin every message with:

```text
From: A or B
Message: A0001 or B0001
In-reply-to: message ID, or NONE
Phase: CLEAN-ROOM | PROPOSAL-REVIEW | DEBATE | EXPERIMENT | FINAL
Status: CONTINUE | BLOCKED | SETTLED
```

Use the stable fact, inference, uncertainty, and claim IDs established in earlier
messages. Quote only the minimum needed; cite repository files and lines directly.

## Order of play

1. B reads `maintainer/A0000-clean-room-request.md` and performs the independent
   review. B must not read the section headed `The architecture hypothesis to review`
   in `docs/architecture-review-brief.md` until after sending B0001.
2. B writes `reviewer/B0001-clean-room-report.md` and then watches `maintainer/` for
   A0001.
3. A reads B0001, reveals and defends the proposal in A0001, explicitly conceding any
   clean-room findings that already defeat part of it.
4. B replies in B0002. A replies in A0002. Continue without an arbitrary round cap.

The recipient should poll its inbound directory periodically while its session is
active. A is also attached to a recurring Codex heartbeat that checks for new B
messages. B should use an equivalent monitor if its environment supports one;
otherwise it should remain active and poll.

## Epistemic rules

The objective is the truest diagnosis and best design—not consensus or compromise.

- Stand by a claim while its evidence and reasoning remain stronger.
- Concede promptly when defeated, naming exactly what changed the conclusion.
- Steelman before disagreeing.
- Do not split the difference. A hybrid wins only if it is independently best.
- Do not repeat old arguments as a new round. Add evidence, a causal argument, a
  counterexample, a changed premise, or an experiment.
- Persistent disagreement is a reason to sharpen or test a claim, not to average it.
- Keep facts, predictions, engineering preferences, and owner value choices separate.

For each consequential disagreement, use:

```text
Claim ID:
Strongest opposing case:
Position:
Evidence/reasoning:
What would change my mind:
Discriminating experiment:
```

## When a claim is finished

A claim leaves active debate only when one of these is true:

1. both models support the same conclusion for compatible reasons;
2. one model explicitly concedes and records what convinced it;
3. a discriminating experiment decides it; or
4. required evidence is unavailable, so the claim is explicitly deferred as
   unresolved rather than compromised.

`Status: SETTLED` means all load-bearing claims satisfy one of those conditions. It
does not mean the models manufactured a shared midpoint.

If either model needs an owner decision about values or authorization for a
meaningful experiment, it writes `Status: BLOCKED` and asks one precise question in
its own mailbox. The user should not need to relay ordinary debate messages.
