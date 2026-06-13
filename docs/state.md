# Project state

Rewritable snapshot of where the project stands. **Read this first.** Rewrite it
freely before any stopping point — history lives in git and decisions.md, not here.

**Last updated:** 2026-06-11 (~21:30) — v2 is CANONICAL (D28); conversion
converged (gate 0 majors / L1 31 / T1 70; seams 0; build clean). Since then, a
round of **site polish + production set-up**, all render/config-only (no
markdown/gate impact), now **SHIPPED** — pushed to `main` and deployed live
(D13, on owner request 2026-06-11):
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
- TOC's Footnotes entry hidden while sidenotes replace the footnote list
  (`c87647c`, pushed + deployed 2026-06-11 eve).
- **Deploy workflow bumped to Node 24 action releases** (checkout v6,
  pnpm/action-setup v6, setup-node v6, upload-pages-artifact v5,
  deploy-pages v5) ahead of GitHub's 2026-06-16 node24 default flip;
  actionlint-clean, `d7c7a76`, **pushed + deployed 2026-06-11 eve on owner
  authorization (D13)** — run 27394439921 green, **0 annotations on both jobs**
  (previously 1 Node-20 deprecation warning each), site 200.

**Repo is now public/contributor-ready (D33):** MIT `LICENSE`, rewritten README
(Status / Running it / Adding a card / docs pointer), `__pycache__`/`worklist.md`
untracked + gitignored, no secrets in tracked files. Docs flattened to `docs/` and
de-v2'd, CLAUDE.md reframed (D34); removed vestigial `worklist.py`; consolidated the
QA methodology into `docs/verification-methodology.md` (+ a pipeline module map in
CLAUDE.md); trimmed this file's superseded round-by-round tail and marked
`generation-design.md` historical; cleaned `cards/*/*/extracted/` to only the live-process
inputs — moved the figure-extraction script to `pipeline/generate/extract_figures.py` and
removed dead v1 dumps/scripts (D36, narrowing D5). Owner: **"good to ship."** **Next:** (1) owner
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
- **Site (Astro → GitHub Pages):** recent features/polish all committed **and
  pushed/deployed** (D13): figure-card merge (D29), internal/external link underlines
  (D30), all-width TOC toggle, evenly-spread header meta-row with middots,
  per-page social-media OG previews (D31). Astro docs MCP wired (`.mcp.json`).
  OG-image rendering lives in `site/src/lib/og.js` + `site/src/pages/og/`.
- **Shipped 2026-06-11:** pushed `main` → `74f4fd9`; Pages deploy succeeded; **v2
  is live** at malob.github.io/ai-system-cards (replacing the v1 line). Verified
  live: homepage / card / `og/home.png` all 200; OG previews now resolve (fair to
  validate via opengraph.xyz or an X/Slack link).
- **Post-ship fix (pushed + deployed 2026-06-11, `7f0cdbf`; verified on the live
  site in real Chrome):** sidenote placement on wide screens. Clustered
  footnote refs (p.302 `[^74][^75][^76]`) overprinted; the placement pass now (a)
  skips `display:none .fnref-shim` refs (table-only footnote shims measured at 0 →
  their bogus offset poisoned the de-collision cascade and piled every note at the
  scroll position — the "weird" regression) and (b) sorts notes by measured position
  before stacking colliders (+14px). Verified in real Chrome on the production build:
  72 notes, 0 overlaps, max drift 202px. Render-only. Then closed the pre-existing
  wide-width gap: table-only footnotes (3/4/11/28/29 — referenced only via hidden
  `.fnref-shim`s) had no sidenote while `section.footnotes` is hidden ≥1500px, so their
  text was invisible there; the sidenote builder now also anchors notes to the visible
  in-table `sup.fn-html` links (notes append to `.doc`). Verified: 77 notes, 0 overlaps,
  all five at drift 0 beside their tables; prose cluster unchanged.
- **Search reworked (committed, unpushed):** owner found unquoted literal phrases
  ("most forms of world-class") didn't surface. Cause: the whole card is ONE
  Pagefind page, so the CLI index yields a single result whose sub-results list
  any-word matches in document order (everything matches "of").
  `site/scripts/pagefind-index.mjs` (replaces `pagefind --site dist` in the
  build script) now indexes **one record per h2–h6 section** (252 records;
  heading text searchable; urls site-relative — pagefind.js prepends the base
  at runtime, absolute urls 404'd doubled), and a result click closes the
  search dialog (results are same-page fragment jumps). Verified in Chrome:
  the phrase ranks §2.1.2.2 #1 unquoted; quoted/single-word/heading queries
  good; click-through lands on the section.
- **June 11 PDF revision converted (D37; committed, unpushed):** Anthropic
  revised the card (changelog page + corrections + frontier-safeguards rewrite;
  317pp, was 319) and gave us the stable canonical URL (Drake Thomas thread).
  Re-converted wholesale: section ranges remapped via the doc's own TOC,
  everything re-extracted (oracle, renders, 153 figures, docling on 71 pages),
  regen + gate at the **same baseline (0 majors / L1 31 / T1 70**, accepted.json
  pages −1). All 7 publisher-changelog items verified in the diff; the changelog
  is a new first section. Header "Original PDF" → canonical CDN URL; `p.N` deep
  links stay on the archived in-repo PDF (owner: they must match the conversion
  even if Anthropic revises again). Verifier page constants updated (TOC 5–11,
  317pp, p.2 now gated). First changed-doc re-run: ~2.5h end to end, no new
  defect classes.
- **Open:** the revision conversion is unpushed (owner push authorization,
  D13). Next milestone remains the second-document generalization (D35).
