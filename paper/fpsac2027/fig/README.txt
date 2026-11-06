Editable figure sources for the FPSAC 2027 manuscript

Figure 1: software-layout/source/representation.html / .svg
Figure 2: software-layout/source/computed-tables.html / .svg
Figure 3: software-layout/source/join-mechanism.html / .svg
Authoring source: software-layout/source/design.mjs
HTML/SVG-to-PDF exporter and geometry checks: source/export.mjs
Independent data computation: source/compute-example.py
Exact inputs, raw and reduced tables, results and source hashes: source/example-data.json
Embedded DejaVu Sans subset and its license: software-layout/fonts/
Matching PDFs: software-layout/pdf/

Edit design.mjs for changes that survive regeneration. The exporter measures
window glyphs to align labels and waning underlines. Tables include every
cell with equal cell dimensions; starred entries are displayed by their
minimum, and all finite entries are preserved. Blue/red identify inputs A/B.
No numerical observations are sampled or excluded.

Rebuild using Node.js and Python >= 3.10:
  Install the exact package revision in ../REPRODUCIBILITY.txt first.
  cd fig
  npm install
  npx playwright install chromium
  npm run compute:example
  npm run build

Alternatively set CHROME_PATH to an installed Chrome/Chromium executable.
For a source checkout instead of an installed package, set TITO_SOURCE_ROOT
to its root when computing the example. The exporter checks text size,
clipping, text overlap, equal cells, panel alignment within 1.5 pt and arrow
attachment to framed objects. It writes previews and QA JSON in generated
preview/ and qa/ directories; inspect the PDFs visually as well.

Overleaf compiles the included PDFs directly; Python, Node and Chrome are
needed only to regenerate figures. The sources contain editable vectors.
