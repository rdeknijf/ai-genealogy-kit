#!/usr/bin/env python3
"""Generate a scan verification HTML page from a JSON records file.

Usage:
    python scripts/generate_verification.py INPUT.json [OUTPUT.html] [--download]

The input JSON should be an array of record objects:
[
  {
    "id": "unique-record-id",
    "iiifUrl": "https://example.com/iiif/image/3.0/12345/full/max/0/default.jpg",
    "name": "Person Name",
    "collection": "Source collection name",
    "expect": "What the reviewer should look for on this scan",
    "aiAnalysis": "AI's reading of the scan content (HTML allowed)",
    "aiConfidence": "high|medium|low",
    "aiConfidenceText": "90% — brief explanation",
    "metadata": {"key": "value", ...},
    "sourceUrl": "https://link-to-original-record"
  }
]

Options:
    --download    Download all images to a local directory next to the
                  output HTML. The HTML will reference local files instead
                  of remote URLs, so it works fully offline.

The IIIF URL is used to derive thumbnail and full-resolution URLs. If
iiifUrl is a full IIIF Image API URL, the script extracts the base and
constructs display/zoom URLs automatically. You can also provide a plain
image URL — it will be used as-is.

Output is a self-contained HTML file with no external dependencies.
Verdicts (confirm/reject/notes) are saved to localStorage AND can be
exported back to a JSON file via the "Export verdicts" button.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path


def iiif_base(url: str) -> str | None:
    """Extract IIIF base from a URL, or None if not IIIF."""
    m = re.match(r"(https?://[^/]+/iiif/image/[\d.]+/[^/]+)/.*", url)
    return m.group(1) if m else None


def download_images(records: list, img_dir: Path) -> None:
    """Download display + full resolution images for all records."""
    img_dir.mkdir(parents=True, exist_ok=True)
    for r in records:
        url = r.get("iiifUrl", "")
        base = iiif_base(url)
        rid = r["id"]

        if base:
            display_url = f"{base}/full/1200,/0/default.jpg"
            full_url = f"{base}/full/max/0/default.jpg"
        else:
            display_url = url
            full_url = url

        display_path = img_dir / f"{rid}_display.jpg"
        full_path = img_dir / f"{rid}_full.jpg"

        if not display_path.exists():
            print(f"  Downloading display: {rid}...")
            urllib.request.urlretrieve(display_url, display_path)

        if not full_path.exists():
            print(f"  Downloading full:    {rid}...")
            urllib.request.urlretrieve(full_url, full_path)

        r["_localDisplay"] = f"{img_dir.name}/{rid}_display.jpg"
        r["_localFull"] = f"{img_dir.name}/{rid}_full.jpg"


def generate_html(records: list, local_images: bool = False) -> str:
    records_json = json.dumps(records, ensure_ascii=False, indent=2)
    local_flag = "true" if local_images else "false"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scan Verification</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: #1a1a2e; color: #e0e0e0; }}

  header {{ background: #16213e; padding: 0.6rem 2rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 10; border-bottom: 1px solid #0f3460; }}
  header h1 {{ font-size: 1rem; font-weight: 500; color: #888; }}
  .header-right {{ display: flex; gap: 0.8rem; align-items: center; }}
  .stats {{ font-size: 0.8rem; color: #888; }}
  .btn-export {{ background: #0f3460; color: #ccc; border: 1px solid #1a4080; padding: 0.3rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }}
  .btn-export:hover {{ background: #1a4080; }}

  .action-bar {{ position: sticky; top: 42px; z-index: 10; background: #0d1b2a; border-bottom: 1px solid #0f3460; padding: 0.6rem 2rem; display: flex; align-items: center; justify-content: center; gap: 1rem; }}
  .action-bar .title-area {{ font-size: 1rem; color: #fff; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px; }}
  .nav-btn {{ background: #0f3460; color: #e0e0e0; border: 1px solid #1a4080; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-size: 0.9rem; }}
  .nav-btn:hover {{ background: #1a4080; }}
  .nav-btn:disabled {{ opacity: 0.3; cursor: default; }}
  .counter {{ color: #a0a0a0; font-size: 0.9rem; }}
  .action-bar .btn {{ padding: 0.5rem 1.8rem; font-size: 1rem; }}
  .action-bar .note-inline {{ background: #1a2744; border: 1px solid #0f3460; border-radius: 4px; color: #ccc; font-size: 0.85rem; padding: 0.45rem 0.6rem; width: 200px; }}
  .action-bar .note-inline::placeholder {{ color: #555; }}

  .record {{ max-width: 1400px; margin: 0 auto; padding: 1.5rem; display: flex; gap: 1.5rem; height: calc(100vh - 95px); }}

  .scan-panel {{ flex: 1; display: flex; flex-direction: column; min-width: 0; }}
  .scan-container {{ flex: 1; overflow: auto; background: #111; border-radius: 8px; cursor: grab; }}
  .scan-container:active {{ cursor: grabbing; }}
  .scan-container img {{ width: 100%; display: block; }}
  .scan-toolbar {{ display: flex; gap: 0.5rem; padding: 0.5rem 0; }}
  .scan-toolbar button {{ background: #0f3460; color: #ccc; border: 1px solid #1a4080; padding: 0.3rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }}
  .scan-toolbar button:hover {{ background: #1a4080; }}

  .info-panel {{ width: 420px; flex-shrink: 0; display: flex; flex-direction: column; gap: 1rem; overflow-y: auto; }}

  .card {{ background: #16213e; border-radius: 8px; padding: 1.2rem; border: 1px solid #0f3460; }}
  .card h3 {{ font-size: 0.85rem; color: #53a8b6; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px; }}

  .expect-box {{ background: #1a2744; border-left: 3px solid #3498db; padding: 0.8rem 1rem; border-radius: 0 6px 6px 0; }}
  .expect-box p {{ font-size: 0.9rem; line-height: 1.5; color: #ccc; }}

  .ai-box {{ background: #1a2744; border-left: 3px solid #9b59b6; padding: 0.8rem 1rem; border-radius: 0 6px 6px 0; }}
  .ai-box .confidence {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 0.3rem; }}
  .ai-box .confidence.high {{ color: #27ae60; }}
  .ai-box .confidence.medium {{ color: #f39c12; }}
  .ai-box .confidence.low {{ color: #e74c3c; }}
  .ai-box p {{ font-size: 0.9rem; line-height: 1.5; color: #ccc; }}

  .meta-table {{ width: 100%; font-size: 0.85rem; border-collapse: collapse; }}
  .meta-table td {{ padding: 0.25rem 0; vertical-align: top; }}
  .meta-table td:first-child {{ font-weight: 600; width: 140px; color: #888; }}
  .meta-table td:last-child {{ color: #ccc; }}

  .btn {{ border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: background 0.15s; }}
  .btn-confirm {{ background: #27ae60; color: white; }}
  .btn-confirm:hover {{ background: #219a52; }}
  .btn-reject {{ background: #e74c3c; color: white; }}
  .btn-reject:hover {{ background: #c0392b; }}
  .btn-reset {{ background: #555; color: white; padding: 0.5rem 1rem; font-size: 0.85rem; }}
  .btn-reset:hover {{ background: #666; }}

  .badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; vertical-align: middle; margin-left: 0.5rem; }}
  .badge.pending {{ background: #f39c12; color: #000; }}
  .badge.verified {{ background: #27ae60; color: #fff; }}
  .badge.rejected {{ background: #e74c3c; color: #fff; }}

  .lightbox {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.95); z-index: 100; overflow: auto; cursor: zoom-out; }}
  .lightbox.active {{ display: block; }}
  .lightbox img {{ display: block; margin: 0 auto; max-width: none; }}

  @media (max-width: 900px) {{
    .record {{ flex-direction: column; height: auto; }}
    .info-panel {{ width: 100%; }}
  }}
</style>
</head>
<body>

<header>
  <h1>Scan Verification</h1>
  <div class="header-right">
    <div class="stats" id="stats"></div>
    <button class="btn-export" onclick="exportVerdicts()">Export verdicts</button>
  </div>
</header>

<div class="action-bar">
  <button class="nav-btn" id="prevBtn" onclick="navigate(-1)">&larr;</button>
  <span class="counter" id="counter"></span>
  <span class="title-area" id="titleArea"></span>
  <input class="note-inline" id="note-input" placeholder="Note (optional)...">
  <button class="btn btn-confirm action-bar-btn" onclick="confirmAndNext()">Confirm &rarr;</button>
  <button class="btn btn-reject action-bar-btn" onclick="rejectAndNext()">Reject &rarr;</button>
  <button class="btn btn-reset" onclick="setStatus('pending')">Reset</button>
  <button class="nav-btn" id="nextBtn" onclick="navigate(1)">&rarr;</button>
</div>

<div class="record" id="record"></div>

<div class="lightbox" id="lightbox" onclick="closeLightbox()">
  <img id="lightbox-img" src="">
</div>

<script>
const LOCAL_IMAGES = {local_flag};
const records = {records_json};

records.forEach(r => {{ r.status = r.status || 'pending'; r.note = r.note || ''; }});

let currentIdx = 0;
const storageKey = 'scan-verify-' + (location.pathname.split('/').pop() || 'default');

function save() {{
  localStorage.setItem(storageKey, JSON.stringify(records.map(r => ({{ id: r.id, status: r.status, note: r.note }}))));
  updateStats();
}}

function load() {{
  const saved = localStorage.getItem(storageKey);
  if (saved) {{
    const verdicts = JSON.parse(saved);
    verdicts.forEach(v => {{
      const r = records.find(r => r.id === v.id);
      if (r) {{ r.status = v.status; r.note = v.note; }}
    }});
  }}
}}

function exportVerdicts() {{
  // Save current note first
  const noteEl = document.getElementById('note-input');
  if (noteEl) records[currentIdx].note = noteEl.value;
  save();

  // Build export: merge verdicts back into original records
  const output = records.map(r => {{
    const out = {{}};
    for (const [k, v] of Object.entries(r)) {{
      if (!k.startsWith('_')) out[k] = v;
    }}
    return out;
  }});

  const blob = new Blob([JSON.stringify(output, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = location.pathname.split('/').pop().replace('.html', '-verdicts.json');
  a.click();
  URL.revokeObjectURL(url);
}}

function updateStats() {{
  const v = records.filter(r => r.status === 'verified').length;
  const j = records.filter(r => r.status === 'rejected').length;
  const p = records.length - v - j;
  document.getElementById('stats').textContent = v + ' verified / ' + j + ' rejected / ' + p + ' pending';
}}

function navigate(delta) {{
  const noteEl = document.getElementById('note-input');
  if (noteEl) records[currentIdx].note = noteEl.value;
  save();
  currentIdx = Math.max(0, Math.min(records.length - 1, currentIdx + delta));
  render();
}}

function setStatus(status) {{
  const noteEl = document.getElementById('note-input');
  if (noteEl) records[currentIdx].note = noteEl.value;
  records[currentIdx].status = status;
  save();
  render();
}}

function confirmAndNext() {{
  setStatus('verified');
  if (currentIdx < records.length - 1) navigate(1);
}}

function rejectAndNext() {{
  setStatus('rejected');
  if (currentIdx < records.length - 1) navigate(1);
}}

function openLightbox() {{
  const r = records[currentIdx];
  document.getElementById('lightbox-img').src = r._fullUrl;
  document.getElementById('lightbox').classList.add('active');
}}

function closeLightbox() {{
  document.getElementById('lightbox').classList.remove('active');
}}

document.addEventListener('keydown', (e) => {{
  if (e.key === 'Escape') closeLightbox();
  if (document.activeElement.tagName === 'INPUT') return;
  if (e.key === 'ArrowLeft') navigate(-1);
  if (e.key === 'ArrowRight') navigate(1);
  if (e.key === 'f' || e.key === 'F') openLightbox();
}});

function render() {{
  const r = records[currentIdx];
  document.getElementById('counter').textContent = (currentIdx + 1) + ' / ' + records.length;
  document.getElementById('prevBtn').disabled = currentIdx === 0;
  document.getElementById('nextBtn').disabled = currentIdx === records.length - 1;
  document.getElementById('titleArea').innerHTML = r.name + ' <span class="badge ' + r.status + '">' + r.status + '</span>';
  document.getElementById('note-input').value = r.note || '';

  const sourceLink = r.sourceUrl
    ? '<a href="' + r.sourceUrl + '" target="_blank" style="color:#3498db;font-size:0.8rem;align-self:center;margin-left:auto;">Open source record &rarr;</a>'
    : '';

  document.getElementById('record').innerHTML =
    '<div class="scan-panel">' +
      '<div class="scan-toolbar">' +
        '<button onclick="openLightbox()">Full Resolution (F)</button>' +
        sourceLink +
      '</div>' +
      '<div class="scan-container">' +
        '<img src="' + r._displayUrl + '" alt="Scan" onclick="openLightbox()">' +
      '</div>' +
    '</div>' +
    '<div class="info-panel">' +
      '<div class="card">' +
        '<h3>What to look for</h3>' +
        '<div class="expect-box"><p>' + r.expect + '</p></div>' +
      '</div>' +
      (r.aiAnalysis ?
        '<div class="card">' +
          '<h3>AI Analysis</h3>' +
          '<div class="ai-box">' +
            '<div class="confidence ' + (r.aiConfidence || 'medium') + '">' + (r.aiConfidenceText || '') + '</div>' +
            '<p>' + r.aiAnalysis + '</p>' +
          '</div>' +
        '</div>' : '') +
      '<div class="card">' +
        '<h3>Source Metadata</h3>' +
        '<table class="meta-table">' +
          Object.entries(r.metadata || {{}}).map(function(e) {{ return '<tr><td>' + e[0] + '</td><td>' + e[1] + '</td></tr>'; }}).join('') +
        '</table>' +
      '</div>' +
    '</div>';
  updateStats();
}}

// Pre-compute display/full URLs
records.forEach(r => {{
  if (LOCAL_IMAGES && r._localDisplay) {{
    r._displayUrl = r._localDisplay;
    r._fullUrl = r._localFull || r._localDisplay;
  }} else {{
    const url = r.iiifUrl || '';
    const m = url.match(/(https?:\\/\\/[^/]+\\/iiif\\/image\\/[\\d.]+\\/[^/]+)\\/.*/);
    if (m) {{
      r._displayUrl = m[1] + '/full/1200,/0/default.jpg';
      r._fullUrl = m[1] + '/full/max/0/default.jpg';
    }} else {{
      r._displayUrl = url;
      r._fullUrl = url;
    }}
  }}
}});

load();
render();
</script>
</body>
</html>"""


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    do_download = "--download" in flags

    input_path = Path(args[0])
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args[1]) if len(args) > 1 else input_path.with_suffix(".html")

    with open(input_path) as f:
        records = json.load(f)

    if not isinstance(records, list):
        print("Error: JSON must be an array of record objects", file=sys.stderr)
        sys.exit(1)

    if do_download:
        img_dir = output_path.parent / (output_path.stem + "_images")
        print(f"Downloading {len(records)} images to {img_dir}/...")
        download_images(records, img_dir)

    html = generate_html(records, local_images=do_download)
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Generated {output_path} with {len(records)} records")


if __name__ == "__main__":
    main()
