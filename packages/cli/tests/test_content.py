# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

"""Tests for strict YAML content loader."""

import textwrap

import pytest

from agoras.cli.content import (
    ContentError,
    load_content_file,
    load_yaml_bytes,
    normalize_to_cli_namespace,
    validate_document,
)


def _write(tmp_path, name: str, body: str):
    path = tmp_path / name
    path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return path


def test_load_valid_x_post(tmp_path):
    path = _write(
        tmp_path,
        "post.yaml",
        """
        version: 1
        text: Hello
        link: https://example.com
        images:
          - https://cdn.example.com/a.jpg
        """,
    )
    payload = load_content_file(path, "x", "post")
    assert payload["text"] == "Hello"
    assert payload["link"] == "https://example.com"
    assert payload["image_1"] == "https://cdn.example.com/a.jpg"
    assert payload["_content_source"] == "file"


def test_reject_json_extension(tmp_path):
    path = _write(tmp_path, "post.json", "version: 1\ntext: hi\n")
    with pytest.raises(ContentError, match="\\.yaml or \\.yml"):
        load_content_file(path, "x", "post")


def test_reject_local_path_media(tmp_path):
    path = _write(
        tmp_path,
        "post.yaml",
        """
        version: 1
        images:
          - ./local.jpg
        """,
    )
    with pytest.raises(ContentError, match="http\\(s\\) URL"):
        load_content_file(path, "x", "post")


def test_reject_file_scheme(tmp_path):
    path = _write(
        tmp_path,
        "post.yaml",
        """
        version: 1
        images:
          - file:///tmp/a.jpg
        """,
    )
    with pytest.raises(ContentError, match="http\\(s\\) URL"):
        load_content_file(path, "instagram", "post")


def test_reject_duplicate_keys():
    data = b"version: 1\ntext: a\ntext: b\n"
    with pytest.raises(ContentError, match="Duplicate YAML key"):
        load_yaml_bytes(data)


def test_reject_alias():
    data = b"version: 1\ntext: &a hello\nlink: *a\n"
    with pytest.raises(ContentError, match="anchors and aliases"):
        load_yaml_bytes(data)


def test_reject_merge_key():
    data = b"version: 1\n<<: {text: hi}\n"
    with pytest.raises(ContentError, match="merge"):
        load_yaml_bytes(data)


def test_reject_multiple_documents():
    data = b"version: 1\ntext: a\n---\nversion: 1\ntext: b\n"
    with pytest.raises(ContentError, match="exactly one"):
        load_yaml_bytes(data)


def test_reject_empty():
    with pytest.raises(ContentError, match="empty"):
        load_yaml_bytes(b"   \n")


def test_reject_non_mapping_root():
    with pytest.raises(ContentError, match="mapping"):
        validate_document(["not", "a", "map"], "x", "post")  # type: ignore[arg-type]


def test_reject_missing_version():
    with pytest.raises(ContentError, match="version"):
        validate_document({"text": "hi"}, "x", "post")


def test_reject_wrong_version():
    with pytest.raises(ContentError, match="Unsupported content schema version"):
        validate_document({"version": 2, "text": "hi"}, "x", "post")


def test_reject_platform_key():
    with pytest.raises(ContentError, match="reserved"):
        validate_document({"version": 1, "platform": "x", "text": "hi"}, "x", "post")


def test_reject_unknown_key():
    with pytest.raises(ContentError, match="unknown content field"):
        validate_document({"version": 1, "not_a_field": 1, "text": "hi"}, "x", "post")


def test_reject_incompatible_key():
    # title is known globally but not on x post
    with pytest.raises(ContentError, match="not supported"):
        validate_document({"version": 1, "title": "nope", "text": "hi"}, "x", "post")


def test_reject_yaml11_bool_as_string_field():
    # unquoted yes becomes bool under YAML 1.1
    data = b"version: 1\ntext: yes\n"
    raw = load_yaml_bytes(data)
    with pytest.raises(ContentError, match="must be a string"):
        validate_document(raw, "x", "post")


def test_reject_images_and_video_in_thread_entry():
    with pytest.raises(ContentError, match="conflict"):
        validate_document(
            {
                "version": 1,
                "entries": [
                    {"text": "a"},
                    {
                        "images": ["https://cdn.example.com/a.jpg"],
                        "video_url": "https://cdn.example.com/a.mp4",
                    },
                ],
            },
            "x",
            "thread",
        )


def test_thread_requires_two_entries():
    with pytest.raises(ContentError, match="at least 2"):
        validate_document({"version": 1, "entries": [{"text": "only"}]}, "x", "thread")


def test_discord_thread_requires_name():
    with pytest.raises(ContentError, match="thread_name is required"):
        validate_document(
            {
                "version": 1,
                "entries": [{"text": "a"}, {"text": "b"}],
            },
            "discord",
            "thread",
        )


def test_discord_thread_ok():
    validated = validate_document(
        {
            "version": 1,
            "thread_name": "Release",
            "entries": [
                {"text": "one"},
                {"video_url": "https://cdn.example.com/v.mp4"},
            ],
        },
        "discord",
        "thread",
    )
    payload = normalize_to_cli_namespace(validated, "discord", "thread")
    assert payload["thread_name"] == "Release"
    assert len(payload["entries"]) == 2


def test_youtube_video_keywords_list(tmp_path):
    path = _write(
        tmp_path,
        "video.yml",
        """
        version: 1
        video_url: https://cdn.example.com/v.mp4
        title: My Video
        keywords:
          - cats
          - dogs
        """,
    )
    payload = load_content_file(path, "youtube", "video")
    assert payload["title"] == "My Video"
    assert payload["keywords"] == "cats,dogs"


def test_tiktok_bool_false_preserved(tmp_path):
    path = _write(
        tmp_path,
        "post.yaml",
        """
        version: 1
        images:
          - https://cdn.example.com/a.jpg
        allow_comments: false
        """,
    )
    payload = load_content_file(path, "tiktok", "post")
    assert payload["allow_comments"] is False


def test_whatsapp_template_components(tmp_path):
    path = _write(
        tmp_path,
        "tpl.yaml",
        """
        version: 1
        template_name: hello
        language_code: en
        template_components:
          - type: body
            parameters:
              - type: text
                text: World
        """,
    )
    payload = load_content_file(path, "whatsapp", "template")
    assert payload["template_name"] == "hello"
    assert isinstance(payload["template_components"], list)


def test_facebook_video_requires_title_description(tmp_path):
    path = _write(
        tmp_path,
        "video.yaml",
        """
        version: 1
        video_url: https://cdn.example.com/v.mp4
        """,
    )
    with pytest.raises(ContentError, match="video_title is required"):
        load_content_file(path, "facebook", "video")
