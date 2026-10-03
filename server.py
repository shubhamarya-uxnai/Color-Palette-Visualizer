#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
RGB_RE = re.compile(r"\brgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", re.I)


def normalize_hex(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    if not value.startswith("#"):
        value = "#" + value
    if not re.fullmatch(r"#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}", value):
        return None
    if len(value) == 4:
        value = "#" + "".join(ch * 2 for ch in value[1:])
    return value.upper()


def rgb_to_hex(match: re.Match[str]) -> str | None:
    parts = [int(match.group(i)) for i in range(1, 4)]
    if any(v > 255 for v in parts):
        return None
    return "#{:02X}{:02X}{:02X}".format(*parts)


def readable_name(hex_value: str, fallback_index: int) -> str:
    return f"Color {fallback_index:02d} {hex_value}"


def group_from_name(filename: str) -> str:
    stem = Path(filename).stem.strip() or "Uploaded Palette"
    return re.sub(r"[-_]+", " ", stem).title()


def rows_from_csv(data: bytes, filename: str) -> list[dict]:
    text = data.decode("utf-8-sig", errors="replace")
    sample = text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample)
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    rows = []
    if not reader.fieldnames:
        return rows_from_text(text, filename)

    fields = {name.lower().strip(): name for name in reader.fieldnames if name}
    hex_field = next((fields[k] for k in fields if k in {"hex", "color", "colour", "code", "value"} or "hex" in k), None)
    name_field = next((fields[k] for k in fields if k in {"name", "color name", "colour name", "token", "role"} or "name" in k), None)
    group_field = next((fields[k] for k in fields if k in {"group", "brand", "palette", "layer", "collection"}), None)

    for row in reader:
        candidates = []
        if hex_field:
            candidates.append(row.get(hex_field, ""))
        candidates.extend(str(v) for v in row.values())
        found = None
        for candidate in candidates:
            m = HEX_RE.search(candidate or "")
            if m:
                found = normalize_hex(m.group(0))
                break
            m = RGB_RE.search(candidate or "")
            if m:
                found = rgb_to_hex(m)
                break
        if not found:
            continue
        rows.append(
            {
                "group": (row.get(group_field, "") if group_field else "") or group_from_name(filename),
                "name": (row.get(name_field, "") if name_field else "") or readable_name(found, len(rows) + 1),
                "hex": found,
                "source": "CSV",
            }
        )
    return rows


def text_from_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        raw = data.decode("latin-1", errors="ignore")
        chunks = re.findall(r"\((.*?)\)\s*Tj|\[(.*?)\]\s*TJ", raw, flags=re.S)
        text_bits = []
        for one, many in chunks:
            text_bits.append(one or many)
        return "\n".join(text_bits) if text_bits else raw


def rows_from_text(text: str, filename: str, source: str = "Text") -> list[dict]:
    rows = []
    seen = set()
    for match in HEX_RE.finditer(text):
        hex_value = normalize_hex(match.group(0))
        if not hex_value or hex_value in seen:
            continue
        seen.add(hex_value)
        before = text[max(0, match.start() - 80) : match.start()]
        label = re.sub(r"[^A-Za-z0-9 /_.-]+", " ", before).strip().split("\n")[-1].strip(" :-")
        rows.append(
            {
                "group": group_from_name(filename),
                "name": label[-48:] if label else readable_name(hex_value, len(rows) + 1),
                "hex": hex_value,
                "source": source,
            }
        )
    for match in RGB_RE.finditer(text):
        hex_value = rgb_to_hex(match)
        if not hex_value or hex_value in seen:
            continue
        seen.add(hex_value)
        rows.append(
            {
                "group": group_from_name(filename),
                "name": readable_name(hex_value, len(rows) + 1),
                "hex": hex_value,
                "source": source,
            }
        )
    return rows


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        if self.path != "/api/extract":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length)
        filename = self.headers.get("X-Filename", "Uploaded Palette")
        lower = filename.lower()
        try:
            if lower.endswith(".csv"):
                colors = rows_from_csv(data, filename)
            elif lower.endswith(".pdf"):
                colors = rows_from_text(text_from_pdf(data), filename, "PDF")
            else:
                colors = rows_from_text(data.decode("utf-8", errors="replace"), filename)
            payload = {"colors": colors, "filename": filename, "count": len(colors)}
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            body = json.dumps({"error": str(exc)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8891
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Color Palette V1 serving at http://127.0.0.1:{port}/")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
