// Unified pipeline turning a stitched system card into HTML plus a table of
// contents. GFM for tables/footnotes, directives for :::transcript/:::example
// boxes, raw HTML passthrough for the complex tables.
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkDirective from 'remark-directive';
import remarkRehype from 'remark-rehype';
import rehypeRaw from 'rehype-raw';
import rehypeSlug from 'rehype-slug';
import rehypeStringify from 'rehype-stringify';
import { visit, SKIP } from 'unist-util-visit';
import { readFileSync } from 'node:fs';
import { join, basename } from 'node:path';

// PNG IHDR: width/height as big-endian u32 at offsets 16/20
function pngSize(path) {
  try {
    const buf = readFileSync(path);
    return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
  } catch {
    return null;
  }
}

function remarkBoxes() {
  return (tree) => {
    visit(tree, (node) => {
      if (node.type !== 'containerDirective') return;
      // A speaker turn inside a transcript: role-colored block with a label.
      if (node.name === 'turn') {
        const role = node.attributes?.role === 'user' ? 'user' : 'assistant';
        const label = node.attributes?.label ?? (role === 'user' ? 'User' : 'Assistant');
        node.data = { hName: 'div', hProperties: { className: ['turn', `turn-${role}`] } };
        node.children.unshift({
          type: 'paragraph',
          data: { hName: 'div', hProperties: { className: ['turn-label'] } },
          children: [{ type: 'text', value: label }],
        });
        return;
      }
      // A caption block: uniform small/muted styling attached to the
      // preceding figure/table/transcript (D23 — captions are a first-class
      // construct, not styling accidents).
      if (node.name === 'caption') {
        node.data = { hName: 'div', hProperties: { className: ['caption'] } };
        return;
      }
      if (node.name !== 'transcript' && node.name !== 'example') return;
      const title = node.attributes?.title;
      node.data = {
        hName: 'aside',
        hProperties: { className: ['box', `box-${node.name}`] },
      };
      const label = title ?? (node.name === 'transcript' ? 'Transcript' : 'Example');
      node.children.unshift({
        type: 'paragraph',
        data: { hName: 'div', hProperties: { className: ['box-label'] } },
        children: [{ type: 'text', value: label }],
      });
    });
  };
}

// Lettered sub-lists: the source marks them 'a.' 'b.' 'c.' as literal text
// inside bullet items (markdown has no lettered markers). A list whose items
// ALL lead with consecutive letters becomes <ol type="a"> with the literal
// prefixes stripped — ordered semantics, letter markers, content untouched.
function remarkLetterLists() {
  return (tree) => {
    visit(tree, 'list', (node) => {
      if (node.ordered) return;
      const leads = node.children.map((li) => {
        const para = li.children?.[0];
        const text = para?.children?.[0];
        if (!text || text.type !== 'text') return null;
        const m = /^([a-z])([.)])\s+/.exec(text.value);
        return m ? { text, letter: m[1], len: m[0].length } : null;
      });
      if (leads.some((l) => !l) || leads.length < 2) return;
      const seq = leads.every((l, i) => l.letter.charCodeAt(0) === 97 + i);
      if (!seq) return;
      for (const l of leads) l.text.value = l.text.value.slice(l.len);
      node.ordered = true;
      node.data = { ...(node.data ?? {}), hProperties: { type: 'a' } };
    });
  };
}

// `:chip[Label]` → a colored pill. Color resolved from the per-card registry
// (label → color name); unknown labels fall back to gray.
function remarkChips(chips = {}) {
  return (tree) => {
      visit(tree, 'textDirective', (node) => {
    if (node.name !== 'ph') return;
    node.data = {
      hName: 'span',
      hProperties: { className: ['ph'] },
    };
  });

visit(tree, 'textDirective', (node) => {
      if (node.name !== 'chip') return;
      const label = (node.children ?? []).map((c) => c.value ?? '').join('');
      const color = chips[label] ?? 'gray';
      node.data = {
        hName: 'span',
        hProperties: { className: ['chip', `chip-${color}`] },
      };
    });
  };
}

function hasClass(node, cls) {
  const c = node.properties?.className;
  return Array.isArray(c) ? c.includes(cls) : c === cls;
}

function rehypeArticle(opts = {}) {
  return (tree) => {
    // A pagemark in its own paragraph directly before a heading floats far
    // above it (headings carry large top margins). Move it inside the
    // heading so it aligns with the first text of that page.
    visit(tree, 'element', (node, index, parent) => {
      if (!parent || node.tagName !== 'p') return;
      const kids = node.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
      if (kids.length !== 1 || kids[0].tagName !== 'a' || !hasClass(kids[0], 'pagemark')) return;
      let ni = index + 1;
      while (parent.children[ni]?.type === 'text' && !parent.children[ni].value.trim()) ni += 1;
      const next = parent.children[ni];
      if (next?.type === 'element' && /^h[2-6]$/.test(next.tagName)) {
        next.children.unshift(kids[0]);
        parent.children.splice(index, 1);
        return index;
      }
    });
    // A paragraph that contains ONLY a page marker (no text) is an empty
    // between-blocks marker; tag it so CSS can collapse its height. (Cannot use
    // `.pagemark:only-child` in CSS — that ignores text-node siblings and would
    // wrongly match prose paragraphs that contain one inline marker.)
    visit(tree, 'element', (node) => {
      if (node.tagName !== 'p') return;
      const kids = node.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
      if (kids.length === 1 && kids[0].tagName === 'a' && hasClass(kids[0], 'pagemark')) {
        const c = node.properties.className;
        node.properties.className = Array.isArray(c) ? [...c, 'pagemark-row'] : ['pagemark-row'];
      }
    });
    // Paragraphs made of figure images → a <figure> card. CONSECUTIVE image
    // paragraphs are merged into ONE card, so a multi-panel figure (stacked
    // charts, plus the running-title strip the PDF repeats atop each page the
    // figure spans) reads as a single unit instead of N separate boxes. The
    // merge STOPS at a page marker — so per-page deep-links stay correctly
    // placed between cards — and at a caption or any non-image block.
    const parseImgPara = (p) => {
      if (!p || p.type !== 'element' || p.tagName !== 'p') return null;
      const kids = p.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
      const pagemarks = [];
      let k = 0;
      while (kids[k]?.tagName === 'a' && hasClass(kids[k], 'pagemark')) pagemarks.push(kids[k++]);
      const rest = kids.slice(k);
      if (!rest.length) return null; // pagemark-only / empty
      const last = rest[rest.length - 1];
      const caption = last.tagName === 'em' ? last : null;
      const imgs = caption ? rest.slice(0, -1) : rest;
      if (!imgs.length || !imgs.every((c) => c.tagName === 'img')) return null;
      return { pagemarks, imgs, caption };
    };
    visit(tree, 'element', (node, index, parent) => {
      if (!parent) return;
      const head = parseImgPara(node);
      if (!head) return;
      const imgs = [...head.imgs];
      let caption = head.caption;
      let endIdx = index; // last sibling folded into this figure
      // walk forward over consecutive image paragraphs (blank text skipped),
      // stopping at a page boundary (pagemark) or any non-image block
      for (let i = index + 1; !caption; ) {
        while (parent.children[i]?.type === 'text' && !parent.children[i].value.trim()) i += 1;
        const parsed = parseImgPara(parent.children[i]);
        if (!parsed || parsed.pagemarks.length) break;
        imgs.push(...parsed.imgs);
        caption = parsed.caption;
        endIdx = i;
        i += 1;
      }
      const zoom = (img) => ({
        type: 'element',
        tagName: 'a',
        properties: { href: img.properties.src, className: ['figure-zoom'] },
        children: [img],
      });
      // the card wraps every panel; .figure-zoom stays the per-image lightbox link
      const card = {
        type: 'element',
        tagName: 'div',
        properties: { className: ['figure-card'] },
        children: imgs.map(zoom),
      };
      const figure = { type: 'element', tagName: 'figure', properties: {}, children: [card] };
      let captionChildren = caption?.children;
      if (!captionChildren) {
        // caption in the paragraph after the group: <p><em>…</em></p>
        let nextIdx = endIdx + 1;
        while (
          parent.children[nextIdx]?.type === 'text' &&
          !parent.children[nextIdx].value.trim()
        ) {
          nextIdx += 1;
        }
        const next = parent.children[nextIdx];
        const nk =
          next?.tagName === 'p'
            ? next.children.filter((c) => !(c.type === 'text' && !c.value.trim()))
            : [];
        if (nk.length === 1 && nk[0].tagName === 'em') {
          captionChildren = nk[0].children;
          endIdx = nextIdx; // consume the caption paragraph too
        }
      }
      if (captionChildren) {
        figure.children.push({
          type: 'element',
          tagName: 'figcaption',
          properties: {},
          children: captionChildren,
        });
      }
      const replacement = [
        ...head.pagemarks.map((a) => ({
          type: 'element',
          tagName: 'p',
          properties: {},
          children: [a],
        })),
        figure,
      ];
      parent.children.splice(index, endIdx - index + 1, ...replacement);
      return index + replacement.length; // continue after the figure
    });

    // Table captions are plain markdown paragraphs (e.g. *__[Table 2.2.1.A] …__*)
    // and otherwise render at body size — tag them so they match figcaptions.
    visit(tree, 'element', (node) => {
      if (node.tagName !== 'p') return;
      const kids = node.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
      if (!kids.length) return;
      if (/^\s*\[(Table|Figure)\b/.test(textOf(node))) {
        const cls = node.properties.className;
        node.properties.className = Array.isArray(cls) ? [...cls, 'tablecap'] : ['tablecap'];
      }
    });

    visit(tree, 'element', (node, index, parent) => {
      if (node.tagName === 'img') {
        node.properties.loading = 'lazy';
        node.properties.decoding = 'async';
        if (opts.figuresDir && !node.properties.width) {
          const size = pngSize(join(opts.figuresDir, basename(String(node.properties.src))));
          if (size) Object.assign(node.properties, size);
        }
      }
      // wrap tables for horizontal overflow
      if (node.tagName === 'table' && parent && !hasClass(parent, 'table-wrap')) {
        parent.children[index] = {
          type: 'element',
          tagName: 'div',
          properties: { className: ['table-wrap'] },
          children: [node],
        };
        return SKIP;
      }
    });
  };
}

// Render-time typography: educate straight quotes/apostrophes into curly ones.
// Runs on the HTML tree (so raw-HTML tables are covered) and skips code, pre,
// and transcript/example boxes — those reproduce verbatim output where the
// source PDF itself prints straight quotes.
function rehypeSmartQuotes() {
  const SKIP = new Set(['pre', 'code', 'script', 'style', 'kbd']);
  // quote context does not flow across block boundaries (new cell, new
  // paragraph, new list item, …)
  const BLOCK = new Set([
    'p', 'li', 'td', 'th', 'tr', 'table', 'caption', 'blockquote', 'figcaption',
    'div', 'section', 'dt', 'dd', 'h2', 'h3', 'h4', 'h5', 'h6', 'br',
  ]);
  const opensAfter = (ch) => /[\s([{=—–‘“>]/.test(ch) || ch === '\n';
  return (tree) => {
    let prev = '\n';
    const walk = (node) => {
      if (node.type === 'element' && (SKIP.has(node.tagName) || hasClass(node, 'box'))) {
        prev = '\n';
        return;
      }
      if (node.type === 'element' && BLOCK.has(node.tagName)) prev = '\n';
      if (node.type === 'text') {
        const chars = [...node.value];
        let out = '';
        for (let i = 0; i < chars.length; i++) {
          const ch = chars[i];
          if (ch === '"') {
            out += opensAfter(prev) ? '“' : '”';
          } else if (ch === "'") {
            // decades ('90s) and mid-word apostrophes always close
            const next = chars[i + 1] ?? '\n';
            out += opensAfter(prev) && !/\d/.test(next) ? '‘' : '’';
          } else {
            out += ch;
          }
          prev = out.at(-1);
        }
        node.value = out;
        return;
      }
      (node.children ?? []).forEach(walk);
    };
    walk(tree);
  };
}

const HEADING_RE = /^(\d+(?:\.\d+)*)\s+(.*)$/;

function textOf(node) {
  if (node.type === 'text') return node.value;
  return (node.children ?? []).map(textOf).join('');
}

export async function renderCard(markdown, opts = {}) {
  const toc = [];
  const chips = opts.chips ?? {};

  const collectToc = () => (tree) => {
    visit(tree, 'element', (node) => {
      const m = /^h([2-6])$/.exec(node.tagName);
      if (!m || !node.properties?.id) return;
      const depth = Number(m[1]);
      const raw = textOf(node).trim();
      const nm = HEADING_RE.exec(raw);
      if (depth <= 4) {
        toc.push({
          depth,
          id: node.properties.id,
          number: nm ? nm[1] : null,
          title: nm ? nm[2] : raw,
        });
      }
      // wrap the leading section number in a styled span
      const first = node.children[0];
      if (nm && first?.type === 'text') {
        const rest = first.value.replace(/^\d+(?:\.\d+)*\s+/, ' ');
        node.children.splice(
          0,
          1,
          {
            type: 'element',
            tagName: 'span',
            properties: { className: ['secnum'] },
            children: [{ type: 'text', value: nm[1] }],
          },
          { type: 'text', value: rest },
        );
      }
      node.children.push({
        type: 'element',
        tagName: 'a',
        properties: {
          href: `#${node.properties.id}`,
          className: ['hanchor'],
          ariaLabel: 'Link to this section',
          dataPagefindIgnore: true,
        },
        children: [{ type: 'text', value: '#' }],
      });
    });
  };

  const file = await unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkDirective)
    .use(remarkChips, chips)
    .use(remarkLetterLists)
    .use(remarkBoxes)
    .use(remarkRehype, { allowDangerousHtml: true, footnoteLabel: 'Footnotes' })
    .use(rehypeRaw)
    .use(rehypeSmartQuotes)
    .use(rehypeSlug)
    .use(collectToc)
    .use(rehypeArticle, opts)
    .use(rehypeStringify, { allowDangerousHtml: true })
    .process(markdown);

  return { html: String(file), toc };
}
