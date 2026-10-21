# Palette Visualizer v1.1.0

React rebuild of the browser-based palette visualizer. CSV and selectable-text PDF files are parsed locally in the browser; uploads are not sent to an application server. RGB and HSL plots remain available, and the HCT plot now uses actual Material Color Utilities hue, chroma, and tone values.

## Develop and build

```bash
cd react-app
npm install
npm run dev
npm run build
```

The Vite build writes deployable `index.html` and `assets/` to the repository root. Open the root with `python3 -m http.server 8891` to test the production build. GitHub Pages publishes `main` from `/ (root)` at <https://shubhamarya-uxnai.github.io/Color-Palette-Visualizer/>.

The shared BA design system is resolved from `../../../va-design-system` during the build. Set `BA_DESIGN_SYSTEM_DIR` to a different checkout when building this repository elsewhere.

CSV files can include name, hex/color/colour/code/RGB, group/brand/palette/collection, and layer columns. PDFs need selectable text containing hex or `rgb(...)` values; scanned PDFs require OCR first. PDF.js loads from its pinned CDN release only when a PDF is imported.
