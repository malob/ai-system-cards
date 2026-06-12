# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-06-11 (~18:15) — v2 is CANONICAL (D28); conversion
converged (gate 0 majors / L1 31 / T1 70; seams 0; build clean). Since then, a
round of **site polish + production set-up**, all render/config-only (no
markdown/gate impact), all committed, **NOTHING PUSHED** (D13):
- **D29** — figures merged into one card per page (multi-panel charts + the
  PDF's repeated running-title strips no longer orphaned);
- **D30** — internal section links dotted-underline, external citations solid;
- TOC "Contents" button toggles the sidebar/drawer at *every* width; header
  meta-row evenly spread (date · Original PDF · Markdown) with clay middots;
- **D31** — social-media previews: per-page Open Graph PNGs via a Satori+resvg
  `og/[...path].png.ts` endpoint, in the site's own fonts/palette;
- Homepage: casual "fair warning" caveat under the lede; card hover-highlight
  given inner padding so text isn't flush to the box edge;
- Footer pinned to the bottom (body is now a flex column) + GitHub contribute CTA;
- **D32** — sitemap (`@astrojs/sitemap`, HTML pages only) + `<link rel=sitemap>`;
  custom `404.astro`; branded § favicon (clay tile) + light/dark `theme-color`.
  robots.txt deliberately skipped (Pages project sub-path — see D32);
- **Astro docs MCP** added (`.mcp.json`, approved + connected) for live-docs
  access (`mcp__astro-docs__search_astro_docs`).
- Favicon hardened: vectorized SVG (§ as a `<path>`, intrinsic size) + PNG /
  apple-touch fallback, after Safari rendered the first `<text>`-based SVG
  favicon inconsistently (D32; `favicon.svg.ts` / `favicon.png.ts`).
- Page markers (`p.N` deep-links) and heading permalink `#` anchors render
  their glyph via CSS (`::before`), not DOM text — so they stay out of text
  selection, copy, Pagefind, and Safari Reader (still visible/clickable, with
  aria-labels).

**Repo is now public/contributor-ready (D33):** MIT `LICENSE`, rewritten README
(Status / Running it / Adding a card / docs pointer), `__pycache__`/`worklist.md`
untracked + gitignored, no secrets in tracked files. Docs flattened to `docs/` and
de-v2'd, CLAUDE.md reframed (D34); removed vestigial `worklist.py`; consolidated the
QA methodology into `docs/verification-methodology.md` (+ a pipeline module map in
CLAUDE.md); trimmed this file's superseded round-by-round tail and marked
`generation-design.md` historical. Owner: **"good to ship."** **Next:** (1) owner
publishes when ready (push `main` → Pages deploy, D13); (2) the pipeline is **heavily
document-specialized** (hard-coded paths, per-card style-manifest, gates tuned to
this card's defects) — likely won't generalize cleanly even to Anthropic's other
cards. **The next milestone is to convert a *second* document and learn whether one
shared pipeline serves all or each needs its own** (D35; supersedes D33's looser
"generalize the `CARD` path" framing). With Fable 5.

## Cold-start capsule

The first attempt converted one card (Claude Fable 5 & Mythos 5, 319 pp, live at
malob.github.io/ai-system-cards) but required so much manual review/repair that the
owner judged the process not worth maintaining. This is a ground-up rebuild whose
goal is: hand over a PDF, the pipeline runs unattended at any token cost, and the
owner certifies the result after a short flag-directed review. The governing idea is
**verification-first** — build and calibrate the thing that says "done" before
rebuilding the thing that generates. Read [charter.md](charter.md) for goal and
principles, [decisions.md](decisions.md) for settled questions,
[design-brief.md](design-brief.md) for the first-attempt retrospective (defect
taxonomy in its §2 is load-bearing), and
[verification-methodology.md](verification-methodology.md) for how output is checked.

## Status

- **Conversion: COMPLETE and canonical (D28).** Card = Claude Fable 5 & Mythos 5
  (319pp). Gate: 0 majors / L1 31 (typed v1-parity) / T1 70 minors; seam
  auditor 0; site builds clean. Verifier still calibrates against git refs
  (`f60899a`/`fb483fb`) — the D5 corpus is intact, not the working tree.
- **Site (Astro → GitHub Pages):** recent features/polish all committed, none
  pushed (D13): figure-card merge (D29), internal/external link underlines
  (D30), all-width TOC toggle, evenly-spread header meta-row with middots,
  per-page social-media OG previews (D31). Astro docs MCP wired (`.mcp.json`).
  OG-image rendering lives in `site/src/lib/og.js` + `site/src/pages/og/`.
- **Open:** nothing blocking. Owner publishes when ready (push `main` triggers
  the Pages deploy). Note: OG previews use absolute `malob.github.io` URLs, so
  they only resolve once deployed — validate then (opengraph.xyz / X composer).
