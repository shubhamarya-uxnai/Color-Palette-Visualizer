# OKLCH-inspired graph and 3D interaction plan

Status: implementation handoff, 2026-11-02. This is a plan, not completed work.

## Context from the discussion

The user shared [OKLCH.com](https://oklch.com/#0.521,0.1194,139,100), liked its graph and 3D behavior, and asked whether the open source code could be used in Palette Visualizer. The desired outcome is to bring comparable graph quality and interaction into this project while preserving its core purpose: comparing **multiple named palette colors** imported from CSV/PDF, filtered by group and layer, in RGB, HSL, and HCT. The user asked for this detailed Markdown handoff so another bot can implement it.

The reference is [Evil Martians' OKLCH Picker repository](https://github.com/evilmartians/oklch-picker). It is MIT licensed; copied or substantially adapted code must retain the upstream copyright and license notice. Its relevant areas are `view/fullmodel/`, `view/chart/`, `view/minimodel/`, and `lib/{cameras,canvas,colors,math,model}.ts`. The upstream app uses Three.js and other color/rendering libraries. Inspect the exact upstream commit and dependencies before copying code. The reference represents OKLCH and display gamuts; its geometry must **not** be presented as HCT, HSL, or RGB geometry.

## Current project baseline

- React/Vite app: `react-app/src/main.jsx`; color parsing and coordinate math: `react-app/src/engine.js`; BA component adapter: `react-app/src/ui/components.jsx`; CSS: `react-app/src/styles.css` and root `styles.css`.
- The current stage is SVG. `Plot` projects points with `project()`, draws an RGB cube or circular guide rings, supports pointer drag rotation and wheel zoom, and draws distance lines from a pinned color. The right sidebar provides metadata and ranked distances.
- `position()` maps RGB to a cube, HSL to hue/saturation/lightness coordinates, and HCT to hue/chroma/tone coordinates. HCT comes from `@material/material-color-utilities`.
- Data is currently six digit HEX based. CSV/PDF parsing is local in the browser. Appearance persists in `localStorage`; palette data does not.
- `npm run build` inside `react-app` writes production assets to the repository root. The build resolves the sibling `va-design-system` checkout unless `BA_DESIGN_SYSTEM_DIR` is set. GitHub Pages serves `main` from root.

## Product scope and decisions

1. Make the **multi-color palette scene** the primary graph. Do not replace the app with a single-color picker.
2. Add smooth orbit, zoom, pan, reset/view presets, readable depth, axes, labels, hover, selection, and group filtering to the existing RGB/HSL/HCT modes.
3. Add a real **OKLCH mode** if adopting the reference gamut surface or OKLCH channel graph. Label coordinates and axes accurately. Do not reuse the OKLCH gamut mesh behind an HCT label.
4. Keep the BA shell, upload/edit modal, group/layer filters, selection, and distance workflow working. Use the BA adapter for normal controls.
5. Prefer a React-owned Three.js scene for the full 3D experience. Isolate rendering from palette state and color conversion. Reuse upstream implementation selectively where it clearly saves effort; avoid transplanting its whole app, global state, styles, and build system.
6. First release target: a robust 3D palette scene and OKLCH mode with an sRGB gamut surface. P3/Rec.2020 overlays, alpha editing, and full single-color channel graphs are follow-on work unless the upstream inspection shows they can be integrated without destabilizing the first release.

## Implementation sequence

### 0. Baseline and upstream audit

- Record the current Git status and commit. Run the existing production build before edits. Do not overwrite unrelated user changes.
- Inspect the upstream `view/fullmodel`, `view/chart`, `view/minimodel`, and `lib` modules at a pinned commit. Document which module renders the 3D gamut, which controls camera gestures, which draws channel graphs, and which supplies color conversions/meshes.
- Check each candidate file's dependencies, license headers, assumptions about Nanostores/DOM, and whether it is independently reusable. Record chosen upstream commit and copied/adapted file list in a `THIRD_PARTY_NOTICES.md` or equivalent notice file.
- Capture reference behavior in a browser: orbit, wheel zoom, right-button pan, reset, point/section selection, resize, mobile gestures, graph toggles, and reduced-motion behavior where present. Do not claim parity from reading source alone.

### 1. Separate palette data from rendering

- Extract `Plot` from `main.jsx` into a dedicated component, for example `react-app/src/visualization/PaletteScene.jsx`, with clear props: visible colors, mode, selected/hovered ID, camera/view commands, and callbacks.
- Keep a single normalized color record shape (`id`, `name`, `group`, `layer`, `hex`), with pure conversion functions in `engine.js` or a new `colorSpaces.js`.
- Make coordinate normalization explicit per mode. Document units, ranges, clamping, axes, and the meaning of distance. HCT chroma normalization is currently a visual scale; do not describe its Euclidean distance as a validated perceptual difference.
- Preserve selected point and filters across mode switches where the selected color remains visible. Clear or explain selection when filtering hides it.

### 2. Add the Three.js scene and camera controls

- Add `three` as a pinned project dependency. Use a React wrapper component that owns renderer, scene, camera, controls, animation loop, resize observer, and disposal. Avoid coupling renderer lifecycle to frequent React state updates.
- Implement orbit drag, wheel/pinch zoom, right-button or modified drag pan, sensible camera bounds, reset, and Front/Top/Side presets. Keep gestures consistent on mouse, trackpad, and touch. Do not let stage wheel gestures scroll the page while interacting with the stage.
- Render visible palette points as readable markers with hover and selected states. Use raycasting or an equivalent picking method and an HTML/SVG overlay for legible names/tooltips if needed. Ensure clicks do not also trigger orbit or pan.
- Draw distinct RGB cube, HSL cylinder, HCT coordinate guide, and OKLCH guide. Coordinate labels must match the active mode. Use appropriate depth cues (grid/axes, opacity, lighting, perspective) and keep point colors visually faithful.
- Provide a fallback message or existing SVG plot when WebGL is unavailable. Dispose geometries, materials, textures, listeners, observers, and animation frames on unmount or mode changes.

### 3. Add OKLCH as a truthful color mode

- Use a maintained conversion library already present upstream or a focused compatible package, with consistent sRGB HEX to OKLCH conversion. Add tests for canonical neutral, saturated, and near-boundary colors.
- Plot OKLCH as cylindrical hue/chroma/lightness coordinates. Define a documented chroma scale and show actual L/C/H metadata for hovered and selected points.
- If porting an upstream sRGB gamut mesh, isolate it as an OKLCH-only layer. Verify its color conversion and gamut boundary against the pinned upstream version. Provide a visible show/hide control and a legend explaining surface versus palette markers.
- Keep HCT as HCT. Do not convert a point to OKLCH and call the result HCT, or assume equal numeric chroma and tone/lightness across the models.

### 4. Integrate the graph into the product UI

- Replace the stage's SVG plot with the new scene while retaining the current header, sidebars, upload/edit modal, palette stats, and distance panel.
- Update the Color Space selector to include OKLCH. Add compact stage controls for view preset, reset, show/hide axes, show/hide gamut surface where applicable, and a help hint for gestures.
- Show precise selected/hovered coordinates and an explicit distance unit/interpretation per mode. Keep line drawing from the pinned point optional if it obscures dense palettes.
- Maintain keyboard access to palette selection through the Visible Colors list, even if WebGL picking itself is pointer based. Provide accessible text summaries of the active mode, selected color, and current filters.
- Match existing BA typography, tokens, light/dark/contrast settings, and responsive layout. Test text contrast over bright plotted colors and tooltips.

### 5. Performance and robustness

- Verify smooth interaction with a small palette and a dense palette (for example 300–500 points). Use instancing or batched geometry if individual meshes become slow. Cap label density and avoid re-creating the renderer on hover.
- Handle empty palettes, invalid colors, a single point, duplicate HEX values with different names, rapid mode toggles, modal open/close, window resize, and touch input.
- Preserve current local-only file processing. Do not add a server upload path.
- Keep production output reasonably sized; use dynamic import for the 3D bundle if the initial load becomes noticeably heavier.

## Acceptance criteria

- A CSV or PDF palette can still be imported, edited, filtered, visualized, and inspected in all four modes.
- Mouse/trackpad/touch orbit and zoom feel smooth; pan and reset work; pointer selection remains reliable after camera movement. Camera state does not jump during hover or filtering.
- RGB, HSL, HCT, and OKLCH points use documented, correct coordinates. Only OKLCH mode can display an OKLCH gamut surface.
- The selected point, hover metadata, group/layer filters, and distance panel stay in sync. A dense palette remains usable.
- The production build succeeds and the root build loads under a local static server with no console errors. Test at desktop and mobile widths, in light and dark appearance, with WebGL available and unavailable.
- Any copied upstream code has a pinned source reference and MIT notice. The implementation report clearly identifies what was reused versus newly written.

## Verification and delivery

1. Run `npm install` (or the repository's lockfile-preserving install) and `npm run build` in `react-app`.
2. Use `test-lays-starbucks.csv` plus a manually created palette containing grayscale and saturated colors. Exercise every mode, filter, selection, camera gesture, and resize.
3. Compare the OKLCH view to the reference with a known color from the shared URL, checking values and behavior rather than only visual resemblance.
4. Inspect generated root files and Git diff so build output, lockfile, and source remain consistent. Do not publish or deploy unless separately authorized.
5. Deliver a concise summary, screenshots or a short recording of the result, test evidence, limitations, and the exact upstream commit/files reused.

## Effort and tradeoffs

Estimated engineering effort after upstream audit: roughly 3–5 focused days for a polished Three.js palette scene, plus 2–4 days for faithful OKLCH gamut integration, responsiveness, accessibility, and QA. A full port of every upstream graph and P3/Rec.2020 feature could extend this to 1–2 weeks or more. Estimates are provisional because the upstream renderer's coupling has not yet been traced line by line.

The key risk is scope drift: an attractive single-color OKLCH picker could displace the existing palette comparison job. Keep the multi-color workflow as the release gate and add upstream graph features only when their color model and interaction semantics are clear.
