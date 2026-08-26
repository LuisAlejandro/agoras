# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Loopback Share-to-TikTok composer for interactive Direct Post."""

from __future__ import annotations

import html
import json
import mimetypes
import os
import re
import secrets
import sys
import time
import webbrowser
from dataclasses import dataclass, replace
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional, Sequence, Tuple, cast
from urllib.parse import parse_qs

from agoras.core.text_limits import TextValidationError, validate_text
from agoras.media.paths import is_local_media_source, normalize_media_path

# OAuth callback stays on this port. The composer must never bind it.
OAUTH_CALLBACK_PORT = 3456
COMPOSER_IDLE_TIMEOUT_SEC = 15 * 60
_PREVIEW_PATH = re.compile(r"^/preview/(\d+)$")
_BYTE_RANGE = re.compile(r"bytes=(\d*)-(\d*)\Z")

MUSIC_USAGE_URL = "https://www.tiktok.com/legal/page/global/music-usage-confirmation/en"
BRANDED_CONTENT_POLICY_URL = "https://www.tiktok.com/legal/page/global/bc-policy/en"

MUSIC_USAGE_CONSENT = f"By posting, you agree to TikTok's Music Usage Confirmation ({MUSIC_USAGE_URL})."
BRANDED_CONTENT_CONSENT = (
    "By posting, you agree to TikTok's Branded Content Policy "
    f"({BRANDED_CONTENT_POLICY_URL}) and Music Usage Confirmation "
    f"({MUSIC_USAGE_URL})."
)

PRIVACY_LABELS = {
    "PUBLIC_TO_EVERYONE": "Everyone",
    "MUTUAL_FOLLOW_FRIENDS": "Friends",
    "FOLLOWER_OF_CREATOR": "Followers",
    "SELF_ONLY": "Only me",
}

BRANDED_PRIVATE_HELPER = "Branded content visibility cannot be set to private"
COMMERCIAL_HELPER = "Select Your Brand and/or Branded Content to enable Publish."
PROCESSING_NOTICE = "Processing may take a few minutes. You can close this window and return to the terminal."


class ComposerValidationError(Exception):
    """Raised when a composer POST cannot be confirmed."""


@dataclass(frozen=True)
class ComposerRequest:
    """Inputs the CLI seeds into the composer page."""

    title: str
    nickname: str
    privacy_options: Sequence[str]
    comment_disabled: bool
    duet_disabled: bool
    stitch_disabled: bool
    kind: str
    preview_urls: Sequence[str]
    preview_ok: bool = True


@dataclass(frozen=True)
class ComposerPayload:
    """Creator-confirmed TikTok metadata. Media URLs stay on the CLI."""

    title: str
    privacy_level: str
    allow_comments: bool
    allow_duet: bool
    allow_stitch: bool
    brand_organic: bool
    brand_content: bool


class ComposerHTTPServer(HTTPServer):
    """HTTPServer that stores composer session state."""

    composer_request: ComposerRequest
    csrf_token: str
    payload: Optional[ComposerPayload]
    cancelled: bool
    error_message: Optional[str]
    preview_files: Tuple[Optional[str], ...]

    def __init__(self, server_address, RequestHandlerClass):
        """Initialize composer session fields."""
        super().__init__(server_address, RequestHandlerClass)
        self.composer_request = ComposerRequest(
            title="",
            nickname="",
            privacy_options=(),
            comment_disabled=False,
            duet_disabled=False,
            stitch_disabled=False,
            kind="video",
            preview_urls=(),
        )
        self.csrf_token = ""
        self.payload = None
        self.cancelled = False
        self.error_message = None
        self.preview_files = ()


def bind_preview_assets(sources: Sequence[str], port: int) -> Tuple[Tuple[str, ...], Tuple[Optional[str], ...]]:
    """Rewrite local preview sources to loopback /preview/N URLs.

    HTTP(s) URLs stay unchanged. Local paths and file:// URIs are served from
    the composer process so the browser can load them.
    """
    urls: List[str] = []
    files: List[Optional[str]] = []
    for index, source in enumerate(sources):
        if source and is_local_media_source(source):
            urls.append(f"http://127.0.0.1:{port}/preview/{index}")
            files.append(normalize_media_path(source))
        else:
            urls.append(source)
            files.append(None)
    return tuple(urls), tuple(files)


def _parse_byte_range(header: Optional[str], file_size: int) -> Optional[Tuple[int, int]]:
    """Return inclusive (start, end) for a single bytes Range, or None for full file."""
    if not header:
        return None
    match = _BYTE_RANGE.match(header.strip())
    if not match:
        return None
    start_s, end_s = match.groups()
    if start_s == "" and end_s == "":
        return None
    if start_s == "":
        suffix = int(end_s)
        if suffix <= 0:
            return None
        start = max(file_size - suffix, 0)
        end = file_size - 1
    else:
        start = int(start_s)
        end = int(end_s) if end_s else file_size - 1
    if start < 0 or start >= file_size or end < start:
        return None
    return start, min(end, file_size - 1)


def is_loopback_host(host_header: Optional[str]) -> bool:
    """Return True when Host is 127.0.0.1 or localhost, with an optional port."""
    if not host_header:
        return False
    host = host_header.split(":", 1)[0].strip().lower()
    return host in ("127.0.0.1", "localhost")


def is_allowed_origin(origin: Optional[str], port: int) -> bool:
    """Return True when Origin matches the loopback composer origin."""
    if not origin:
        return False
    allowed = {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}
    return origin.strip() in allowed


def flatten_form(raw: Dict[str, List[str]]) -> Dict[str, str]:
    """Take the last value for each form key."""
    return {key: values[-1] if values else "" for key, values in raw.items()}


def form_checked(form: Dict[str, str], name: str) -> bool:
    """Return True when a checkbox field was submitted."""
    value = form.get(name, "")
    return value not in ("", "0", "false", "False", "off")


def consent_copy(*, brand_content: bool) -> str:
    """Return the live Music Usage / Branded Content consent string."""
    if brand_content:
        return BRANDED_CONTENT_CONSENT
    return MUSIC_USAGE_CONSENT


def _validate_interaction_flags(
    request: ComposerRequest,
    allow_comments: bool,
    allow_duet: bool,
    allow_stitch: bool,
) -> None:
    """Reject interaction flags the creator_info snapshot would not allow."""
    if request.kind == "photo" and (allow_duet or allow_stitch):
        raise ComposerValidationError("Duet and Stitch are not available for photo posts.")
    if request.comment_disabled and allow_comments:
        raise ComposerValidationError("Comments are disabled for this creator.")
    if request.duet_disabled and allow_duet:
        raise ComposerValidationError("Duet is disabled for this creator.")
    if request.stitch_disabled and allow_stitch:
        raise ComposerValidationError("Stitch is disabled for this creator.")


def validate_confirm(form: Dict[str, str], request: ComposerRequest, csrf_token: str) -> ComposerPayload:
    """
    Validate a composer POST and return the confirm payload.

    Media URL fields in the form body are ignored. Privacy and commercial
    values that the creator_info snapshot would not allow are rejected.
    """
    submitted_csrf = form.get("csrf", "")
    if not csrf_token or submitted_csrf != csrf_token:
        raise ComposerValidationError("Invalid or missing confirmation token.")

    title = form.get("title", "")
    privacy_level = form.get("privacy_level", "").strip()
    allow_comments = form_checked(form, "allow_comments")
    allow_duet = form_checked(form, "allow_duet")
    allow_stitch = form_checked(form, "allow_stitch")
    brand_organic = form_checked(form, "brand_organic")
    brand_content = form_checked(form, "brand_content")
    commercial_on = form_checked(form, "commercial")
    consent = form_checked(form, "consent")
    if not commercial_on:
        brand_organic = False
        brand_content = False

    if not privacy_level:
        raise ComposerValidationError("Choose a privacy setting before publishing.")
    if privacy_level not in request.privacy_options:
        raise ComposerValidationError("That privacy setting is not available for this account.")

    _validate_interaction_flags(request, allow_comments, allow_duet, allow_stitch)

    if commercial_on and not brand_organic and not brand_content:
        raise ComposerValidationError(COMMERCIAL_HELPER)

    if brand_content and privacy_level == "SELF_ONLY":
        raise ComposerValidationError(BRANDED_PRIVATE_HELPER)

    if not consent:
        raise ComposerValidationError("Confirm the TikTok policy agreement before publishing.")

    if not request.preview_ok:
        raise ComposerValidationError("Preview failed to load. Publish is disabled.")

    title_mode = "photo" if request.kind == "photo" else "video"
    try:
        validate_text("tiktok", "title", title, mode=title_mode)
    except TextValidationError as exc:
        raise ComposerValidationError(f"Title exceeds the {exc.limit}-character TikTok {title_mode} limit.") from exc

    return ComposerPayload(
        title=title,
        privacy_level=privacy_level,
        allow_comments=allow_comments,
        allow_duet=False if request.kind == "photo" else allow_duet,
        allow_stitch=False if request.kind == "photo" else allow_stitch,
        brand_organic=brand_organic,
        brand_content=brand_content,
    )


def render_composer_html(request: ComposerRequest, csrf_token: str, error_message: Optional[str] = None) -> str:
    """Render the Share-to-TikTok page. Never includes secrets or media form fields."""
    nickname = html.escape(request.nickname or "TikTok creator")
    title_value = html.escape(request.title or "")
    error_block = ""
    if error_message:
        error_block = f'<p class="error" role="alert">{html.escape(error_message)}</p>'

    privacy_options_data = [
        {"value": option, "label": PRIVACY_LABELS.get(option, option)} for option in request.privacy_options
    ]
    privacy_options_json = json.dumps(privacy_options_data)
    preview_urls_json = json.dumps(list(request.preview_urls))

    preview_block = _render_preview(request)
    interaction_block = _render_interactions(request)
    preview_ok_json = "true" if request.preview_ok else "false"
    photo_json = "true" if request.kind == "photo" else "false"
    title_maxlength = 90 if request.kind == "photo" else 2200

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Share to TikTok — Agoras</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #f8f8f8; color: #111; margin: 0; padding: 24px; }}
    main {{ max-width: 560px; margin: 0 auto; background: #fff; padding: 28px; border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
    h1 {{ font-size: 1.4rem; font-weight: 600; margin: 0 0 8px; }}
    .nickname {{ color: #555; margin-bottom: 20px; }}
    label, .legend {{ display: block; font-weight: 500; margin: 16px 0 6px; }}
    input[type=text], select {{ width: 100%; padding: 8px; font-size: 1rem; box-sizing: border-box; }}
    .preview {{ margin: 16px 0; }}
    .preview img, .preview video {{ max-width: 100%; border-radius: 6px; background: #000; }}
    .photos {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .photos img {{ width: 120px; height: 120px; object-fit: cover; }}
    .row {{ display: flex; align-items: center; gap: 8px; margin: 8px 0; }}
    .helper {{ color: #8a1c1c; font-size: .9rem; display: none; }}
    .helper.visible {{ display: block; }}
    .error {{ color: #8a1c1c; }}
    .commercial-fields {{ display: none; margin-left: 8px; }}
    .commercial-fields.open {{ display: block; }}
    .actions {{ display: flex; gap: 12px; margin-top: 24px; }}
    button, .cancel {{ padding: 10px 16px; font-size: 1rem; cursor: pointer; }}
    button[type=submit] {{ background: #fe2c55; color: #fff; border: 0; border-radius: 4px; }}
    button[type=submit]:disabled {{ background: #ccc; cursor: not-allowed; }}
    .cancel {{
      background: transparent; border: 1px solid #ccc; text-decoration: none;
      color: #333; border-radius: 4px;
    }}
    .expiry {{ color: #666; font-size: .85rem; margin-top: 16px; }}
    .prompt {{ color: #444; font-size: .9rem; margin: 4px 0 12px; }}
  </style>
</head>
<body>
  <main>
    <h1>Share to TikTok</h1>
    <p class="nickname">Posting as {nickname}</p>
    {error_block}
    <form id="compose" method="post" action="/">
      <input type="hidden" name="csrf" value="{html.escape(csrf_token)}">
      <label for="title">Title</label>
      <input id="title" name="title" type="text" value="{title_value}" maxlength="{title_maxlength}">
      <div class="preview">{preview_block}</div>
      <label for="privacy_level">Who can watch this</label>
      <select id="privacy_level" name="privacy_level" required>
        <option value="" selected>Select privacy</option>
      </select>
      <p id="branded-private-helper" class="helper">{html.escape(BRANDED_PRIVATE_HELPER)}</p>
      {interaction_block}
      <div class="row">
        <input id="commercial" name="commercial" type="checkbox" value="1">
        <label for="commercial">This is commercial content</label>
      </div>
      <div id="commercial-fields" class="commercial-fields">
        <div class="row">
          <input id="brand_organic" name="brand_organic" type="checkbox" value="1">
          <label for="brand_organic">Your Brand</label>
        </div>
        <p class="prompt">Your photo/video will be labeled as 'Promotional content'.</p>
        <div class="row">
          <input id="brand_content" name="brand_content" type="checkbox" value="1">
          <label for="brand_content">Branded Content</label>
        </div>
        <p class="prompt">Your photo/video will be labeled as 'Paid partnership'.</p>
        <p id="commercial-helper" class="helper">{html.escape(COMMERCIAL_HELPER)}</p>
      </div>
      <div class="row">
        <input id="consent" name="consent" type="checkbox" value="1" required>
        <label id="consent-label" for="consent">{html.escape(MUSIC_USAGE_CONSENT)}</label>
      </div>
      <div class="actions">
        <button id="publish" type="submit" disabled>Publish</button>
        <a class="cancel" href="/cancel">Cancel</a>
      </div>
    </form>
    <p class="expiry">This page expires in <span id="countdown">15:00</span>.</p>
  </main>
  <script>
    const previewOk = {preview_ok_json};
    const isPhoto = {photo_json};
    const previewUrls = {preview_urls_json};
    const privacyOptionsData = {privacy_options_json};
    const musicConsent = {json.dumps(MUSIC_USAGE_CONSENT)};
    const brandedConsent = {json.dumps(BRANDED_CONTENT_CONSENT)};
    const privacy = document.getElementById('privacy_level');
    const previewEl = document.querySelector('.preview');
    const commercial = document.getElementById('commercial');
    const brandOrganic = document.getElementById('brand_organic');
    const brandContent = document.getElementById('brand_content');
    const consent = document.getElementById('consent');
    const consentLabel = document.getElementById('consent-label');
    const publish = document.getElementById('publish');
    const commercialFields = document.getElementById('commercial-fields');
    const brandedHelper = document.getElementById('branded-private-helper');
    const commercialHelper = document.getElementById('commercial-helper');
    for (const opt of privacyOptionsData) {{
      const option = document.createElement('option');
      option.value = opt.value;
      option.textContent = opt.label;
      privacy.appendChild(option);
    }}
    let onlyMeOption = Array.from(privacy.options).find(o => o.value === 'SELF_ONLY');
    let previewFailed = !previewOk;

    function attachPreviewError(el) {{
      el.addEventListener('error', () => {{
        previewFailed = true;
        publish.disabled = true;
        const err = document.createElement('p');
        err.className = 'error';
        err.setAttribute('role', 'alert');
        err.textContent = 'Preview failed to load. Publish is disabled.';
        el.replaceWith(err);
        update();
      }});
    }}

    if (previewOk && previewUrls.length && !previewEl.querySelector('.error')) {{
      if (isPhoto) {{
        const photos = document.createElement('div');
        photos.className = 'photos';
        for (const url of previewUrls) {{
          const img = document.createElement('img');
          img.src = url;
          img.alt = 'Photo preview';
          attachPreviewError(img);
          photos.appendChild(img);
        }}
        previewEl.appendChild(photos);
      }} else {{
        const video = document.createElement('video');
        video.controls = true;
        video.src = previewUrls[0];
        attachPreviewError(video);
        previewEl.appendChild(video);
      }}
    }}

    function update() {{
      if (!commercial.checked) {{
        brandOrganic.checked = false;
        brandContent.checked = false;
      }}
      const branded = brandContent.checked;
      commercialFields.classList.toggle('open', commercial.checked);
      if (branded && privacy.value === 'SELF_ONLY') {{
        privacy.value = '';
      }}
      if (onlyMeOption) {{
        onlyMeOption.disabled = branded;
      }}
      brandedHelper.classList.toggle('visible', branded);
      brandContent.disabled = privacy.value === 'SELF_ONLY';
      const commercialIncomplete = commercial.checked && !brandOrganic.checked && !brandContent.checked;
      commercialHelper.classList.toggle('visible', commercialIncomplete);
      const nextConsent = branded ? brandedConsent : musicConsent;
      if (consentLabel.dataset.copy !== nextConsent) {{
        consentLabel.textContent = nextConsent;
        consentLabel.dataset.copy = nextConsent;
        consent.checked = false;
      }}
      const canPublish = previewOk && !previewFailed
        && privacy.value
        && consent.checked
        && !commercialIncomplete;
      publish.disabled = !canPublish;
    }}

    ['change', 'input'].forEach((evt) => {{
      document.getElementById('compose').addEventListener(evt, update);
    }});
    update();

    let remaining = {COMPOSER_IDLE_TIMEOUT_SEC};
    const countdown = document.getElementById('countdown');
    setInterval(() => {{
      remaining -= 1;
      if (remaining < 0) remaining = 0;
      const m = String(Math.floor(remaining / 60)).padStart(2, '0');
      const s = String(remaining % 60).padStart(2, '0');
      countdown.textContent = m + ':' + s;
    }}, 1000);
  </script>
</body>
</html>
"""


def render_processing_html() -> str:
    """Render the post-confirm processing notice."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Share to TikTok — Agoras</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #f8f8f8; color: #111;
           display: flex; min-height: 100vh; align-items: center; justify-content: center; }}
    main {{ background: #fff; padding: 40px; max-width: 480px; text-align: center; border-radius: 8px; }}
  </style>
</head>
<body>
  <main>
    <h1>Uploading to TikTok</h1>
    <p>{html.escape(PROCESSING_NOTICE)}</p>
  </main>
</body>
</html>
"""


def render_cancelled_html() -> str:
    """Render the cancel page."""
    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Cancelled — Agoras</title></head>
<body><main><h1>Publish cancelled</h1><p>You can close this window and return to the terminal.</p></main></body>
</html>
"""


def _render_preview(request: ComposerRequest) -> str:
    """Render preview error markup when preview cannot load; media is built in JS."""
    if not request.preview_ok or not request.preview_urls:
        return '<p class="error" role="alert">Preview failed to load. Publish is disabled.</p>'
    return ""


def _render_interactions(request: ComposerRequest) -> str:
    """Render unchecked interaction boxes; omit duet/stitch for photos."""
    comment_disabled = " disabled" if request.comment_disabled else ""
    rows = [
        '<p class="legend">Interactions</p>',
        (
            f'<div class="row"><input id="allow_comments" name="allow_comments" '
            f'type="checkbox" value="1"{comment_disabled}>'
            f'<label for="allow_comments">Allow comments</label></div>'
        ),
    ]
    if request.kind != "photo":
        duet_disabled = " disabled" if request.duet_disabled else ""
        stitch_disabled = " disabled" if request.stitch_disabled else ""
        rows.append(
            f'<div class="row"><input id="allow_duet" name="allow_duet" '
            f'type="checkbox" value="1"{duet_disabled}>'
            f'<label for="allow_duet">Allow Duet</label></div>'
        )
        rows.append(
            f'<div class="row"><input id="allow_stitch" name="allow_stitch" '
            f'type="checkbox" value="1"{stitch_disabled}>'
            f'<label for="allow_stitch">Allow Stitch</label></div>'
        )
    return "\n".join(rows)


class ComposerHandler(BaseHTTPRequestHandler):
    """HTTP handler for the Share-to-TikTok composer."""

    def log_message(self, format, *args):
        """Suppress default HTTP server logging so tokens never hit logs."""

    def do_GET(self):
        """Serve the composer page, local preview bytes, or cancel."""
        server = cast(ComposerHTTPServer, self.server)
        if not is_loopback_host(self.headers.get("Host")):
            self._send_plain(403, "Forbidden")
            return
        path = self.path.split("?", 1)[0]
        if path == "/cancel":
            server.cancelled = True
            self._send_html(200, render_cancelled_html())
            return
        preview_match = _PREVIEW_PATH.fullmatch(path)
        if preview_match:
            self._serve_preview(server, int(preview_match.group(1)))
            return
        if path != "/":
            self._send_plain(404, "Not found")
            return
        self._send_html(200, render_composer_html(server.composer_request, server.csrf_token, server.error_message))

    def do_POST(self):
        """Validate confirm or cancel. Media URLs in the body are ignored."""
        server = cast(ComposerHTTPServer, self.server)
        if not is_loopback_host(self.headers.get("Host")):
            self._send_plain(403, "Forbidden")
            return
        if not is_allowed_origin(self.headers.get("Origin"), server.server_port):
            self._send_plain(403, "Forbidden")
            return
        path = self.path.split("?", 1)[0]
        if path != "/":
            self._send_plain(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length).decode("utf-8") if length else ""
        form = flatten_form(parse_qs(body, keep_blank_values=True))
        if form.get("action") == "cancel":
            server.cancelled = True
            self._send_html(200, render_cancelled_html())
            return
        try:
            payload = validate_confirm(form, server.composer_request, server.csrf_token)
        except ComposerValidationError as exc:
            server.error_message = str(exc)
            self._send_html(400, render_composer_html(server.composer_request, server.csrf_token, str(exc)))
            return
        server.csrf_token = ""
        self._send_html(200, render_processing_html())
        server.payload = payload

    def _serve_preview(self, server: ComposerHTTPServer, index: int) -> None:
        """Serve an allowlisted local preview file (loopback Host already checked)."""
        if index < 0 or index >= len(server.preview_files):
            self._send_plain(404, "Not found")
            return
        filepath = server.preview_files[index]
        if not filepath or not os.path.isfile(filepath):
            self._send_plain(404, "Not found")
            return
        file_size = os.path.getsize(filepath)
        byte_range = _parse_byte_range(self.headers.get("Range"), file_size)
        if self.headers.get("Range") and byte_range is None:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()
            return
        if byte_range is None:
            start, end, status = 0, file_size - 1, 200
        else:
            start, end, status = byte_range[0], byte_range[1], 206
        length = max(end - start + 1, 0) if file_size else 0
        content_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.end_headers()
        if length == 0:
            return
        with open(filepath, "rb") as handle:
            handle.seek(start)
            remaining = length
            while remaining > 0:
                chunk = handle.read(min(65536, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def _send_html(self, status: int, body: str):
        """Send an HTML response."""
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(encoded)

    def _send_plain(self, status: int, body: str):
        """Send a plain-text response."""
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(encoded)


def bind_composer_server() -> ComposerHTTPServer:
    """Bind HTTP on 127.0.0.1 with an ephemeral port that is not 3456."""
    for _ in range(8):
        server = ComposerHTTPServer(("127.0.0.1", 0), ComposerHandler)
        if server.server_port != OAUTH_CALLBACK_PORT:
            return server
        server.server_close()
    raise RuntimeError("Could not bind TikTok composer to a free loopback port")


def run_composer(
    request: ComposerRequest,
    timeout: int = COMPOSER_IDLE_TIMEOUT_SEC,
    open_browser: bool = True,
) -> Optional[ComposerPayload]:
    """
    Serve the Share-to-TikTok page and wait for confirm, cancel, or timeout.

    Returns:
        ComposerPayload on confirm, None on cancel or idle timeout.
    """
    server = bind_composer_server()
    preview_urls, preview_files = bind_preview_assets(request.preview_urls, server.server_port)
    server.composer_request = replace(request, preview_urls=preview_urls)
    server.preview_files = preview_files
    server.csrf_token = secrets.token_urlsafe(32)
    server.payload = None
    server.cancelled = False
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Share to TikTok: {url}", file=sys.stderr)
    print("Open that URL if your browser does not.", file=sys.stderr)
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    start = time.time()
    try:
        while True:
            if time.time() - start >= timeout:
                return None
            remaining = timeout - (time.time() - start)
            server.timeout = min(remaining, 1.0)
            server.handle_request()
            if server.payload is not None or server.cancelled:
                break
        return server.payload
    finally:
        server.server_close()


def composer_from_creator_info(
    creator_info: Dict[str, Any],
    *,
    title: str,
    kind: str,
    preview_urls: Sequence[str],
    preview_ok: bool = True,
) -> ComposerRequest:
    """Build a composer request from a live creator_info snapshot."""
    options = creator_info.get("privacy_level_options") or []
    return ComposerRequest(
        title=title,
        nickname=str(creator_info.get("creator_nickname") or ""),
        privacy_options=tuple(str(option) for option in options),
        comment_disabled=bool(creator_info.get("comment_disabled")),
        duet_disabled=bool(creator_info.get("duet_disabled")),
        stitch_disabled=bool(creator_info.get("stitch_disabled")),
        kind=kind,
        preview_urls=tuple(preview_urls),
        preview_ok=preview_ok,
    )
