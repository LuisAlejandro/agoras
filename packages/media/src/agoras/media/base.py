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
"""agoras.media.base module."""

import asyncio
import io
import os
import tempfile
from abc import ABC, abstractmethod
from enum import Enum
from urllib.request import Request, urlopen

import filetype

from agoras.common import __version__

from .paths import is_local_media_source, normalize_media_path


class MediaState(str, Enum):
    """
    Lifecycle state of a media object.

    ``_set_state`` is the only writer. Everything the rest of the codebase
    reads about lifecycle (``_downloaded``) or source (``_is_local``) is
    derived from here, so the two can never disagree.

    ``DOWNLOADED`` is entered *before* validation runs so the content probes
    (``_probe_video``, ``get_dimensions``) see the state they require.
    """

    NEW = "new"
    DOWNLOADED = "downloaded"
    CLEANED = "cleaned"


class Media(ABC):
    """
    Abstract base class for media handling.

    Provides common functionality for downloading, validating, and managing
    media files from URLs.
    """

    def __init__(self, url):
        """
        Initialize media instance.

        Args:
            url (str): URL of the media to download
        """
        self.url = url
        self.temp_file = None
        self.content = None
        self.file_type = None
        self._file_handle = None
        self._state = MediaState.NEW

    def _set_state(self, state, **fields):
        """Move to ``state``, applying its field values. The only state writer."""
        for name, value in fields.items():
            setattr(self, name, value)
        self._state = state

    @property
    def _downloaded(self) -> bool:
        """True only in ``DOWNLOADED`` (derived, never stored)."""
        return self._state is MediaState.DOWNLOADED

    @_downloaded.setter
    def _downloaded(self, value):
        """ponytail: migration shim for direct flag writes; drop with its last assignment."""
        self._state = MediaState.DOWNLOADED if value else MediaState.NEW

    @property
    def _is_local(self) -> bool:
        """True when the source is a local file (derived from url, never stored)."""
        return isinstance(self.url, str) and is_local_media_source(self.url)

    @property
    def is_local(self) -> bool:
        """True when this instance reads a user-owned local file (not a temp download)."""
        return self._is_local

    @property
    @abstractmethod
    def allowed_types(self) -> list[str]:
        """
        Get list of allowed MIME types for this media type.

        Returns:
            list: List of allowed MIME types
        """

    async def download(self):
        """
        Download media from URL asynchronously.

        Returns:
            tuple: (temp_file_path, content, file_type)

        Raises:
            Exception: If download or validation fails
        """
        if self._downloaded:
            return self.temp_file, self.content, self.file_type

        if self._is_local:

            def _sync_read_local():
                local_path = normalize_media_path(self.url)
                if not os.path.isfile(local_path):
                    raise FileNotFoundError(f"Local media file not found: {local_path}")
                max_bytes = getattr(self, "max_size", None)
                if max_bytes is None:
                    constraints = getattr(self, "constraints", None)
                    max_bytes = getattr(constraints, "max_bytes", None)
                if max_bytes is not None:
                    file_size = os.path.getsize(local_path)
                    if file_size > max_bytes:
                        from .errors import MediaValidationError

                        platform_key = getattr(self, "platform_key", "generic")
                        media_kind = getattr(self, "media_kind", self.__class__.__name__.lower())
                        raise MediaValidationError(platform_key, media_kind, "max_bytes", file_size, max_bytes)
                with open(local_path, "rb") as handle:
                    content = handle.read()
                return local_path, content

            self.temp_file, self.content = await asyncio.to_thread(_sync_read_local)
        else:

            def _sync_download():
                _, tmpfile = tempfile.mkstemp(prefix=self._get_file_prefix(), suffix=".bin")

                with open(tmpfile, "wb") as f:
                    request = Request(url=self.url, headers={"User-Agent": f"Agoras/{__version__}"})
                    content = urlopen(request, timeout=30).read()
                    f.write(content)

                return tmpfile, content

            self.temp_file, self.content = await asyncio.to_thread(_sync_download)

        # Enter DOWNLOADED before validating: the content probes gate on the
        # lifecycle state and previously ran half-initialized (state still NEW),
        # which silently skipped every duration/dimension limit.
        self._set_state(MediaState.DOWNLOADED)
        self.file_type = self._validate_file_type()
        self._validate_content()

        return self.temp_file, self.content, self.file_type

    def get_file_like_object(self):
        """
        Get a file-like object that can be used with libraries expecting file handles.

        Returns:
            io.BytesIO: File-like object containing the media content

        Raises:
            Exception: If file hasn't been downloaded
        """
        if not self._downloaded:
            raise Exception("File must be downloaded before getting file object")

        if self.content is not None:
            return io.BytesIO(self.content)
        raise Exception("No file content available in memory")

    def _get_file_prefix(self):
        """
        Get file prefix for temporary files.

        Returns:
            str: File prefix
        """
        return f"{self.__class__.__name__.lower()}-"

    def _validate_file_type(self):
        """
        Validate file type and return file type info.

        Returns:
            FileType: File type information

        Raises:
            Exception: If file type is invalid
        """
        if self.content is not None:
            kind = filetype.guess(self.content)
        elif self.temp_file:
            kind = filetype.guess(self.temp_file)
        else:
            raise Exception("File must be downloaded before validation")

        if not kind:
            self.cleanup()
            raise Exception(f"Invalid {self.__class__.__name__.lower()} type for {self.url}")

        if kind.mime not in self.allowed_types:
            self.cleanup()
            media_type = self.__class__.__name__.lower()
            platform_key = getattr(self, "platform_key", "generic")
            media_kind = getattr(self, "media_kind", media_type)
            if hasattr(self, "constraints"):
                from .errors import MediaValidationError

                raise MediaValidationError(
                    platform_key,
                    media_kind,
                    "mime_types",
                    kind.mime,
                    sorted(self.allowed_types),
                )
            raise Exception(
                f'Invalid {media_type} type "{kind.mime}" for {self.url}. Allowed types: {self.allowed_types}'
            )

        return kind

    def _validate_content(self):
        """
        Validate media content. Override in subclasses for specific validation.
        """

    def get_file_size(self):
        """
        Get file size in bytes.

        Returns:
            int: File size in bytes

        Raises:
            Exception: If file hasn't been downloaded
        """
        if self.content is not None:
            return len(self.content)
        if self._downloaded and self.temp_file:
            return os.path.getsize(self.temp_file)
        raise Exception("File must be downloaded before getting size")

    def cleanup(self):
        """
        Clean up temporary files and file handles.
        """
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception:
                pass

        if self.temp_file and os.path.exists(self.temp_file) and not self._is_local:
            try:
                os.unlink(self.temp_file)
            except Exception:
                pass

        # Local sources are never unlinked, but the pointer is always dropped so
        # CLEANED has exactly one shape.
        self._set_state(MediaState.CLEANED, _file_handle=None, temp_file=None, content=None, file_type=None)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.cleanup()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with automatic cleanup."""
        self.cleanup()
