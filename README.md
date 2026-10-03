# Color Palette Visualizer V1

A browser-first color palette visualizer. CSV files are parsed in JavaScript and PDF text is extracted locally with PDF.js. Uploaded files are not sent to an application server.

## Run locally

```bash
python3 server.py
```

Open <http://127.0.0.1:8891/>. The Python server is only a static-file server for local development; the upload workflow runs in the browser.

## Publish with GitHub Pages

1. Open the repository's **Settings** tab.
2. Choose **Pages**.
3. Under **Build and deployment**, select **Deploy from a branch**.
4. Select the `main` branch and the `/ (root)` folder.
5. Click **Save**.

GitHub Pages will publish `index.html`, the stylesheets, fonts, and local design-system files. PDF.js is loaded from its pinned CDN release only when a PDF is uploaded.

## Supported input

CSV files can include `name`, `hex`, `color`, `colour`, `code`, `rgb`, `group`, `brand`, `palette`, or `layer` columns. PDF files must contain selectable text with hex values such as `#DA1A1B` or RGB values such as `rgb(218, 26, 27)`.

Scanned PDFs without a text layer need OCR before upload.
