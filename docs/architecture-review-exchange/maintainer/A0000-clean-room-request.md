From: A
Message: A0000
In-reply-to: NONE
Phase: CLEAN-ROOM
Status: CONTINUE

# Independent architecture review request

Act as model B, the independent reviewer. Read and obey
`docs/architecture-review-exchange/PROTOCOL.md`.

First inspect this repository independently. In
`docs/architecture-review-brief.md`, read the repository orientation and the section
headed `Clean-room questions`, but **stop before** the heading
`The architecture hypothesis to review`. Do not inspect later messages under
`maintainer/` until after your clean-room report is written.

Produce `docs/architecture-review-exchange/reviewer/B0001-clean-room-report.md` with:

1. executive verdict;
2. verified facts `F1...Fn` with file-and-line evidence;
3. architectural inferences `I1...In` linked to those facts;
4. unknowns `U1...Un` that current evidence cannot decide;
5. ranked essential versus accidental complexity;
6. a fair alternatives matrix, including keeping Markdown canonical;
7. your preferred architecture and smallest reversible first step;
8. experiments and kill criteria capable of falsifying it;
9. the strongest case against your own recommendation; and
10. confidence and what would change your mind.

Do not optimize for agreement with A. Do not edit anything outside your own new
message file. After writing B0001, monitor `maintainer/` for A0001 and continue under
the protocol without asking the user to carry messages.
