# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Strict YAML content-file loader and normalizer for Agoras CLI."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Set
from urllib.parse import urlparse

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

from agoras.media.paths import is_local_media_source, normalize_media_path

from .content_specs import (
    ALL_CONTENT_KEYS,
    CONTENT_SCHEMA_VERSION,
    INLINE_CONTENT_DESTINATIONS,
    RESERVED_CONTENT_KEYS,
    ActionSpec,
    FieldSpec,
    get_action_spec,
    supports_content_file,
)

# Resource limits (plan KTD2).
MAX_CONTENT_BYTES = 1 * 1024 * 1024
MAX_YAML_DEPTH = 32
MAX_YAML_NODES = 10_000

DISCORD_EMBED_KEYS = frozenset({"title", "description", "url", "image_url"})


class ContentError(ValueError):
    """Raised when a content file fails validation."""


class StrictSafeLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicates, aliases, merges, and tracks node count."""

    def __init__(self, stream):
        """Initialize loader state for node and depth limits."""
        super().__init__(stream)
        self._node_count = 0
        self._depth = 0

    def compose_node(self, parent, index):
        """Compose a node while enforcing node-count and depth limits."""
        self._node_count += 1
        if self._node_count > MAX_YAML_NODES:
            raise ContentError(f"YAML exceeds maximum node count of {MAX_YAML_NODES}")
        self._depth += 1
        if self._depth > MAX_YAML_DEPTH:
            raise ContentError(f"YAML exceeds maximum depth of {MAX_YAML_DEPTH}")
        try:
            return super().compose_node(parent, index)
        finally:
            self._depth -= 1

    def compose_mapping_node(self, anchor):
        """Compose a mapping node, rejecting anchors/aliases."""
        # Reject aliases: SafeLoader still supports anchors; block graph features.
        if anchor is not None:
            raise ContentError("YAML anchors and aliases are not allowed in content files")
        node = super().compose_mapping_node(anchor)
        return node

    def compose_sequence_node(self, anchor):
        """Compose a sequence node, rejecting anchors/aliases."""
        if anchor is not None:
            raise ContentError("YAML anchors and aliases are not allowed in content files")
        return super().compose_sequence_node(anchor)

    def compose_scalar_node(self, anchor):
        """Compose a scalar node, rejecting anchors/aliases."""
        if anchor is not None:
            raise ContentError("YAML anchors and aliases are not allowed in content files")
        return super().compose_scalar_node(anchor)

    def construct_mapping(self, node, deep=False):
        """Construct a mapping, rejecting duplicate and non-string keys."""
        if not isinstance(node, MappingNode):
            raise ConstructorError(None, None, f"expected a mapping node, but found {node.id}", node.start_mark)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise ContentError(
                    f"YAML mapping keys must be strings (got {type(key).__name__})" + _mark_suffix(key_node)
                )
            if key in mapping:
                raise ContentError(f"Duplicate YAML key: {key!r}" + _mark_suffix(key_node))
            if key == "<<":
                raise ContentError("YAML merge keys are not allowed in content files" + _mark_suffix(key_node))
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


# Remove merge-key resolver if present on this loader subclass only.
if "<<" in getattr(StrictSafeLoader, "yaml_implicit_resolvers", {}):
    StrictSafeLoader.yaml_implicit_resolvers = {
        ch: [(tag, regexp) for (tag, regexp) in resolvers if tag != "tag:yaml.org,2002:merge"]
        for ch, resolvers in StrictSafeLoader.yaml_implicit_resolvers.items()
    }


def _mark_suffix(node) -> str:
    mark = getattr(node, "start_mark", None)
    if mark is None:
        return ""
    return f" (line {mark.line + 1}, column {mark.column + 1})"


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _exact_type_name(value: Any) -> str:
    if type(value) is bool:
        return "bool"
    if type(value) is int:
        return "int"
    if type(value) is float:
        return "float"
    if type(value) is str:
        return "str"
    if type(value) is list:
        return "list"
    if type(value) is dict:
        return "dict"
    if value is None:
        return "null"
    return type(value).__name__


def _validate_http_url(value: str, path: str) -> None:
    if not _is_http_url(value):
        raise ContentError(f"{path} must be an absolute http(s) URL (got {value!r})")


def _validate_media_source_field(value: str, path: str) -> None:
    if not value or not isinstance(value, str):
        raise ContentError(f"{path} must be a non-empty string")
    if _is_http_url(value) or is_local_media_source(value):
        return
    raise ContentError(f"{path} must be an absolute http(s) URL or local media path (got {value!r})")


def _resolve_media_value(value: str, base_dir: Optional[str] = None) -> str:
    if _is_http_url(value):
        return value
    if is_local_media_source(value):
        return normalize_media_path(value, base_dir=base_dir)
    return value


def _validate_str_field(field: FieldSpec, value: Any, path: str) -> str:
    if type(value) is not str:
        raise ContentError(f"{path} must be a string (got {_exact_type_name(value)})")
    if field.http_url:
        _validate_http_url(value, path)
    elif field.media_source:
        _validate_media_source_field(value, path)
    if field.max_length is not None and len(value) > field.max_length:
        raise ContentError(f"{path} exceeds max length {field.max_length}")
    if field.choices is not None and value not in field.choices:
        raise ContentError(f"{path} must be one of {sorted(field.choices)} (got {value!r})")
    return value


def _validate_int_field(field: FieldSpec, value: Any, path: str) -> int:
    # Discord archive durations are ints; choices stored as strings in FieldSpec.
    if type(value) is not int or type(value) is bool:
        raise ContentError(f"{path} must be an integer (got {_exact_type_name(value)})")
    if field.choices is not None and str(value) not in field.choices:
        raise ContentError(f"{path} must be one of {[int(c) for c in sorted(field.choices, key=int)]}")
    return value


def _validate_str_list_field(field: FieldSpec, value: Any, path: str) -> list:
    if type(value) is not list:
        raise ContentError(f"{path} must be a list (got {_exact_type_name(value)})")
    if field.min_items is not None and len(value) < field.min_items:
        raise ContentError(f"{path} must have at least {field.min_items} item(s)")
    if field.max_items is not None and len(value) > field.max_items:
        raise ContentError(f"{path} must have at most {field.max_items} item(s)")
    result = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if type(item) is not str:
            raise ContentError(f"{item_path} must be a string (got {_exact_type_name(item)})")
        if field.http_url:
            _validate_http_url(item, item_path)
        elif field.media_source:
            _validate_media_source_field(item, item_path)
        result.append(item)
    return result


def _validate_embed_mapping(item: Mapping[str, Any], item_path: str) -> dict:
    cleaned = {}
    for key, nested in item.items():
        if type(key) is not str:
            raise ContentError(f"{item_path} keys must be strings")
        if key not in DISCORD_EMBED_KEYS:
            raise ContentError(f"{item_path}.{key} is not a valid embed field")
        if nested is None:
            continue
        if type(nested) is not str:
            raise ContentError(f"{item_path}.{key} must be a string")
        if key in ("url", "image_url"):
            _validate_http_url(nested, f"{item_path}.{key}")
        cleaned[key] = nested
    if not cleaned:
        raise ContentError(f"{item_path} must include at least one embed field")
    return cleaned


def _validate_map_list_field(field: FieldSpec, value: Any, path: str) -> list:
    if type(value) is not list:
        raise ContentError(f"{path} must be a list (got {_exact_type_name(value)})")
    if field.max_items is not None and len(value) > field.max_items:
        raise ContentError(f"{path} must have at most {field.max_items} item(s)")
    result = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if type(item) is not dict:
            raise ContentError(f"{item_path} must be a mapping (got {_exact_type_name(item)})")
        result.append(_validate_embed_mapping(item, item_path))
    return result


def _validate_field_value(field: FieldSpec, value: Any, path: str) -> Any:
    """Validate and return a single field value (may apply light normalization)."""
    if value is None:
        raise ContentError(f"{path} must not be null")

    kind = field.kind
    if kind == "str":
        return _validate_str_field(field, value, path)
    if kind == "bool":
        if type(value) is not bool:
            raise ContentError(f"{path} must be a boolean (got {_exact_type_name(value)})")
        return value
    if kind == "int":
        return _validate_int_field(field, value, path)
    if kind == "str_list":
        return _validate_str_list_field(field, value, path)
    if kind == "map_list":
        return _validate_map_list_field(field, value, path)
    if kind == "any":
        # WhatsApp template components: list or mapping of structured data.
        if type(value) not in (list, dict, str):
            raise ContentError(f"{path} must be a list, mapping, or string")
        return value
    if kind == "entries":
        raise ContentError(f"{path} entries kind must be validated via validate_document")
    raise ContentError(f"Unknown field kind {kind!r} for {path}")


def _check_require_one_of(data: Mapping[str, Any], groups: Sequence[Sequence[str]], path: str) -> None:
    for group in groups:
        if any(key in data and data[key] not in (None, "", []) for key in group):
            continue
        raise ContentError(f"{path} requires at least one of: {', '.join(group)}")


def _check_conflicts(data: Mapping[str, Any], conflicts: Sequence[Sequence[str]], path: str) -> None:
    for group in conflicts:
        present = [key for key in group if key in data and data[key] not in (None, "", [])]
        if len(present) > 1:
            raise ContentError(f"{path} fields conflict and cannot be combined: {', '.join(present)}")


def _validate_mapping_against_fields(
    data: Mapping[str, Any],
    *,
    field_map: Mapping[str, FieldSpec],
    require_one_of: Sequence[Sequence[str]],
    conflicts: Sequence[Sequence[str]],
    path: str,
    known_elsewhere: Set[str],
) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in data.items():
        if key in RESERVED_CONTENT_KEYS:
            raise ContentError(f"{path}.{key} is reserved and must not appear in content files")
        if key not in field_map:
            if key in ALL_CONTENT_KEYS or key in known_elsewhere:
                raise ContentError(f"{path}.{key} is not supported for this action")
            raise ContentError(f"{path}.{key} is an unknown content field")
        result[key] = _validate_field_value(field_map[key], value, f"{path}.{key}" if path else key)

    for name, field in field_map.items():
        if field.required and name not in result:
            label = f"{path}.{name}" if path else name
            raise ContentError(f"{label} is required")
        if name not in result and field.default is not None:
            result[name] = field.default

    _check_require_one_of(result, require_one_of, path or "document")
    _check_conflicts(result, conflicts, path or "document")
    return result


def validate_document(raw: Mapping[str, Any], platform: str, action: str) -> Dict[str, Any]:
    """Validate a parsed content document against the action specification."""
    if type(raw) is not dict:
        raise ContentError(f"Content root must be a mapping (got {_exact_type_name(raw)})")

    if "version" not in raw:
        raise ContentError("Content file requires version: 1")
    version = raw["version"]
    if type(version) is not int or type(version) is bool:
        raise ContentError(f"version must be an integer (got {_exact_type_name(version)})")
    if version != CONTENT_SCHEMA_VERSION:
        raise ContentError(f"Unsupported content schema version {version} (expected {CONTENT_SCHEMA_VERSION})")

    spec = get_action_spec(platform, action)
    body = {key: value for key, value in raw.items() if key != "version"}

    # Entries need special handling.
    if "entries" in spec.field_map:
        entries_raw = body.get("entries")
        if entries_raw is None and spec.field_map["entries"].required:
            raise ContentError("entries is required")
        root_without_entries = {k: v for k, v in body.items() if k != "entries"}
        root_fields = {k: v for k, v in spec.field_map.items() if k != "entries"}
        validated_root = _validate_mapping_against_fields(
            root_without_entries,
            field_map=root_fields,
            require_one_of=(),
            conflicts=(),
            path="",
            known_elsewhere=set(spec.entry_field_map.keys()),
        )
        entries_field = spec.field_map["entries"]
        if type(entries_raw) is not list:
            raise ContentError(f"entries must be a list (got {_exact_type_name(entries_raw)})")
        if entries_field.min_items is not None and len(entries_raw) < entries_field.min_items:
            raise ContentError(f"entries must have at least {entries_field.min_items} item(s)")
        if entries_field.max_items is not None and len(entries_raw) > entries_field.max_items:
            raise ContentError(f"entries must have at most {entries_field.max_items} item(s)")
        validated_entries = []
        for index, entry in enumerate(entries_raw):
            if type(entry) is not dict:
                raise ContentError(f"entries[{index}] must be a mapping (got {_exact_type_name(entry)})")
            validated_entries.append(
                _validate_mapping_against_fields(
                    entry,
                    field_map=spec.entry_field_map,
                    require_one_of=spec.entry_require_one_of,
                    conflicts=spec.entry_conflicts,
                    path=f"entries[{index}]",
                    known_elsewhere=set(spec.allowed_keys),
                )
            )
        validated_root["entries"] = validated_entries
        validated_root["version"] = version
        return validated_root

    validated = _validate_mapping_against_fields(
        body,
        field_map=spec.field_map,
        require_one_of=spec.require_one_of,
        conflicts=spec.conflicts,
        path="",
        known_elsewhere=set(),
    )
    validated["version"] = version
    return validated


def flatten_images(images: Optional[Sequence[str]]) -> Dict[str, str]:
    """Convert images list to image_1..image_4 destinations."""
    result: Dict[str, str] = {}
    if not images:
        return result
    for index, url in enumerate(images, start=1):
        result[f"image_{index}"] = url
    return result


def _resolve_media_paths_in_mapping(
    data: MutableMapping[str, Any],
    base_dir: Optional[str],
    fields: Sequence[FieldSpec],
) -> None:
    for field in fields:
        if not field.media_source:
            continue
        value = data.get(field.name)
        if field.kind == "str" and isinstance(value, str):
            data[field.name] = _resolve_media_value(value, base_dir)
        elif field.kind == "str_list" and isinstance(value, list):
            data[field.name] = [
                _resolve_media_value(item, base_dir) if isinstance(item, str) else item for item in value
            ]


def normalize_to_cli_namespace(
    validated: Mapping[str, Any],
    platform: str,
    action: str,
    *,
    base_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Flatten validated YAML into argparse-style destinations for ParameterConverter.

    Does not include version. Includes `_content_source` and `_content_keys` metadata
    for presence-aware config (stripped before wrapper conversion by apply helpers).
    """
    payload: Dict[str, Any] = {}
    keys_present: Set[str] = set()
    working = dict(validated)
    spec = get_action_spec(platform, action)
    _resolve_media_paths_in_mapping(working, base_dir, spec.fields)

    def set_field(name: str, value: Any) -> None:
        payload[name] = value
        keys_present.add(name)

    for key, value in working.items():
        if key == "version":
            continue
        if key == "images":
            for dest, url in flatten_images(value).items():
                set_field(dest, url)
            keys_present.add("images")
            continue
        if key == "keywords":
            # YouTube converter expects comma-separated string historically.
            if isinstance(value, list):
                set_field("keywords", ",".join(value))
            else:
                set_field("keywords", value)
            continue
        if key == "entries":
            normalized_entries = []
            for entry in value:
                entry_payload: Dict[str, Any] = dict(entry)
                _resolve_media_paths_in_mapping(entry_payload, base_dir, spec.entry_fields)
                for entry_key, entry_value in list(entry_payload.items()):
                    if entry_key == "images":
                        entry_payload.update(flatten_images(entry_value))
                        entry_payload.pop("images", None)
                normalized_entries.append(entry_payload)
            set_field("entries", normalized_entries)
            continue
        set_field(key, value)

    payload["_content_source"] = "file"
    payload["_content_keys"] = sorted(keys_present)
    return payload


def load_yaml_bytes(data: bytes, *, source: str = "<content>") -> Any:
    """Parse YAML bytes with StrictSafeLoader; enforce single document."""
    if len(data) > MAX_CONTENT_BYTES:
        raise ContentError(f"Content file exceeds maximum size of {MAX_CONTENT_BYTES} bytes")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ContentError("Content file must be UTF-8") from exc
    if not text.strip():
        raise ContentError("Content file is empty")

    try:
        documents = list(yaml.load_all(text, Loader=StrictSafeLoader))
    except ContentError:
        raise
    except yaml.YAMLError as exc:
        raise ContentError(f"Invalid YAML: {exc}") from exc

    documents = [doc for doc in documents if doc is not None]
    if not documents:
        raise ContentError("Content file is empty")
    if len(documents) > 1:
        raise ContentError("Content file must contain exactly one YAML document")
    return documents[0]


def load_content_file(path: str | Path, platform: str, action: str) -> Dict[str, Any]:
    """Load, validate, and normalize a content YAML file for platform/action."""
    if not supports_content_file(platform, action):
        raise ContentError(f"{platform} {action} does not accept --content")

    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix not in (".yaml", ".yml"):
        raise ContentError("Content file must use a .yaml or .yml extension")

    try:
        data = file_path.read_bytes()
    except OSError as exc:
        raise ContentError(f"Cannot read content file: {exc}") from exc

    raw = load_yaml_bytes(data, source=str(file_path))
    if type(raw) is not dict:
        raise ContentError(f"Content root must be a mapping (got {_exact_type_name(raw)})")

    validated = validate_document(raw, platform, action)
    base_dir = str(file_path.parent.resolve())
    return normalize_to_cli_namespace(validated, platform, action, base_dir=base_dir)


def detect_explicit_inline_content(args: argparse.Namespace) -> List[str]:
    """Return destinations present on Namespace that are inline content fields.

    ``None`` values (e.g. store_true flags with default=None) are not treated as
    explicit content so they do not false-conflict with ``--content``.
    """
    found = []
    for name in INLINE_CONTENT_DESTINATIONS:
        if hasattr(args, name) and getattr(args, name) is not None:
            found.append(name)
    return sorted(found)


def apply_content_to_namespace(args: argparse.Namespace, payload: Mapping[str, Any]) -> argparse.Namespace:
    """Merge normalized payload into args; strip loader-only metadata for converters later."""
    for key, value in payload.items():
        setattr(args, key, value)
    return args


def strip_content_metadata(legacy_args: MutableMapping[str, Any]) -> None:
    """Remove content-file metadata before platform wrappers see config."""
    legacy_args.pop("content", None)
    legacy_args.pop("content_file", None)
    # Keep _content_source / _content_keys for presence-aware SocialNetwork until U3;
    # wrappers should ignore unknown underscore keys. Converter may pass them through.


def _apply_content_file_to_args(args: argparse.Namespace, platform: str, action: str, content_path: str) -> None:
    if not supports_content_file(platform, action):
        raise ContentError(f"{platform} {action} does not accept --content")
    payload = load_content_file(content_path, platform, action)
    for name in INLINE_CONTENT_DESTINATIONS:
        if hasattr(args, name) and name not in payload:
            delattr(args, name)
    apply_content_to_namespace(args, payload)


def _inline_group_present(args: argparse.Namespace, group: Sequence[str]) -> bool:
    for key in group:
        if key == "images":
            if any(getattr(args, f"image_{i}", None) for i in range(1, 5)):
                return True
        elif getattr(args, key, None) not in (None, "", []):
            return True
    return False


def _inline_group_flags(group: Sequence[str]) -> list:
    flags = []
    for key in group:
        if key == "images":
            flags.append("--image-1..4")
        else:
            flags.append("--" + key.replace("_", "-"))
    return flags


def _enforce_inline_required(args: argparse.Namespace, spec: ActionSpec) -> None:
    for field in spec.fields:
        if field.name == "entries":
            continue
        if field.name == "images":
            has_image = any(getattr(args, f"image_{i}", None) for i in range(1, 5))
            if field.required and not has_image:
                raise ContentError("at least one --image-N is required")
            continue
        if field.required and not getattr(args, field.name, None):
            flag = "--" + field.name.replace("_", "-")
            raise ContentError(f"{flag} is required")
    for group in spec.require_one_of:
        if not _inline_group_present(args, group):
            raise ContentError(f"Provide at least one of: {', '.join(_inline_group_flags(group))}")


def _apply_inline_defaults(args: argparse.Namespace, spec: ActionSpec) -> None:
    # argparse uses SUPPRESS so ActionSpec defaults are not explicit CLI values.
    for field in spec.fields:
        if field.name in ("entries", "images"):
            continue
        if field.default is not None and not hasattr(args, field.name):
            setattr(args, field.name, field.default)


def _apply_media_source_arg(args: argparse.Namespace, name: str, base_dir: str) -> None:
    value = getattr(args, name, None)
    if value:
        _validate_media_source_field(value, name)
        setattr(args, name, _resolve_media_value(value, base_dir))


def _resolve_inline_media_args(args: argparse.Namespace, spec: ActionSpec) -> None:
    base_dir = os.getcwd()
    for field in spec.fields:
        if field.name == "images":
            for index in range(1, 5):
                _apply_media_source_arg(args, f"image_{index}", base_dir)
            continue
        if field.media_source and field.kind == "str":
            _apply_media_source_arg(args, field.name, base_dir)


def ensure_content_source_xor(args: argparse.Namespace, platform: str, action: str) -> None:
    """
    Enforce file XOR inline content after argparse.

    When --content is set, load and apply the file. When absent, leave inline args as-is
    but still validate required fields via ActionSpec when useful.
    """
    content_path = getattr(args, "content", None)
    explicit = detect_explicit_inline_content(args)

    if content_path and explicit:
        raise ContentError(
            "Cannot combine --content with inline content options "
            f"({', '.join('--' + name.replace('_', '-') for name in explicit)})"
        )

    if content_path:
        _apply_content_file_to_args(args, platform, action, content_path)
        return

    if not supports_content_file(platform, action):
        return
    spec = get_action_spec(platform, action)
    _enforce_inline_required(args, spec)
    _resolve_inline_media_args(args, spec)
    _apply_inline_defaults(args, spec)


def add_content_file_option(parser: argparse.ArgumentParser) -> None:
    """Register --content on a content-capable action parser."""
    group = parser.add_argument_group("Content File")
    group.add_argument(
        "--content",
        metavar="<file.yaml>",
        help=(
            "YAML content file (mutually exclusive with inline content options). "
            "Relative video_url and images paths resolve against the YAML file directory, not cwd."
        ),
    )


def content_arg_default():
    """Use SUPPRESS so unspecified content destinations are absent from Namespace."""
    return argparse.SUPPRESS
