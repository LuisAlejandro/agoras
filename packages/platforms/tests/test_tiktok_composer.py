# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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

"""Tests for the localhost Share-to-TikTok composer."""

import http.client
import threading

import pytest

from agoras.platforms.tiktok.composer import (
    BRANDED_CONTENT_CONSENT,
    BRANDED_PRIVATE_HELPER,
    COMMERCIAL_HELPER,
    COMPOSER_IDLE_TIMEOUT_SEC,
    MUSIC_USAGE_CONSENT,
    OAUTH_CALLBACK_PORT,
    PROCESSING_NOTICE,
    ComposerRequest,
    ComposerValidationError,
    bind_composer_server,
    bind_preview_assets,
    composer_from_creator_info,
    flatten_form,
    is_allowed_origin,
    is_loopback_host,
    render_composer_html,
    render_processing_html,
    validate_confirm,
)


def _request(**overrides):
    """Build a composer request for tests."""
    data = dict(
        title="Seeded title",
        nickname="Ada",
        privacy_options=("PUBLIC_TO_EVERYONE", "SELF_ONLY"),
        comment_disabled=False,
        duet_disabled=False,
        stitch_disabled=False,
        kind="video",
        preview_urls=("https://luisalejandro.org/files/videos/test.mp4",),
        preview_ok=True,
    )
    data.update(overrides)
    return ComposerRequest(**data)


def _form(**overrides):
    """Build a confirm form dict."""
    data = {
        "csrf": "token",
        "title": "Edited title",
        "privacy_level": "SELF_ONLY",
        "consent": "1",
    }
    data.update(overrides)
    return data


def test_composer_html_has_editable_title_and_empty_privacy():
    """Composer HTML seeds title and does not preselect privacy."""
    html = render_composer_html(_request(), "csrf-token")
    assert 'name="title"' in html
    assert 'value="Seeded title"' in html
    assert "Posting as Ada" in html
    assert '<option value="" selected>Select privacy</option>' in html
    assert "SELF_ONLY" in html
    assert "Only me" in html
    assert "selected>Only me" not in html
    assert "Allow comments" in html
    assert "Allow Duet" in html
    assert "This is commercial content" in html
    assert MUSIC_USAGE_CONSENT in html
    assert PROCESSING_NOTICE not in html
    assert "csrf-token" in html
    assert "video_url" not in html.split('name="')[0] or 'name="video_url"' not in html


def test_composer_html_photos_omit_duet_stitch_and_grey_disabled_flags():
    """Photos omit Duet/Stitch; disabled creator flags are greyed."""
    html = render_composer_html(
        _request(kind="photo", comment_disabled=True, preview_urls=("https://example.com/a.jpg",)),
        "csrf",
    )
    assert "Allow comments" in html
    assert "disabled" in html
    assert "Allow Duet" not in html
    assert "Allow Stitch" not in html


def test_composer_html_only_self_only_still_has_empty_default():
    """Even when the only option is SELF_ONLY, privacy stays unselected."""
    html = render_composer_html(_request(privacy_options=("SELF_ONLY",)), "csrf")
    assert '<option value="" selected>Select privacy</option>' in html
    assert html.count("selected") >= 1


def test_composer_html_clears_only_me_before_disabling_it():
    """Branded content must clear Only me before disabling that option."""
    html = render_composer_html(_request(), "csrf")
    clear_at = html.find("privacy.value = ''")
    disable_at = html.find("onlyMeOption.disabled = branded")
    assert clear_at != -1
    assert disable_at != -1
    assert clear_at < disable_at
    assert 'value="" selected disabled>' not in html


def test_validate_confirm_requires_privacy_and_returns_edited_title():
    """Missing privacy is rejected; edited title is in the payload."""
    request = _request()
    with pytest.raises(ComposerValidationError, match="privacy"):
        validate_confirm(_form(privacy_level=""), request, "token")

    payload = validate_confirm(_form(title="New title"), request, "token")
    assert payload.title == "New title"
    assert payload.privacy_level == "SELF_ONLY"


def test_validate_confirm_rejects_branded_self_only():
    """Branded content cannot confirm with Only me."""
    with pytest.raises(ComposerValidationError, match="private"):
        validate_confirm(
            _form(commercial="1", brand_content="1", privacy_level="SELF_ONLY"),
            _request(),
            "token",
        )


def test_validate_confirm_ignores_form_video_url():
    """Extra media URL fields must not enter the payload."""
    payload = validate_confirm(
        _form(video_url="https://evil.example/steal.mp4"),
        _request(),
        "token",
    )
    assert not hasattr(payload, "video_url")
    assert payload.title == "Edited title"


def test_validate_confirm_csrf_missing_and_replay():
    """CSRF missing or mismatched is rejected."""
    request = _request()
    with pytest.raises(ComposerValidationError, match="token"):
        validate_confirm(_form(csrf=""), request, "token")
    with pytest.raises(ComposerValidationError, match="token"):
        validate_confirm(_form(csrf="other"), request, "token")


def test_validate_confirm_commercial_neither_box():
    """Commercial toggle with neither disclosure box cannot confirm."""
    with pytest.raises(ComposerValidationError, match="Your Brand"):
        validate_confirm(_form(commercial="1"), _request(), "token")
    assert COMMERCIAL_HELPER


def test_validate_confirm_commercial_off_zeros_brand_flags():
    """Commercial omitted or off drops leftover Your Brand / Branded Content flags."""
    payload = validate_confirm(
        _form(brand_organic="1", brand_content="1"),
        _request(),
        "token",
    )
    assert payload.brand_organic is False
    assert payload.brand_content is False

    payload_off = validate_confirm(
        _form(commercial="0", brand_organic="1", brand_content="1"),
        _request(),
        "token",
    )
    assert payload_off.brand_organic is False
    assert payload_off.brand_content is False


def test_composer_html_unchecks_brand_when_commercial_off():
    """Composer JS unchecks brand boxes when commercial content is off."""
    html = render_composer_html(_request(), "csrf")
    assert "if (!commercial.checked)" in html
    assert "brandOrganic.checked = false" in html
    assert "brandContent.checked = false" in html


def test_composer_html_title_maxlength_matches_kind():
    """Photo titles cap at 90 runes; video titles keep 2200."""
    video_html = render_composer_html(_request(kind="video"), "csrf")
    photo_html = render_composer_html(
        _request(kind="photo", preview_urls=("https://example.com/a.jpg",)),
        "csrf",
    )
    assert 'maxlength="2200"' in video_html
    assert 'maxlength="90"' in photo_html
    assert 'maxlength="90"' not in video_html


def test_validate_confirm_rejects_photo_title_over_90():
    """Photo composer rejects titles over the 90-rune limit before confirm."""
    with pytest.raises(ComposerValidationError, match="90"):
        validate_confirm(_form(title="a" * 91), _request(kind="photo"), "token")


def test_validate_confirm_allows_video_title_of_91():
    """Video composer still accepts a 91-character title."""
    payload = validate_confirm(_form(title="a" * 91), _request(kind="video"), "token")
    assert payload.title == "a" * 91


def test_validate_confirm_disabled_interactions_and_photo_duet():
    """Creator-disabled flags and photo duet/stitch cannot confirm."""
    with pytest.raises(ComposerValidationError, match="Comments are disabled"):
        validate_confirm(_form(allow_comments="1"), _request(comment_disabled=True), "token")
    with pytest.raises(ComposerValidationError, match="Duet and Stitch"):
        validate_confirm(_form(allow_duet="1"), _request(kind="photo"), "token")


def test_validate_confirm_privacy_must_be_in_options():
    """Privacy values outside creator_info options are rejected."""
    with pytest.raises(ComposerValidationError, match="not available"):
        validate_confirm(
            _form(privacy_level="MUTUAL_FOLLOW_FRIENDS"),
            _request(privacy_options=("SELF_ONLY",)),
            "token",
        )


def test_validate_confirm_requires_consent_and_preview():
    """Consent and a working preview are required."""
    with pytest.raises(ComposerValidationError, match="policy"):
        validate_confirm(_form(consent=""), _request(), "token")
    with pytest.raises(ComposerValidationError, match="Preview"):
        validate_confirm(_form(), _request(preview_ok=False), "token")


def test_consent_copy_switches_with_branded_content():
    """Branded disclosure uses the Branded Content Policy consent string."""
    html = render_composer_html(_request(), "csrf")
    assert MUSIC_USAGE_CONSENT in html
    assert BRANDED_CONTENT_CONSENT in html
    assert BRANDED_PRIVATE_HELPER in html


def test_processing_html_mentions_minutes():
    """After confirm, the page tells the creator processing may take minutes."""
    assert "minutes" in render_processing_html()
    assert PROCESSING_NOTICE in render_processing_html()


def test_loopback_host_and_origin():
    """Only loopback Host/Origin are accepted."""
    assert is_loopback_host("127.0.0.1:9999") is True
    assert is_loopback_host("localhost:9999") is True
    assert is_loopback_host("example.com") is False
    assert is_loopback_host(None) is False
    assert is_allowed_origin("http://127.0.0.1:9999", 9999) is True
    assert is_allowed_origin("http://evil.example", 9999) is False
    assert is_allowed_origin(None, 9999) is False


def test_bind_composer_never_uses_oauth_port():
    """Composer bind must not use port 3456."""
    server = bind_composer_server()
    try:
        assert server.server_port != OAUTH_CALLBACK_PORT
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()


def test_composer_from_creator_info_maps_fields():
    """Composer request is driven by live creator_info, not login cache shape."""
    request = composer_from_creator_info(
        {
            "creator_nickname": "Ada",
            "privacy_level_options": ["SELF_ONLY"],
            "comment_disabled": True,
            "duet_disabled": True,
            "stitch_disabled": False,
        },
        title="Hi",
        kind="video",
        preview_urls=["https://example.com/v.mp4"],
    )
    assert request.nickname == "Ada"
    assert request.privacy_options == ("SELF_ONLY",)
    assert request.comment_disabled is True
    assert request.duet_disabled is True


def test_flatten_form_takes_last_value():
    """parse_qs lists flatten to the last submitted value."""
    assert flatten_form({"title": ["a", "b"]}) == {"title": "b"}


def test_bind_preview_assets_rewrites_local_and_keeps_http(tmp_path):
    """Local paths become loopback /preview/N; HTTP URLs stay unchanged."""
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"video-bytes")
    urls, files = bind_preview_assets(
        (str(clip), "https://example.com/v.mp4", "file://" + str(clip)),
        9999,
    )
    assert urls[0] == "http://127.0.0.1:9999/preview/0"
    assert urls[1] == "https://example.com/v.mp4"
    assert urls[2] == "http://127.0.0.1:9999/preview/2"
    assert files[0] == str(clip.resolve())
    assert files[1] is None
    assert files[2] == str(clip.resolve())


def test_composer_serves_local_preview_bytes(tmp_path):
    """Loopback GET /preview/0 returns the allowlisted file; Range and Host are enforced."""
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"abcdefghij")
    server = bind_composer_server()
    urls, files = bind_preview_assets((str(clip),), server.server_port)
    server.composer_request = _request(preview_urls=urls)
    server.preview_files = files
    server.timeout = 0.5
    thread = threading.Thread(target=_serve_until_done, args=(server,), daemon=True)
    thread.start()
    port = server.server_port
    try:
        html = _http_get(port, "/", host="127.0.0.1")
        assert f"http://127.0.0.1:{port}/preview/0" in html

        status, headers, body = _http_get_raw(port, "/preview/0", host="127.0.0.1")
        assert status == 200
        assert body == b"abcdefghij"
        assert "video/mp4" in headers.get("content-type", "")

        range_status, range_headers, range_body = _http_get_raw(
            port,
            "/preview/0",
            host="127.0.0.1",
            extra_headers={"Range": "bytes=2-5"},
        )
        assert range_status == 206
        assert range_body == b"cdef"
        assert range_headers.get("content-range") == "bytes 2-5/10"

        forbidden = _http_get(port, "/preview/0", host="evil.example", expect_status=403)
        assert "Forbidden" in forbidden

        missing = _http_get(port, "/preview/9", host="127.0.0.1", expect_status=404)
        assert "Not found" in missing
    finally:
        server.cancelled = True
        server.server_close()
        thread.join(timeout=2)


def test_composer_http_csrf_and_cancel_and_path_traversal():
    """HTTP: confirm returns payload, replay/cancel/traversal do not publish."""
    server = bind_composer_server()
    server.composer_request = _request()
    server.csrf_token = "secret-csrf"
    server.timeout = 0.5
    thread = threading.Thread(target=_serve_until_done, args=(server,), daemon=True)
    thread.start()
    port = server.server_port
    try:
        html = _http_get(port, "/", host="127.0.0.1")
        assert "Share to TikTok" in html
        assert server.server_port != OAUTH_CALLBACK_PORT

        forbidden = _http_get(port, "/", host="evil.example", expect_status=403)
        assert "Forbidden" in forbidden

        missing = _http_get(port, "/../secrets", host="127.0.0.1", expect_status=404)
        assert "Not found" in missing

        status, body = _http_post(
            port,
            "/",
            "csrf=secret-csrf&title=From+HTTP&privacy_level=SELF_ONLY&consent=1&video_url=https://evil.example/x.mp4",
            origin=f"http://127.0.0.1:{port}",
        )
        assert status == 200
        assert "minutes" in body
        assert server.payload is not None
        assert server.payload.title == "From HTTP"
        assert not hasattr(server.payload, "video_url")

        replay_status, _replay_body = _http_post(
            port,
            "/",
            "csrf=secret-csrf&title=Replay&privacy_level=SELF_ONLY&consent=1",
            origin=f"http://127.0.0.1:{port}",
            expect_status=400,
        )
        assert replay_status == 400
        assert server.payload.title == "From HTTP"

        cancel_body = _http_get(port, "/cancel", host="127.0.0.1")
        assert "cancelled" in cancel_body.lower()
        assert server.cancelled is True
    finally:
        server.cancelled = True
        server.server_close()
        thread.join(timeout=2)


def test_composer_idle_timeout_constant():
    """Idle timeout is 15 minutes."""
    assert COMPOSER_IDLE_TIMEOUT_SEC == 15 * 60


def _serve_until_done(server):
    """Handle a bounded number of requests for the HTTP test."""
    try:
        for _ in range(20):
            server.handle_request()
    except Exception:
        return


def _http_get(port, path, host, expect_status=200):
    """GET via http.client so urllib blocking does not apply."""
    _status, _headers, body = _http_get_raw(port, path, host, expect_status=expect_status)
    return body.decode("utf-8")


def _http_get_raw(port, path, host, expect_status=None, extra_headers=None):
    """GET bytes and headers via http.client."""
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        headers = {"Host": f"{host}:{port}"}
        if extra_headers:
            headers.update(extra_headers)
        conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        body = response.read()
        if expect_status is not None:
            assert response.status == expect_status
        return response.status, {key.lower(): value for key, value in response.getheaders()}, body
    finally:
        conn.close()


def _http_post(port, path, body, origin, expect_status=None):
    """POST via http.client with a loopback Origin."""
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        headers = {
            "Host": f"127.0.0.1:{port}",
            "Origin": origin,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        conn.request("POST", path, body=body, headers=headers)
        response = conn.getresponse()
        text = response.read().decode("utf-8")
        if expect_status is not None:
            assert response.status == expect_status
        return response.status, text
    finally:
        conn.close()
