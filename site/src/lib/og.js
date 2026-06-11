// Build-time Open Graph card renderer: Satori (element tree → SVG) + resvg
// (SVG → PNG), in the site's own palette and type. Produces one 1200×630 PNG
// per page; the endpoint at src/pages/og/[...path].png.ts emits them at build.
// Satori vectorizes glyphs, so only Satori needs the fonts (resvg rasterizes
// the already-pathed SVG). Fonts must be woff/ttf/otf — NOT woff2.
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';

const require = createRequire(import.meta.url);
const fontData = (pkg, rel) =>
  readFileSync(join(dirname(require.resolve(`${pkg}/package.json`)), rel));

const FONTS = [
  { name: 'Fraunces', weight: 400, style: 'normal',
    data: fontData('@fontsource/fraunces', 'files/fraunces-latin-400-normal.woff') },
  { name: 'Fraunces', weight: 600, style: 'normal',
    data: fontData('@fontsource/fraunces', 'files/fraunces-latin-600-normal.woff') },
  { name: 'IBM Plex Mono', weight: 500, style: 'normal',
    data: fontData('@fontsource/ibm-plex-mono', 'files/ibm-plex-mono-latin-500-normal.woff') },
];

const C = { paper: '#f6f2ea', ink: '#221d15', soft: '#6b6354', faint: '#97907f', clay: '#a8512a' };
const MONO = 'IBM Plex Mono';
const SERIF = 'Fraunces';

// minimal hyperscript for Satori's element tree (avoids needing JSX)
const h = (style, children) => ({
  type: 'div',
  props: children === undefined ? { style } : { style, children },
});

const spine = h({ position: 'absolute', left: 0, top: 0, width: 14, height: 630, backgroundColor: C.clay });

const wordmark = (size) =>
  h({ display: 'flex', alignItems: 'baseline', fontFamily: SERIF, fontWeight: 600, fontSize: size, color: C.ink }, [
    h({ display: 'flex' }, 'AI System Cards'),
    h({ display: 'flex', color: C.clay, marginLeft: Math.round(size * 0.18) }, '§'),
  ]);

const dot = () => h({ display: 'flex', color: C.clay, marginLeft: 14, marginRight: 14 }, '·');

const cardTree = (o) =>
  h({
    display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
    width: 1200, height: 630, backgroundColor: C.paper,
    paddingTop: 70, paddingBottom: 70, paddingLeft: 80, paddingRight: 80, position: 'relative',
  }, [
    spine,
    wordmark(30),
    h({ display: 'flex', flexDirection: 'column' }, [
      h({ fontFamily: MONO, fontWeight: 500, fontSize: 24, letterSpacing: 4,
          textTransform: 'uppercase', color: C.clay, marginBottom: 22 },
        `${o.vendor} · System Card`),
      h({ display: 'flex', fontFamily: SERIF, fontWeight: 600,
          fontSize: o.title.length > 30 ? 76 : 92, color: C.ink, lineHeight: 1.05, letterSpacing: -1 },
        o.title),
    ]),
    h({ display: 'flex', fontFamily: MONO, fontWeight: 500, fontSize: 25, color: C.soft }, [
      h({ display: 'flex' }, o.date),
      dot(),
      h({ display: 'flex' }, `${o.pages} pages`),
      dot(),
      h({ display: 'flex' }, 'faithful HTML archive'),
    ]),
  ]);

const homeTree = () =>
  h({
    display: 'flex', flexDirection: 'column', justifyContent: 'center',
    width: 1200, height: 630, backgroundColor: C.paper,
    paddingTop: 80, paddingBottom: 80, paddingLeft: 80, paddingRight: 80, position: 'relative',
  }, [
    spine,
    h({ fontFamily: MONO, fontWeight: 500, fontSize: 23, letterSpacing: 5,
        textTransform: 'uppercase', color: C.clay, marginBottom: 26 }, 'A readable archive'),
    wordmark(104),
    h({ display: 'flex', fontFamily: SERIF, fontWeight: 400, fontSize: 35, color: C.soft, marginTop: 30 },
      'Faithful, readable web renderings of AI model system cards.'),
    h({ display: 'flex', fontFamily: SERIF, fontWeight: 400, fontSize: 28, color: C.faint, marginTop: 14 },
      'Every sentence, table, figure, and footnote — linked to the source PDF.'),
    h({ display: 'flex', fontFamily: MONO, fontWeight: 500, fontSize: 24, color: C.clay, marginTop: 48 },
      'malob.github.io/ai-system-cards'),
  ]);

// input: { kind: 'home' } | { kind: 'card', title, vendor, date, pages }
export async function renderOgPng(input) {
  const tree = input.kind === 'home' ? homeTree() : cardTree(input);
  const svg = await satori(tree, { width: 1200, height: 630, fonts: FONTS });
  return new Resvg(svg, { fitTo: { mode: 'width', value: 1200 } }).render().asPng();
}
