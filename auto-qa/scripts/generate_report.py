#!/usr/bin/env python3
"""
Generate HTML QA report from a JSON issues file.

Usage:
  python3 generate_report.py <issues.json> [output.html]

issues.json format:
[
  {
    "id": "ISS-1",
    "title": "Issue title",
    "severity": "high|mid|low",
    "category": "crash|function|ux|security|performance",
    "location": "path/to/file.tsx",
    "description": "What went wrong",
    "cause": "Root cause",
    "fix": "What was fixed",
    "status": "fixed|open|skipped",
    "commit_hash": "abc1234",
    "commit_message": "fix: description of the fix",
    "linear_id": "TEAM-123",
    "linear_url": "https://linear.app/...",
    "screenshots_before": ["path/to/before.png"],
    "screenshots_after": ["path/to/after.png"],
    "recording_before": "path/to/before.gif",
    "recording_after": "path/to/after.gif"
  }
]
"""

import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def encode_media(path: str) -> tuple[str, str]:
    """Encode a file to base64, return (data_uri, media_type)."""
    if not path or not os.path.exists(path):
        return "", ""
    ext = Path(path).suffix.lower()
    mime_map = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".webm": "video/webm", ".mp4": "video/mp4",
    }
    mime = mime_map.get(ext, "application/octet-stream")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}", mime


def media_tag(path: str, alt: str = "") -> str:
    """Generate an <img> or <video> tag for a media file."""
    if not path or not os.path.exists(path):
        return ""
    data_uri, mime = encode_media(path)
    if not data_uri:
        return ""
    if mime.startswith("video/"):
        return f'<video src="{data_uri}" controls class="screenshot" loading="lazy"></video>'
    return f'<img src="{data_uri}" alt="{alt}" class="screenshot" loading="lazy">'


def generate_html(issues: list[dict], meta: dict | None = None) -> str:
    meta = meta or {}
    date = meta.get("date", datetime.now().strftime("%Y-%m-%d"))
    branch = meta.get("branch", "")
    tester = meta.get("tester", "Claude QA Agent")
    app_url = meta.get("app_url", "")
    title = meta.get("title", "QA Test Report")

    total = len(issues)
    fixed = sum(1 for i in issues if i.get("status") == "fixed")
    open_count = sum(1 for i in issues if i.get("status") == "open")
    skipped = sum(1 for i in issues if i.get("status") == "skipped")

    severity_counts = {}
    category_counts = {}
    for issue in issues:
        s = issue.get("severity", "mid")
        c = issue.get("category", "other")
        severity_counts[s] = severity_counts.get(s, 0) + 1
        category_counts[c] = category_counts.get(c, 0) + 1

    # Build issue cards
    issue_cards = ""
    for issue in issues:
        sev = issue.get("severity", "mid")
        sev_class = f"severity-{sev}"
        sev_badge = f'<span class="badge badge-severity-{sev}">{sev.upper()}</span>'
        status = issue.get("status", "open")
        status_badge = f'<span class="badge badge-{"fixed" if status == "fixed" else "open"}">{status.upper()}</span>'
        cat = issue.get("category", "")
        cat_badge = f'<span class="badge badge-type">{cat}</span>' if cat else ""
        linear_link = ""
        if issue.get("linear_id"):
            url = issue.get("linear_url", "#")
            linear_link = f'<a href="{url}" target="_blank" class="badge badge-linear">{issue["linear_id"]}</a>'

        # Commit hash section
        commit_html = ""
        commit_hash = issue.get("commit_hash", "")
        commit_msg = issue.get("commit_message", "")
        if commit_hash:
            short_hash = commit_hash[:9]
            commit_html = f'''
        <h4>Commit</h4>
        <div class="commit-row">
          <code class="commit-hash" id="hash-{issue.get("id","")}">{short_hash}</code>
          <button class="copy-btn" onclick="copyHash('{commit_hash}', this)" title="Copy full hash">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
          </button>
          {"<span class='commit-msg'>" + commit_msg + "</span>" if commit_msg else ""}
        </div>'''

        # Media sections
        media_html = ""
        before_imgs = issue.get("screenshots_before", [])
        after_imgs = issue.get("screenshots_after", [])
        rec_before = issue.get("recording_before", "")
        rec_after = issue.get("recording_after", "")

        if before_imgs or after_imgs or rec_before or rec_after:
            media_html += '<h4>Evidence</h4>'
            if rec_before or rec_after:
                media_html += '<div class="screenshot-group">'
                if rec_before:
                    media_html += f'<div class="screenshot-wrap"><div class="label before">BEFORE</div>{media_tag(rec_before, "before")}</div>'
                if rec_after:
                    media_html += f'<div class="screenshot-wrap"><div class="label after">AFTER</div>{media_tag(rec_after, "after")}</div>'
                media_html += '</div>'
            if before_imgs or after_imgs:
                cols = "1fr 1fr" if before_imgs and after_imgs else "1fr"
                media_html += f'<div class="screenshot-group" style="grid-template-columns:{cols}">'
                for img in before_imgs:
                    media_html += f'<div class="screenshot-wrap"><div class="label before">BEFORE</div>{media_tag(img, "before")}</div>'
                for img in after_imgs:
                    media_html += f'<div class="screenshot-wrap"><div class="label after">AFTER</div>{media_tag(img, "after")}</div>'
                media_html += '</div>'

        issue_cards += f'''
    <div class="issue-card {sev_class}">
      <div class="issue-header" onclick="this.parentElement.classList.toggle('open')">
        <span class="issue-title">{issue.get("id","")} {issue.get("title","")}</span>
        <div class="issue-badges">{sev_badge}{cat_badge}{status_badge}{linear_link}<span class="toggle-icon">▼</span></div>
      </div>
      <div class="issue-body">
        <h4>Location</h4><p><code>{issue.get("location","")}</code></p>
        <h4>Description</h4><p>{issue.get("description","")}</p>
        {"<h4>Root Cause</h4><p>" + issue.get("cause","") + "</p>" if issue.get("cause") else ""}
        {"<h4>Fix</h4><p>" + issue.get("fix","") + "</p>" if issue.get("fix") else ""}
        {commit_html}
        {media_html}
      </div>
    </div>'''

    # Category table rows
    cat_rows = "".join(
        f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in sorted(category_counts.items())
    )

    # Commit summary table (only issues with commit_hash)
    issues_with_commits = [i for i in issues if i.get("commit_hash")]
    commit_table = ""
    if issues_with_commits:
        commit_rows = ""
        for i in issues_with_commits:
            short = i["commit_hash"][:9]
            full = i["commit_hash"]
            commit_rows += f'''<tr>
              <td><code>{i.get("id","")}</code></td>
              <td class="commit-cell">
                <code class="commit-hash">{short}</code>
                <button class="copy-btn" onclick="copyHash('{full}', this)" title="Copy full hash">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                </button>
              </td>
              <td>{i.get("commit_message","")}</td>
              <td><span class="badge badge-severity-{i.get("severity","mid")}">{i.get("severity","mid").upper()}</span></td>
            </tr>'''

        commit_table = f'''
  <div class="section">
    <h2 class="section-title">Commits</h2>
    <div style="background:#fff;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.08);overflow:hidden">
      <table>
        <thead><tr><th>Issue</th><th>Commit</th><th>Message</th><th>Severity</th></tr></thead>
        <tbody>{commit_rows}</tbody>
      </table>
    </div>
    <div style="margin-top:.75rem;display:flex;gap:.5rem">
      <button class="btn-copy-all" onclick="copyAllHashes()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
        Copy all hashes
      </button>
      <button class="btn-copy-all" onclick="copyCherryPick()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v8m-4-4h8"/></svg>
        Copy cherry-pick command
      </button>
    </div>
  </div>'''

    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
:root{{--purple:#7c3aed;--purple-light:#ede9fe;--purple-dark:#5b21b6;--green:#10b981;--green-light:#d1fae5;--red:#ef4444;--red-light:#fee2e2;--orange:#f59e0b;--orange-light:#fef3c7;--gray-50:#f9fafb;--gray-100:#f3f4f6;--gray-200:#e5e7eb;--gray-500:#6b7280;--gray-700:#374151;--gray-900:#111827}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Noto Sans KR',sans-serif;background:var(--gray-50);color:var(--gray-900);line-height:1.6}}
.header{{background:linear-gradient(135deg,var(--purple),var(--purple-dark));color:#fff;padding:3rem 2rem;text-align:center}}
.header h1{{font-size:2rem;margin-bottom:.5rem}}
.header .subtitle{{opacity:.9;font-size:1rem}}
.header .meta{{margin-top:1.5rem;display:flex;justify-content:center;gap:2rem;flex-wrap:wrap}}
.header .meta-item{{background:rgba(255,255,255,.15);padding:.5rem 1rem;border-radius:8px;font-size:.875rem}}
.container{{max-width:1100px;margin:0 auto;padding:2rem 1rem}}
.summary-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:2rem}}
.summary-card{{background:#fff;border-radius:12px;padding:1.5rem;box-shadow:0 1px 3px rgba(0,0,0,.08);text-align:center}}
.summary-card .number{{font-size:2.5rem;font-weight:700;color:var(--purple)}}
.summary-card .label{{color:var(--gray-500);font-size:.875rem}}
.summary-card.green .number{{color:var(--green)}}
.summary-card.red .number{{color:var(--red)}}
.summary-card.orange .number{{color:var(--orange)}}
.section{{margin-bottom:2rem}}
.section-title{{font-size:1.5rem;font-weight:700;margin-bottom:1rem;padding-bottom:.5rem;border-bottom:2px solid var(--purple-light);color:var(--purple-dark)}}
.issue-card{{background:#fff;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.08);margin-bottom:1.5rem;overflow:hidden;border-left:4px solid var(--purple)}}
.issue-card.severity-high{{border-left-color:var(--red)}}
.issue-card.severity-mid{{border-left-color:var(--orange)}}
.issue-card.severity-low{{border-left-color:var(--green)}}
.issue-header{{padding:1rem 1.5rem;display:flex;justify-content:space-between;align-items:center;cursor:pointer;user-select:none}}
.issue-header:hover{{background:var(--gray-50)}}
.issue-title{{font-weight:600;font-size:1rem}}
.issue-badges{{display:flex;gap:.5rem;flex-shrink:0;flex-wrap:wrap}}
.badge{{font-size:.7rem;padding:.2rem .6rem;border-radius:999px;font-weight:600;text-transform:uppercase;text-decoration:none}}
.badge-fixed{{background:var(--green-light);color:#065f46}}
.badge-open{{background:var(--red-light);color:#991b1b}}
.badge-severity-high{{background:var(--red-light);color:#991b1b}}
.badge-severity-mid{{background:var(--orange-light);color:#92400e}}
.badge-severity-low{{background:var(--green-light);color:#065f46}}
.badge-type{{background:var(--purple-light);color:var(--purple-dark)}}
.badge-linear{{background:#5e6ad2;color:#fff}}
.issue-body{{padding:0 1.5rem 1.5rem;display:none}}
.issue-card.open .issue-body{{display:block}}
.issue-card.open .toggle-icon{{transform:rotate(180deg)}}
.toggle-icon{{transition:transform .2s;color:var(--gray-500)}}
.issue-body h4{{font-size:.85rem;color:var(--gray-500);margin:1rem 0 .25rem;text-transform:uppercase;letter-spacing:.05em}}
.issue-body h4:first-child{{margin-top:0}}
.issue-body p{{font-size:.9rem;color:var(--gray-700)}}
.commit-row{{display:flex;align-items:center;gap:.5rem;margin:.25rem 0}}
.commit-hash{{background:var(--gray-100);padding:.2rem .5rem;border-radius:4px;font-size:.85rem;color:var(--purple-dark);font-family:'SF Mono',Menlo,Monaco,monospace}}
.commit-msg{{font-size:.85rem;color:var(--gray-500)}}
.commit-cell{{display:flex;align-items:center;gap:.35rem}}
.copy-btn{{background:none;border:1px solid var(--gray-200);border-radius:4px;padding:3px 5px;cursor:pointer;color:var(--gray-500);display:inline-flex;align-items:center;transition:all .15s}}
.copy-btn:hover{{background:var(--purple-light);color:var(--purple-dark);border-color:var(--purple)}}
.copy-btn.copied{{background:var(--green-light);color:#065f46;border-color:var(--green)}}
.btn-copy-all{{background:#fff;border:1px solid var(--gray-200);border-radius:8px;padding:.5rem 1rem;cursor:pointer;font-size:.85rem;color:var(--gray-700);display:inline-flex;align-items:center;gap:.4rem;transition:all .15s}}
.btn-copy-all:hover{{background:var(--purple-light);color:var(--purple-dark);border-color:var(--purple)}}
.btn-copy-all.copied{{background:var(--green-light);color:#065f46;border-color:var(--green)}}
.screenshot-group{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:.75rem 0}}
.screenshot-wrap{{text-align:center}}
.screenshot-wrap .label{{font-size:.75rem;font-weight:600;margin-bottom:.25rem;text-transform:uppercase}}
.screenshot-wrap .label.before{{color:var(--red)}}
.screenshot-wrap .label.after{{color:var(--green)}}
.screenshot,.screenshot-wrap video{{max-width:100%;border-radius:8px;border:1px solid var(--gray-200);box-shadow:0 2px 8px rgba(0,0,0,.06);cursor:pointer;transition:transform .2s}}
.screenshot:hover{{transform:scale(1.02)}}
table{{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.9rem}}
th,td{{padding:.75rem 1rem;text-align:left;border-bottom:1px solid var(--gray-200)}}
th{{background:var(--gray-100);font-weight:600;color:var(--gray-700)}}
.lightbox{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.85);z-index:1000;justify-content:center;align-items:center;cursor:pointer}}
.lightbox.active{{display:flex}}
.lightbox img,.lightbox video{{max-width:95%;max-height:95%;border-radius:8px}}
.toast{{position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);background:var(--gray-900);color:#fff;padding:.6rem 1.2rem;border-radius:8px;font-size:.85rem;opacity:0;transition:opacity .2s;pointer-events:none;z-index:2000}}
.toast.show{{opacity:1}}
@media(max-width:768px){{.screenshot-group{{grid-template-columns:1fr}}.summary-grid{{grid-template-columns:1fr 1fr}}}}
</style>
</head>
<body>
<div class="header">
  <h1>{title}</h1>
  <div class="subtitle">Auto-QA Black-box Testing Report</div>
  <div class="meta">
    <div class="meta-item">Date: {date}</div>
    {"<div class='meta-item'>Branch: " + branch + "</div>" if branch else ""}
    <div class="meta-item">Tester: {tester}</div>
    {"<div class='meta-item'>URL: " + app_url + "</div>" if app_url else ""}
  </div>
</div>
<div class="container">
  <div class="summary-grid">
    <div class="summary-card"><div class="number">{total}</div><div class="label">Total Issues</div></div>
    <div class="summary-card green"><div class="number">{fixed}</div><div class="label">Fixed</div></div>
    <div class="summary-card red"><div class="number">{open_count}</div><div class="label">Open</div></div>
    <div class="summary-card orange"><div class="number">{skipped}</div><div class="label">Skipped (Duplicate)</div></div>
  </div>
  {commit_table}
  <div class="section">
    <h2 class="section-title">Category Breakdown</h2>
    <div style="background:#fff;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.08);overflow:hidden">
      <table><thead><tr><th>Category</th><th>Count</th></tr></thead><tbody>{cat_rows}</tbody></table>
    </div>
  </div>
  <div class="section">
    <h2 class="section-title">Issues</h2>
    {issue_cards}
  </div>
</div>
<div class="lightbox" id="lightbox" onclick="this.classList.remove('active')">
  <img id="lightbox-img" src="" alt="">
</div>
<div class="toast" id="toast"></div>
<script>
const ALL_HASHES = {json.dumps([i["commit_hash"] for i in issues_with_commits])};

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1500);
}}

function copyHash(hash, btn) {{
  navigator.clipboard.writeText(hash).then(() => {{
    btn.classList.add('copied');
    showToast('Copied: ' + hash.slice(0, 9));
    setTimeout(() => btn.classList.remove('copied'), 1200);
  }});
}}

function copyAllHashes() {{
  const text = ALL_HASHES.join('\\n');
  navigator.clipboard.writeText(text).then(() => {{
    const btn = event.currentTarget;
    btn.classList.add('copied');
    showToast('Copied ' + ALL_HASHES.length + ' hashes');
    setTimeout(() => btn.classList.remove('copied'), 1200);
  }});
}}

function copyCherryPick() {{
  const cmd = 'git cherry-pick ' + ALL_HASHES.join(' ');
  navigator.clipboard.writeText(cmd).then(() => {{
    const btn = event.currentTarget;
    btn.classList.add('copied');
    showToast('Copied cherry-pick command');
    setTimeout(() => btn.classList.remove('copied'), 1200);
  }});
}}

document.querySelectorAll('.screenshot').forEach(img => {{
  img.addEventListener('click', () => {{
    const lb = document.getElementById('lightbox');
    document.getElementById('lightbox-img').src = img.src;
    lb.classList.add('active');
  }});
}});
</script>
</body>
</html>'''


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_report.py <issues.json> [output.html] [meta.json]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    issues = data if isinstance(data, list) else data.get("issues", [])
    meta = data.get("meta", {}) if isinstance(data, dict) else {}

    if len(sys.argv) >= 4:
        with open(sys.argv[3]) as f:
            meta = json.load(f)

    output = sys.argv[2] if len(sys.argv) >= 3 else "qa-report.html"
    html = generate_html(issues, meta)

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = os.path.getsize(output) / 1024 / 1024
    print(f"Report: {output} ({size_mb:.1f} MB, {len(issues)} issues)")


if __name__ == "__main__":
    main()
