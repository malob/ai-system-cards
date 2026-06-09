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

function hasClass(node, cls) {
  const c = node.properties?.className;
  return Array.isArray(c) ? c.includes(cls) : c === cls;
}

function rehypeArticle(opts = {}) {
  return (tree) => {
    // Paragraphs made of figure images (1+ <img>, optional trailing <em>
    // caption, caption may also live in the following paragraph) → <figure>
    visit(tree, 'element', (node, index, parent) => {
      if (!parent || node.tagName !== 'p') return;
      let kids = node.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
      // hoist page-marker anchors out of figure paragraphs
      const pagemarks = [];
      while (kids[0]?.tagName === 'a' && hasClass(kids[0], 'pagemark')) {
        pagemarks.push(kids.shift());
      }
      if (!kids.length) return;
      const last = kids[kids.length - 1];
      const caption = last.tagName === 'em' ? last : null;
      const imgs = caption ? kids.slice(0, -1) : kids;
      if (!imgs.length || !imgs.every((k) => k.tagName === 'img')) return;
      const zoom = (img) => ({
        type: 'element',
        tagName: 'a',
        properties: { href: img.properties.src, className: ['figure-zoom'] },
        children: [img],
      });
      const figure = {
        type: 'element',
        tagName: 'figure',
        properties: {},
        children: imgs.map(zoom),
      };
      let captionChildren = caption?.children;
      if (!captionChildren) {
        // caption in the next paragraph: <p><em>…</em></p>
        let nextIdx = index + 1;
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
          parent.children.splice(index + 1, nextIdx - index);
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
      parent.children.splice(index, 1, ...pagemarks.map((a) => ({
        type: 'element',
        tagName: 'p',
        properties: {},
        children: [a],
      })), figure);
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

const HEADING_RE = /^(\d+(?:\.\d+)*)\s+(.*)$/;

function textOf(node) {
  if (node.type === 'text') return node.value;
  return (node.children ?? []).map(textOf).join('');
}

export async function renderCard(markdown, opts = {}) {
  const toc = [];

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
    .use(remarkBoxes)
    .use(remarkRehype, { allowDangerousHtml: true, footnoteLabel: 'Footnotes' })
    .use(rehypeRaw)
    .use(rehypeSlug)
    .use(collectToc)
    .use(rehypeArticle, opts)
    .use(rehypeStringify, { allowDangerousHtml: true })
    .process(markdown);

  return { html: String(file), toc };
}
